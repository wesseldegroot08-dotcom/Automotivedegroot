"""Voorstellen maken, controleren, goedkeuren en vergelijken.

Stappen:
1. bouw_probleem (alleen toegestane combinaties) -> solver (benadering).
2. exacte_controle: zet het voorstel tijdelijk in een losse sessie, toets met alle regels, en draai terug.
   Een rit die een harde regel (of 3, 7, 11 = hard voor voorstellen) schendt, mag niet in het voorstel.
   Dan rekent de solver opnieuw zonder die combinatie (maximaal 3 rondes).
3. Opslaan met invoer, regelversie, keuzes en uitleg (gemaakt door code, met getallen uit de controle).
4. Goedkeuren zet de keuzes op het planbord. Publiceren gaat daarna via het planbord.
"""

import hashlib
from dataclasses import dataclass, field
from datetime import date, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app import db as dbmod
from app import models as m
from app.audit import log_actie
from app.db import nu_utc
from app.jobs import handler
from app.planner.context import DagContext, laad_dag
from app.planner.probleem import VAST, bouw_probleem, eenheid_sleutel, van_min
from app.planner.ritten import plan_rit
from app.planner.solver import CpSatSolver
from app.ports.clock import NL
from app.rules.basis import HARD
from app.rules.planning import open_harde_regels, rijtijd_per_chauffeur, toets_rit
from app.statussen import zet_status

MAX_RONDES = 3


class VoorstelFout(ValueError):
    pass


def regelversie(db: Session) -> str:
    """Vingerafdruk van alle regels en instellingen. Zo weet je met welke regels een voorstel is gemaakt."""
    delen = [f"{r.id}|{r.code}|{r.waarde}|{r.geldig_van}|{r.geldig_tot}|{r.status}|{r.in_gebruik}"
             for r in db.scalars(select(m.Regel).order_by(m.Regel.id))]
    delen += [f"{i.sleutel}={i.waarde}" for i in db.scalars(select(m.Instelling).order_by(m.Instelling.sleutel))]
    return hashlib.sha256("\n".join(delen).encode()).hexdigest()[:16]


def noodstop_aan(db: Session) -> bool:
    i = db.get(m.Instelling, "noodstop")
    return bool(i and i.waarde.strip().lower() == "aan")


def tijdlimiet(db: Session) -> float:
    i = db.get(m.Instelling, "solver_tijdlimiet_sec")
    try:
        return max(1.0, min(120.0, float(i.waarde))) if i else 15.0
    except ValueError:
        return 15.0


# ---------------------------------------------------------------- meten (voor de vergelijking)


@dataclass
class Meting:
    ingepland: int = 0
    lege_km: int = 0
    lege_min: int = 0
    wacht_min: int = 0
    per_rit: dict[int, tuple[int, int]] = field(default_factory=dict)  # rit_id -> (lege_min, lege_km) ervoor


