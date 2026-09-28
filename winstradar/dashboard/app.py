"""Het dashboard: een webpagina op je eigen laptop (http://127.0.0.1:5000)."""

import json

from flask import Flask, abort, g, redirect, render_template, request, url_for

from .. import analyse, database, rdw
from ..logboek import log
from ..normaliseren import toon_kenteken, vul_aan
from ..ophalen import NietToegestaan, SiteGeblokkeerd
from ..sites import site_voor_link
from ..zoeker import maak_ophaler


def euro(x, decimalen=0):
    if x is None:
        return "–"
    tekst = f"{x:,.{decimalen}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"€ {tekst}"


def getal(x):
    return "onbekend" if x is None else f"{x:,}".replace(",", ".")


def maak_app(inst, db_pad=None):
    app = Flask(__name__)
    app.jinja_env.filters.update(euro=euro, getal=getal, kenteken=toon_kenteken)
    ophaler = maak_ophaler(inst)

    def db():
        if "conn" not in g:
            g.conn = database.verbind(db_pad)
        return g.conn

    @app.teardown_appcontext
    def sluit_db(_fout):
        conn = g.pop("conn", None)
        if conn is not None:
            conn.close()

    @app.route("/")
    def overzicht():
        conn = db()
        resultaten = analyse.analyseer_alle(conn, inst)
        modellen = sorted({f"{r.auto['merk']} {r.auto['model']}" for r in resultaten})

        f = request.args
        def als_getal(naam):
            try:
                return int(f.get(naam, ""))
            except ValueError:
                return None

        filters = {"model": f.get("model", ""), "max_prijs": als_getal("max_prijs"), "max_km": als_getal("max_km"),
                   "min_marge": als_getal("min_marge"), "min_winst": als_getal("min_winst"),
                   "alleen_deals": f.get("alleen_deals") == "1"}
        lijst = []
        for r in resultaten:
            a = r.auto
            if filters["model"] and f"{a['merk']} {a['model']}" != filters["model"]:
                continue
            if filters["max_prijs"] is not None and a["vraagprijs"] > filters["max_prijs"]:
                continue
            if filters["max_km"] is not None and (a["kilometerstand"] or 0) > filters["max_km"]:
                continue
            if filters["min_marge"] is not None and (r.marge is None or r.marge < filters["min_marge"]):
                continue
            if filters["min_winst"] is not None and (r.winst is None or r.winst < filters["min_winst"]):
                continue
            if filters["alleen_deals"] and not r.is_deal:
                continue
            lijst.append(r)

        samenvatting = {
            "totaal": database.aantal_advertenties(conn),
            "doel": len(resultaten),
            "deals": sum(r.is_deal for r in resultaten),
            "vlaggen": sum(bool(r.rode_vlaggen) for r in resultaten),
            "weinig_data": sum(r.status == "te_weinig_data" for r in resultaten),
        }
        statussen = database.alle_site_statussen(conn)
        sites = [(naam, statussen.get(naam)) for naam, aan in inst.get("sites", {}).items() if aan]
        return render_template("overzicht.html", lijst=lijst, modellen=modellen, filters=filters,
                               s=samenvatting, sites=sites, inst=inst, fout=f.get("fout"),
                               now_str=database.nu())

    @app.route("/auto/<int:pk>")
    def detail(pk):
        conn = db()
        auto = database.haal_auto(conn, pk)
        if auto is None:
            abort(404)
        r = analyse.analyseer(conn, auto, inst)
        rdw_gegevens = json.loads(auto["rdw_gegevens"]) if auto["rdw_gegevens"] else None
        return render_template("auto.html", r=r, a=r.auto, inst=inst,
                               geschiedenis=database.prijsgeschiedenis(conn, pk), rdw_gegevens=rdw_gegevens)

    @app.route("/link", methods=["POST"])
    def link():
        url = request.form.get("url", "").strip()
        if not url.startswith("http"):
            return redirect(url_for("overzicht", fout="Plak een volledige link die begint met https://"))
        try:
            pk = reken_link_door(db(), ophaler, inst, url)
        except (ValueError, NietToegestaan, SiteGeblokkeerd, ConnectionError) as fout:
            return redirect(url_for("overzicht", fout=str(fout)))
        return redirect(url_for("detail", pk=pk))

    return app


def reken_link_door(conn, ophaler, inst, url):
    """Haalt één advertentie op (geplakte link), slaat hem op en geeft het id terug."""
    site = site_voor_link(url, ophaler, inst)
    adv = site.haal_advertentie(url)
    if adv is None:
        raise ValueError("Kon op deze pagina geen auto-gegevens vinden. "
                         "Gebruik 'python main.py handmatig' om de gegevens zelf in te voeren.")
    merk, model = _herken_merk_model(adv, inst)
    if not merk:
        raise ValueError("Kon merk en model niet herkennen. Staat dit model in instellingen.toml?")
    vul_aan(adv, merk, model)
    pk, _ = database.sla_op(conn, adv)
    if adv.kenteken and inst["rdw"]["aan"]:
        try:
            database.sla_rdw_op(conn, pk, rdw.haal_op(ophaler, adv.kenteken))
        except (ConnectionError, SiteGeblokkeerd) as fout:
            log.warning("RDW-controle mislukt: %s", fout)
    return pk


def _herken_merk_model(adv, inst):
    tekst = f"{adv.titel} {adv.extra.get('merk_site') or ''} {adv.extra.get('model_site') or ''}".lower()
    for m in inst["zoeken"]["modellen"]:
        if m["model"].lower() in tekst:
            return m["merk"], m["model"]
    if adv.extra.get("merk_site") and adv.extra.get("model_site"):
        return adv.extra["merk_site"], adv.extra["model_site"]
    return None, None
