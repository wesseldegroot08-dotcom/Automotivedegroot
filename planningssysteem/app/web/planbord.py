"""Planbord: tijdlijn per trekker of chauffeur voor één dag.

Plannen kan op twee manieren: slepen met de muis, of met het formulier bij een rit
(werkt ook met alleen het toetsenbord). Bij elke wijziging draait de regelmotor opnieuw.
"""

from datetime import date, datetime, time, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models as m
from app.audit import log_actie
from app.keuzes import REDENCODES
from app.planner.context import dag_grenzen, laad_dag
from app.planner.ritten import maak_rit_voor_order, orders_zonder_rit, plan_rit
from app.planner.voorfilter import beschikbare_chauffeurs, eenheden, toegestane_paren
from app.ports.clock import NL, morgen_nl, vandaag_nl
from app.rules.basis import HARD, WAARSCHUWING
from app.rules.kosten import dd_bedrag_per_dag
from app.rules.planning import dd_banden, open_harde_regels, rijtijd_per_chauffeur, toets_dag
from app.statussen import OngeldigeOvergang, volgende, zet_status
from app.web.deps import csrf_controle, get_db, planner_of_admin
from app.web.sjablonen import templates

router = APIRouter(prefix="/planbord", dependencies=[Depends(csrf_controle)])

BEGIN_UUR, EIND_UUR = 4, 22


def _datum(tekst: str | None) -> date:
    if tekst:
        try:
            return date.fromisoformat(tekst)
        except ValueError:
            pass
    return morgen_nl()


def _positie(start: datetime, eind: datetime, d: date) -> tuple[float, float]:
    begin = datetime.combine(d, time(BEGIN_UUR)).replace(tzinfo=NL)
    totaal = (EIND_UUR - BEGIN_UUR) * 60
    links = max(0.0, (start - begin).total_seconds() / 60 / totaal * 100)
    breed = max(1.5, (eind - start).total_seconds() / 60 / totaal * 100)
    return round(links, 2), round(min(breed, 100 - links), 2)


def dag_waarschuwingen(ctx, toetsen, rijtijden) -> list[dict]:
    uit = []
    dagen = int(ctx.instellingen.get("lfd_waarschuwing_dagen", "2"))
    gezien = set()
    for rit in ctx.ritten:
        if not rit.order:
            continue
        for c in rit.order.containers:
            v = ctx.vrijgave_per_container.get(c.id)
            if v and c.id not in gezien and v.lfd <= ctx.datum + timedelta(days=dagen):
                gezien.add(c.id)
                banden = dd_banden(ctx, c)
                dag_na = (v.lfd - v.ontlaaddatum).days + 2
                bedrag = dd_bedrag_per_dag(banden, dag_na) if banden else None
                tekst = f"LFD {v.lfd:%d-%m} voor {c.nummer} ({rit.order.klantreferentie})."
                if bedrag:
                    tekst += f" Daarna € {bedrag / 100:.2f} per dag demurrage (voorbeeldtarief).".replace(".", ",", 1)
                uit.append({"soort": "LFD", "tekst": tekst, "rit_id": rit.id})
            if v and (v.status != "Vrij" or not (v.commercieel and v.douane and v.terminal_status)):
                uit.append({"soort": "Release", "tekst": f"Release ontbreekt voor {c.nummer} "
                            f"({rit.order.klantreferentie}): status '{v.status}'.", "rit_id": rit.id})
    for rit_id, t in toetsen.items():
        for u in t.uitslagen:
            if u.nr in (9, 10) and u.niveau in (HARD, WAARSCHUWING) and t.toegewezen:
                uit.append({"soort": "Slot", "tekst": f"Rit {rit_id} ({t.rit.order.klantreferentie}): {u.uitleg}",
                            "rit_id": rit_id})
    for c in beschikbare_chauffeurs(ctx):
        g = ctx.geschiedenis(c.id)
        rest_week = ctx.boek.waarde("rijtijd.week", ctx.datum, 3360) - g.rijtijd_deze_week_min
        if c.id in rijtijden:
            rt = rijtijden[c.id][0]
            rest_dag, rest_week = rt.rest_dag_min, rt.rest_week_min
        else:
            rest_dag = ctx.boek.waarde("rijtijd.dag", ctx.datum, 540)
        if min(rest_dag, rest_week) < 120:
            uit.append({"soort": "Rijtijd", "tekst": f"{c.pseudoniem} zit dicht bij de rijtijdlimiet: nog "
                        f"{min(rest_dag, rest_week) // 60} u {min(rest_dag, rest_week) % 60:02d} min rijden over "
                        f"(deze week nog {rest_week // 60} u).", "rit_id": None})
    return uit


