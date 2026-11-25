"""Demodata. Alles is verzonnen.

Gebruik:
    python -m app.seed            -> vult de database (alleen als hij leeg is)
    python -m app.seed --reset    -> maakt alles leeg en vult opnieuw

De bedrijfsnaam in de app komt uit BEDRIJFSNAAM in .env. Alle data hieronder is verzonnen (demo).
Chauffeurs hebben pseudoniemen. Terminals zijn echt (die zijn openbaar), maar de
coördinaten zijn benaderd (aanname).

Er zitten expres een paar valkuilen in, zodat je de regels in actie ziet:
- een container die te zwaar is voor 42 ton (order DEMO-1003),
- een order met LFD morgen (DEMO-1005),
- twee tank/ADR-ritten tegelijk, maar maar één chauffeur met ADR-tank (DEMO-1010 en 1011),
- een slot dat niet past bij het tijdvenster van de klant (DEMO-1007),
- een chauffeur die bijna aan zijn weekrijtijd zit (Dirk),
- een chauffeur zonder geldige ECT-veiligheidstest (Gijs).
"""

import argparse
from datetime import date, time, timedelta

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app import models as m
from app.auth import hash_wachtwoord
from app.config import instellingen
from app.db import Base, SessionLocal
from app.ports.clock import morgen_nl, nl_tijd, vandaag_nl
from app.rules.iso6346 import bereken_controlecijfer

BRON_OPDRACHT = "Opdracht testversie / docs/onderzoek.md"
BRON_DEMO = "Verzonnen demodata"


def containernummer(eigenaar: str, serie: int) -> str:
    basis = f"{eigenaar}U{serie:06d}"
    return basis + str(bereken_controlecijfer(basis))


