# Noodprocedure (één A4)

**Wanneer?** Het systeem doet het niet, geeft rare voorstellen, of berichten kloppen niet.

## 1. Meteen
1. **Rare voorstellen of berichten?** Laat een admin op **Instellingen → Noodstop** drukken. Voorstellen en automatische berichten staan dan uit. Het planbord werkt nog, dus je plant met de hand verder.
2. **Systeem helemaal uit?** Werk verder met de **export van gisteren** (zie stap 2) en de telefoonlijst.

## 2. Werken zonder systeem
- **Rooster:** pak de export van het rooster van vandaag. Die heb je gisteren gemaakt via *Planbord → Rooster (print / CSV)*. Gebruik de print of de CSV op je telefoon.
- **Telefoonlijst:** chauffeurs, klanten, terminals en de werkplaats. **Bewaar deze lijst BUITEN het systeem**, bijvoorbeeld geprint in de map in de cabine en op je telefoon. Zet hier geen namen of nummers in Git.
- **Slots:** regel slots via het portaal van de terminal of via Portbase zelf. Schrijf TAR en slot op.
- **Rijtijd:** de tachograaf is de wettelijke waarheid. Kijk daar, niet in het systeem.

## 3. Back-up terugzetten
1. Stop de app (sluit het venster van `start.bat` of `start.sh`).
2. Zoek de nieuwste back-up in de map `backups/` (bijvoorbeeld `planning-20261125-180000.db`).
3. Hernoem `data/planning.db` naar `data/planning-kapot.db`. Zo blijft hij bewaard.
4. Kopieer de back-up naar `data/planning.db`.
5. Start de app opnieuw. Controleer het planbord en het logboek.

## 4. Elke dag (voorkomen)
- Maak 's avonds een back-up: `python scripts/backup.py`. Op Windows met de map `planningssysteem` open: `.venv\Scripts\python scripts\backup.py`.
- Maak elke middag de export van het rooster van morgen en bewaar die buiten de computer.
- Bewaar de back-ups ook op een tweede plek, zoals een USB-stick of de cloud.

## 5. Na afloop
- Zet de noodstop pas weer uit als duidelijk is wat er mis was.
- Schrijf in het logboek of in een notitie wat er gebeurde.
