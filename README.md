# Occasion Scanner

Een tool die auto-advertenties zoekt en uitrekent of je er winst op maakt.

- Zoekt elke 30 minuten op Marktplaats, AutoScout24, Gaspedaal, AutoTrack en Autowereld.
- Slaat alles op in een database op je laptop.
- Rekent per auto de **marge** en de **winst** uit, en laat de hele berekening zien.
- Controleert het kenteken bij de RDW (APK, datum eerste toelating, tellerstand).
- Geeft **rode vlaggen** bij verdachte advertenties.
- Stuurt een melding (Telegram of e-mail) als een auto minimaal €1.000 marge **én** €750 winst oplevert.
- Heeft een dashboard in je browser.

---

## Snelste manier op Windows (dubbelklikken)

1. Installeer Python via [python.org/downloads](https://www.python.org/downloads/).
   Zet een vinkje bij **"Add python.exe to PATH"**.
2. Download deze map (groene knop **Code** → **Download ZIP**), klik met rechts op de ZIP → **Alles uitpakken**.
3. Dubbelklik in de uitgepakte map op:

| Bestand | Wat het doet | Wanneer |
|---|---|---|
| `installeren.bat` | Installeert alles wat de tool nodig heeft | Eén keer |
| `demo.bat` | Dashboard met verzonnen auto's | Om te kijken hoe het werkt |
| `test-marktplaats.bat` | Kijkt of Marktplaats werkt | Voordat je echt begint |
| `verken-sites.bat` | Kijkt per site of zoeken werkt en mag | Voordat je echt begint, en als een site niets meer vindt |
| `start.bat` | Zoekt elke 30 minuten + opent het dashboard | Elke keer dat je hem gebruikt |

Stoppen: sluit het zwarte venster.

Komt er een blauw scherm **"Windows heeft uw pc beveiligd"**? Dat komt omdat het bestand van internet komt. Klik op **Meer informatie** → **Toch uitvoeren**.

De rest van deze README legt hetzelfde uit met getypte opdrachten, voor als je meer wilt weten.

---

## 1. Installeren (eenmalig)

### Stap 1: Python installeren
Je hebt **Python 3.11 of nieuwer** nodig.

- **Windows:** download Python via [python.org/downloads](https://www.python.org/downloads/).
  Zet bij het installeren een vinkje bij **"Add python.exe to PATH"**. Dit is belangrijk.
- **macOS:** download Python via [python.org/downloads](https://www.python.org/downloads/).
- **Linux:** meestal staat het er al op. Check met `python3 --version`.

Check of het gelukt is. Open een terminal:
- Windows: druk op de Windows-toets, typ `cmd` en druk op Enter.
- macOS: open het programma **Terminal**.

Typ:
```
python --version
```
Zie je `Python 3.11` of hoger? Dan is het goed. (Op macOS/Linux: typ `python3` in plaats van `python`.)

### Stap 2: De tool downloaden
Download deze map van GitHub (groene knop **Code** → **Download ZIP**) en pak hem uit.
Of met git: `git clone <link van deze repository>`.

### Stap 3: Naar de map gaan
In de terminal:
```
cd pad/naar/Automotivedegroot
```
Tip: typ `cd ` (met spatie) en sleep de map in het terminalvenster. Dan staat het pad er vanzelf.

### Stap 4: Onderdelen installeren
```
python -m venv .venv
```
Dit maakt een eigen "doos" voor de onderdelen van deze tool. Zet hem aan:

- Windows: `.venv\Scripts\activate`
- macOS/Linux: `source .venv/bin/activate`

Je ziet nu `(.venv)` voor je regel staan. Installeer daarna:
```
pip install -r requirements.txt
```

> Elke keer dat je een nieuwe terminal opent, moet je eerst weer naar de map gaan (`cd ...`) en de doos aanzetten (stap 4, de `activate`-regel).

---

## 2. Eerst proberen: de demo

Bekijk het dashboard met verzonnen auto's. Er wordt niets van internet gehaald.
```
python main.py demo
```
Je browser opent `http://127.0.0.1:5000`. Stoppen: druk in de terminal op **Ctrl+C**.

---

## 3. Controleren of Marktplaats werkt

```
python main.py test-marktplaats
```
De tool kijkt eerst in **robots.txt** of ophalen mag. Daarna haalt hij één pagina op en laat hij 5 auto's zien.

- **"robots.txt staat het niet toe"** → dan mag deze module niet gebruikt worden. Zet `marktplaats = false` in `instellingen.toml`. Gebruik dan de back-up (zie hoofdstuk 6).
- **"Marktplaats blokkeert"** → de tool stopt met die site. Probeer het niet te omzeilen.
- **"0 advertenties gevonden"** → Marktplaats heeft waarschijnlijk zijn website veranderd. De code moet dan aangepast worden.

---

## 4. Starten

```
python main.py start
```
Dit doet twee dingen tegelijk:
1. Elke 30 minuten zoeken naar nieuwe auto's.
2. Het dashboard openen in je browser.

Laat het terminalvenster open. Stoppen: **Ctrl+C**.

**Let op:** de tool zoekt alleen als je laptop aan staat en niet in slaapstand is.

Andere opdrachten:

| Opdracht | Wat het doet |
|---|---|
| `python main.py zoek` | Eén zoekronde en dan stoppen |
| `python main.py dashboard` | Alleen het dashboard openen |
| `python main.py link <url>` | Eén advertentie doorrekenen |
| `python main.py handmatig` | Zelf de gegevens van een auto intypen |
| `python main.py test-melding` | Testbericht sturen |

---

## 5. Belangrijk: de eerste weken

De winstberekening vergelijkt een auto met **minimaal 5 vergelijkbare auto's** in de database. In het begin is de database leeg. Dan staat bijna alles op **"Te weinig data"**.

- Reken op **2 tot 4 weken** verzamelen voordat de berekening echt iets zegt.
- De tool slaat daarom ook auto's van €1.000 tot €7.000 op, alleen om mee te vergelijken. Waarom? Als je alleen auto's van €2.000–€4.000 opslaat, ligt de mediaan altijd rond de €3.000. Dan vind je bijna nooit een deal.

---

## 6. Back-up: zelf een link doorrekenen

Werkt het automatisch zoeken niet? Of zie je zelf een leuke auto?

- In het dashboard: plak de link onderaan de pagina.
- Of in de terminal: `python main.py link https://www.marktplaats.nl/v/...`
- Lukt het ophalen niet? Typ de gegevens zelf in: `python main.py handmatig`

---

## 7. Meldingen instellen

1. Kopieer `geheimen.voorbeeld.toml` en noem de kopie `geheimen.toml`.
2. Kies in `instellingen.toml` bij `[meldingen]`: `kanaal = "telegram"` of `kanaal = "email"`.

### Telegram (aanrader: gratis, snel, op je telefoon)
1. Zoek in Telegram naar **@BotFather**. Stuur `/newbot` en volg de stappen.
2. Je krijgt een **token** (lange code). Zet die in `geheimen.toml` bij `bot_token`.
3. Stuur je nieuwe bot een berichtje (bv. "hoi").
4. Open in je browser: `https://api.telegram.org/bot<JOUW_TOKEN>/getUpdates`
   Zoek `"chat":{"id":123456789` op. Dat getal is je **chat_id**.
5. Test: `python main.py test-melding`

### E-mail (Gmail)
1. Zet bij je Google-account **tweestapsverificatie** aan.
2. Maak een **app-wachtwoord** aan (zoek in je Google-account op "app-wachtwoorden").
3. Vul `gebruiker`, `wachtwoord` (het app-wachtwoord) en `naar` in `geheimen.toml` in.
4. Test: `python main.py test-melding`

`geheimen.toml` wordt **niet** naar GitHub geüpload. Deel dit bestand met niemand.

---

## 8. Instellingen aanpassen

Alles staat in **`instellingen.toml`**. Open het met Kladblok (Windows) of TextEdit (macOS).
Er staat bij elke instelling uitleg. Na een wijziging: stop de tool (Ctrl+C) en start hem opnieuw.

---

## 9. Zo rekent de tool

1. **Vergelijkbare auto's zoeken:** zelfde merk, model én generatie, zelfde motor en transmissie, bouwjaar max 1 jaar verschil, km max 25.000 verschil. Auto's met woorden als "defect" of "schade" tellen niet mee.
2. **Minder dan 5?** Dan geen schatting: "Te weinig data".
3. **Geschatte verkoopprijs** = mediaan van hun vraagprijzen − 5%.
4. **Marge** = geschatte verkoopprijs − vraagprijs.
5. **Winst** = marge − kosten (reparatie €300 + poetsen €50 + transport €75 + overschrijving €50 = €475).
6. **Melding** als marge ≥ €1.000 én winst ≥ €750.

Voorbeeld:
```
Mediaan van 7 vergelijkbare Polo's      € 4.750,00
- 5%                                    €  -237,50
= Geschatte verkoopprijs                € 4.512,50
- Vraagprijs                            € -3.100,00
= Marge                                 € 1.412,50
- Kosten                                €  -475,00
= Winst                                 €   937,50   -> melding
```

**Goed om te weten:** met €475 kosten betekent "winst ≥ €750" automatisch "marge ≥ €1.225". De marge-grens van €1.000 wordt dan altijd al gehaald.

### Wat de tool NIET weet
- De **echte staat** van de auto. Ga altijd kijken, maak een proefrit en laat hem bij twijfel keuren.
- De **echte verkoopprijs**. Vraagprijzen zijn geen verkoopprijzen. Auto's die lang online staan, zijn vaak te duur. Daardoor kan de schatting te hoog zijn.
- **Generatie in wisseljaren.** Een Golf uit 2012 kan een Golf 6 of 7 zijn. Staat dat niet in de advertentie? Dan rekent de tool hem niet door.

---

## 10. Hoe de tool websites netjes behandelt

- Maximaal **1 verzoek per 5 seconden** per site.
- Controleert **robots.txt** voor elke link. Mag het niet? Dan haalt hij niets op.
- Geen inlog, geen captcha omzeilen, geen trucs. De tool zegt eerlijk wie hij is.
- Blokkeert een site? Dan stopt de tool 6 uur met die site, schrijft het in `logs/occasionscanner.log` en gaat door met de rest.

---

## 11. Mappen en bestanden

| Wat | Waar |
|---|---|
| Instellingen | `instellingen.toml` |
| Wachtwoorden/tokens | `geheimen.toml` (maak je zelf) |
| Database | `data/autos.db` |
| Logboek | `logs/occasionscanner.log` |
| Code | `occasionscanner/` |
| Site-modules | `occasionscanner/sites/` |
| Tests | `tests/` (draaien met `python -m pytest`) |

---

## 12. Sites

| Site | Status |
|---|---|
| Marktplaats | Getest en werkt (via de gewone zoekpagina; de API mag niet volgens robots.txt) |
| AutoScout24, Gaspedaal, AutoTrack, Autowereld | Gebouwd, maar **nog niet getest** tegen de echte site |

Draai `verken-sites.bat`. Per site zie je:

- **WERKT** → prima, laat hem aan staan.
- **MAG NIET (robots.txt)** → de site verbiedt automatisch zoeken. Zet hem uit in `instellingen.toml` onder `[sites]` (bijvoorbeeld `gaspedaal = false`). De tool haalt er toch al niets op.
- **ZOEK-URL KLOPT NIET** → zoek zelf op die site naar een Volkswagen Polo, kopieer de link uit je browser en zet hem in `instellingen.toml` onder `[zoek_urls]`. Vervang `volkswagen` door `{merk}`, `polo` door `{model}` en het paginanummer door `{pagina}`.
- **GEEN ADVERTENTIES HERKEND** → de site is anders opgebouwd dan verwacht. De pagina staat in `logs/verkenning/`. Stuur die op, dan kan de herkenning aangepast worden.

Dezelfde auto op meerdere sites (bijvoorbeeld op AutoTrack én Gaspedaal) wordt herkend aan kenteken of kilometerstand en telt maar één keer.

**Let op met handelaren.** Op AutoScout24, AutoTrack en Gaspedaal staan vooral auto's van autobedrijven. Die vragen meer (garantie, BOVAG). Als hun prijzen meetellen als vergelijking, lijkt een particuliere auto op Marktplaats sneller een deal. Controleer bij een melding dus altijd welke vergelijkbare auto's zijn gebruikt (staat op de detailpagina, met de site erbij).
