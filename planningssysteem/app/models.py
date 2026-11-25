"""Alle tabellen van de database.

Afspraken:
- Gewichten in hele kg (int).
- Geld in hele centen (int).
- Tijden in UTC (UTCDatumTijd). Datums zonder tijd zijn gewone Date.
- Regels zijn data: ze hebben geldig_van, geldig_tot, bron en status.
- Een waarde die we niet zeker weten krijgt een 'aanname'-vlag.
"""

from datetime import date, datetime, time

from sqlalchemy import Boolean, Date, ForeignKey, Integer, String, Text, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, declared_attr, mapped_column, relationship

from app.db import Base, UTCDatumTijd, nu_utc

# ---------------------------------------------------------------- hulpstukken


class RegelData:
    """Velden die elke regel heeft: wanneer geldig, waar komt het vandaan, hoe zeker."""

    geldig_van: Mapped[date] = mapped_column(Date, nullable=False)
    geldig_tot: Mapped[date | None] = mapped_column(Date)
    bron: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)  # bevestigd / schatting / open


class Tijdstempels:
    @declared_attr
    def aangemaakt(cls) -> Mapped[datetime]:
        return mapped_column(UTCDatumTijd, default=nu_utc, nullable=False)


# ---------------------------------------------------------------- gebruikers en logboek


class Gebruiker(Base, Tijdstempels):
    __tablename__ = "gebruiker"
    id: Mapped[int] = mapped_column(primary_key=True)
    gebruikersnaam: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    wachtwoord_hash: Mapped[str] = mapped_column(String(200), nullable=False)
    rol: Mapped[str] = mapped_column(String(20), nullable=False)
    actief: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    chauffeur_id: Mapped[int | None] = mapped_column(ForeignKey("chauffeur.id"))


class InlogPoging(Base):
    __tablename__ = "inlog_poging"
    id: Mapped[int] = mapped_column(primary_key=True)
    gebruikersnaam: Mapped[str] = mapped_column(String(50), nullable=False)
    ip: Mapped[str] = mapped_column(String(64), nullable=False)
    tijd: Mapped[datetime] = mapped_column(UTCDatumTijd, default=nu_utc, nullable=False)
    gelukt: Mapped[bool] = mapped_column(Boolean, nullable=False)


class AuditLog(Base):
    """Logboek. Mag via de app nooit gewijzigd of verwijderd worden (zie app/audit.py)."""

    __tablename__ = "audit_log"
    id: Mapped[int] = mapped_column(primary_key=True)
    tijd: Mapped[datetime] = mapped_column(UTCDatumTijd, default=nu_utc, nullable=False)
    gebruiker: Mapped[str] = mapped_column(String(50), nullable=False)
    actie: Mapped[str] = mapped_column(String(30), nullable=False)
    tabel: Mapped[str] = mapped_column(String(50), nullable=False, default="")
    record_id: Mapped[str] = mapped_column(String(50), nullable=False, default="")
    voor: Mapped[str | None] = mapped_column(Text)
    na: Mapped[str | None] = mapped_column(Text)
    reden_code: Mapped[str | None] = mapped_column(String(30))
    reden: Mapped[str | None] = mapped_column(Text)


class Instelling(Base):
    """Losse instellingen, zoals de noodstop of een ingangsdatum."""

    __tablename__ = "instelling"
    sleutel: Mapped[str] = mapped_column(String(80), primary_key=True)
    waarde: Mapped[str] = mapped_column(Text, nullable=False)
    omschrijving: Mapped[str] = mapped_column(Text, nullable=False, default="")
    bron: Mapped[str] = mapped_column(Text, nullable=False, default="")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="bevestigd")


# ---------------------------------------------------------------- regels als data


class Regel(Base, RegelData):
    """Eén getal-regel, bijvoorbeeld 'max gewicht intermodaal 3-assig = 44000 kg'.

    De code bepaalt welke regel het is. De waarde staat in 'eenheid'.
    Voorbeelden van eenheden: kg, mm, minuten, cent, '0,1 ct/km', procent.
    """

    __tablename__ = "regel"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    categorie: Mapped[str] = mapped_column(String(40), nullable=False)
    omschrijving: Mapped[str] = mapped_column(Text, nullable=False)
    waarde: Mapped[int | None] = mapped_column(Integer)
    eenheid: Mapped[str] = mapped_column(String(30), nullable=False, default="")
    land: Mapped[str | None] = mapped_column(String(5))
    in_gebruik: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    opmerking: Mapped[str | None] = mapped_column(Text)


