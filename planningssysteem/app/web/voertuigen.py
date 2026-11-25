"""Voertuigen: trekkers, chassis, voorkeuren, combinatiepagina en CSV import/export.

Niets wordt echt verwijderd: je kunt een voertuig archiveren. De historie blijft bestaan.
"""

import csv
import io
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import keuzes as k
from app import models as m
from app.ports.clock import vandaag_nl
from app.rules.basis import RegelBoek, ergste
from app.rules.voertuig import (
    GRENZEN,
    ContainerInvoer,
    aslast_grens,
    bereken_gewicht,
    chassis_uit,
    geschikt_voor,
    grens_code_voor,
    toets_combinatie,
    trekker_uit,
)
from app.rules.volledigheid import ontbreekt_chassis, ontbreekt_trekker, volledigheid_procent
from app.web.deps import csrf_controle, get_db, planner_of_admin
from app.web.sjablonen import templates
from app.web.velden import Veld, controleer

router = APIRouter(prefix="/voertuigen", dependencies=[Depends(csrf_controle)])


def _naam(o):
    return getattr(o, "naam", None) or getattr(o, "nummer", None) or getattr(o, "pseudoniem", None) or f"#{o.id}"


TREKKER_VELDEN = [
    Veld("kenteken", "Kenteken", verplicht=True),
    Veld("intern_nummer", "Intern nummer", verplicht=True),
    Veld("merk_model", "Merk en model (vrije tekst)"),
    Veld("bouwjaar", "Bouwjaar", "getal", min=1980, max=2100),
    Veld("aandrijving", "Assen en aandrijving", "keuze", verplicht=True, keuzes=k.AANDRIJVING),
    Veld("tarra_kg", "Tarra (leeggewicht) in kg", "getal", min=0, max=30000),
    Veld("tarra_bron", "Bron van de tarra", "keuze", verplicht=True, keuzes=k.TARRA_BRON,
         hulp="Verplicht kiezen. Weet je het niet zeker? Kies 'aanname'."),
    Veld("toegestane_massa_kg", "Technisch toegestane massa (kg)", "getal", min=0),
    Veld("max_aandrijfas_kg", "Max last aandrijfas (kg)", "getal", min=0),
    Veld("max_koppelplaat_kg", "Max koppelplaatlast (kg)", "getal", min=0),
    Veld("euro_klasse", "Euro-klasse (bijv. Euro 6)"),
    Veld("co2_klasse", "CO2-klasse (voor tol, 1 t/m 5)", "getal", min=1, max=5),
    Veld("zero_emissie", "Zero-emissie", "bool"),
    Veld("adr_uitvoering", "ADR-uitvoering", "keuze", verplicht=True, keuzes=k.ADR_UITVOERING),
    Veld("lzv_geschikt", "LZV-geschikt", "bool"),
    Veld("lzv_ontheffing_tot", "LZV-ontheffing geldig tot", "datum"),
    Veld("tolkastje", "Tolkastje aanwezig", "bool"),
    Veld("apk_datum", "APK geldig tot", "datum"),
    Veld("onderhoud_datum", "Volgend onderhoud", "datum"),
    Veld("tachograaf_ijking", "Tachograaf-ijking geldig tot", "datum"),
    Veld("status", "Status", "keuze", verplicht=True, keuzes=k.VOERTUIG_STATUS),
    Veld("standplaats_id", "Standplaats / standaard depot", "fk", fk_model=m.Locatie, fk_label=_naam),
    Veld("opmerking", "Opmerkingen", "lang"),
    # voorkeuren met één waarde
    Veld("begin_tijd", "Standaard begintijd", "tijd"),
    Veld("eind_tijd", "Standaard eindtijd", "tijd"),
    Veld("max_km_dag", "Max kilometers per dag", "getal", min=0),
    Veld("kosten_per_km_cent", "Kosten per km (cent)", "getal", min=0),
    Veld("kosten_per_uur_cent", "Kosten per uur (cent)", "getal", min=0),
    Veld("verbruik_l_per_100km", "Brandstofverbruik (liter per 100 km)", "getal", min=0),
    Veld("vaste_chassis_id", "Vaste chassis-koppeling (optioneel)", "fk", fk_model=m.Chassis, fk_label=_naam),
]

