# Aannames en onzekere waarden

**Verzin niets:** alles wat niet zeker is, staat in de app met een label: **Aanname**, **Schatting** of **Open**. Je ziet het label bij de regel, de instelling of de waarde zelf. Deze lijst is een momentopname van de demodata. De database en het scherm *Stamdata en regels* zijn leidend.

- **Bevestigd:** uit een bron die we hebben nagekeken. Toch periodiek controleren.
- **Schatting:** een redelijke waarde, maar niet nagekeken of verouderd.
- **Open:** de bronnen spreken elkaar tegen of het is niet uitgezocht. **Niet op vertrouwen.**
- **Aanname (vlag):** een waarde die het systeem invult als niets bekend is, zoals de tarra van een trekker of een standaard laadtijd.

## Regels met status Open
| Code | Wat | Waarde | Waarom open |
|---|---|---|---|
| gewicht.BE | België (Vlaanderen) | 44.000 kg | Bronnen spreken elkaar tegen |
| gewicht.FR / gewicht.LU | Frankrijk, Luxemburg | geen | Niet uitgezocht, niet gebruiken |
| aslast.tridem.hoog | Tridem, hoge waarde | 27.000 kg | Alleen sommige bronnen |
| aslast.aandrijfas.min | Aandrijfas minimaal deel van totaal | 20% | Details onbekend |
| de.intermodaal.wegdeel | Duitsland: wegdeel bij gecombineerd vervoer | 150 km | Rotterdam-Duisburg is ca. 220 km: risico |
| Instelling ect_veiligheidstest_ingang | Ingangsdatum ECT-veiligheidstest | 2026-11-03 | Bronnen: 3-11-2026 of 5-1-2027 |
| Terminalregel APM Terminals MVII | Slots 30 min, tolerantie 45 min | | FAQ zonder datum |
| Terminalregel RWG | Piektoeslag € 25,80 | | Rest onbekend |
| Feestdagen per Duitse deelstaat | | | Alleen landelijke feestdagen in de demo |
| Cao-loonschalen | | | Alleen de 30% toeslag is bekend |

## Regels met status Schatting
- **Aslasten:** enkel 10.000, aangedreven 11.500, tandem 18.000, tridem 24.000 kg.
- **Tarra lege container:** 20ft ca. 2.250, 40ft dry 3.750, 40ft HC 4.150, 45ft HC 4.800 kg. Bronnen verschillen 100 tot 250 kg.
- **Tarra trekker als niets bekend is:** 8.000 kg. Krijgt altijd de vlag *aanname*.
- **Dienst maximaal 13 uur:** afgeleid uit 11 uur rust.
- **Wachten, laden en lossen tellen als werktijd.**
- **Kostprijs (prijspeil 2021, verouderd):** € 66,84 per uur, € 1,65 per km, € 41,12 per uur laden, lossen en wachten. De index staat op 100, dus er is nog niet gecorrigeerd naar 2026.
- **Tol:** NL 20,6 ct/km in 2027 (voorlopig), DE 34,8 ct/km (sinds 1-7-2024 niet gecontroleerd), BE 13,2 ct/km (CO2-toeslag onzeker).
- **Wachttijd bij de klant:** 2 uur vrij, daarna € 40 per half uur (voorbeeld Maersk).
- **D&D-tarieven Maersk:** voorbeeld per 1-8-2026, niet algemeen. Demo Lines is verzonnen.
- **Reistijden:** de tabel in de demo is geschat. Ontbreekt een reistijd, dan rekent het systeem hemelsbreed × 130% bij 60 km/u. Dat is grof.

## Aannames in het systeem zelf (ontwerpkeuzes)
- Eén chauffeur per trekker per dag in de voorstellen. Wisselen van trekker komt later.
- Trekker en chassis zijn één vaste eenheid. Ontkoppelen (drop-and-hook) komt later.
- **Laadtijd** is de standaardtijd per locatie (vaak *aanname*). Bij een terminal met minstens 3 metingen gebruikt het systeem het gemeten gemiddelde.
- De **solver** rekent met een benadering van de rij- en rusttijden. Daarna toetst de exacte controle het resultaat. De tachograaf blijft de waarheid.
- **LZV (regel 19)** is niet gebouwd.
- **Portbase en order inlezen** zijn simulatoren. Er gaat geen echt bericht naar buiten.
- **BTW** staat niet op het factuurconcept. Dat hangt af van de soort vervoer.