def _kan_niet_gepland(ctx, toetsen) -> list[dict]:
    eenh = eenheden(ctx)
    chauffeurs = beschikbare_chauffeurs(ctx)
    uit = []
    for rit in ctx.ritten:
        if toetsen[rit.id].toegewezen:
            continue
        t = toegestane_paren(ctx, rit, eenh, chauffeurs)
        if t.paren:
            reden = f"Nog niet ingepland. {len(t.paren)} geschikte combinatie(s) mogelijk."
            niveau = "open"
        else:
            reden = " ".join(t.redenen)
            niveau = HARD
        uit.append({"rit": rit, "reden": reden, "niveau": niveau, "paren": t.paren[:6]})
    return uit


def planbord_context(db: Session, d: date, per: str, gekozen: int | None = None) -> dict:
    ctx = laad_dag(db, d)
    rijtijden = rijtijd_per_chauffeur(ctx)
    toetsen = toets_dag(ctx)
    if per == "chauffeur":
        rijen = [(c.id, c.pseudoniem, None) for c in db.scalars(select(m.Chauffeur).where(
            m.Chauffeur.actief.is_(True)).order_by(m.Chauffeur.pseudoniem))]
        sleutel = "chauffeur_id"
    else:
        rijen = [(t.id, f"{t.intern_nummer} · {t.kenteken}", t.status) for t in db.scalars(
            select(m.Trekker).where(m.Trekker.gearchiveerd.is_(False)).order_by(m.Trekker.intern_nummer))]
        sleutel = "trekker_id"
    blokken = {rid: [] for rid, _, _ in rijen}
    for rit in ctx.ritten:
        t = toetsen[rit.id]
        rid = getattr(rit, sleutel)
        if rit.gepland_start and rid in blokken:
            links, breed = _positie(rit.gepland_start, t.eind, d)
            blokken[rid].append({"rit": rit, "toets": t, "links": links, "breed": breed,
                                 "overrides": {nr for (r, nr) in ctx.overrides if r == rit.id}})
    afwezig = {a.chauffeur_id or a.trekker_id: a.reden for a in ctx.afwezig
               if (per == "chauffeur" and a.chauffeur_id) or (per != "chauffeur" and a.trekker_id)}
    toegewezen = [t for t in toetsen.values() if t.toegewezen]
    blokkerend = {t.rit.id: open_harde_regels(ctx, t) for t in toegewezen}
    gekozen_toets = toetsen.get(gekozen) if gekozen else None
    return {
        "datum": d, "per": per, "rijen": rijen, "blokken": blokken, "afwezig": afwezig,
        "uren": list(range(BEGIN_UUR, EIND_UUR + 1)), "kan_niet": _kan_niet_gepland(ctx, toetsen),
        "waarschuwingen": dag_waarschuwingen(ctx, toetsen, rijtijden), "rijtijden": rijtijden,
        "aantal_toegewezen": len(toegewezen), "aantal_ritten": len(ctx.ritten),
        "blokkerend": {k: v for k, v in blokkerend.items() if v},
        "gepubliceerd": bool(toegewezen) and all(t.rit.gepubliceerd for t in toegewezen),
        "gekozen": gekozen_toets, "ctx": ctx, "noodstop": ctx.instellingen.get("noodstop") == "aan",
        "orders_zonder_rit": orders_zonder_rit(db, _orders_van_dag(db, d)),
        "vorige": d - timedelta(days=1), "volgende": d + timedelta(days=1), "vandaag": vandaag_nl(),
    }