class Feestdag(Base, RegelData):
    __tablename__ = "feestdag"
    id: Mapped[int] = mapped_column(primary_key=True)
    land: Mapped[str] = mapped_column(String(5), nullable=False)
    deelstaat: Mapped[str | None] = mapped_column(String(10))
    datum: Mapped[date] = mapped_column(Date, nullable=False)
    naam: Mapped[str] = mapped_column(String(100), nullable=False)
    rijverbod: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class TerminalRegel(Base, RegelData):
    """Slotregels per terminal of depot."""

    __tablename__ = "terminal_regel"
    id: Mapped[int] = mapped_column(primary_key=True)
    locatie_id: Mapped[int] = mapped_column(ForeignKey("locatie.id"), nullable=False)
    slotsysteem: Mapped[str] = mapped_column(String(30), nullable=False)
    slotlengte_min: Mapped[int | None] = mapped_column(Integer)
    tolerantie_min: Mapped[int | None] = mapped_column(Integer)
    capaciteit_per_slot: Mapped[int | None] = mapped_column(Integer)
    tar_verplicht: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    cargo_closing_uren: Mapped[int | None] = mapped_column(Integer)
    no_show_kosten_cent: Mapped[int | None] = mapped_column(Integer)
    no_show_heffing_vanaf: Mapped[date | None] = mapped_column(Date)
    piektoeslag_cent: Mapped[int | None] = mapped_column(Integer)
    lege_container_regels: Mapped[str | None] = mapped_column(Text)
    opmerking: Mapped[str | None] = mapped_column(Text)

    locatie = relationship("Locatie")


class DDTarief(Base, RegelData):
    """Demurrage of detention per rederij (voorbeeldtarieven)."""

    __tablename__ = "dd_tarief"
    id: Mapped[int] = mapped_column(primary_key=True)
    rederij_id: Mapped[int] = mapped_column(ForeignKey("rederij.id"), nullable=False)
    soort: Mapped[str] = mapped_column(String(20), nullable=False)
    container_maat: Mapped[str] = mapped_column(String(5), nullable=False)
    container_type: Mapped[str] = mapped_column(String(10), nullable=False)
    vrije_dagen: Mapped[int] = mapped_column(Integer, nullable=False)
    dag_van: Mapped[int] = mapped_column(Integer, nullable=False)  # dag 1 = eerste dag (bijv. dag 5-8)
    dag_tot: Mapped[int | None] = mapped_column(Integer)  # leeg = en verder
    bedrag_per_dag_cent: Mapped[int] = mapped_column(Integer, nullable=False)

    rederij = relationship("Rederij")


class Tariefregel(Base, RegelData):
    """Verkooptarief voor de factuur (verzonnen demowaarden)."""

    __tablename__ = "tariefregel"
    id: Mapped[int] = mapped_column(primary_key=True)
    klant_id: Mapped[int | None] = mapped_column(ForeignKey("klant.id"))
    order_type: Mapped[str | None] = mapped_column(String(10))
    container_maat: Mapped[str | None] = mapped_column(String(5))
    basisprijs_cent: Mapped[int] = mapped_column(Integer, nullable=False)
    wachttijd_vrij_min: Mapped[int] = mapped_column(Integer, default=120, nullable=False)
    wachttijd_per_half_uur_cent: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    adr_toeslag_cent: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    reefer_toeslag_cent: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    handeling_per_uur_cent: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


# ---------------------------------------------------------------- stamdata


