"""Welke stamdata-schermen er zijn, en welke velden ze hebben."""

from dataclasses import dataclass, field
from typing import Any

from app import keuzes as k
from app import models as m
from app.web.velden import Veld, regel_velden


@dataclass
class Entiteit:
    slug: str
    titel: str
    model: Any
    velden: list[Veld]
    groep: str = "Stamdata"
    archief_veld: str | None = None  # 'actief' (True = in gebruik) of 'gearchiveerd'
    uitleg: str = ""
    sorteer: str = "id"
    extra: dict = field(default_factory=dict)

    def label(self, obj) -> str:
        for naam in ("naam", "pseudoniem", "kenteken", "nummer", "klantreferentie", "code"):
            if hasattr(obj, naam):
                return str(getattr(obj, naam))
        return f"#{obj.id}"


def _naam(obj) -> str:
    return getattr(obj, "naam", None) or getattr(obj, "pseudoniem", None) or getattr(
        obj, "kenteken", None) or getattr(obj, "nummer", None) or getattr(
        obj, "klantreferentie", None) or f"#{obj.id}"


def fk(naam, label, model, verplicht=False, in_lijst=False, hulp=""):
    return Veld(naam, label, "fk", verplicht=verplicht, fk_model=model, fk_label=_naam,
                in_lijst=in_lijst, hulp=hulp)