def _orders_van_dag(db, d):
    begin, eind = dag_grenzen(d)
    return list(db.scalars(select(m.Order).where(m.Order.venster_van >= begin, m.Order.venster_van < eind)))


def _rit_context(db: Session, rit: m.Rit, d: date) -> dict:
    ctx = laad_dag(db, d)
    toetsen = toets_dag(ctx)
    t = toetsen.get(rit.id)
    trekkers = db.scalars(select(m.Trekker).where(m.Trekker.gearchiveerd.is_(False))
                          .order_by(m.Trekker.intern_nummer)).all()
    chassis = db.scalars(select(m.Chassis).where(m.Chassis.gearchiveerd.is_(False)).order_by(m.Chassis.nummer)).all()
    chauffeurs = db.scalars(select(m.Chauffeur).where(m.Chauffeur.actief.is_(True))
                            .order_by(m.Chauffeur.pseudoniem)).all()
    terminals = [loc for loc in (rit.van_locatie, rit.naar_locatie) if loc.type == "terminal"]
    slots = db.scalars(select(m.Slot).where(m.Slot.rit_id == rit.id)).all()
    overrides = db.scalars(select(m.Override).where(m.Override.rit_id == rit.id)
                           .order_by(m.Override.tijd.desc())).all()
    return {"rit": rit, "toets": t, "duur": ctx.rit_duur(rit), "trekkers": trekkers, "chassis": chassis,
            "chauffeurs": chauffeurs, "volgende_status": volgende("rit", rit.status), "redencodes": REDENCODES,
            "terminals": terminals, "slots": slots, "overrides": overrides, "datum": d,
            "override_nrs": {o.regel_nr for o in overrides if o.actief}}


@router.get("")
def planbord(request: Request, datum: str = "", per: str = "trekker", rit: int | None = None,
             db: Session = Depends(get_db), gebruiker=Depends(planner_of_admin)):
    d = _datum(datum)
    ctx = planbord_context(db, d, "chauffeur" if per == "chauffeur" else "trekker", rit)
    ctx["melding"] = request.query_params.get("melding")
    ctx["fout"] = request.query_params.get("fout")
    if rit:
        r = db.get(m.Rit, rit)
        if r:
            ctx.update({"paneel": _rit_context(db, r, d)})
    return templates.TemplateResponse(request, "planbord/planbord.html", ctx)


@router.get("/rit/{rit_id}")
def rit_paneel(rit_id: int, request: Request, datum: str = "", db: Session = Depends(get_db),
               gebruiker=Depends(planner_of_admin)):
    rit = db.get(m.Rit, rit_id)
    if not rit:
        raise HTTPException(404, "Rit niet gevonden.")
    d = _datum(datum) if datum else (rit.gepland_start.astimezone(NL).date() if rit.gepland_start
                                     else rit.order.venster_van.astimezone(NL).date())
    if not request.headers.get("HX-Request"):
        return RedirectResponse(f"/planbord?datum={d}&rit={rit_id}#rit", status_code=303)
    return templates.TemplateResponse(request, "planbord/_rit.html", _rit_context(db, rit, d))


def _terug(d: date, rit_id: int | None = None, melding: str = "", fout: str = "", per: str = "trekker"):
    from urllib.parse import urlencode

    q = {"datum": d.isoformat(), "per": per}
    if rit_id:
        q["rit"] = rit_id
    if melding:
        q["melding"] = melding
    if fout:
        q["fout"] = fout
    return RedirectResponse("/planbord?" + urlencode(q) + ("#rit" if rit_id else ""), status_code=303)