CHASSIS_VELDEN = [
    Veld("nummer", "Nummer", verplicht=True),
    Veld("type", "Type", "keuze", verplicht=True, keuzes=k.CHASSIS_TYPES),
    Veld("assen", "Aantal assen", "getal", verplicht=True, min=1, max=4),
    Veld("tarra_kg", "Tarra (leeggewicht) in kg", "getal", min=0, max=20000),
    Veld("tarra_bron", "Bron van de tarra", "keuze", verplicht=True, keuzes=k.TARRA_BRON),
    Veld("max_kingpin_kg", "Max last koppelpen / kingpin (kg)", "getal", min=0),
    Veld("max_asgroep_kg", "Max last as-groep (kg)", "getal", min=0),
    Veld("kingpinhoogte_mm", "Kingpinhoogte (mm)", "getal", min=0),
    Veld("lengte_in_mm", "Lengte ingeschoven (mm)", "getal", min=0),
    Veld("lengte_uit_mm", "Lengte uitgeschoven (mm)", "getal", min=0),
    Veld("twistlock_20", "Twistlocks voor 20ft", "bool"),
    Veld("twistlock_40", "Twistlocks voor 40ft", "bool"),
    Veld("twistlock_45", "Twistlocks voor 45ft", "bool"),
    Veld("liftas", "Liftas", "bool"),
    Veld("genset", "Reefer-genset", "keuze", verplicht=True, keuzes=k.GENSET),
    Veld("geschikt_voor", "Geschikt voor (komma's: dry, HC, reefer, tank, flat rack, open top)", verplicht=True),
    Veld("max_bruto_container_kg", "Max bruto containergewicht (kg)", "getal", min=0),
    Veld("adr_tank", "ADR/tank-geschikt", "bool"),
    Veld("kiepfunctie", "Kiepfunctie", "bool"),
    Veld("eigen_of_pool", "Eigen of pool", "keuze", verplicht=True, keuzes=["eigen", "pool"]),
    Veld("keuring_datum", "Keuring geldig tot", "datum"),
    Veld("status", "Status", "keuze", verplicht=True, keuzes=k.VOERTUIG_STATUS),
    Veld("opmerking", "Opmerkingen", "lang"),
]

SOORTEN = {
    "trekker": (m.Trekker, TREKKER_VELDEN, "Trekker"),
    "chassis": (m.Chassis, CHASSIS_VELDEN, "Chassis"),
}

# Sjablonen: een begin voor een nieuw voertuig. Waarden die een aanname zijn, krijgen bron 'aanname'.
SJABLONEN = {
    "trekker": {
        "4x2-aanname": ("4x2 trekker, aanname", {"aandrijving": "4x2", "tarra_bron": "aanname",
                                                 "adr_uitvoering": "geen", "status": "actief"}),
        "6x2-aanname": ("6x2 trekker, aanname", {"aandrijving": "6x2", "tarra_bron": "aanname",
                                                 "adr_uitvoering": "geen", "status": "actief"}),
        "4x2-adr-tank": ("4x2 trekker met ADR-tank, aanname", {"aandrijving": "4x2", "tarra_bron": "aanname",
                                                               "adr_uitvoering": "tank", "status": "actief"}),
    },
    "chassis": {
        "vast-20": ("Vast 20ft (3.450 kg, fabrikant)", {"type": "20ft", "assen": 2, "tarra_kg": 3450,
                                                       "tarra_bron": "fabrikant", "twistlock_20": True,
                                                       "geschikt_voor": "dry,HC", "genset": "niet",
                                                       "eigen_of_pool": "eigen", "status": "actief"}),
        "vast-40": ("Vast 40ft (4.540 kg, fabrikant)", {"type": "40ft", "assen": 3, "tarra_kg": 4540,
                                                       "tarra_bron": "fabrikant", "twistlock_40": True,
                                                       "geschikt_voor": "dry,HC", "genset": "niet",
                                                       "eigen_of_pool": "eigen", "status": "actief"}),
        "multi": ("Multi-chassis 20-45ft (5.300 kg, fabrikant)", {"type": "multi", "assen": 3, "tarra_kg": 5300,
                                                                  "tarra_bron": "fabrikant", "twistlock_20": True,
                                                                  "twistlock_40": True, "twistlock_45": True,
                                                                  "geschikt_voor": "dry,HC", "genset": "niet",
                                                                  "eigen_of_pool": "eigen", "status": "actief"}),
    },
}


