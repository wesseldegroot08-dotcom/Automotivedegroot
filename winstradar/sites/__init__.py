"""Overzicht van alle site-modules.

Een nieuwe site toevoegen (bv. AutoScout24):
1. Maak winstradar/sites/autoscout24.py met een class die van Site erft.
2. Voeg hem hieronder toe aan ALLE_SITES.
3. Zet `autoscout24 = true` in instellingen.toml onder [sites].
"""

from urllib.parse import urlparse

from .basis import AlgemeneSite
from .marktplaats import Marktplaats

ALLE_SITES = {
    "marktplaats": Marktplaats,
    # "autoscout24": AutoScout24,   # nog niet gebouwd
    # "gaspedaal": Gaspedaal,       # nog niet gebouwd
    # "autotrack": AutoTrack,       # nog niet gebouwd
    # "autowereld": Autowereld,     # nog niet gebouwd
}


def actieve_sites(ophaler, inst):
    aan = inst.get("sites", {})
    return [klasse(ophaler, inst) for naam, klasse in ALLE_SITES.items() if aan.get(naam, False)]


def site_voor_link(url, ophaler, inst):
    host = urlparse(url).netloc.lower()
    for klasse in ALLE_SITES.values():
        if host in klasse.domeinen:
            return klasse(ophaler, inst)
    return AlgemeneSite(ophaler, inst)
