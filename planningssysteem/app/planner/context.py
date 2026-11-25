"""Alle gegevens van één plandag op één plek, plus het rekenmodel voor de duur van een rit.

Rekenmodel van een rit (zelfde voor handmatig plannen en voor de solver):
    gepland_start = aankomst bij de ophaalplek
    + laden (standaard laadtijd, bij een terminal de gemeten gemiddelde wachttijd als die er is)
    + reistijd van ophaalplek naar afleverplek
    + lossen + extra handelingen (kiepen, flexitank, ...)
    = gepland_eind
Het lege rijden naar de ophaalplek komt vóór gepland_start (vanaf de vorige rit of de standplaats).
"""

from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app import models as m
from app.ports.clock import NL, klok
from app.ports.reistijd import Reis, TabelReistijden
from app.rules.basis import RegelBoek
from app.rules.rijtijd import Activiteit, Geschiedenis


@dataclass
class WachtStatistiek:
    gemiddeld_min: int
    metingen: int

    @property
    def zekerheid(self) -> str:
        if self.metingen >= 20:
            return "hoog"
        if self.metingen >= 5:
            return "gemiddeld"
        return "laag"


@dataclass
class RitDuur:
    laden_min: int
    reis: Reis
    lossen_min: int
    wacht_bron: str
    handelingen_aanname: bool = False

    @property
    def totaal_min(self) -> int:
        return self.laden_min + self.reis.minuten + self.lossen_min


