"""Module voor Marktplaats.

Eerlijke waarschuwing: Marktplaats kan zijn website op elk moment veranderen.
Dan vindt deze module geen advertenties meer. De tool schrijft dat in het
logboek. Met `python main.py test-marktplaats` kun je snel kijken of het nog werkt.

Hoe het werkt:
1. Eerst proberen we de zoekresultaten als JSON op te halen (dat gebruikt de
   website zelf ook). Staat robots.txt dat niet toe? Dan proberen we de gewone
   zoekpagina. Staat robots.txt dat ook niet toe? Dan stopt de module.
2. Van elke advertentie halen we titel, prijs, bouwjaar, km, enz.
3. Voor auto's die binnen je zoekcriteria vallen, halen we ook de
   advertentiepagina op (volledige beschrijving en misschien het kenteken).
"""

import re
from urllib.parse import quote_plus

from ..advertentie import Advertentie
from ..logboek import log
from ..normaliseren import lees_getal, bevat_woord
from ..generaties import is_ander_model
from ..ophalen import NietToegestaan
from .basis import (Site, zoek_dicts, json_uit_html, zonder_html, meta_inhoud,
                    jaar_uit_tekst, km_uit_tekst, auto_uit_ld_json)

BASIS = "https://www.marktplaats.nl"
API = BASIS + "/lrp/api/search"
CATEGORIE_AUTOS = 91
PER_PAGINA = 30


def _is_listing(d):
    return "itemId" in d and "title" in d


def _attributen(d):
    """Zet de lijst met kenmerken om naar {sleutel: waarde} met kleine letters."""
    uit = {}
    for lijst_naam in ("attributes", "extendedAttributes"):
        for a in d.get(lijst_naam) or []:
            if not isinstance(a, dict):
                continue
            sleutel = str(a.get("key") or a.get("label") or "").lower()
            waarde = a.get("value")
            if waarde is None and a.get("values"):
                waarde = a["values"][0]
            if sleutel and waarde is not None:
                uit[sleutel] = str(waarde)
    return uit


def _zoek_attr(attr, *namen):
    for sleutel, waarde in attr.items():
        if any(n in sleutel for n in namen):
            return waarde
    return None


def listing_naar_advertentie(d):
    """Maakt van één Marktplaats-advertentie (JSON) een Advertentie."""
    attr = _attributen(d)
    titel = d.get("title") or ""
    beschrijving = zonder_html(d.get("description") or "")
    tekst = f"{titel} {beschrijving}"

    prijs_info = d.get("priceInfo") or {}
    centen = prijs_info.get("priceCents")
    prijs = round(centen / 100) if isinstance(centen, (int, float)) and centen > 0 else None

    link = d.get("vipUrl") or ""
    if link.startswith("/"):
        link = BASIS + link

    locatie = d.get("location") or {}
    bouwjaar = lees_getal(_zoek_attr(attr, "constructionyear", "bouwjaar", "year"))
    km = lees_getal(_zoek_attr(attr, "mileage", "kilometerstand"))

    return Advertentie(
        site="marktplaats",
        advertentie_id=str(d["itemId"]),
        link=link,
        titel=titel,
        beschrijving=beschrijving,
        brandstof=_zoek_attr(attr, "fuel", "brandstof"),
        transmissie=_zoek_attr(attr, "transmission", "transmissie"),
        bouwjaar=bouwjaar or jaar_uit_tekst(titel),
        kilometerstand=km if km is not None else km_uit_tekst(tekst),
        vraagprijs=prijs,
        locatie=locatie.get("cityName") if isinstance(locatie, dict) else None,
        kenteken=_zoek_attr(attr, "licenseplate", "kenteken"),
        extra={"cilinderinhoud": _zoek_attr(attr, "enginedisplacement", "cilinderinhoud", "cylinder"),
               "prijstype": prijs_info.get("priceType")},
    )


def hoort_bij_model(adv, merk, model):
    """Is dit echt een <merk> <model>? Zoekresultaten bevatten soms andere auto's."""
    if not bevat_woord(adv.titel, [model.lower()]):
        return False
    if is_ander_model(merk, model, adv.titel):
        return False
    # In de link staat het merk, bv. /v/auto-s/volkswagen/...
    if "/auto-s/" in adv.link and merk.lower().replace(" ", "-") not in adv.link.lower():
        return False
    return True