def meet(ctx: DagContext) -> Meting:
    uit = Meting()
    per_trekker: dict[int, list[m.Rit]] = {}
    for r in ctx.ritten:
        if r.gepland_start and r.trekker_id and r.chassis_id and r.chauffeur_id:
            per_trekker.setdefault(r.trekker_id, []).append(r)
            uit.ingepland += 1
    for ritten in per_trekker.values():
        ritten.sort(key=lambda r: r.gepland_start)
        positie, vorige_eind = ctx.standplaats, None
        for r in ritten:
            aan = ctx.reistijden.reis(positie, r.van_locatie) if positie else None
            aan_min, aan_km = (aan.minuten, aan.km) if aan else (0, 0)
            uit.lege_min += aan_min
            uit.lege_km += aan_km
            uit.per_rit[r.id] = (aan_min, aan_km)
            if vorige_eind:
                gat = int((r.gepland_start - vorige_eind).total_seconds() // 60) - aan_min
                uit.wacht_min += max(0, gat)
            vorige_eind = ctx.bereken_eind(r)
            positie = r.naar_locatie
        if positie and ctx.standplaats:
            terug = ctx.reistijden.reis(positie, ctx.standplaats)
            uit.lege_min += terug.minuten
            uit.lege_km += terug.km
    return uit


# ---------------------------------------------------------------- de exacte controle


@dataclass
class Keuze:
    start: datetime
    trekker_id: int
    chassis_id: int
    chauffeur_id: int


@dataclass
class RitControle:
    harde_problemen: list[str]
    uitslagen: dict[int, tuple[str, str]]  # regelnummer -> (niveau, uitleg); eerste uitslag per regel
    eind: datetime | None
    wacht_bron: str
    rest_rijtijd_min: int | None


@dataclass
class ExactUitkomst:
    per_rit: dict[int, RitControle]
    meting: Meting

    def fouten(self, alleen: set[int] | None = None) -> dict[int, list[str]]:
        return {rid: c.harde_problemen for rid, c in self.per_rit.items()
                if c.harde_problemen and (alleen is None or rid in alleen)}


def _blokkeert(ctx: DagContext, rit: m.Rit, u, heeft_slot: bool) -> bool:
    if (rit.id, u.nr) in ctx.overrides:
        return False
    if u.nr in (9, 10) and not heeft_slot and u.niveau == HARD:
        return False  # nog geen slot: dat is de volgende stap (pre-notificatie), geen fout van het voorstel
    return u.niveau == HARD or u.blokkeert_voorstel


def exacte_controle(d: date, keuzes: dict[int, Keuze | None], gebruiker: str = "systeem") -> ExactUitkomst:
    """Zet de keuzes tijdelijk op de ritten (in een losse sessie), toets alles en draai daarna terug.

    keuzes: rit_id -> Keuze (inplannen) of None (niet inplannen). Ritten die er niet in staan blijven zoals ze zijn.
    """
    with dbmod.SessionLocal() as s:
        s.info["gebruiker"] = gebruiker
        try:
            with s.no_autoflush:
                ctx = laad_dag(s, d)
                for rit in ctx.ritten:
                    if rit.id not in keuzes:
                        continue
                    k = keuzes[rit.id]
                    if k is None:
                        rit.gepland_start = rit.trekker_id = rit.chassis_id = rit.chauffeur_id = None
                        rit.trekker = rit.chassis = rit.chauffeur = None
                        continue
                    rit.gepland_start = k.start
                    rit.trekker_id, rit.chassis_id, rit.chauffeur_id = k.trekker_id, k.chassis_id, k.chauffeur_id
                    rit.trekker = s.get(m.Trekker, k.trekker_id)
                    rit.chassis = s.get(m.Chassis, k.chassis_id)
                    rit.chauffeur = s.get(m.Chauffeur, k.chauffeur_id)
                rijtijden = rijtijd_per_chauffeur(ctx)
                per_rit = {}
                for rit in ctx.ritten:
                    t = toets_rit(ctx, rit, rijtijden)
                    heeft_slot = any(sl.status in ("Toegekend", "Gewijzigd")
                                     for sl in ctx.slots_per_rit.get(rit.id, []))
                    harde = [f"Regel {u.nr} ({u.naam}): {u.uitleg}" for u in t.uitslagen
                             if t.toegewezen and _blokkeert(ctx, rit, u, heeft_slot)]
                    uitslagen: dict[int, tuple[str, str]] = {}
                    for u in t.uitslagen:
                        uitslagen.setdefault(u.nr, (u.niveau, u.uitleg))
                    rest = rijtijden[rit.chauffeur_id][0].rest_dag_min if rit.chauffeur_id in rijtijden else None
                    per_rit[rit.id] = RitControle(harde, uitslagen, t.eind, ctx.rit_duur(rit).wacht_bron, rest)
                meting = meet(ctx)
        finally:
            s.rollback()
    return ExactUitkomst(per_rit, meting)


# ---------------------------------------------------------------- uitleg (door code, met getallen uit de controle)


def _u(minuten: int | None) -> str:
    if minuten is None:
        return "onbekend"
    return f"{minuten // 60} u {minuten % 60:02d} min"


def maak_uitleg(chauffeur: str, trekker: str, chassis: str, rit_naam: str, start: datetime, c: RitControle,
                lege_min: int, lege_km: int, alternatieven: int) -> str:
    delen = [f"Voorstel: chauffeur {chauffeur}, trekker {trekker}, chassis {chassis}.",
             f"Begint om {start.astimezone(NL):%H:%M} bij de ophaalplek"
             + (f", klaar om {c.eind.astimezone(NL):%H:%M}." if c.eind else ".")]
    if 2 in c.uitslagen:
        delen.append(f"Chassis: {c.uitslagen[2][1]}")
    delen.append(f"Nog {_u(c.rest_rijtijd_min)} rijtijd over op deze dag (na alle ritten).")
    delen.append(f"Leeg rijden ervoor: {lege_min} min ({lege_km} km).")
    if 9 in c.uitslagen:
        niveau, tekst = c.uitslagen[9]
        delen.append(tekst if niveau != HARD or "Geen slot" not in tekst
                     else "Nog geen slot: na goedkeuren eerst de pre-notificatie sturen.")
    delen.append(f"Laadtijd: {c.wacht_bron}.")
    delen.append(f"Andere geschikte combinaties voor deze rit: {alternatieven}.")
    getoetst = []
    for nr, naam in ((3, "gewicht"), (7, "rijtijd"), (11, "release"), (12, "LFD"), (13, "tijdvenster")):
        if nr in c.uitslagen:
            niveau, tekst = c.uitslagen[nr]
            getoetst.append(f"{naam} {niveau.upper()} ({tekst.rstrip('.')})")
    if getoetst:
        delen.append("Regels getoetst: " + "; ".join(getoetst) + ".")
    return " ".join(delen)


# ---------------------------------------------------------------- een voorstel maken


def maak_voorstel(db: Session, d: date, gebruiker: str, job_id: int | None = None) -> m.Voorstel:
    if noodstop_aan(db):
        raise VoorstelFout("De noodstop staat aan. Voorstellen zijn uit. Plan handmatig op het planbord.")
    ctx = laad_dag(db, d)
    huidig = meet(ctx)
    probleem = bouw_probleem(ctx)
    invoer_hash = probleem.invoer_hash()
    invoer = probleem.naar_json()
    solver = CpSatSolver()
    limiet = tijdlimiet(db)
    eenheden = {e.sleutel: e for e in probleem.eenheden}
    oplossing, controle, keuzes = None, None, {}
    afgekeurd: dict[int, list[str]] = {}
    rekentijd = 0
    db.commit()  # de controle gebruikt een losse sessie
    for _ronde in range(MAX_RONDES):
        oplossing = solver.los_op(probleem, limiet)
        rekentijd += oplossing.rekentijd_ms
        keuzes = {}
        for t in probleem.taken:
            if t.vast:
                continue
            tw = oplossing.toewijzingen.get(t.rit_id)
            if tw:
                e = eenheden[tw.eenheid]
                keuzes[t.rit_id] = Keuze(van_min(ctx, tw.start_min), e.trekker_id, e.chassis_id, tw.chauffeur_id)
            else:
                keuzes[t.rit_id] = None
        controle = exacte_controle(d, keuzes, gebruiker)
        fouten = controle.fouten(alleen={rid for rid, k in keuzes.items() if k})
        if not fouten:
            break
        for rid, problemen in fouten.items():
            k = keuzes[rid]
            probleem.verboden.add((rid, eenheid_sleutel(k.trekker_id, k.chassis_id)))
            afgekeurd[rid] = problemen
    else:
        # Na de laatste ronde: wat nog faalt gaat eruit (een voorstel gebruikt nooit een geschonden harde regel)
        for rid, problemen in controle.fouten(alleen={rid for rid, k in keuzes.items() if k}).items():
            keuzes[rid] = None
            oplossing.toewijzingen.pop(rid, None)
            oplossing.ongepland[rid] = "De exacte controle keurde elke gevonden plek af: " + " | ".join(problemen)
        controle = exacte_controle(d, keuzes, gebruiker)

    open_fouten = controle.fouten(alleen={rid for rid, k in keuzes.items() if k})
    v = m.Voorstel(datum=d, status="Berekend", job_id=job_id, aangemaakt_door=gebruiker, regelversie=regelversie(db),
                   invoer_hash=invoer_hash, invoer=invoer, solver_status=oplossing.status, rekentijd_ms=rekentijd,
                   ingepland=controle.meting.ingepland, ongepland=sum(1 for k in keuzes.values() if k is None),
                   lege_km=controle.meting.lege_km, lege_min=controle.meting.lege_min,
                   wacht_min=controle.meting.wacht_min, exact_ok=not open_fouten)
    db.add(v)
    db.flush()
    namen_ch = {c.id: c.naam for c in probleem.chauffeurs}
    taken = {t.rit_id: t for t in probleem.taken}
    for t in probleem.taken:
        rit = db.get(m.Rit, t.rit_id)
        c = controle.per_rit.get(t.rit_id)
        if t.vast:
            lm, lk = controle.meting.per_rit.get(t.rit_id, (0, 0))
            db.add(m.VoorstelRit(voorstel_id=v.id, rit_id=t.rit_id, ingepland=True, vast=True, start=rit.gepland_start,
                                 eind=c.eind if c else None, trekker_id=rit.trekker_id, chassis_id=rit.chassis_id,
                                 chauffeur_id=rit.chauffeur_id, lege_min=lm, lege_km=lk,
                                 uitleg=f"Staat vast ({rit.vastheid}). De solver heeft deze rit niet verschoven.",
                                 harde_problemen="\n".join(c.harde_problemen) if c and c.harde_problemen else None))
            continue
        k = keuzes.get(t.rit_id)
        if not k:
            reden = oplossing.ongepland.get(t.rit_id) or "Geen plek gevonden."
            if t.rit_id in afgekeurd and "exacte controle" not in reden:
                reden += " Eerder afgekeurd door de exacte controle: " + " | ".join(afgekeurd[t.rit_id])
            db.add(m.VoorstelRit(voorstel_id=v.id, rit_id=t.rit_id, ingepland=False, reden=reden))
            continue
        lm, lk = controle.meting.per_rit.get(t.rit_id, (0, 0))
        e = eenheden[eenheid_sleutel(k.trekker_id, k.chassis_id)]
        trekker = db.get(m.Trekker, k.trekker_id)
        chassis = db.get(m.Chassis, k.chassis_id)
        alternatieven = len({p for p in probleem.toegestaan.get(t.rit_id, [])}) - 1
        uitleg = maak_uitleg(namen_ch.get(k.chauffeur_id, "?"), trekker.intern_nummer, chassis.nummer,
                             taken[t.rit_id].naam, k.start, c, lm, lk, max(0, alternatieven))
        db.add(m.VoorstelRit(voorstel_id=v.id, rit_id=t.rit_id, ingepland=True, start=k.start, eind=c.eind,
                             trekker_id=e.trekker_id, chassis_id=e.chassis_id, chauffeur_id=k.chauffeur_id,
                             lege_min=lm, lege_km=lk, uitleg=uitleg,
                             harde_problemen="\n".join(c.harde_problemen) if c.harde_problemen else None))
    zet_status(v, "voorstel", "Voorgesteld")
    log_actie(db, "voorstel berekend", tabel="voorstel", record_id=v.id, na={
        "datum": d.isoformat(), "regelversie": v.regelversie, "invoer_hash": invoer_hash,
        "solver": oplossing.status, "rekentijd_ms": rekentijd, "ingepland": v.ingepland, "ongepland": v.ongepland,
        "huidig_plan": {"ingepland": huidig.ingepland, "lege_km": huidig.lege_km, "wacht_min": huidig.wacht_min},
        "keuzes": {str(rid): ([k.start.isoformat(), k.trekker_id, k.chassis_id, k.chauffeur_id] if k else None)
                   for rid, k in keuzes.items()}})
    return v


@handler("voorstel")
def _job_voorstel(db: Session, payload: dict, job: m.Job) -> dict:
    v = maak_voorstel(db, date.fromisoformat(payload["datum"]), payload.get("gebruiker", "systeem"), job.id)
    db.flush()
    return {"voorstel_id": v.id}


# ---------------------------------------------------------------- vergelijken, goedkeuren, afkeuren


def huidige_hash(db: Session, d: date) -> str:
    return bouw_probleem(laad_dag(db, d)).invoer_hash()


def keuzes_van(v: m.Voorstel) -> dict[int, Keuze | None]:
    return {r.rit_id: (Keuze(r.start, r.trekker_id, r.chassis_id, r.chauffeur_id) if r.ingepland else None)
            for r in v.regels if not r.vast}


def vergelijking(db: Session, v: m.Voorstel) -> dict:
    huidig = meet(laad_dag(db, v.datum))
    return {"huidig": huidig, "voorstel": v}


def goedkeuren(db: Session, v: m.Voorstel, gebruiker: str) -> int:
    """Zet de keuzes op het planbord. Eerst opnieuw de exacte controle met de data van nu."""
    if noodstop_aan(db):
        raise VoorstelFout("De noodstop staat aan. Voorstellen zijn uit.")
    if v.status != "Voorgesteld":
        raise VoorstelFout(f"Dit voorstel staat op '{v.status}' en kan niet meer goedgekeurd worden.")
    if huidige_hash(db, v.datum) != v.invoer_hash:
        raise VoorstelFout("Het plan, de orders of de middelen zijn veranderd sinds dit voorstel. Klik op "
                           "'Herbereken' voor een nieuw voorstel.")
    keuzes = keuzes_van(v)
    db.commit()
    controle = exacte_controle(v.datum, keuzes, gebruiker)
    fouten = controle.fouten(alleen={rid for rid, k in keuzes.items() if k})
    if fouten:
        v.exact_ok = False
        db.commit()
        tekst = "; ".join(f"rit {rid}: {p[0]}" for rid, p in list(fouten.items())[:5])
        raise VoorstelFout(f"De exacte controle keurt dit voorstel af ({len(fouten)} rit(ten)): {tekst}. "
                           "Dit voorstel kan niet gepubliceerd worden.")
    ctx = laad_dag(db, v.datum)
    per_id = {r.id: r for r in ctx.ritten}
    aantal = 0
    for rid, k in keuzes.items():
        rit = per_id.get(rid)
        if not rit or rit.vastheid in VAST:
            continue
        if k:
            plan_rit(ctx, rit, k.start, k.trekker_id, k.chassis_id, k.chauffeur_id)
        elif rit.gepland_start or rit.trekker_id or rit.chauffeur_id:
            plan_rit(ctx, rit, None, None, None, None)
        aantal += 1
    zet_status(v, "voorstel", "Goedgekeurd")
    v.beoordeeld_door, v.beoordeeld, v.exact_ok = gebruiker, nu_utc(), True
    log_actie(db, "voorstel goedgekeurd", tabel="voorstel", record_id=v.id, na={"ritten": aantal})
    return aantal


def afkeuren(db: Session, v: m.Voorstel, gebruiker: str, reden: str) -> None:
    if v.status != "Voorgesteld":
        raise VoorstelFout(f"Dit voorstel staat op '{v.status}'.")
    zet_status(v, "voorstel", "Afgekeurd")
    v.beoordeeld_door, v.beoordeeld, v.reden_afkeur = gebruiker, nu_utc(), reden.strip() or None
    log_actie(db, "voorstel afgekeurd", tabel="voorstel", record_id=v.id, reden=reden.strip() or None)


def goedgekeurd_voorstel(db: Session, d: date) -> m.Voorstel | None:
    return db.scalar(select(m.Voorstel).where(m.Voorstel.datum == d, m.Voorstel.status == "Goedgekeurd")
                     .order_by(m.Voorstel.id.desc()))


def ongewijzigd_uit_voorstel(v: m.Voorstel, rit: m.Rit) -> bool:
    r = next((x for x in v.regels if x.rit_id == rit.id and x.ingepland and not x.vast), None)
    return bool(r and rit.gepland_start == r.start and (rit.trekker_id, rit.chassis_id, rit.chauffeur_id)
                == (r.trekker_id, r.chassis_id, r.chauffeur_id))


def blokkades_voor_publiceren(ctx: DagContext, toetsen: dict, v: m.Voorstel | None) -> list[tuple[m.Rit, object]]:
    """Harde regels zonder override. Voor ritten die ongewijzigd uit een voorstel komen zijn 3, 7 en 11 ook hard."""
    uit = []
    for t in toetsen.values():
        if not t.toegewezen:
            continue
        uit += [(t.rit, u) for u in open_harde_regels(ctx, t)]
        if v and ongewijzigd_uit_voorstel(v, t.rit):
            uit += [(t.rit, u) for u in t.uitslagen if u.niveau != HARD and u.blokkeert_voorstel
                    and (t.rit.id, u.nr) not in ctx.overrides]
    return uit


def aangepast_door_planner(v: m.Voorstel, ctx: DagContext) -> int:
    n = 0
    regels = {r.rit_id: r for r in v.regels if not r.vast}
    for rit in ctx.ritten:
        r = regels.get(rit.id)
        if r is None:
            continue
        if r.ingepland != bool(rit.gepland_start and rit.trekker_id) or (r.ingepland and not
                                                                        ongewijzigd_uit_voorstel(v, rit)):
            n += 1
    return n

