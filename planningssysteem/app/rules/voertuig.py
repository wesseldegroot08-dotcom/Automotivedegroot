"""Regels over de combinatie trekker + chassis + container(s).

Regel 2  chassis past bij container (hard)
Regel 3  gewicht binnen de grens (waarschuwing, hard voor voorstellen)
Regel 4  aslast (waarschuwing)
Regel 5  hoogte (waarschuwing)
Regel 14 ADR: chauffeur en voertuig (hard)
Regel 15 reefer: stroom of genset (hard)

De formule voor gewicht (uit de opdracht):
    max lading = toegestaan gewicht combinatie - trekker - chassis - lege container(s)
"""

from dataclasses import dataclass, field
from datetime import date

from app.rules.basis import HARD, OK, WAARSCHUWING, RegelBoek, Uitslag, kg_tekst, ton_tekst

# ------------------------------------------------------------------ invoer


@dataclass
class ContainerInvoer:
    maat: str  # "20", "40", "45"
    type: str  # DC, HC, reefer, tank, flat, OT
    vgm_kg: int  # gewogen bruto: lading + lege container
    tarra_kg: int | None = None
    tarra_aanname: bool = True
    imo_klasse: str | None = None
    nummer: str = ""

    @property
    def lading_kg(self) -> int | None:
        return None if self.tarra_kg is None else self.vgm_kg - self.tarra_kg

    @property
    def is_adr(self) -> bool:
        return bool(self.imo_klasse)


@dataclass
class TrekkerInvoer:
    naam: str
    aandrijving: str
    tarra_kg: int | None
    tarra_bron: str
    adr_uitvoering: str = "geen"
    max_aandrijfas_kg: int | None = None


@dataclass
class ChassisInvoer:
    naam: str
    type: str
    assen: int
    tarra_kg: int | None
    tarra_bron: str
    twistlock_20: bool = False
    twistlock_40: bool = False
    twistlock_45: bool = False
    geschikt_voor: str = "dry,HC"
    genset: str = "niet"
    adr_tank: bool = False
    kiepfunctie: bool = False
    max_bruto_container_kg: int | None = None
    kingpinhoogte_mm: int | None = None


def trekker_uit(t) -> TrekkerInvoer:
    return TrekkerInvoer(f"trekker {t.intern_nummer}", t.aandrijving, t.tarra_kg, t.tarra_bron, t.adr_uitvoering,
                         t.max_aandrijfas_kg)


def chassis_uit(c) -> ChassisInvoer:
    return ChassisInvoer(f"chassis {c.nummer}", c.type, c.assen, c.tarra_kg, c.tarra_bron, c.twistlock_20,
                         c.twistlock_40, c.twistlock_45, c.geschikt_voor, c.genset, c.adr_tank, c.kiepfunctie,
                         c.max_bruto_container_kg, c.kingpinhoogte_mm)


def container_uit(c) -> ContainerInvoer:
    return ContainerInvoer(c.maat, c.type, c.vgm_kg, c.tarra_kg, c.tarra_is_aanname, c.imo_klasse, c.nummer)


# ------------------------------------------------------------------ gewicht (regel 3)

GRENZEN = [
    ("gewicht.NL", "Nederland algemeen"),
    ("gewicht.intermodaal.3as", "Intermodaal, 3-assige trekker"),
    ("gewicht.intermodaal.2as", "Intermodaal, 2-assige trekker"),
    ("gewicht.DE", "Duitsland normaal"),
]


def grens_code_voor(route: str, aandrijving: str) -> str:
    """Welke gewichtsgrens hoort bij deze route en deze trekker?"""
    if route == "NL":
        return "gewicht.NL"
    if route.endswith("intermodaal"):
        return "gewicht.intermodaal.2as" if aandrijving == "4x2" else "gewicht.intermodaal.3as"
    if route == "DE":
        return "gewicht.DE"
    if route == "BE":
        return "gewicht.BE"
    return "gewicht.NL"


@dataclass
class GewichtRegel:
    code: str
    naam: str
    limiet_kg: int
    status: str
    bron: str
    max_lading_kg: int
    totaal_kg: int
    marge_kg: int  # positief = ruimte over, negatief = te zwaar
    past: bool


