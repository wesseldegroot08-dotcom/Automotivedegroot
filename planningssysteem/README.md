# Planningssysteem containertransport (testversie)

Een **testversie** van een planningssysteem voor een klein containertransportbedrijf rond Rotterdam.
Het systeem doet voorstellen. **De planner beslist altijd.**

> ⚠ **Belangrijk**
> - Dit is een testversie met **verzonnen data** ("Demo Transport BV" bestaat niet).
> - De **planner is eindverantwoordelijk**. Het systeem belooft geen perfectie en geen wettelijke naleving.
> - De **tachograaf is de wettelijke waarheid**. Het systeem voorspelt alleen.
> - Veel regels, tarieven en gewichten zijn een **aanname, schatting of open vraag**.
>   Controleer ze altijd bij de bron voordat je er iets mee doet.

## Starten (één commando)

Je hebt **Python 3.11 of nieuwer** nodig ([python.org/downloads](https://www.python.org/downloads/)).
Op Windows: vink bij installeren "Add python.exe to PATH" aan.

| Systeem | Commando |
|---|---|
| Windows | dubbelklik op `start.bat` (of typ `start.bat` in de map) |
| Mac / Linux | `./start.sh` |

Het script doet alles zelf:
1. maakt een virtuele omgeving (`.venv`, een aparte map met de pakketten voor deze app),
2. installeert de pakketten (de eerste keer heb je internet nodig, daarna niet meer),
3. maakt een `.env`-bestand met een geheime sleutel,
4. zet de database klaar (migraties) en vult de demodata,
5. start de app.

Open daarna **http://localhost:8000** in je browser.

Verse demodata nodig (bijvoorbeeld een dag later)? Start met `./start.sh --reset` of `start.bat --reset`.
De demo-orders staan altijd op **morgen**, gerekend vanaf het moment dat je de demodata laadt.

### Inloggen (alleen op je eigen computer)

| Gebruiker | Rol | Wat mag het |
|---|---|---|
| `planner` | planner | plannen, stamdata en regels aanpassen |
| `admin` | admin | alles, plus instellingen en noodstop |
| `chauffeur` | chauffeur | alleen de chauffeurspagina |

Het wachtwoord staat in `.env` bij `DEMO_WACHTWOORD` (standaard `demo1234`).
**Draait de app ooit buiten je eigen computer? Verander dan eerst alle wachtwoorden en de geheime sleutel.**

## Tests draaien

```bash
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pytest                           # alle tests
pytest tests/test_iso6346.py -v  # één testbestand, met namen
ruff check app tests             # controle van de codestijl
```

## Hoe zit het in elkaar?

| Map | Wat staat erin |
|---|---|
| `app/models.py` | alle tabellen van de database |
| `app/audit.py` | het logboek: elke wijziging wordt vanzelf vastgelegd |
| `app/rules/` | de regelmotor: alle controles op één plek |
| `app/ports/` | "poorten" naar de buitenwereld (klok, reistijden, Portbase, orderlezer) met nep-versies |
| `app/web/` | de pagina's |
| `app/seed.py` | de demodata (alles verzonnen) |
| `migrations/` | database-migraties (Alembic) |
| `docs/` | onderzoek, aannames, noodprocedure |
| `tests/` | de tests |

Belangrijke keuzes:
- **Regels zijn data.** Limieten, tarieven, slotregels en feestdagen staan in de database, met
  `geldig_van`, `geldig_tot`, `bron` en `status` (bevestigd / schatting / open). Aanpassen kan via
  *Stamdata en regels*. Elke wijziging staat in het logboek.
- **Logboek.** Wie, wat, voor, na en wanneer. Via de app kun je het niet wijzigen of wissen.
- **Niets echt verwijderen.** Je kunt archiveren. De geschiedenis blijft bewaard.
- **Gewicht in hele kg, geld in hele centen.** Tijden staan in UTC en worden in Nederlandse tijd getoond.
- **Geen taalmodel.** Alle berekeningen en uitleg maakt gewone, geteste code.

## Nog te doen (later)

- Tweestapsverificatie (2FA) bij het inloggen.
- Zie verder het plan per mijlpaal.

## Status per mijlpaal

- [x] Mijlpaal 1: basis (login, logboek, regels als data, demodata, stamdata-schermen, start-scripts)
- [x] Mijlpaal 2: voertuigen en regelmotor (trekker, chassis, voorkeuren, combinatiepagina, sjablonen, CSV, gewicht, aslast, chassis-fit, ADR, reefer, hoogte, verbodsdag)
- [ ] Mijlpaal 3: planbord
- [ ] Mijlpaal 4: voorstellen (solver)
- [ ] Mijlpaal 5: simulatoren en afronding
