# Taxatie-app

Persoonlijke web-app (PWA) voor de iPhone om auto's te taxeren.
De app rekent uit wat je maximaal kunt bieden: verwachte verkoopprijs − schade − marge.

**Je gegevens (taxaties, foto's, kentekens) staan alleen op je telefoon.** Niets daarvan staat in deze repository.

## Wat zit erin (fase 1)

- **Taxeren**: kenteken checken bij de RDW (merk, model, bouwjaar, brandstof, vermogen, APK, catalogusprijs, tellerstandoordeel), kilometerstand, uitvoering, transmissie, opties, advertentie-link, foto's, schade met bedragen, notities en het advies-bod op een zwarte kaart.
- **Archief**: alle opgeslagen auto's, zoeken op kenteken/merk/model, sorteren op datum of bod, openen, bewerken en verwijderen.
- **Instellingen**: marge (standaard € 1.500 – € 2.000), standaardbedragen per schadetype (beginnen op € 0), back-up maken en terugzetten.
- Werkt zonder internet (behalve het opzoeken van een kenteken).

## Op de iPhone zetten

1. Open de app-link in **Safari**.
2. Tik op het deel-icoon (vierkantje met pijl omhoog).
3. Kies **Zet op beginscherm** → **Voeg toe**.
4. Open de app voortaan via het icoon op je beginscherm.

> Let op: gegevens in Safari en in de app op je beginscherm zijn gescheiden. Gebruik alleen de app op je beginscherm. Maak regelmatig een back-up (Instellingen → Exporteer alles). Verwijder je de app van je beginscherm, dan zijn de gegevens weg.

## Hoe het gepubliceerd wordt

Elke wijziging op `main` wordt automatisch getest en op GitHub Pages gezet (zie `.github/workflows/publiceren.yml`).

## Voor ontwikkelaars

Geen frameworks, geen installatie nodig. Alleen Node.js 22.

```bash
npm test                     # tests van berekening, kenteken, RDW en back-up
npm run build                # maakt dist/ (met versienummer voor de service worker)
node scripts/serve.mjs 8080  # dist/ lokaal bekijken op http://localhost:8080
node scripts/e2e.mjs         # hele app testen in een "iPhone"-browser (Playwright)
```

| Map | Inhoud |
|---|---|
| `src/js/calc.js` | De berekening van het bod |
| `src/js/rdw.js` | Ophalen en uitlezen van RDW Open Data |
| `src/js/kenteken.js` | Kenteken opschonen en met streepjes tonen |
| `src/js/db.js` | Lokale opslag (IndexedDB via Dexie) |
| `src/js/backup.js`, `src/js/zip.js` | Back-up als ZIP (gegevens + foto's) |
| `src/js/views/` | De drie schermen |

RDW-datasets (gecontroleerd op opendata.rdw.nl):
`m9d7-ebf2` (gekentekende voertuigen), `8ys7-d773` (brandstof en vermogen), `jqs4-4kvw` (uitleg tellerstandoordeel).

Meegeleverd: [Dexie.js](https://dexie.org) 4.4.7 (Apache-2.0) en het lettertype [Inter](https://rsms.me/inter/) (OFL-1.1).
