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
from app.eenvoudig import kort_reden, regel_zin
from app.keuzes import REDENCODES
from app.planner.automatisch import laatste_voorstel
from app.planner.context import dag_grenzen, laad_dag
from app.planner.ritten import maak_rit_voor_order, orders_zonder_rit, plan_op_chauffeur, plan_rit
from app.planner.voorfilter import beschikbare_chauffeurs, eenheden, toegestane_paren
from app.planner.voorstel import aangepast_door_planner, blokkades_voor_publiceren, goedgekeurd_voorstel
from app.ports.clock import NL, morgen_nl, vandaag_nl
from app.rules.basis import HARD, WAARSCHUWING
from app.rules.planning import toets_dag
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


def _niet_gepland(ctx, toetsen) -> list[dict]:
    """Ritten zonder chauffeur of tijd, met één korte reden in gewone woorden."""
    eenh = eenheden(ctx)
    chauffeurs = beschikbare_chauffeurs(ctx)
    uit = []
    for rit in ctx.ritten:
        if toetsen[rit.id].toegewezen:
            continue
        t = toegestane_paren(ctx, rit, eenh, chauffeurs)
        if t.paren:
            uit.append({"rit": rit, "reden": "", "kan": True})
        else:
            uit.append({"rit": rit, "reden": kort_reden(" ".join(t.redenen)), "kan": False})
    return uit


def korte_klant(rit: m.Rit) -> str:
    return rit.order.klant.naam.replace(" (demo)", "") if rit.order and rit.order.klant else ""