ENTITEITEN: list[Entiteit] = [
    Entiteit("klanten", "Klanten", m.Klant, archief_veld="actief", sorteer="naam", velden=[
        Veld("naam", "Naam", verplicht=True, in_lijst=True),
        Veld("factuuradres", "Factuuradres", "lang"),
        Veld("betaaltermijn_dagen", "Betaaltermijn (dagen)", "getal", verplicht=True, min=0, in_lijst=True),
        Veld("contactpersoon", "Contactpersoon (verzonnen naam)"),
        Veld("email", "E-mail (verzonnen)"),
        Veld("opmerking", "Opmerking", "lang"),
    ]),
    Entiteit("locaties", "Locaties", m.Locatie, archief_veld="actief", sorteer="naam",
             uitleg="Terminals, depots en klantadressen. Openingstijden en laad/lostijd zijn nodig om te plannen.",
             velden=[
        Veld("type", "Soort locatie", "keuze", verplicht=True, keuzes=k.LOCATIE_TYPES, in_lijst=True),
        Veld("naam", "Naam", verplicht=True, in_lijst=True),
        Veld("lat", "Breedtegraad (lat)", "kommagetal", verplicht=True),
        Veld("lon", "Lengtegraad (lon)", "kommagetal", verplicht=True),
        Veld("land", "Land (NL, DE, BE)", verplicht=True, in_lijst=True),
        Veld("open_van", "Open vanaf", "tijd", verplicht=True, in_lijst=True),
        Veld("open_tot", "Open tot", "tijd", verplicht=True, in_lijst=True),
        Veld("open_dagen", "Open op dagen (1=ma ... 7=zo, bijv. 12345)", verplicht=True),
        Veld("laad_los_min", "Standaard laad- en lostijd (minuten)", "getal", verplicht=True, min=0),
        Veld("laad_los_is_aanname", "Laad/lostijd is een aanname", "bool"),
        Veld("live_of_drop", "Live of drop", "keuze", verplicht=True, keuzes=k.LIVE_OF_DROP),
        Veld("max_gewicht_kg", "Max gewicht (kg)", "getal", min=0),
        Veld("max_hoogte_mm", "Max hoogte (mm)", "getal", min=0),
        Veld("adr_toegestaan", "ADR toegestaan", "bool"),
        Veld("reefer_stroom", "Stroom voor reefer", "bool"),
        Veld("terminalcode", "Havennummer of terminalcode", in_lijst=True),
        fk("klant_id", "Hoort bij klant", m.Klant),
    ]),
    Entiteit("rederijen", "Rederijen", m.Rederij, archief_veld="actief", sorteer="naam", velden=[
        Veld("naam", "Naam", verplicht=True, in_lijst=True),
        Veld("scac", "SCAC-code (4 letters)", verplicht=True, in_lijst=True),
        Veld("retourregels", "Retourregels lege containers", "lang"),
    ]),
    Entiteit("chauffeurs", "Chauffeurs", m.Chauffeur, archief_veld="actief", sorteer="pseudoniem",
             uitleg="Gebruik alleen pseudoniemen. Geen echte namen, geen GPS.", velden=[
        Veld("pseudoniem", "Pseudoniem", verplicht=True, in_lijst=True),
        Veld("contracturen_week", "Contracturen per week", "getal", verplicht=True, min=0, max=60, in_lijst=True),
        Veld("ce_geldig_tot", "Rijbewijs CE geldig tot", "datum"),
        Veld("code95_geldig_tot", "Code 95 geldig tot", "datum"),
        Veld("adr_basis_tot", "ADR basis geldig tot", "datum", in_lijst=True),
        Veld("adr_tank_tot", "ADR tank geldig tot", "datum", in_lijst=True),
        Veld("ccv_lzv", "CCV-certificaat voor LZV", "bool"),
        Veld("ect_test_tot", "ECT-veiligheidstest geldig tot", "datum", verplicht=False, in_lijst=True),
        Veld("cargocard_tot", "CargoCard geldig tot", "datum"),
        Veld("standaard_begin", "Standaard begintijd", "tijd", verplicht=True),
        Veld("standaard_eind", "Standaard eindtijd", "tijd", verplicht=True),
        Veld("voorkeur_regio", "Voorkeur regio"),
        fk("voorkeur_trekker_id", "Voorkeur trekker", m.Trekker),
        Veld("opmerking", "Opmerking", "lang"),
    ]),
    Entiteit("afwezigheid", "Verlof en niet beschikbaar", m.Afwezigheid, velden=[
        fk("chauffeur_id", "Chauffeur", m.Chauffeur, in_lijst=True),
        fk("trekker_id", "Trekker", m.Trekker, in_lijst=True),
        fk("chassis_id", "Trailer", m.Chassis, in_lijst=True),
        Veld("van", "Van", "datum", verplicht=True, in_lijst=True),
        Veld("tot", "Tot en met", "datum", verplicht=True, in_lijst=True),
        Veld("reden", "Reden (verlof, onderhoud, keuring)", verplicht=True, in_lijst=True),
    ]),
    Entiteit("rijtijden", "Rij- en werktijd per dag", m.RijtijdRegistratie, sorteer="datum",
             uitleg="Nu handmatig of demodata. De tachograaf is de wettelijke waarheid.", velden=[
        fk("chauffeur_id", "Chauffeur", m.Chauffeur, verplicht=True, in_lijst=True),
        Veld("datum", "Datum", "datum", verplicht=True, in_lijst=True),
        Veld("rijtijd_min", "Rijtijd (minuten)", "getal", verplicht=True, min=0, in_lijst=True),
        Veld("werktijd_min", "Werktijd (minuten)", "getal", verplicht=True, min=0, in_lijst=True),
        Veld("bron", "Bron", verplicht=True),
    ]),
    Entiteit("orders", "Orders", m.Order, groep="Werk", sorteer="venster_van", velden=[
        fk("klant_id", "Klant", m.Klant, verplicht=True, in_lijst=True),
        Veld("klantreferentie", "Klantreferentie", verplicht=True, in_lijst=True),
        Veld("type", "Soort order", "keuze", verplicht=True, keuzes=k.ORDER_TYPES, in_lijst=True),
        Veld("boeking_bl", "Boeking of B/L", verplicht=True),
        Veld("venster_van", "Gewenst tijdvenster vanaf", "datumtijd", verplicht=True, in_lijst=True),
        Veld("venster_tot", "Gewenst tijdvenster tot", "datumtijd", verplicht=True),
        fk("van_locatie_id", "Ophalen bij", m.Locatie, verplicht=True, in_lijst=True),
        fk("naar_locatie_id", "Afleveren bij", m.Locatie, verplicht=True, in_lijst=True),
        fk("retour_locatie_id", "Lege container terug naar", m.Locatie),
        Veld("land_route", "Grens voor gewicht", "keuze", verplicht=True,
             keuzes=["NL", "NL-intermodaal", "DE", "DE-intermodaal", "BE"],
             hulp="Bepaalt welke gewichtsgrens geldt."),
        Veld("gecombineerd_vervoer", "Gecombineerd vervoer (haven/spoor)", "bool"),
        Veld("status", "Status", verplicht=True, in_lijst=True,
             hulp="Wordt later via vaste stappen gewijzigd (mijlpaal 3)."),
        Veld("opmerkingen", "Opmerkingen", "lang"),
    ]),
    Entiteit("handelingen", "Extra handelingen bij orders", m.OrderHandeling, groep="Werk", velden=[
        fk("order_id", "Order", m.Order, verplicht=True, in_lijst=True),
        Veld("soort", "Handeling", "keuze", verplicht=True, keuzes=k.HANDELINGEN, in_lijst=True),
        Veld("duur_min", "Duur (minuten)", "getal", verplicht=True, min=0, in_lijst=True),
        Veld("duur_is_aanname", "Duur is een aanname", "bool", in_lijst=True),
    ]),
    Entiteit("containers", "Containers", m.Container, groep="Werk", sorteer="nummer", velden=[
        Veld("nummer", "Containernummer (bijv. CSQU3054383)", verplicht=True, in_lijst=True),
        fk("rederij_id", "Rederij", m.Rederij, verplicht=True, in_lijst=True),
        fk("order_id", "Order", m.Order, in_lijst=True),
        Veld("maat", "Maat (voet)", "keuze", verplicht=True, keuzes=k.CONTAINER_MATEN, in_lijst=True),
        Veld("type", "Type", "keuze", verplicht=True, keuzes=k.CONTAINER_TYPES, in_lijst=True),
        Veld("tarra_kg", "Tarra leeg (kg)", "getal", min=0),
        Veld("tarra_is_aanname", "Tarra is een aanname", "bool"),
        Veld("bruto_kg", "Bruto (kg)", "getal", min=0),
        Veld("vgm_kg", "VGM (gewogen bruto, kg)", "getal", verplicht=True, min=0, in_lijst=True),
        Veld("imo_klasse", "IMO-klasse (gevaarlijke stoffen)", in_lijst=True),
        Veld("un_nummer", "UN-nummer"),
        Veld("reefer_setpoint", "Reefer-temperatuur"),
        Veld("status", "Status", verplicht=True, in_lijst=True),
    ]),
    Entiteit("vrijgaven", "Vrijgave (release) en LFD", m.Vrijgave, groep="Werk", sorteer="lfd",
             uitleg="In de testversie vult de planner de last free day (LFD) zelf in.", velden=[
        fk("container_id", "Container", m.Container, verplicht=True, in_lijst=True),
        Veld("status", "Release-status", "keuze", verplicht=True,
             keuzes=["Onbekend", "Verwacht", "Vrij", "Geblokkeerd"], in_lijst=True),
        Veld("commercieel", "Commerciële release", "bool", in_lijst=True),
        Veld("douane", "Douane vrij", "bool", in_lijst=True),
        Veld("inspectie_vrij", "Geen inspectie (vrij)", "bool"),
        Veld("terminal_status", "Terminal vrij", "bool", in_lijst=True),
        Veld("ontlaaddatum", "Ontlaaddatum", "datum", verplicht=True),
        Veld("lfd", "Last free day (LFD)", "datum", verplicht=True, in_lijst=True),
        Veld("bron", "Bron", verplicht=True),
    ]),
    Entiteit("ritten", "Ritten", m.Rit, groep="Werk", sorteer="gepland_start",
             uitleg="Ritten plan je straks vooral op het planbord (mijlpaal 3).", velden=[
        fk("order_id", "Order", m.Order, verplicht=True, in_lijst=True),
        fk("container_id", "Container", m.Container, in_lijst=True),
        Veld("type", "Soort rit", "keuze", verplicht=True, keuzes=k.RIT_TYPES, in_lijst=True),
        fk("van_locatie_id", "Van", m.Locatie, verplicht=True, in_lijst=True),
        fk("naar_locatie_id", "Naar", m.Locatie, verplicht=True, in_lijst=True),
        Veld("gepland_start", "Gepland begin", "datumtijd", in_lijst=True),
        Veld("gepland_eind", "Gepland einde", "datumtijd"),
        fk("trekker_id", "Trekker", m.Trekker, in_lijst=True),
        fk("chassis_id", "Trailer", m.Chassis),
        fk("chauffeur_id", "Chauffeur", m.Chauffeur, in_lijst=True),
        Veld("status", "Status", verplicht=True, in_lijst=True),
        Veld("vastheid", "Vastheid", "keuze", verplicht=True, keuzes=k.VASTHEID),
    ]),
    Entiteit("stops", "Stops", m.Stop, groep="Werk", velden=[
        fk("rit_id", "Rit", m.Rit, verplicht=True, in_lijst=True),
        Veld("volgnr", "Volgnummer", "getal", verplicht=True, min=1, in_lijst=True),
        fk("locatie_id", "Locatie", m.Locatie, verplicht=True, in_lijst=True),
        Veld("type", "Soort stop", "keuze", verplicht=True, keuzes=k.STOP_TYPES, in_lijst=True),
        fk("chassis_id", "Trailer bij deze stop (drop-and-hook)", m.Chassis),
        Veld("gepland_aankomst", "Geplande aankomst", "datumtijd", in_lijst=True),
        Veld("gepland_vertrek", "Gepland vertrek", "datumtijd"),
        Veld("werkelijk_aankomst", "Werkelijke aankomst", "datumtijd"),
        Veld("werkelijk_vertrek", "Werkelijk vertrek", "datumtijd"),
        Veld("wachttijd_min", "Wachttijd (minuten)", "getal", min=0, in_lijst=True),
    ]),
    Entiteit("slots", "Slots en pre-notificatie", m.Slot, groep="Werk", velden=[
        fk("rit_id", "Rit", m.Rit, in_lijst=True),
        fk("terminal_id", "Terminal", m.Locatie, verplicht=True, in_lijst=True),
        Veld("handlingtype", "Handeling (ophalen/brengen)", verplicht=True),
        Veld("slot_van", "Slot vanaf", "datumtijd", in_lijst=True),
        Veld("slot_tot", "Slot tot", "datumtijd"),
        Veld("tar", "TAR (alleen-lezen in het echt)", in_lijst=True),
        Veld("label", "Label pre-notificatie"),
        Veld("status", "Status", verplicht=True, in_lijst=True),
        Veld("afwijzingscode", "Afwijzingscode"),
    ]),
    # ------------------------------------------------ regels (allemaal met bron en status)
    Entiteit("regels", "Regels en grenzen", m.Regel, groep="Regels", sorteer="categorie",
             uitleg="Gewichten, aslasten, maten, rijtijden, tol en kosten. Regels zijn data: "
                    "pas ze hier aan als de bron verandert. Elke wijziging komt in het logboek.",
             velden=[
        Veld("code", "Code (voor het systeem)", verplicht=True, in_lijst=True),
        Veld("categorie", "Categorie", verplicht=True, in_lijst=True),
        Veld("omschrijving", "Omschrijving", "lang", verplicht=True, in_lijst=True),
        Veld("waarde", "Waarde (heel getal)", "getal", in_lijst=True),
        Veld("eenheid", "Eenheid", verplicht=True, in_lijst=True),
        Veld("land", "Land", in_lijst=True),
        Veld("in_gebruik", "In gebruik", "bool", in_lijst=True),
        Veld("opmerking", "Opmerking", "lang"),
        *regel_velden(),
    ]),
    Entiteit("feestdagen", "Feestdagen en verbodsdagen", m.Feestdag, groep="Regels", sorteer="datum", velden=[
        Veld("land", "Land", verplicht=True, in_lijst=True),
        Veld("deelstaat", "Deelstaat (leeg = heel land)", in_lijst=True),
        Veld("datum", "Datum", "datum", verplicht=True, in_lijst=True),
        Veld("naam", "Naam", verplicht=True, in_lijst=True),
        Veld("rijverbod", "Rijverbod voor vrachtwagens", "bool", in_lijst=True),
        *regel_velden(),
    ]),
    Entiteit("terminalregels", "Slotregels per terminal", m.TerminalRegel, groep="Regels", velden=[
        fk("locatie_id", "Terminal of depot", m.Locatie, verplicht=True, in_lijst=True),
        Veld("slotsysteem", "Slotsysteem", "keuze", verplicht=True, keuzes=k.SLOTSYSTEEM, in_lijst=True),
        Veld("slotlengte_min", "Slotlengte (minuten)", "getal", min=0, in_lijst=True),
        Veld("tolerantie_min", "Tolerantie (minuten)", "getal", min=0, in_lijst=True),
        Veld("capaciteit_per_slot", "Capaciteit per slot (voor ons bedrijf)", "getal", min=0),
        Veld("tar_verplicht", "TAR verplicht", "bool"),
        Veld("cargo_closing_uren", "Cargo closing (uren voor vertrek schip)", "getal", min=0),
        Veld("no_show_kosten_cent", "No-show kosten (cent)", "getal", min=0),
        Veld("no_show_heffing_vanaf", "No-show kosten worden geheven vanaf", "datum"),
        Veld("piektoeslag_cent", "Piektoeslag per slot (cent)", "getal", min=0),
        Veld("lege_container_regels", "Regels lege containers", "lang"),
        Veld("opmerking", "Opmerking", "lang"),
        *regel_velden(),
    ]),
    Entiteit("ddtarieven", "Demurrage en detention", m.DDTarief, groep="Regels",
             uitleg="Voorbeeldtarieven, niet algemeen geldig. Controleer per rederij.", velden=[
        fk("rederij_id", "Rederij", m.Rederij, verplicht=True, in_lijst=True),
        Veld("soort", "Soort", "keuze", verplicht=True, keuzes=k.DD_SOORT, in_lijst=True),
        Veld("container_maat", "Maat", "keuze", verplicht=True, keuzes=k.CONTAINER_MATEN, in_lijst=True),
        Veld("container_type", "Type", "keuze", verplicht=True, keuzes=k.CONTAINER_TYPES, in_lijst=True),
        Veld("vrije_dagen", "Vrije dagen", "getal", verplicht=True, min=0, in_lijst=True),
        Veld("dag_van", "Vanaf dag (dag 1 = eerste dag)", "getal", verplicht=True, min=1, in_lijst=True),
        Veld("dag_tot", "Tot en met dag (leeg = verder)", "getal", min=1, in_lijst=True),
        Veld("bedrag_per_dag_cent", "Bedrag per dag (cent)", "getal", verplicht=True, min=0, in_lijst=True),
        *regel_velden(),
    ]),
    Entiteit("tariefregels", "Verkooptarieven", m.Tariefregel, groep="Regels",
             uitleg="Verzonnen demotarieven voor het factuurconcept.", velden=[
        fk("klant_id", "Klant (leeg = alle klanten)", m.Klant, in_lijst=True),
        Veld("order_type", "Soort order (leeg = alle)", "keuze", keuzes=k.ORDER_TYPES, in_lijst=True),
        Veld("container_maat", "Maat (leeg = alle)", "keuze", keuzes=k.CONTAINER_MATEN, in_lijst=True),
        Veld("basisprijs_cent", "Basisprijs (cent)", "getal", verplicht=True, min=0, in_lijst=True),
        Veld("wachttijd_vrij_min", "Vrije wachttijd (minuten)", "getal", verplicht=True, min=0),
        Veld("wachttijd_per_half_uur_cent", "Wachttijd per half uur (cent)", "getal", verplicht=True, min=0),
        Veld("adr_toeslag_cent", "ADR-toeslag (cent)", "getal", verplicht=True, min=0),
        Veld("reefer_toeslag_cent", "Reefer-toeslag (cent)", "getal", verplicht=True, min=0),
        Veld("handeling_per_uur_cent", "Extra handeling per uur (cent)", "getal", verplicht=True, min=0),
        *regel_velden(),
    ]),
]

PER_SLUG = {e.slug: e for e in ENTITEITEN}
