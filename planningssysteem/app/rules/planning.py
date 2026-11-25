"""De regelmotor voor de dagplanning. Toetst elke rit aan alle regels.

Gebruik: toets_dag(ctx) -> {rit_id: [Uitslag, ...]}
"""

from dataclasses import dataclass
from datetime import date, datetime, timedelta

from app import models as m
from app.planner.context import DagContext
from app.ports.clock import NL
from app.rules.basis import HARD, OK, WAARSCHUWING, Uitslag, ergste
from app.rules.kosten import RitKosten, banden_uit, bereken_rit_kosten, dd_bedrag_per_dag, dd_kosten
from app.rules.rijtijd import RijtijdUitslag, controleer_dag
from app.rules.verbodsdag import regel_de_intermodaal, regel_verbodsdag
from app.rules.voertuig import (
    chassis_uit,
    container_uit,
    toets_combinatie,
    trekker_uit,
)

AFGEROND = {"Afgerond", "Klaar"}


def _overlap(a_start, a_eind, b_start, b_eind) -> bool:
    return a_start < b_eind and b_start < a_eind


def _in_nl(t: datetime) -> datetime:
    return t.astimezone(NL)


# ---------------------------------------------------------------- regel 1: dubbele boeking en beschikbaarheid


def regel_dubbel(ctx: DagContext, rit: m.Rit, eind: datetime) -> Uitslag:
    fouten = []
    containers = {c.id for c in rit.order.containers} if rit.order else set()
    for ander in ctx.ritten:
        if ander.id == rit.id or not ander.gepland_start:
            continue
        a_eind = ctx.bereken_eind(ander)
        if not _overlap(rit.gepland_start, eind, ander.gepland_start, a_eind):
            continue
        for veld, naam in (("trekker_id", "trekker"), ("chassis_id", "chassis"), ("chauffeur_id", "chauffeur")):
            if getattr(rit, veld) and getattr(rit, veld) == getattr(ander, veld):
                fouten.append(f"{naam} staat ook op rit {ander.id} ({_in_nl(ander.gepland_start):%H:%M}-"
                              f"{_in_nl(a_eind):%H:%M})")
        if ander.order and containers & {c.id for c in ander.order.containers}:
            fouten.append(f"container staat ook op rit {ander.id}")
    for a in [ctx.is_afwezig(chauffeur_id=rit.chauffeur_id), ctx.is_afwezig(trekker_id=rit.trekker_id),
              ctx.is_afwezig(chassis_id=rit.chassis_id)]:
        if a:
            wie = "chauffeur" if a.chauffeur_id else ("trekker" if a.trekker_id else "chassis")
            fouten.append(f"{wie} is niet beschikbaar ({a.reden})")
    if rit.trekker and (rit.trekker.status != "actief" or rit.trekker.gearchiveerd):
        fouten.append(f"trekker {rit.trekker.intern_nummer} is '{rit.trekker.status}'")
    if rit.chassis and (rit.chassis.status != "actief" or rit.chassis.gearchiveerd):
        fouten.append(f"chassis {rit.chassis.nummer} is '{rit.chassis.status}'")
    if fouten:
        return Uitslag(1, "Dubbele boeking / beschikbaarheid", HARD, "Niet toegestaan: " + "; ".join(fouten) + ".")
    return Uitslag(1, "Dubbele boeking / beschikbaarheid", OK, "Geen dubbele boeking. Alles beschikbaar.")


# ---------------------------------------------------------------- regel 9 en 10: slot en pre-notificatie


@dataclass
class TerminalBezoek:
    locatie: m.Locatie
    aankomst: datetime


def terminal_bezoeken(ctx: DagContext, rit: m.Rit) -> list[TerminalBezoek]:
    duur = ctx.rit_duur(rit)
    uit = []
    if rit.van_locatie.type == "terminal":
        uit.append(TerminalBezoek(rit.van_locatie, rit.gepland_start))
    if rit.naar_locatie.type == "terminal":
        uit.append(TerminalBezoek(rit.naar_locatie, rit.gepland_start + timedelta(
            minutes=duur.laden_min + duur.reis.minuten)))
    return uit


def binnen_slot(aankomst: datetime, slot_van: datetime, slot_tot: datetime, tolerantie_min: int) -> bool:
    t = timedelta(minutes=tolerantie_min)
    return slot_van - t <= aankomst <= slot_tot + t


