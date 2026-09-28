"""Leest robots.txt en zegt of een link opgehaald mag worden.

Waarom een eigen versie? De standaard robots.txt-lezer van Python begrijpt
geen sterretjes (*) en dollartekens ($) in regels. Een regel als
"Disallow: /*?sort=" negeert hij, en dan denkt hij dat het mag. Deze versie
volgt de regels zoals Google ze gebruikt (RFC 9309):

- Eerst de groep voor onze naam (bv. "OccasionScanner"); anders de groep "*".
- * betekent "alles", $ betekent "hier houdt de link op".
- De langste regel die past wint. Even lang? Dan wint Allow.
"""

import re
from urllib.parse import urlparse


def _naar_regex(patroon):
    eind = patroon.endswith("$")
    if eind:
        patroon = patroon[:-1]
    regex = ".*".join(re.escape(deel) for deel in patroon.split("*"))
    return re.compile(regex + ("$" if eind else ""))


class Robots:
    def __init__(self, tekst):
        self.groepen = []  # lijst van (set met namen, lijst met (mag, patroon, regex))
        namen, regels, vorige_was_agent = set(), [], False
        for regel in tekst.splitlines():
            regel = regel.split("#", 1)[0].strip()
            if ":" not in regel:
                continue
            veld, waarde = (x.strip() for x in regel.split(":", 1))
            veld = veld.lower()
            if veld == "user-agent":
                if not vorige_was_agent and namen:
                    self.groepen.append((namen, regels))
                    namen, regels = set(), []
                namen.add(waarde.lower())
                vorige_was_agent = True
            elif veld in ("allow", "disallow"):
                vorige_was_agent = False
                if namen and waarde:  # lege Disallow = alles mag
                    regels.append((veld == "allow", waarde, _naar_regex(waarde)))
            else:
                vorige_was_agent = False
        if namen:
            self.groepen.append((namen, regels))

    def _regels_voor(self, user_agent):
        naam = user_agent.split("/", 1)[0].strip().lower()
        eigen = [r for namen, regels in self.groepen for n in namen if n != "*" and n in naam for r in regels]
        if any(n != "*" and n in naam for namen, _ in self.groepen for n in namen):
            return eigen
        return [r for namen, regels in self.groepen if "*" in namen for r in regels]

    def mag(self, user_agent, url):
        deel = urlparse(url)
        pad = (deel.path or "/") + (f"?{deel.query}" if deel.query else "")
        if deel.path == "/robots.txt":
            return True
        beste = None  # (lengte, mag)
        for mag, patroon, regex in self._regels_voor(user_agent):
            if regex.match(pad):
                kandidaat = (len(patroon), mag)
                if beste is None or kandidaat > beste:
                    beste = kandidaat
        return True if beste is None else beste[1]