def _soort(soort: str):
    if soort not in SOORTEN:
        raise HTTPException(404, "Onbekend soort voertuig.")
    return SOORTEN[soort]


def _vandaag() -> date:
    return vandaag_nl()


# ------------------------------------------------------------------ overzicht


@router.get("")
def overzicht(request: Request, archief: int = 0, db: Session = Depends(get_db),
              gebruiker=Depends(planner_of_admin)):
    vandaag = _vandaag()
    tq = select(m.Trekker).order_by(m.Trekker.intern_nummer)
    cq = select(m.Chassis).order_by(m.Chassis.nummer)
    if not archief:
        tq = tq.where(m.Trekker.gearchiveerd.is_(False))
        cq = cq.where(m.Chassis.gearchiveerd.is_(False))
    trekkers = [(t, ontbreekt_trekker(t, vandaag)) for t in db.scalars(tq)]
    chassis = [(c, ontbreekt_chassis(c, vandaag)) for c in db.scalars(cq)]
    return templates.TemplateResponse(request, "voertuigen/overzicht.html", {
        "trekkers": trekkers, "chassis": chassis, "sjablonen": SJABLONEN, "archief": archief,
        "melding": request.query_params.get("melding"),
    })


# ------------------------------------------------------------------ formulier


def _waarden(obj, velden) -> dict:
    uit = {}
    for v in velden:
        w = getattr(obj, v.naam, None) if obj is not None else None
        uit[v.naam] = "" if w is None else (w.strftime("%H:%M") if v.soort == "tijd" else w)
    return uit


def _fk_keuzes(db, velden):
    return {v.naam: [(r.id, v.fk_label(r)) for r in db.scalars(select(v.fk_model).order_by(v.fk_model.id))]
            for v in velden if v.soort == "fk"}


def _detail_context(db: Session, soort: str, obj) -> dict:
    if obj is None:
        return {}
    vandaag = _vandaag()
    boek = RegelBoek.laad(db)
    if soort == "trekker":
        ontbreekt = ontbreekt_trekker(obj, vandaag)
        voorkeuren = db.scalars(select(m.VoertuigVoorkeur).where(m.VoertuigVoorkeur.trekker_id == obj.id)).all()
        afw = db.scalars(select(m.Afwezigheid).where(m.Afwezigheid.trekker_id == obj.id)).all()
        andere = db.scalars(select(m.Chassis).where(m.Chassis.gearchiveerd.is_(False)).order_by(m.Chassis.nummer))
        combos = [(obj, c) for c in andere]
    else:
        ontbreekt = ontbreekt_chassis(obj, vandaag)
        voorkeuren = db.scalars(select(m.VoertuigVoorkeur).where(m.VoertuigVoorkeur.chassis_id == obj.id)).all()
        afw = db.scalars(select(m.Afwezigheid).where(m.Afwezigheid.chassis_id == obj.id)).all()
        andere = db.scalars(select(m.Trekker).where(m.Trekker.gearchiveerd.is_(False))
                            .order_by(m.Trekker.intern_nummer))
        combos = [(t, obj) for t in andere]
    rijen = []
    for t, c in combos:
        ti, ci = trekker_uit(t), chassis_uit(c)
        g = bereken_gewicht(boek, vandaag, ti, ci, [], [grens_code_voor("NL-intermodaal", t.aandrijving)])
        a = aslast_grens(boek, vandaag, t.aandrijving, c.assen)
        rijen.append({"trekker": t, "chassis": c, "gewicht": g, "aslast": a, "geschikt": geschikt_voor(ti, ci)})
    return {"ontbreekt": ontbreekt, "volledig": volledigheid_procent(ontbreekt), "voorkeuren": voorkeuren,
            "afwezigheid": afw, "combos": rijen}


