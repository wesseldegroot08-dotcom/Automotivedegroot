"""Eén zoekronde: alle sites langs, opslaan, doorrekenen en meldingen sturen."""

import time
from datetime import datetime, timedelta

from . import analyse, database, meldingen, rdw
from .logboek import log
from .normaliseren import vul_aan
from .ophalen import NetteOphaler, NietToegestaan, SiteGeblokkeerd
from .sites import actieve_sites

MAX_RDW_PER_RONDE = 30


def maak_ophaler(inst):
    v = inst["verzoeken"]
    return NetteOphaler(v["user_agent"], v["wachttijd_seconden"])


def _zoek_op_site(conn, site, inst):
    z = inst["zoeken"]
    eerste_keer = conn.execute("SELECT COUNT(*) FROM advertenties WHERE site=?", (site.naam,)).fetchone()[0] == 0
    max_paginas = z["max_paginas_eerste_keer"] if eerste_keer else z["max_paginas_daarna"]
    teller = {"gezien": 0, "nieuw": 0, "prijs": 0}

    for m in z["modellen"]:
        merk, model = m["merk"], m["model"]
        try:
            for adv in site.zoek(merk, model, max_paginas,
                                 lambda ad_id: database.is_bekend(conn, site.naam, ad_id)):
                vul_aan(adv, merk, model)
                pk, status = database.sla_op(conn, adv)
                teller["gezien"] += 1
                if status == "prijs_gewijzigd":
                    teller["prijs"] += 1
                if status == "nieuw":
                    teller["nieuw"] += 1
                    # Alleen voor auto's binnen je criteria de hele advertentie ophalen
                    if database.voldoet_aan_criteria(database.haal_auto(conn, pk), inst):
                        try:
                            vul_aan(site.haal_details(adv), merk, model)
                            database.sla_op(conn, adv)
                        except NietToegestaan as fout:
                            log.info("%s: advertentiepagina niet opgehaald (%s)", site.naam, fout)
        except ConnectionError as fout:
            log.warning("%s: probleem bij %s %s (%s). Door naar het volgende model.", site.naam, merk, model, fout)
    return teller


def _rdw_controles(conn, ophaler, inst):
    if not inst["rdw"]["aan"]:
        return
    grens = (datetime.now() - timedelta(days=7)).isoformat(timespec="seconds")
    te_doen = [a for a in database.doelautos(conn, inst)
               if a["kenteken"] and (a["rdw_opgehaald"] is None or a["rdw_opgehaald"] < grens)]
    for a in te_doen[:MAX_RDW_PER_RONDE]:
        try:
            database.sla_rdw_op(conn, a["id"], rdw.haal_op(ophaler, a["kenteken"]))
        except (ConnectionError, SiteGeblokkeerd) as fout:
            log.warning("RDW: kon %s niet controleren (%s)", a["kenteken"], fout)
            break


def _stuur_meldingen(conn, inst, geheimen):
    aantal = 0
    for r in analyse.analyseer_alle(conn, inst):
        if not r.is_deal:
            continue
        vorige = r.auto.get("melding_bij_prijs")
        # Nog nooit gemeld, of de prijs is sinds de vorige melding gezakt
        if vorige is None or r.auto["vraagprijs"] < vorige:
            if meldingen.verstuur_deal(r, inst, geheimen):
                aantal += 1
            # Ook bij kanaal "geen" markeren, anders komt hij elke ronde terug in het logboek
            database.markeer_melding(conn, r.auto["id"], r.auto["vraagprijs"])
    return aantal


def zoekronde(conn, inst, geheimen, ophaler=None):
    ophaler = ophaler or maak_ophaler(inst)
    log.info("=== Zoekronde gestart ===")
    for site in actieve_sites(ophaler, inst):
        tot = database.site_geblokkeerd_tot(conn, site.naam)
        if tot:
            log.info("%s: overgeslagen, geblokkeerd tot %s", site.naam, tot)
            continue
        try:
            t = _zoek_op_site(conn, site, inst)
            log.info("%s: %d advertenties gezien, %d nieuw, %d prijswijzigingen",
                     site.naam, t["gezien"], t["nieuw"], t["prijs"])
        except SiteGeblokkeerd as fout:
            tot = database.blokkeer_site(conn, site.naam, inst["verzoeken"]["blokkade_pauze_uren"], str(fout))
            log.error("%s BLOKKEERT ons: %s. Gestopt met deze site tot %s. Andere sites gaan door.",
                      site.naam, fout, tot)
        except NietToegestaan as fout:
            log.error("%s: %s. Deze module haalt niets op. Zet hem uit in instellingen.toml.", site.naam, fout)
        except Exception as fout:  # een fout in één site mag de rest niet stoppen
            log.exception("%s: onverwachte fout: %s", site.naam, fout)

    _rdw_controles(conn, ophaler, inst)
    aantal = _stuur_meldingen(conn, inst, geheimen)
    log.info("=== Zoekronde klaar. %d nieuwe meldingen. ===", aantal)


def blijf_zoeken(conn, inst, geheimen):
    ophaler = maak_ophaler(inst)
    minuten = inst["zoeken"]["interval_minuten"]
    while True:
        begin = time.monotonic()
        try:
            zoekronde(conn, inst, geheimen, ophaler)
        except Exception as fout:
            log.exception("Zoekronde mislukt: %s", fout)
        rust = max(60, minuten * 60 - (time.monotonic() - begin))
        volgende = datetime.now() + timedelta(seconds=rust)
        log.info("Volgende zoekronde om %s. Stoppen? Druk op Ctrl+C.", volgende.strftime("%H:%M"))
        time.sleep(rust)