class Klant(Base, Tijdstempels):
    __tablename__ = "klant"
    id: Mapped[int] = mapped_column(primary_key=True)
    naam: Mapped[str] = mapped_column(String(100), nullable=False)
    factuuradres: Mapped[str | None] = mapped_column(Text)
    betaaltermijn_dagen: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    contactpersoon: Mapped[str | None] = mapped_column(String(100))
    email: Mapped[str | None] = mapped_column(String(100))
    opmerking: Mapped[str | None] = mapped_column(Text)
    actief: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class Locatie(Base, Tijdstempels):
    __tablename__ = "locatie"
    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    naam: Mapped[str] = mapped_column(String(100), nullable=False)
    lat: Mapped[float] = mapped_column(nullable=False)
    lon: Mapped[float] = mapped_column(nullable=False)
    land: Mapped[str] = mapped_column(String(5), nullable=False, default="NL")
    open_van: Mapped[time] = mapped_column(Time, nullable=False)
    open_tot: Mapped[time] = mapped_column(Time, nullable=False)
    open_dagen: Mapped[str] = mapped_column(String(7), nullable=False, default="12345")  # 1=ma ... 7=zo
    laad_los_min: Mapped[int] = mapped_column(Integer, nullable=False)
    laad_los_is_aanname: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    live_of_drop: Mapped[str] = mapped_column(String(10), nullable=False, default="live")
    max_gewicht_kg: Mapped[int | None] = mapped_column(Integer)
    max_hoogte_mm: Mapped[int | None] = mapped_column(Integer)
    adr_toegestaan: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    reefer_stroom: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    terminalcode: Mapped[str | None] = mapped_column(String(20))
    klant_id: Mapped[int | None] = mapped_column(ForeignKey("klant.id"))
    actief: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class Rederij(Base, Tijdstempels):
    __tablename__ = "rederij"
    id: Mapped[int] = mapped_column(primary_key=True)
    naam: Mapped[str] = mapped_column(String(100), nullable=False)
    scac: Mapped[str] = mapped_column(String(4), nullable=False)
    retourregels: Mapped[str | None] = mapped_column(Text)
    actief: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class Chauffeur(Base, Tijdstempels):
    """Alleen pseudoniemen. Geen echte persoonsgegevens, geen GPS."""

    __tablename__ = "chauffeur"
    id: Mapped[int] = mapped_column(primary_key=True)
    pseudoniem: Mapped[str] = mapped_column(String(50), nullable=False)
    contracturen_week: Mapped[int] = mapped_column(Integer, nullable=False)
    ce_geldig_tot: Mapped[date | None] = mapped_column(Date)
    code95_geldig_tot: Mapped[date | None] = mapped_column(Date)
    adr_basis_tot: Mapped[date | None] = mapped_column(Date)
    adr_tank_tot: Mapped[date | None] = mapped_column(Date)
    ccv_lzv: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    ect_test_tot: Mapped[date | None] = mapped_column(Date)
    cargocard_tot: Mapped[date | None] = mapped_column(Date)
    standaard_begin: Mapped[time] = mapped_column(Time, nullable=False, default=time(6, 0))
    standaard_eind: Mapped[time] = mapped_column(Time, nullable=False, default=time(17, 0))
    voorkeur_regio: Mapped[str | None] = mapped_column(String(100))
    voorkeur_trekker_id: Mapped[int | None] = mapped_column(ForeignKey("trekker.id"))
    opmerking: Mapped[str | None] = mapped_column(Text)
    actief: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class Afwezigheid(Base):
    """Verlof of niet beschikbaar: voor een chauffeur, trekker of chassis."""

    __tablename__ = "afwezigheid"
    id: Mapped[int] = mapped_column(primary_key=True)
    chauffeur_id: Mapped[int | None] = mapped_column(ForeignKey("chauffeur.id"))
    trekker_id: Mapped[int | None] = mapped_column(ForeignKey("trekker.id"))
    chassis_id: Mapped[int | None] = mapped_column(ForeignKey("chassis.id"))
    van: Mapped[date] = mapped_column(Date, nullable=False)
    tot: Mapped[date] = mapped_column(Date, nullable=False)
    reden: Mapped[str] = mapped_column(String(100), nullable=False)


