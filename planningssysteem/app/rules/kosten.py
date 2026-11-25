"""Kosten: demurrage/detention (regel 12), tol (regel 20) en kosten per rit.

Alle bedragen in hele centen. Tarieven komen uit de database (regels als data).
Kostprijzen zijn een schatting (prijspeil 2021) met een instelbare index.
"""

from dataclasses import dataclass, field
from datetime import date

from app.rules.basis import RegelBoek


@dataclass
class DDBand:
    vrije_dagen: int
    dag_van: int
    dag_tot: int | None
    bedrag_per_dag_cent: int


def dd_bedrag_per_dag(banden: list[DDBand], dagnummer: int) -> int:
    """Wat kost dag nummer N (dag 1 = eerste dag)? 0 als het een vrije dag is."""
    for b in banden:
        if dagnummer <= b.vrije_dagen:
            return 0
        if b.dag_van <= dagnummer and (b.dag_tot is None or dagnummer <= b.dag_tot):
            return b.bedrag_per_dag_cent
    return 0


def dd_kosten(banden: list[DDBand], begin: date, einde: date) -> tuple[int, int]:
    """Totale kosten en aantal betaalde dagen van 'begin' (dag 1) tot en met 'einde'."""
    totaal, betaald = 0, 0
    dagen = (einde - begin).days + 1
    for n in range(1, dagen + 1):
        bedrag = dd_bedrag_per_dag(banden, n)
        if bedrag:
            totaal += bedrag
            betaald += 1
    return totaal, betaald


def banden_uit(tarieven) -> list[DDBand]:
    return [DDBand(t.vrije_dagen, t.dag_van, t.dag_tot, t.bedrag_per_dag_cent) for t in tarieven]


@dataclass
class RitKosten:
    rijkosten_cent: int = 0
    wachtkosten_cent: int = 0
    tol_cent: int = 0
    demurrage_cent: int = 0
    slot_kosten_cent: int = 0
    uitleg: list[str] = field(default_factory=list)

    @property
    def totaal_cent(self) -> int:
        return self.rijkosten_cent + self.wachtkosten_cent + self.tol_cent + self.demurrage_cent + self.slot_kosten_cent


def tol_tarief(boek: RegelBoek, d: date, land: str, zero_emissie: bool) -> int | None:
    """Tol in tienden van een cent per km."""
    if land == "NL":
        return boek.waarde("tol.NL.zero" if zero_emissie else "tol.NL.euro6_co2_1", d)
    return boek.waarde(f"tol.{land}", d)


def bereken_rit_kosten(boek: RegelBoek, d: date, km: int, rij_min: int, werk_min: int, km_buitenland: int = 0,
                       land_buitenland: str | None = None, zero_emissie: bool = False,
                       eigen_km_cent: int | None = None, eigen_uur_cent: int | None = None,
                       demurrage_cent: int = 0, slot_kosten_cent: int = 0) -> RitKosten:
    k = RitKosten(demurrage_cent=demurrage_cent, slot_kosten_cent=slot_kosten_cent)
    index = boek.waarde("kostprijs.index", d, 100)
    per_km = eigen_km_cent if eigen_km_cent is not None else boek.waarde("kostprijs.km", d, 0) * index // 100
    per_uur = eigen_uur_cent if eigen_uur_cent is not None else boek.waarde("kostprijs.uur", d, 0) * index // 100
    per_uur_wachten = boek.waarde("kostprijs.wachten.uur", d, 0) * index // 100
    k.rijkosten_cent = km * per_km + rij_min * per_uur // 60
    k.wachtkosten_cent = werk_min * per_uur_wachten // 60
    km_nl = max(0, km - km_buitenland)
    tol_nl = tol_tarief(boek, d, "NL", zero_emissie) or 0
    k.tol_cent = km_nl * tol_nl // 10
    if km_buitenland and land_buitenland:
        tarief = tol_tarief(boek, d, land_buitenland, zero_emissie)
        if tarief is None:
            k.uitleg.append(f"Tol {land_buitenland} onbekend.")
        else:
            k.tol_cent += km_buitenland * tarief // 10
    k.uitleg.append("Kostprijs is een schatting (prijspeil 2021, met index). Tol: aangenomen dat de heffing "
                    "voor alle km geldt.")
    return k