def no_show_geheven(instellingen: dict[str, str], tr: m.TerminalRegel, d: date) -> bool:
    """Worden no-showkosten al echt gerekend? Instelling 'ja', of de ingangsdatum in de terminalregel is bereikt."""
    if instellingen.get("no_show_heffing_actief", "nee") == "ja":
        return True
    return bool(tr.no_show_heffing_vanaf and d >= tr.no_show_heffing_vanaf)


def regel_slot(ctx: DagContext, rit: m.Rit) -> list[Uitslag]:
    uit = []
    for bezoek in terminal_bezoeken(ctx, rit):
        tr = ctx.terminalregels.get(bezoek.locatie.id)
        if not tr or tr.slotsysteem == "geen":
            continue
        bron, status = tr.bron, tr.status
        slots = [s for s in ctx.slots_per_rit.get(rit.id, []) if s.terminal_id == bezoek.locatie.id
                 and s.status in ("Toegekend", "Gewijzigd", "Aangevraagd")]
        if not slots:
            uit.append(Uitslag(9, "Slot", HARD, f"Geen slot bij {bezoek.locatie.naam}. Stuur eerst de pre-notificatie.",
                               bron, status))
            continue
        s = slots[0]
        if s.status == "Aangevraagd" or s.slot_van is None:
            uit.append(Uitslag(10, "Pre-notificatie", HARD, f"Pre-notificatie bij {bezoek.locatie.naam} is verstuurd, "
                               "maar er is nog geen slot toegekend.", bron, status))
            continue
        tol = tr.tolerantie_min or 0
        venster = f"{_in_nl(s.slot_van):%H:%M}-{_in_nl(s.slot_tot):%H:%M}"
        if not binnen_slot(bezoek.aankomst, s.slot_van, s.slot_tot, tol):
            uit.append(Uitslag(9, "Slot", HARD, f"Aankomst {_in_nl(bezoek.aankomst):%H:%M} past niet in slot {venster} "
                               f"(tolerantie {tol} min) bij {bezoek.locatie.naam}.", bron, status))
        else:
            uit.append(Uitslag(9, "Slot", OK, f"Slot {bezoek.locatie.naam} {venster} past (aankomst "
                               f"{_in_nl(bezoek.aankomst):%H:%M}, tolerantie {tol} min).", bron, status))
        if ctx.nu > s.slot_van and rit.status in ("Concept", "Gepland", "Geaccepteerd"):
            bedrag = tr.no_show_kosten_cent
            geheven = no_show_geheven(ctx.instellingen, tr, ctx.datum)
            tekst = "Het slot is al begonnen. Een wijziging of annulering telt nu als no-show"
            if bedrag:
                euro = f"{bedrag / 100:.2f}".replace(".", ",")
                tekst += f" (€ {euro}" + (")" if geheven else ", nog niet geheven)")
            uit.append(Uitslag(9, "Slot", WAARSCHUWING, tekst + ".", bron, status,
                               bedrag_cent=bedrag if geheven else None))
        if tr.tar_verplicht and not s.tar:
            uit.append(Uitslag(10, "Pre-notificatie", HARD, f"TAR ontbreekt voor {bezoek.locatie.naam}.", bron, status))
        elif not s.label:
            uit.append(Uitslag(10, "Pre-notificatie", HARD, "Pre-notificatie is niet compleet (geen label).",
                               bron, status))
        if tr.capaciteit_per_slot:
            tegelijk = sum(1 for lst in ctx.slots_per_rit.values() for x in lst if x.terminal_id == s.terminal_id
                           and x.slot_van == s.slot_van and x.status in ("Toegekend", "Gewijzigd"))
            if tegelijk > tr.capaciteit_per_slot:
                uit.append(Uitslag(9, "Slot", HARD, f"Slot {venster} is vol: {tegelijk} van {tr.capaciteit_per_slot}.",
                                   bron, status))
    return uit


# ---------------------------------------------------------------- regel 11 en 12: release en LFD


def regel_release(ctx: DagContext, rit: m.Rit) -> Uitslag | None:
    if not rit.order or rit.order.type != "import":
        return None
    problemen = []
    for c in rit.order.containers:
        v = ctx.vrijgave_per_container.get(c.id)
        if v is None:
            problemen.append(f"{c.nummer}: geen vrijgave bekend")
            continue
        missend = [n for n, ok in (("commercieel", v.commercieel), ("douane", v.douane),
                                   ("inspectie", v.inspectie_vrij), ("terminal", v.terminal_status)) if not ok]
        if v.status != "Vrij" or missend:
            problemen.append(f"{c.nummer}: release '{v.status}'" + (f", niet vrij: {', '.join(missend)}" if missend
                                                                     else ""))
    if problemen:
        return Uitslag(11, "Release", WAARSCHUWING, "Release niet groen: " + "; ".join(problemen) + ".",
                       hard_voor_voorstel=True)
    return Uitslag(11, "Release", OK, "Release, douane en terminal zijn groen.", hard_voor_voorstel=True)


