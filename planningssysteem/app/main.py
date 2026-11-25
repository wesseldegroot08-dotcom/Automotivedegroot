"""De web-app. Start met: uvicorn app.main:app (of start.sh / start.bat)."""

import secrets

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException
from starlette.middleware.sessions import SessionMiddleware

from app.config import BASIS_MAP, instellingen
from app.web import (
    algemeen,
    beheer,
    chauffeur,
    export,
    morgen,
    orders,
    planbord,
    stamdata,
    voertuigen,
    voorstellen,
    wagenpark,
)
from app.web.deps import NietIngelogd, csrf_token
from app.web.sjablonen import templates


def maak_app() -> FastAPI:
    cfg = instellingen()
    sleutel = cfg.geheime_sleutel
    if not sleutel or sleutel == "verander-mij":
        # Geen sleutel ingesteld: maak een tijdelijke. Na een herstart moet je opnieuw inloggen.
        sleutel = secrets.token_urlsafe(32)

    app = FastAPI(title="Planningssysteem (testversie)", docs_url=None, redoc_url=None)
    app.add_middleware(SessionMiddleware, secret_key=sleutel, session_cookie="planning_sessie",
                       same_site="lax", https_only=cfg.cookie_secure, max_age=12 * 3600)
    app.mount("/static", StaticFiles(directory=str(BASIS_MAP / "app" / "static")), name="static")
    templates.env.globals["csrf_token"] = csrf_token
    templates.env.globals["bedrijf"] = cfg.bedrijfsnaam

    app.include_router(algemeen.router)
    app.include_router(morgen.router)
    app.include_router(beheer.router)
    app.include_router(wagenpark.router)
    app.include_router(stamdata.router)
    app.include_router(voertuigen.router)
    app.include_router(planbord.router)
    app.include_router(voorstellen.router)
    app.include_router(chauffeur.router)
    app.include_router(export.router)
    app.include_router(orders.router)

    @app.exception_handler(NietIngelogd)
    async def _niet_ingelogd(request: Request, _exc):
        return RedirectResponse("/login", status_code=303)

    @app.exception_handler(HTTPException)
    async def _fout(request: Request, exc: HTTPException):
        return templates.TemplateResponse(request, "fout.html", {"code": exc.status_code, "melding": exc.detail},
                                          status_code=exc.status_code)

    return app


app = maak_app()