def _regels(db: Session) -> None:
    """Alle startwaarden uit de opdracht, met status. Regels zijn data, geen code."""
    v = date(2026, 1, 1)
    R = []  # noqa: N806

    def r(code, cat, oms, waarde, eenheid, status, bron=BRON_OPDRACHT, land=None, van=v, tot=None,
          in_gebruik=True, opm=None):
        R.append(m.Regel(code=code, categorie=cat, omschrijving=oms, waarde=waarde, eenheid=eenheid,
                         status=status, bron=bron, land=land, geldig_van=van, geldig_tot=tot,
                         in_gebruik=in_gebruik, opmerking=opm))

    # Gewicht (max toegestaan gewicht van de hele combinatie)
    r("gewicht.NL", "gewicht", "Nederland algemeen, trekker met oplegger", 50000, "kg", "bevestigd", land="NL")
    r("gewicht.intermodaal.3as", "gewicht", "Intermodaal met 3-assige trekker (buitenland/EU-regel)", 44000, "kg",
      "bevestigd", opm="Details controleren")
    r("gewicht.intermodaal.2as", "gewicht", "Intermodaal met 2-assige trekker", 42000, "kg", "bevestigd",
      opm="Details controleren")
    r("gewicht.DE", "gewicht", "Duitsland normaal (5 of meer assen)", 40000, "kg", "bevestigd", land="DE")
    r("gewicht.BE", "gewicht", "België (Vlaanderen)", 44000, "kg", "open", land="BE",
      opm="Bronnen spreken elkaar tegen. Waarde is instelbaar.")
    r("gewicht.FR", "gewicht", "Frankrijk", None, "kg", "open", land="FR", in_gebruik=False,
      opm="Niet uitgezocht. Niet gebruiken.")
    r("gewicht.LU", "gewicht", "Luxemburg", None, "kg", "open", land="LU", in_gebruik=False,
      opm="Niet uitgezocht. Niet gebruiken.")
    # Aslasten (waarschuwing)
    r("aslast.enkel", "aslast", "Enkele as", 10000, "kg", "schatting", opm="Bronnen spreken elkaar tegen")
    r("aslast.aangedreven", "aslast", "Aangedreven as", 11500, "kg", "schatting")
    r("aslast.tandem", "aslast", "Tandem (asafstand 1,30 tot 1,80 m)", 18000, "kg", "schatting")
    r("aslast.tridem", "aslast", "Tridem (3 assen)", 24000, "kg", "schatting",
      opm="Soms 27.000 kg bij aangedreven, zie aslast.tridem.hoog")
    r("aslast.tridem.hoog", "aslast", "Tridem, hogere waarde volgens sommige bronnen", 27000, "kg", "open",
      in_gebruik=False)
    r("aslast.aandrijfas.min", "aslast", "Aandrijfas draagt minimaal dit deel van het totaal", 20, "procent", "open",
      opm="1/5 van het totaal. Details Open.")
    # Maten
    r("maat.hoogte", "maat", "Maximale hoogte", 4000, "mm", "bevestigd", land="NL")
    r("maat.breedte", "maat", "Maximale breedte", 2550, "mm", "bevestigd", land="NL")
    r("maat.breedte.geconditioneerd", "maat", "Maximale breedte geconditioneerd", 2600, "mm", "bevestigd", land="NL")
    r("maat.lengte.trekker_oplegger", "maat", "Lengte trekker met oplegger", 16500, "mm", "bevestigd", land="NL")
    r("lzv.lengte", "maat", "LZV maximale lengte", 25250, "mm", "bevestigd", land="NL")
    r("lzv.massa", "gewicht", "LZV maximale massa (ontheffing, CCV, alleen aangewezen routes)", 60000, "kg",
      "bevestigd", land="NL")
    # VGM (alleen informatie)
    r("vgm.tolerantie.onder10t", "info", "VGM-tolerantie onder 10 t (zeevaartregel, GEEN toestemming op de weg)",
      500, "kg", "bevestigd")
    r("vgm.tolerantie.procent", "info", "VGM-tolerantie vanaf 10 t (zeevaartregel, GEEN toestemming op de weg)",
      5, "procent", "bevestigd")
    # Rij- en rusttijden (EU 561/2006)
    b561 = "EU-verordening 561/2006"
    r("rijtijd.dag", "rijtijd", "Rijtijd per dag", 540, "minuten", "bevestigd", bron=b561)
    r("rijtijd.dag.verlengd", "rijtijd", "Verlengde rijtijd per dag (max 2x per week)", 600, "minuten",
      "bevestigd", bron=b561)
    r("rijtijd.verlengd.per_week", "rijtijd", "Aantal keer verlengde rijtijd per week", 2, "keer", "bevestigd",
      bron=b561)
    r("rijtijd.week", "rijtijd", "Rijtijd per week", 3360, "minuten", "bevestigd", bron=b561)
    r("rijtijd.twee_weken", "rijtijd", "Rijtijd per twee weken", 5400, "minuten", "bevestigd", bron=b561)
    r("pauze.na_rijden", "rijtijd", "Pauze verplicht na zoveel rijden", 270, "minuten", "bevestigd", bron=b561)
    r("pauze.duur", "rijtijd", "Duur van de pauze", 45, "minuten", "bevestigd", bron=b561)
    r("pauze.deel1", "rijtijd", "Gesplitste pauze: eerste deel minimaal", 15, "minuten", "bevestigd", bron=b561)
    r("pauze.deel2", "rijtijd", "Gesplitste pauze: tweede deel minimaal", 30, "minuten", "bevestigd", bron=b561)
    r("rust.dag", "rijtijd", "Dagelijkse rust", 660, "minuten", "bevestigd", bron=b561)
    r("rust.dag.verkort", "rijtijd", "Verkorte dagelijkse rust", 540, "minuten", "bevestigd", bron=b561)
    r("dienst.max", "rijtijd", "Maximale dienst bij 11 uur rust (afgeleid)", 780, "minuten", "schatting",
      bron=b561 + " (afgeleid)")
    r("wachten.is_werktijd", "rijtijd", "Wachten, laden en lossen tellen als werktijd (1 = ja)", 1, "ja/nee",
      "schatting")
    # Nederlandse arbeidstijd en cao
    r("arbeid.pauze.6_9", "arbeidstijd", "Pauze bij 6 tot 9 uur werk", 30, "minuten", "bevestigd",
      bron="Arbeidstijdenbesluit vervoer")
    r("arbeid.pauze.9plus", "arbeidstijd", "Pauze bij meer dan 9 uur werk", 45, "minuten", "bevestigd",
      bron="Arbeidstijdenbesluit vervoer")
    r("arbeid.max_zonder_pauze", "arbeidstijd", "Nooit langer werken zonder pauze dan", 360, "minuten",
      "bevestigd", bron="Arbeidstijdenbesluit vervoer")
    r("cao.overwerk.toeslag", "arbeidstijd", "Overwerktoeslag boven contracturen", 30, "procent", "bevestigd",
      bron="Cao beroepsgoederenvervoer")
    r("cao.nacht.van", "arbeidstijd", "Nachttoeslag vanaf (minuten na middernacht, 21:00)", 1260, "minuten",
      "bevestigd", bron="Cao beroepsgoederenvervoer")
    r("cao.nacht.tot", "arbeidstijd", "Nachttoeslag tot (minuten na middernacht, 05:00)", 300, "minuten",
      "bevestigd", bron="Cao beroepsgoederenvervoer")
    # Verbodsdagen
    r("verbod.DE.van", "verbodsdag", "Duitsland zon- en feestdagen: rijverbod vanaf (minuten na 00:00)", 0,
      "minuten", "bevestigd", land="DE")
    r("verbod.DE.tot", "verbodsdag", "Duitsland zon- en feestdagen: rijverbod tot (22:00)", 1320, "minuten",
      "bevestigd", land="DE")
    r("verbod.DE.massa", "verbodsdag", "Rijverbod geldt boven deze massa", 7500, "kg", "bevestigd", land="DE")
    r("verbod.DE.uitz.spoor", "verbodsdag", "Uitzondering gecombineerd vervoer spoor-weg tot", 200, "km",
      "bevestigd", land="DE")
    r("verbod.DE.uitz.haven", "verbodsdag", "Uitzondering gecombineerd vervoer haven-weg tot", 150, "km",
      "bevestigd", land="DE")
    r("de.intermodaal.wegdeel", "gewicht", "Duitsland intermodaal: wegdeel maximaal (Rotterdam-Duisburg ca. 220 km)",
      150, "km", "open", land="DE")
    # Tol (0,1 ct/km = tiende cent per km)
    r("tol.NL.euro6_co2_1", "tol", "NL vrachtwagenheffing >32 t, Euro 6, CO2-klasse 1", 201, "0,1 ct/km",
      "bevestigd", land="NL", van=date(2026, 7, 1), tot=date(2026, 8, 31))
    r("tol.NL.euro6_co2_1", "tol", "NL vrachtwagenheffing >32 t, Euro 6, CO2-klasse 1", 156, "0,1 ct/km",
      "bevestigd", land="NL", van=date(2026, 9, 1), tot=date(2026, 12, 31))
    r("tol.NL.euro6_co2_1", "tol", "NL vrachtwagenheffing >32 t, Euro 6, CO2-klasse 1 (voorlopig)", 206,
      "0,1 ct/km", "schatting", land="NL", van=date(2027, 1, 1))
    r("tol.NL.zero", "tol", "NL vrachtwagenheffing zero-emissie", 38, "0,1 ct/km", "bevestigd", land="NL",
      van=date(2026, 7, 1))
    r("tol.DE", "tol", "Duitse Maut (tarief sinds 1 juli 2024, daarna niet gecontroleerd)", 348, "0,1 ct/km",
      "schatting", land="DE", van=date(2024, 7, 1))
    r("tol.BE", "tol", "Vlaamse kilometerheffing (CO2-toeslag onzeker)", 132, "0,1 ct/km", "schatting", land="BE")
    # Kosten
    r("kostprijs.uur", "kosten", "Kostprijs per uur (prijspeil 2021, verouderd)", 6684, "cent", "schatting")
    r("kostprijs.km", "kosten", "Kostprijs per km (prijspeil 2021, verouderd)", 165, "cent", "schatting")
    r("kostprijs.wachten.uur", "kosten", "Kostprijs per uur laden, lossen, wachten (prijspeil 2021)", 4112, "cent",
      "schatting")
    r("kostprijs.index", "kosten", "Index om kostprijs naar nu te corrigeren (100 = geen correctie)", 100,
      "procent", "schatting", opm="Pas aan naar het prijspeil van 2026")
    r("portbase.eenmalig", "kosten", "Portbase HCN Road eenmalig", 24950, "cent", "bevestigd")
    r("portbase.maand", "kosten", "Portbase HCN Road per maand", 1136, "cent", "bevestigd", tot=date(2026, 12, 31))
    r("portbase.maand", "kosten", "Portbase HCN Road per maand", 1170, "cent", "bevestigd", van=date(2027, 1, 1))
    r("portbase.container", "kosten", "Portbase per volle container", 40, "cent", "bevestigd", tot=date(2026, 12, 31))
    r("portbase.container", "kosten", "Portbase per volle container", 41, "cent", "bevestigd", van=date(2027, 1, 1))
    r("klant.wachttijd.vrij", "kosten", "Vrije wachttijd bij de klant (voorbeeld Maersk)", 120, "minuten",
      "schatting", opm="Voorbeeld, niet algemeen")
    r("klant.wachttijd.half_uur", "kosten", "Wachttijd bij de klant per half uur (voorbeeld Maersk)", 4000, "cent",
      "schatting", opm="Voorbeeld, niet algemeen")
    # Containers (richtwaarden)
    r("container.breedte", "container", "Breedte van alle containers", 2438, "mm", "bevestigd")
    r("container.hoogte", "container", "Hoogte standaard container", 2591, "mm", "bevestigd")
    r("container.hoogte.hc", "container", "Hoogte High Cube", 2896, "mm", "bevestigd")
    r("container.mgw", "container", "Bruto maximum (MGW), meestal", 30480, "kg", "bevestigd",
      opm="Nieuwere boxen tot 36.000 kg")
    r("container.tarra.20", "container", "Lege 20ft, richtwaarde", 2250, "kg", "bevestigd",
      opm="Bronnen verschillen 100 tot 250 kg")
    r("container.tarra.40", "container", "Lege 40ft dry, richtwaarde", 3750, "kg", "schatting",
      opm="Niet in de opdracht; aanname")
    r("container.tarra.40hc", "container", "Lege 40ft HC, richtwaarde", 4150, "kg", "bevestigd")
    r("container.tarra.45", "container", "Lege 45ft HC, richtwaarde", 4800, "kg", "schatting",
      opm="Niet in de opdracht; aanname")
    r("trekker.tarra.aanname", "container", "Aanname leeggewicht trekker als niets bekend is", 8000, "kg",
      "schatting", opm="Geen bron. Haal het uit het kentekenbewijs.")
    db.add_all(R)

    feest = [
        (date(2026, 12, 25), "Eerste Kerstdag"), (date(2026, 12, 26), "Tweede Kerstdag"),
        (date(2027, 1, 1), "Nieuwjaarsdag"), (date(2027, 3, 26), "Goede Vrijdag"),
        (date(2027, 3, 29), "Paasmaandag"), (date(2027, 5, 1), "Dag van de Arbeid"),
    ]
    for d, naam in feest:
        db.add(m.Feestdag(land="DE", deelstaat=None, datum=d, naam=naam, rijverbod=True, geldig_van=d,
                          bron="Landelijke Duitse feestdagen (deelstaten Open)", status="schatting"))