def dd_banden(ctx: DagContext, container: m.Container, soort: str = "demurrage"):
    return banden_uit([t for t in ctx.dd_tarieven if t.rederij_id == container.rederij_id and t.soort == soort
                       and t.container_maat == container.maat and t.container_type == container.type
                       and t.geldig_van <= ctx.datum and (t.geldig_tot is None or ctx.datum <= t.geldig_tot)])


def regel_lfd(ctx: DagContext, rit: m.Rit) -> Uitslag | None:
    if not rit.order or rit.order.type != "import" or not rit.gepland_start:
        return None
    ophaal = _in_nl(rit.gepland_start).date()
    teksten, totaal, te_laat = [], 0, False
    for c in rit.order.containers:
        v = ctx.vrijgave_per_container.get(c.id)
        if not v:
            continue
        banden = dd_banden(ctx, c)
        if ophaal > v.lfd:
            te_laat = True
            bedrag, dagen = dd_kosten(banden, v.ontlaaddatum, ophaal)
            totaal += bedrag
            teksten.append(f"{c.nummer}: LFD was {v.lfd:%d-%m}, ophalen {ophaal:%d-%m}: {dagen} dag(en) demurrage" +
                           (f" = € {bedrag / 100:.2f}".replace(".", ",") if banden else " (tarief onbekend)"))
        else:
            dag_na = (v.lfd - v.ontlaaddatum).days + 2
            extra = dd_bedrag_per_dag(banden, dag_na) if banden else None
            teksten.append(f"{c.nummer}: op tijd (LFD {v.lfd:%d-%m})" +
                           (f"; een dag later kost € {extra / 100:.2f}".replace(".", ",") if extra else ""))
    if not teksten:
        return None
    if te_laat:
        return Uitslag(12, "LFD", WAARSCHUWING, "; ".join(teksten) + ".", "Voorbeeldtarief rederij", "schatting",
                       bedrag_cent=totaal)
    return Uitslag(12, "LFD", OK, "; ".join(teksten) + ".", "Voorbeeldtarief rederij", "schatting")


# ---------------------------------------------------------------- regel 13: tijdvensters en openingstijden


def _open_op(loc: m.Locatie, t: datetime) -> bool:
    lokaal = _in_nl(t)
    if str(lokaal.isoweekday()) not in loc.open_dagen:
        return False
    if loc.open_van <= loc.open_tot:
        return loc.open_van <= lokaal.time() <= loc.open_tot
    return lokaal.time() >= loc.open_van or lokaal.time() <= loc.open_tot


def regel_tijdvenster(ctx: DagContext, rit: m.Rit, conflict: str | None) -> Uitslag:
    duur = ctx.rit_duur(rit)
    start = rit.gepland_start
    vertrek_van = start + timedelta(minutes=duur.laden_min)
    aankomst_naar = vertrek_van + timedelta(minutes=duur.reis.minuten)
    eind = aankomst_naar + timedelta(minutes=duur.lossen_min)
    hard = ctx.instellingen.get("tijdvenster_klant_hard", "ja") == "ja"
    fouten = []
    if conflict:
        fouten.append(conflict)
    for loc, t1, t2 in ((rit.van_locatie, start, vertrek_van), (rit.naar_locatie, aankomst_naar, eind)):
        if not (_open_op(loc, t1) and _open_op(loc, t2)):
            fouten.append(f"{loc.naam} is dan gesloten (open {loc.open_van:%H:%M}-{loc.open_tot:%H:%M})")
    o = rit.order
    klant_tijd = None
    if o:
        if rit.naar_locatie.type == "klant":
            klant_tijd = aankomst_naar
        elif rit.van_locatie.type == "klant":
            klant_tijd = start
        else:
            klant_tijd = start
        if not (o.venster_van <= klant_tijd <= o.venster_tot):
            fouten.append(f"klant wil {_in_nl(o.venster_van):%H:%M}-{_in_nl(o.venster_tot):%H:%M}, gepland "
                          f"{_in_nl(klant_tijd):%H:%M}")
    if fouten:
        niveau = HARD if (hard or conflict) else WAARSCHUWING
        return Uitslag(13, "Tijdvenster", niveau, ("Niet toegestaan: " if niveau == HARD else "")
                       + "; ".join(fouten) + ".")
    return Uitslag(13, "Tijdvenster", OK, f"Binnen het tijdvenster. Klaar om {_in_nl(eind):%H:%M}.")


