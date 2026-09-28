"""Welke generatie hoort bij welk bouwjaar?

Een nieuwe generatie komt meestal halverwege een jaar uit. In zo'n
"wisseljaar" kan een auto van beide generaties zijn. Dan kijkt de tool of
de advertentie een hint geeft (bv. "Golf 7"). Geen hint? Dan is de generatie
onzeker en rekent de tool de auto niet door. Liever geen schatting dan een
foute schatting.

Voeg je een nieuw model toe in instellingen.toml? Zet het dan ook hier.
"""

# (naam, eerste bouwjaar, laatste bouwjaar)
GENERATIES = {
    ("volkswagen", "polo"): [("9N", 2001, 2009), ("6R/6C", 2009, 2017), ("AW", 2017, 2099)],
    ("volkswagen", "golf"): [("V", 2003, 2008), ("VI", 2008, 2012), ("VII", 2012, 2020), ("VIII", 2020, 2099)],
    ("toyota", "yaris"): [("XP9", 2005, 2011), ("XP13", 2011, 2020), ("XP21", 2020, 2099)],
    ("renault", "clio"): [("III", 2005, 2012), ("IV", 2012, 2019), ("V", 2019, 2099)],
    ("ford", "focus"): [("II", 2004, 2011), ("III", 2011, 2018), ("IV", 2018, 2099)],
    ("opel", "astra"): [("H", 2004, 2010), ("J", 2009, 2015), ("K", 2015, 2021), ("L", 2021, 2099)],
}

# Woorden in de advertentie die de generatie verraden (kleine letters).
HINTS = {
    ("volkswagen", "polo"): {"6R/6C": ["6r", "6c"], "AW": [" aw ", "polo aw"], "9N": ["9n"]},
    ("volkswagen", "golf"): {"VI": ["golf 6", "golf vi", "mk6"], "VII": ["golf 7", "golf vii", "mk7"],
                             "VIII": ["golf 8", "golf viii", "mk8"]},
    ("toyota", "yaris"): {"XP13": ["xp13", "xp130"], "XP9": ["xp9", "xp90"]},
    ("renault", "clio"): {"III": ["clio 3", "clio iii"], "IV": ["clio 4", "clio iv"], "V": ["clio 5", "clio v"]},
    ("ford", "focus"): {"II": ["focus 2", "mk2"], "III": ["focus 3", "mk3"], "IV": ["focus 4", "mk4"]},
    ("opel", "astra"): {"H": ["astra h"], "J": ["astra j"], "K": ["astra k"]},
}

# Modellen met dezelfde naam erin, die toch een ANDER model zijn.
# Die worden overgeslagen (tellen ook niet mee als vergelijking).
ANDERE_MODELLEN = {
    ("volkswagen", "golf"): ["golf plus", "golf sportsvan"],
    ("toyota", "yaris"): ["yaris verso", "yaris cross"],
    ("ford", "focus"): ["c-max", "focus c max"],
    ("opel", "astra"): ["astra classic"],
    ("volkswagen", "polo"): [],
    ("renault", "clio"): [],
}


def bepaal_generatie(merk, model, bouwjaar, tekst=""):
    """Geeft de naam van de generatie terug, of None als het onzeker is."""
    if not merk or not model or not bouwjaar:
        return None
    sleutel = (merk.lower(), model.lower())
    opties = [naam for naam, van, tot in GENERATIES.get(sleutel, []) if van <= bouwjaar <= tot]
    if len(opties) == 1:
        return opties[0]
    if len(opties) > 1:
        tekst = f" {tekst.lower()} "
        for naam in opties:
            if any(hint in tekst for hint in HINTS.get(sleutel, {}).get(naam, [])):
                return naam
    return None


def is_ander_model(merk, model, tekst):
    tekst = tekst.lower()
    return any(woord in tekst for woord in ANDERE_MODELLEN.get((merk.lower(), model.lower()), []))
