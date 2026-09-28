"""Netjes pagina's ophalen van websites.

Regels die hier worden afgedwongen:
- Maximaal 1 verzoek per 5 seconden per site (instelbaar, maar nooit sneller).
- robots.txt wordt gecontroleerd voor ELKE link. Mag het niet? Dan halen we hem niet op.
- Geen inlog, geen captcha omzeilen, geen trucs. Een eerlijke user-agent.
- Blokkeert een site ons? Dan komt er een SiteGeblokkeerd-fout en stopt de tool voor die site.
"""

import threading
import time
from urllib.parse import urlparse

import requests

from .logboek import log
from .robots import Robots

MIN_WACHTTIJD = 5  # seconden, ondergrens: ook als je in de instellingen iets lagers zet


class SiteGeblokkeerd(Exception):
    """De site blokkeert ons (bv. fout 403, 429 of een captcha)."""


class NietToegestaan(Exception):
    """robots.txt van de site staat dit ophalen niet toe."""


BLOKKADE_TEKENS = ["captcha", "cf-challenge", "access denied", "are you a robot", "ben je een robot",
                   "unusual traffic", "verdacht verkeer"]


class NetteOphaler:
    def __init__(self, user_agent, wachttijd=5):
        self.user_agent = user_agent
        self.wachttijd = max(wachttijd, MIN_WACHTTIJD)
        self.sessie = requests.Session()
        self.sessie.headers.update({"User-Agent": user_agent, "Accept-Language": "nl-NL,nl;q=0.9"})
        self._laatste = {}          # host -> tijd van laatste verzoek
        self._robots = {}           # host -> (Robots, opgehaald_om)
        self._slot = threading.Lock()

    # ---------- wachten ----------
    def _wacht(self, host):
        with self._slot:
            vorige = self._laatste.get(host)
            if vorige is not None:
                nog = self.wachttijd - (time.monotonic() - vorige)
                if nog > 0:
                    time.sleep(nog)
            self._laatste[host] = time.monotonic()

    # ---------- robots.txt ----------
    def _robots_voor(self, url):
        deel = urlparse(url)
        host = deel.netloc
        cache = self._robots.get(host)
        if cache and time.time() - cache[1] < 24 * 3600:
            return cache[0]
        robots_url = f"{deel.scheme}://{host}/robots.txt"
        self._wacht(host)
        # Lukt ophalen niet? Dan weten we niet of het mag. Dat is een verbindingsprobleem,
        # geen verbod: we halen niets op en proberen het bij de volgende ronde opnieuw.
        try:
            antwoord = self.sessie.get(robots_url, timeout=20)
        except requests.RequestException as fout:
            raise ConnectionError(f"kon robots.txt van {host} niet ophalen, dus voor de zekerheid "
                                  f"niets opgehaald ({fout.__class__.__name__})") from fout
        if antwoord.status_code in (401, 403):
            # Volgens de regels betekent dit: niets mag.
            parser = Robots("User-agent: *\nDisallow: /")
        elif antwoord.status_code >= 500:
            raise ConnectionError(f"robots.txt van {host} gaf fout {antwoord.status_code}, "
                                  f"dus voor de zekerheid niets opgehaald")
        elif antwoord.status_code >= 400:
            parser = Robots("")  # geen robots.txt = alles mag
        else:
            parser = Robots(antwoord.text)
        self._robots[host] = (parser, time.time())
        return parser

    def mag_ophalen(self, url):
        """True/False volgens robots.txt. ConnectionError als robots.txt niet op te halen is."""
        return self._robots_voor(url).mag(self.user_agent, url)

    # ---------- ophalen ----------
    def haal(self, url, params=None, controleer_robots=True, json_verwacht=False):
        """Haalt een pagina op. Geeft de tekst (of JSON) terug."""
        volledige_url = requests.Request("GET", url, params=params).prepare().url
        if controleer_robots and not self.mag_ophalen(volledige_url):
            raise NietToegestaan(f"robots.txt staat dit niet toe: {volledige_url}")

        host = urlparse(volledige_url).netloc
        self._wacht(host)
        try:
            antwoord = self.sessie.get(volledige_url, timeout=30)
        except requests.RequestException as fout:
            raise ConnectionError(f"Geen verbinding met {host}: {fout}") from fout

        if antwoord.status_code in (403, 429):
            raise SiteGeblokkeerd(f"{host} gaf fout {antwoord.status_code}")
        if antwoord.status_code == 404:
            return None
        if antwoord.status_code >= 400:
            raise ConnectionError(f"{host} gaf fout {antwoord.status_code}")

        tekst = antwoord.text
        if not json_verwacht:
            begin = tekst[:5000].lower()
            if any(teken in begin for teken in BLOKKADE_TEKENS):
                raise SiteGeblokkeerd(f"{host} toont een captcha of blokkadepagina")
        if json_verwacht:
            try:
                return antwoord.json()
            except ValueError:
                if any(teken in tekst[:5000].lower() for teken in BLOKKADE_TEKENS):
                    raise SiteGeblokkeerd(f"{host} toont een captcha of blokkadepagina")
                raise ConnectionError(f"{host} gaf geen geldige JSON terug")
        return tekst
