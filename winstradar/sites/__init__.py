"""Overzicht van alle site-modules.

- Marktplaats heeft een eigen module (marktplaats.py).
- De andere sites gebruiken de algemene module (algemeen.py). Hun zoek-URL
  staat in instellingen.toml onder [zoek_urls].

Een nieuwe site toevoegen:
1. Zet onder [zoek_urls] een regel: sitenaam = "https://...{merk}...{model}...{pagina}..."
2. Zet onder [sites] een regel: sitenaam = true
3. Draai verken-sites.bat om te kijken of het werkt.
"""

from urllib.parse import urlparse

from .algemeen import AlgemeneZoekSite
from .basis import AlgemeneSite
from .marktplaats import Marktplaats

EIGEN_MODULES = {"marktplaats": Marktplaats}


def maak_site(naam, ophaler, inst):
    if naam in EIGEN_MODULES:
        return EIGEN_MODULES[naam](ophaler, inst)
    url = inst.get("zoek_urls", {}).get(naam)
    return AlgemeneZoekSite(ophaler, inst, naam, url) if url else None


def alle_sitenamen(inst):
    return list(EIGEN_MODULES) + [n for n in inst.get("zoek_urls", {}) if n not in EIGEN_MODULES]


def actieve_sites(ophaler, inst):
    aan = inst.get("sites", {})
    sites = [maak_site(naam, ophaler, inst) for naam in alle_sitenamen(inst) if aan.get(naam, False)]
    return [s for s in sites if s is not None]


def site_voor_link(url, ophaler, inst):
    host = urlparse(url).netloc.lower()
    for naam in alle_sitenamen(inst):
        site = maak_site(naam, ophaler, inst)
        if site is not None and host in site.domeinen:
            return site
    return AlgemeneSite(ophaler, inst)
