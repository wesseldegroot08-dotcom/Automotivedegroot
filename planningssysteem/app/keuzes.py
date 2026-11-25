"""Vaste keuzelijsten. We slaan ze op als tekst, zodat de database simpel blijft."""

ROLLEN = ["planner", "admin", "chauffeur"]

STATUS_REGEL = ["bevestigd", "schatting", "open"]

LOCATIE_TYPES = ["terminal", "depot", "klant", "overig"]
LIVE_OF_DROP = ["live", "drop", "beide"]

AANDRIJVING = ["4x2", "6x2", "6x4"]
TARRA_BRON = ["gewogen", "kentekenbewijs", "fabrikant", "aanname"]
ADR_UITVOERING = ["geen", "basis", "tank"]
VOERTUIG_STATUS = ["actief", "in onderhoud", "buiten gebruik"]

CHASSIS_TYPES = ["20ft", "40ft", "45ft", "uitschuifbaar 20-40-45", "tank", "kipchassis", "multi"]
GENSET = ["clip-on", "onderbouw", "niet"]
CONTAINER_SOORTEN = ["dry", "HC", "reefer", "tank", "flat rack", "open top"]

CONTAINER_MATEN = ["20", "40", "45"]
CONTAINER_TYPES = ["DC", "HC", "reefer", "tank", "flat", "OT"]

ORDER_TYPES = ["import", "export", "leeg", "ITT"]
HANDELINGEN = ["kiepen", "flexitank inbouwen", "overpompen", "tankwas", "reachstacker"]

RIT_TYPES = ["afhaal", "aflever", "leeg retour", "pre-pull", "shuttle", "ITT"]
STOP_TYPES = ["gate-in", "gate-out", "laden", "lossen", "drop", "pickup"]
VASTHEID = ["open", "toegezegd", "gestart"]

VOORKEUR_SOORTEN = [
    "taak",  # waarde: zware containers, tank/ADR, kiepwerk, flexitank, reefer, standaard dry
    "locatie_voorkeur",
    "locatie_uitgesloten",
    "klant_voorkeur",
    "klant_uitgesloten",
    "terminal_voorkeur",
    "regio",
    "chauffeur_voorkeur",
]
VOORKEUR_TAKEN = ["zware containers", "tank/ADR", "kiepwerk", "flexitank", "reefer", "standaard dry"]

DD_SOORT = ["demurrage", "detention"]
SLOTSYSTEEM = ["prenotificatie-eta", "slotboeking", "geen"]

REDENCODES = {
    "KLANT": "Afgesproken met de klant",
    "DATA": "Gegevens in het systeem kloppen niet",
    "SPOED": "Spoed, geen andere oplossing",
    "GECONTROLEERD": "Zelf gecontroleerd bij de bron",
    "ANDERS": "Anders (leg uit in de tekst)",
}