# ---------------------------------------------------------------- regel 16: toegang terminal


def regel_toegang(ctx: DagContext, rit: m.Rit, chauffeur: m.Chauffeur | None = None) -> Uitslag | None:
    chauffeur = chauffeur or rit.chauffeur
    if not chauffeur:
        return None
    terminals = [loc for loc in (rit.van_locatie, rit.naar_locatie) if loc.type == "terminal"]
    if not terminals:
        return None
    c = chauffeur
    fouten = []
    ingang = ctx.instellingen.get("ect_veiligheidstest_ingang", "")
    try:
        ingang_datum = date.fromisoformat(ingang)
    except ValueError:
        ingang_datum = None
    for t in terminals:
        if (t.terminalcode or "").startswith("ECT") and ingang_datum and ctx.datum >= ingang_datum:
            if not c.ect_test_tot or c.ect_test_tot < ctx.datum:
                fouten.append(f"{c.pseudoniem} heeft geen geldige ECT-veiligheidstest (nodig voor {t.naam})")
        if not c.cargocard_tot or c.cargocard_tot < ctx.datum:
            fouten.append(f"{c.pseudoniem} heeft geen geldige CargoCard")
    if fouten:
        return Uitslag(16, "Toegang terminal", HARD, "Niet toegestaan: " + "; ".join(sorted(set(fouten))) + ".",
                       "ECT (ingangsdatum veiligheidstest is een instelling)", "open")
    return Uitslag(16, "Toegang terminal", OK, "Chauffeur heeft toegang tot de terminal(s).")


# ---------------------------------------------------------------- regel 18: lege container retour


def regel_retour(ctx: DagContext, rit: m.Rit) -> Uitslag | None:
    if not rit.order or rit.order.type != "leeg" or rit.naar_locatie.type != "depot":
        return None
    regels = "; ".join(c.rederij.retourregels or "" for c in rit.order.containers if c.rederij) or "onbekend"
    return Uitslag(18, "Lege retour", WAARSCHUWING if "onbekend" in regels else OK,
                   f"Retour naar {rit.naar_locatie.naam}. Regels rederij: {regels}. Controleer of het depot deze "
                   "rederij aanneemt.")


# ---------------------------------------------------------------- alles samen


@dataclass
class RitToets:
    rit: m.Rit
    eind: datetime | None
    uitslagen: list[Uitslag]
    kosten: RitKosten | None
    toegewezen: bool

    @property
    def ergste(self) -> str:
        return ergste(self.uitslagen)


def rijtijd_per_chauffeur(ctx: DagContext) -> dict[int, tuple[RijtijdUitslag, list[tuple]]]:
    uit = {}
    for cid in {r.chauffeur_id for r in ctx.ritten if r.chauffeur_id and r.gepland_start}:
        acts, conflicten = ctx.dagschema(cid)
        chauffeur = next(r.chauffeur for r in ctx.ritten if r.chauffeur_id == cid)
        uit[cid] = (controleer_dag(ctx.boek, ctx.datum, acts, ctx.geschiedenis(cid), chauffeur.contracturen_week),
                    conflicten)
    return uit