def _instellingen(db: Session) -> None:
    rijen = [
        ("noodstop", "uit", "Noodstop. 'aan' = voorstellen en automatische berichten uit. Alleen admin.", "",
         "bevestigd"),
        ("ect_veiligheidstest_ingang", "2026-11-03", "Vanaf deze datum is de ECT-veiligheidstest verplicht.",
         "Bronnen tegenstrijdig: 3 november 2026 of 5 januari 2027", "open"),
        ("no_show_heffing_actief", "nee", "Worden no-showkosten bij ECT al geheven? (nu nog niet)",
         "ECT, stand 23 november 2026", "bevestigd"),
        ("solver_tijdlimiet_sec", "15", "Maximale rekentijd voor een voorstel (seconden).", "", "bevestigd"),
        ("lfd_waarschuwing_dagen", "2", "Waarschuw als de last free day binnen zoveel dagen valt.", "", "bevestigd"),
        ("tijdvenster_klant_hard", "ja", "Is het tijdvenster van de klant een harde regel? (ja/nee)", "", "bevestigd"),
        ("reistijd_correctiefactor_procent", "130",
         "Als een reistijd niet in de tabel staat: afstand in rechte lijn x deze factor.", "Aanname", "schatting"),
        ("gemiddelde_snelheid_kmu", "60", "Gemiddelde snelheid voor de terugval-reistijd (km/u).", "Aanname",
         "schatting"),
    ]
    for sleutel, waarde, oms, bron, status in rijen:
        db.add(m.Instelling(sleutel=sleutel, waarde=waarde, omschrijving=oms, bron=bron, status=status))


