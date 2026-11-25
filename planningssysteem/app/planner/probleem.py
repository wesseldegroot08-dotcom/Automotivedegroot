"""Het planprobleem als gewone gegevens, los van de database en los van de solver.

Zo kan later een andere solver dezelfde invoer gebruiken (interface: Solver.los_op).
Alle tijden zijn minuten vanaf middernacht (Nederlandse tijd) van de plandag.
"""

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, time, timedelta
from typing import Protocol

from app import models as m
from app.planner.context import DagContext
from app.planner.voorfilter import beschikbare_chauffeurs, eenheden, toegestane_paren
from app.ports.clock import NL

VAST = ("toegezegd", "gestart")


@dataclass
class Taak:
    rit_id: int
    naam: str
    van_id: int
    naar_id: int
    laden_min: int
    reis_min: int
    reis_km: int
    lossen_min: int
    start_min: int  # vroegste begintijd (aankomst ophaalplek)
    start_max: int  # laatste begintijd
    prioriteit: int = 1  # 2 = LFD vandaag of eerder: niet plannen kost extra
    vast: bool = False
    vast_start: int | None = None
    vast_eenheid: str | None = None
    vast_chauffeur: int | None = None
    hint_eenheid: str | None = None
    hint_chauffeur: int | None = None
    hint_start: int | None = None

    @property
    def duur(self) -> int:
        return self.laden_min + self.reis_min + self.lossen_min


@dataclass
class EenheidInvoer:
    sleutel: str  # "trekker_id-chassis_id"
    trekker_id: int
    chassis_id: int
    naam: str


@dataclass
class ChauffeurInvoer:
    id: int
    naam: str
    begin_min: int
    eind_min: int  # einde contractdag: later mag, maar kost overwerk
    rest_rij_min: int  # rijtijd die vandaag nog mag (dag, week en twee weken)
    voorkeur_trekker_id: int | None = None


@dataclass
class Probleem:
    datum: str
    standplaats_id: int | None
    taken: list[Taak] = field(default_factory=list)
    eenheden: list[EenheidInvoer] = field(default_factory=list)
    chauffeurs: list[ChauffeurInvoer] = field(default_factory=list)
    toegestaan: dict[int, list[tuple[str, int]]] = field(default_factory=dict)
    reis: dict[tuple[int, int], tuple[int, int]] = field(default_factory=dict)  # (van, naar) -> (minuten, km)
    niet_te_plannen: dict[int, str] = field(default_factory=dict)
    verboden: set[tuple[int, str]] = field(default_factory=set)
    staat: list[str] = field(default_factory=list)  # ruwe stand van ritten, orders, vrijgaven en slots (voor de hash)
    # benadering rij- en rusttijd (waarden uit de regeltabel)
    max_rij_dag: int = 540
    pauze_na: int = 270
    pauze_duur: int = 45
    max_dienst: int = 780

    def reistijd(self, van: int | None, naar: int | None) -> tuple[int, int]:
        if van is None or naar is None or van == naar:
            return (0, 0)
        return self.reis.get((van, naar), (0, 0))

    def naar_json(self) -> str:
        d = asdict(self)
        d["reis"] = [[a, b, mi, km] for (a, b), (mi, km) in sorted(self.reis.items())]
        d["verboden"] = sorted([list(v) for v in self.verboden])
        d["toegestaan"] = {str(k): v for k, v in sorted(self.toegestaan.items())}
        d["niet_te_plannen"] = {str(k): v for k, v in sorted(self.niet_te_plannen.items())}
        return json.dumps(d, sort_keys=True, ensure_ascii=False)

    def invoer_hash(self) -> str:
        """Vingerafdruk van de invoer. Verandert het plan, dan verandert de hash."""
        return hashlib.sha256(self.naar_json().encode()).hexdigest()


@dataclass
class Toewijzing:
    eenheid: str
    chauffeur_id: int
    start_min: int


@dataclass
class Oplossing:
    status: str  # OPTIMAAL, GOED (tijdlimiet), GEEN, FOUT
    toewijzingen: dict[int, Toewijzing] = field(default_factory=dict)
    ongepland: dict[int, str] = field(default_factory=dict)
    rekentijd_ms: int = 0


class Solver(Protocol):
    def los_op(self, probleem: Probleem, tijdlimiet_sec: float) -> Oplossing: ...


# ---------------------------------------------------------------- van de database naar een probleem


def dag_begin(ctx: DagContext) -> datetime:
    return datetime.combine(ctx.datum, time()).replace(tzinfo=NL)