@dataclass
class GewichtOverzicht:
    lege_combinatie_kg: int | None
    totaal_kg: int | None  # trekker + chassis + alle VGM
    lading_kg: int | None
    per_grens: list[GewichtRegel] = field(default_factory=list)
    onzeker: list[str] = field(default_factory=list)
    ontbreekt: list[str] = field(default_factory=list)

    @property
    def zekerheid(self) -> str:
        if self.ontbreekt:
            return "onbekend: gegevens ontbreken"
        return "onzeker door aanname" if self.onzeker else "zeker"


def lege_combinatie(trekker_kg: int, chassis_kg: int, container_tarra_kg: list[int]) -> int:
    return trekker_kg + chassis_kg + sum(container_tarra_kg)


def max_lading(limiet_kg: int, lege_combinatie_kg: int) -> int:
    return limiet_kg - lege_combinatie_kg


def bereken_gewicht(boek: RegelBoek, datum: date, trekker: TrekkerInvoer, chassis: ChassisInvoer,
                    containers: list[ContainerInvoer], grens_codes: list[str] | None = None) -> GewichtOverzicht:
    onzeker, ontbreekt = [], []
    if trekker.tarra_kg is None:
        ontbreekt.append(f"tarra van {trekker.naam}")
    elif trekker.tarra_bron == "aanname":
        onzeker.append(f"tarra van {trekker.naam} is een aanname")
    if chassis.tarra_kg is None:
        ontbreekt.append(f"tarra van {chassis.naam}")
    elif chassis.tarra_bron == "aanname":
        onzeker.append(f"tarra van {chassis.naam} is een aanname")
    for c in containers:
        if c.tarra_kg is None:
            ontbreekt.append(f"tarra van container {c.nummer or c.maat + 'ft'}")
        elif c.tarra_aanname:
            onzeker.append(f"tarra van container {c.nummer or c.maat + 'ft'} is een aanname")
    if ontbreekt:
        return GewichtOverzicht(None, None, None, [], onzeker, ontbreekt)
    leeg = lege_combinatie(trekker.tarra_kg, chassis.tarra_kg, [c.tarra_kg for c in containers])
    totaal = trekker.tarra_kg + chassis.tarra_kg + sum(c.vgm_kg for c in containers)
    lading = totaal - leeg
    uit = GewichtOverzicht(leeg, totaal, lading, [], onzeker, [])
    codes = grens_codes or [g[0] for g in GRENZEN]
    namen = dict(GRENZEN) | {"gewicht.BE": "België (Vlaanderen)"}
    for code in codes:
        rw = boek.get(code, datum)
        if rw is None:
            continue
        ml = max_lading(rw.waarde, leeg)
        uit.per_grens.append(GewichtRegel(code, namen.get(code, rw.omschrijving), rw.waarde, rw.status, rw.bron, ml,
                                          totaal, rw.waarde - totaal, totaal <= rw.waarde))
    return uit


def regel_gewicht(boek: RegelBoek, datum: date, trekker, chassis, containers, route: str) -> Uitslag:
    code = grens_code_voor(route, trekker.aandrijving)
    g = bereken_gewicht(boek, datum, trekker, chassis, containers, [code])
    if g.ontbreekt:
        return Uitslag(3, "Gewicht", WAARSCHUWING, "Gewicht kan niet berekend worden. Ontbreekt: "
                       + ", ".join(g.ontbreekt) + ".", hard_voor_voorstel=True, onzeker=g.ontbreekt)
    if not g.per_grens:
        return Uitslag(3, "Gewicht", WAARSCHUWING, f"Geen geldige gewichtsgrens gevonden ({code}).",
                       hard_voor_voorstel=True)
    gr = g.per_grens[0]
    zeker = "" if not g.onzeker else " Onzeker: " + "; ".join(g.onzeker) + "."
    if gr.past:
        return Uitslag(3, "Gewicht", OK, f"{ton_tekst(gr.totaal_kg)} van {ton_tekst(gr.limiet_kg)} ({gr.naam}). "
                       f"Marge {kg_tekst(gr.marge_kg)}.{zeker}", gr.bron, gr.status, True, onzeker=g.onzeker)
    return Uitslag(3, "Gewicht", WAARSCHUWING, f"Te zwaar: {ton_tekst(gr.totaal_kg)} van {ton_tekst(gr.limiet_kg)} "
                   f"({gr.naam}). {kg_tekst(-gr.marge_kg)} te veel.{zeker}", gr.bron, gr.status, True,
                   onzeker=g.onzeker)


