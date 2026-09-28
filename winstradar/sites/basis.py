"""Basis voor elke site-module.

Elke site (Marktplaats, AutoScout24, ...) is een losse module met dezelfde
functies. Gaat er iets mis bij één site, dan werkt de rest gewoon door.
"""

import html as html_lib
import json
import re

from ..advertentie import Advertentie
from ..normaliseren import lees_getal


class Site:
    naam = "basis"
    domeinen: list[str] = []

    def __init__(self, ophaler, inst):
        self.ophaler = ophaler
        self.inst = inst

    def zoek(self, merk, model, max_paginas, is_bekend):
        """Geeft advertenties terug (generator). is_bekend(id) zegt of we hem al hebben."""
        raise NotImplementedError

    def haal_details(self, adv):
        """Haalt de advertentiepagina op voor de volledige beschrijving en het kenteken."""
        return adv

    def haal_advertentie(self, url):
        """Voor als je zelf een link plakt."""
        raise NotImplementedError


# ---------- hulpfuncties die elke site kan gebruiken ----------

def zoek_dicts(obj, test):
    """Loopt door een JSON-boom en geeft alle dictionaries waarvoor test(d) waar is."""
    stapel = [obj]
    while stapel:
        huidig = stapel.pop()
        if isinstance(huidig, dict):
            if test(huidig):
                yield huidig
            stapel.extend(huidig.values())
        elif isinstance(huidig, list):
            stapel.extend(huidig)


def json_uit_html(pagina):
    """Haalt de JSON-blokken uit een HTML-pagina die sites gebruiken om hun data mee te sturen."""
    blokken = []
    decoder = json.JSONDecoder()
    for m in re.finditer(r'<script[^>]*type="application/(?:ld\+)?json"[^>]*>(.*?)</script>', pagina, re.S):
        try:
            blokken.append(json.loads(m.group(1)))
        except ValueError:
            pass
    for m in re.finditer(r"window\.__[A-Z_]+__\s*=\s*", pagina):
        try:
            blok, _ = decoder.raw_decode(pagina, m.end())
            blokken.append(blok)
        except ValueError:
            pass
    return blokken


def zonder_html(tekst):
    if not tekst:
        return ""
    tekst = re.sub(r"<br\s*/?>|</p>", "\n", tekst, flags=re.I)
    tekst = re.sub(r"<[^>]+>", " ", tekst)
    tekst = html_lib.unescape(tekst)
    return re.sub(r"[ \t]+", " ", tekst).strip()


def meta_inhoud(pagina, eigenschap):
    m = re.search(rf'<meta[^>]+(?:property|name)="{re.escape(eigenschap)}"[^>]+content="([^"]*)"', pagina)
    return html_lib.unescape(m.group(1)) if m else None


def jaar_uit_tekst(tekst):
    m = re.search(r"bouwjaar\s*:?\s*((?:19|20)\d\d)", tekst, re.I) or re.search(r"\b(20[0-3]\d)\b", tekst)
    return int(m.group(1)) if m else None


def km_uit_tekst(tekst):
    m = re.search(r"(\d{1,3}(?:[.\s]\d{3})+|\d{4,6})\s*(?:km|kilometer)", tekst, re.I)
    return lees_getal(m.group(1)) if m else None


def auto_uit_ld_json(blokken, site, url):
    """Veel autosites zetten een standaard 'Car'-blok in hun pagina (schema.org).

    Daarmee kunnen we ook een geplakte link van een onbekende site doorrekenen.
    """
    for blok in blokken:
        for d in zoek_dicts(blok, lambda d: str(d.get("@type", "")).lower() in ("car", "vehicle", "product")):
            if "vehicleModelDate" not in d and "mileageFromOdometer" not in d and d.get("@type") == "Product":
                continue
            aanbod = d.get("offers") or {}
            if isinstance(aanbod, list):
                aanbod = aanbod[0] if aanbod else {}
            km = d.get("mileageFromOdometer")
            if isinstance(km, dict):
                km = km.get("value")
            merk = d.get("brand")
            if isinstance(merk, dict):
                merk = merk.get("name")
            return Advertentie(
                site=site, advertentie_id=url, link=url,
                titel=d.get("name") or "",
                beschrijving=zonder_html(d.get("description") or ""),
                beschrijving_volledig=True,
                bouwjaar=lees_getal(str(d.get("vehicleModelDate") or d.get("productionDate") or "")[:4]),
                kilometerstand=lees_getal(km),
                vraagprijs=lees_getal(str(aanbod.get("price", "")).split(".")[0].split(",")[0]),
                brandstof=(d.get("fuelType") or None),
                transmissie=(d.get("vehicleTransmission") or None),
                extra={"merk_site": merk, "model_site": d.get("model")},
            )
    return None


class AlgemeneSite(Site):
    """Voor een geplakte link van een site zonder eigen module.

    Werkt alleen als de pagina een standaard auto-blok (schema.org) heeft.
    """
    naam = "overig"

    def haal_advertentie(self, url):
        pagina = self.ophaler.haal(url)
        if not pagina:
            return None
        return auto_uit_ld_json(json_uit_html(pagina), self.naam, url)
