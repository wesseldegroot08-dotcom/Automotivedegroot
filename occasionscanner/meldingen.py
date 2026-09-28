"""Meldingen versturen via Telegram of e-mail."""

import smtplib
from email.message import EmailMessage

import requests

from .logboek import log
from .normaliseren import toon_kenteken


def euro(x):
    return f"€ {x:,.0f}".replace(",", ".")


def maak_bericht(r):
    a = r.auto
    regels = [
        "Nieuwe deal gevonden!",
        f"{a['merk']} {a['model']} {a.get('motor') or ''} {a.get('uitvoering') or ''}".strip(),
        f"{a['bouwjaar']} | {a['kilometerstand']:,} km | {a.get('locatie') or '?'}".replace(",", "."),
        "",
        f"Vraagprijs: {euro(a['vraagprijs'])}",
        f"Geschatte verkoop: {euro(r.verkoopprijs)}",
        f"Marge: {euro(r.marge)}",
        f"Winst na kosten: {euro(r.winst)}",
        f"Gebaseerd op {len(r.vergelijkbaar)} vergelijkbare auto's",
    ]
    if a.get("kenteken"):
        regels.append(f"Kenteken: {toon_kenteken(a['kenteken'])}")
    for ok, tekst in r.rdw:
        if not ok:
            regels.append(f"RDW let op: {tekst}")
    for vlag in r.rode_vlaggen:
        regels.append(f"Rode vlag: {vlag}")
    regels += ["", a.get("link") or ""]
    return "\n".join(regels)


def stuur_telegram(tekst, geheimen):
    t = geheimen.get("telegram", {})
    if not t.get("bot_token") or not t.get("chat_id"):
        raise ValueError("Telegram is niet ingesteld. Vul bot_token en chat_id in geheimen.toml in.")
    antwoord = requests.post(f"https://api.telegram.org/bot{t['bot_token']}/sendMessage",
                             data={"chat_id": t["chat_id"], "text": tekst, "disable_web_page_preview": "false"},
                             timeout=20)
    if not antwoord.ok:
        raise ConnectionError(f"Telegram gaf fout {antwoord.status_code}: {antwoord.text[:200]}")


def stuur_email(onderwerp, tekst, geheimen):
    m = geheimen.get("email", {})
    if not all(m.get(k) for k in ("smtp_server", "gebruiker", "wachtwoord", "naar")):
        raise ValueError("E-mail is niet ingesteld. Vul de gegevens in geheimen.toml in.")
    bericht = EmailMessage()
    bericht["Subject"] = onderwerp
    bericht["From"] = m["gebruiker"]
    bericht["To"] = m["naar"]
    bericht.set_content(tekst)
    with smtplib.SMTP(m["smtp_server"], int(m.get("poort", 587)), timeout=30) as server:
        server.starttls()
        server.login(m["gebruiker"], m["wachtwoord"])
        server.send_message(bericht)


def verstuur(tekst, onderwerp, inst, geheimen):
    """Stuurt een bericht via het gekozen kanaal. Geeft True terug als het gelukt is."""
    kanaal = inst["meldingen"]["kanaal"].lower()
    if kanaal == "geen":
        log.info("Melding (niet verstuurd, kanaal = geen):\n%s", tekst)
        return False
    try:
        if kanaal == "telegram":
            stuur_telegram(tekst, geheimen)
        elif kanaal == "email":
            stuur_email(onderwerp, tekst, geheimen)
        else:
            raise ValueError(f"Onbekend kanaal '{kanaal}'. Kies telegram, email of geen.")
    except Exception as fout:  # een mislukte melding mag de tool niet stoppen
        log.error("Melding versturen mislukt: %s", fout)
        return False
    return True


def verstuur_deal(r, inst, geheimen):
    a = r.auto
    onderwerp = f"Deal: {a['merk']} {a['model']} - winst {euro(r.winst)}"
    return verstuur(maak_bericht(r), onderwerp, inst, geheimen)