@dataclass
class DagContext:
    db: Session
    datum: date
    boek: RegelBoek
    reistijden: TabelReistijden
    instellingen: dict[str, str]
    ritten: list[m.Rit]
    feestdagen_de: set[date]
    terminalregels: dict[int, m.TerminalRegel]
    slots_per_rit: dict[int, list[m.Slot]]
    vrijgave_per_container: dict[int, m.Vrijgave]
    dd_tarieven: list[m.DDTarief]
    overrides: dict[tuple[int, int], m.Override]
    afwezig: list[m.Afwezigheid]
    wachttijden: dict[int, WachtStatistiek]
    standplaats: m.Locatie | None
    registraties: list[m.RijtijdRegistratie] = field(default_factory=list)
    inzet: dict[int, int] = field(default_factory=dict)  # chauffeur_id -> trekker_id (uitzondering voor deze dag)

    @property
    def nu(self) -> datetime:
        return klok().nu()

    # ---------------------------------------------------------- duur

    def rit_duur(self, rit: m.Rit) -> RitDuur:
        van, naar = rit.van_locatie, rit.naar_locatie
        laden = van.laad_los_min
        bron = "standaard laadtijd (aanname)" if van.laad_los_is_aanname else "standaard laadtijd"
        stat = self.wachttijden.get(van.id)
        if van.type == "terminal" and stat and stat.metingen >= 3:
            laden = stat.gemiddeld_min
            bron = f"gemiddeld {stat.gemiddeld_min} min ({stat.metingen} metingen, zekerheid: {stat.zekerheid})"
        handelingen = list(rit.order.handelingen) if rit.order else []
        lossen = naar.laad_los_min + sum(h.duur_min for h in handelingen)
        return RitDuur(laden, self.reistijden.reis(van, naar), lossen, bron,
                       any(h.duur_is_aanname for h in handelingen))

    def bereken_eind(self, rit: m.Rit) -> datetime | None:
        if rit.gepland_start is None:
            return None
        return rit.gepland_start + timedelta(minutes=self.rit_duur(rit).totaal_min)

    # ---------------------------------------------------------- per chauffeur

    def ritten_van_chauffeur(self, chauffeur_id: int) -> list[m.Rit]:
        return sorted([r for r in self.ritten if r.chauffeur_id == chauffeur_id and r.gepland_start],
                      key=lambda r: r.gepland_start)

    def dagschema(self, chauffeur_id: int, ritten: list[m.Rit] | None = None) -> tuple[list[Activiteit], list[tuple]]:
        """Activiteiten van een chauffeur op deze dag, en conflicten (lege rit past niet)."""
        ritten = ritten if ritten is not None else self.ritten_van_chauffeur(chauffeur_id)
        acts: list[Activiteit] = []
        conflicten = []
        positie = self.standplaats
        vorige_eind = None
        for rit in ritten:
            duur = self.rit_duur(rit)
            aanrij = self.reistijden.reis(positie, rit.van_locatie) if positie else Reis(0, 0)
            aanrij_start = rit.gepland_start - timedelta(minutes=aanrij.minuten)
            if vorige_eind and aanrij_start < vorige_eind:
                conflicten.append((rit.id, f"Niet haalbaar: na de vorige rit ({vorige_eind.astimezone(NL):%H:%M}) is "
                                           f"{aanrij.minuten} min rijden nodig naar {rit.van_locatie.naam}."))
            if aanrij.minuten:
                acts.append(Activiteit("rijden", aanrij_start, rit.gepland_start, rit.id))
            t = rit.gepland_start
            acts.append(Activiteit("werk", t, t + timedelta(minutes=duur.laden_min), rit.id))
            t += timedelta(minutes=duur.laden_min)
            acts.append(Activiteit("rijden", t, t + timedelta(minutes=duur.reis.minuten), rit.id))
            t += timedelta(minutes=duur.reis.minuten)
            acts.append(Activiteit("werk", t, t + timedelta(minutes=duur.lossen_min), rit.id))
            t += timedelta(minutes=duur.lossen_min)
            vorige_eind = t
            positie = rit.naar_locatie
        if ritten and positie and self.standplaats:
            terug = self.reistijden.reis(positie, self.standplaats)
            if terug.minuten:
                acts.append(Activiteit("rijden", vorige_eind, vorige_eind + timedelta(minutes=terug.minuten),
                                       ritten[-1].id))
        # Overlappende activiteiten (bij een conflict) niet dubbel tellen: knip ze af
        acts.sort(key=lambda a: a.start)
        schoon: list[Activiteit] = []
        for a in acts:
            if schoon and a.start < schoon[-1].eind:
                if a.eind <= schoon[-1].eind:
                    continue
                a = Activiteit(a.soort, schoon[-1].eind, a.eind, a.rit_id)
            schoon.append(a)
        return schoon, conflicten

    def geschiedenis(self, chauffeur_id: int) -> Geschiedenis:
        maandag = self.datum - timedelta(days=self.datum.weekday())
        vorige_maandag = maandag - timedelta(days=7)
        g = Geschiedenis()
        for r in self.registraties:
            if r.chauffeur_id != chauffeur_id:
                continue
            if maandag <= r.datum < self.datum:
                g.rijtijd_deze_week_min += r.rijtijd_min
                if r.rijtijd_min > self.boek.waarde("rijtijd.dag", self.datum, 540):
                    g.verlengde_dagen_deze_week += 1
            elif vorige_maandag <= r.datum < maandag:
                g.rijtijd_vorige_week_min += r.rijtijd_min
        return g

    def trekker_van(self, chauffeur: m.Chauffeur) -> int | None:
        """De trekker die deze chauffeur vandaag rijdt: de uitzondering voor vandaag, anders zijn eigen trekker."""
        return self.inzet.get(chauffeur.id) or chauffeur.voorkeur_trekker_id

    def is_afwezig(self, *, chauffeur_id=None, trekker_id=None, chassis_id=None) -> m.Afwezigheid | None:
        for a in self.afwezig:
            if (chauffeur_id and a.chauffeur_id == chauffeur_id) or (trekker_id and a.trekker_id == trekker_id) or (
                    chassis_id and a.chassis_id == chassis_id):
                return a
        return None


