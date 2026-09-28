"""Algemene module voor autosites (AutoScout24, Gaspedaal, AutoTrack, Autowereld, ...).

Hoe het werkt:
- Moderne websites sturen hun advertenties als JSON-data mee in de pagina
  (voor Google of voor hun eigen app). Die data halen we eruit.
- We zoeken in die data naar "iets dat op een auto-advertentie lijkt":
  een blokje met een prijs, een kilometerstand of bouwjaar, een titel en een link.
- Zo werkt dezelfde code voor veel sites, ook als die sites anders zijn opgebouwd.

De zoek-URL per site staat in instellingen.toml onder [zoek_urls].
Klopt een URL niet meer? Zoek zelf op de site, kopieer de link uit je browser
en zet {merk}, {model} en {pagina} op de juiste plek. Zie de README.

Eerlijke waarschuwing: deze modules zijn niet getest tegen de echte sites,
omdat ik (de bouwer) die niet kon bereiken. Draai `verken-sites.bat` om te
zien welke sites werken.
"""

import re
from urllib.parse import urljoin, urlparse

from ..advertentie import Advertentie
from ..generaties import is_ander_model
from ..logboek import log
from ..normaliseren import bevat_woord, lees_getal
from .basis import Site, auto_uit_ld_json, jaar_uit_tekst, json_uit_html, meta_inhoud, zonder_html

# Welke veldnamen betekenen wat? (kleine letters, stukje van de naam is genoeg)
PRIJS = ["price", "prijs"]
PRIJS_NIET = ["month", "maand", "lease", "financ", "old", "previous", "vorige", "vat", "btw", "currency",
              "label", "type", "rating", "evaluation", "indicator", "range", "from", "total"]
KM = ["mileage", "kilometer", "odometer", "kmstand", "km"]
JAAR = ["firstregistration", "registrationdate", "constructionyear", "bouwjaar", "modeldate",
        "productiondate", "eerstetoelating", "year", "calendar"]

# Veel sites tonen kenmerken als lijstje: [{"label": "Bouwjaar", "value": "03/2014"}, ...]
LABEL_SLEUTELS = ["arialabel", "label", "iconname", "key"]
WAARDE_SLEUTELS = ["data", "value", "text", "formatted"]
MAAND_JAAR = re.compile(r"(?<!\d)(0?[1-9]|1[0-2])\s*[/-]\s*((?:19[89]|20[0-3])\d)(?!\d)")
TITEL = ["title", "titel", "name", "heading"]
MERK = ["make", "brand", "merk"]
MODEL = ["model"]
UITVOERING = ["modelversion", "version", "variant", "uitvoering", "subtitle"]
LINK = ["url", "link", "href", "detailurl", "vipurl", "permalink"]
ID = ["listingid", "advertid", "adid", "itemid", "guid", "id"]
BRANDSTOF = ["fuel", "brandstof"]
TRANSMISSIE = ["transmission", "gearbox", "geartype", "transmissie", "versnelling"]
PLAATS = ["city", "plaats", "woonplaats", "locality"]
KENTEKEN = ["licenseplate", "licenceplate", "kenteken", "registrationnumber"]
CC = ["displacement", "cilinder", "cylinder"]


def _plat(d, voorvoegsel="", diepte=0, uit=None):
    """{'price': {'value': 3100}} -> {'price.value': 3100}.

    Van lijsten nemen we alleen kenmerken-lijstjes over (zie _plat_kenmerken).
    """
    uit = {} if uit is None else uit
    for sleutel, waarde in d.items():
        pad = f"{voorvoegsel}{str(sleutel).lower()}"
        if isinstance(waarde, dict):
            if diepte < 3:
                _plat(waarde, pad + ".", diepte + 1, uit)
        elif isinstance(waarde, list):
            _plat_kenmerken(waarde, pad, uit)
        elif waarde not in (None, ""):
            uit.setdefault(pad, waarde)
    return uit


def _plat_kenmerken(lijst, pad, uit):
    """[{"ariaLabel": "Bouwjaar", "data": "03/2014"}] -> {"pad.bouwjaar": "03/2014"}."""
    for item in lijst[:40]:
        if not isinstance(item, dict):
            continue
        item = {str(k).lower(): v for k, v in item.items()}
        inhoud = next((item[k] for k in WAARDE_SLEUTELS
                       if k in item and isinstance(item[k], (str, int, float)) and item[k] != ""), None)
        if inhoud is None:
            continue
        for k in LABEL_SLEUTELS:
            label = item.get(k)
            if isinstance(label, str) and label:
                uit.setdefault(f"{pad}.{label.lower()}", inhoud)