def _tijd(d: date, hhmm: str) -> datetime | None:
    if not hhmm:
        return None
    try:
        u, mi = hhmm.split(":")[:2]
        return datetime.combine(d, time(int(u), int(mi))).replace(tzinfo=NL)
    except (ValueError, TypeError):
        raise HTTPException(422, "Vul een tijd in als uu:mm, bijvoorbeeld 08:30.") from None


def _int(v):
    try:
        return int(v) if v not in (None, "") else None
    except ValueError:
        return None


@router.post("/rit/{rit_id}/toewijzen")
async def toewijzen(rit_id: int, request: Request, db: Session = Depends(get_db),
                    gebruiker=Depends(planner_of_admin)):
    form = await request.form()
    rit = db.get(m.Rit, rit_id)
    if not rit:
        raise HTTPException(404, "Rit niet gevonden.")
    d = _datum(str(form.get("datum", "")))
    per = str(form.get("per", "trekker"))
    if rit.vastheid == "gestart":
        return _terug(d, rit_id, fout="Deze rit is gestart en staat vast.", per=per)
    ctx = laad_dag(db, d)
    start = _tijd(d, str(form.get("start", "")))
    try:
        oude_start = rit.gepland_start
        plan_rit(ctx, rit, start, _int(form.get("trekker_id")), _int(form.get("chassis_id")),
                 _int(form.get("chauffeur_id")))
    except (OngeldigeOvergang, ValueError) as e:
        db.rollback()
        return _terug(d, rit_id, fout=str(e), per=per)
    melding = "Rit opgeslagen. De regels zijn opnieuw getoetst."
    slot = db.scalar(select(m.Slot).where(m.Slot.rit_id == rit.id, m.Slot.status.in_(["Toegekend", "Gewijzigd"])))
    if slot and slot.slot_van and ctx.nu > slot.slot_van and oude_start != start:
        melding += " Let op: het slot is al begonnen. Deze wijziging telt als no-show."
        log_actie(db, "no-show-waarschuwing", tabel="rit", record_id=rit.id,
                  na={"tekst": "Rit gewijzigd na begin van het slot"})
    db.commit()
    return _terug(d, rit_id, melding=melding, per=per)


@router.post("/rit/{rit_id}/verplaats")
async def verplaats(rit_id: int, request: Request, db: Session = Depends(get_db),
                    gebruiker=Depends(planner_of_admin)):
    """Voor slepen op het planbord: nieuwe rij (trekker of chauffeur) en nieuwe begintijd."""
    form = await request.form()
    rit = db.get(m.Rit, rit_id)
    if not rit:
        raise HTTPException(404, "Rit niet gevonden.")
    d = _datum(str(form.get("datum", "")))
    per = str(form.get("per", "trekker"))
    rij = _int(form.get("rij_id"))
    minuten = _int(form.get("minuten")) or 0
    start = datetime.combine(d, time(BEGIN_UUR)).replace(tzinfo=NL) + timedelta(minutes=round(minuten / 15) * 15)
    trekker_id, chassis_id, chauffeur_id = rit.trekker_id, rit.chassis_id, rit.chauffeur_id
    if per == "chauffeur":
        chauffeur_id = rij
        c = db.get(m.Chauffeur, rij)
        if c and not trekker_id and c.voorkeur_trekker_id:
            trekker_id = c.voorkeur_trekker_id
    else:
        trekker_id = rij
    t = db.get(m.Trekker, trekker_id) if trekker_id else None
    if t and t.vaste_chassis_id and (per != "chauffeur" or not chassis_id):
        chassis_id = t.vaste_chassis_id
    if t and not chauffeur_id:
        c = db.scalar(select(m.Chauffeur).where(m.Chauffeur.voorkeur_trekker_id == t.id))
        chauffeur_id = c.id if c else None
    ctx = laad_dag(db, d)
    try:
        plan_rit(ctx, rit, start, trekker_id, chassis_id, chauffeur_id)
    except (OngeldigeOvergang, ValueError) as e:
        db.rollback()
        return _terug(d, rit_id, fout=str(e), per=per)
    db.commit()
    return _terug(d, rit_id, melding="Rit verplaatst. De regels zijn opnieuw getoetst.", per=per)