def naar_min(ctx: DagContext, t: datetime) -> int:
    return int((t - dag_begin(ctx)).total_seconds() // 60)


def van_min(ctx: DagContext, minuten: int) -> datetime:
    return dag_begin(ctx) + timedelta(minutes=minuten)


def _tijd_min(t: time) -> int:
    return t.hour * 60 + t.minute


def eenheid_sleutel(trekker_id: int, chassis_id: int) -> str:
    return f"{trekker_id}-{chassis_id}"


def _venster(ctx: DagContext, rit: m.Rit, duur) -> tuple[int, int, str | None]:
    """Vroegste en laatste begintijd uit klantvenster, openingstijden en slot."""
    o = rit.order
    lo, hi = 0, 24 * 60 - duur.totaal_min
    # klantvenster: geldt voor aankomst bij de klant (afleveren) of voor het ophalen
    tot_klant = duur.laden_min + duur.reis.minuten if rit.naar_locatie.type == "klant" else 0
    lo = max(lo, naar_min(ctx, o.venster_van) - tot_klant)
    hi = min(hi, naar_min(ctx, o.venster_tot) - tot_klant)
    # openingstijden (alleen als ze niet over middernacht gaan)
    dag = str(ctx.datum.isoweekday())
    for loc, voor in ((rit.van_locatie, 0), (rit.naar_locatie, duur.laden_min + duur.reis.minuten)):
        if dag not in loc.open_dagen:
            return lo, hi, f"{loc.naam} is op deze dag gesloten"
        if loc.open_van <= loc.open_tot:
            lo = max(lo, _tijd_min(loc.open_van) - voor)
            na = duur.laden_min if voor == 0 else duur.lossen_min
            hi = min(hi, _tijd_min(loc.open_tot) - voor - na)
    # slot (als er al een slot is, moet de aankomst erin passen)
    for s in ctx.slots_per_rit.get(rit.id, []):
        if s.status not in ("Toegekend", "Gewijzigd") or not s.slot_van:
            continue
        tr = ctx.terminalregels.get(s.terminal_id)
        tol = (tr.tolerantie_min or 0) if tr else 0
        voor = 0 if s.terminal_id == rit.van_locatie_id else duur.laden_min + duur.reis.minuten
        lo = max(lo, naar_min(ctx, s.slot_van) - tol - voor)
        hi = min(hi, naar_min(ctx, s.slot_tot) + tol - voor)
    if lo > hi:
        delen = [f"klant {o.venster_van.astimezone(NL):%H:%M}-{o.venster_tot.astimezone(NL):%H:%M}"]
        if ctx.slots_per_rit.get(rit.id):
            delen.append("slot")
        delen.append("openingstijden")
        return lo, hi, "Tijden passen niet samen (" + ", ".join(delen) + ")"
    return lo, hi, None


def bouw_probleem(ctx: DagContext, verboden: set[tuple[int, str]] | None = None) -> Probleem:
    boek, d = ctx.boek, ctx.datum
    p = Probleem(datum=d.isoformat(), standplaats_id=ctx.standplaats.id if ctx.standplaats else None,
                 verboden=set(verboden or set()),
                 max_rij_dag=boek.waarde("rijtijd.dag", d, 540), pauze_na=boek.waarde("pauze.na_rijden", d, 270),
                 pauze_duur=boek.waarde("pauze.duur", d, 45), max_dienst=boek.waarde("dienst.max", d, 780))
    eenh = eenheden(ctx)
    chauffeurs = beschikbare_chauffeurs(ctx)
    for e in eenh:
        p.eenheden.append(EenheidInvoer(eenheid_sleutel(e.trekker.id, e.chassis.id), e.trekker.id, e.chassis.id,
                                        e.naam))
    week = boek.waarde("rijtijd.week", d, 3360)
    twee = boek.waarde("rijtijd.twee_weken", d, 5400)
    for c in chauffeurs:
        g = ctx.geschiedenis(c.id)
        rest = min(p.max_rij_dag, week - g.rijtijd_deze_week_min,
                   twee - g.rijtijd_deze_week_min - g.rijtijd_vorige_week_min)
        p.chauffeurs.append(ChauffeurInvoer(c.id, c.pseudoniem, _tijd_min(c.standaard_begin),
                                            _tijd_min(c.standaard_eind), max(0, rest), c.voorkeur_trekker_id))
    bekende_eenheden = {e.sleutel for e in p.eenheden}
    bekende_chauffeurs = {c.id for c in p.chauffeurs}
    locaties: set[int] = {p.standplaats_id} if p.standplaats_id else set()
    for rit in ctx.ritten:
        if rit.status in ("Afgerond", "Klaar") or (rit.order and rit.order.status == "Geannuleerd"):
            continue
        duur = ctx.rit_duur(rit)
        naam = f"{rit.order.klantreferentie} ({rit.van_locatie.naam} → {rit.naar_locatie.naam})"
        vast = rit.vastheid in VAST and bool(rit.gepland_start and rit.trekker_id and rit.chassis_id
                                             and rit.chauffeur_id)
        t = Taak(rit.id, naam, rit.van_locatie_id, rit.naar_locatie_id, duur.laden_min, duur.reis.minuten,
                 duur.reis.km, duur.lossen_min, 0, 0)
        locaties |= {rit.van_locatie_id, rit.naar_locatie_id}
        lfd_vandaag = any((v := ctx.vrijgave_per_container.get(c.id)) and v.lfd <= d for c in rit.order.containers)
        t.prioriteit = 2 if lfd_vandaag else 1
        if vast:
            sleutel = eenheid_sleutel(rit.trekker_id, rit.chassis_id)
            t.vast, t.vast_start, t.vast_eenheid, t.vast_chauffeur = True, naar_min(ctx, rit.gepland_start), sleutel, \
                rit.chauffeur_id
            t.start_min = t.start_max = t.vast_start
            if sleutel not in bekende_eenheden:
                p.eenheden.append(EenheidInvoer(sleutel, rit.trekker_id, rit.chassis_id,
                                                f"trekker {rit.trekker.intern_nummer} + chassis {rit.chassis.nummer}"))
                bekende_eenheden.add(sleutel)
            if rit.chauffeur_id not in bekende_chauffeurs:
                c = rit.chauffeur
                p.chauffeurs.append(ChauffeurInvoer(c.id, c.pseudoniem, 0, 24 * 60, p.max_rij_dag,
                                                    c.voorkeur_trekker_id))
                bekende_chauffeurs.add(c.id)
            p.toegestaan[rit.id] = [(sleutel, rit.chauffeur_id)]
            p.taken.append(t)
            continue
        lo, hi, probleem = _venster(ctx, rit, duur)
        t.start_min, t.start_max = lo, hi
        if rit.gepland_start and rit.trekker_id and rit.chassis_id and rit.chauffeur_id:
            t.hint_eenheid = eenheid_sleutel(rit.trekker_id, rit.chassis_id)
            t.hint_chauffeur, t.hint_start = rit.chauffeur_id, naar_min(ctx, rit.gepland_start)
        p.taken.append(t)
        if probleem:
            p.niet_te_plannen[rit.id] = probleem
            continue
        toegestaan = toegestane_paren(ctx, rit, eenh, chauffeurs)
        if not toegestaan.paren:
            p.niet_te_plannen[rit.id] = " ".join(toegestaan.redenen)
            continue
        p.toegestaan[rit.id] = [(eenheid_sleutel(e.trekker.id, e.chassis.id), c.id) for e, c in toegestaan.paren]
    for rit in ctx.ritten:
        o = rit.order
        vrij = [(c.id, v.status, v.lfd.isoformat()) for c in o.containers
                if (v := ctx.vrijgave_per_container.get(c.id))]
        slots = [(s.id, s.status, str(s.slot_van), str(s.slot_tot)) for s in ctx.slots_per_rit.get(rit.id, [])]
        p.staat.append(json.dumps([rit.id, rit.status, rit.vastheid, str(rit.gepland_start), rit.trekker_id,
                                   rit.chassis_id, rit.chauffeur_id, rit.van_locatie_id, rit.naar_locatie_id,
                                   o.status, str(o.venster_van), str(o.venster_tot), vrij, slots]))
    p.staat.append(json.dumps(sorted((a.id, a.chauffeur_id, a.trekker_id, a.chassis_id) for a in ctx.afwezig)))
    loc_obj = {rit.van_locatie_id: rit.van_locatie for rit in ctx.ritten}
    loc_obj.update({rit.naar_locatie_id: rit.naar_locatie for rit in ctx.ritten})
    if ctx.standplaats:
        loc_obj[ctx.standplaats.id] = ctx.standplaats
    for a in sorted(locaties):
        for b in sorted(locaties):
            if a != b and a in loc_obj and b in loc_obj:
                r = ctx.reistijden.reis(loc_obj[a], loc_obj[b])
                p.reis[(a, b)] = (r.minuten, r.km)
    return p