def _zoek(plat, woorden, niet=(), alleen_laatste=False, geldig=None):
    """Eerste waarde waarvan de veldnaam een van de woorden bevat (in volgorde van voorkeur).

    Velden als "@type" (zegt wat voor soort blokje het is) slaan we over.
    Met geldig=functie tellen alleen waarden mee waarvoor die functie iets teruggeeft.
    """
    for woord in woorden:
        for pad, waarde in plat.items():
            laatste = pad.rsplit(".", 1)[-1]
            if laatste.startswith("@"):
                continue
            naam = laatste if alleen_laatste else pad
            if alleen_laatste:
                if naam != woord:
                    continue
            elif woord not in naam:
                continue
            if any(n in pad for n in niet):
                continue
            if geldig is not None and geldig(waarde, pad) is None:
                continue
            return pad, waarde
    return None, None


def lees_prijs(waarde, pad=""):
    """'€ 3.100,-' -> 3100, 310000 (centen) -> 3100, '3100.00' -> 3100."""
    if isinstance(waarde, bool):
        return None
    if isinstance(waarde, (int, float)):
        bedrag = waarde / 100 if "cent" in pad else waarde
    else:
        tekst = re.sub(r"[.,]\d{1,2}\s*$|,-", "", str(waarde).strip())
        bedrag = lees_getal(tekst)
        if bedrag is None:
            return None
        if "cent" in pad:
            bedrag = bedrag / 100
    bedrag = round(bedrag)
    return bedrag if 300 <= bedrag <= 200_000 else None


def lees_km(waarde, _pad=""):
    if isinstance(waarde, bool):
        return None
    km = lees_getal(re.sub(r"[.,]\d{1,2}\s*$", "", str(waarde))) if not isinstance(waarde, (int, float)) else int(waarde)
    return km if km is not None and 0 <= km <= 1_000_000 else None


def lees_jaar(waarde, _pad=""):
    m = re.search(r"(19[89]\d|20[0-3]\d)", str(waarde))
    return int(m.group(1)) if m else None


def jaar_uit_plat(plat):
    """Bouwjaar uit een veld; anders een datum als "03/2014" ergens in de advertentie."""
    _, jaar = _zoek(plat, JAAR, geldig=lees_jaar)
    if jaar is not None:
        return lees_jaar(jaar)
    for pad, waarde in plat.items():
        # Plaatsingsdatum e.d. is geen bouwjaar
        if any(w in pad for w in ("created", "publish", "updated", "online", "time", "since")):
            continue
        if isinstance(waarde, str):
            m = MAAND_JAAR.search(waarde)
            if m:
                return int(m.group(2))
    return None


def lijkt_op_advertentie(d):
    """Geeft de platte gegevens terug als dit blokje op een auto-advertentie lijkt, anders None."""
    plat = _plat(d)
    pad, _ = _zoek(plat, PRIJS, PRIJS_NIET, geldig=lees_prijs)
    if pad is None:
        return None
    km_pad, _ = _zoek(plat, KM, ["price", "bookmark"], geldig=lees_km)
    if km_pad is None and jaar_uit_plat(plat) is None:
        return None
    _, link = _zoek(plat, LINK, alleen_laatste=True)
    if not isinstance(link, str) or not (link.startswith("/") or link.startswith("http")):
        return None
    return plat


def vind_advertenties(blok):
    """Loopt door de JSON en geeft alle blokjes die op een advertentie lijken.

    Als een blokje zelf een advertentie is, kijken we er niet verder in
    (anders tellen we dezelfde auto twee keer).
    """
    stapel = [blok]
    while stapel:
        huidig = stapel.pop()
        if isinstance(huidig, dict):
            plat = lijkt_op_advertentie(huidig)
            if plat is not None:
                yield plat
            else:
                stapel.extend(reversed(list(huidig.values())))
        elif isinstance(huidig, list):
            stapel.extend(reversed(huidig))


def plat_naar_advertentie(plat, site, basis_url):
    pad, prijs = _zoek(plat, PRIJS, PRIJS_NIET, geldig=lees_prijs)
    _, link = _zoek(plat, LINK, alleen_laatste=True)
    link = urljoin(basis_url, link)
    _, titel = _zoek(plat, TITEL, ["seller", "dealer", "verkoper", "location", "brand.", "make."],
                     alleen_laatste=True)
    _, merk = _zoek(plat, MERK)
    _, model = _zoek(plat, MODEL, ["modelversion", "modeldate", "modelyear"])
    _, uitvoering = _zoek(plat, UITVOERING)
    if not isinstance(titel, str) or len(titel) < 4:
        titel = " ".join(str(x) for x in (merk, model, uitvoering) if isinstance(x, str))
    elif isinstance(merk, str) and merk.lower() not in titel.lower():
        titel = f"{merk} {titel}"
    _, ad_id = _zoek(plat, ID, alleen_laatste=True)
    _, km = _zoek(plat, KM, ["price", "bookmark"], geldig=lees_km)
    _, brandstof = _zoek(plat, BRANDSTOF)
    _, transmissie = _zoek(plat, TRANSMISSIE)
    _, plaats = _zoek(plat, PLAATS)
    _, kenteken = _zoek(plat, KENTEKEN)
    _, cc = _zoek(plat, CC)
    _, beschrijving = _zoek(plat, ["description", "beschrijving"])
    return Advertentie(
        site=site,
        advertentie_id=str(ad_id) if ad_id not in (None, "") else urlparse(link).path,
        link=link,
        titel=str(titel),
        beschrijving=zonder_html(beschrijving) if isinstance(beschrijving, str) else "",
        brandstof=str(brandstof) if brandstof else None,
        transmissie=str(transmissie) if transmissie else None,
        bouwjaar=jaar_uit_plat(plat) or jaar_uit_tekst(str(titel)),
        kilometerstand=lees_km(km),
        vraagprijs=lees_prijs(prijs, pad),
        locatie=str(plaats) if isinstance(plaats, str) else None,
        kenteken=str(kenteken) if isinstance(kenteken, str) else None,
        extra={"cilinderinhoud": cc, "merk_site": merk if isinstance(merk, str) else None,
               "velden": plat},
    )