# ------------------------------------------------------------------ aslast (regel 4)


@dataclass
class AslastOverzicht:
    trekker_kg: int
    chassis_kg: int
    totaal_kg: int
    uitleg: str
    alternatief_kg: int | None = None  # met de hogere tridem-waarde (Open)


def aslast_grens(boek: RegelBoek, datum: date, aandrijving: str, chassis_assen: int) -> AslastOverzicht | None:
    enkel = boek.waarde("aslast.enkel", datum)
    aangedreven = boek.waarde("aslast.aangedreven", datum)
    tandem = boek.waarde("aslast.tandem", datum)
    tridem = boek.waarde("aslast.tridem", datum)
    if None in (enkel, aangedreven, tandem, tridem):
        return None
    if aandrijving == "4x2":
        t_kg, t_uitleg = enkel + aangedreven, f"stuuras {kg_tekst(enkel)} + aandrijfas {kg_tekst(aangedreven)}"
    else:  # 6x2 en 6x4: stuuras + tandem achter (aanname)
        t_kg, t_uitleg = enkel + tandem, f"stuuras {kg_tekst(enkel)} + tandem {kg_tekst(tandem)}"
    if chassis_assen <= 1:
        c_kg, c_naam = enkel, "enkele as"
    elif chassis_assen == 2:
        c_kg, c_naam = tandem, "tandem"
    else:
        c_kg, c_naam = tridem, "tridem"
    alt = None
    hoog = boek.waarde("aslast.tridem.hoog", datum) or 27000
    if chassis_assen >= 3:
        alt = t_kg + hoog
    return AslastOverzicht(t_kg, c_kg, t_kg + c_kg, f"{t_uitleg} + chassis {c_naam} {kg_tekst(c_kg)}", alt)


def regel_aslast(boek: RegelBoek, datum: date, trekker, chassis, containers) -> Uitslag:
    a = aslast_grens(boek, datum, trekker.aandrijving, chassis.assen)
    rw = boek.get("aslast.tandem", datum)
    bron, status = (rw.bron, rw.status) if rw else ("", "open")
    if a is None:
        return Uitslag(4, "Aslast", WAARSCHUWING, "Aslast-regels ontbreken in de regeltabel.", status="open")
    if trekker.tarra_kg is None or chassis.tarra_kg is None:
        return Uitslag(4, "Aslast", WAARSCHUWING, "Aslast kan niet berekend worden: tarra ontbreekt.", bron, status)
    totaal = trekker.tarra_kg + chassis.tarra_kg + sum(c.vgm_kg for c in containers)
    extra = ""
    pct = boek.waarde("aslast.aandrijfas.min", datum)
    if pct and trekker.max_aandrijfas_kg and trekker.max_aandrijfas_kg * 100 < totaal * pct:
        extra = (f" Let op: de aandrijfas ({kg_tekst(trekker.max_aandrijfas_kg)}) kan geen {pct}% van het totaal "
                 f"dragen (details Open).")
    if totaal > a.totaal_kg:
        return Uitslag(4, "Aslast", WAARSCHUWING, f"Assen samen mogen {kg_tekst(a.totaal_kg)} dragen ({a.uitleg}). "
                       f"Totaal is {kg_tekst(totaal)}: {kg_tekst(totaal - a.totaal_kg)} te zwaar. Een chassis met "
                       f"meer assen kan helpen.{extra}", bron, status)
    return Uitslag(4, "Aslast", WAARSCHUWING if extra else OK,
                   f"Totaal {kg_tekst(totaal)} binnen de asgrens {kg_tekst(a.totaal_kg)} ({a.uitleg}).{extra}",
                   bron, status)


# ------------------------------------------------------------------ chassis past (regel 2) en reefer (regel 15)