def dag_grenzen(d: date) -> tuple[datetime, datetime]:
    begin = datetime.combine(d, time()).replace(tzinfo=NL)
    return begin, begin + timedelta(days=1)


def wachttijd_statistiek(db: Session) -> dict[int, WachtStatistiek]:
    rijen = db.execute(select(m.Stop.locatie_id, func.avg(m.Stop.wachttijd_min), func.count(m.Stop.id))
                       .where(m.Stop.wachttijd_min.is_not(None)).group_by(m.Stop.locatie_id)).all()
    return {lid: WachtStatistiek(round(gem), n) for lid, gem, n in rijen}


def laad_dag(db: Session, d: date) -> DagContext:
    begin, eind = dag_grenzen(d)
    ritten = list(db.scalars(
        select(m.Rit).options(
            selectinload(m.Rit.order).selectinload(m.Order.containers),
            selectinload(m.Rit.order).selectinload(m.Order.handelingen),
            selectinload(m.Rit.order).selectinload(m.Order.klant),
            selectinload(m.Rit.van_locatie), selectinload(m.Rit.naar_locatie), selectinload(m.Rit.trekker),
            selectinload(m.Rit.chassis), selectinload(m.Rit.chauffeur),
        ).join(m.Order).where(
            ((m.Rit.gepland_start >= begin) & (m.Rit.gepland_start < eind))
            | ((m.Rit.gepland_start.is_(None)) & (m.Order.venster_van >= begin) & (m.Order.venster_van < eind))
        ).order_by(m.Rit.gepland_start, m.Rit.id)
    ))
    rit_ids = [r.id for r in ritten]
    container_ids = [c.id for r in ritten if r.order for c in r.order.containers]
    vandaag_regels = {}
    for tr in db.scalars(select(m.TerminalRegel)):
        if tr.geldig_van <= d and (tr.geldig_tot is None or d <= tr.geldig_tot):
            if tr.locatie_id not in vandaag_regels or tr.geldig_van > vandaag_regels[tr.locatie_id].geldig_van:
                vandaag_regels[tr.locatie_id] = tr
    slots: dict[int, list[m.Slot]] = {}
    for s in db.scalars(select(m.Slot).where(m.Slot.rit_id.in_(rit_ids))):
        slots.setdefault(s.rit_id, []).append(s)
    vrijgaven = {}
    for v in db.scalars(select(m.Vrijgave).where(m.Vrijgave.container_id.in_(container_ids))
                        .order_by(m.Vrijgave.tijdstip)):
        vrijgaven[v.container_id] = v  # de nieuwste telt
    overrides = {(o.rit_id, o.regel_nr): o for o in db.scalars(
        select(m.Override).where(m.Override.rit_id.in_(rit_ids), m.Override.actief.is_(True)))}
    afwezig = list(db.scalars(select(m.Afwezigheid).where(m.Afwezigheid.van <= d, m.Afwezigheid.tot >= d)))
    registraties = list(db.scalars(select(m.RijtijdRegistratie).where(
        m.RijtijdRegistratie.datum >= d - timedelta(days=14), m.RijtijdRegistratie.datum < d)))
    feest = {f.datum for f in db.scalars(select(m.Feestdag).where(m.Feestdag.land == "DE", m.Feestdag.rijverbod))}
    inst = {i.sleutel: i.waarde for i in db.scalars(select(m.Instelling))}
    standplaats = db.scalar(select(m.Locatie).where(m.Locatie.type == "overig", m.Locatie.naam.like("Standplaats%")))
    inzet = {i.chauffeur_id: i.trekker_id for i in db.scalars(select(m.Inzet).where(m.Inzet.datum == d))}
    return DagContext(db, d, RegelBoek.laad(db), TabelReistijden(db), inst, ritten, feest, vandaag_regels, slots,
                      vrijgaven, list(db.scalars(select(m.DDTarief))), overrides, afwezig, wachttijd_statistiek(db),
                      standplaats, registraties, inzet)
