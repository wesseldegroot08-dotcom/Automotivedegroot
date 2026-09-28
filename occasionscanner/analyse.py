"""De winstberekening.

Stappen:
1. Zoek vergelijkbare auto's (zelfde merk, model, generatie, motor en
   transmissie; bouwjaar max 1 jaar verschil; km max 25.000 verschil).
2. Minder dan 5? Dan "te weinig data" en geen schatting.
3. Geschatte verkoopprijs = mediaan van hun vraagprijzen - 5%.
4. Marge = geschatte verkoopprijs - vraagprijs.
5. Winst = marge - kosten.
6. Melding alleen als marge >= 1000 EN winst >= 750.
"""

import json
from dataclasses import dataclass, field
from statistics import median

from . import database, rdw, rode_vlaggen
from .instellingen import totale_kosten

VERPLICHTE_VELDEN = {
    "generatie": "generatie onbekend of onzeker (wisseljaar tussen twee generaties)",
    "motor_sleutel": "motor niet te herkennen uit de advertentie",
    "transmissie": "transmissie onbekend",
    "bouwjaar": "bouwjaar onbekend",
    "kilometerstand": "kilometerstand onbekend",
    "vraagprijs": "geen vaste vraagprijs",
}

STATUS_TEKST = {
    "melding": "Melding",
    "bijna": "Bijna",
    "geen_winst": "Geen winst",
    "te_weinig_data": "Te weinig data",
}


@dataclass
class Resultaat:
    auto: dict
    status: str = "te_weinig_data"
    redenen: list = field(default_factory=list)       # waarom te weinig data
    vergelijkbaar: list = field(default_factory=list)  # gebruikte auto's
    uitgesloten: list = field(default_factory=list)    # (auto, reden) niet meegeteld
    mediaan: float | None = None
    korting: float | None = None
    verkoopprijs: float | None = None
    marge: float | None = None
    kosten: dict = field(default_factory=dict)
    kosten_totaal: float = 0
    winst: float | None = None
    rode_vlaggen: list = field(default_factory=list)
    rdw: list = field(default_factory=list)            # (in_orde, tekst)

    @property
    def status_tekst(self):
        return STATUS_TEKST[self.status]

    @property
    def is_deal(self):
        return self.status == "melding"

    @property
    def rdw_waarschuwing(self):
        return any(not ok for ok, _ in self.rdw)


def analyseer(conn, auto, inst):
    auto = dict(auto)
    r = Resultaat(auto=auto, kosten=dict(inst["kosten"]), kosten_totaal=totale_kosten(inst))
    v = inst["vergelijken"]
    g = inst["grenzen"]

    r.redenen = [tekst for veld, tekst in VERPLICHTE_VELDEN.items() if auto.get(veld) in (None, "")]

    if not r.redenen:
        for kandidaat in database.vergelijkbare_autos(conn, auto, inst):
            woorden = rode_vlaggen.gevonden_woorden(f"{kandidaat['titel']} {kandidaat['beschrijving']}", inst)
            if woorden:
                # Een auto met "defect" of "schade" drukt de mediaan; die telt niet mee.
                r.uitgesloten.append((dict(kandidaat), f"rode-vlag-woord: {', '.join(woorden)}"))
            else:
                r.vergelijkbaar.append(dict(kandidaat))
        if len(r.vergelijkbaar) < v["min_aantal"]:
            r.redenen.append(f"maar {len(r.vergelijkbaar)} vergelijkbare auto's gevonden, "
                             f"minimaal {v['min_aantal']} nodig")

    if not r.redenen:
        r.mediaan = median(a["vraagprijs"] for a in r.vergelijkbaar)
        r.korting = r.mediaan * v["korting_vraagprijs_procent"] / 100
        r.verkoopprijs = r.mediaan - r.korting
        r.marge = r.verkoopprijs - auto["vraagprijs"]
        r.winst = r.marge - r.kosten_totaal
        if r.marge >= g["min_marge"] and r.winst >= g["min_winst"]:
            r.status = "melding"
        elif r.marge >= g["min_marge"]:
            r.status = "bijna"
        else:
            r.status = "geen_winst"

    r.rode_vlaggen = rode_vlaggen.controleer(auto, inst, r.mediaan)
    if auto.get("kenteken") and auto.get("rdw_gegevens"):
        r.rdw = rdw.controleer(auto, json.loads(auto["rdw_gegevens"]), inst)
    return r


def analyseer_alle(conn, inst):
    """Alle auto's binnen je criteria, gesorteerd op winst (hoogste eerst)."""
    resultaten = [analyseer(conn, a, inst) for a in database.doelautos(conn, inst)]
    resultaten.sort(key=lambda r: (r.winst is None, -(r.winst or 0)))
    return resultaten


def als_tekst(r):
    """De volledige berekening als tekst (voor de terminal)."""
    a = r.auto
    e = lambda x: f"€ {x:>10,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    regels = [
        f"{a['merk']} {a['model']} {a.get('motor') or ''} {a.get('uitvoering') or ''}".strip(),
        f"  {a.get('bouwjaar') or '?'} | {a['kilometerstand'] or '?'} km | {a.get('brandstof') or '?'} | "
        f"{a.get('transmissie') or '?'} | generatie {a.get('generatie') or '?'}",
        f"  {a.get('link') or ''}",
        "",
    ]
    if r.status == "te_weinig_data":
        regels.append("TE WEINIG DATA - geen schatting:")
        regels += [f"  - {x}" for x in r.redenen]
    else:
        regels += [
            f"Mediaan van {len(r.vergelijkbaar)} vergelijkbare auto's   {e(r.mediaan)}",
            f"- {inst_procent(r)}% (vraagprijs is geen verkoopprijs)     {e(-r.korting)}",
            f"= Geschatte verkoopprijs                    {e(r.verkoopprijs)}",
            f"- Vraagprijs                                {e(-a['vraagprijs'])}",
            f"= MARGE                                     {e(r.marge)}",
        ]
        for naam, bedrag in r.kosten.items():
            regels.append(f"- {naam.replace('_', ' '):<42}{e(-bedrag)}")
        regels += [f"= WINST                                     {e(r.winst)}", "",
                   f"Status: {r.status_tekst.upper()}", "", "Gebruikte vergelijkbare auto's:"]
        for c in r.vergelijkbaar:
            regels.append(f"  {c['bouwjaar']}  {c['kilometerstand']:>7} km  € {c['vraagprijs']:>6}  {c['titel'][:50]}")
        for c, reden in r.uitgesloten:
            regels.append(f"  (niet meegeteld: {c['titel'][:40]} - {reden})")
    if r.rode_vlaggen:
        regels += ["", "RODE VLAGGEN:"] + [f"  ! {x}" for x in r.rode_vlaggen]
    if r.rdw:
        regels += ["", "RDW-controle:"] + [f"  {'OK' if ok else '!!'} {t}" for ok, t in r.rdw]
    return "\n".join(regels)


def inst_procent(r):
    return round(r.korting / r.mediaan * 100) if r.mediaan else 0