_SOORT_VAN_TYPE = {"DC": "dry", "HC": "HC", "reefer": "reefer", "tank": "tank", "flat": "flat rack", "OT": "open top"}


def regel_chassis_past(chassis: ChassisInvoer, containers: list[ContainerInvoer],
                       handelingen: list[str] | None = None) -> Uitslag:
    fouten = []
    geschikt = {s.strip() for s in chassis.geschikt_voor.split(",") if s.strip()}
    maten = [c.maat for c in containers]
    if maten.count("20") == 2 and len(maten) == 2:
        if not (chassis.twistlock_20 and chassis.type in ("multi", "uitschuifbaar 20-40-45")):
            fouten.append("twee 20ft passen alleen op een multi- of uitschuifbaar chassis")
    elif len(containers) > 1:
        fouten.append("meer dan één container kan alleen als het twee 20ft zijn")
    for c in containers:
        lock = {"20": chassis.twistlock_20, "40": chassis.twistlock_40, "45": chassis.twistlock_45}.get(c.maat)
        if not lock:
            fouten.append(f"een {c.maat}ft past niet op {chassis.naam} (geen twistlocks voor {c.maat}ft)")
        soort = _SOORT_VAN_TYPE.get(c.type, c.type)
        if c.type == "reefer":
            continue  # reefer: zie regel 15
        if soort not in geschikt:
            fouten.append(f"{chassis.naam} is niet geschikt voor {soort}")
        if c.type != "tank" and chassis.type == "tank":
            fouten.append("een tankchassis is alleen voor tankcontainers")
        if chassis.max_bruto_container_kg and c.vgm_kg > chassis.max_bruto_container_kg:
            fouten.append(f"container ({kg_tekst(c.vgm_kg)}) is zwaarder dan het chassis mag dragen "
                          f"({kg_tekst(chassis.max_bruto_container_kg)})")
    if handelingen and "kiepen" in handelingen and not chassis.kiepfunctie:
        fouten.append("deze order moet gekiept worden, maar het chassis heeft geen kiepfunctie")
    if fouten:
        return Uitslag(2, "Chassis past", HARD, "Niet toegestaan: " + "; ".join(fouten) + ".", "docs/onderzoek.md h3",
                       "bevestigd")
    return Uitslag(2, "Chassis past", OK, f"{chassis.naam} past bij de container(s).", "docs/onderzoek.md h3",
                   "bevestigd")


def regel_reefer(chassis: ChassisInvoer, containers: list[ContainerInvoer]) -> Uitslag | None:
    reefers = [c for c in containers if c.type == "reefer"]
    if not reefers:
        return None
    if chassis.genset in ("clip-on", "onderbouw"):
        return Uitslag(15, "Reefer: stroom", OK, f"Genset aanwezig ({chassis.genset}).", "docs/onderzoek.md h2.4",
                       "bevestigd")
    return Uitslag(15, "Reefer: stroom", HARD, f"Niet toegestaan: reefer zonder stroom. {chassis.naam} heeft geen "
                   "genset.", "docs/onderzoek.md h2.4", "bevestigd")


# ------------------------------------------------------------------ hoogte (regel 5)


def regel_hoogte(boek: RegelBoek, datum: date, chassis: ChassisInvoer, containers) -> Uitslag:
    max_mm = boek.waarde("maat.hoogte", datum)
    hc = boek.waarde("container.hoogte.hc", datum, 2896)
    std = boek.waarde("container.hoogte", datum, 2591)
    if not containers or max_mm is None:
        return Uitslag(5, "Hoogte", OK, "Geen container of geen hoogteregel.")
    hoogste = max(hc if c.type in ("HC", "reefer") or c.maat == "45" else std for c in containers)
    if chassis.kingpinhoogte_mm is None:
        return Uitslag(5, "Hoogte", WAARSCHUWING if hoogste == hc else OK,
                       "Hoogte onbekend: kingpinhoogte van het chassis ontbreekt."
                       + (" Een High Cube komt dicht bij 4,00 m." if hoogste == hc else ""), status="schatting")
    totaal = chassis.kingpinhoogte_mm + hoogste
    tekst = f"Geschat {totaal / 1000:.2f} m van max {max_mm / 1000:.2f} m (kingpinhoogte + container, aanname)."
    if totaal > max_mm:
        return Uitslag(5, "Hoogte", WAARSCHUWING, "Mogelijk te hoog. " + tekst + " Let ook op tunnels.",
                       status="schatting")
    return Uitslag(5, "Hoogte", OK, tekst, status="schatting")


