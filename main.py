"""Occasion Winstradar - startbestand.

Gebruik (typ in de terminal, in deze map):
    python main.py start             zoek elke 30 minuten + open het dashboard
    python main.py zoek              doe één zoekronde en stop
    python main.py dashboard         alleen het dashboard openen
    python main.py link <url>        één advertentie doorrekenen (back-up)
    python main.py handmatig         zelf de gegevens van een auto invoeren
    python main.py test-melding      stuur een testbericht (Telegram/e-mail)
    python main.py test-marktplaats  kijk of Marktplaats nog werkt (haalt 1 pagina op)
    python main.py demo              bekijk het dashboard met verzonnen auto's
"""

import argparse
import sys
import threading
import webbrowser

if sys.version_info < (3, 11):
    sys.exit("Deze tool heeft Python 3.11 of nieuwer nodig. Zie de README.")

from winstradar import analyse, database, meldingen
from winstradar.advertentie import Advertentie
from winstradar.instellingen import DATA_MAP, laad_geheimen, laad_instellingen
from winstradar.logboek import maak_logboek
from winstradar.normaliseren import lees_getal, vul_aan
from winstradar.ophalen import NietToegestaan, SiteGeblokkeerd
from winstradar.zoeker import blijf_zoeken, maak_ophaler, zoekronde


def start_dashboard(inst, db_pad=None, open_browser=True, demo=False):
    from winstradar.dashboard.app import maak_app
    poort = inst["dashboard"]["poort"]
    adres = f"http://127.0.0.1:{poort}"
    print(f"\nDashboard: {adres}  (open deze link in je browser)\n")
    if open_browser:
        threading.Timer(1.5, lambda: webbrowser.open(adres)).start()
    # 127.0.0.1 = alleen jouw eigen laptop kan erbij, niet anderen op je wifi
    maak_app(inst, db_pad, demo).run(host="127.0.0.1", port=poort, debug=False, use_reloader=False)


def cmd_start(inst, geheimen):
    conn = database.verbind()
    threading.Thread(target=blijf_zoeken, args=(conn, inst, geheimen), daemon=True).start()
    start_dashboard(inst)


def cmd_link(inst, url):
    from winstradar.dashboard.app import reken_link_door
    conn = database.verbind()
    try:
        pk = reken_link_door(conn, maak_ophaler(inst), inst, url)
    except (ValueError, NietToegestaan, SiteGeblokkeerd, ConnectionError) as fout:
        sys.exit(f"Niet gelukt: {fout}")
    print()
    print(analyse.als_tekst(analyse.analyseer(conn, database.haal_auto(conn, pk), inst)))


def vraag(tekst, verplicht=True):
    while True:
        antwoord = input(f"{tekst}: ").strip()
        if antwoord or not verplicht:
            return antwoord or None
        print("  Dit is verplicht.")


def cmd_handmatig(inst):
    print("Vul de gegevens van de auto in. (Enter = leeg laten, als het niet verplicht is)\n")
    merk = vraag("Merk (bv. Volkswagen)")
    model = vraag("Model (bv. Polo)")
    motor = vraag("Motor (bv. 1.2 TSI)")
    transmissie = vraag("Transmissie (handgeschakeld/automaat)")
    brandstof = vraag("Brandstof (benzine/hybride)")
    bouwjaar = lees_getal(vraag("Bouwjaar"))
    km = lees_getal(vraag("Kilometerstand"))
    prijs = lees_getal(vraag("Vraagprijs"))
    kenteken = vraag("Kenteken (mag leeg)", verplicht=False)
    link = vraag("Link (mag leeg)", verplicht=False)
    tekst = vraag("Beschrijving (mag leeg)", verplicht=False) or ""

    adv = Advertentie(site="handmatig", advertentie_id=f"{merk}-{model}-{bouwjaar}-{km}-{prijs}", link=link or "",
                      titel=f"{merk} {model} {motor}", beschrijving=tekst, beschrijving_volledig=bool(tekst),
                      transmissie=transmissie, brandstof=brandstof, bouwjaar=bouwjaar,
                      kilometerstand=km, vraagprijs=prijs, kenteken=kenteken)
    vul_aan(adv, merk, model)
    conn = database.verbind()
    pk, _ = database.sla_op(conn, adv)
    if adv.kenteken and inst["rdw"]["aan"]:
        from winstradar import rdw
        try:
            database.sla_rdw_op(conn, pk, rdw.haal_op(maak_ophaler(inst), adv.kenteken))
        except (ConnectionError, SiteGeblokkeerd) as fout:
            print(f"RDW-controle niet gelukt: {fout}")
    print()
    print(analyse.als_tekst(analyse.analyseer(conn, database.haal_auto(conn, pk), inst)))


