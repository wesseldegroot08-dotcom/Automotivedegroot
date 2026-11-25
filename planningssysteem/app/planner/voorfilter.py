"""Vooraf bepalen welke combinaties (eenheid + chauffeur) per rit toegestaan zijn.

Een eenheid = trekker + vast chassis (ontkoppelen komt later).
We toetsen hier de harde regels die NIET van de tijd afhangen:
chassis past (2), reefer (15), gewicht (3, hard voor voorstellen), ADR (14), toegang terminal (16),
beschikbaarheid, release (11, hard voor voorstellen).
De solver mag daarna alleen uit deze toegestane combinaties kiezen.
"""

from dataclasses import dataclass, field

from sqlalchemy import select

from app import models as m
from app.planner.context import DagContext
from app.rules.basis import Uitslag
from app.rules.planning import regel_release, regel_toegang
from app.rules.voertuig import (
    chassis_uit,
    container_uit,
    regel_adr,
    regel_chassis_past,
    regel_gewicht,
    regel_reefer,
    trekker_uit,
)


@dataclass
class Eenheid:
    trekker: m.Trekker
    chassis: m.Chassis

    @property
    def naam(self) -> str:
        return f"trekker {self.trekker.intern_nummer} + chassis {self.chassis.nummer}"


@dataclass
class Toegestaan:
    rit: m.Rit
    paren: list[tuple[Eenheid, m.Chauffeur]] = field(default_factory=list)
    redenen: list[str] = field(default_factory=list)


def eenheden(ctx: DagContext) -> list[Eenheid]:
    uit = []
    trekkers = ctx.db.scalars(select(m.Trekker).where(m.Trekker.gearchiveerd.is_(False))
                              .order_by(m.Trekker.intern_nummer))
    for t in trekkers:
        if not t.vaste_chassis_id or t.status != "actief" or ctx.is_afwezig(trekker_id=t.id):
            continue
        c = ctx.db.get(m.Chassis, t.vaste_chassis_id)
        if c and c.status == "actief" and not c.gearchiveerd and not ctx.is_afwezig(chassis_id=c.id):
            uit.append(Eenheid(t, c))
    return uit


def beschikbare_chauffeurs(ctx: DagContext) -> list[m.Chauffeur]:
    return [c for c in ctx.db.scalars(select(m.Chauffeur).where(m.Chauffeur.actief.is_(True))
                                      .order_by(m.Chauffeur.pseudoniem))
            if not ctx.is_afwezig(chauffeur_id=c.id)]


def _eerste_blokkade(uitslagen: list[Uitslag | None]) -> Uitslag | None:
    for u in uitslagen:
        if u is not None and u.blokkeert_voorstel:
            return u
    return None


def toegestane_paren(ctx: DagContext, rit: m.Rit, eenh: list[Eenheid] | None = None,
                     chauffeurs: list[m.Chauffeur] | None = None) -> Toegestaan:
    eenh = eenh if eenh is not None else eenheden(ctx)
    chauffeurs = chauffeurs if chauffeurs is not None else beschikbare_chauffeurs(ctx)
    uit = Toegestaan(rit)
    rel = regel_release(ctx, rit)
    if rel and rel.blokkeert_voorstel:
        uit.redenen.append(rel.uitleg)
        return uit
    containers = [container_uit(c) for c in rit.order.containers]
    handelingen = [h.soort for h in rit.order.handelingen]
    eenheid_redenen: list[str] = []
    goede_eenheden = []
    for e in eenh:
        ti, ci = trekker_uit(e.trekker), chassis_uit(e.chassis)
        blok = _eerste_blokkade([
            regel_chassis_past(ci, containers, handelingen), regel_reefer(ci, containers),
            regel_gewicht(ctx.boek, ctx.datum, ti, ci, containers, rit.order.land_route),
            regel_adr(ctx.datum, containers, ti, ci, None),
        ])
        if blok:
            eenheid_redenen.append(f"{e.naam}: {blok.uitleg}")
        else:
            goede_eenheden.append(e)
    if not goede_eenheden:
        uit.redenen.append("Geen eenheid (trekker + chassis) is geschikt. " + " | ".join(eenheid_redenen))
        return uit
    chauffeur_redenen = []
    for c in chauffeurs:
        adr = regel_adr(ctx.datum, containers, None, None, c)
        toegang = regel_toegang(ctx, rit, c)
        blok = _eerste_blokkade([adr, toegang])
        if blok:
            chauffeur_redenen.append(blok.uitleg)
            continue
        for e in goede_eenheden:
            uit.paren.append((e, c))
    if not uit.paren:
        uit.redenen.append("Geen geschikte chauffeur beschikbaar. " + " | ".join(sorted(set(chauffeur_redenen))))
        return uit
    # Elke chauffeur rijdt zijn eigen trekker (met de trailer die eraan gekoppeld is)
    eigen = [(e, c) for e, c in uit.paren if ctx.trekker_van(c) == e.trekker.id]
    if not eigen:
        namen = sorted({c.pseudoniem for _e, c in uit.paren})
        uit.redenen.append("Wel geschikte chauffeurs (" + ", ".join(namen) + "), maar hun eigen trekker of trailer "
                           "past niet bij deze rit. Geef een chauffeur voor deze dag een andere trekker.")
    uit.paren = eigen
    return uit
