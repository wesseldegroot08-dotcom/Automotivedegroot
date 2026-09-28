"""Logboek: schrijft meldingen naar het scherm en naar logs/winstradar.log."""

import logging
from logging.handlers import RotatingFileHandler

from .instellingen import LOG_MAP

_klaar = False


def maak_logboek():
    global _klaar
    log = logging.getLogger("winstradar")
    if _klaar:
        return log
    LOG_MAP.mkdir(exist_ok=True)
    log.setLevel(logging.INFO)
    opmaak = logging.Formatter("%(asctime)s  %(levelname)-7s  %(message)s", "%Y-%m-%d %H:%M:%S")

    bestand = RotatingFileHandler(LOG_MAP / "winstradar.log", maxBytes=2_000_000,
                                  backupCount=3, encoding="utf-8")
    bestand.setFormatter(opmaak)
    scherm = logging.StreamHandler()
    scherm.setFormatter(opmaak)

    log.addHandler(bestand)
    log.addHandler(scherm)
    _klaar = True
    return log


log = logging.getLogger("winstradar")