def cmd_test_melding(inst, geheimen):
    if inst["meldingen"]["kanaal"] == "geen":
        sys.exit("Kanaal staat op 'geen'. Zet kanaal op 'telegram' of 'email' in instellingen.toml.")
    gelukt = meldingen.verstuur("Testbericht van Occasion Winstradar. Meldingen werken!",
                                "Test Occasion Winstradar", inst, geheimen)
    print("Gelukt! Kijk op je telefoon of in je mail." if gelukt else "Niet gelukt. Kijk in logs/winstradar.log.")


def cmd_test_marktplaats(inst):
    from winstradar.sites.marktplaats import Marktplaats
    site = Marktplaats(maak_ophaler(inst), inst)
    m = inst["zoeken"]["modellen"][0]
    print(f"Test: één pagina zoeken naar {m['merk']} {m['model']} (duurt ongeveer 10 seconden)...")
    try:
        gevonden = list(site.zoek(m["merk"], m["model"], 1, lambda _id: False))
    except NietToegestaan as fout:
        sys.exit(f"robots.txt staat het niet toe: {fout}\nDeze module mag dus niet gebruikt worden.")
    except SiteGeblokkeerd as fout:
        sys.exit(f"Marktplaats blokkeert: {fout}")
    except ConnectionError as fout:
        sys.exit(f"Verbindingsprobleem: {fout}")
    print(f"{len(gevonden)} advertenties gevonden.")
    for adv in gevonden[:5]:
        vul_aan(adv, m["merk"], m["model"])
        print(f"  {adv.vraagprijs} euro | {adv.bouwjaar} | {adv.kilometerstand} km | "
              f"motor {adv.motor_sleutel} | {adv.transmissie} | {adv.titel[:50]}")
    if not gevonden:
        print("Geen advertenties. Waarschijnlijk is de website veranderd. Laat het mij weten.")


def main():
    parser = argparse.ArgumentParser(description="Occasion Winstradar")
    parser.add_argument("opdracht", choices=["start", "zoek", "dashboard", "link", "handmatig",
                                             "test-melding", "test-marktplaats", "demo"])
    parser.add_argument("url", nargs="?", help="alleen bij 'link'")
    args = parser.parse_args()

    maak_logboek()
    inst = laad_instellingen()
    geheimen = laad_geheimen()

    try:
        if args.opdracht == "start":
            cmd_start(inst, geheimen)
        elif args.opdracht == "zoek":
            zoekronde(database.verbind(), inst, geheimen)
        elif args.opdracht == "dashboard":
            start_dashboard(inst)
        elif args.opdracht == "link":
            if not args.url:
                sys.exit("Geef een link mee, bv: python main.py link https://www.marktplaats.nl/v/...")
            cmd_link(inst, args.url)
        elif args.opdracht == "handmatig":
            cmd_handmatig(inst)
        elif args.opdracht == "test-melding":
            cmd_test_melding(inst, geheimen)
        elif args.opdracht == "test-marktplaats":
            cmd_test_marktplaats(inst)
        elif args.opdracht == "demo":
            from winstradar.demo import vul_demo
            DATA_MAP.mkdir(exist_ok=True)
            vul_demo(DATA_MAP / "demo.db")
            start_dashboard(inst, DATA_MAP / "demo.db", demo=True)
    except KeyboardInterrupt:
        print("\nGestopt.")


if __name__ == "__main__":
    main()