@router.post("/rit/{rit_id}/status")
async def status(rit_id: int, request: Request, db: Session = Depends(get_db), gebruiker=Depends(planner_of_admin)):
    form = await request.form()
    rit = db.get(m.Rit, rit_id)
    if not rit:
        raise HTTPException(404, "Rit niet gevonden.")
    d = _datum(str(form.get("datum", "")))
    try:
        zet_status(rit, "rit", str(form.get("status", "")))
        if rit.status == "Onderweg":
            rit.vastheid = "gestart"
    except OngeldigeOvergang as e:
        db.rollback()
        return _terug(d, rit_id, fout=str(e))
    db.commit()
    return _terug(d, rit_id, melding=f"Status is nu '{rit.status}'.")


@router.post("/rit/{rit_id}/vastheid")
async def vastheid(rit_id: int, request: Request, db: Session = Depends(get_db), gebruiker=Depends(planner_of_admin)):
    form = await request.form()
    rit = db.get(m.Rit, rit_id)
    nieuw = str(form.get("vastheid", ""))
    d = _datum(str(form.get("datum", "")))
    if not rit or nieuw not in ("open", "toegezegd"):
        return _terug(d, rit_id, fout="Kies 'open' of 'toegezegd'. 'Gestart' gaat vanzelf als de rit begint.")
    if rit.vastheid == "gestart":
        return _terug(d, rit_id, fout="Een gestarte rit kan niet meer vrijgegeven worden.")
    rit.vastheid = nieuw
    db.commit()
    return _terug(d, rit_id, melding=f"Vastheid is nu '{nieuw}'.")


def maak_override(db: Session, rit: m.Rit, regel_nr: int, niveau: str, uitleg: str, reden_code: str,
                  reden: str, gebruiker: str) -> m.Override:
    """Een override kan alleen met een redencode én een uitleg."""
    if reden_code not in REDENCODES:
        raise ValueError("Kies een redencode.")
    if not reden or len(reden.strip()) < 5:
        raise ValueError("Schrijf kort op waarom je doorgaat (minimaal 5 tekens).")
    o = m.Override(rit_id=rit.id, regel_nr=regel_nr, niveau=niveau, uitleg_regel=uitleg, reden_code=reden_code,
                   reden=reden.strip(), gebruiker=gebruiker)
    db.add(o)
    log_actie(db, "override", tabel="rit", record_id=rit.id, na={"regel": regel_nr, "niveau": niveau,
                                                                 "uitleg": uitleg}, reden_code=reden_code,
              reden=reden.strip())
    return o


@router.post("/rit/{rit_id}/override")
async def override(rit_id: int, request: Request, db: Session = Depends(get_db), gebruiker=Depends(planner_of_admin)):
    form = await request.form()
    rit = db.get(m.Rit, rit_id)
    if not rit:
        raise HTTPException(404, "Rit niet gevonden.")
    d = _datum(str(form.get("datum", "")))
    try:
        maak_override(db, rit, int(form.get("regel_nr", 0)), str(form.get("niveau", "")),
                      str(form.get("uitleg", "")), str(form.get("reden_code", "")), str(form.get("reden", "")),
                      gebruiker.gebruikersnaam)
    except ValueError as e:
        db.rollback()
        return _terug(d, rit_id, fout=f"Override niet opgeslagen: {e}")
    db.commit()
    return _terug(d, rit_id, melding="Override opgeslagen met reden. Je ziet hem in het logboek.")