def _toon_formulier(request, db, soort, obj, waarden, fouten, status=200):
    model, velden, titel = _soort(soort)
    ctx = {"soort": soort, "titel": titel, "obj": obj, "velden": velden, "waarden": waarden, "fouten": fouten,
           "fk_keuzes": _fk_keuzes(db, velden), "voorkeur_soorten": k.VOORKEUR_SOORTEN,
           "voorkeur_taken": k.VOORKEUR_TAKEN}
    ctx.update(_detail_context(db, soort, obj))
    return templates.TemplateResponse(request, "voertuigen/formulier.html", ctx, status_code=status)


@router.get("/{soort}/nieuw")
def nieuw(soort: str, request: Request, sjabloon: str = "", db: Session = Depends(get_db),
          gebruiker=Depends(planner_of_admin)):
    model, velden, _ = _soort(soort)
    waarden = _waarden(None, velden)
    if sjabloon:
        sj = SJABLONEN.get(soort, {}).get(sjabloon)
        if not sj:
            raise HTTPException(404, "Onbekend sjabloon.")
        waarden.update(sj[1])
        if soort == "trekker":
            # Tarra uit de regeltabel (aanname 8.000 kg), niet uit de code
            waarden["tarra_kg"] = RegelBoek.laad(db).waarde("trekker.tarra.aanname", _vandaag(), "") or ""
    return _toon_formulier(request, db, soort, None, waarden, {})


def controleer_voertuig(db: Session, soort: str, invoer: dict, obj_id: int | None = None):
    model, velden, _ = _soort(soort)
    uitkomst = controleer(velden, invoer)
    if not uitkomst.ok:
        return uitkomst
    d = uitkomst.data
    sleutel = "kenteken" if soort == "trekker" else "nummer"
    d[sleutel] = d[sleutel].upper().strip()
    bestaand = db.scalar(select(model).where(getattr(model, sleutel) == d[sleutel]))
    if bestaand and bestaand.id != obj_id:
        uitkomst.fouten[sleutel] = f"Er bestaat al een {soort} met {sleutel} {d[sleutel]}."
    if soort == "chassis":
        onbekend = {s.strip() for s in d["geschikt_voor"].split(",")} - set(k.CONTAINER_SOORTEN)
        if onbekend:
            uitkomst.fouten["geschikt_voor"] = "Onbekend: " + ", ".join(sorted(onbekend)) + ". Kies uit: " + ", ".join(
                k.CONTAINER_SOORTEN) + "."
    return uitkomst


async def _opslaan(soort, request, db, obj_id=None):
    model, velden, _ = _soort(soort)
    form = dict(await request.form())
    uitkomst = controleer_voertuig(db, soort, form, obj_id)
    obj = db.get(model, obj_id) if obj_id else None
    if obj_id and obj is None:
        raise HTTPException(404, "Niet gevonden.")
    if not uitkomst.ok:
        return _toon_formulier(request, db, soort, obj, form, uitkomst.fouten, status=422)
    if obj is None:
        obj = model()
        db.add(obj)
    for naam, waarde in uitkomst.data.items():
        setattr(obj, naam, waarde)
    db.commit()
    return RedirectResponse(f"/voertuigen/{soort}/{obj.id}?opgeslagen=1", status_code=303)