# ------------------------------------------------------------------ ADR (regel 14)


def regel_adr(datum: date, containers: list[ContainerInvoer], trekker: TrekkerInvoer | None = None,
              chassis: ChassisInvoer | None = None, chauffeur=None) -> Uitslag | None:
    adr = [c for c in containers if c.is_adr]
    if not adr:
        return None
    tank = any(c.type == "tank" for c in adr)
    fouten = []
    if trekker is not None:
        nodig = ("tank",) if tank else ("basis", "tank")
        if trekker.adr_uitvoering not in nodig:
            fouten.append(f"{trekker.naam} heeft geen ADR-{'tank' if tank else 'uitvoering'}")
    if tank and chassis is not None and not chassis.adr_tank:
        fouten.append(f"{chassis.naam} is niet ADR/tank-geschikt")
    if chauffeur is not None:
        if not chauffeur.adr_basis_tot or chauffeur.adr_basis_tot < datum:
            fouten.append(f"chauffeur {chauffeur.pseudoniem} heeft geen geldig ADR-certificaat"
                          + (" (verlopen)" if chauffeur.adr_basis_tot else ""))
        elif tank and (not chauffeur.adr_tank_tot or chauffeur.adr_tank_tot < datum):
            fouten.append(f"chauffeur {chauffeur.pseudoniem} heeft geen geldig ADR-tank-certificaat")
    klassen = ", ".join(sorted({c.imo_klasse for c in adr}))
    if fouten:
        return Uitslag(14, "ADR", HARD, f"Niet toegestaan (ADR klasse {klassen}): " + "; ".join(fouten) + ".",
                       "ADR / docs/onderzoek.md h2.4", "bevestigd")
    return Uitslag(14, "ADR", OK, f"ADR klasse {klassen}: chauffeur en voertuig in orde. Controleer zelf de "
                   "tunnelcategorie van de route.", "ADR / docs/onderzoek.md h2.4", "bevestigd")


# ------------------------------------------------------------------ alles samen


def toets_combinatie(boek: RegelBoek, datum: date, trekker: TrekkerInvoer, chassis: ChassisInvoer,
                     containers: list[ContainerInvoer], route: str = "NL-intermodaal", chauffeur=None,
                     handelingen: list[str] | None = None) -> list[Uitslag]:
    uit = [regel_chassis_past(chassis, containers, handelingen)]
    r15 = regel_reefer(chassis, containers)
    if r15:
        uit.append(r15)
    uit.append(regel_gewicht(boek, datum, trekker, chassis, containers, route))
    uit.append(regel_aslast(boek, datum, trekker, chassis, containers))
    uit.append(regel_hoogte(boek, datum, chassis, containers))
    r14 = regel_adr(datum, containers, trekker, chassis, chauffeur)
    if r14:
        uit.append(r14)
    return uit


def geschikt_voor(trekker: TrekkerInvoer, chassis: ChassisInvoer) -> list[str]:
    """Welke containers kan deze combinatie rijden? Afgeleid uit chassis en trekker."""
    maten = [m for m, ok in (("20ft", chassis.twistlock_20), ("40ft", chassis.twistlock_40),
                             ("45ft", chassis.twistlock_45)) if ok]
    if chassis.twistlock_20 and chassis.type in ("multi", "uitschuifbaar 20-40-45"):
        maten.append("2x20ft")
    soorten = [s.strip() for s in chassis.geschikt_voor.split(",") if s.strip() and s.strip() != "reefer"]
    if chassis.genset != "niet":
        soorten.append("reefer (genset)")
    extra = []
    if chassis.adr_tank and trekker.adr_uitvoering == "tank":
        extra.append("ADR tank")
    elif trekker.adr_uitvoering in ("basis", "tank"):
        extra.append("ADR (geen tank)")
    if chassis.kiepfunctie:
        extra.append("kiepen")
    return [", ".join(maten), ", ".join(soorten)] + extra
