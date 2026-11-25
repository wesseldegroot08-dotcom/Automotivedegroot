"""Factuurconcept per order op basis van tariefregels. Alleen een concept: geen koppeling met boekhouding.

Regels:
- Basisprijs uit de best passende tariefregel (klant, ordertype en containermaat; meest specifieke wint).
- Toeslag ADR (als een container een IMO-klasse heeft) en reefer.
- Handelingen (kiepen, flexitank, ...) per uur.
- Wachttijd: gemeten tijd op de stops boven de vrije tijd, per begonnen half uur. Zonder meting: geen bedrag.
- BTW rekenen we niet uit: dat hangt af van de soort vervoer (Open, controleer bij je boekhouder).
"""

from dataclasses import dataclass, field
from datetime import date

from app import models as m


@dataclass
class Regel:
    omschrijving: str
    bedrag_cent: int


@dataclass
class FactuurConcept:
    order: m.Order
    regels: list[Regel] = field(default_factory=list)
    opmerkingen: list[str] = field(default_factory=list)
    tarief: m.Tariefregel | None = None

    @property
    def totaal_cent(self) -> int:
        return sum(r.bedrag_cent for r in self.regels)


def kies_tarief(tarieven: list[m.Tariefregel], order: m.Order, maat: str, d: date) -> m.Tariefregel | None:
    beste, score = None, -1
    for t in tarieven:
        if t.geldig_van > d or (t.geldig_tot and t.geldig_tot < d):
            continue
        if (t.klant_id and t.klant_id != order.klant_id) or (t.order_type and t.order_type != order.type) or (
                t.container_maat and t.container_maat != maat):
            continue
        s = (4 if t.klant_id else 0) + (2 if t.order_type else 0) + (1 if t.container_maat else 0)
        if s > score:
            beste, score = t, s
    return beste


def maak_concept(order: m.Order, ritten: list[m.Rit], tarieven: list[m.Tariefregel], d: date) -> FactuurConcept:
    f = FactuurConcept(order)
    maten = [c.maat for c in order.containers] or ["40"]
    grootste = max(maten, key=lambda x: int(x) if x.isdigit() else 0)
    t = kies_tarief(tarieven, order, grootste, d)
    f.tarief = t
    if not t:
        f.opmerkingen.append(f"Geen tariefregel voor {order.type} {grootste}ft. Vul een tarief in bij Stamdata.")
        return f
    f.regels.append(Regel(f"Transport {order.type} ({', '.join(c.nummer for c in order.containers) or '-'})",
                          t.basisprijs_cent))
    if any(c.imo_klasse for c in order.containers) and t.adr_toeslag_cent:
        f.regels.append(Regel("Toeslag ADR", t.adr_toeslag_cent))
    if any(c.type == "reefer" for c in order.containers) and t.reefer_toeslag_cent:
        f.regels.append(Regel("Toeslag reefer", t.reefer_toeslag_cent))
    for h in order.handelingen:
        bedrag = h.duur_min * t.handeling_per_uur_cent // 60
        f.regels.append(Regel(f"{h.soort} ({h.duur_min} min)" + (" (duur is aanname)" if h.duur_is_aanname else ""),
                              bedrag))
    wacht = [s.wachttijd_min for r in ritten for s in r.stops if s.wachttijd_min is not None and
             s.locatie.type == "klant"]
    if wacht:
        totaal = sum(wacht)
        boven = max(0, totaal - t.wachttijd_vrij_min)
        halve_uren = -(-boven // 30)
        if halve_uren:
            f.regels.append(Regel(f"Wachttijd bij de klant: {totaal} min, {t.wachttijd_vrij_min} min vrij, "
                                  f"{halve_uren} x half uur", halve_uren * t.wachttijd_per_half_uur_cent))
    else:
        f.opmerkingen.append("Nog geen gemeten wachttijd bij de klant (chauffeurspagina).")
    if t.status != "bevestigd":
        f.opmerkingen.append(f"Tarief heeft status '{t.status}' (bron: {t.bron}). Controleer het.")
    f.opmerkingen.append("BTW niet berekend (Open).")
    return f