class Marktplaats(Site):
    naam = "marktplaats"
    domeinen = ["marktplaats.nl", "www.marktplaats.nl"]

    def _pagina_via_api(self, zoekterm, pagina):
        v = self.inst["vergelijken"]
        params = {
            "l1CategoryId": CATEGORIE_AUTOS,
            "limit": PER_PAGINA,
            "offset": pagina * PER_PAGINA,
            "query": zoekterm,
            "searchInTitleAndDescription": "false",
            "sortBy": "SORT_INDEX",
            "sortOrder": "DECREASING",
            "viewOptions": "list-view",
            "attributeRanges[]": f"PriceCents:{v['min_prijs_vergelijkingsauto'] * 100}:"
                                 f"{v['max_prijs_vergelijkingsauto'] * 100}",
        }
        return self.ophaler.haal(API, params=params, json_verwacht=True)

    def _pagina_via_html(self, zoekterm, pagina):
        url = f"{BASIS}/l/auto-s/q/{quote_plus(zoekterm)}/"
        if pagina > 0:
            url += f"p/{pagina + 1}/"
        html = self.ophaler.haal(url)
        return json_uit_html(html) if html else None

    def zoek(self, merk, model, max_paginas, is_bekend):
        zoekterm = f"{merk} {model}".lower()
        methode = None
        for pagina in range(max_paginas):
            data = None
            for naam, functie in (("api", self._pagina_via_api), ("html", self._pagina_via_html)):
                if methode and methode != naam:
                    continue
                try:
                    data = functie(zoekterm, pagina)
                    methode = naam
                    break
                except NietToegestaan as fout:
                    log.info("Marktplaats: %s", fout)
            if methode is None:
                raise NietToegestaan("robots.txt van Marktplaats staat geen van beide zoekmethodes toe")
            if not data:
                break

            listings = list(zoek_dicts(data, _is_listing))
            if not listings:
                if pagina == 0:
                    log.warning("Marktplaats: geen advertenties gevonden voor '%s'. "
                                "Misschien is de website veranderd.", zoekterm)
                break

            nieuw_op_pagina = 0
            for d in listings:
                try:
                    adv = listing_naar_advertentie(d)
                except (KeyError, TypeError, ValueError) as fout:
                    log.debug("Marktplaats: advertentie overgeslagen (%s)", fout)
                    continue
                if not hoort_bij_model(adv, merk, model):
                    continue
                if not is_bekend(adv.advertentie_id):
                    nieuw_op_pagina += 1
                yield adv

            # Alles op deze pagina kenden we al? Dan zijn de volgende pagina's ook oud.
            if nieuw_op_pagina == 0 or len(listings) < PER_PAGINA:
                break

    def _vul_uit_pagina(self, adv, html):
        blokken = json_uit_html(html)
        eigen = [d for b in blokken for d in zoek_dicts(b, _is_listing)
                 if str(d.get("itemId")) == adv.advertentie_id]
        if eigen:
            vol = listing_naar_advertentie(eigen[0])
            for veld in ("beschrijving", "brandstof", "transmissie", "bouwjaar",
                         "kilometerstand", "vraagprijs", "kenteken", "locatie"):
                if getattr(vol, veld):
                    setattr(adv, veld, getattr(vol, veld))
            adv.extra.update({k: v for k, v in vol.extra.items() if v})
        else:
            ld = auto_uit_ld_json(blokken, self.naam, adv.link)
            if ld and ld.beschrijving:
                adv.beschrijving = ld.beschrijving
            elif meta_inhoud(html, "og:description"):
                adv.beschrijving = meta_inhoud(html, "og:description")
        # Het kenteken staat soms alleen als tekst op de pagina
        if not adv.kenteken:
            m = re.search(r"Kenteken\s*</[^>]+>\s*<[^>]+>\s*([A-Z0-9-]{6,8})", html)
            if m:
                adv.kenteken = m.group(1)
        adv.beschrijving_volledig = bool(adv.beschrijving)
        return adv

    def haal_details(self, adv):
        if not adv.link:
            return adv
        html = self.ophaler.haal(adv.link)
        return self._vul_uit_pagina(adv, html) if html else adv

    def haal_advertentie(self, url):
        m = re.search(r"/(m\d+|a\d+)", url)
        if not m:
            raise ValueError("Dit lijkt geen link naar een Marktplaats-advertentie.")
        html = self.ophaler.haal(url)
        if not html:
            return None
        blokken = json_uit_html(html)
        # Een advertentiepagina toont ook "vergelijkbare advertenties". Pak de juiste.
        eigen = [d for b in blokken for d in zoek_dicts(b, _is_listing) if str(d.get("itemId")) == m.group(1)]
        if eigen:
            adv = listing_naar_advertentie(eigen[0])
            adv.link = adv.link or url
        else:
            adv = auto_uit_ld_json(blokken, self.naam, url)
            if adv is None:
                titel = meta_inhoud(html, "og:title") or ""
                adv = Advertentie(site=self.naam, advertentie_id=m.group(1), link=url, titel=titel)
            adv.advertentie_id = m.group(1)
        return self._vul_uit_pagina(adv, html)