@router.post("/rit/{rit_id}/slot")
async def slot_invoeren(rit_id: int, request: Request, db: Session = Depends(get_db),
                        gebruiker=Depends(planner_of_admin)):
    """Handmatig een slot invullen (bijvoorbeeld uit het terminalportaal)."""
    form = await request.form()
    rit = db.get(m.Rit, rit_id)
    d = _datum(str(form.get("datum", "")))
    if not rit:
        raise HTTPException(404, "Rit niet gevonden.")
    terminal_id = _int(form.get("terminal_id"))
    van, tot = _tijd(d, str(form.get("slot_van", ""))), _tijd(d, str(form.get("slot_tot", "")))
    if not terminal_id or not van or not tot or tot <= van:
        return _terug(d, rit_id, fout="Vul terminal, begin en einde van het slot in (einde na begin).")
    bestaand = db.scalar(select(m.Slot).where(m.Slot.rit_id == rit.id, m.Slot.terminal_id == terminal_id,
                                              m.Slot.status.in_(["Toegekend", "Gewijzigd", "Aangevraagd"])))
    if bestaand:
        bestaand.slot_van, bestaand.slot_tot = van, tot
        bestaand.tar = str(form.get("tar", "")) or bestaand.tar
        if bestaand.status == "Toegekend":
            zet_status(bestaand, "slot", "Gewijzigd")
    else:
        db.add(m.Slot(rit_id=rit.id, terminal_id=terminal_id, slot_van=van, slot_tot=tot,
                      tar=str(form.get("tar", "")) or None, label=f"HANDMATIG-{rit.id}", status="Toegekend"))
    db.commit()
    return _terug(d, rit_id, melding="Slot opgeslagen.")


@router.post("/ritten-aanmaken")
async def ritten_aanmaken(request: Request, db: Session = Depends(get_db), gebruiker=Depends(planner_of_admin)):
    form = await request.form()
    d = _datum(str(form.get("datum", "")))
    nieuw = orders_zonder_rit(db, _orders_van_dag(db, d))
    for o in nieuw:
        maak_rit_voor_order(db, o)
    db.commit()
    return _terug(d, melding=f"{len(nieuw)} rit(ten) aangemaakt.")


@router.post("/publiceren")
async def publiceren(request: Request, db: Session = Depends(get_db), gebruiker=Depends(planner_of_admin)):
    form = await request.form()
    d = _datum(str(form.get("datum", "")))
    ctx = laad_dag(db, d)
    toetsen = toets_dag(ctx)
    toegewezen = [t for t in toetsen.values() if t.toegewezen]
    if not toegewezen:
        return _terug(d, fout="Er zijn nog geen ingeplande ritten om te publiceren.")
    blokkades = [(t.rit, u) for t in toegewezen for u in open_harde_regels(ctx, t)]
    if blokkades:
        tekst = "; ".join(f"rit {r.id} regel {u.nr}" for r, u in blokkades[:8])
        return _terug(d, fout=f"Niet gepubliceerd: {len(blokkades)} harde regel(s) zonder override ({tekst}). "
                              "Los ze op of overrule ze met een reden.")
    for t in toegewezen:
        t.rit.gepubliceerd = True
    log_actie(db, "publiceren", tabel="planning", record_id=d.isoformat(),
              na={"ritten": [t.rit.id for t in toegewezen]})
    db.commit()
    return _terug(d, melding=f"Planning van {d:%d-%m-%Y} gepubliceerd ({len(toegewezen)} ritten).")


@router.get("/terminals")
def terminals(request: Request, db: Session = Depends(get_db), gebruiker=Depends(planner_of_admin)):
    from app.planner.context import wachttijd_statistiek

    stats = wachttijd_statistiek(db)
    locaties = db.scalars(select(m.Locatie).where(m.Locatie.type.in_(["terminal", "depot", "klant"]))
                          .order_by(m.Locatie.type, m.Locatie.naam)).all()
    return templates.TemplateResponse(request, "planbord/terminals.html", {"stats": stats, "locaties": locaties})