class RijtijdRegistratie(Base):
    """Rij- en werktijd per dag (nu handmatig of demo; later uit de tachograaf)."""

    __tablename__ = "rijtijd_registratie"
    __table_args__ = (UniqueConstraint("chauffeur_id", "datum"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    chauffeur_id: Mapped[int] = mapped_column(ForeignKey("chauffeur.id"), nullable=False)
    datum: Mapped[date] = mapped_column(Date, nullable=False)
    rijtijd_min: Mapped[int] = mapped_column(Integer, nullable=False)
    werktijd_min: Mapped[int] = mapped_column(Integer, nullable=False)
    bron: Mapped[str] = mapped_column(String(30), nullable=False, default="handmatig")


# ---------------------------------------------------------------- voertuigen


class Trekker(Base, Tijdstempels):
    __tablename__ = "trekker"
    id: Mapped[int] = mapped_column(primary_key=True)
    kenteken: Mapped[str] = mapped_column(String(12), unique=True, nullable=False)
    intern_nummer: Mapped[str] = mapped_column(String(20), nullable=False)
    merk_model: Mapped[str | None] = mapped_column(String(100))
    bouwjaar: Mapped[int | None] = mapped_column(Integer)
    aandrijving: Mapped[str] = mapped_column(String(5), nullable=False)
    tarra_kg: Mapped[int | None] = mapped_column(Integer)
    tarra_bron: Mapped[str] = mapped_column(String(20), nullable=False)
    toegestane_massa_kg: Mapped[int | None] = mapped_column(Integer)
    max_aandrijfas_kg: Mapped[int | None] = mapped_column(Integer)
    max_koppelplaat_kg: Mapped[int | None] = mapped_column(Integer)
    euro_klasse: Mapped[str | None] = mapped_column(String(10))
    co2_klasse: Mapped[int | None] = mapped_column(Integer)
    zero_emissie: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    adr_uitvoering: Mapped[str] = mapped_column(String(10), default="geen", nullable=False)
    lzv_geschikt: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    lzv_ontheffing_tot: Mapped[date | None] = mapped_column(Date)
    tolkastje: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    apk_datum: Mapped[date | None] = mapped_column(Date)
    onderhoud_datum: Mapped[date | None] = mapped_column(Date)
    tachograaf_ijking: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(20), default="actief", nullable=False)
    standplaats_id: Mapped[int | None] = mapped_column(ForeignKey("locatie.id"))
    opmerking: Mapped[str | None] = mapped_column(Text)
    # voorkeuren die één waarde hebben
    begin_tijd: Mapped[time | None] = mapped_column(Time)
    eind_tijd: Mapped[time | None] = mapped_column(Time)
    max_km_dag: Mapped[int | None] = mapped_column(Integer)
    kosten_per_km_cent: Mapped[int | None] = mapped_column(Integer)
    kosten_per_uur_cent: Mapped[int | None] = mapped_column(Integer)
    verbruik_l_per_100km: Mapped[int | None] = mapped_column(Integer)
    vaste_chassis_id: Mapped[int | None] = mapped_column(ForeignKey("chassis.id"))
    gearchiveerd: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class Chassis(Base, Tijdstempels):
    __tablename__ = "chassis"
    id: Mapped[int] = mapped_column(primary_key=True)
    nummer: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    type: Mapped[str] = mapped_column(String(30), nullable=False)
    assen: Mapped[int] = mapped_column(Integer, nullable=False)
    tarra_kg: Mapped[int | None] = mapped_column(Integer)
    tarra_bron: Mapped[str] = mapped_column(String(20), nullable=False)
    max_kingpin_kg: Mapped[int | None] = mapped_column(Integer)
    max_asgroep_kg: Mapped[int | None] = mapped_column(Integer)
    kingpinhoogte_mm: Mapped[int | None] = mapped_column(Integer)
    lengte_in_mm: Mapped[int | None] = mapped_column(Integer)
    lengte_uit_mm: Mapped[int | None] = mapped_column(Integer)
    twistlock_20: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    twistlock_40: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    twistlock_45: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    liftas: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    genset: Mapped[str] = mapped_column(String(15), default="niet", nullable=False)
    geschikt_voor: Mapped[str] = mapped_column(String(100), default="dry,HC", nullable=False)
    max_bruto_container_kg: Mapped[int | None] = mapped_column(Integer)
    adr_tank: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    kiepfunctie: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    eigen_of_pool: Mapped[str] = mapped_column(String(10), default="eigen", nullable=False)
    keuring_datum: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(20), default="actief", nullable=False)
    opmerking: Mapped[str | None] = mapped_column(Text)
    gearchiveerd: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class VoertuigVoorkeur(Base):
    """Zachte wens voor de solver. Gewicht 0 (negeren) tot 10 (zeer belangrijk)."""

    __tablename__ = "voertuig_voorkeur"
    id: Mapped[int] = mapped_column(primary_key=True)
    trekker_id: Mapped[int | None] = mapped_column(ForeignKey("trekker.id"))
    chassis_id: Mapped[int | None] = mapped_column(ForeignKey("chassis.id"))
    soort: Mapped[str] = mapped_column(String(30), nullable=False)
    waarde: Mapped[str] = mapped_column(String(100), nullable=False)
    gewicht: Mapped[int] = mapped_column(Integer, nullable=False)


# ---------------------------------------------------------------- orders en containers


