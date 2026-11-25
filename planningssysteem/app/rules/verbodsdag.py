"""Regel 17: verbodsdagen (bijvoorbeeld Duitsland op zondag) en regel 21 (Duitsland intermodaal).

Duitsland: op zondagen en feestdagen van 00:00 tot 22:00 geen vrachtwagens boven 7,5 t.
Uitzondering voor gecombineerd vervoer: haven-weg tot 150 km, spoor-weg tot 200 km (Bevestigd).
Feestdagen per deelstaat zijn Open: we kennen alleen de landelijke feestdagen.
Frankrijk en Luxemburg: niet uitgezocht, dus niet gebruiken.
"""

from datetime import date, datetime, time, timedelta

from app.ports.clock import NL
from app.rules.basis import HARD, OK, WAARSCHUWING, RegelBoek, Uitslag


def is_verboden_dag(d: date, feestdagen: set[date]) -> bool:
    return d.weekday() == 6 or d in feestdagen


def regel_verbodsdag(boek: RegelBoek, land: str, start: datetime, eind: datetime, massa_kg: int,
                     feestdagen: set[date], gecombineerd_vervoer: bool = False, km_weg: int | None = None,
                     soort_uitzondering: str = "haven") -> Uitslag | None:
    if land != "DE":
        return None
    d = start.astimezone(NL).date()
    rw_van = boek.get("verbod.DE.van", d)
    rw_tot = boek.get("verbod.DE.tot", d)
    massa_grens = boek.waarde("verbod.DE.massa", d, 7500)
    if rw_van is None or rw_tot is None:
        return Uitslag(17, "Verbodsdag", WAARSCHUWING, "Verbodsdag-regel voor Duitsland ontbreekt.", status="open")
    bron, status = rw_van.bron, rw_van.status
    if massa_kg <= massa_grens:
        return Uitslag(17, "Verbodsdag", OK, "Voertuig is niet zwaarder dan 7,5 t.", bron, status)
    # Loop over elke dag die de rit raakt
    dag = d
    laatste = eind.astimezone(NL).date()
    while dag <= laatste:
        if is_verboden_dag(dag, feestdagen):
            blok_van = datetime.combine(dag, time()).replace(tzinfo=NL) + timedelta(minutes=rw_van.waarde)
            blok_tot = datetime.combine(dag, time()).replace(tzinfo=NL) + timedelta(minutes=rw_tot.waarde)
            if start < blok_tot and eind > blok_van:
                if gecombineerd_vervoer and km_weg is not None:
                    code = "verbod.DE.uitz.spoor" if soort_uitzondering == "spoor" else "verbod.DE.uitz.haven"
                    max_km = boek.waarde(code, dag)
                    if max_km is not None and km_weg <= max_km:
                        return Uitslag(17, "Verbodsdag", OK, f"Uitzondering gecombineerd vervoer: wegdeel {km_weg} km "
                                       f"(max {max_km} km).", bron, status)
                naam = "zondag" if dag.weekday() == 6 else "feestdag"
                return Uitslag(17, "Verbodsdag", HARD, f"Niet toegestaan: rijverbod in Duitsland op {naam} "
                               f"{dag:%d-%m-%Y} tussen 00:00 en 22:00 voor voertuigen boven 7,5 t.", bron, status)
        dag += timedelta(days=1)
    return Uitslag(17, "Verbodsdag", OK, "Geen verbodsdag tijdens de rit.", bron, status)


def regel_de_intermodaal(boek: RegelBoek, d: date, route: str, km_weg: int | None) -> Uitslag | None:
    if route != "DE-intermodaal":
        return None
    rw = boek.get("de.intermodaal.wegdeel", d)
    if rw is None or km_weg is None:
        return Uitslag(21, "Duitsland intermodaal", WAARSCHUWING, "Wegdeel in Duitsland onbekend.", status="open")
    if km_weg > rw.waarde:
        return Uitslag(21, "Duitsland intermodaal", WAARSCHUWING, f"Wegdeel {km_weg} km is meer dan {rw.waarde} km. "
                       "Het 44 t-regime geldt dan misschien niet (Open). Controleer het.", rw.bron, rw.status)
    return Uitslag(21, "Duitsland intermodaal", OK, f"Wegdeel {km_weg} km (max {rw.waarde} km).", rw.bron, rw.status)