def vul(db: Session) -> None:
    db.info["gebruiker"] = "seed"
    morgen = morgen_nl()
    vandaag = vandaag_nl()
    _regels(db)
    _instellingen(db)

    # ---------------------------------------------------------- locaties
    def loc(type_, naam, lat, lon, open_van=(6, 0), open_tot=(22, 0), dagen="123456", laad_los=45, land="NL",
            code=None, adr=False, stroom=False, klant=None, live="live"):
        obj = m.Locatie(type=type_, naam=naam, lat=lat, lon=lon, land=land, open_van=time(*open_van),
                        open_tot=time(*open_tot), open_dagen=dagen, laad_los_min=laad_los, laad_los_is_aanname=True,
                        live_of_drop=live, adr_toegestaan=adr, reefer_stroom=stroom, terminalcode=code)
        if klant:
            obj.klant_id = klant.id
        db.add(obj)
        return obj

    ect_delta = loc("terminal", "ECT Delta", 51.9580, 4.0470, (0, 0), (23, 59), "1234567", 60, code="ECTDELTA",
                    adr=True, stroom=True)
    ect_euromax = loc("terminal", "ECT Euromax", 51.9860, 4.0240, (0, 0), (23, 59), "1234567", 60, code="ECTEUROMAX",
                      adr=True, stroom=True)
    apmt = loc("terminal", "APM Terminals Maasvlakte II", 51.9560, 3.9990, (0, 0), (23, 59), "1234567", 50,
               code="APMTMVII", adr=True, stroom=True)
    rwg = loc("terminal", "RWG", 51.9640, 4.0080, (0, 0), (23, 59), "1234567", 50, code="RWG", adr=True, stroom=True)
    depot_w = loc("depot", "Depot Waalhaven (demo)", 51.8880, 4.4300, (6, 0), (22, 0), "12345", 30)
    depot_m = loc("depot", "Depot Maasvlakte (demo)", 51.9500, 4.0300, (0, 0), (23, 59), "123456", 30)
    depot_b = loc("depot", "Depot Botlek (demo)", 51.8780, 4.2900, (6, 0), (20, 0), "12345", 30)
    standplaats = loc("overig", "Standplaats (demo, Barendrecht)", 51.8520, 4.5280, (0, 0), (23, 59),
                      "1234567", 0)
    db.flush()

    # ---------------------------------------------------------- klanten
    klanten = [m.Klant(naam=n, betaaltermijn_dagen=t, contactpersoon=c, email=e, factuuradres=a) for n, t, c, e, a in [
        ("Alfa Distributie BV (demo)", 30, "Planner Alfa", "orders@alfa.demo", "Demoweg 1, Waalwijk"),
        ("Bravo Chemie BV (demo)", 14, "Planner Bravo", "logistiek@bravo.demo", "Testkade 2, Botlek"),
        ("Charlie Foods BV (demo)", 30, "Planner Charlie", "inkoop@charlie.demo", "Proefstraat 3, Barendrecht"),
        ("Delta Bouwstoffen BV (demo)", 45, "Planner Delta", "orders@delta.demo", "Zandpad 4, Moerdijk"),
        ("Echo Handel GmbH (demo)", 30, "Planner Echo", "dispo@echo.demo", "Beispielstr. 5, Duisburg"),
    ]]
    db.add_all(klanten)
    db.flush()
    alfa, bravo, charlie, delta, echo = klanten
    l_alfa = loc("klant", "Alfa DC Waalwijk (demo)", 51.6890, 5.0700, (7, 0), (17, 0), "12345", 60, klant=alfa)
    l_bravo = loc("klant", "Bravo Chemie Botlek (demo)", 51.8800, 4.3100, (6, 0), (18, 0), "12345", 75, adr=True,
                  klant=bravo)
    l_charlie = loc("klant", "Charlie Koelhuis Barendrecht (demo)", 51.8580, 4.5400, (5, 0), (20, 0), "123456", 60,
                    stroom=True, klant=charlie)
    l_delta = loc("klant", "Delta Bouwstoffen Moerdijk (demo)", 51.6950, 4.6000, (7, 0), (16, 0), "12345", 90,
                  klant=delta)
    l_echo = loc("klant", "Echo Lager Duisburg (demo)", 51.4340, 6.7620, (6, 0), (20, 0), "12345", 60, land="DE",
                 klant=echo)
    db.flush()

    # ---------------------------------------------------------- slotregels per terminal
    ect_bron = "ECT, stand 23 november 2026 (TCMS sinds 5-7 oktober 2026)"
    for t in (ect_delta, ect_euromax):
        db.add(m.TerminalRegel(locatie_id=t.id, slotsysteem="prenotificatie-eta", slotlengte_min=240,
                               tolerantie_min=30, tar_verplicht=True, no_show_kosten_cent=10000,
                               geldig_van=date(2026, 10, 5), geldig_tot=date(2026, 11, 24), bron=ect_bron,
                               status="bevestigd", opmerking="Slots van 4 uur tot 25 november 2026"))
        db.add(m.TerminalRegel(locatie_id=t.id, slotsysteem="prenotificatie-eta", slotlengte_min=120,
                               tolerantie_min=30, tar_verplicht=True, no_show_kosten_cent=10000,
                               no_show_heffing_vanaf=None, geldig_van=date(2026, 11, 25), bron=ect_bron,
                               status="bevestigd",
                               opmerking="No-show en te vroeg: € 100, nog niet geheven. Delta II valt buiten TCMS."))
    db.add(m.TerminalRegel(locatie_id=apmt.id, slotsysteem="slotboeking", slotlengte_min=30, tolerantie_min=45,
                           tar_verplicht=True, geldig_van=date(2026, 1, 1), bron="APMT FAQ (ongedateerd)",
                           status="open", opmerking="Eén TAR per bezoek"))
    db.add(m.TerminalRegel(locatie_id=rwg.id, slotsysteem="slotboeking", piektoeslag_cent=2580,
                           geldig_van=date(2026, 1, 1), bron="RWG website", status="open",
                           opmerking="Piektoeslag € 25,80 per slot, ook bij een gemiste boeking. Rest Open."))

    # ---------------------------------------------------------- rederijen en D&D
    maersk = m.Rederij(naam="Maersk (voorbeeldtarieven)", scac="MAEU",
                       retourregels="Lege 20ft en 40ft naar Depot Waalhaven of Depot Maasvlakte (demo)")
    demolines = m.Rederij(naam="Demo Lines (verzonnen)", scac="DEMU",
                          retourregels="Leeg retour naar Depot Botlek (demo)")
    db.add_all([maersk, demolines])
    db.flush()
    bron_dd = "Maersk Nederland import, geldig per 1 augustus 2026 (voorbeeld, niet algemeen)"
    dd = [
        ("demurrage", "20", "DC", 4, [(5, 8, 8500), (9, 13, 13000), (14, None, 19000)]),
        ("demurrage", "40", "DC", 4, [(5, 8, 11000), (9, 13, 21000), (14, None, 25000)]),
        ("demurrage", "40", "HC", 4, [(5, 8, 11000), (9, 13, 21000), (14, None, 25000)]),
        ("demurrage", "45", "HC", 4, [(5, 8, 11000), (9, 13, 21000), (14, None, 25000)]),
        ("demurrage", "20", "reefer", 4, [(5, 8, 23000), (9, 13, 32000), (14, None, 38500)]),
        ("demurrage", "40", "reefer", 4, [(5, 8, 23000), (9, 13, 32000), (14, None, 38500)]),
        ("detention", "20", "DC", 3, [(4, 10, 6000), (11, 14, 9000), (15, None, 11000)]),
        ("detention", "40", "DC", 3, [(4, 10, 8000), (11, 14, 11000), (15, None, 15000)]),
        ("detention", "20", "reefer", 3, [(4, 10, 15000), (11, 14, 17000), (15, None, 19000)]),
    ]
    for soort, maat, type_, vrij, banden in dd:
        for dvan, dtot, bedrag in banden:
            db.add(m.DDTarief(rederij_id=maersk.id, soort=soort, container_maat=maat, container_type=type_,
                              vrije_dagen=vrij, dag_van=dvan, dag_tot=dtot, bedrag_per_dag_cent=bedrag,
                              geldig_van=date(2026, 8, 1), bron=bron_dd, status="schatting"))
    # Demo Lines: verzonnen, zelfde vorm
    db.add(m.DDTarief(rederij_id=demolines.id, soort="demurrage", container_maat="20", container_type="DC",
                      vrije_dagen=5, dag_van=6, dag_tot=None, bedrag_per_dag_cent=9000,
                      geldig_van=date(2026, 1, 1), bron=BRON_DEMO, status="schatting"))
    db.add(m.DDTarief(rederij_id=demolines.id, soort="demurrage", container_maat="40", container_type="HC",
                      vrije_dagen=5, dag_van=6, dag_tot=None, bedrag_per_dag_cent=12000,
                      geldig_van=date(2026, 1, 1), bron=BRON_DEMO, status="schatting"))

    # ---------------------------------------------------------- verkooptarieven (verzonnen)
    for maat, prijs in (("20", 29500), ("40", 34500), ("45", 37500)):
        db.add(m.Tariefregel(order_type=None, container_maat=maat, basisprijs_cent=prijs, wachttijd_vrij_min=120,
                             wachttijd_per_half_uur_cent=4000, adr_toeslag_cent=7500, reefer_toeslag_cent=5000,
                             handeling_per_uur_cent=6500, geldig_van=date(2026, 1, 1), bron=BRON_DEMO,
                             status="schatting"))

    # ---------------------------------------------------------- chassis
    def chassis(nr, type_, assen, tarra, bron, t20=False, t40=False, t45=False, geschikt="dry,HC", genset="niet",
                adr=False, kiep=False, max_bruto=30480, kingpin=None, asgroep=None, opm=None, status="actief"):
        c = m.Chassis(nummer=nr, type=type_, assen=assen, tarra_kg=tarra, tarra_bron=bron, twistlock_20=t20,
                      twistlock_40=t40, twistlock_45=t45, geschikt_voor=geschikt, genset=genset, adr_tank=adr,
                      kiepfunctie=kiep, max_bruto_container_kg=max_bruto, max_kingpin_kg=kingpin,
                      max_asgroep_kg=asgroep, opmerking=opm, status=status, keuring_datum=vandaag + timedelta(days=200))
        db.add(c)
        return c

    c201 = chassis("C-201", "20ft", 2, 3450, "fabrikant", t20=True, opm="Vast 20ft, 2 assen (aantal assen: aanname)")
    c202 = chassis("C-202", "20ft", 3, 4200, "aanname", t20=True, geschikt="dry,HC,open top,flat rack",
                   max_bruto=36000, opm="Zwaar 20ft tridem-chassis")
    c204 = chassis("C-204", "40ft", 3, 4540, "fabrikant", t40=True)
    c205 = chassis("C-205", "40ft", 3, 4540, "fabrikant", t40=True, opm="Gooseneck")
    c206 = chassis("C-206", "multi", 3, 5300, "fabrikant", t20=True, t40=True, t45=True, kingpin=16000,
                   asgroep=27000, opm="Multi-chassis: 1x20, 2x20, 40 of 45")
    c207 = chassis("C-207", "uitschuifbaar 20-40-45", 3, 5000, "aanname", t20=True, t40=True, t45=True,
                   geschikt="dry,HC,reefer", genset="clip-on")
    c208 = chassis("C-208", "tank", 3, 4800, "aanname", t20=True, geschikt="tank", adr=True)
    c209 = chassis("C-209", "kipchassis", 3, 5800, "aanname", t20=True, t40=True, geschikt="dry,HC", kiep=True)
    db.flush()

    # ---------------------------------------------------------- trekkers
    def trekker(kenteken, nr, merk, jaar, aandr, tarra, bron, adr="geen", massa=None, aandrijfas=11500,
                status="actief", ze=False, euro="Euro 6", co2=1, chassis_id=None, opm=None):
        t = m.Trekker(kenteken=kenteken, intern_nummer=nr, merk_model=merk, bouwjaar=jaar, aandrijving=aandr,
                      tarra_kg=tarra, tarra_bron=bron, toegestane_massa_kg=massa, max_aandrijfas_kg=aandrijfas,
                      max_koppelplaat_kg=None, euro_klasse=euro, co2_klasse=co2, zero_emissie=ze,
                      adr_uitvoering=adr, tolkastje=True, apk_datum=vandaag + timedelta(days=120),
                      onderhoud_datum=vandaag + timedelta(days=40), tachograaf_ijking=vandaag + timedelta(days=300),
                      status=status, standplaats_id=standplaats.id, begin_tijd=time(6, 0), eind_tijd=time(18, 0),
                      max_km_dag=600, kosten_per_km_cent=None, kosten_per_uur_cent=None,
                      verbruik_l_per_100km=None, vaste_chassis_id=chassis_id, opmerking=opm)
        db.add(t)
        return t

    t11 = trekker("01-DTB-1", "11", "Demo merk A (vrije tekst)", 2021, "4x2", 8000, "aanname", chassis_id=c204.id,
                  opm="Leeggewicht is een aanname")
    t12 = trekker("02-DTB-2", "12", "Demo merk B", 2022, "4x2", 7650, "gewogen", adr="tank", chassis_id=c208.id)
    t13 = trekker("03-DTB-3", "13", "Demo merk A", 2020, "6x2", 8900, "aanname", adr="basis", chassis_id=c206.id)
    t14 = trekker("04-DTB-4", "14", "Demo merk C", 2019, "6x4", 9400, "aanname", chassis_id=c209.id,
                  opm="Zwaar werk en kiepen")
    t15 = trekker("05-DTB-5", "15", "Demo merk B", 2023, "4x2", 8100, "kentekenbewijs", chassis_id=c207.id)
    t16 = trekker("06-DTB-6", "16", "Demo merk A", 2018, "4x2", None, "aanname", status="in onderhoud",
                  opm="Tarra onbekend. Staat in onderhoud.")
    db.flush()
    db.add(m.Afwezigheid(trekker_id=t16.id, van=vandaag, tot=morgen + timedelta(days=2), reden="Onderhoud"))
    # voorkeuren
    db.add_all([
        m.VoertuigVoorkeur(trekker_id=t12.id, soort="taak", waarde="tank/ADR", gewicht=9),
        m.VoertuigVoorkeur(trekker_id=t14.id, soort="taak", waarde="kiepwerk", gewicht=8),
        m.VoertuigVoorkeur(trekker_id=t14.id, soort="taak", waarde="zware containers", gewicht=7),
        m.VoertuigVoorkeur(trekker_id=t15.id, soort="taak", waarde="reefer", gewicht=8),
        m.VoertuigVoorkeur(trekker_id=t11.id, soort="taak", waarde="standaard dry", gewicht=5),
        m.VoertuigVoorkeur(trekker_id=t11.id, soort="terminal_voorkeur", waarde="ECT Delta", gewicht=3),
        m.VoertuigVoorkeur(trekker_id=t13.id, soort="klant_uitgesloten", waarde="Echo Handel GmbH (demo)", gewicht=6),
    ])

    # ---------------------------------------------------------- chauffeurs (pseudoniemen)
    lang = vandaag + timedelta(days=700)

    def chauffeur(naam, uren, adr_b=None, adr_t=None, ect=lang, trekker_=None, regio="Rotterdam", opm=None):
        c = m.Chauffeur(pseudoniem=naam, contracturen_week=uren, ce_geldig_tot=lang, code95_geldig_tot=lang,
                        adr_basis_tot=adr_b, adr_tank_tot=adr_t, ect_test_tot=ect, cargocard_tot=lang,
                        standaard_begin=time(6, 0), standaard_eind=time(17, 30), voorkeur_regio=regio,
                        voorkeur_trekker_id=trekker_.id if trekker_ else None, opmerking=opm)
        db.add(c)
        return c

    arend = chauffeur("Arend", 40, adr_b=lang, adr_t=lang, trekker_=t12, opm="ADR basis en tank")
    bas = chauffeur("Bas", 40, adr_b=lang, trekker_=t13, opm="ADR basis")
    celine = chauffeur("Celine", 40, trekker_=t15)
    dirk = chauffeur("Dirk", 40, trekker_=t11, opm="Valkuil: weekrijtijd is bijna op")
    esra = chauffeur("Esra", 32, trekker_=t14)
    fenna = chauffeur("Fenna", 40, opm="Valkuil: heeft morgen verlof")
    gijs = chauffeur("Gijs", 40, ect=None, opm="Valkuil: geen geldige ECT-veiligheidstest")
    hamza = chauffeur("Hamza", 24, adr_b=vandaag - timedelta(days=10),
                      opm="ADR basis is verlopen (valkuil)")
    db.flush()
    db.add(m.Afwezigheid(chauffeur_id=fenna.id, van=morgen, tot=morgen, reden="Verlof"))
    # Dirk heeft deze week al veel gereden: valkuil "bijna aan rijtijd".
    week_start = morgen - timedelta(days=morgen.weekday())
    d = week_start
    while d < morgen:
        db.add(m.RijtijdRegistratie(chauffeur_id=dirk.id, datum=d, rijtijd_min=600 if d.weekday() < 2 else 540,
                                    werktijd_min=720, bron="demodata"))
        d += timedelta(days=1)
    # Vorige week (voor de twee-wekenregel)
    for i in range(5):
        dag = week_start - timedelta(days=7 - i)
        db.add(m.RijtijdRegistratie(chauffeur_id=dirk.id, datum=dag, rijtijd_min=540, werktijd_min=660,
                                    bron="demodata"))
        db.add(m.RijtijdRegistratie(chauffeur_id=arend.id, datum=dag, rijtijd_min=420, werktijd_min=540,
                                    bron="demodata"))

    # ---------------------------------------------------------- gebruikers
    ww = instellingen().demo_wachtwoord
    db.add_all([
        m.Gebruiker(gebruikersnaam="planner", wachtwoord_hash=hash_wachtwoord(ww), rol="planner"),
        m.Gebruiker(gebruikersnaam="admin", wachtwoord_hash=hash_wachtwoord(ww), rol="admin"),
        m.Gebruiker(gebruikersnaam="chauffeur", wachtwoord_hash=hash_wachtwoord(ww), rol="chauffeur",
                    chauffeur_id=arend.id),
    ])

    # ---------------------------------------------------------- orders voor morgen
    serie = [100000]

    def order(ref, klant, type_, van, naar, uur_van, uur_tot, containers, retour=None, route="NL",
              handelingen=(), release="Vrij", opm=None, min_van=0):
        o = m.Order(klant_id=klant.id, klantreferentie=ref, type=type_, boeking_bl=f"BL-{ref}",
                    venster_van=nl_tijd(morgen, uur_van, min_van), venster_tot=nl_tijd(morgen, uur_tot),
                    van_locatie_id=van.id, naar_locatie_id=naar.id,
                    retour_locatie_id=retour.id if retour else None, status="Nieuw", land_route=route,
                    gecombineerd_vervoer=True, opmerkingen=opm)
        db.add(o)
        db.flush()
        for soort, duur in handelingen:
            db.add(m.OrderHandeling(order_id=o.id, soort=soort, duur_min=duur, duur_is_aanname=True))
        for c in containers:
            maat, type_c, vgm, rederij = c[:4]
            imo = c[4] if len(c) > 4 else None
            un = c[5] if len(c) > 5 else None
            serie[0] += 137
            tarra = {"20": 2250, "40": 3750 if type_c != "HC" else 4150, "45": 4800}[maat]
            eig = "MSKU" if rederij is maersk else "DEMU"
            cont = m.Container(nummer=containernummer(eig[:3], serie[0]), rederij_id=rederij.id, order_id=o.id,
                               maat=maat, type=type_c, tarra_kg=tarra, tarra_is_aanname=True, vgm_kg=vgm,
                               bruto_kg=vgm, imo_klasse=imo, un_nummer=un,
                               reefer_setpoint="-18" if type_c == "reefer" else None,
                               status="Vrij" if type_ == "import" else "Aangekondigd")
            db.add(cont)
            db.flush()
            if type_ == "import":
                ontlaad = morgen - timedelta(days=2)
                db.add(m.Vrijgave(container_id=cont.id, status=release, commercieel=release == "Vrij",
                                  douane=release == "Vrij", terminal_status=release == "Vrij",
                                  ontlaaddatum=ontlaad, lfd=ontlaad + timedelta(days=3)))
        return o

    import_ = "import"
    export = "export"
    # Gewone importen
    order("DEMO-1001", alfa, import_, ect_delta, l_alfa, 8, 14, [("40", "HC", 18500, maersk)], retour=depot_w)
    order("DEMO-1002", alfa, import_, ect_euromax, l_alfa, 9, 16, [("40", "HC", 21000, maersk)], retour=depot_w)
    # VALKUIL: te zwaar voor 42 ton (intermodaal)
    order("DEMO-1003", charlie, import_, apmt, l_charlie, 7, 15, [("40", "HC", 28500, maersk)], retour=depot_m,
          route="NL-intermodaal", opm="Valkuil: zwaar, past niet bij 42 t")
    order("DEMO-1004", charlie, import_, rwg, l_charlie, 6, 12, [("20", "DC", 14000, demolines)], retour=depot_b)
    # VALKUIL: LFD morgen
    o5 = order("DEMO-1005", delta, import_, ect_delta, l_delta, 7, 15, [("20", "DC", 22000, maersk)],
               retour=depot_w, opm="Valkuil: last free day is morgen")
    # Zware 20ft (aslast)
    order("DEMO-1006", delta, import_, apmt, l_delta, 8, 15, [("20", "DC", 30480, maersk)], retour=depot_m,
          route="NL-intermodaal", opm="Zware 20ft: aslast-controle")
    # VALKUIL: slot past niet (slot vroeg, klant pas later open)
    o7 = order("DEMO-1007", alfa, import_, ect_euromax, l_alfa, 13, 17, [("40", "HC", 17000, maersk)],
               retour=depot_w, opm="Valkuil: slot past niet bij het tijdvenster")
    # Reefer
    order("DEMO-1008", charlie, import_, ect_delta, l_charlie, 5, 11, [("40", "reefer", 24000, maersk)],
          retour=depot_m, opm="Reefer: stroom of genset nodig")
    # 45ft
    order("DEMO-1009", alfa, import_, rwg, l_alfa, 9, 17, [("45", "HC", 19000, demolines)], retour=depot_b)
    # VALKUIL: twee tank/ADR-ritten tegelijk, maar maar één chauffeur met ADR-tank
    order("DEMO-1010", bravo, import_, ect_delta, l_bravo, 8, 12, [("20", "tank", 24000, maersk, "3", "UN1993")],
          retour=depot_b, opm="ADR tank")
    order("DEMO-1011", bravo, import_, ect_euromax, l_bravo, 8, 12, [("20", "tank", 23500, maersk, "8", "UN1830")],
          retour=depot_b, opm="Valkuil: tegelijk met DEMO-1010, te weinig ADR-tank chauffeurs")
    # ADR in een gewone dry-container (ADR basis)
    order("DEMO-1012", bravo, export, l_bravo, ect_delta, 10, 16, [("20", "DC", 16000, maersk, "9", "UN3077")],
          opm="ADR basis (klasse 9)")
    # Kiepwerk
    order("DEMO-1013", delta, import_, ect_delta, l_delta, 7, 14, [("20", "DC", 21000, demolines)], retour=depot_w,
          handelingen=[("kiepen", 45)], opm="Kiepen bij de klant")
    # Flexitank
    order("DEMO-1014", charlie, export, depot_b, ect_euromax, 9, 17, [("20", "DC", 21500, demolines)],
          handelingen=[("flexitank inbouwen", 60)], opm="Flexitank inbouwen voor export")
    # Exporten
    order("DEMO-1015", alfa, export, l_alfa, ect_delta, 10, 18, [("40", "HC", 15000, maersk)])
    order("DEMO-1016", delta, export, l_delta, apmt, 9, 16, [("40", "DC", 19000, maersk)])
    order("DEMO-1017", charlie, export, l_charlie, rwg, 11, 18, [("20", "DC", 12000, demolines)])
    # Twee 20ft op één chassis
    order("DEMO-1018", alfa, import_, ect_euromax, l_alfa, 8, 15,
          [("20", "DC", 11000, maersk), ("20", "DC", 12000, maersk)], retour=depot_w, opm="Twee 20ft samen")
    # Lege retouren
    order("DEMO-1019", alfa, "leeg", l_alfa, depot_w, 14, 18, [("40", "HC", 4150, maersk)], opm="Lege retour")
    order("DEMO-1020", delta, "leeg", l_delta, depot_m, 12, 18, [("20", "DC", 2250, maersk)], opm="Lege retour")
    order("DEMO-1021", charlie, "leeg", depot_b, l_charlie, 6, 10, [("40", "HC", 4150, demolines)],
          opm="Lege container ophalen voor export")
    # Duitsland (wegdeel > 150 km)
    order("DEMO-1022", echo, import_, ect_euromax, l_echo, 6, 18, [("40", "HC", 20000, maersk)], retour=depot_m,
          route="DE-intermodaal", opm="Naar Duisburg: wegdeel ca. 220 km, risico (Open)")
    # Release ontbreekt
    order("DEMO-1023", delta, import_, rwg, l_delta, 8, 15, [("40", "DC", 20000, demolines)], retour=depot_b,
          release="Verwacht", opm="Release nog niet vrij")
    order("DEMO-1024", alfa, import_, apmt, l_alfa, 7, 13, [("20", "DC", 17500, maersk)], retour=depot_m)
    order("DEMO-1025", charlie, export, l_charlie, ect_euromax, 13, 19, [("40", "reefer", 22000, maersk)],
          opm="Reefer export")
    db.flush()

    # ---------------------------------------------------------- reistijden (aanname, de planner kan ze aanpassen)
    maasvlakte = [ect_delta, ect_euromax, apmt, rwg, depot_m]
    vaste = [  # (locatie, minuten vanaf Maasvlakte, km)
        (depot_w, 35, 35), (depot_b, 25, 22), (standplaats, 45, 48), (l_alfa, 85, 100), (l_bravo, 25, 23),
        (l_charlie, 45, 50), (l_delta, 60, 68),
    ]
    for t in maasvlakte:
        for loc, mins, km in vaste:
            db.add(m.Reistijd(van_locatie_id=t.id, naar_locatie_id=loc.id, minuten=mins, km=km,
                              bron="schatting demodata", is_aanname=True))
        db.add(m.Reistijd(van_locatie_id=t.id, naar_locatie_id=l_echo.id, minuten=190, km=225, km_buitenland=95,
                          land_buitenland="DE", bron="schatting demodata (Rotterdam-Duisburg ca. 220 km)",
                          is_aanname=True))
    for i, a in enumerate(maasvlakte):
        for b in maasvlakte[i + 1:]:
            db.add(m.Reistijd(van_locatie_id=a.id, naar_locatie_id=b.id, minuten=10, km=6, bron="schatting demodata"))
    db.flush()

    # LFD morgen voor DEMO-1005
    c5 = o5.containers[0]
    vr5 = db.scalar(select(m.Vrijgave).where(m.Vrijgave.container_id == c5.id))
    vr5.lfd = morgen
    vr5.ontlaaddatum = morgen - timedelta(days=3)
    # Slot voor DEMO-1007: 06:00-08:00 bij ECT Euromax, maar de klant wil pas om 13:00
    db.add(m.Slot(terminal_id=ect_euromax.id, handlingtype="ophalen", slot_van=nl_tijd(morgen, 6),
                  slot_tot=nl_tijd(morgen, 8), label=f"PN-{o7.klantreferentie}", status="Toegekend",
                  tar="TAR-DEMO-7"))
    db.flush()

    # ---------------------------------------------------------- ritten (één per order) en twee vooraf geplande ritten
    from app.planner.context import laad_dag
    from app.planner.ritten import maak_rit_voor_order, plan_rit

    orders = list(db.scalars(select(m.Order).order_by(m.Order.id)))
    ritten = {o.klantreferentie: maak_rit_voor_order(db, o) for o in orders}
    db.flush()
    slot7 = db.scalar(select(m.Slot).where(m.Slot.label == f"PN-{o7.klantreferentie}"))
    slot7.rit_id = ritten["DEMO-1007"].id
    ctx = laad_dag(db, morgen)
    rit4 = next(r for r in ctx.ritten if r.order.klantreferentie == "DEMO-1004")
    plan_rit(ctx, rit4, nl_tijd(morgen, 6, 0), t15.id, c207.id, celine.id)
    rit4.vastheid = "toegezegd"
    rit21 = next(r for r in ctx.ritten if r.order.klantreferentie == "DEMO-1021")
    plan_rit(ctx, rit21, nl_tijd(morgen, 7, 0), t14.id, c209.id, esra.id)
    rit21.vastheid = "toegezegd"
    db.flush()
    _ = (t11, t12, t13, t14, t15, c201, c202, c204, c205, c206, c207, c208, c209, bas, celine, esra, gijs, hamza,
         ect_delta, depot_m, l_echo)


def is_leeg(db: Session) -> bool:
    return (db.scalar(select(func.count()).select_from(m.Gebruiker)) or 0) == 0


def maak_leeg(db: Session) -> None:
    """Alles weg, ook het logboek. Alleen voor de demo (niet via de app te doen)."""
    conn = db.connection()
    for tabel in reversed(Base.metadata.sorted_tables):
        conn.execute(delete(tabel))
    db.commit()


def main() -> None:
    parser = argparse.ArgumentParser(description="Vul de database met demodata (verzonnen).")
    parser.add_argument("--reset", action="store_true", help="Maak alles leeg en vul opnieuw")
    args = parser.parse_args()
    with SessionLocal() as db:
        if args.reset:
            maak_leeg(db)
        if not is_leeg(db):
            print("Database bevat al data. Niets gedaan. Gebruik --reset om opnieuw te beginnen.")
            return
        vul(db)
        db.commit()
        print(f"Demodata geladen voor {morgen_nl():%d-%m-%Y} (morgen).")


if __name__ == "__main__":
    main()
