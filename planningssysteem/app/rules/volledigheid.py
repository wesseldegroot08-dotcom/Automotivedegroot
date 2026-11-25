"""Wat ontbreekt er nog per voertuig? Hoe vollediger, hoe zekerder het systeem rekent."""

from datetime import date


def _check(lijst, voorwaarde, tekst, belangrijk=True):
    if voorwaarde:
        lijst.append((tekst, belangrijk))


def ontbreekt_trekker(t, vandaag: date) -> list[tuple[str, bool]]:
    """Geeft een lijst (tekst, belangrijk). 'Belangrijk' = nodig voor gewicht of veiligheid."""
    uit: list[tuple[str, bool]] = []
    _check(uit, t.tarra_kg is None, "Tarra (leeggewicht) is onbekend. Gewicht kan niet berekend worden.")
    _check(uit, t.tarra_kg is not None and t.tarra_bron == "aanname",
           "Tarra is een aanname. Weeg de trekker of neem 'massa rijklaar' van het kentekenbewijs.")
    _check(uit, t.toegestane_massa_kg is None, "Technisch toegestane massa is onbekend.")
    _check(uit, t.max_aandrijfas_kg is None, "Max last op de aandrijfas is onbekend (nodig voor de aslast).")
    _check(uit, t.max_koppelplaat_kg is None, "Max koppelplaatlast is onbekend.", False)
    _check(uit, t.co2_klasse is None, "CO2-klasse onbekend (nodig voor de tol).", False)
    _check(uit, t.euro_klasse is None, "Euro-klasse onbekend.", False)
    _check(uit, t.apk_datum is None, "APK-datum onbekend.")
    _check(uit, t.apk_datum is not None and t.apk_datum < vandaag, "APK is verlopen.")
    _check(uit, t.tachograaf_ijking is None, "Datum tachograaf-ijking onbekend.", False)
    _check(uit, t.tachograaf_ijking is not None and t.tachograaf_ijking < vandaag, "Tachograaf-ijking is verlopen.")
    _check(uit, t.kosten_per_km_cent is None and t.kosten_per_uur_cent is None,
           "Eigen kosten per km/uur onbekend. Het systeem gebruikt de algemene kostprijs (schatting).", False)
    _check(uit, t.lzv_geschikt and (t.lzv_ontheffing_tot is None or t.lzv_ontheffing_tot < vandaag),
           "LZV-geschikt, maar de ontheffing ontbreekt of is verlopen.")
    return uit


def ontbreekt_chassis(c, vandaag: date) -> list[tuple[str, bool]]:
    uit: list[tuple[str, bool]] = []
    _check(uit, c.tarra_kg is None, "Tarra (leeggewicht) is onbekend. Gewicht kan niet berekend worden.")
    _check(uit, c.tarra_kg is not None and c.tarra_bron == "aanname", "Tarra is een aanname. Weeg de trailer.")
    _check(uit, c.max_kingpin_kg is None, "Max last op de koppelpen (kingpin) is onbekend.", False)
    _check(uit, c.max_asgroep_kg is None, "Max last op de as-groep is onbekend.", False)
    _check(uit, c.kingpinhoogte_mm is None, "Kingpinhoogte onbekend (nodig voor de hoogtecontrole).", False)
    _check(uit, c.lengte_in_mm is None, "Lengte onbekend.", False)
    _check(uit, not (c.twistlock_20 or c.twistlock_40 or c.twistlock_45), "Geen twistlock-posities ingevuld.")
    _check(uit, c.keuring_datum is None, "Keuringsdatum onbekend.")
    _check(uit, c.keuring_datum is not None and c.keuring_datum < vandaag, "Keuring is verlopen.")
    return uit


def volledigheid_procent(ontbreekt: list[tuple[str, bool]], totaal_punten: int = 12) -> int:
    return max(0, round(100 * (totaal_punten - len(ontbreekt)) / totaal_punten))