class Order(Base, Tijdstempels):
    __tablename__ = "order_"
    id: Mapped[int] = mapped_column(primary_key=True)
    klant_id: Mapped[int] = mapped_column(ForeignKey("klant.id"), nullable=False)
    klantreferentie: Mapped[str] = mapped_column(String(50), nullable=False)
    type: Mapped[str] = mapped_column(String(10), nullable=False)
    boeking_bl: Mapped[str] = mapped_column(String(50), nullable=False)
    venster_van: Mapped[datetime] = mapped_column(UTCDatumTijd, nullable=False)
    venster_tot: Mapped[datetime] = mapped_column(UTCDatumTijd, nullable=False)
    van_locatie_id: Mapped[int] = mapped_column(ForeignKey("locatie.id"), nullable=False)
    naar_locatie_id: Mapped[int] = mapped_column(ForeignKey("locatie.id"), nullable=False)
    retour_locatie_id: Mapped[int | None] = mapped_column(ForeignKey("locatie.id"))
    status: Mapped[str] = mapped_column(String(30), default="Nieuw", nullable=False)
    land_route: Mapped[str] = mapped_column(String(30), default="NL", nullable=False)
    gecombineerd_vervoer: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    opmerkingen: Mapped[str | None] = mapped_column(Text)

    klant = relationship("Klant")
    van_locatie = relationship("Locatie", foreign_keys=[van_locatie_id])
    naar_locatie = relationship("Locatie", foreign_keys=[naar_locatie_id])
    containers = relationship("Container", back_populates="order")
    handelingen = relationship("OrderHandeling", back_populates="order")


class OrderHandeling(Base):
    __tablename__ = "order_handeling"
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("order_.id"), nullable=False)
    soort: Mapped[str] = mapped_column(String(30), nullable=False)
    duur_min: Mapped[int] = mapped_column(Integer, nullable=False)
    duur_is_aanname: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    order = relationship("Order", back_populates="handelingen")


class Container(Base, Tijdstempels):
    __tablename__ = "container"
    id: Mapped[int] = mapped_column(primary_key=True)
    nummer: Mapped[str] = mapped_column(String(11), nullable=False)
    rederij_id: Mapped[int] = mapped_column(ForeignKey("rederij.id"), nullable=False)
    order_id: Mapped[int | None] = mapped_column(ForeignKey("order_.id"))
    maat: Mapped[str] = mapped_column(String(5), nullable=False)
    type: Mapped[str] = mapped_column(String(10), nullable=False)
    tarra_kg: Mapped[int | None] = mapped_column(Integer)
    tarra_is_aanname: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    bruto_kg: Mapped[int | None] = mapped_column(Integer)
    vgm_kg: Mapped[int] = mapped_column(Integer, nullable=False)
    imo_klasse: Mapped[str | None] = mapped_column(String(10))
    un_nummer: Mapped[str | None] = mapped_column(String(10))
    reefer_setpoint: Mapped[str | None] = mapped_column(String(10))
    status: Mapped[str] = mapped_column(String(30), default="Aangekondigd", nullable=False)

    order = relationship("Order", back_populates="containers")
    rederij = relationship("Rederij")