@router.post("/{soort}/nieuw")
async def maak(soort: str, request: Request, db: Session = Depends(get_db), gebruiker=Depends(planner_of_admin)):
    return await _opslaan(soort, request, db)


@router.get("/combinatie")
def combinatie_pagina(request: Request, db: Session = Depends(get_db), gebruiker=Depends(planner_of_admin)):
    return combinatie(request, db)


@router.get("/export/{soort}.csv")
def exporteer(soort: str, db: Session = Depends(get_db), gebruiker=Depends(planner_of_admin)):
    model, velden, _ = _soort(soort)
    buf = io.StringIO()
    w = csv.writer(buf, delimiter=";")
    w.writerow([v.naam for v in velden] + ["gearchiveerd"])
    for obj in db.scalars(select(model).order_by(model.id)):
        rij = []
        for v in velden:
            waarde = getattr(obj, v.naam)
            if waarde is None:
                rij.append("")
            elif v.soort == "bool":
                rij.append("ja" if waarde else "nee")
            elif v.soort == "tijd":
                rij.append(waarde.strftime("%H:%M"))
            else:
                rij.append(str(waarde))
        rij.append("ja" if obj.gearchiveerd else "nee")
        w.writerow(rij)
    return Response(buf.getvalue().encode("utf-8-sig"), media_type="text/csv; charset=utf-8",
                    headers={"Content-Disposition": f'attachment; filename="{soort}.csv"'})


@router.get("/import")
def import_pagina(request: Request, gebruiker=Depends(planner_of_admin)):
    return templates.TemplateResponse(request, "voertuigen/import.html", {"resultaat": None})


def importeer_csv(db: Session, soort: str, tekst: str) -> dict:
    """Lees een CSV. Goede rijen worden opgeslagen, rijen met fouten worden geweigerd met een melding."""
    model, velden, _ = _soort(soort)
    tekst = tekst.lstrip("﻿")
    eerste = tekst.splitlines()[0] if tekst.strip() else ""
    scheiding = ";" if eerste.count(";") >= eerste.count(",") else ","
    lezer = csv.DictReader(io.StringIO(tekst), delimiter=scheiding)
    goed, fouten = 0, []
    if not lezer.fieldnames:
        return {"goed": 0, "fouten": ["Het bestand is leeg."]}
    sleutel = "kenteken" if soort == "trekker" else "nummer"
    if sleutel not in lezer.fieldnames:
        return {"goed": 0, "fouten": [f"Kolom '{sleutel}' ontbreekt in de eerste regel."]}
    for nr, rij in enumerate(lezer, start=2):
        invoer = {}
        for v in velden:
            w = (rij.get(v.naam) or "").strip()
            if v.soort == "bool":
                if w.lower() in ("ja", "1", "true", "on"):
                    invoer[v.naam] = "on"
            else:
                invoer[v.naam] = w
        bestaand = db.scalar(select(model).where(getattr(model, sleutel) == invoer.get(sleutel, "").upper()))
        uitkomst = controleer_voertuig(db, soort, invoer, bestaand.id if bestaand else None)
        if not uitkomst.ok:
            labels = {v.naam: v.label for v in velden}
            fouten.append(f"Rij {nr}: " + "; ".join(f"{labels.get(n, n)}: {t}" for n, t in uitkomst.fouten.items()))
            continue
        obj = bestaand or model()
        if bestaand is None:
            db.add(obj)
        for naam, waarde in uitkomst.data.items():
            setattr(obj, naam, waarde)
        db.flush()
        goed += 1
    db.commit()
    return {"goed": goed, "fouten": fouten}


