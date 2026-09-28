"""Vult een aparte demo-database met verzonnen auto's.

Zo kun je het dashboard bekijken zonder dat de tool iets van internet haalt.
De demo-database (data/demo.db) staat los van je echte database.
"""

import random
from datetime import datetime, timedelta

from . import database
from .advertentie import Advertentie
from .normaliseren import vul_aan

# (merk, model, titel, jaar, km, prijs, transmissie, beschrijving, kenteken)
DOELAUTOS = [
    ("Volkswagen", "Polo", "Volkswagen Polo 1.2 TSI Comfortline", 2014, 142000, 3100, "Handgeschakeld",
     "Nette Polo, dealer onderhouden, nieuwe remmen en banden. Airco, cruise control, 5 deurs. "
     "Onderhoudsboekjes aanwezig en tweede eigenaar. APK tot volgend jaar juni. Rijdt en schakelt perfect.", "KX218T"),
    ("Toyota", "Yaris", "Toyota Yaris 1.33 VVT-i Aspiration", 2013, 118000, 3450, "Handgeschakeld",
     "Zuinige Yaris met airco en bluetooth. Altijd bij Toyota onderhouden, facturen aanwezig. "
     "Distributieketting dus geen riem nodig. Kleine kras op achterbumper, verder netjes.", None),
    ("Renault", "Clio", "Renault Clio 0.9 TCe Expression", 2015, 131000, 2450, "Handgeschakeld",
     "Clio met motorstoring, lampje brandt. Verder rijdt hij.", None),
    ("Ford", "Focus", "Ford Focus 1.0 EcoBoost Titanium", 2014, 163000, 2950, "Handgeschakeld",
     "Focus Titanium met navigatie, climate control, parkeersensoren en stoelverwarming. "
     "Distributieriem vervangen bij 150.000 km. Twee sleutels. Inruil mogelijk.", None),
    ("Opel", "Astra", "Opel Astra 1.4 Turbo Sport automaat", 2013, 149000, 3300, "Automaat",
     "Astra automaat, sport uitvoering, lichtmetalen velgen. Goed onderhouden en APK tot 2027.", None),
    ("Renault", "Clio", "Renault Clio opknapper", 2014, None, 2100, "Handgeschakeld",
     "Opknapper, meeneemprijs. Bel voor info.", None),
]

PRIJZEN_VERGELIJK = {
    "Volkswagen Polo 1.2 TSI": [4950, 4600, 4750, 5100, 4400, 4850, 4700],
    "Toyota Yaris 1.33 VVT-i": [4900, 5200, 4650, 4800, 5000],
    "Renault Clio 0.9 TCe": [4100, 3950, 4300, 4000, 4250, 4150],
    "Ford Focus 1.0 EcoBoost": [3900, 3750, 4100, 3850, 4000],
    "Opel Astra 1.4 Turbo": [4200, 4450, 3990],
}


def vul_demo(pad):
    if pad.exists():
        pad.unlink()
    conn = database.verbind(pad)
    rnd = random.Random(1)
    nu = datetime.now()
    teller = 0
    for merk, model, titel, jaar, km, prijs, tr, tekst, kenteken in DOELAUTOS:
        teller += 1
        adv = Advertentie(site="demo", advertentie_id=f"doel{teller}", link="", titel=titel,
                          beschrijving=tekst, beschrijving_volledig=True, transmissie=tr, bouwjaar=jaar,
                          kilometerstand=km, vraagprijs=prijs, locatie=rnd.choice(["Utrecht", "Zwolle", "Breda"]),
                          kenteken=kenteken)
        vul_aan(adv, merk, model)
        database.sla_op(conn, adv, (nu - timedelta(hours=teller)).isoformat(timespec="seconds"))

        sleutel = next((k for k in PRIJZEN_VERGELIJK if titel.startswith(k)), None)
        for i, p in enumerate(PRIJZEN_VERGELIJK.get(sleutel, [])):
            teller += 1
            v = Advertentie(site="demo", advertentie_id=f"verg{teller}", link="", titel=f"{sleutel} (vergelijking)",
                            beschrijving="Vergelijkingsauto.", transmissie=tr, bouwjaar=jaar + [0, -1, 1][i % 3],
                            kilometerstand=(km or 0) + [-12000, 8000, -20000, 15000, 3000, -6000, 22000][i % 7],
                            vraagprijs=p, locatie="Nederland")
            vul_aan(v, merk, model)
            database.sla_op(conn, v, (nu - timedelta(days=i + 1)).isoformat(timespec="seconds"))
    conn.close()