class Vrijgave(Base):
    __tablename__ = "vrijgave"
    id: Mapped[int] = mapped_column(primary_key=True)
    container_id: Mapped[int] = mapped_column(ForeignKey("container.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="Onbekend", nullable=False)
    commercieel: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    douane: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    inspectie_vrij: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    terminal_status: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    ontlaaddatum: Mapped[date] = mapped_column(Date, nullable=False)
    lfd: Mapped[date] = mapped_column(Date, nullable=False)
    bron: Mapped[str] = mapped_column(String(100), nullable=False, default="handmatig door planner")
    tijdstip: Mapped[datetime] = mapped_column(UTCDatumTijd, default=nu_utc, nullable=False)

    container = relationship("Container")


# ---------------------------------------------------------------- ritten


class Rit(Base, Tijdstempels):
    __tablename__ = "rit"
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("order_.id"), nullable=False)
    container_id: Mapped[int | None] = mapped_column(ForeignKey("container.id"))
    volgnr: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    van_locatie_id: Mapped[int] = mapped_column(ForeignKey("locatie.id"), nullable=False)
    naar_locatie_id: Mapped[int] = mapped_column(ForeignKey("locatie.id"), nullable=False)
    gepland_start: Mapped[datetime | None] = mapped_column(UTCDatumTijd)
    gepland_eind: Mapped[datetime | None] = mapped_column(UTCDatumTijd)
    trekker_id: Mapped[int | None] = mapped_column(ForeignKey("trekker.id"))
    chassis_id: Mapped[int | None] = mapped_column(ForeignKey("chassis.id"))
    chauffeur_id: Mapped[int | None] = mapped_column(ForeignKey("chauffeur.id"))
    status: Mapped[str] = mapped_column(String(30), default="Concept", nullable=False)
    vastheid: Mapped[str] = mapped_column(String(15), default="open", nullable=False)
    geplande_km: Mapped[int | None] = mapped_column(Integer)
    werkelijke_km: Mapped[int | None] = mapped_column(Integer)
    gepubliceerd: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    order = relationship("Order")
    container = relationship("Container")
    van_locatie = relationship("Locatie", foreign_keys=[van_locatie_id])
    naar_locatie = relationship("Locatie", foreign_keys=[naar_locatie_id])
    trekker = relationship("Trekker")
    chassis = relationship("Chassis")
    chauffeur = relationship("Chauffeur")
    stops = relationship("Stop", back_populates="rit", order_by="Stop.volgnr")


class Stop(Base):
    __tablename__ = "stop"
    id: Mapped[int] = mapped_column(primary_key=True)
    rit_id: Mapped[int] = mapped_column(ForeignKey("rit.id"), nullable=False)
    volgnr: Mapped[int] = mapped_column(Integer, nullable=False)
    locatie_id: Mapped[int] = mapped_column(ForeignKey("locatie.id"), nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    chassis_id: Mapped[int | None] = mapped_column(ForeignKey("chassis.id"))  # drop-and-hook
    gepland_aankomst: Mapped[datetime | None] = mapped_column(UTCDatumTijd)
    gepland_vertrek: Mapped[datetime | None] = mapped_column(UTCDatumTijd)
    werkelijk_aankomst: Mapped[datetime | None] = mapped_column(UTCDatumTijd)
    werkelijk_vertrek: Mapped[datetime | None] = mapped_column(UTCDatumTijd)
    wachttijd_min: Mapped[int | None] = mapped_column(Integer)

    rit = relationship("Rit", back_populates="stops")
    locatie = relationship("Locatie")


class Slot(Base, Tijdstempels):
    __tablename__ = "slot"
    id: Mapped[int] = mapped_column(primary_key=True)
    rit_id: Mapped[int | None] = mapped_column(ForeignKey("rit.id"))
    terminal_id: Mapped[int] = mapped_column(ForeignKey("locatie.id"), nullable=False)
    handlingtype: Mapped[str] = mapped_column(String(20), nullable=False, default="ophalen")
    slot_van: Mapped[datetime | None] = mapped_column(UTCDatumTijd)
    slot_tot: Mapped[datetime | None] = mapped_column(UTCDatumTijd)
    tar: Mapped[str | None] = mapped_column(String(30))
    label: Mapped[str | None] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(20), default="Aangevraagd", nullable=False)
    afwijzingscode: Mapped[str | None] = mapped_column(String(10))

    terminal = relationship("Locatie")


# ---------------------------------------------------------------- mijlpaal 3: reistijden en overrides


class Reistijd(Base):
    """Vaste reistijd tussen twee locaties. De planner kan deze aanpassen."""

    __tablename__ = "reistijd"
    __table_args__ = (UniqueConstraint("van_locatie_id", "naar_locatie_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    van_locatie_id: Mapped[int] = mapped_column(ForeignKey("locatie.id"), nullable=False)
    naar_locatie_id: Mapped[int] = mapped_column(ForeignKey("locatie.id"), nullable=False)
    minuten: Mapped[int] = mapped_column(Integer, nullable=False)
    km: Mapped[int] = mapped_column(Integer, nullable=False)
    km_buitenland: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    land_buitenland: Mapped[str | None] = mapped_column(String(5))
    is_aanname: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    bron: Mapped[str] = mapped_column(String(100), nullable=False, default="aanname")


class Override(Base):
    """De planner gaat bewust door ondanks een regel. Altijd met redencode en uitleg."""

    __tablename__ = "override"
    id: Mapped[int] = mapped_column(primary_key=True)
    rit_id: Mapped[int] = mapped_column(ForeignKey("rit.id"), nullable=False)
    regel_nr: Mapped[int] = mapped_column(Integer, nullable=False)
    niveau: Mapped[str] = mapped_column(String(20), nullable=False)
    uitleg_regel: Mapped[str] = mapped_column(Text, nullable=False)
    reden_code: Mapped[str] = mapped_column(String(30), nullable=False)
    reden: Mapped[str] = mapped_column(Text, nullable=False)
    gebruiker: Mapped[str] = mapped_column(String(50), nullable=False)
    tijd: Mapped[datetime] = mapped_column(UTCDatumTijd, default=nu_utc, nullable=False)
    actief: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