def toets_rit(ctx: DagContext, rit: m.Rit, rijtijden=None) -> RitToets:
    toegewezen = bool(rit.trekker_id and rit.chassis_id and rit.chauffeur_id and rit.gepland_start)
    uit: list[Uitslag] = []
    r11 = regel_release(ctx, rit)
    if r11:
        uit.append(r11)
    if not rit.gepland_start:
        return RitToets(rit, None, uit, None, False)
    eind = ctx.bereken_eind(rit)
    rijtijden = rijtijden if rijtijden is not None else rijtijd_per_chauffeur(ctx)
    conflict = None
    if rit.chauffeur_id and rit.chauffeur_id in rijtijden:
        for rid, tekst in rijtijden[rit.chauffeur_id][1]:
            if rid == rit.id:
                conflict = tekst
    uit.append(regel_dubbel(ctx, rit, eind))
    containers = [container_uit(c) for c in rit.order.containers] if rit.order else []
    if rit.trekker and rit.chassis:
        uit += toets_combinatie(ctx.boek, ctx.datum, trekker_uit(rit.trekker), chassis_uit(rit.chassis), containers,
                                rit.order.land_route if rit.order else "NL", rit.chauffeur,
                                [h.soort for h in rit.order.handelingen] if rit.order else [])
    # Rijtijd (7) en arbeidstijd (8): uitkomst van de exacte controle voor deze chauffeur
    if rit.chauffeur_id and rit.chauffeur_id in rijtijden:
        rt = rijtijden[rit.chauffeur_id][0]
        eigen = [o for o in rt.overtredingen if o.rit_id == rit.id]
        if eigen:
            uit.append(Uitslag(7, "Rijtijd", WAARSCHUWING, " ".join(o.tekst for o in eigen), "EU 561/2006",
                               "bevestigd", hard_voor_voorstel=True))
        else:
            uit.append(Uitslag(7, "Rijtijd", OK, f"Rijtijd vandaag {rt.rijtijd_min // 60} u {rt.rijtijd_min % 60:02d} "
                               f"min, nog {rt.rest_dag_min // 60} u {rt.rest_dag_min % 60:02d} min over.",
                               "EU 561/2006", "bevestigd", hard_voor_voorstel=True))
        arbeid = [o for o in rt.arbeid if o.rit_id == rit.id]
        if arbeid:
            uit.append(Uitslag(8, "Arbeidstijd", WAARSCHUWING, " ".join(o.tekst for o in arbeid),
                               "Arbeidstijdenbesluit vervoer", "bevestigd"))
        laatste = ctx.ritten_van_chauffeur(rit.chauffeur_id)
        if rt.overwerk_min and laatste and laatste[-1].id == rit.id:
            toeslag = ctx.boek.waarde("cao.overwerk.toeslag", ctx.datum, 30)
            uurprijs = ctx.boek.waarde("kostprijs.uur", ctx.datum, 0) * ctx.boek.waarde("kostprijs.index", ctx.datum,
                                                                                         100) // 100
            bedrag = rt.overwerk_min * uurprijs * toeslag // 100 // 60
            uit.append(Uitslag(8, "Arbeidstijd", WAARSCHUWING, f"Overwerk ca. {rt.overwerk_min} min boven de "
                               f"contracturen: {toeslag}% toeslag, ca. € {bedrag / 100:.2f}".replace(".", ",")
                               + " (schatting, loonschalen Open).", "Cao", "schatting", bedrag_cent=bedrag))
    uit += regel_slot(ctx, rit)
    for regel in (regel_lfd(ctx, rit), regel_tijdvenster(ctx, rit, conflict), regel_toegang(ctx, rit),
                  regel_retour(ctx, rit)):
        if regel:
            uit.append(regel)
    duur = ctx.rit_duur(rit)
    landen = {rit.van_locatie.land, rit.naar_locatie.land}
    if "DE" in landen and rit.trekker and rit.chassis:
        massa = (rit.trekker.tarra_kg or 0) + (rit.chassis.tarra_kg or 0) + sum(c.vgm_kg for c in containers)
        r17 = regel_verbodsdag(ctx.boek, "DE", rit.gepland_start, eind, massa, ctx.feestdagen_de,
                               rit.order.gecombineerd_vervoer if rit.order else False, duur.reis.km)
        if r17:
            uit.append(r17)
    if rit.order:
        r21 = regel_de_intermodaal(ctx.boek, ctx.datum, rit.order.land_route, duur.reis.km)
        if r21:
            uit.append(r21)
    # Kosten (regel 20: tol is kosten)
    demurrage = sum(u.bedrag_cent or 0 for u in uit if u.nr == 12)
    kosten = bereken_rit_kosten(
        ctx.boek, ctx.datum, duur.reis.km, duur.reis.minuten, duur.laden_min + duur.lossen_min,
        duur.reis.km_buitenland, duur.reis.land_buitenland, bool(rit.trekker and rit.trekker.zero_emissie),
        rit.trekker.kosten_per_km_cent if rit.trekker else None,
        rit.trekker.kosten_per_uur_cent if rit.trekker else None, demurrage)
    return RitToets(rit, eind, uit, kosten, toegewezen)


def toets_dag(ctx: DagContext) -> dict[int, RitToets]:
    rijtijden = rijtijd_per_chauffeur(ctx)
    return {r.id: toets_rit(ctx, r, rijtijden) for r in ctx.ritten}


def open_harde_regels(ctx: DagContext, toets: RitToets) -> list[Uitslag]:
    """Harde regels zonder override. Daarmee mag je niet publiceren."""
    return [u for u in toets.uitslagen if u.niveau == HARD and (toets.rit.id, u.nr) not in ctx.overrides]