def advertenties_uit_pagina(html, site, basis_url):
    """Alle advertenties op een zoekpagina, zonder dubbele."""
    gezien, uit = set(), []
    for blok in json_uit_html(html):
        for plat in vind_advertenties(blok):
            try:
                adv = plat_naar_advertentie(plat, site, basis_url)
            except (TypeError, ValueError) as fout:
                log.debug("%s: blokje overgeslagen (%s)", site, fout)
                continue
            if adv.link not in gezien:
                gezien.add(adv.link)
                uit.append(adv)
    return uit


def slug(tekst):
    return re.sub(r"[^a-z0-9]+", "-", tekst.lower()).strip("-")


class AlgemeneZoekSite(Site):
    """Een site waarvan we de zoekpagina's lezen met de algemene herkenning."""

    def __init__(self, ophaler, inst, naam, zoek_url):
        super().__init__(ophaler, inst)
        self.naam = naam
        self.zoek_url = zoek_url
        self.domeinen = [urlparse(zoek_url).netloc]

    def maak_zoek_url(self, merk, model, pagina):
        v = self.inst["vergelijken"]
        return self.zoek_url.format(merk=slug(merk), model=slug(model), pagina=pagina + 1,
                                    min_prijs=v["min_prijs_vergelijkingsauto"],
                                    max_prijs=v["max_prijs_vergelijkingsauto"])

    def hoort_bij_model(self, adv, merk, model):
        if not bevat_woord(adv.titel, [model.lower()]) or is_ander_model(merk, model, adv.titel):
            return False
        merk_site = adv.extra.get("merk_site")
        if merk_site and merk.lower() not in merk_site.lower():
            return False
        return True

    def zoek(self, merk, model, max_paginas, is_bekend):
        for pagina in range(max_paginas):
            url = self.maak_zoek_url(merk, model, pagina)
            html = self.ophaler.haal(url)
            if not html:
                if pagina == 0:
                    log.warning("%s: zoekpagina bestaat niet (%s). Klopt de zoek-URL in instellingen.toml?",
                                self.naam, url)
                break
            gevonden = advertenties_uit_pagina(html, self.naam, url)
            if not gevonden:
                if pagina == 0:
                    log.warning("%s: geen advertenties herkend op %s. Misschien is de site anders "
                                "opgebouwd. Draai verken-sites.bat.", self.naam, url)
                break
            nieuw = 0
            for adv in gevonden:
                if not self.hoort_bij_model(adv, merk, model):
                    continue
                if not is_bekend(adv.advertentie_id):
                    nieuw += 1
                yield adv
            if nieuw == 0:
                break

    def haal_details(self, adv):
        html = self.ophaler.haal(adv.link) if adv.link else None
        if not html:
            return adv
        ld = auto_uit_ld_json(json_uit_html(html), self.naam, adv.link)
        beschrijving = (ld.beschrijving if ld else "") or meta_inhoud(html, "og:description") or ""
        if len(beschrijving) > len(adv.beschrijving or ""):
            adv.beschrijving = beschrijving
            adv.beschrijving_volledig = True
        if ld and not adv.kenteken and ld.kenteken:
            adv.kenteken = ld.kenteken
        return adv

    def haal_advertentie(self, url):
        html = self.ophaler.haal(url)
        if not html:
            return None
        adv = auto_uit_ld_json(json_uit_html(html), self.naam, url)
        if adv is None:
            # Geen standaard auto-blok? Pak dan het eerste advertentie-blokje van de pagina.
            gevonden = advertenties_uit_pagina(html, self.naam, url)
            adv = next((a for a in gevonden if a.link.rstrip("/") == url.rstrip("/")), None)
        if adv is not None:
            adv.link, adv.advertentie_id = url, urlparse(url).path
        return adv
