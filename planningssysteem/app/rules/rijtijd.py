"""Regel 7 (rij- en rusttijden, EU 561/2006) en regel 8 (arbeidstijd).

Dit is de EXACTE controle. De solver rekent met een benadering; daarna toetst deze code het resultaat.
Let op: de tachograaf is de wettelijke waarheid. Dit systeem voorspelt alleen.

Een dag bestaat uit activiteiten: 'rijden', 'werk' (laden, lossen, wachten) en 'pauze'.
Wachten telt als werk, niet als pauze (Schatting, staat als regel in de database).

Wat we controleren (waarden uit de regeltabel):
- Na 4,5 uur rijden is 45 minuten pauze nodig. Splitsen mag: eerst minimaal 15, dan minimaal 30 minuten.
- Maximaal 9 uur rijden per dag. Twee keer per week mag 10 uur.
- Maximaal 56 uur rijden per week en 90 uur per twee weken.
- Een dienst duurt maximaal 13 uur (bij 11 uur rust, afgeleid).
- Arbeidstijd: bij 6 tot 9 uur werk minimaal 30 minuten pauze, bij meer dan 9 uur minimaal 45.
  Nooit meer dan 6 uur werken zonder pauze.
"""

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta

from app.rules.basis import RegelBoek


@dataclass
class Activiteit:
    soort: str  # rijden, werk, pauze
    start: datetime
    eind: datetime
    rit_id: int | None = None

    @property
    def minuten(self) -> int:
        return int((self.eind - self.start).total_seconds() // 60)


@dataclass
class Overtreding:
    regel_nr: int
    tekst: str
    tijdstip: datetime | None = None
    rit_id: int | None = None
    bedrag_cent: int | None = None


@dataclass
class RijtijdUitslag:
    rijtijd_min: int = 0
    werktijd_min: int = 0
    pauze_min: int = 0
    dienst_min: int = 0
    rest_dag_min: int = 0
    rest_week_min: int = 0
    verlengde_dag: bool = False
    overtredingen: list[Overtreding] = field(default_factory=list)  # regel 7: rijtijd
    arbeid: list[Overtreding] = field(default_factory=list)  # regel 8: arbeidstijd (waarschuwing)
    overwerk_min: int = 0

    @property
    def ok(self) -> bool:
        return not self.overtredingen


@dataclass
class Geschiedenis:
    """Rijtijd van eerdere dagen (uit de tachograaf of handmatig)."""

    rijtijd_deze_week_min: int = 0  # maandag tot en met gisteren
    rijtijd_vorige_week_min: int = 0
    verlengde_dagen_deze_week: int = 0


def vul_pauzes_aan(activiteiten: list[Activiteit]) -> list[Activiteit]:
    """Sorteer en vul gaten tussen activiteiten op met 'pauze'."""
    acts = sorted(activiteiten, key=lambda a: a.start)
    uit: list[Activiteit] = []
    for a in acts:
        if uit and a.start > uit[-1].eind:
            uit.append(Activiteit("pauze", uit[-1].eind, a.start))
        uit.append(a)
    return uit


def _r(boek: RegelBoek, code: str, d: date, standaard: int) -> int:
    return boek.waarde(code, d, standaard)


def controleer_dag(boek: RegelBoek, d: date, activiteiten: list[Activiteit],
                   geschiedenis: Geschiedenis | None = None, contracturen_week: int | None = None) -> RijtijdUitslag:
    g = geschiedenis or Geschiedenis()
    acts = vul_pauzes_aan(activiteiten)
    uit = RijtijdUitslag()
    if not acts:
        uit.rest_dag_min = _r(boek, "rijtijd.dag", d, 540)
        return uit

    na_rijden = _r(boek, "pauze.na_rijden", d, 270)
    pauze_heel = _r(boek, "pauze.duur", d, 45)
    deel1 = _r(boek, "pauze.deel1", d, 15)
    deel2 = _r(boek, "pauze.deel2", d, 30)

    # 1. Pauze na 4,5 uur rijden
    teller = 0
    eerste_deel = False
    gemeld = False
    for a in acts:
        if a.soort == "pauze":
            if a.minuten >= pauze_heel or (eerste_deel and a.minuten >= deel2):
                teller, eerste_deel, gemeld = 0, False, False
            elif a.minuten >= deel1:
                eerste_deel = True
        elif a.soort == "rijden":
            if teller + a.minuten > na_rijden and not gemeld:
                moment = a.start + timedelta(minutes=na_rijden - teller)
                uit.overtredingen.append(Overtreding(
                    7, f"Meer dan {na_rijden // 60} u {na_rijden % 60} min rijden zonder pauze van {pauze_heel} "
                    f"minuten (of {deel1} + {deel2}). Pauze nodig vóór {moment:%H:%M} UTC.", moment, a.rit_id))
                gemeld = True
            teller += a.minuten

    # 2. Rijtijd per dag
    uit.rijtijd_min = sum(a.minuten for a in acts if a.soort == "rijden")
    uit.werktijd_min = sum(a.minuten for a in acts if a.soort in ("rijden", "werk"))
    uit.pauze_min = sum(a.minuten for a in acts if a.soort == "pauze")
    dag_max = _r(boek, "rijtijd.dag", d, 540)
    dag_lang = _r(boek, "rijtijd.dag.verlengd", d, 600)
    max_verlengd = _r(boek, "rijtijd.verlengd.per_week", d, 2)
    laatste_rit = next((a.rit_id for a in reversed(acts) if a.rit_id), None)
    if uit.rijtijd_min > dag_max:
        if uit.rijtijd_min <= dag_lang and g.verlengde_dagen_deze_week < max_verlengd:
            uit.verlengde_dag = True
        else:
            reden = (f"meer dan {dag_lang // 60} uur" if uit.rijtijd_min > dag_lang
                     else f"10 uur mag maar {max_verlengd} keer per week (al {g.verlengde_dagen_deze_week} keer)")
            uit.overtredingen.append(Overtreding(7, f"Rijtijd vandaag {uit.rijtijd_min // 60} u {uit.rijtijd_min % 60} "
                                                 f"min: {reden}.", acts[-1].eind, laatste_rit))
    limiet_vandaag = dag_lang if (uit.verlengde_dag or g.verlengde_dagen_deze_week < max_verlengd) else dag_max

    # 3. Week en twee weken
    week = _r(boek, "rijtijd.week", d, 3360)
    twee = _r(boek, "rijtijd.twee_weken", d, 5400)
    deze_week = g.rijtijd_deze_week_min + uit.rijtijd_min
    if deze_week > week:
        uit.overtredingen.append(Overtreding(7, f"Rijtijd deze week wordt {deze_week // 60} uur (max {week // 60}).",
                                             acts[-1].eind, laatste_rit))
    if deze_week + g.rijtijd_vorige_week_min > twee:
        uit.overtredingen.append(Overtreding(
            7, f"Rijtijd in twee weken wordt {(deze_week + g.rijtijd_vorige_week_min) // 60} uur (max {twee // 60}).",
            acts[-1].eind, laatste_rit))

    # 4. Dienstlengte
    uit.dienst_min = int((acts[-1].eind - acts[0].start).total_seconds() // 60)
    dienst_max = _r(boek, "dienst.max", d, 780)
    if uit.dienst_min > dienst_max:
        uit.overtredingen.append(Overtreding(7, f"Dienst duurt {uit.dienst_min // 60} u {uit.dienst_min % 60} min "
                                             f"(max {dienst_max // 60} uur bij 11 uur rust).", acts[-1].eind,
                                             laatste_rit))
    uit.rest_dag_min = max(0, limiet_vandaag - uit.rijtijd_min)
    uit.rest_week_min = max(0, week - deze_week)
    uit.rest_dag_min = min(uit.rest_dag_min, uit.rest_week_min)

    # 5. Arbeidstijd (regel 8, waarschuwing)
    p69 = _r(boek, "arbeid.pauze.6_9", d, 30)
    p9 = _r(boek, "arbeid.pauze.9plus", d, 45)
    max_zonder = _r(boek, "arbeid.max_zonder_pauze", d, 360)
    pauzes_geldig = sum(a.minuten for a in acts if a.soort == "pauze" and a.minuten >= 15)
    werk = uit.werktijd_min
    nodig = p9 if werk > 540 else (p69 if werk >= 360 else 0)
    if pauzes_geldig < nodig:
        uit.arbeid.append(Overtreding(8, f"{werk // 60} u {werk % 60} min werk vraagt minimaal {nodig} min pauze. "
                                      f"Gepland: {pauzes_geldig} min.", acts[-1].eind, laatste_rit))
    aaneen = 0
    for a in acts:
        if a.soort == "pauze" and a.minuten >= 15:
            aaneen = 0
            continue
        if a.soort in ("rijden", "werk"):
            aaneen += a.minuten
            if aaneen > max_zonder:
                uit.arbeid.append(Overtreding(8, f"Meer dan {max_zonder // 60} uur werken zonder pauze.",
                                              a.eind, a.rit_id))
                break
    if contracturen_week:
        dag_contract = contracturen_week * 60 // 5
        uit.overwerk_min = max(0, werk - dag_contract)
    return uit