@router.post("/import")
async def importeer(request: Request, db: Session = Depends(get_db), gebruiker=Depends(planner_of_admin)):
    form = await request.form()
    soort = str(form.get("soort", ""))
    _soort(soort)
    bestand = form.get("bestand")
    if bestand is None or not hasattr(bestand, "read"):
        resultaat = {"goed": 0, "fouten": ["Kies een CSV-bestand."]}
    else:
        inhoud = await bestand.read()
        try:
            resultaat = importeer_csv(db, soort, inhoud.decode("utf-8"))
        except UnicodeDecodeError:
            resultaat = {"goed": 0, "fouten": ["Het bestand is geen UTF-8 tekst. Sla het op als 'CSV UTF-8'."]}
    return templates.TemplateResponse(request, "voertuigen/import.html", {"resultaat": resultaat, "soort": soort})


@router.get("/{soort}/{obj_id}")
def bewerk(soort: str, obj_id: int, request: Request, db: Session = Depends(get_db),
           gebruiker=Depends(planner_of_admin)):
    model, velden, _ = _soort(soort)
    obj = db.get(model, obj_id)
    if not obj:
        raise HTTPException(404, "Niet gevonden.")
    return _toon_formulier(request, db, soort, obj, _waarden(obj, velden), {})


@router.post("/{soort}/{obj_id}")
async def wijzig(soort: str, obj_id: int, request: Request, db: Session = Depends(get_db),
                 gebruiker=Depends(planner_of_admin)):
    return await _opslaan(soort, request, db, obj_id)


@router.post("/{soort}/{obj_id}/archiveren")
def archiveer(soort: str, obj_id: int, db: Session = Depends(get_db), gebruiker=Depends(planner_of_admin)):
    model, _, _ = _soort(soort)
    obj = db.get(model, obj_id)
    if not obj:
        raise HTTPException(404, "Niet gevonden.")
    obj.gearchiveerd = not obj.gearchiveerd
    db.commit()
    return RedirectResponse(f"/voertuigen/{soort}/{obj_id}", status_code=303)


@router.post("/{soort}/{obj_id}/voorkeur")
async def voorkeur_toevoegen(soort: str, obj_id: int, request: Request, db: Session = Depends(get_db),
                             gebruiker=Depends(planner_of_admin)):
    model, _, _ = _soort(soort)
    if not db.get(model, obj_id):
        raise HTTPException(404, "Niet gevonden.")
    form = dict(await request.form())
    uitkomst = controleer([
        Veld("soort", "Soort", "keuze", verplicht=True, keuzes=k.VOORKEUR_SOORTEN),
        Veld("waarde", "Waarde", verplicht=True),
        Veld("gewicht", "Gewicht", "getal", verplicht=True, min=0, max=10),
    ], form)
    if not uitkomst.ok:
        raise HTTPException(422, "Voorkeur niet opgeslagen: " + "; ".join(uitkomst.fouten.values())
                            + " (gewicht moet 0 tot 10 zijn).")
    db.add(m.VoertuigVoorkeur(**uitkomst.data, **{f"{soort}_id": obj_id}))
    db.commit()
    return RedirectResponse(f"/voertuigen/{soort}/{obj_id}#voorkeuren", status_code=303)


@router.post("/voorkeur/{vid}/verwijderen")
def voorkeur_verwijderen(vid: int, db: Session = Depends(get_db), gebruiker=Depends(planner_of_admin)):
    v = db.get(m.VoertuigVoorkeur, vid)
    if not v:
        raise HTTPException(404, "Niet gevonden.")
    terug = f"/voertuigen/trekker/{v.trekker_id}" if v.trekker_id else f"/voertuigen/chassis/{v.chassis_id}"
    db.delete(v)
    db.commit()
    return RedirectResponse(terug + "#voorkeuren", status_code=303)


# ------------------------------------------------------------------ combinatiepagina


def _int(waarde, standaard=None):
    try:
        return int(str(waarde).replace(".", "").strip())
    except (TypeError, ValueError):
        return standaard