def planbord_context(db: Session, d: date, per: str = "chauffeur", gekozen: int | None = None) -> dict:
    ctx = laad_dag(db, d)
    toetsen = toets_dag(ctx)
    if per == "trekker":
        rijen = [(t.id, f"{t.intern_nummer} · {t.kenteken}", t.status if t.status != "actief" else "")
                 for t in db.scalars(select(m.Trekker).where(m.Trekker.gearchiveerd.is_(False))
                                     .order_by(m.Trekker.intern_nummer))]
        sleutel = "trekker_id"
    else:
        rijen = []
        afwezig = {a.chauffeur_id: a.reden for a in ctx.afwezig if a.chauffeur_id}
        for c in db.scalars(select(m.Chauffeur).where(m.Chauffeur.actief.is_(True))
                            .order_by(m.Chauffeur.pseudoniem)):
            if c.id in afwezig:
                notitie = f"afwezig ({afwezig[c.id]})"
            elif not ctx.trekker_van(c):
                notitie = "geen trekker"
            else:
                notitie = ""
            rijen.append((c.id, c.pseudoniem, notitie))
        sleutel = "chauffeur_id"
    blokken = {rid: [] for rid, _, _ in rijen}
    for rit in ctx.ritten:
        t = toetsen[rit.id]
        rid = getattr(rit, sleutel)
        if rit.gepland_start and rid in blokken:
            links, breed = _positie(rit.gepland_start, t.eind, d)
            blokken[rid].append({"rit": rit, "toets": t, "links": links, "breed": breed, "klant": korte_klant(rit),
                                 "niveau": t.ergste, "concept": False})
    # Het automatische plan dat nog op akkoord wacht: als 'concept' op het bord (stippellijn)
    concept = None
    v = laatste_voorstel(db, d)
    if v and v.status == "Voorgesteld" and not ctx.instellingen.get("noodstop") == "aan":
        concept = v
        for r in v.regels:
            if not r.ingepland or r.rit_id not in toetsen or toetsen[r.rit_id].toegewezen:
                continue
            rid = getattr(r, sleutel)
            if rid in blokken and r.start and r.eind:
                links, breed = _positie(r.start, r.eind, d)
                blokken[rid].append({"rit": r.rit, "toets": None, "links": links, "breed": breed,
                                     "klant": korte_klant(r.rit), "concept": True,
                                     "niveau": "waarschuwing" if r.harde_problemen else "ok", "start": r.start,
                                     "eind": r.eind})
    in_concept = {b["rit"].id for rij in blokken.values() for b in rij if b["concept"]}
    redenen = {r.rit_id: r.reden for r in (concept.regels if concept else []) if r.reden}
    niet_gepland = [k for k in _niet_gepland(ctx, toetsen) if k["rit"].id not in in_concept]
    for k in niet_gepland:
        if k["rit"].id in redenen:
            k.update(reden=kort_reden(redenen[k["rit"].id]), kan=False)
    niet_gepland.sort(key=lambda k: (k["kan"], k["rit"].order.venster_van))
    toegewezen = [t for t in toetsen.values() if t.toegewezen]
    return {
        "datum": d, "per": per, "rijen": rijen, "blokken": blokken,
        "uren": list(range(BEGIN_UUR, EIND_UUR + 1)), "niet_gepland": niet_gepland,
        "concept": concept, "aantal_concept": len(in_concept),
        "aantal_toegewezen": len(toegewezen), "aantal_ritten": len(ctx.ritten),
        "aantal_verstuurd": sum(1 for t in toegewezen if t.rit.gepubliceerd),
        "gepubliceerd": bool(toegewezen) and all(t.rit.gepubliceerd for t in toegewezen),
        "gekozen": gekozen, "ctx": ctx, "noodstop": ctx.instellingen.get("noodstop") == "aan",
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
    afwezig = {a.chauffeur_id for a in ctx.afwezig if a.chauffeur_id}
    keuzes = []
    for c in chauffeurs:
        tid = ctx.trekker_van(c)
        tr = db.get(m.Trekker, tid) if tid else None
        if c.id in afwezig:
            extra = "afwezig"
        elif not tr:
            extra = "geen trekker"
        else:
            extra = tr.intern_nummer
        keuzes.append({"id": c.id, "naam": c.pseudoniem, "extra": extra, "kan": bool(tr) and c.id not in afwezig})
    problemen = []
    if t and t.toegewezen:
        for u in t.uitslagen:
            if u.niveau in (HARD, WAARSCHUWING):
                problemen.append({"niveau": u.niveau, "tekst": regel_zin(u.nr, u.uitleg)})
    elif t:
        r = toegestane_paren(ctx, rit, eenheden(ctx), beschikbare_chauffeurs(ctx))
        if not r.paren:
            problemen.append({"niveau": HARD, "tekst": kort_reden(" ".join(r.redenen))})
    plan = None
    v = laatste_voorstel(db, d)
    if v and v.status == "Voorgesteld" and not (t and t.toegewezen):
        plan = next((r for r in v.regels if r.rit_id == rit.id and r.ingepland), None)
    terminals = [loc for loc in (rit.van_locatie, rit.naar_locatie) if loc.type == "terminal"]
    slots = db.scalars(select(m.Slot).where(m.Slot.rit_id == rit.id)).all()
    overrides = db.scalars(select(m.Override).where(m.Override.rit_id == rit.id)
                           .order_by(m.Override.tijd.desc())).all()
    return {"rit": rit, "toets": t, "duur": ctx.rit_duur(rit), "trekkers": trekkers, "chassis": chassis,
            "chauffeurs": chauffeurs, "keuzes": keuzes, "problemen": problemen, "plan": plan, "klant": korte_klant(rit),
            "volgende_status": volgende("rit", rit.status), "redencodes": REDENCODES,
            "terminals": terminals, "slots": slots, "overrides": overrides, "datum": d,
            "override_nrs": {o.regel_nr for o in overrides if o.actief},
            "noodstop": ctx.instellingen.get("noodstop") == "aan"}


@router.get("")
def planbord(request: Request, datum: str = "", per: str = "chauffeur", rit: int | None = None,
             db: Session = Depends(get_db), gebruiker=Depends(planner_of_admin)):
    d = _datum(datum)
    ctx = planbord_context(db, d, "trekker" if per == "trekker" else "chauffeur", rit)
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
    return templates.TemplateResponse(request, "planbord/_rit.html", {"p": _rit_context(db, rit, d)})


def _terug(d: date, rit_id: int | None = None, melding: str = "", fout: str = "", per: str = "chauffeur"):
    from urllib.parse import urlencode

    q = {"datum": d.isoformat()}
    if per == "trekker":
        q["per"] = per
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
    per = str(form.get("per", "chauffeur"))
    if rit.vastheid == "gestart":
        return _terug(d, rit_id, fout="Deze rit is gestart en staat vast.", per=per)
    ctx = laad_dag(db, d)
    start = _tijd(d, str(form.get("start", "")))
    try:
        oude_start = rit.gepland_start
        if "trekker_id" in form or "chassis_id" in form:  # oude manier: alles zelf kiezen (onder 'meer')
            plan_rit(ctx, rit, start, _int(form.get("trekker_id")), _int(form.get("chassis_id")),
                     _int(form.get("chauffeur_id")))
        else:  # gewoon: kies de chauffeur, zijn eigen trekker en trailer gaan mee
            plan_op_chauffeur(ctx, rit, start, _int(form.get("chauffeur_id")))
    except (OngeldigeOvergang, ValueError) as e:
        db.rollback()
        return _terug(d, rit_id, fout=str(e), per=per)
    melding = "Opgeslagen en gecontroleerd."
    slot = db.scalar(select(m.Slot).where(m.Slot.rit_id == rit.id, m.Slot.status.in_(["Toegekend", "Gewijzigd"])))
    if slot and slot.slot_van and ctx.nu > slot.slot_van and oude_start != start:
        melding += " Let op: het tijdslot bij de terminal is al begonnen. Dit telt als no-show."
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
    per = str(form.get("per", "chauffeur"))
    rij = _int(form.get("rij_id"))
    minuten = _int(form.get("minuten")) or 0
    start = datetime.combine(d, time(BEGIN_UUR)).replace(tzinfo=NL) + timedelta(minutes=round(minuten / 15) * 15)
    if rit.vastheid == "gestart":
        return _terug(d, rit_id, fout="Deze rit is gestart en staat vast.", per=per)
    ctx = laad_dag(db, d)
    try:
        if per == "trekker":
            t = db.get(m.Trekker, rij) if rij else None
            chassis_id = t.vaste_chassis_id if t and t.vaste_chassis_id else rit.chassis_id
            c = db.scalar(select(m.Chauffeur).where(m.Chauffeur.voorkeur_trekker_id == rij)) if rij else None
            plan_rit(ctx, rit, start, rij, chassis_id, rit.chauffeur_id or (c.id if c else None))
        else:
            plan_op_chauffeur(ctx, rit, start, rij)
    except (OngeldigeOvergang, ValueError) as e:
        db.rollback()
        return _terug(d, rit_id, fout=str(e), per=per)
    db.commit()
    return _terug(d, rit_id, melding="Verplaatst en gecontroleerd.", per=per)


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
    voorstel = goedgekeurd_voorstel(db, d)
    blokkades = blokkades_voor_publiceren(ctx, toetsen, voorstel)
    if blokkades:
        tekst = "; ".join(f"rit {r.id} regel {u.nr}" for r, u in blokkades[:8])
        return _terug(d, fout=f"Niet gepubliceerd: {len(blokkades)} harde regel(s) zonder override ({tekst}). "
                              "Los ze op of overrule ze met een reden.")
    for t in toegewezen:
        t.rit.gepubliceerd = True
    if voorstel:
        voorstel.aangepast_door_planner = aangepast_door_planner(voorstel, ctx)
        zet_status(voorstel, "voorstel", "Gepubliceerd")
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


def _stuur(db: Session, rit_id: int, gebruiker: str, bevestig: bool) -> tuple[list[str], str]:
    """Via de job-wachtrij (idempotent): zelfde rit, tijd en keuze = zelfde taak."""
    import json

    from app.jobs import plaats_job, voer_uit

    rit = db.get(m.Rit, rit_id)
    sleutel = f"pn:{rit_id}:{rit.gepland_start.isoformat() if rit and rit.gepland_start else '-'}:{int(bevestig)}"
    job = plaats_job(db, "prenotificatie", {"rit_id": rit_id, "gebruiker": gebruiker, "bevestig": bevestig}, sleutel)
    db.commit()
    voer_uit(job.id)
    db.expire_all()
    job = db.get(m.Job, job.id)
    if job.status == "fout":
        fout = (job.fout or "").splitlines()[0].split(": ", 1)[-1]
        job.sleutel += f":mislukt-{job.id}"  # later opnieuw proberen mag
        db.commit()
        return [], fout
    return json.loads(job.resultaat or "{}").get("teksten", []), ""


@router.post("/rit/{rit_id}/prenotificatie")
async def prenotificatie(rit_id: int, request: Request, db: Session = Depends(get_db),
                         gebruiker=Depends(planner_of_admin)):
    form = await request.form()
    d = _datum(str(form.get("datum", "")))
    teksten, fout = _stuur(db, rit_id, gebruiker.gebruikersnaam, form.get("bevestig") == "ja")
    if fout:
        return _terug(d, rit_id, fout=fout)
    return _terug(d, rit_id, melding="Pre-notificatie (simulator): " + " ".join(teksten))


@router.post("/prenotificaties")
async def prenotificaties_dag(request: Request, db: Session = Depends(get_db), gebruiker=Depends(planner_of_admin)):
    """Stuur pre-notificaties voor alle geplande ritten van de dag die nog geen slot hebben."""
    form = await request.form()
    d = _datum(str(form.get("datum", "")))
    ctx = laad_dag(db, d)
    gestuurd, fouten = 0, []
    for rit in ctx.ritten:
        if rit.status not in ("Gepland", "Geaccepteerd") or ctx.slots_per_rit.get(rit.id):
            continue
        if not any(loc.type == "terminal" for loc in (rit.van_locatie, rit.naar_locatie)):
            continue
        teksten, fout = _stuur(db, rit.id, gebruiker.gebruikersnaam, False)
        if fout:
            fouten.append(f"rit {rit.id}: {fout}")
        else:
            gestuurd += 1
    melding = f"{gestuurd} pre-notificatie(s) verstuurd (simulator)."
    return _terug(d, melding=melding, fout="; ".join(fouten[:5]))