def combinatie(request: Request, db: Session):
    q = request.query_params
    vandaag = _vandaag()
    boek = RegelBoek.laad(db)
    trekkers = db.scalars(select(m.Trekker).where(m.Trekker.gearchiveerd.is_(False))
                          .order_by(m.Trekker.intern_nummer)).all()
    chassis_lijst = db.scalars(select(m.Chassis).where(m.Chassis.gearchiveerd.is_(False))
                               .order_by(m.Chassis.nummer)).all()
    chauffeurs = db.scalars(select(m.Chauffeur).where(m.Chauffeur.actief.is_(True))
                            .order_by(m.Chauffeur.pseudoniem)).all()
    keuze = {
        "trekker_id": _int(q.get("trekker_id")), "chassis_id": _int(q.get("chassis_id")),
        "chauffeur_id": _int(q.get("chauffeur_id")), "route": q.get("route", "NL-intermodaal"),
        "containers": [],
    }
    fouten = []
    containers: list[ContainerInvoer] = []
    for i in (1, 2):
        maat = q.get(f"c{i}_maat", "")
        if not maat:
            keuze["containers"].append({})
            continue
        type_ = q.get(f"c{i}_type", "DC")
        gewicht = _int(q.get(f"c{i}_gewicht"))
        soort_gewicht = q.get(f"c{i}_soort", "vgm")
        tarra = _int(q.get(f"c{i}_tarra"))
        tarra_aanname = False
        if tarra is None:
            code = {"20": "container.tarra.20", "45": "container.tarra.45"}.get(
                maat, "container.tarra.40hc" if type_ in ("HC", "reefer") else "container.tarra.40")
            tarra = boek.waarde(code, vandaag)
            tarra_aanname = True
        keuze["containers"].append({"maat": maat, "type": type_, "gewicht": q.get(f"c{i}_gewicht", ""),
                                    "soort": soort_gewicht, "tarra": q.get(f"c{i}_tarra", ""),
                                    "imo": q.get(f"c{i}_imo", "")})
        if gewicht is None:
            fouten.append(f"Container {i}: vul het gewicht in (hele kg).")
            continue
        vgm = gewicht if soort_gewicht == "vgm" else gewicht + (tarra or 0)
        containers.append(ContainerInvoer(maat, type_, vgm, tarra, tarra_aanname, q.get(f"c{i}_imo") or None,
                                          f"container {i}"))
    resultaat = None
    trekker = db.get(m.Trekker, keuze["trekker_id"]) if keuze["trekker_id"] else None
    chassis = db.get(m.Chassis, keuze["chassis_id"]) if keuze["chassis_id"] else None
    chauffeur = db.get(m.Chauffeur, keuze["chauffeur_id"]) if keuze["chauffeur_id"] else None
    if trekker and chassis and not fouten:
        ti, ci = trekker_uit(trekker), chassis_uit(chassis)
        codes = [g[0] for g in GRENZEN]
        if keuze["route"] == "BE":
            codes.append("gewicht.BE")
        gewicht = bereken_gewicht(boek, vandaag, ti, ci, containers, codes)
        uitslagen = toets_combinatie(boek, vandaag, ti, ci, containers, keuze["route"], chauffeur)
        resultaat = {
            "gewicht": gewicht, "uitslagen": uitslagen, "ergste": ergste(uitslagen),
            "grens_code": grens_code_voor(keuze["route"], trekker.aandrijving),
            "aslast": aslast_grens(boek, vandaag, trekker.aandrijving, chassis.assen),
            "geschikt": geschikt_voor(ti, ci), "trekker": trekker, "chassis": chassis,
        }
    ctx = {"trekkers": trekkers, "chassis_lijst": chassis_lijst, "chauffeurs": chauffeurs, "keuze": keuze,
           "resultaat": resultaat, "fouten": fouten, "maten": k.CONTAINER_MATEN, "types": k.CONTAINER_TYPES}
    sjabloon = "voertuigen/_combinatie_resultaat.html" if request.headers.get("HX-Request") else \
        "voertuigen/combinatie.html"
    return templates.TemplateResponse(request, sjabloon, ctx)
