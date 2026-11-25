> Bureauonderzoek. Veel waarden zijn aannames (zie de status bij elke waarde).
> Deel 2 van het oorspronkelijke rapport (over een bestaand bedrijf) is bewust weggelaten: in deze repo staat geen echte bedrijfsdata.

# Deel 1: Zo werkt een containerrit vanuit Rotterdam

*Peildatum: 23 november 2026. Geschreven voor Wessel, als basis voor een planningssysteem voor een transportbedrijf.*

> **Dit bestand heeft drie delen**
>
> - **Deel 1** (hoofdstuk 1 tot 13): zo werkt zeecontainertransport, van containers en regels tot Rotterdam en daarbuiten.
> - **Deel 2** (hoofdstuk 14 tot 25): een bestaand bedrijf (in deze versie weggelaten).
> - **Deel 3** (hoofdstuk A tot R): een planningssysteem dat het meeste zelf doet. Bouwen of kopen, wat kan automatisch, risico's en wat je als eerste doet.
>
> Zoek je snel de conclusies? Lees per deel eerst "Het belangrijkste in 1 minuut".

## Het belangrijkste in 1 minuut

Een zeecontainerrit over de weg is simpel: een trekker met chassis haalt een container bij een terminal in de haven, rijdt naar de klant en brengt de lege container terug. Het lastige zit in de regels eromheen. Je mag minder lading meenemen dan op de container staat. In Nederland mag een combinatie 50 ton wegen. In Duitsland is 40 ton normaal. Daar kan 44 ton alleen met een 3-assige trekker en een intermodale container. Bij een 40ft High Cube en een trekker van 8 ton (mijn aanname) blijft grofweg 33 ton lading over bij 50 ton en 27 ton bij 44 ton (hoofdstuk 5). Bij de grote terminals op de Maasvlakte meld je elk bezoek vooraf aan in Portbase. Bij ECT Delta en Euromax heb je sinds 5 oktober 2026 ook een tijdslot nodig. Vanaf 25 november zijn dat blokken van 2 uur. Een chauffeur mag 9 uur per dag rijden en wachten bij de terminal telt als werktijd. Het onderzoek vond geen betrouwbare cijfers voor ritprijzen per container, ritten per dag per truck, het gewicht van een trekker en de wachttijden van nu. Voor je planningssysteem betekent dit: begin met een planbord met waarschuwingen, zet de regels als aanpasbare data (ECT veranderde ze de afgelopen weken meerdere keren) en praat met een echte planner voordat je veel bouwt.

| Onderwerp | Kerncijfer | Status |
|---|---|---|
| Maximaal gewicht combinatie in Nederland | 50.000 kg ([government.nl](https://government.nl/topics/freight-transportation/requiremenst-for-lorries)) | Bevestigd |
| Maximaal gewicht in Duitsland | 40 t normaal; 42 t (2-assige trekker) of 44 t (3-assige trekker) bij intermodaal ([§ 34 StVZO](https://www.gesetze-im-internet.de/stvzo_2012/__34.html)) | Bevestigd, details controleren |
| Maximale hoogte en breedte in Nederland | 4,00 m en 2,55 m ([OM](https://www.om.nl/onderwerpen/b/beleidsregels/instructies/verkeer/instructie-voertuigafmetingen-2021i003)) | Bevestigd |
| Rijtijd per dag | 9 uur, twee keer per week 10 uur ([EC](https://transport.ec.europa.eu/transport-modes/road/mobility-package-i/driving-rest-times_en)) | Bevestigd |
| Nederlandse tol, Euro 6, boven 32 ton | 20,1 ct/km (juli-aug 2026), 15,6 ct/km (sep-dec 2026), 20,6 ct/km (2027) ([vrachtwagenheffing.nl](https://www.vrachtwagenheffing.nl/dit-gaat-u-betalen)) | Bevestigd |
| ECT-slot | Blokken van 2 uur vanaf 25 nov 2026, 30 min tolerantie ([ECT](https://www.ect.nl/en/news/news-feed/update-truck-capacity-management-system-hutchison-ports-ect-rotterdam)) | Bevestigd |
| Ritten per dag per truck | 2 tot 3 | Schatting, geen bron |
| Ritprijs per container | Niet gevonden | Open |

---

## 1. Zo lees je dit rapport

Je ziet drie labels. Waar een bronlink staat, is het bevestigd door die bron. Waar "Schatting" of "Open" staat, is het dat niet.

| Label | Wat het betekent |
|---|---|
| **Bevestigd** | Staat in een bron. De link staat erbij. |
| **Schatting** | Door mij berekend of afgeleid. Geen bronfeit. Kan fout zijn. |
| **Open** | Niet uitgezocht, of de bronnen spreken elkaar tegen. |

Bedragen zijn zonder btw, tenzij er iets anders staat. Dit rapport is geen juridisch advies. Veel bronnen zijn samenvattingen. Sommige zijn oud (RDW-overzicht uit 2012, chassis-brochure van ca. 2021). Controleer een regel altijd bij de bron voordat je hem als harde regel in een systeem zet.

**Woorden die je nodig hebt**

| Woord | Uitleg |
|---|---|
| Trekker | De kop van de truck. |
| Chassis (oplegger) | Het onderstel waar de container op staat. |
| Tarra | Het gewicht van iets als het leeg is. |
| Netto lading | Het gewicht van de spullen in de container. |
| Bruto gewicht | Container plus spullen samen. |
| VGM | Het gewogen gewicht van de volle container. De afzender moet dit doorgeven. |
| TEU | Maat voor containers. 1 TEU is een container van 20ft. |
| HC (High Cube) | Extra hoge container: 2,896 m. |
| Terminal | Plek in de haven waar containers van en naar het schip gaan. |
| Depot | Plek waar lege containers staan. |
| Portbase | Het digitale systeem van de haven. Hier meld je alles aan. |
| Pre-notificatie | Vooraf melden dat je komt: container, chauffeur en tijd. |
| TAR | Afspraaknummer voor de poort van de terminal. |
| Slot | Tijdvak waarin je naar de terminal mag. |
| Release | Vrijgave van de container door rederij, douane en terminal. |
| LFD (last free day) | Laatste gratis dag voordat de rederij kosten rekent. |
| Demurrage | Kosten aan de rederij als de container te lang op de terminal staat. |
| Detention | Kosten aan de rederij als de container te lang buiten de terminal is. |
| Merchant haulage | Het transport is geregeld door de verlader of expediteur. |
| Carrier haulage | Het transport is geregeld door de rederij. |
| Pre-pull | Container eerder ophalen en ergens neerzetten. |
| LZV | Lange zware vrachtwagencombinatie: 25,25 m en 60 ton. |
| ISPS | Internationale beveiligingsregels voor havens (toegangscontrole). |
| ADR | Regels voor gevaarlijke stoffen over de weg. |
| TMS | Transport management system. Dat is een planningssysteem. |

---

## 2. Containers wegen tot 30,5 ton, maar de weg bepaalt wat er mee mag

### 2.1 Types en gewichten

Alle containers zijn 2,438 m breed. De lengte is 20, 40 of 45 voet. De hoogte is 2,591 m of 2,896 m (High Cube). De cijfers hieronder komen uit twee bronnen. Ze verschillen een beetje per fabrikant ([DHL](https://www.dhl.com/nl-en/home/global-forwarding/freight-forwarding-education-center/cargo-container-sizes-and-types.html), [Wikipedia](https://en.wikipedia.org/wiki/Intermodal_container)).

| Type | Buitenmaat L x B x H (m) | Leeg (kg) | Lading max (kg) | Bruto max (kg) | Status |
|---|---|---|---|---|---|
| 20ft standaard | 6,058 x 2,438 x 2,591 | 2.200 - 2.250 | 28.230 - 28.280 | 30.480 | Bevestigd |
| 40ft standaard | 12,192 x 2,438 x 2,591 | 3.800 | 26.680 | 30.480 | Bevestigd (1 bron) |
| 40ft High Cube | 12,192 x 2,438 x 2,896 | 3.935 - 4.150 | 26.330 - 26.545 | 30.480 | Bevestigd |
| 45ft High Cube | 13,716 x 2,438 x 2,896 | 4.280 - 4.500 | 26.500 - 28.500 | zie hieronder | Open |
| 20ft koel (reefer) | 6,058 x 2,438 x 2,591 | 2.840 | 27.640 | 30.480 | Bevestigd (1 bron) |
| 40ft HC koel (reefer) | 12,192 x 2,438 x 2,896 | 4.330 | 29.670 | 34.000 | Bevestigd (1 bron) |

Let op bij deze tabel:

- **Het leeggewicht verschilt per container.** Een 40ft HC weegt 3.935 kg (Wikipedia) of 4.150 kg (DHL). Gebruik voor een berekening het gewicht van het echte containernummer (CSC-plaat of rederij), niet het catalogusgewicht (Schatting).
- **De 45ft-cijfers kloppen niet.** Bij DHL is 4.280 + 26.500 = 30.780 kg. Bij Wikipedia is 4.500 + 28.500 = 33.000 kg. Beide zijn niet 30.480 kg. Dat is mijn eigen rekencontrole (Schatting). Gebruik geen 45ft-cijfers zonder het gewicht van de container zelf.
- **Het maximum is hoger geworden.** Een ISO-wijziging uit 2016 verhoogde het maximum voor standaardmaten (behalve 10ft) tot 36.000 kg. Veel containers hebben nog de oude 30.480 kg ([Wikipedia](https://en.wikipedia.org/wiki/Intermodal_container)).
- **Pallet-wide.** Deze container is binnen ca. 2,44 m breed in plaats van ca. 2,34 m. Er passen meer Euro-pallets in: 15 tegen 11 (20ft), 30 tegen 25 (40ft), 34 tegen 27 (45ft) ([Wikipedia](https://en.wikipedia.org/wiki/Intermodal_container)).
- **Tunnel aan de voorkant.** 40ft en 45ft HC hebben een uitsparing voor de gooseneck van het chassis ([Wikipedia](https://en.wikipedia.org/wiki/Intermodal_container)). Het chassis moet daarbij passen ([Cargobull](https://www.cargobull.com/be/producten/container-chassis/s-cf-light-40-45)).
- **Andere types.** Maersk noemt open top, flat, tank en meer ([Maersk](https://www.maersk.com/support/faqs/2024/07/01/types-and-sizes-of-containers)). Ca. 6% van alle containers is een reefer, ca. 0,75% een tank ([Wikipedia](https://en.wikipedia.org/wiki/Intermodal_container)). Betrouwbare maten en gewichten voor open top, flat rack, platform, side door en bulk zijn **Open**.

### 2.2 Het containernummer

Een containernummer heeft 4 letters, 6 cijfers en 1 controlecijfer. Voorbeeld: CSQU3054383. De eerste 3 letters zijn de eigenaar. De 4e letter is meestal U ([Wikipedia ISO 6346](https://en.wikipedia.org/wiki/ISO_6346)).

Zo werkt het controlecijfer (handig om typfouten in je systeem te vangen):

1. Zet elke letter om naar een getal (C = 13, S = 30, Q = 28, U = 32). De getallen 11, 22 en 33 worden overgeslagen.
2. Vermenigvuldig elk getal met 2 tot de macht van zijn plek (1, 2, 4, 8, 16 ...).
3. Tel alles op. Hier: 6.185.
4. Deel door 11. De rest is het controlecijfer. Hier: 3. Bij rest 10 wordt het cijfer 0 ([Wikipedia ISO 6346](https://en.wikipedia.org/wiki/ISO_6346)).

Daarnaast heeft elke container een type-code van 4 tekens. De eerste twee tekens zeggen lengte en hoogte, de laatste twee het type.

| Code | Betekenis |
|---|---|
| 22G1 | 20ft, 8'6" hoog, algemeen (dry) |
| 42G1 | 40ft, 8'6" hoog, algemeen |
| 45G1 | 40ft, 9'6" hoog (High Cube), algemeen. Dit is dus **geen** 45ft |
| 45R1 | 40ft High Cube reefer |
| 22R1 | 20ft reefer |
| 22U1 | 20ft open top |
| 22P1 | 20ft flat met vaste koppen |

Bron: [Wikipedia ISO 6346](https://en.wikipedia.org/wiki/ISO_6346). De nieuwere codering uit 2022 geeft 45ft mogelijk een andere code. Dat is niet bevestigd (**Open**). Sla in je systeem maat (20/40/45) en type (DC/HC/reefer/tank/...) daarom apart op en leid ze niet af van de code.

### 2.3 Gewicht: VGM, plaatje en "zware container"

- **VGM** is verplicht sinds 1 juli 2016. De afzender geeft het gewicht door aan de rederij. Methode 1 is wegen. Methode 2 is optellen (lading + pallets + stuwmateriaal + tarra). Zonder VGM wordt de container niet op het schip geladen ([GOV.UK](https://www.gov.uk/government/publications/verified-gross-mass-of-containers)).
- **In Nederland** mag de VGM 500 kg (onder 10 ton) of 5% (vanaf 10 ton) afwijken. Er is geen vaste deadline. Zonder VGM komt de container meestal wel op de terminal, maar wordt hij niet geladen ([Port of Rotterdam](https://www.portofrotterdam.com/en/logistics/cargo/containers/mandatory-container-weighing-port-rotterdam)). Die tolerantie geldt voor de zee. Ze is geen vrijbrief voor de weg (Schatting).
- **De lading staat op de deur.** Het toegestane lading-gewicht staat op de rechter achterdeur. Het hangt af van de tarra ([Rothschenk](https://rothschenk.de/en/sequence-19-combined-traffic/)).
- **Zware container.** Ik vond geen officiële regel voor wat "overweight" is. Mijn lezing: een zware 20ft is een 20ft van bijna 30 ton bruto die niet past op een gewoon chassis met 2 assen. Dan is een chassis met 3 of 4 assen nodig (**Schatting**, zie hoofdstuk 5).
- **Overbelading is een bekend probleem**, maar de bronnen zijn oud of zijn meningen ([Rijkswaterstaat 1997](https://open.rijkswaterstaat.nl/@124359/containers-vrachtwagens-paar-apart/), [Rothschenk](https://rothschenk.de/en/sequence-19-combined-traffic/)).

### 2.4 Gevaarlijke stoffen en koellading

- **ADR.** Bij gevaarlijke stoffen heeft de chauffeur een ADR-certificaat nodig. Het bedrijf heeft een veiligheidsadviseur nodig. Bepaalde voertuigen moeten gekeurd zijn. Bij vervoer dat over zee verder gaat is een containerbeladingscertificaat (CPC) nodig ([Ondernemersplein](https://ondernemersplein.overheid.nl/wetten-en-regels/gevaarlijke-stoffen-vervoeren-over-de-weg/)).
- **IMDG en ADR.** ADR accepteert IMDG-documenten. Alle andere ADR-eisen blijven gelden op de weg ([HSE](https://www.hse.gov.uk/CDG/commonproblems/adr-imdg.htm), Britse bron).
- **Tunnels.** Rotterdam heeft tunnels met ADR-categorie: Maastunnel D, Botlektunnel D, Beneluxtunnel C, Heinenoordtunnel C, Drechttunnel C, Kiltunnel C ([evofenedex](https://www.evofenedex.nl/api/v1/sharepoint/file/Shared%20Documents/Download%20Gevaarlijke%20Stoffen/ADR-tunneloverzicht%20Nederland%202026.pdf)). Welke stoffen per categorie mogen, is **Open**.
- **Reefers** hebben stroom nodig: een stopcontact (plug) of een aggregaat (genset) op het chassis. Maersk rekent daar kosten voor (hoofdstuk 8).

---

## 3. Trekker en chassis: de combinatie hangt aan gewicht en lengte

### 3.1 De trekker

De code 4x2, 6x2 of 6x4 zegt hoeveel wielposities de trekker heeft en hoeveel daarvan worden aangedreven. 4x2 is een trekker met 2 assen waarvan 1 wordt aangedreven. 6x2 en 6x4 hebben 3 assen. Bij 6x2 wordt 1 as aangedreven, bij 6x4 worden er 2 aangedreven.

Wat een trekker leeg weegt, welke aslast hij heeft en welke combinaties per type zijn toegestaan, kon ik **niet** uit bronnen halen (**Open**). Kässbohrer zegt alleen welke trekker bij welk chassis hoort (zie hieronder). Dit is het belangrijkste ontbrekende getal voor een gewichtsberekening.

### 3.2 Chassistypes

De cijfers komen uit de Kässbohrer-brochure voor de Nederlandse markt (ca. 2021, afgeleid uit de bestandsnaam) en van Broshuis ([Kässbohrer](https://kaessbohrer.com/static/media/category/585/attachments/container-chassis-nl-digi_210518_1409.pdf), [Broshuis](https://directindustry.com/prod/broshuis-bv/product-201391-2296130.html)).

| Chassis | Voor welke container | Leeg (kg) | Opmerking |
|---|---|---|---|
| Vast 20ft (K.SHF S/20) | 1 x 20ft | 3.450 | Voor 4x2-trekker |
| Tankchassis (T/20, T/30) | 20ft tank, 20-30ft | 3.200 en 3.540 | Voor 4x2-trekker |
| Vast 40ft vlak (K.SHF S/40) | 40ft (45ft met achteruitbreiding) | 4.540 | 4x2, 6x2 of 6x4 |
| Vast gooseneck 40ft (K.SHG S/40) | 40ft High Cube | 4.520 | 4x2, 6x2 of 6x4 |
| Uitschuifbaar (AH/40, AVH/45, AMH/40, AVMH/45) | 20, 30, 40 of 45ft | 5.050 - 5.130 | Veel flexibiliteit, zwaarder |
| Lichtgewicht gooseneck 45ft (L/45, M/45, UL/45) | 45ft | 3.600 - 3.940 | Lager gewicht, meer lading |
| 4-assig gooseneck (S/40 11/36) | Zware 20ft of 40ft | 5.880 | Asgroep 36 t, kingpin 11 t |
| Broshuis MFCC HD (multi) | 20 tot 45ft | 5.300 | Max lading 37.700 kg, kingpin 16 t, bogie 3 x 9 t |

Meer feiten:

- **Lengtes.** Vast 20ft-chassis 7.235 mm. Vast 40ft 12.515 - 12.730 mm. Koppelhoogte (kingpin) 1.100 - 1.250 mm ([Kässbohrer](https://kaessbohrer.com/static/media/category/585/attachments/container-chassis-nl-digi_210518_1409.pdf)).
- **Hoogte.** Kingpin van ca. 1,1 m plus een HC-container van 2,896 m is ca. 4,0 m. Dat past precies onder de maximale hoogte van 4,00 m (mijn rekensom, **Schatting**).
- **Side loader** (zelflader, bijvoorbeeld Hammar) heeft kranen aan beide kanten. Hij laadt en lost zelf: 1 x 20ft, 1 x 40ft of 2 x 20ft op een chassis van 40ft of langer. In havens zijn andere machines gebruikelijker ([Wikipedia](https://en.wikipedia.org/wiki/Sidelifter)).
- **Twistlocks** (de sloten in de hoekgutsen) zitten op alle acht hoeken van de container ([Wikipedia](https://en.wikipedia.org/wiki/Intermodal_container)). Waar ze precies zitten bij een 20ft op een 40ft-chassis, is **Open**.
- **Merken.** Bevestigd: Kässbohrer, Schmitz Cargobull, Broshuis, Hammar. Andere merken (o.a. Pacton, Renders, Krone, Kögel) zijn niet gecontroleerd.

### 3.3 Welke combinatie voor welke container

Dit is mijn afleiding uit de tabel hierboven, geen bronfeit (**Schatting**).

| Container | Waarschijnlijke combinatie | Let op |
|---|---|---|
| 1 x 40ft HC | Vast 40ft- of gooseneck-chassis (4.520 - 4.540 kg), of multi-chassis (5.100 - 5.300 kg) | Hoogte met kingpin ca. 4,0 m |
| 2 x 20ft | Uitschuifbaar of multi-chassis (5,0 - 5,3 t) | Beide containers tellen mee in het gewicht (hoofdstuk 5) |
| 1 x 45ft HC | 45ft-chassis (3.600 - 3.940 kg) of uitschuifbaar (5.100 kg) | Lengte: zie hoofdstuk 4 |
| 20ft tank | Tankchassis (3.200 - 3.540 kg) | ADR-regels bij gevaarlijke stof |
| Zware 20ft | 3- of 4-assig chassis (bijv. 5.880 kg) | Aslasten (hoofdstuk 5) |
| Reefer | Chassis met genset of stroom op locatie | Genset kost extra |

**Open (geen bron gevonden):** kipper-chassis (container kantelen voor bulk), swap bodies (afmetingen en gewichten), haakarm- en kabelsysteem, kraanwagens (Hiab), 'mega-trailers' met lage koppelhoogte, tandem 20ft (twee 20ft achter elkaar) en reefer-genset (gewicht en plaatsing).

---

## 4. Wettelijke maten en gewichten: NL 50 ton, Duitsland meestal 40 ton

Elk land heeft eigen regels. Je systeem moet de regels kennen van het land waar de route doorheen gaat.

### 4.1 Nederland: maten

Bron: [OM-instructie 2021I003](https://www.om.nl/onderwerpen/b/beleidsregels/instructies/verkeer/instructie-voertuigafmetingen-2021i003) en het [RDW-overzicht](https://cuatro.sim-cdn.nl/fryslan/uploads/Overzicht-maten-en-gewichten%20%28RDW%29.pdf). Het RDW-overzicht is een samenvatting uit maart 2012 ("geen rechten aan te ontlenen"). De OM-instructie is actueler. De Regeling voertuigen zelf is niet gelezen.

| Wat | Maximum | Boete-grens (proces-verbaal) | Status |
|---|---|---|---|
| Hoogte | 4,00 m | boven 4,05 m (leeg voertuig: boven 4,01 m) | Bevestigd |
| Breedte | 2,55 m (2,60 m geconditioneerd, zoals reefer) | Marge 10 cm | Bevestigd |
| Trekker + oplegger | 16,50 m | boven 16,70 m | Bevestigd |
| Trekker + oplegger met 45ft-container | 17,30 m | boven 17,31 m | Bevestigd |
| Vrachtwagen + aanhanger | 18,75 m | boven 18,95 m | Bevestigd |
| Oplegger, koppelplaat tot achterkant | 12,00 m | n.v.t. | Bevestigd |
| LZV | 25,25 m | n.v.t. | Bevestigd ([RDW](https://www.rdw.nl/zakelijke-partners/exceptioneel-transport/ontheffing-aanvragen-voor-exceptioneel-transport/aanvragen-jaarontheffing-lzv)) |

### 4.2 Nederland: gewichten

- **Maximum 50.000 kg** voor een gewone combinatie. Overschrijden is strafbaar ([government.nl](https://government.nl/topics/freight-transportation/requiremenst-for-lorries)).
- **Het echte maximum is lager of gelijk.** Het is de laagste van: 50 t, vijf keer de toegestane last op de aangedreven as, en het motorvermogen gedeeld door 0,002 kW/kg (combinatie). Bij moderne trucks is het vermogen zelden de beperking (Schatting). De waarde op het kentekenbewijs gaat voor. Staat er niets, dan geldt 50.000 kg ([OM bijlage 3](https://www.om.nl/binaries/om/documenten/richtlijnen/2022/12/13/tabel-toegestane-maximummassa-en-aslasten-buitenlandse-voertuigen/Bijlage+3+bij+Instructie+wegingen+en+wiellastmetingen+%282022I006%29.pdf), [OM 2022I006](https://www.om.nl/onderwerpen/b/beleidsregels/instructies/verkeer/instructie-wegingen-en-wiellastmetingen-2022i006)).

**Aslasten (kg)** ([RDW-overzicht](https://cuatro.sim-cdn.nl/fryslan/uploads/Overzicht-maten-en-gewichten%20%28RDW%29.pdf), [OM bijlage 3](https://www.om.nl/binaries/om/documenten/richtlijnen/2022/12/13/tabel-toegestane-maximummassa-en-aslasten-buitenlandse-voertuigen/Bijlage+3+bij+Instructie+wegingen+en+wiellastmetingen+%282022I006%29.pdf)):

| As | Niet aangedreven | Aangedreven |
|---|---|---|
| Enkele as | 10.000 | 11.500 |
| Tandem (2 assen), afstand onder 1,00 m | 11.000 | 11.500 |
| Tandem, afstand 1,00 tot 1,30 m | 16.000 | 16.000 |
| Tandem, afstand 1,30 tot 1,80 m | 18.000 | 18.000 (19.000 met dubbellucht en luchtvering) |
| Tridem (3 assen) | 7.000 per as (onder 1,30 m); 8.000 per as (1,30 tot 1,80 m) | Zie opmerking |

- **Tridem.** De asgroep van een tridem is 24.000 kg. In de bronnen staat ook 9.000 kg per as bij luchtvering (3 x 9 = 27.000 kg). Wanneer 27 ton precies mag, is in de bronnen onduidelijk (**Open**). Het Broshuis-chassis heeft technisch een bogie van 3 x 9 t. Reken voorzichtig met 24 t.
- **De 1/5-regel.** Een deel van de last moet op de aandrijfas en op de koppelplaat staan. In mijn notities staat op één plek "aandrijfas minstens 1/5 van het totaalgewicht" en op een andere plek "stuuras". De OM-regel (5 x de toegestane last op de aangedreven as) past bij de **aandrijfas**. Ik gebruik die. Controleer dit (**Open**).
- **Handhaving.** Meer dan 5% over het totaalgewicht geeft een proces-verbaal. Meer dan 10% geeft ook een "overladen"-maatregel: je mag pas doorrijden als je lading hebt verminderd. Bij een aslast is dat 10% en 20%. De weegbrug rekent een correctie van 20 tot 60 kg ([OM 2022I006](https://www.om.nl/onderwerpen/b/beleidsregels/instructies/verkeer/instructie-wegingen-en-wiellastmetingen-2022i006)). De boetebedragen zijn **Open**.

### 4.3 LZV en andere Nederlandse regels

- **LZV** (25,25 m, 60 ton) mag alleen met een RDW-ontheffing op het kenteken van de trekker. Die kost € 160 per kenteken per jaar. De chauffeur heeft een CCV-certificaat nodig. De combinatie mag alleen over het groene LZV-netwerk op de Digitale Wegenkaart Ontheffingen. Buiten dat netwerk is een aparte ontheffing nodig (€ 132 per 4 kentekens). RDW beslist binnen 5 werkdagen ([RDW](https://www.rdw.nl/zakelijke-partners/exceptioneel-transport/ontheffing-aanvragen-voor-exceptioneel-transport/aanvragen-jaarontheffing-lzv)). Elk EU-land beslist zelf over LZV ([Stimular](https://www.stimular.nl/maatregelen/grotere-of-lichtere-vrachtautos)).
- **LZV met containers** (bijvoorbeeld 2 x 40ft of 3 x 20ft): de RDW-pagina noemt containers niet. **Open.**
- **Rijverboden.** Nederland heeft geen algemeen weekend- of feestdagenverbod voor vrachtwagens (secundaire bron: [Impargo](https://impargo.de/en/blog/truck-driving-bans-europe)). Er is wel een inhaalverbod voor vrachtverkeer op ca. 950 km snelweg ([Rijkswaterstaat](https://www.rijkswaterstaat.nl/wegen/wetten-regels-en-vergunningen/verkeerswetten/inhaalverbod-vrachtverkeer)).
- **Wekelijkse rust in de cabine** is verboden en wordt gehandhaafd ([government.nl](https://government.nl/topics/freight-transportation/requiremenst-for-lorries)).
- **Maastunnel.** Een NOS-bericht van november 2024 zegt dat de doorrijhoogte van 4,0 m naar 3,9 m gaat ([NOS](https://nos.nl/l/2546194)). Ik heb alleen de kop gezien. Of dit is ingevoerd, is **Open**. Voor een HC-combinatie van ca. 4,0 m is dit belangrijk.

### 4.4 EU: het is nog niet wat het wordt

De huidige EU-richtlijn 96/53/EG kon niet worden opgehaald. De getallen 40 t en 44 t en de hoogte van 4,00 m heb ik afgeleid uit de Raadstekst en het Duitse StVZO. Dat is betrouwbaar, maar niet uit de richtlijn zelf.

- **Gecombineerd vervoer (intermodaal):** 42 t met een 2-assige trekker. 44 t met een 3-assige trekker ([Rothschenk](https://rothschenk.de/en/sequence-19-combined-traffic/)). Dit geldt over de grens.
- **Herziening.** De Commissie stelde dit voor op 11 juli 2023. Het Europees Parlement stemde op 12 maart 2024. De Raad nam een standpunt in op 4 december 2025. Sinds 9 december 2025 wordt onderhandeld. Op 25 oktober 2026 was er geen akkoord ([Europarl](https://www.europarl.europa.eu/legislative-train/theme-a-european-green-deal/file-revision-of-the-weights-and-dimensions-directive)).
- **Wat de Raadstekst wil.** Emissievrije voertuigen krijgen +2 of +4 ton. Hoogte blijft 4,00 m (de extra hoogte voor High Cube is geschrapt). 45ft-containers in intermodaal vervoer krijgen +0,15 m lengte ([Raadsdocument](https://data.consilium.europa.eu/doc/document/ST-15611-2025-INIT/en/pdf)).
- **Wat dat betekent.** Het is nog geen wet en moet daarna nog 2 jaar worden omgezet. Voor je planning verandert er in 2027 waarschijnlijk niets (Schatting).

### 4.5 België, Duitsland, Frankrijk, Luxemburg

| Land | Maximaal gewicht | Verbodsdagen | Tol (>32 t, Euro 6, CO2-klasse 1) | Status |
|---|---|---|---|---|
| **Duitsland** | 40 t (5+ assen). 42 t (2-assige trekker + 3-assige oplegger, intermodaal). 44 t (3-assige trekker, intermodaal, containers tot 45ft). Tridem 21 t (as-afstand tot 1,3 m) of 24 t (1,3 - 1,4 m) ([§ 34 StVZO](https://www.gesetze-im-internet.de/stvzo_2012/__34.html)) | Zon- en feestdagen 00:00 - 22:00 voor wagens boven 7,5 t. Uitzondering: haven-weg binnen 150 km, spoor-weg tot 200 km ([§ 30 StVO](https://www.gesetze-im-internet.de/stvo_2013/__30.html)) | 34,8 ct/km voor 5+ assen (tarief sinds 1 juli 2024) ([Toll Collect](https://toll-collect.de/en/toll_collect/bezahlen/maut_tarife/p1745_mauttarife_07_2024.html)) | Bevestigd, tekst via samenvatting |
| **België (Vlaanderen)** | 44 t standaard. Tot 48 t onder zware voorwaarden. Tot 50 t voor emissiearm ([Vlaanderen.be](https://www.vlaanderen.be/mobiliteit-en-openbare-werken/vrachtverkeer/tonnageverhoging-voor-vrachtverkeer)) | Geen algemeen zondagsverbod (secundair: [Impargo](https://impargo.de/en/blog/truck-driving-bans-europe)) | 0,132 euro/km ([Viapass](https://viapass.be/en/rates/)) | Bevestigd; Wallonië en Brussel **Open** |
| **Frankrijk** | **Open** | Vanaf 22:00 op de dag voor een zon- of feestdag tot 22:00 op de dag zelf (boven 7,5 t). Zomer: zaterdag 07:00 - 19:00 ([Impargo](https://impargo.de/en/blog/truck-driving-bans-europe)) | Grand Est vanaf 2027 ([trans.info](https://trans.info/de/lkw-maut-2027-neue-regeln-fuer-europas-transporteure-507770)) | Gewicht **Open**; verbod secundair |
| **Luxemburg** | **Open** | Doorgaand verkeer boven 7,5 t: richting Frankrijk zaterdag 21:30 - 24:00 en zon- en feestdagen tot 21:45 ([Impargo](https://impargo.de/en/blog/truck-driving-bans-europe)) | **Open** | Alles **Open** of secundair |

Dingen om extra op te letten in Duitsland:

- **De 150 km-eis.** Volgens een samenvatting van het StVZO mag het wegdeel bij voor- of natransport over zee of binnenvaart voor de 44 t-regel maximaal 150 km zijn ([§ 34 StVZO](https://www.gesetze-im-internet.de/stvzo_2012/__34.html)). Rotterdam - Duisburg is ca. 220 km (mijn schatting, hoofdstuk 9). Of 44 t dan nog mag, is niet uitgezocht en is een groot risico (**Open**).
- **25% op de aandrijfassen.** De samenvatting noemt bij grensoverschrijdend vervoer minimaal 25% van het totaalgewicht op de aandrijfassen. Dat is meer dan de Nederlandse 1/5 (20%). Controleer dit (**Open**).
- **Feestdagen.** Impargo noemt andere dagen dan de wettekst (bijvoorbeeld 6 januari, 15 augustus en 18 november). Gebruik de officiële lijst per deelstaat ([§ 30 StVO](https://www.gesetze-im-internet.de/stvo_2013/__30.html)).
- **Zomerverbod op zaterdag.** Impargo noemt 1 juli - 31 augustus, een EU-studie uit 2010 noemt 3 juli - 28 augustus. De officiële regeling (Ferienreiseverordnung) is niet gevonden (**Open**).
- **Tijdelijke uitzondering.** In augustus 2026 was het zondagsverbod opgeschort in meerdere deelstaten wegens laag water in de Rijn, tot 31 augustus. Er is geen verlenging gemeld ([ANWB](https://www.anwb.nl/verkeer/nieuws/buitenland/2026/augustus/tijdelijk-vrachtverkeer-op-zondag-in-duitsland)).

---

## 5. Rekenvoorbeeld: bij 44 ton blijft ongeveer 27 ton lading over

Hoeveel lading mag er echt in? Gebruik deze formule:

**Max lading = max gewicht combinatie - trekker - chassis - lege container**

Rothschenk beschrijft dezelfde formule en adviseert de lege combinatie te wegen ([Rothschenk](https://rothschenk.de/en/sequence-19-combined-traffic/)).

### Voorbeeld 1: één 40ft High Cube

| Onderdeel | Gewicht (kg) | Bron en status |
|---|---|---|
| Trekker | 8.000 | **Schatting.** Geen bron. Echte waarde: "massa rijklaar" op het kentekenbewijs |
| Chassis, vast 40ft | 4.540 | Bevestigd ([Kässbohrer](https://kaessbohrer.com/static/media/category/585/attachments/container-chassis-nl-digi_210518_1409.pdf)) |
| Lege 40ft HC | 4.150 | Bevestigd ([DHL](https://www.dhl.com/nl-en/home/global-forwarding/freight-forwarding-education-center/cargo-container-sizes-and-types.html)) |
| **Lege combinatie samen** | **16.690** | Som |

| Grens | Max combinatie (kg) | Max lading (kg) | Past 26.330 kg (de lading op papier)? |
|---|---|---|---|
| Nederland algemeen | 50.000 | 33.310 | Ja, maar let op aslasten |
| Intermodaal, 3-assige trekker | 44.000 | 27.310 | Ja, net |
| Intermodaal, 2-assige trekker | 42.000 | 25.310 | Nee |
| Duitsland normaal (5+ assen) | 40.000 | 23.310 | Nee |

Alle uitkomsten zijn **Schatting**, omdat de trekker een aanname is. Hoe gevoelig is dat? Zo verandert de maximale lading (kg) als de trekker lichter of zwaarder is:

| Grens | Trekker 7.000 kg | Trekker 8.000 kg | Trekker 9.000 kg |
|---|---|---|---|
| 50.000 kg | 34.310 | 33.310 | 32.310 |
| 44.000 kg | 28.310 | 27.310 | 26.310 |
| 42.000 kg | 26.310 | 25.310 | 24.310 |
| 40.000 kg | 24.310 | 23.310 | 22.310 |

Wat zie je?

- Een volle 40ft HC (26.330 kg lading) past bij 44 ton alleen als de trekker maximaal 8.980 kg weegt (44.000 - 4.540 - 4.150 - 26.330). Een 3-assige trekker is zwaarder. Dan blijft er minder over.
- Bij 42 ton moet de trekker lichter zijn dan 6.980 kg. Dat lukt waarschijnlijk niet.
- Elke 1.000 kg minder tarra aan trekker of chassis is 1.000 kg meer lading.

**Het totaalgewicht is niet genoeg: kijk ook naar de assen.** Tel de maximale aslasten uit hoofdstuk 4 op voor een 2-assige trekker met een 3-assig chassis: 10 t (stuuras) + 11,5 t (aangedreven as) + 24 t (tridem) = 45,5 t. Mag de tridem 27 t dragen, dan is het 48,5 t. Voor 50 ton heb je dus een trekker met meer assen nodig. Dit is mijn eigen optelsom (**Schatting**). Daarbovenop moet de aandrijfas minstens 1/5 van het totaal dragen. Zware lading ver naar achteren overbelast de tridem. Ver naar voren overbelast de koppelplaat (Schatting).

### Voorbeeld 2: twee 20ft op één chassis

Trekker 8.000 (aanname) + Broshuis MFCC HD 5.300 + 2 x lege 20ft van 2.250 = 4.500. Lege combinatie: 17.800 kg.

- Bij 44.000 kg: 26.200 kg lading voor beide containers samen.
- Bij 50.000 kg: 32.200 kg.

Twee zware 20ft (op papier elk ca. 28 t lading) kunnen dus nooit allebei vol mee. De containers delen het wegbudget ([Broshuis](https://directindustry.com/prod/broshuis-bv/product-201391-2296130.html) voor het chassis, **Schatting** voor de rest).

### Voorbeeld 3: één zware 20ft

Een 20ft van 30.480 kg bruto op een vast 20ft-chassis (3.450 kg) met een trekker van 8.000 kg (aanname) is samen 41.930 kg. Dat past binnen 44 ton. Stel dat het chassis 2 assen heeft (het aantal assen staat niet in de brochure). Dan is de grens voor de assen 10 + 11,5 + 18 (tandem, 1,30 tot 1,80 m) = 39,5 t. Je zit dan 2.430 kg te zwaar. Een chassis met 3 assen lost dat op. Dat is de reden dat zware 20ft vaak een tridem-chassis vragen (**Schatting**).

### Wat dit betekent voor het systeem

Per container heb je nodig: de VGM (het echte gewicht), de tarra van de lege container, het chassis-gewicht en het trekkergewicht. Daarnaast de limiet van elk land op de route en de aslast. De VGM-tolerantie (500 kg of 5%) is een zeevaartregel en geen toestemming om op de weg te zwaar te rijden.

---

## 6. Rij- en rusttijden: 9 uur rijden en een harde klok voor rust

### 6.1 De EU-regels (Verordening 561/2006)

| Regel | Waarde | Status |
|---|---|---|
| Rijtijd per dag | 9 uur. Twee keer per week 10 uur | Bevestigd |
| Rijtijd per week | Maximaal 56 uur | Bevestigd |
| Rijtijd per 2 weken | Maximaal 90 uur | Bevestigd |
| Pauze | 45 minuten na 4,5 uur rijden. Mag in 2 delen: eerst minimaal 15, dan minimaal 30 minuten | Bevestigd |
| Dagelijkse rust | 11 uur. Verkort 9 uur (volgens een Nederlandse bron maximaal 3 keer tussen twee weekrusten). Moet starten binnen 24 uur na het einde van de vorige rust. Splitsen mag als 3 + 9 uur (niet andersom) | Bevestigd |
| Wekelijkse rust | Regulier minimaal 45 uur. Verkort minimaal 24 uur, met compensatie. De volgende weekrust start uiterlijk na 6 x 24 uur. In 4 weken minimaal 4 weekrusten, waarvan minimaal 2 regulier | Bevestigd |
| Weekrust in de cabine | Een reguliere weekrust mag niet in de cabine. Het bedrijf betaalt een geschikte slaapplek | Bevestigd |
| Terugkeer chauffeur | Binnen 3 weken naar huis of naar het bedrijf (4 weken na twee verkorte rusten). Geldt voor werknemers | Bevestigd |
| Controle | De chauffeur moet de gegevens van vandaag en de vorige 56 dagen kunnen tonen | Bevestigd ([business.gov.nl](https://business.gov.nl/international/international-transport/new-rules-for-international-transport-and-drivers/)) |

Bronnen: [Europese Commissie](https://transport.ec.europa.eu/transport-modes/road/mobility-package-i/driving-rest-times_en) en [Rijksoverheid](https://www.rijksoverheid.nl/themas/werk/arbeidsomstandigheden/vraag-en-antwoord/werktijden/rijtijden-en-rusttijden-wegvervoer).

### 6.2 Tachograaf, cabotage en detachering

- **Slimme tachograaf (G2V2).** Nieuwe voertuigen vanaf 21 augustus 2023. Voertuigen in internationaal vervoer met een eerste-versie slimme tachograaf uiterlijk 18 augustus 2025. Bestelwagens boven 2,5 ton in internationaal vervoer uiterlijk 1 juli 2026 ([Europese Commissie](https://transport.ec.europa.eu/news-events/news/stronger-and-more-unified-enforcement-eu-rules-international-road-transport-smart-tachograph-2025-08-19_en)). G2V2 doet automatische grensregistratie.
- **Cabotage** (binnenlands werk in een ander land): maximaal 3 ritten in 7 dagen. Daarna 4 dagen wachten in hetzelfde land ([business.gov.nl](https://business.gov.nl/international/international-transport/new-rules-for-international-transport-and-drivers/)).
- **Detachering.** Wie in het buitenland werkt, heeft recht op het loon van dat land. Of pure heen-en-terugritten (Rotterdam - Duisburg) onder de uitzondering vallen, is **Open**.

### 6.3 Een tegenstrijdigheid die je moet kennen

De Nederlandse ondernemersportal noemt nog de regel dat het **voertuig** elke 8 weken terug moet naar het bedrijf ([business.gov.nl](https://business.gov.nl/international/international-transport/new-rules-for-international-transport-and-drivers/)). Het Hof van Justitie heeft die regel op 4 oktober 2024 vernietigd. De terugkeerplicht voor **chauffeurs** (3 - 4 weken) en het verbod op weekrust in de cabine blijven wel gelden ([Hof van Justitie](https://curia.europa.eu/jcms/upload/docs/application/pdf/2024-10/cp240173en.pdf)). De portal is waarschijnlijk niet bijgewerkt (Schatting). Of de Commissie een nieuw voorstel deed, is **Open**.

### 6.4 Nederlandse arbeidstijd en cao

- **Werktijd telt ook laden, lossen en wachten.** Bij 6 tot 9 uur werk: minimaal 30 minuten pauze. Bij meer dan 9 uur: minimaal 45 minuten. Nooit meer dan 6 uur werken zonder pauze. Pauzes mogen in stukken van 15 minuten ([Rijksoverheid](https://www.rijksoverheid.nl/themas/werk/arbeidsomstandigheden/vraag-en-antwoord/werktijden/rijtijden-en-rusttijden-wegvervoer)).
- **Rooster.** De cao heeft bijna geen roosterafspraken. Dan geldt: het rooster moet minimaal 28 dagen vooraf bekend zijn. In uitzonderingen moeten de werktijden minimaal 4 dagen vooraf bekend zijn ([CNV](https://www.cnv.nl/vervoer/vervoer-en-logistiek/cao-beroepsgoederenvervoer/nieuws/cao-bgv-ken-je-cao-2026-nr-6-roosters-2026-09-01/)). Containerplanning gaat vaak per dag. Dat botst met deze regel. Hoe bedrijven dat oplossen is **Open**.
- **Cao Beroepsgoederenvervoer 2026:** +4% per 1 januari 2026. Overwerk zijn alle uren boven de contracturen per week, met 30% toeslag. Nachttoeslag voor werk tussen 21:00 en 05:00 ([CNV](https://www.cnv.nl/vervoer/vervoer-en-logistiek/cao-beroepsgoederenvervoer/01-01-2026_31-12-2026/)). Loonschalen en vergoedingen zijn niet gelezen (**Open**).

### 6.5 Wat betekent dit voor containerritten?

- **Wachten telt als werktijd, niet als rust** (Schatting; de bronnen noemen geen aparte terminalregel).
- **Mijn voorbeeld wijst iets anders aan dan mijn notities.** De notities zeiden dat de 9 uur rijtijd bij korte havenritten meestal de beperking is. In mijn voorbeeld-ritdag (hoofdstuk 10) rijdt de chauffeur maar 5,5 uur. De beperking is daar de lengte van de dienst: 11,5 uur werk, vooral door wachten en lossen. Dat is niet gecontroleerd met een echt bedrijf (**Open**).
- **Een dienst is begrensd.** Een nieuwe dagrust moet starten binnen 24 uur na de vorige rust. Met 11 uur rust is een dienst dus maximaal 13 uur lang (24 - 11). Met 9 uur verkorte rust maximaal 15 uur (Schatting, afgeleid uit de regels hierboven).

---

## 7. Rotterdam: alles gaat via Portbase, een slot en een pasje

Rotterdam verwerkte in 2025 **14,2 miljoen TEU** ([Port of Rotterdam](https://www.portofrotterdam.com/en/node/1164)). Dat is ca. 30% van alle containers in Noordwest-Europa ([Port of Rotterdam](https://www.portofrotterdam.com/en/news-and-press-releases/between-growth-and-pressure-rotterdams-2025-container-year-under-review)). Op de Maasvlakte liggen vijf diepzeeterminals.

### 7.1 Terminals

| Terminal | Adres (havennummer) | Eigenaar of rol | Trucks en slots |
|---|---|---|---|
| ECT Delta | Europaweg 875 (8202) | Hutchison Ports | Open voor trucks 24 uur. Slotsysteem TCMS ([ECT](https://www.ect.nl/en/services/road-services)) |
| ECT Euromax | Maasvlakteweg 951 (9830) | Hutchison Ports | 24 uur. TCMS. Deel van de kade is vanaf 10 april 2026 beperkt door nieuwe kranen. Op 1 mei 2026 opende een "Pre Security-in Truck Buffer" voor pieken ([ECT](https://www.ect.nl/en/news-feed)) |
| Hutchison Ports Delta II | Coloradoweg 50 (8203) | Hutchison (voorheen APMT-Rotterdam) | Niet bij TCMS. Slots en openingstijden **Open** ([Hutchison](https://hutchisonports.com/ports/world/hutchison-ports-delta-ii/)) |
| APM Terminals Maasvlakte II | Europaweg 910 (lijst uit 2021) | Maersk. Hapag-Lloyd nam rond 10 nov 2026 25% over. Geautomatiseerd | 24 uur, behalve 24 dec 15:00 - 26 dec 07:00 en 31 dec 15:00 - 1 jan 15:00 ([APMT](https://www.apmterminals.com/en/maasvlakte/e-tools/online-services), [Cyprus Shipping News](https://cyprusshippingnews.com/2026/11/10/hapag-lloyd-completes-acquisition-of-25-stake-in-apm-terminals-maasvlakte-ii/)) |
| RWG (Rotterdam World Gateway) | Amoerweg 50 (8970) | ONE, HMM, CMA CGM, DP World | Openingstijden **Open** ([RWG](https://www.rwg.nl/en/about-rwg)) |

Andere terminals en depots (shortsea, barge, lege containers) liggen in Waalhaven, Eemhaven, Botlek en op de Maasvlakte. De lijst van het Havenbedrijf uit april 2021 is de enige gedetailleerde bron (o.a. Matrans, Broekman Distriport, Kramer Delta Depot, United Waalhaven Terminals). Actuele eigenaren zijn niet gecontroleerd ([Port of Rotterdam 2021](https://www.portofrotterdam.com/sites/default/files/2021-06/container-terminals-and-depots-in-the-rotterdam-port-area.pdf)). De **Container Exchange Route** is een gesloten weg van 17 km op de Maasvlakte tussen RWG, ECT Delta, de Kramer-terminals en de Staatsinspectieterminal ([Port of Rotterdam](https://portofrotterdam.com/en/node/1012)).

Voor een planner zijn er vier clusters met eigen regels: ECT (Delta + Euromax), Delta II, APMT en RWG (Schatting).

### 7.2 Portbase en pre-notificatie

**Portbase** is het digitale systeem van de haven. Je gebruikt vooral **HCN Road** (Hinterland Container Notification Road). In terminal-documenten heet het ook "MCA Road" of "Road Planning". Daarmee meld je vooraf welke truck, chauffeur en container komen. Je krijgt automatisch statusberichten. Bij sommige terminals vraag je tegelijk een slot aan ([Portbase](https://www.portbase.com/en/services/hinterland-container-notification-road/), [ECT](https://myterminal.ect.nl/help-center/features/pages/timeslots)).

| Wat | Bedrag (zonder btw) |
|---|---|
| Eenmalig aansluiten | € 249,50 |
| Per maand (inland operator) | € 11,36 (vanaf 1 jan 2027: € 11,70) |
| Per pre-notificatie van een volle container | € 0,40 (vanaf 1 jan 2027: € 0,41) |
| Tarief van de terminal zelf | Verschilt per terminal |

Bron: [Portbase](https://www.portbase.com/en/services/hinterland-container-notification-road/).

**Koppelen met je eigen systeem (API)** ([Portbase HCN API](https://hcn.pcs.portbase.com/api-documentation/connection_instructions.html)):

- JSON-berichten. Je krijgt een client ID en client secret van Portbase.
- Eerst testen in een testomgeving. Daarna productie.
- Statusberichten haal je op met "long polling", niet met een webhook. De oude push-methode is verouderd.
- Handlingtypes: volle container laden of lossen, lege container laden of lossen (full/unload, full/load, empty/unload, empty/load). Het boekingsnummer is verplicht. Bij sommige terminals mag het containernummer ontbreken bij een lege container ("loading on size type").
- De aanvraag voor toegang doet de klant (het transportbedrijf), niet de softwareleverancier. Je hebt een IAMconnected-account en een EAN-nummer nodig ([Portbase](https://www.portbase.com/en/services/hinterland-container-notification-road/)).
- Of een gewone trucker (geen "inland operator") API-toegang krijgt tot **Cargo Controller** (release en douanestatus), is niet bevestigd (**Open**).

**Welke terminals doen mee?** Portbase noemt 20 locaties, o.a. APMT MVII, ECT Delta, ECT Euromax, Delta II, RWG, RCT, Matrans en Broekman. Per terminal verschilt of pre-notificatie verplicht of optioneel is. Die symbolen waren niet leesbaar (**Open**) ([Portbase](https://portbase.com/en/?p=10109)).

**TAR.** Dat is het afspraaknummer dat je bij het slot krijgt. Bij APMT is één bezoek één TAR. Meerdere containers per bezoek kan als je ze goed vooraf aanmeldt ([APMT FAQ](https://www.apmterminals.com/en/maasvlakte/practical-information/faq)). Een oude Portbase-pagina zegt dat ECT geen TAR nodig heeft. ECT noemt in 2026 wel een "verkeerde TAR-code". De oude pagina is dus verouderd ([Portbase legacy](https://support.portbase.com/en/services/road-planning-system-interface/), [ECT](https://www.ect.nl/en/news/news-feed/ect-introduces-truck-capacity-management-system)).

**Eigen systemen van terminals.** ECT heeft MyTerminal (Free, Premium, Premium Plus) en een chauffeurs-app. API's zijn er pas bij Premium Plus ([ECT](https://www.ect.nl/en/services/digital-services)). Bedrijven die containers brengen of halen bij ECT moeten met EAN-nummer geregistreerd zijn. ECT valideert dat binnen 2 werkdagen ([ECT](https://myterminal.ect.nl/help-center/registration/finance/truck-invoices)). Voor APMT en RWG vond ik geen API-informatie (**Open**). **Port Alert** (Havenbedrijf, Portbase, TLN) is een app met wachttijden, storingen en TAR-opzoeken ([Port of Rotterdam](https://publications.portofrotterdam.com/digital-report-2024/port-alert)).

### 7.3 Release en pincode

Een importcontainer mag pas weg als drie dingen kloppen. In **Cargo Controller** heten ze Arrival (aankomst), Release (douane en rederij) en Pickup (aanwijzing vervoerder, pre-notificatie, gate-out). Ze hebben de kleuren groen, geel of rood ([Portbase](https://support.portbase.com/en/services/cargo-controller-en/)). Dat alle drie groen moeten zijn, is mijn afleiding uit de opzet (**Schatting**).

- **Geen pincode per e-mail meer (Secure Chain).** Je krijgt de release digitaal in Portbase. Het recht om op te halen kan worden doorgegeven aan een expediteur of inland operator. De verlader krijgt een klantcode van de rederij ([Portbase](https://www.portbase.com/en/programs/secure-chain/shippers/)).
- **Gaat over Far East en Oceanië.** Voor die import geven rederijen geen "fraudegevoelige pincodes" meer uit. Alle diepzeeterminals op de Maasvlakte controleren bij de poort of de juiste vervoerder komt ([Portbase](https://www.portbase.com/en/programs/secure-chain/)).
- **APMT:** de pincode wordt in Portbase gecontroleerd. De chauffeur heeft alleen het TAR-nummer nodig ([APMT FAQ](https://www.apmterminals.com/en/maasvlakte/practical-information/faq)).
- **Andere handelsstromen:** daar kan een pincode nog bestaan. Niet geverifieerd (**Open**).
- **Hoe krijg je de LFD?** Dat staat niet in de Portbase-documentatie. De bron kan de rederij, de agent of Portbase zijn (**Open**).
- **Betrouwbaarheid van data.** Gegevens van de rederij zijn het best ca. 4 dagen voor aankomst van het schip. Terminalgegevens soms al 14 dagen ervoor ([Portbase](https://support.portbase.com/en/services/cargo-controller-en/)). Schema's van rederijen zijn niet betrouwbaar: ca. 50 - 55% op tijd in 2024 ([EUR](https://www.eur.nl/en/upt/media/2025-12-rapportde-opkomst-van-carrier-logistics201125-2)).

### 7.4 Douane

- **Importaangifte.** Sinds oktober 2021 wordt een aangifte alleen geaccepteerd als het schip is aangekomen. De aangifte moet kloppen met de tijdelijke opslagmelding (aantal colli, gewicht en B/L-nummer). Bij een verschil wordt hij afgewezen. Je kunt ook vooraf aangeven in AGS en krijgt dan een MRN ([Belastingdienst](https://belastingdienst.nl/wps/wcm/connect/en/customs/content/container-release-message-see-how-your-import-declaration-is-changing)).
- **Transit-export (T-documenten).** Je meldt ze vooraf via Portbase. Code RT1/RT2: afmelden bij aankomst op de terminal (lading gaat daarna over zee). Code TT1/TT2: niet afmelden (doorvoer naar een ander EU-land). De terminal meldt elektronisch af. Chauffeurs hoeven niet langs een douaneloket ([Portbase](https://support.portbase.com/en/services/clearance-transit-export-containers)).
- **Foutregels.** De aankomstmelding moet vóór het exportmanifest naar de Douane. Terminalaankomst en Portbase-melding mogen maximaal 7 dagen uit elkaar liggen ([Portbase](https://support.portbase.com/en/services/clearance-transit-export-containers)).
- **Papieren documenten** (T2L, TIR, ATA Carnet) kunnen bij APMT bij de emergency desk, maar moeten vooraf elektronisch zijn aangemeld ([APMT FAQ](https://www.apmterminals.com/en/maasvlakte/practical-information/faq)).

### 7.5 Slots

| Terminal | Slotlengte | Tolerantie | Nacht en weekend | Status |
|---|---|---|---|---|
| ECT Delta en Euromax | 2 uur vanaf 25 nov 2026: 04:00-05:59, 06:00-07:59, 08:00-09:59, 10:00-11:59, 12:00-13:59, 14:00-15:59, 16:00-17:59, 18:00-19:59, 20:00-03:59 | 30 min voor of na | Nachtblok 20:00-03:59. Weekend in het eerste schema één slot vr 19:00 - ma 02:59; of dat blijft is **Open** | Bevestigd ([ECT](https://www.ect.nl/en/news/news-feed/update-truck-capacity-management-system-hutchison-ports-ect-rotterdam)) |
| APMT MVII | 30 min | 45 min voor of na | Nacht 20:15-03:45. Weekend vr 20:15 - ma 03:45 één groot slot | Bevestigd ([APMT FAQ](https://www.apmterminals.com/en/maasvlakte/practical-information/faq)) |
| RWG | 60 min (04:00-19:59) | 30 min | 00:00-03:59 en 20:00-23:59 één groot slot | Ongedateerd overzicht ([Portbase](https://support.portbase.com/en/?p=19733)) |
| DCS en RCT (Kramer) | 60 min | 15 min | Weekend één slot | Tabel is intern tegenstrijdig |
| Hutchison Delta II | **Open** | | | Open |

**ECT TCMS in het kort** ([ECT 18 sep](https://www.ect.nl/en/news/news-feed/ect-introduces-truck-capacity-management-system), [ECT help](https://myterminal.ect.nl/help-center/features/pages/timeslots), [ECT 18 nov](https://www.ect.nl/en/news/news-feed/update-truck-capacity-management-system-hutchison-ports-ect-rotterdam)):

- Gestart in de week van 5 oktober 2026. ECT overlegt met TLN-AZV.
- Je boekt via Portbase (niet in MyTerminal). Slots komen 2 werkdagen vooraf om 09:00 vrij. Je ziet gisteren, vandaag en tot 4 dagen vooruit.
- Elk slot heeft een maximale capaciteit. Is het slot vol, dan krijg je het eerstvolgende vrije slot. Bij Delta geldt de capaciteit per groep "blokken", bij Euromax voor de hele terminal.
- Te vroeg komen mag niet. De slagboom gaat toch open om wachtrijen op de openbare weg te voorkomen. Je hebt 30 minuten om een bezoek te corrigeren, bijvoorbeeld een verkeerde TAR.
- **€ 100** voor te vroeg of ongeautoriseerd komen en **€ 100** voor een no-show. Niet voor het avond-, nacht- en weekendslot. **Deze heffingen worden nog niet in rekening gebracht.** De startdatum is niet genoemd.
- Bekende problemen volgens ECT: een container-info wijzigen vraagt dat je de pre-notificatie intrekt en kan je slot kosten (oplossing begin 2027). Het TAR-nummer mag nu worden hergebruikt voor een andere container of een ander slot.
- Bij grote verstoring kan ECT terugvallen op first-in-first-out.
- **Remote Check-In** (sinds 15 juli 2025): de pre-aankondiging heeft datum en exacte tijd. Het bezoek moet binnen 12 uur voor of na die tijd plaatsvinden. Maximaal 6 dagen vooruit aanmelden ([ECT](https://myterminal.ect.nl/news/period-validity-pre-announced-truck-visits-ect-terminals)).
- Slots komen 2 werkdagen vooraf vrij, maar je kunt 6 dagen vooruit pre-notificeren. De pre-notificatie is dus een gewenste tijd en het slot wordt later toegewezen (Schatting).

**APMT** meldde in juni 2026 dat de truck-slots vol zaten door hogere volumes en storing aan kranen. Vervoerders worden gevraagd buiten de spits te komen ([APMT](https://www.apmterminals.com/en/maasvlakte/about/news-and-updates/2026/260626-Fully-booked-timeslots-working-on-solutions)). Last-minute annuleringen en no-shows worden strenger behandeld ([APMT](https://www.apmterminals.com/en/maasvlakte/newsletter/20260209-newsletter-2026-02)).

### 7.6 Toegang, ISPS en veiligheid

Alle terminals zijn beveiligd volgens ISPS-regels. In de praktijk betekent dat voor een chauffeur:

| Onderwerp | Wat er geldt | Bron |
|---|---|---|
| ECT toegang | CargoCard verplicht. Vooraf registreren. Geldig ID en kentekenbewijs tonen. Steekproefcontroles | [ECT folder](https://www.ect.nl/sites/d10p.ect.nl/files/2025-09/ECT_Veilig_En_Beveiligd_DT_1c_EN_hvnr8202.pdf) |
| ECT veiligheidstest | Verplicht, handhaving vanaf **5 januari 2027**. Eerder genoemd: september 2026, daarna 3 november. De ECT-pagina "road services" zegt nog "november 2026" en is dus verouderd | [ECT update](https://www.ect.nl/en/news/news-feed/update-2-mandatory-safety-test-drivers) |
| De test zelf | Video kijken en voorwaarden accepteren in Secure Logistics. CargoCard met gezichtsherkenning nodig. 3 pogingen, daarna 3 maanden geblokkeerd. Certificaat 2 jaar geldig. Testcentrum Maasvlakte Plaza ma-vr 08:15 - 16:30 | [ECT](https://www.ect.nl/en/services/road-services) |
| Gezichtsherkenning | ECT Delta sinds 17 augustus 2026 | [ECT](https://www.ect.nl/en/news-feed) |
| APMT toegang | Veiligheidsinstructie vooraf. Vingerafdruk gekoppeld aan de CargoCard. Inchecken met visit-referentie, CargoCard en vingerscan | [APMT](https://www.apmterminals.com/en/maasvlakte/modalities/truck) |
| PBM en gedrag (ECT Delta) | Veiligheidsvest en -schoenen bij de blocks. Helm in operationele gebieden en op de kade. Telefoon alleen met carkit of oortje. Max 50 km/u, op de kade 30 km/u. Chauffeur begrijpt Nederlands, Duits of Engels | [ECT folder](https://www.ect.nl/sites/d10p.ect.nl/files/2025-09/ECT_Veilig_En_Beveiligd_DT_1c_EN_hvnr8202.pdf) |
| Op de terminal | Bij laden en lossen verlaat de chauffeur de cabine en staat naast de truck, in zicht van de machinist. Twistlocks en chassisaanpassingen alleen bij de blocks | [ECT folder](https://www.ect.nl/sites/d10p.ect.nl/files/2025-09/ECT_Veilig_En_Beveiligd_DT_1c_EN_hvnr8202.pdf) |

Poortregels voor RWG en Euromax en het "havenpas"-proces zijn niet apart gevonden (**Open**).

### 7.7 Wachttijden: er zijn geen openbare cijfers van nu

Dit is wat wel bekend is:

- **Oude metingen (TU Delft-scriptie, gebaseerd op Rijnmond):** ca. 40 minuten (2014), ca. 1 uur 40 (2016), tot 3 uur (2020) bij de terminalpoorten ([TU Delft](https://repository.tudelft.nl/file/File_105b8c36-b4d0-4b76-9519-9ba2a3fd60dd?preview=1)).
- **Buiten de spits rijden** verkort de rit gemiddeld met ca. 10 minuten ([Port of Rotterdam](https://publications.portofrotterdam.com/digital-report-2025/case-study-1)).
- **Uitspraak van een ondernemer (ODIN):** vijf jaar geleden haalde een truck tussen 06:00 en 18:00 vaak 6 containers, nu vaak 2 en hooguit 3. Dit is geen meting ([Port of Rotterdam](https://www.portofrotterdam.com/en/news-and-press-releases/peak-transport-makes-supply-chains-faster-and-more-reliable)).
- **Port Alert** gebruikt live gegevens van meer dan 2.200 trucks (2025). De wachttijden zelf zijn niet openbaar ([Port of Rotterdam](https://publications.portofrotterdam.com/digital-report-2025/case-study-1)).
- **Contargo** meldt voor Rotterdam een "congestie" van 37 tot 44 uur (november 2026). Het is niet duidelijk of dat schepen, barges of trucks meet. Gebruik dit niet als truckwachttijd ([Contargo](https://www.contargo.net/en/business/business-news/current-customer-information/)).
- Wachttijd per terminal in 2025 - 2026 is **Open**. Het is de grootste ontbrekende bron: vraag het aan echte planners.

### 7.8 Lege containers

- **De rederij bepaalt waar de lege container naartoe moet.** Bij Maersk is dat de "Place of Delivery" op de B/L. Een andere plek vraagt toestemming en een drop-off fee ([Maersk](https://www.maersk.com/local-information/europe/netherlands/import)).
- **Terminals nemen lege containers per rederij en per modaliteit aan.** ECT toont dat met kleuren: groen (open), oranje (sluit binnenkort of op verzoek), rood (gesloten of opent later) ([ECT](https://myterminal.ect.nl/help-center/features/pages/empty-container-delivery)).
- **Depots** staan in Waalhaven, Eemhaven, Botlek en op de Maasvlakte (o.a. Kramer, Alconet, Van Doorn, OCC Overbeek, CARU, Medrepair, Hacon, Progeco) ([Port of Rotterdam 2021](https://www.portofrotterdam.com/sites/default/files/2021-06/container-terminals-and-depots-in-the-rotterdam-port-area.pdf)). Openingstijden en capaciteit zijn **Open**.
- **Groei van lege stromen.** Import is veel groter dan export. Het gat liep van 2020 tot 2025 met 1,47 miljoen TEU op ([Port of Rotterdam](https://www.portofrotterdam.com/en/news-and-press-releases/between-growth-and-pressure-rotterdams-2025-container-year-under-review)). Nachtvervoer groeit alleen als ook de lege depots 's avonds en 's nachts open zijn (ODIN).
- **Open:** herstel (M&R) doorlooptijden en tarieven, en retourregels van MSC en CMA CGM.

### 7.9 Wegen rond de haven

| Onderwerp | Wat bekend is | Bron |
|---|---|---|
| A15 Maasvlakte - Vaanplein | Nieuw asfalt. Botlekbrug - Vaanplein in 2026 en 2027. Onderhoud doordeweeks tussen 22:00 en 05:00. Weekendafsluitingen meestal vr 21:00 - ma 05:00. Omleidingen kosten 30 - 60 minuten | [Rijkswaterstaat](https://www.rijkswaterstaat.nl/wegen/projectenoverzicht/a15-onderhoud-maasvlakte-vaanplein/hinder-en-maatregelen) |
| Botlekbrug | Schepen hebben voorrang, ook in de spits. Volledig dicht op 10 - 11 december 2026 (22:00 - 05:00), omleiding via de Botlektunnel | [Rijkswaterstaat](https://www.rijkswaterstaat.nl/wegen/projectenoverzicht/a15-botlekbrug-nieuwe-verbinding-weg-en-goederenspoorverkeer-scheepvaart-en-bromfietsers) |
| Tunnels (ADR) | Maastunnel D, Botlektunnel D, andere C (zie hoofdstuk 2) | [evofenedex](https://www.evofenedex.nl/api/v1/sharepoint/file/Shared%20Documents/Download%20Gevaarlijke%20Stoffen/ADR-tunneloverzicht%20Nederland%202026.pdf) |
| A24 Blankenburgverbinding | Tolweg (e-TOL). Tarief niet gevonden | [Rijkswaterstaat](https://www.rijkswaterstaat.nl/wegen/projectenoverzicht/a15-onderhoud-maasvlakte-vaanplein/hinder-en-maatregelen) |

Nachtvervoer (18:00 - 06:00) botst deels met het nachtelijk onderhoud (22:00 - 05:00) (Schatting). Verkeersintensiteit en gewichts- of hoogtebeperkingen in de haven zijn **Open**.

### 7.10 Een importrit stap voor stap

Dit is gereconstrueerd uit losse pagina's. Er is geen officiële stap-voor-stap-handleiding gevonden.

1. **Het schip komt aan en wordt gelost.** Bij grote schepen kan het dagen duren voordat jouw container eraf is ([FreshPlaza](https://www.freshplaza.com/article/9306281/when-can-i-collect-my-container/)).
2. **Douane.** Importaangifte of voorafgaande aangifte (7.4).
3. **Commerciële release** van de rederij via Secure Chain (7.3).
4. **Status checken.** Bij APMT is de container beschikbaar zodra de importdocumentatie compleet is en alle statussen in Road Planning groen zijn ([APMT FAQ](https://www.apmterminals.com/en/maasvlakte/practical-information/faq)). Bij ECT kijk je in MyTerminal.
5. **Pre-notificatie en slot** in Portbase. Je krijgt een TAR.
6. **Aankomst bij de poort.** ID, voertuig, CargoCard (plus vingerscan of gezichtsherkenning).
7. **Op de terminal.** Wachtgebied, blok, ophalen. De chauffeur staat naast de truck.
8. **Afleveren bij de klant.** Lossen (live) of de container neerzetten (drop).
9. **Lege container terugbrengen** naar de door de rederij bepaalde plek, vóór de detention-grens.

### 7.11 Een exportrit stap voor stap

1. **Lege container ophalen** bij een depot en laden. (Over de uitgifte bij depots is geen bron gevonden.)
2. **T-document melden** als dat nodig is (RT of TT, 7.4).
3. **Cargo opening en cargo closing** per container opvragen. Bij ECT staan ze in de Export Booking Status en verschuiven ze mee met de aankomsttijd van het schip. VGM, IMO en OOG-status staan er ook ([ECT](https://myterminal-tst.ect.nl/api-products/export-booking-status)).
4. **Pre-notificatie, slot en gate-in.** Bij ECT krijg je niet voor elk documenttype een gate-in-melding. Voor T1, ICT en REX verschijnt die pas bij laden of vertrek ([Portbase](https://support.portbase.com/en/kennis/my-container-is-at-the-terminal-but-it-does-not-have-a-gate-in-how-is-that-possible/)).
5. **Een vast cut-off-tijdstip bestaat niet.** Het hangt af van de cargo closing per schip.

### 7.12 Wat er in 2026 speelt

- **Capaciteit.** Transhipment daalde 20% in de eerste 9 maanden van 2026 door beperkte capaciteit. Extra capaciteit komt vanaf eind 2026 en meer in 2027 ([AJOT](https://www.ajot.com/news/throughput-in-the-port-of-rotterdam-rose-by-0.9-in-the-first-nine-months-of-the-year), [Port of Rotterdam](https://www.portofrotterdam.com/en/news-and-press-releases/between-growth-and-pressure-rotterdams-2025-container-year-under-review)). Een nieuwe terminal van Hutchison en TIL in de Europahaven staat gepland, eerste fase 2027 ([Seatrade](https://www.seatrade-maritime.com/terminals/hutchison-and-msc-to-develop-new-maasvlakte-i-box-terminal)).
- **Verstoringen.** Op 4 september 2026 legden havenwerkers het werk neer. Containerwerk stopte op sommige plekken van 11:15 tot 19:00. ECT zei dat inhalen dagen kon duren ([Welingelichte Kringen](https://www.welingelichtekringen.nl/economie/havenbedrijf-impact-staking-op-rotterdamse-haven-is-beperkt)). Ook storm en hitte legden de haven in 2025 en 2026 tijdelijk stil ([Port of Rotterdam](https://www.portofrotterdam.com/en/news-and-press-releases/between-growth-and-pressure-rotterdams-2025-container-year-under-review)).
- **Gevolg voor jou:** slotregels, heffingen en datums veranderen snel. Bouw ze als aanpasbare data.

---

## 8. Kosten: wachten, te lang laten staan en tol zijn de grote posten

### 8.1 Kosten van de rederij: demurrage en detention

Elke rederij heeft eigen regels en bedragen. Je systeem moet ze per rederij opslaan. Hieronder twee voorbeelden.

**Maersk Nederland, import (geldig vanaf 1 augustus 2026), in euro** ([Maersk](https://www.maersk.com/local-information/europe/netherlands/import)):

| Container | Demurrage dag 5-8 | dag 9-13 | dag 14+ |
|---|---|---|---|
| 20ft dry | 85 | 130 | 190 |
| 40ft dry, HC en 45ft | 110 | 210 | 250 |
| 20ft flat of open top | 150 | 180 | 275 |
| 40ft flat of open top | 175 | 215 | 330 |
| Reefer (20ft en 40ft) | 230 | 320 | 385 |

Demurrage: dag 1 tot 4 gratis. IMO-containers: 3 vrije dagen en hogere tarieven.

| Container | Detention dag 4-10 | dag 11-14 | dag 15+ |
|---|---|---|---|
| 20ft dry | 60 | 90 | 110 |
| 40ft dry | 80 | 110 | 150 |
| Reefer | 150 | 170 | 190 |

Detention: dag 1 tot 3 gratis bij ophalen per directe truck. Bij rail of barge zijn de eerste 5 dagen gratis. Detention loopt van gate-out tot gate-in van de lege container.

**Rekenvoorbeeld (Schatting; zo lees ik de tabel, de telregels zijn niet gecontroleerd).** Een 40ft dry blijft 6 dagen op de terminal. Demurrage dag 5 en 6: 2 x € 110 = € 220. De lege container komt 6 dagen na gate-out terug. Detention dag 4, 5 en 6: 3 x € 80 = € 240. Totaal € 460 voor één container.

**Hapag-Lloyd Nederland, import (geldig vanaf 19 januari 2026)** ([Hapag-Lloyd](https://www.hapag-lloyd.com/content/dam/website/downloads/pdf/netherlands_demurrage_detention_import_20260120_update.pdf)): 4 vrije kalenderdagen bij de zeeterminal, 7 bij een inlandterminal. Per dag: 20ft € 80 (eerste 5 dagen) en daarna € 140. 40ft € 95 en daarna € 220. Specials 20ft € 100 en € 160, 40ft € 115 en € 240. Er is een aparte "move cost" van € 55 per container vanaf dag 15. Reefers en IMO-klasse 1, 5.2 en 7 vallen buiten de standaardtarieven. Welke kolom bij welk bedrag hoort is in de bron onduidelijk (**Open**). Een oudere Hapag-Lloyd-lijst uit 2024 heeft lagere bedragen. Die gebruik ik niet.

**Andere Maersk-kosten (import)** ([Maersk](https://www.maersk.com/local-information/europe/netherlands/import)):

| Kostenpost | Bedrag |
|---|---|
| Inspectie of scanning in Rotterdam | € 195 per container |
| Extra importservice (handmatige wijziging, DO-verzoek) | € 50 per boeking |
| Wachttijd bij de klant na 2 vrije uren | € 40 per half uur |
| Meerdere stops | € 75 (tot 50 km extra) of € 150 (tot 100 km) |
| Gevaarlijke lading, inland haulage | € 40 per container |
| Genset | € 300 (rail of road), € 200 (plug-in barge of road), € 115 (koelchassis, directe truck) |

**Open:** terminal handling charges, gate fees, opslag, plugkosten, chassishuur, pre-pull-kosten en de tarieven van MSC en CMA CGM. Ook niet gevonden: wie de demurrage en detention uiteindelijk betaalt (vervoerder of klant). Dat hangt af van afspraken.

### 8.2 Kosten van de terminal en Portbase

- **Portbase:** zie hoofdstuk 7.2.
- **ECT-heffingen.** De factuur komt op de 2e van de maand voor de vorige maand. Delta en Euromax staan op één factuur, per bezoek met kenteken en chauffeur-ID ([ECT](https://myterminal.ect.nl/help-center/registration/finance/truck-invoices)). Op de factuur staan "Distribution Premium +13,50" en "Distribution Surcharge -4,50" per bezoek. De betekenis wordt niet uitgelegd (**Open**). Bestaande heffingen (distributietoeslag, klimaattarief, off-peak-incentive) blijven in 2027 gelijk. De heffingen van € 100 staan in 7.5 ([ECT](https://www.ect.nl/en/news/news-feed/ect-introduces-truck-capacity-management-system)).
- **Antwerpen:** zie hoofdstuk 9.

### 8.3 Wat een truck per uur kost

| Wat | Bedrag | Bron | Status |
|---|---|---|---|
| Trekker + oplegger voor containers, prijsjaar 2021 | € 66,84 per uur en € 1,65 per km | [KiM](https://www.kimnet.nl/binaries/kimnet/documenten/notities/2023/03/30/kostenkengetallen-voor-het-goederenvervoer/Kostenkengetallen+voor+het+goederenvervoer_Wegvervoer.pdf) | Bevestigd, oud |
| Opbouw per uur (KiM) | Personeel 29,25. Variabel (trekker, banden, brandstof, onderhoud) 25,34. Vast 5,75. Algemeen 6,11. Specifiek 0,38 | KiM | Bevestigd |
| Laden, lossen en wachten (KiM) | € 41,12 per uur | KiM | Bevestigd, oud |
| Wachtkosten volgens een TU Delft-scriptie | € 38 per uur | [TU Delft](https://repository.tudelft.nl/file/File_105b8c36-b4d0-4b76-9519-9ba2a3fd60dd?preview=1) | Bevestigd, jaar onbekend |
| Kosten per uur in 2026 | € 85 - 95 | Eigen extrapolatie | **Schatting** |
| Cao | +4% op 1 jan 2026. Overwerk +30%. Nacht 21:00 - 05:00 | [CNV](https://www.cnv.nl/vervoer/vervoer-en-logistiek/cao-beroepsgoederenvervoer/01-01-2026_31-12-2026/) | Bevestigd |

**Hoe ik aan € 85 - 95 kom (Schatting):** € 66,84 x 1,13 (stijging 2022, Rabobank) = ca. € 75,5. Dan drie jaar ongeveer 4,5% per jaar (gemiddelde van Rabobank en EVO) = ca. € 86. Dan nog ca. 4% voor 2026 = ca. € 90. De KiM-waarde geldt voor alle containertransport, niet speciaal voor havenritten. Vervang dit door een echte kostprijs van het bedrijf.

Meer context:

- **Kostenstijging.** EVO en TLN: binnenlands wegvervoer in 2024 +3,9% tot +5,2% (excl. brandstof en tol) ([EVO](https://www.evofenedex.nl/api/v1/sharepoint/file/Shared%20Documents/Download%20Vervoer/Kostenontwikkelingen_in_het_wegvervoer_in_2024_en_2025.pdf)). Rabobank verwacht +15,8% tussen 1 januari 2026 en 1 januari 2028. Personeel is ca. 44% van de kosten, brandstof ca. 20%. Ca. 80% van de vervoerders heeft een brandstofclausule ([Rabobank](https://www.rabobank.nl/kennis/d011532908-investeringsruimte-wegtransport-staat-onder-druk-door-kostenstijgingen)).
- **Tegenstrijdig:** de extra kosten door de kilometerheffing zijn tot 10% (Panteia, via [ABN AMRO](https://www.abnamro.nl/nl/zakelijk/insights/sectoren-en-trends/logistiek/2026-is-kantelpunt-voor-wegtransport.html)), tot 9,8% voor gewone voertuigen ([Upply](https://market-insights.upply.com/en/the-dutch-road-freight-sector-strives-to-maintain-its-competitiveness)) of +1 - 3% voor de hele sector in een analyse van vóór de start ([trans.info](https://trans.info/en/dutch-and-romanian-hauliers-face-mounting-insolvency-pressure-511121)). Het verschil zit in wat er wordt gemeten (nationale distributie, conventionele trucks of de hele sector).
- **Diesel.** Gemiddeld in de EU € 1,92 per liter in juli, € 2,05 in augustus en € 2,19 in september 2026. Piek € 2,27 op 27 september ([trans.info](https://trans.info/road-freight-rates-q3-2026-record-513960)).

### 8.4 Tol en milieuzones

**Nederland: kilometerheffing sinds 1 juli 2026** voor vrachtwagens boven 3.500 kg. Het Eurovignet is afgeschaft. Je hebt een werkend tolkastje (OBU) nodig. De boetes zijn de eerste zes maanden gehalveerd ([Rijksoverheid](https://www.rijksoverheid.nl/actueel/nieuws/2026/07/01/vrachtwagenheffing-vandaag-van-start)). Van 1 september tot 31 december 2026 is er 22,3% korting door hoge brandstofkosten. Het tarief hangt af van de technisch maximale massa, de CO2-klasse en voor klasse 1 ook de Euro-klasse ([vrachtwagenheffing.nl](https://www.vrachtwagenheffing.nl/dit-gaat-u-betalen)).

| Per 100 km, voertuig boven 32 t, Euro 6, CO2-klasse 1 | Bedrag | Status |
|---|---|---|
| Nederland, 1 juli - 31 aug 2026 | € 20,10 | Bevestigd |
| Nederland, 1 sep - 31 dec 2026 (met korting) | € 15,60 | Bevestigd |
| Nederland, 2027 (+2,6% indexering) | € 20,60 | Bevestigd; in een andere bron nog "voorlopig" |
| Nederland, emissievrij (CO2-klasse 5) | € 3,80 (2027: € 4,00) | Bevestigd |
| Vlaanderen | € 13,20 (plus CO2-toeslag sinds 1 juli 2026, bedrag onbekend) | Bevestigd, toeslag **Open** ([Viapass](https://viapass.be/en/rates/)) |
| Duitsland (5+ assen) | € 34,80 (tarief van 1 juli 2024) | Bevestigd, 2026-tarief **Open** ([Toll Collect](https://toll-collect.de/en/toll_collect/bezahlen/maut_tarife/p1745_mauttarife_07_2024.html)) |

Bronnen NL: [vrachtwagenheffing.nl](https://www.vrachtwagenheffing.nl/dit-gaat-u-betalen), [RDW](https://www.rdw.nl/over-rdw/nieuws/2026/tarieven-vrachtwagenheffing-2027), [trans.info IRU](https://trans.info/de/lkw-maut-2027-neue-regeln-fuer-europas-transporteure-507770).

- Het emissievrije tarief is ca. 81% lager dan Euro 6 (3,8 gedeeld door 20,1, **Schatting**).
- **Duitsland rekent per aantal assen.** Liftassen tellen mee ([WKO](https://www.wko.at/transport/maut-lkw-deutschland)). Een trekker met 3-assig chassis heeft 5 of meer assen en valt in de duurste klasse (Schatting).
- **Nederland rekent op massa**, niet op assen (afgeleid uit de bron, **Schatting**).
- **Zero-emissiezones.** Nieuwe trucks met eerste registratie vanaf 1 januari 2025 moeten emissievrij zijn om een ZE-zone in te mogen. Euro 6-opleggertrekkers uit 2017 - 2024 mogen tot 1 januari 2030 ([Op weg naar ZES](https://opwegnaarzes.nl/bedrijven/toegangsregels/vrachtauto-n2-en-n3-voertuigen-zwaarder-dan-3500-kg)). Of de haven of een Rotterdamse zone eronder valt, is **Open**.
- **Duitse vrijstelling voor emissievrije trucks** tot medio 2031: alleen de titel van het bericht is gezien (**Open**).

### 8.5 Ritprijzen: er zijn geen openbare prijzen per container

Ik vond **geen** openbare ritprijzen per container voor Rotterdam - Antwerpen, Venlo, Duisburg, Born of Moerdijk. Aanbieders tonen alleen "vraag een offerte". Ook het TLN-kostenmodel en de formules voor dieseltoeslag zijn niet gevonden (**Open**). Wat wel bekend is:

| Wat | Bedrag | Bron |
|---|---|---|
| Antwerpen - Duisburg, Q3 2026 | € 2,74 per km (contract), € 3,02 per km (spot) | [trans.info, Upply](https://trans.info/road-freight-rates-q3-2026-record-513960) |
| Duisburg - Lille, Q3 2026 | € 2,10 per km (contract), € 2,21 per km (spot) | idem |
| Congestietoeslag Antwerpen (sept. 2025) | € 20 - 35 per container | [Brussels Times](https://www.brusselstimes.com/1729204/antwerp-port-congestion-leads-transporters-to-introduce-heavy-surcharges) |
| PSA-slottoeslag Antwerpen | € 14 per bezoek (06:00 - 20:00) | [PSA](https://psa-antwerp.be/en/faq-ds-en) |

De Antwerpse bedragen zijn prijzen per km op lange internationale ritten en zeggen weinig over korte havenritten. Gebruik ze als richting, niet als tarief.

**Zo bouw je een ritprijs op (ontwerp, geen bronfeit).** Basisprijs per rit of relatie. Plus dieseltoeslag. Plus doorberekening van heffing en tol. Plus wachttijd na de vrije minuten. Plus extra stop. Plus gewichtstoeslag. Plus ADR- of reefer-toeslag. Plus afstandstoeslag. Plus chassis-standplaats. Plus administratieve toeslagen (zoals slotboetes).

### 8.6 Rekenvoorbeeld: wat kost een dag met 2 containers? (Schatting)

Dit rekenvoorbeeld laat het principe zien. Het is **geen marktprijs**. Het gebruikt mijn voorbeeld-ritdag uit hoofdstuk 10: 5,5 uur rijden en 6,0 uur laden, lossen en wachten.

| Stap | Berekening | Uitkomst |
|---|---|---|
| Rijden (KiM 2021) | 5,5 uur x € 66,84 | € 367,62 |
| Laden, lossen, wachten (KiM 2021) | 6,0 uur x € 41,12 | € 246,72 |
| Dag, prijzen van 2021, zonder tol | | € 614,34 |
| Per container (2 containers) | | ca. € 307 |
| Naar 2026 (ca. 1,34 maal, zie 8.3) | | ca. € 410 per container |

Daar komen tol (ca. € 15,60 - 20,60 per 100 km snelweg), terminalheffingen en eventuele demurrage en detention nog bovenop. De werkelijke kostprijs hangt af van het bedrijf. Vraag er een echt bedrijf naar.

---

## 9. Buiten Rotterdam: Antwerpen is anders, de rest is meestal voor- en natransport

### 9.1 Overzicht

| Plaats | Rol | Wat we weten | Afstand vanaf Rotterdam (Schatting) |
|---|---|---|---|
| Antwerpen | Zeehaven. 13,6 miljoen TEU in 2025 ([PoAB](https://newsroom.portofantwerpbruges.com/hubfs/260122_Factsheet_Jaarcijfers_2025_ENG.pdf?hsLang=en)) | Eigen regels en systemen (9.2) | ca. 100 - 110 km |
| Moerdijk | Binnenvaart- en spoorhub (MCT en CCT) | Goed gedocumenteerd (9.3) | ca. 60 - 70 km |
| Tilburg | Binnenvaart en spoor | Alleen genoemd in lijsten | ca. 90 - 100 km |
| Venlo | Spoor (Cabooter) en barge (Limburg Express) | Weinig informatie | ca. 170 km |
| Born | Binnenvaart en spoor | Limburg Express | ca. 190 - 200 km |
| Duisburg | Grootste binnenhaven ter wereld | Zie 9.4 | ca. 220 km |

De afstanden zijn **mijn eigen schattingen**. Ze staan niet in de bronnen. Controleer ze met een routeplanner. Duisburg ca. 220 km komt ook uit de opdracht.

### 9.2 Antwerpen: andere regels dan Rotterdam

| Onderwerp | Rotterdam | Antwerpen |
|---|---|---|
| Release | Secure Chain, digitaal in Portbase | **Certified Pick-up** (CPu) sinds 15 januari 2024. De rederij geeft de release. De vervoerder krijgt het "release right" en wijst een "pick-up right" toe aan een specifieke chauffeur (Alfapass-nummer). Alleen die chauffeur haalt de container op, na biometrische controle ([Transport Journal](https://www.transportjournal.com/home/news/artikeldetail/no-more-pin-codes-in-antwerp.html?L=.), [NxtPort](https://documentation.nxtport.com/certified-pickup/cpu-for-transport-operators)) |
| Systeem | Portbase (HCN Road) | NxtPort. Je registreert je bedrijf vooraf ([Maersk](https://maersk.com/news/articles/2024/05/02/certified-pick-up-go-live-date-for-terminals-behind-the-locks)). CPu is API-first. Bij grote aantallen is de API aanbevolen ([NxtPort](https://documentation.nxtport.com/certified-pickup/cpu-for-transport-operators)) |
| Slots | ECT TCMS, APMT, RWG | PSA werkt met TAMS: pre-notificatie, dan een "visit" met afspraaktijd, dan een TAR. Een volle importcontainer moet vooraf aan de visit zijn gekoppeld ([PSA](https://www.psa-antwerp.be/sites/psa-antwerp/files/2025-05/eportal-guideline-tams.pdf)) |
| Openingstijden | 24 uur per dag (Maasvlakte) | DP World, MPET en PSA: doorlopend van **maandag 05:00 tot zaterdag 05:00**. Dus **niet op zondag** ([DP World](https://www.dpworld.com/belgium/contact-us/opening-hours), [PoAB](https://www.portofantwerpbruges.com/en/business/transportation/road-transport/night-logistics)) |
| Toeslagen | ECT € 100 no-show (nog niet geheven) | PSA: **€ 14 per bezoek** tussen 06:00 en 20:00, sinds 12 mei 2025 (alleen kade 869 en 913). Nacht is gratis binnen het slot ([PSA](https://psa-antwerp.be/en/faq-ds-en)). Vervoerders voerden in september 2025 een congestietoeslag in van € 20 - 35 (de bron zegt "per container", de metabeschrijving "per ton": **Open**) ([Brussels Times](https://www.brusselstimes.com/1729204/antwerp-port-congestion-leads-transporters-to-introduce-heavy-surcharges)) |
| Export | Cargo closing per schip | PSA verkortte het leveringsvenster voor export op 7 april 2025 van 7 naar 5 dagen ([Kuehne+Nagel](https://mykn.kuehne-nagel.com/news/article/psa-antwerp-reduces-export-delivery-window-to-07-Apr-2025)) |
| Tol | NL 20,1 ct/km | Vlaanderen 13,2 ct/km. De goedkoopste route (hoofdstuk 8) |
| Verstoringen | Staking 4 sep 2026, storm, hitte | Ca. 25 dagen actie in 2025. In 2026: staking in maart, olielek in april, loodsenacties in juni, samen ca. 260.000 TEU verloren ([Hellenic Shipping News](https://www.hellenicshippingnews.com/port-of-antwerp-bruges-stands-firm-in-a-challenging-first-half-of-2026/)) |

Meer over Antwerpen:

- **Nachtlogistiek.** "Hubs" nemen 's nachts containers aan zonder slots en handelen af in 15 - 20 minuten. Export gaat overdag naar de hub en 's nachts naar de terminal ([PoAB](https://www.portofantwerpbruges.com/en/business/transportation/road-transport/night-logistics)).
- **Liefkenshoektunnel.** Tolvrije uren zijn bijna verdwenen: ca. 5 uur in 2025, tegen 273 uur in 2022. De R2 is "bijna altijd verzadigd" ([VRT](https://www.vrt.be/vrtnws/nl/2026/01/08/liefkenshoektunnel-tolvrij-gezakt-file-antwerpen/)).
- **Zondag.** Wie maandagochtend in Antwerpen wil laden, moet zondagavond of -nacht vertrekken. Dat botst met nachtdiensten en rijtijden (Schatting).
- **Wachttijd per terminal** in minuten of uren is niet gevonden. Contargo noemt 48 uur "congestie" in Antwerpen. Wat dat meet, is onduidelijk ([Contargo](https://www.contargo.net/en/business/business-news/detail-business/serious-delays-in-truck-handling-in-rotterdam-and-antwerp/)).
- **Open:** Gent, Vlissingen, Amsterdam, Zeebrugge (volume, openingstijden), Hesse-Noord Natie, Antwerp Euroterminal, het Belgische rijverbod en regels voor de Kennedytunnel.

### 9.3 Moerdijk, Tilburg, Venlo en Born

**Moerdijk (MCT, ECT/Hutchison)** ([ECT](https://www.ect.nl/en/terminals/mct-moerdijk)):

- Adres Middenweg 35. Open maandag tot vrijdag 06:00 - 21:00, zaterdag 07:00 - 12:00, zondag gesloten.
- Een dagelijkse bargeshuttle naar ECT Delta en Euromax. De bargetijd is ca. 4 uur naar Rotterdam en 6 uur naar Antwerpen. Er is ook een spoorterminal met 3 sporen en een depot voor lege containers.
- Automatische poort. Chauffeurs gebruiken de CargoCard.

**Moerdijk (CCT)**: dagelijkse bargediensten Maasvlakte - Moerdijk. Ca. 60% van de containers tussen Rotterdam en Moerdijk gaat nog per truck. Lege containers kunnen in Moerdijk blijven, wat demurrage en detention scheelt. Let op: dit is gesponsorde content van CCT zelf ([UIRR](https://www.uirr.com/web-news/smart-carrier-chooses-multimodal-moerdijk)).

**Tilburg, Venlo, Born.** Maersk noemt Terminal Born en Terminal Tilburg als depots met barge én spoor, en Cabooter Terminal Venlo als alleen spoor. Over de weg kan altijd ([Maersk](https://www.maersk.com/local-information/europe/netherlands/local-solutions/inland-services)). Havenbedrijf-brochure uit 2021 (dus oud): de West Brabant Corridor (Tilburg, Moerdijk, Oosterhout) had 22 vaste diensten per week en de Limburg Express (Venlo, Born) 4 per week ([Port of Rotterdam](https://www.portofrotterdam.com/sites/default/files/2021-08/cooperation-in-the-corridor-port-of-rotterdam.pdf)). Openingstijden, systemen en Portbase-koppeling van Tilburg, Venlo en Born zijn **Open**. Alleen Moerdijk is volledig uitgezocht.

**De truck blijft nodig voor het laatste stuk.** Voorbeeld: Born - Susteren is "een paar kilometer" ([Port of Rotterdam](https://portofrotterdam.com/en/news-and-press-releases/water-if-possible-road-if-necessary)). Het project Joint Corridors Off-Road verschoof in drie jaar ca. 370.000 TEU van de weg (30% spoor, 70% water). Bedrijven met minimaal 375 TEU per jaar kunnen 2 jaar € 11,76 per TEU subsidie krijgen. Wegvervoer is op dit moment erg goedkoop en de verschuiving naar water is deels teruggedraaid (zelfde bron).

**Voor een truckbedrijf in Zuid-Holland** verkort een hub als Moerdijk de rit. De truck rijdt niet naar de Maasvlakte (slots, wachttijd, toeslagen) maar doet het laatste stuk vanaf de hub. De hub bepaalt dan de capaciteit (Schatting).

### 9.4 Duisburg en Duitsland

- **duisport** haalde in 2025 **5,1 miljoen TEU** (+5,1%). Er zijn tien terminals en meer dan 400 intermodale treinen per week naar 100 bestemmingen. De Duisburg Intermodal Terminal doet containers en gevaarlijke stoffen ([UIRR](https://www.uirr.com/web-news/duisport-closes-very-successful-2025), [duisport](https://duisport.de/en/terminals/)).
- **Regels:** zie hoofdstuk 4 (gewicht, Maut, zondagsverbod). Een rit Rotterdam - Duisburg op zondag voor 22:00 mag in de praktijk niet. Of de uitzondering van 150 km (haven-weg) of 200 km (spoor-weg) geldt voor een directe truck van Rotterdam naar Duisburg, moet per geval worden getoetst. Dat is niet uitgezocht (**Open**). Voor de 44 t-regel geldt de 150 km-vraag uit hoofdstuk 4 ook.
- **Laag water in de Rijn in 2026.** Kaub (een meetplek in de Rijn) stond op 27 juli op 31 cm, op 18 september op 20 cm en op 1 oktober op **-6 cm**, een nieuw record. De scheepvaart lag bijna stil. Schepen laadden 600 - 1.000 ton in plaats van 2.500 ton. De bargeprijs ARA - Karlsruhe was ca. € 200 per ton, bijna tien keer het niveau van januari. Laagwatertoeslagen liepen op tot vierciferige bedragen per container ([Hapag-Lloyd](https://www.hapag-lloyd.com/en/services-information/offices-localinfo/local-news/2026/07/germany--rhine-low-water-is-affecting-hinterland-transport.html), [S&P Global](https://www.spglobal.com/energy/en/news-research/latest-news/refined-products/100126-rhine-water-levels-fall-to-new-record-low-stalling-fuel-logistics), [VerkehrsRundschau](https://www.verkehrsrundschau.de/nachrichten/transport-logistik/historisches-niedrigwasser-und-seine-folgen-fuer-die-lieferketten-3890475)). Eén binnenschip vervangt 100 tot 200 trucks. De rechter Middenrijn-spoorlijn is van 10 juli tot 12 december 2026 dicht ([S&P Global](https://www.spglobal.com/energy/en/news-research/latest-news/crude-oil/091826-rhine-water-levels-approach-zero-threaten-barge-transport)).
- **De stand van november 2026** is niet gevonden. De laatste meting is van begin oktober (**Open**).
- **Gevolg voor trucks.** Meer vraag en hogere spotprijzen, maar de chauffeurs en de infrastructuur zitten al aan de limiet (Schatting).
- **Open:** Keulen, Neuss, Dortmund, Mannheim, Frankfurt, Hamburg, milieuzones in Duitsland.

### 9.5 Binnenvaart en spoor: wat betekent het voor een trucker?

| Onderwerp | Wat bekend is | Bron |
|---|---|---|
| Verdeling hinterland | Weg 58%, binnenvaart 34%, spoor 8% (interview met de directeur containers van het Havenbedrijf, juni 2025). Het Havenbedrijf zegt zelf: 34% van de containers tussen de Maasvlakte en het achterland gaat per binnenschip. Dat zijn verschillende afbakeningen | [Dredgewire](https://dredgewire.com/interview-with-hanna-stelzel-director-containers-port-of-rotterdam), [Port of Rotterdam](https://www.portofrotterdam.com/en/node/1164) |
| Barge | APMT verhoogde per 1 jan 2026 de minimale callgrootte van 15 naar 20 moves. Strengere free time en demurrage verkorten de bundeltijd | [APMT](https://www.apmterminals.com/en/maasvlakte/newsletter/20260209-newsletter-2026-02), [Port of Rotterdam](https://portofrotterdam.com/en/logistics/connections/intermodal-transportation/inland-shipping/optimising-inland) |
| Spoor bij APMT | Treincapaciteit sterk beperkt van 1 juli 2026 tot medio 2027 | [Contargo](https://www.contargo.net/en/business/business-news/detail-business/rotterdam-rail-capacity-limitations-from-july-2026/) |
| Spoorkosten | Trein van 1.200 ton: € 1,55 per km vanaf Rotterdam tegen € 0,88 vanaf Antwerpen na subsidie. Nederland geeft geen subsidie. België betaalt € 1,20 per treinkilometer. Duitsland dekt 32,5% (2025) en 36,8% (2026) van de kosten | [Breakbulk News](https://breakbulk.news/dutch-rail-freight-faces-higher-costs-from-subsidy-gap/) |
| Antwerpen tegen Rotterdam | Truck goedkoper vanuit Antwerpen, spoor goedkoper vanuit Rotterdam, THC in Rotterdam ca. 15% hoger. Het artikel heeft geen datum | [Loadstar](https://theloadstar.com/greener-or-cheaper-intermodal-options-from-ports-of-rotterdam-and-antwerp) |
| Subsidie Modal Shift (RVO) | € 20 per verschoven container, minimaal 3 containers per dag en 35 km. Staat op "gesloten" (aanvragen vóór 1 okt 2025). Opvolger niet bevestigd | [business.gov.nl](https://business.gov.nl/subsidy/subsidy-modal-shift) |

**Voor een truckbedrijf betekent dit** (Schatting): (1) voor- en natransport vanaf inlandterminals, kortere ritten met een lagere prijs per rit; (2) pendelritten tussen terminals (inter-terminal transport) als barge of spoor uitvalt; (3) extra werk bij laag water in de Rijn of stakingen in Antwerpen. Klanten kiezen de weg bij korte afstand, spoed, weinig volume en kort free time. Ze kiezen barge of spoor bij grote vaste volumes en lange vaste afstanden.

### 9.6 Verder weg

Frankrijk, Luxemburg, Zwitserland, Italië en Oost-Europa gaan vooral per trein en binnenvaart tot een Duitse of Alpiene terminal. De truck doet het voor- en natransport. Hupac vervoerde in 2025 ca. 975.000 zendingen (1,85 miljoen TEU). Grote werken op de Rijn-Alpen-corridor lopen tot vóór 2029 ([Railmarket](https://zh.railmarket.com/news/freight-rail/55916-hupac-posts-profit-despite-rail-disruptions)). **Open:** Frankrijk (Lille, Parijs), Luxemburg (Bettembourg), Zwitserland (Bazel), corridors naar Oost-Europa, de Betuweroute, Kombiverkehr, ERS en DB Cargo. De directe markt voor een Nederlandse trucker is Benelux en West-Duitsland (Schatting).

---

## 10. Rittypes en een voorbeeld-ritdag: 2 tot 3 containers per dag

### 10.1 Wie regelt het transport?

In Rotterdam is **merchant haulage** het meest gebruikelijk: de verlader of expediteur regelt het. De trucker moet dan zelf alle documenten, releases en vrije dagen bewaken ([TU/EUR-scriptie](https://thesis.eur.nl/pub/40373/Vliet-L-van-der-373098-MA-thesis.pdf)). Een schatting uit interviews: ca. 85 - 90% merchant haulage en 10 - 15% carrier haulage ([EUR](https://www.eur.nl/en/upt/media/2025-12-rapportde-opkomst-van-carrier-logistics201125-2)). Dat is geen systematische meting.

### 10.2 Rittypes

De namen hieronder komen uit mijn eigen branchekennis, niet uit een bron (**Schatting**). Bevestigd is alleen dat Portbase vier handlingtypes kent: volle container laden of lossen, lege container laden of lossen ([Portbase](https://hcn.pcs.portbase.com/api-documentation/connection_instructions.html)). Drayage-systemen noemen als standaardworkflows: live load of unload, one-way land bridge, chassis splits, pre-pulls, street turns en shuttles ([CargoWise](https://www.cargowise.com/landside/solutions/containers-by-road/drayage-tms/profit-tools-tms/)).

| Rittype | Engelse term | Wat het is |
|---|---|---|
| Importrit | import pick-up / delivery | Volle container ophalen op de terminal en bij de ontvanger afleveren |
| Leeg retour | empty return | Lege container terugbrengen naar het depot van de rederij |
| Exportrit, leeg ophalen | empty pick-up | Lege container ophalen bij een depot, laden bij de klant |
| Inleverrit | export delivery / gate-in | Volle exportcontainer inleveren bij de terminal vóór de cut-off |
| Pre-pull | pre-pull | Container eerder ophalen en tijdelijk neerzetten, tegen LFD- of slotdruk |
| Dual cycle | dual cycle | Eén bezoek aan de terminal: export inleveren en import ophalen |
| Street turn | street turn | Lege importcontainer direct hergebruiken voor export, zonder depot. De rederij moet toestemming geven |
| Drop and hook | drop and hook | Container of chassis achterlaten en een ander oppakken |
| Live laden of lossen | live load / unload | De chauffeur wacht tijdens het laden of lossen |
| Shuttle of bijrit | shuttle | Korte pendelrit, bijvoorbeeld terminal - depot |
| Pendel tussen terminals | inter-terminal transport (ITT) | Verplaatsing tussen terminals in de haven |
| Herpositioneren | repositioning | Leeg materieel verplaatsen naar waar het nodig is |

Een rit is een eigen object. Eén order heeft één of meer containers. Eén container heeft één of meer ritten. Modality (een Nederlands TMS) gebruikt dezelfde opzet ([Modality](https://modality.nl/?p=1673)).

### 10.3 Combineren

- **Bevestigd:** bij APMT is één TAR genoeg voor meerdere aflever- en ophaalacties in één bezoek, als je ze goed vooraf aanmeldt ([APMT FAQ](https://www.apmterminals.com/en/maasvlakte/practical-information/faq)). Bij ECT staan gecombineerde pre-notificaties in één bezoek op het voorkeursslot, dat voor alle containers van het bezoek geldt ([ECT](https://www.ect.nl/en/news/news-feed/ect-introduces-truck-capacity-management-system)).
- **Of "dual cycle" officieel wordt ondersteund** bij Rotterdamse terminals en of de rederij een lege container op die terminal toestaat, is **Open**.
- **Nacht (ODIN):** laden en lossen tussen 18:00 en 06:00 op meerdere Maasvlakte-locaties. Containers die na 23:30 aankomen worden ontkoppeld en de volgende ochtend verwerkt. De chauffeur kan dan terug naar de terminal voor een volgende rit ([Port of Rotterdam](https://www.portofrotterdam.com/en/news-and-press-releases/peak-transport-makes-supply-chains-faster-and-more-reliable)).

### 10.4 Wat beslist een planner? (Schatting)

Er is geen openbare beschrijving van een planningsdag gevonden. Dit is mijn reconstructie:

1. Welke ritten kunnen op één trekker (combineren)?
2. In welke volgorde langs terminal, klant en depot?
3. Welke chauffeur? Let op uren, ADR of reefer, en toegang tot de terminal.
4. Welk chassis? Type, lengte en gewichtsklasse.
5. Welk slot? Boeken vóór de rit.
6. Live laden of drop and hook?
7. Pre-pull of niet? Wanneer terug met de lege container?

### 10.5 Voorbeeld-ritdag

**Alle tijden en aannames zijn mijn eigen voorbeeld (Schatting).** Aannames: 1 uur rijden tussen yard, terminal, klant en depot (de TU Delft-scriptie gebruikt ook gemiddeld 1 uur transport in Nederland), 1,5 uur op de terminal, 1 uur lossen. Het is een importdag na 25 november 2026 bij ECT Delta, met twee slots van 2 uur.

| Tijd | Wat | Regel of opmerking |
|---|---|---|
| 06:45 | Start dienst: tachograaf, truck controleren, chassis koppelen | Werktijd begint. Past het chassis bij de container? |
| 07:00 | Rijden naar ECT Delta (1 uur) | Rijtijd 1:00 |
| 08:00 | Aankomst, slot 08:00 - 09:59 | Binnen 30 min tolerantie. Niet te vroeg |
| 08:00 - 09:30 | Poort, wachtgebied, container oppakken (1,5 uur) | Wachten telt als werktijd |
| 09:30 | Rijden naar klant 1 (1 uur) | Rijtijd 2:00 |
| 10:30 - 11:30 | Lossen bij klant 1 (1 uur) | Maersk rekent € 40 per half uur wachttijd na 2 vrije uren |
| 11:30 - 12:15 | Pauze van 45 minuten | Nooit meer dan 6 uur werk zonder pauze |
| 12:15 | Rijden naar lege-container-depot (1 uur) | Rijtijd 3:00 |
| 13:15 - 13:45 | Lege container inleveren (30 min) | Regels van de rederij en het depot |
| 13:45 | Rijden naar de terminal (30 min) | Rijtijd 3:30 |
| 14:15 - 15:45 | Slot 14:00 - 15:59, tweede container oppakken (1,5 uur) | Tweede bezoek, tweede slot |
| 15:45 | Rijden naar klant 2 (1 uur) | Rijtijd 4:30 |
| 16:45 - 17:45 | Lossen bij klant 2 (1 uur) | |
| 17:45 | Rijden naar het bedrijf (1 uur) | Rijtijd 5:30 |
| 18:45 - 19:00 | Afsluiten: tachograaf, papieren, app | De lege container van klant 2 gaat morgen terug. Detention loopt door |

**Uitkomst:** dienst 06:45 - 19:00 (12 uur 15). Pauze 45 minuten. Werktijd **11 uur 30**. Rijtijd **5 uur 30**.

**Controle met de regels:**

- Rijtijd 5,5 uur is minder dan 9 uur. Goed.
- Na 2 uur rijden komt de pauze. Dat is ruim binnen de 4,5 uur. Goed.
- Dienst van 12,25 uur past binnen 13 uur (24 - 11 uur rust). Goed.
- Werktijd van 11,5 uur geeft waarschijnlijk overwerk met 30% toeslag boven de contracturen.

**Verbetering:** laat de chauffeur de lege container terugbrengen op de terminal zelf en tegelijk de volgende container ophalen. Dat scheelt een depotrit. Dat kan alleen als de rederij daar lege containers toestaat. ECT toont dat per rederij met kleuren (7.8).

**Wat als de wachttijd langer is?** Werktijd = 8,5 uur + 2 x de wachttijd per bezoek (Schatting).

| Wachttijd per terminalbezoek | Werktijd (zonder pauze) | Dienst (met 45 min pauze) | Past binnen 13 uur? |
|---|---|---|---|
| 0,5 uur | 9,5 uur | 10 u 15 | Ja |
| 1,0 uur | 10,5 uur | 11 u 15 | Ja |
| 1,5 uur (voorbeeld) | 11,5 uur | 12 u 15 | Ja |
| 3,0 uur | 14,5 uur | 15 u 15 | Nee. Ook niet bij 9 uur rust (maximaal 15 uur) |

Bij 3 uur wachten per bezoek past de tweede container niet meer in dezelfde dienst. 3 uur extra wachten per dag kost bovendien ca. € 123 (3 x € 41,12 volgens KiM, prijzen van 2021).

### 10.6 Hoeveel ritten per dag? Er is geen betrouwbare bron

- **Uitspraak van een ondernemer (ODIN):** vroeger vaak 6 containers per dag tussen 06:00 en 18:00, nu vaak 2 en hooguit 3. Geen meting. Het is niet duidelijk of de ritten vergelijkbaar zijn.
- **Mijn eigen schatting:** 2 tot 3 per werkdag, afgeleid uit 2 uur rijden in de regio, laden, lossen en 0,7 tot 3 uur poortwachttijd. Dat past bij de ODIN-uitspraak, maar is geen bewijs. Voor een rit naar Duisburg (ca. 3 uur enkele reis, Schatting) is het waarschijnlijk 1 per dag.
- **KiM-gemiddelde:** 105.000 km en 2.585 effectieve uren per jaar voor een container-trekker. Dat is een jaargemiddelde voor alle containertransport en zegt niets over ritten per dag ([KiM](https://www.kimnet.nl/binaries/kimnet/documenten/notities/2023/03/30/kostenkengetallen-voor-het-goederenvervoer/Kostenkengetallen+voor+het+goederenvervoer_Wegvervoer.pdf)).
- Documenten die dit mogelijk wel hebben (Topsector Logistiek "Containercongestie 2024", TNO-rapport R11569) kon ik niet lezen.

---

## 11. Tegenstrijdigheden en gaten in het onderzoek

Dit onderzoek bestaat uit bureauonderzoek op websites. Er zijn geen gesprekken met planners of chauffeurs gevoerd. Veel bronnen zijn samenvattingen of oud. Hieronder staat wat niet klopt of ontbreekt.

| Onderwerp | Wat de bronnen laten zien | Wat je ermee doet |
|---|---|---|
| **Ritten per dag per truck** | Geen meting. Een ondernemer zegt: van 6 naar 2 - 3. Mijn eigen schatting: 2 - 3 | Gebruik 2 - 3 alleen als startwaarde. Meet zelf |
| **Gewicht van de trekker** | Geen bron. Ik rekende met 7.000 - 9.000 kg | Haal het per trekker uit het kentekenbewijs |
| **Ritprijs per container** | Geen openbare prijzen. Alleen prijzen per km (Upply) en kostprijs uit 2021 (KiM) | Vraag tarieven en kostprijs aan het bedrijf |
| **Kipper-chassis, swap body, haakarm, kraan, reefer-genset** | Geen bron gevonden | Open. Vraag welk materieel het bedrijf heeft |
| **LZV met containers** | De RDW-pagina noemt containers niet. De EU-Raadstekst wil 0,15 m extra voor 45ft in intermodaal vervoer | Open |
| **Frankrijk en Luxemburg** | Gewichten niet gevonden. Rijverboden alleen uit een secundaire bron | Laat ze weg uit de eerste versie |
| **Wachttijden van trucks** | Geen openbare cijfers voor 2025 - 2026. Oude cijfers: 40 min (2014), 1 u 40 (2016), 3 u (2020). Contargo noemt 37, 44 en 48 uur, maar het is onduidelijk wat dat meet | Meet zelf per terminal en per tijdstip |
| **De 1/5-regel** | Mijn notities noemen één keer aandrijfas en één keer stuuras | Ik ga uit van de aandrijfas. Controleer |
| **Tridem: 24 of 27 ton** | Bronnen onduidelijk | Reken met 24 ton |
| **45ft-container** | OM staat 17,30 m toe, het RDW-overzicht noemt 16,50 m, Cargobull noemt een bijzondere ontheffing. Gewichtscijfers tellen niet op | Controleer per container en route |
| **Duitse 44 ton en de 150 km** | Een samenvatting van het StVZO noemt 150 km voor het wegdeel. Rotterdam - Duisburg is ca. 220 km | Controleer. Grote kans op een beperking |
| **Hapag-Lloyd demurrage** | Een lijst van 2024 en een van 2026 geven andere bedragen. Kolomindeling onduidelijk | Gebruik 2026. Controleer de kolommen |
| **TAR bij ECT** | Oude Portbase-pagina: niet nodig. ECT 2026: TAR wordt gebruikt | De oude pagina is verouderd |
| **ECT-veiligheidstest** | Drie datums: september 2026, 3 november, 5 januari 2027. ECT "road services" is niet bijgewerkt | Gebruik 5 januari 2027 |
| **Terugkeer van het voertuig (8 weken)** | business.gov.nl noemt de regel nog. Het Hof van Justitie vernietigde hem in oktober 2024 | Het Hof wint. De portal is waarschijnlijk verouderd |
| **Duitse feestdagen en zomerverbod** | Impargo en de wettekst verschillen. Zomer: 1 juli - 31 augustus tegen 3 juli - 28 augustus | Gebruik de officiële bron per deelstaat |
| **Gewicht in België** | Vlaanderen.be noemt 44 t, tot 48 t onder voorwaarden en tot 50 t emissiearm. Brussels Times (okt 2025) noemt 44 t als norm voor 5-assers en 45 en 46 t voor emissiearm en emissievrij als regels die nog niet gelden | Waarschijnlijk andere voertuigtypes. Niet opgelost |
| **Rijtijd als beperking** | Notities: de 9 uur is meestal de beperking. Mijn voorbeeld: dienstlengte en wachten | Controleer met een echt bedrijf |
| **Extra kosten door km-heffing** | Tot 10%, tot 9,8% of +1 - 3% | Andere meetmethoden. Rekenen met een eigen cijfer |
| **Maastunnel 3,9 m** | Alleen een NOS-kop gezien | Vraag na of het is ingevoerd |
| **Verdeling weg - water - spoor** | Twee keer "34%" met een andere betekenis | Gebruik het als indicatie |
| **Open materieel-getallen** | Open top, flat rack, side door, bulk, twistlock-posities, tandem 20ft | Vraag na |

---

## 12. Wat moet je nog zelf navragen bij een echt transportbedrijf

Praat met 2 of 3 planners en een paar chauffeurs. Dat is de grootste ontbrekende bron in dit onderzoek. Neem deze vragen mee.

**Materieel en gewicht**
- Welke trekkers (4x2, 6x2, 6x4) en welke chassis heeft het bedrijf? Wat is de "massa rijklaar" en de technisch toegestane massa van elk?
- Hoeveel assen heeft elk chassis? Welke aslast-grenzen gebruiken ze?
- Hoeveel netto lading kan een 20ft en een 40ft HC in de praktijk mee? Hoe gaan ze om met zware containers?
- Hoe weten ze het echte gewicht van een container? Gebruiken ze de VGM? Wegen ze zelf?
- Rijden ze met LZV, kipper-chassis, swap bodies, haakarm of kraan? Met containers?
- Naar Duitsland: hoe regelen ze de 44 ton en de 150 km-eis? Hoe regelen ze het zondagsverbod?

**Dagelijkse planning**
- Hoeveel containers haalt een truck gemiddeld per dag? Hoe lang duurt een rit?
- Hoe komen orders binnen (e-mail, EDI, portaal)? Hoe maakt de planner er ritten van?
- Welke software of Excel gebruiken ze nu? Wat werkt niet?
- Doen ze dual cycles, pre-pulls, street turns, drop and hook? Wanneer?

**Haven**
- Naar welke terminals en depots rijden ze het meest?
- Hoe lang wachten ze per terminal en per tijdstip? Hebben ze eigen data (GPS, tachograaf)?
- Hoe vaak komt een no-show of een gemist slot voor?
- Wie boekt slots en doet de pre-notificatie? Hebben ze Portbase, een EAN-nummer en MyTerminal?
- Waar komt de last free day vandaan? Wordt een pincode nog gebruikt?
- Wie betaalt demurrage en detention? Hoe vaak komt het voor?
- Welke regels hebben rederijen voor lege containers? Wat gebeurt er als het depot dicht is?

**Kosten en prijzen**
- Wat is hun kostprijs per uur en per km? Hoe rekenen ze een ritprijs uit?
- Hoe rekenen ze dieseltoeslag, tol, wachttijd (vrije minuten), extra stop en gewichtstoeslag door?

**Personeel en regels**
- Hoe vaak moeten chauffeurs overwerken? Hoe werkt het rooster (28 dagen vooraf)?
- Welke chauffeurs hebben ADR, ECT-veiligheidstest en CargoCard?
- Kunnen ze tachograafgegevens uitlezen? Hoe gaan ze om met 'virtuele' rijtijd?

**Buitenland en software**
- Welke landen rijden ze op en hoe vaak? Hoe gaan ze om met Frankrijk en Luxemburg?
- Welke koppelingen zijn nodig (Portbase, rederijen, telematica, e-CMR, boekhouding)?
- Wie is eigenaar van de data? Wat is het budget? Hoe vaak verandert het plan per dag? Wat vindt de planner van bestaande pakketten zoals Modality? Hoe gaan ze om met de privacy van chauffeursgegevens?

---

## 13. Wat dit betekent voor jouw planningssysteem

### 13.1 Wat is makkelijk en wat is moeilijk?

| Onderdeel | Inschatting | Waarom |
|---|---|---|
| Orders, klanten, locaties en containers invoeren | **Makkelijk** | Gewone formulieren. Het controlecijfer van het containernummer is simpel (hoofdstuk 2) |
| Planbord met ritten, chauffeurs en trekkers | **Middel** | Veel uitzonderingen. Een planner wijzigt het plan vaak. Snel bewerken is belangrijk |
| Statusflow en chauffeurs-app | **Middel** | App op de telefoon, foto's, tijdstempels |
| LFD en demurrage/detention-teller | **Makkelijk om te rekenen, moeilijk om de data te krijgen** | Datumrekenen is simpel. De LFD komt van rederijen en elke rederij is anders |
| Rij- en rusttijden berekenen | **Middel** | De regels zijn duidelijk. Maar de tachograaf is de echte waarheid. Jij voorspelt alleen |
| Gewichtscontrole | **Moeilijk** | Je hebt trekkergewicht, assen en regels per land nodig. Bronnen spreken elkaar tegen |
| Slotbeheer en pre-notificatie | **Moeilijk** | Via Portbase. Regels veranderen. Een wijziging kan je slot kosten |
| Koppelingen (Portbase, terminals, rederijen) | **Moeilijk** | De klant moet de aanvraag doen. ECT-API's pas bij Premium Plus. Voor APMT en RWG geen API-info gevonden |
| Tarief en facturatie | **Middel** | Veel toeslagen. Dieselformules en wachttijdregels zijn onbekend |
| Automatisch optimaliseren van combinaties en routes | **Moeilijk, en het minst nodig** | Onderzoeksmodellen negeren rijtijdregels ([arXiv](https://arxiv.org/pdf/2012.06538)). Een planner wil eerst overzicht en waarschuwingen |
| Meerdere landen | **Moeilijk** | Verbodsdagen, feestdagen per deelstaat, gewichten. Frankrijk en Luxemburg onbekend |
| Ritduur voorspellen | **Moeilijk** | Geen wachttijddata. Je moet van je eigen data leren |

### 13.2 Entiteiten en velden (voorstel)

Dit is **mijn ontwerp**, afgeleid van wat Portbase, Modality en drayage-systemen gebruiken ([Portbase CCI](https://support.portbase.com/hc/en-gb/articles/32493593538450), [Portbase HCN](https://hcn.pcs.portbase.com/api-documentation/connection_instructions.html), [Modality](https://modality.nl/?p=1673)). Velden met * zijn nodig voor een eerste versie. **Vet** zijn velden die uit dit onderzoek komen en die in een standaard planningssysteem vaak ontbreken. Toets het met een planner.

| Entiteit | Belangrijkste velden |
|---|---|
| **Klant** | id*, naam*, factuuradres, betaaltermijn, tariefgroep, contactpersoon, e-mail voor orderbevestiging |
| **Locatie** | id*, type* (terminal, depot, klant, overig), naam*, adres, lat/lon*, **land***, openingstijden*, standaard laad- en lostijd*, live of drop, max gewicht en hoogte, ADR toegestaan, stroom voor reefer, toegangseisen, **havennummer of terminalcode** |
| **Terminal- of depotregels** | locatie*, Portbase-code, handlingtypes, **slotsysteem (type, slotlengte, tolerantie, capaciteit)**, TAR verplicht?, cargo closing, **lege-container-regels per rederij**, no-show-regels, geldig van - tot |
| **Rederij** | id*, naam*, SCAC*, **vrije dagen demurrage en detention***, **tarieftabel per type container***, retourregels, street-turn-regels |
| **Order** | id*, klant*, klantreferentie*, type* (import, export, leeg, ITT), boeking of B/L*, gewenst tijdvenster*, status*, bron, opmerkingen |
| **Container** | nummer* (controlecijfer), rederij*, **maat*** (20/40/45), **type*** (DC/HC/reefer/tank/flat/OT), tarra, bruto, **VGM***, zegel, **IMO-klasse en UN-nummer**, reefer-setpoint, OOG, status |
| **Vrijgave (release)** | container*, commerciële release (release-to, geldig tot), douane, inspectie, terminalstatus, pincode of release-nr (indien van toepassing), ontlaaddatum*, **last free day***, bron en tijdstip |
| **Rit** | id*, order*, container*, volgnr, type* (afhaal, aflever, leeg retour, pre-pull, shuttle, ITT), van*, naar*, tijdvenster*, slot, trekker*, chassis*, chauffeur*, status*, geplande en werkelijke km |
| **Stop** | rit*, volgnr*, locatie*, type* (gate-in, gate-out, laden, lossen, drop, pickup), geplande en werkelijke aankomst en vertrek*, **wachttijd***, geofence-events |
| **Slot en pre-notificatie** | rit*, terminal*, handlingtype*, slotvenster*, **TAR***, HCN-id, status* (aangevraagd, toegekend, geweigerd, no-show, gebruikt), reject-code, laatst gewijzigd |
| **Chauffeur** | id*, naam*, contracturen*, CE en code 95, **ADR geldig tot**, **CCV (LZV)**, **ECT-veiligheidstest geldig tot***, CargoCard, beschikbaarheid en verlof*, tachograafkaart, app-account |
| **Trekker** | id*, kenteken*, **assen en aandrijving (4x2, 6x2, 6x4)***, **tarra***, **technisch toegestane massa***, **max last aandrijfas**, Euro-klasse, CO2-klasse, ZE, ADR-uitvoering, LZV-ontheffing, tolkastje (OBU), APK en onderhoud |
| **Chassis** | id*, nummer*, **type*** (20, 40, 45, uitschuifbaar, tank), **assen***, **tarra***, **max kingpin en asgroep**, gooseneck-tunnel, **hoogte kingpin**, lengte in en uit, liftas, genset, twistlock-uitrusting, eigen of pool |
| **Landregels** (nieuw) | land*, **max massa per combinatietype***, max hoogte, breedte en lengte, tol per klasse, **verbodsdagen en uren met uitzonderingen***, geldig van - tot*, bron |
| **Feestdagenkalender** (nieuw) | land en deelstaat*, datum*, verbod ja of nee |
| **Rijtijd-registratie** (nieuw) | chauffeur*, datum*, rijtijd, werktijd, pauze, rust, bron (tachograaf of handmatig) |
| **Document** | id*, gekoppeld aan order, container of rit, type (B/L, D.O., CMR, POD-foto, weegbon, douanedocument), bestand, tijdstip |
| **Tariefregel** | klant of tariefgroep*, van - naar*, containertype*, basisprijs*, geldig van - tot, dieseltoeslag, heffing-doorbelasting, wachttijdtarief en vrije minuten, extra stop, ADR-, reefer- en gewichtstoeslag |
| **Factuur en regel** | factuur*, klant*, order of rit, regeltype, bedrag*, btw, periode, status |

**Relaties.** Eén klant heeft meerdere orders. Eén order heeft meerdere containers. Eén container heeft meerdere ritten en meerdere versies van de vrijgave. Een rit heeft precies één trekker, één chauffeur en één chassis. Bij drop and hook kan het chassis per stop wisselen. Een rit heeft meerdere stops en nul of één slot. Een terminal heeft meerdere slots. Een rederij heeft meerdere containers.

### 13.3 Statusflow (voorstel)

```
Order:      Nieuw -> Gepland (alle ritten toegewezen) -> Onderweg -> Op terminal / Bij klant
            -> Geleverd -> Leeg retour -> Afgerond -> Gefactureerd
            Zijtakken: Geannuleerd | Geblokkeerd (release ontbreekt) | Probleem (no-show, cut-off gemist)

Rit:        Concept -> Gepland (chauffeur, trekker, chassis en slot vast) -> Geaccepteerd (app)
            -> Onderweg -> Aangekomen -> In behandeling -> Klaar -> Afgerond
            Zijtak: Geweigerd door terminal | Slot gemist

Container:  Aangekondigd -> Gelost -> Vrij (release + douane + terminal) -> Opgehaald
            -> Geleverd -> Geladen of geleegd -> Leeg retour afgemeld

Slot:       Aangevraagd -> Toegekend -> Gebruikt
            Zijtakken: Geweigerd | Gewijzigd | Geannuleerd | No-show

Release:    Onbekend -> Verwacht -> Vrij
            Zijtak: Geblokkeerd (douane, rederij of terminal)
```

### 13.4 Belangrijkste planningsregels (constraints)

"Hard" betekent dat het systeem de planning niet laat opslaan. "Waarschuwing" betekent dat de planner het mag overrulen, met een reden. Begin met waarschuwingen waar je data nog niet compleet of zeker is.

| Nr | Regel | Soort | Data die je nodig hebt | Kennis nu |
|---|---|---|---|---|
| 1 | Geen dubbele boeking van container, trekker, chassis of chauffeur | Hard | Tijden van ritten | Eigen ontwerp |
| 2 | Chassis past bij container (maat, HC en tunnel, tank, reefer) | Hard | Chassis- en containertype | Bevestigd (hoofdstuk 3) |
| 3 | Gewicht: bruto + chassis + trekker binnen de grens van route en kenteken | Waarschuwing, later hard | VGM, tarra's, technisch toegestane massa, land | Deels (hoofdstuk 4 - 5) |
| 4 | Aslast: aandrijfas minimaal 1/5, tridem-limiet | Waarschuwing | Assen, aslasten | Details **Open** |
| 5 | Hoogte maximaal 4,00 m en tunnelhoogte | Waarschuwing | Kingpinhoogte, containerhoogte | Schatting |
| 6 | Lengte (45ft: 17,30 m, LZV) | Hard of waarschuwing | Lengte, ontheffing | Bevestigd en **Open** |
| 7 | Rij- en rusttijden (EU 561) | Waarschuwing | Rijtijd-registratie | Bevestigd (hoofdstuk 6) |
| 8 | Arbeidstijd: pauze, dienstlengte, overwerk | Waarschuwing en kosten | Contracturen, tijden | Deels bevestigd |
| 9 | Slot nodig, binnen tolerantie, capaciteit | Hard | Slotregels per terminal | Bevestigd (ECT, APMT). RWG en Delta II **Open** |
| 10 | Pre-notificatie compleet vóór de rit | Hard | HCN-velden | Bevestigd |
| 11 | Release, douane en terminal groen | Waarschuwing | Release-status | Deels |
| 12 | Ophalen vóór LFD, toon de kosten | Waarschuwing met bedrag | LFD, D&D-tabel | Tarieven bevestigd. Bron LFD **Open** |
| 13 | Tijdvensters en openingstijden van klant, depot, terminal | Hard of zacht | Openingstijden | Eigen data |
| 14 | ADR: chauffeur, voertuig en tunnel | Hard | ADR-gegevens | Bevestigd (hoofdstuk 2) |
| 15 | Reefer: stroom of genset | Hard | Plug of genset | Bevestigd |
| 16 | Chauffeur heeft toegang tot de terminal (ECT-test, CargoCard) | Hard | Geldigheidsdatums | Bevestigd |
| 17 | Verbodsdagen per land en deelstaat (DE zondag, FR, LU) | Hard | Kalender per land | Duitsland bevestigd. FR en LU secundair |
| 18 | Retourregels lege container (rederij, depot open of dicht) | Waarschuwing | Regels per rederij | Deels |
| 19 | LZV: ontheffing, CCV en route op het netwerk | Hard | Ontheffing en certificaat | Bevestigd |
| 20 | Tol en zero-emissiezone | Kosten of route | Euro- en CO2-klasse, jaar eerste registratie | Bevestigd. Haven in ZE-zone **Open** |

### 13.5 Kritische punten en risico's

Je vraagt om eerlijkheid, dus hier komt het.

1. **Je weet nog niet wat de planner echt nodig heeft.** Alles in dit rapport komt van websites. Er is geen enkel gesprek met een planner gevoerd. Zonder dat bouw je kans op het verkeerde. Ga eerst een dag meekijken. Dat is belangrijker dan het volgende stuk code.
2. **Bouwen of kopen?** Er bestaan al systemen. Modality (Barendrecht) doet o.a. planning met tijdlijn, Portbase-koppeling, e-CMR, orderinvoer met OCR en AI, een truck-app en automatische facturatie. ICT Intermodal TMS en Go4Logistics bestaan ook ([Modality](https://modality.nl/?p=1673), [ICT](https://www.ict.eu/en/products/intermodal-transport-management-system-tms), [Go4Logistics](https://www.antwerpxl.com/products/container-transport-software-30180/)). Een generiek pakket als EasyTrans kost vanaf ca. $ 32 per gebruiker per maand en mist waarschijnlijk containerfuncties (Schatting, [Capterra](https://www.capterra.com/p/167861/EasyTrans/)). Vraag het bedrijf waarom het deze systemen niet gebruikt. Mogelijke kansen zijn een hypothese en niet getest: slot-bewuste planning, LFD- en detention-bewaking met het bedrag erbij, rijtijdcontrole in de planning, en een lage drempel voor kleine bedrijven.
3. **Fouten kosten echt geld.** Een no-show bij ECT kan € 100 kosten, detention € 60 - 150 per dag, overbelading een proces-verbaal en een doorrijverbod. Laat het systeem waarschuwen en laat de planner beslissen. Draai het eerste half jaar naast het oude systeem.
4. **De regels veranderen snel.** ECT wijzigde in korte tijd de slotlengte (4 naar 2 uur), de datum van de veiligheidstest (twee keer verschoven) en de invoering van de heffingen. De Nederlandse tol, de Portbase-tarieven en de EU-gewichtsregels veranderen in 2027. **Sla regels op als data** met "geldig van - tot" en een bron. Zet ze niet in de code.
5. **De data komt van anderen.** Release, LFD, slot en TAR komen van rederijen, terminals en Portbase. Portbase-toegang vraagt de klant aan, met testomgeving en een IAMconnected-account. ECT-API's zijn alleen voor Premium Plus. Voor APMT en RWG vond ik geen API-informatie. Koppelen met de IT van een grote verlader kan meer dan een jaar duren ([EUR](https://www.eur.nl/en/upt/media/2025-12-rapportde-opkomst-van-carrier-logistics201125-2)). Begin met handmatige invoer van TAR, slot en LFD.
6. **Pre-notificatie en slots hebben bijwerkingen.** Een wijziging van containergegevens kan je slot kosten. Gebruik een statusmodel en stuur nooit automatisch opnieuw. Updates komen via long polling, dus je hebt een poller nodig die dubbele berichten aankan.
7. **Gewicht is moeilijker dan het lijkt.** Het trekkergewicht en het aantal assen zijn onbekend. Bronnen spreken elkaar tegen (24 of 27 ton, aandrijfas of stuuras). Elk land is anders. Begin met: VGM + tarra's tegen de technisch toegestane massa en de landgrens, met een marge in beeld.
8. **Beloof geen wettelijke naleving.** De tachograaf is de wettelijke waarheid. Jij voorspelt. Tachograafdata uitlezen is niet onderzocht. Arbeidstijd (pauze, overwerk) is een aparte regel naast rijtijd.
9. **Ritduur voorspellen kan niet zonder eigen data.** Er zijn geen openbare wachttijden. Log vanaf dag één echte tijden (aankomst, vertrek, wachten) per terminal en tijdstip. Daarmee kun je later plannen en wachttijd doorbelasten. Dat laatste is een hypothese.
10. **Automatisch optimaliseren is verleidelijk en niet nodig.** Planners moeten snel kunnen wijzigen als het plan verandert. Eerst overzicht en waarschuwingen. Optimalisatie later.
11. **Eén land eerst.** Begin met Nederland. Zet Duitsland op alleen waarschuwingen. Laat Frankrijk en Luxemburg weg tot ze zijn uitgezocht.
12. **Privacy.** Locatie en rijtijden van chauffeurs zijn persoonsgegevens (AVG). Dat is niet onderzocht. Vraag het na.
13. **ETA's van schepen zijn onbetrouwbaar.** Schema's van rederijen waren in 2024 maar ca. 50 - 55% op tijd. Je LFD en vrijgave schuiven dus. Bouw voor wijzigen, niet voor een vast plan.
14. **Wat is makkelijk te onderschatten?** (a) Hoeveel uitzonderingen er per dag zijn. (b) Dat veel gegevens handmatig blijven. (c) Dat regels per terminal, rederij en land verschillen. (d) Dat een planner een systeem alleen gebruikt als het sneller is dan Excel of de telefoon.
15. **Wat is makkelijk te overschatten?** Dat je alles in een eerste versie kunt koppelen.

### 13.6 Voorstel bouwvolgorde (mijn advies)

1. **Fase 1: planbord.** Orders, containers (met controlecijfer), locaties, chauffeurs, trekkers, chassis. Ritten plannen en verslepen. Statusflow. Handmatig invoeren van slot, TAR en LFD. Waarschuwingen voor dubbele boeking, LFD, chassis-fit en een eenvoudige rijtijdcontrole.
2. **Fase 2: chauffeurs-app en data.** Mijlpalen en tijden (ook wachttijd) vastleggen. Foto's en handtekening. Eigen wachttijd-statistiek per terminal. Tariefmodule en een exportbestand voor facturatie. Bewaking van demurrage en detention met bedrag.
3. **Fase 3: koppelingen.** Eerst Portbase HCN Road (pre-notificatie en status). Dan Cargo Controller (als je toegang krijgt). Daarna rederij-ETA (DCSA of een aanbieder), telematica en e-CMR ([DCSA](https://dcsa.org/newsroom/dcsa-standards-roadmap-2026), eFTI voor autoriteiten vanaf 9 juli 2027: [Europese Commissie](https://transport.ec.europa.eu/transport-themes/logistics-and-multimodal-transport/efti-regulation_en)).
4. **Fase 4: slim.** Gewichtscontrole met echte trekker- en chassisdata. Slot-bewuste planning. Pas daarna optimaliseren.

---

## Bronnenlijst

**Containers en materieel**
- [DHL, cargo container sizes and types](https://www.dhl.com/nl-en/home/global-forwarding/freight-forwarding-education-center/cargo-container-sizes-and-types.html)
- [Wikipedia, Intermodal container](https://en.wikipedia.org/wiki/Intermodal_container)
- [Wikipedia, ISO 6346](https://en.wikipedia.org/wiki/ISO_6346)
- [Wikipedia, Sidelifter](https://en.wikipedia.org/wiki/Sidelifter)
- [Maersk, types and sizes of containers](https://www.maersk.com/support/faqs/2024/07/01/types-and-sizes-of-containers)
- [Rothschenk, intermodal transport](https://rothschenk.de/en/sequence-19-combined-traffic/)
- [Rijkswaterstaat, Containers en vrachtwagens (1997)](https://open.rijkswaterstaat.nl/@124359/containers-vrachtwagens-paar-apart/)
- [GOV.UK, Verified gross mass of containers](https://www.gov.uk/government/publications/verified-gross-mass-of-containers)
- [HSE, ADR/IMDG combined road and sea journey](https://www.hse.gov.uk/CDG/commonproblems/adr-imdg.htm)
- [Kässbohrer, container chassis brochure](https://kaessbohrer.com/static/media/category/585/attachments/container-chassis-nl-digi_210518_1409.pdf)
- [Broshuis MFCC HD (DirectIndustry)](https://directindustry.com/prod/broshuis-bv/product-201391-2296130.html)
- [Schmitz Cargobull, S.CF LIGHT 40/45](https://www.cargobull.com/be/producten/container-chassis/s-cf-light-40-45)

**Wetgeving, rij- en rusttijden, tol**
- [government.nl, requirements for lorries](https://government.nl/topics/freight-transportation/requiremenst-for-lorries)
- [Rijksoverheid, goederenvervoer over de weg](https://www.rijksoverheid.nl/onderwerpen/goederenvervoer/goederenvervoer-over-de-weg)
- [RDW, overzicht maten en gewichten (2012, via Provincie Fryslan)](https://cuatro.sim-cdn.nl/fryslan/uploads/Overzicht-maten-en-gewichten%20%28RDW%29.pdf)
- [OM, instructie voertuigafmetingen 2021I003](https://www.om.nl/onderwerpen/b/beleidsregels/instructies/verkeer/instructie-voertuigafmetingen-2021i003)
- [OM, instructie wegingen en wiellastmetingen 2022I006](https://www.om.nl/onderwerpen/b/beleidsregels/instructies/verkeer/instructie-wegingen-en-wiellastmetingen-2022i006)
- [OM, bijlage 3 toegestane massa en aslasten](https://www.om.nl/binaries/om/documenten/richtlijnen/2022/12/13/tabel-toegestane-maximummassa-en-aslasten-buitenlandse-voertuigen/Bijlage+3+bij+Instructie+wegingen+en+wiellastmetingen+%282022I006%29.pdf)
- [RDW, jaarontheffing LZV](https://www.rdw.nl/zakelijke-partners/exceptioneel-transport/ontheffing-aanvragen-voor-exceptioneel-transport/aanvragen-jaarontheffing-lzv)
- [Stimular, grotere of lichtere vrachtauto's](https://www.stimular.nl/maatregelen/grotere-of-lichtere-vrachtautos)
- [Rijkswaterstaat, inhaalverbod vrachtverkeer](https://www.rijkswaterstaat.nl/wegen/wetten-regels-en-vergunningen/verkeerswetten/inhaalverbod-vrachtverkeer)
- [NOS, Maastunnel doorrijhoogte](https://nos.nl/l/2546194)
- [Europarl Legislative Train, revision weights and dimensions](https://www.europarl.europa.eu/legislative-train/theme-a-european-green-deal/file-revision-of-the-weights-and-dimensions-directive)
- [Raadsdocument ST-15611-2025](https://data.consilium.europa.eu/doc/document/ST-15611-2025-INIT/en/pdf)
- [Gesetze im Internet, § 34 StVZO](https://www.gesetze-im-internet.de/stvzo_2012/__34.html)
- [Gesetze im Internet, § 30 StVO](https://www.gesetze-im-internet.de/stvo_2013/__30.html)
- [ANWB, zondagsverbod Duitsland augustus 2026](https://www.anwb.nl/verkeer/nieuws/buitenland/2026/augustus/tijdelijk-vrachtverkeer-op-zondag-in-duitsland)
- [Vlaanderen.be, tonnageverhoging](https://www.vlaanderen.be/mobiliteit-en-openbare-werken/vrachtverkeer/tonnageverhoging-voor-vrachtverkeer)
- [Brussels Times, Flanders weights (okt 2025)](https://www.brusselstimes.com/1800798/flanders-increases-maximum-weight-for-low-and-zero-emission-trucks)
- [Impargo, truck driving bans Europe (secundair)](https://impargo.de/en/blog/truck-driving-bans-europe)
- [EC, Mobility Package driving and rest times](https://transport.ec.europa.eu/transport-modes/road/mobility-package-i/driving-rest-times_en)
- [Rijksoverheid, rijtijden en rusttijden wegvervoer](https://www.rijksoverheid.nl/themas/werk/arbeidsomstandigheden/vraag-en-antwoord/werktijden/rijtijden-en-rusttijden-wegvervoer)
- [Hof van Justitie, persbericht 173/24](https://curia.europa.eu/jcms/upload/docs/application/pdf/2024-10/cp240173en.pdf)
- [business.gov.nl, new rules for international transport](https://business.gov.nl/international/international-transport/new-rules-for-international-transport-and-drivers/)
- [Europese Commissie, slimme tachograaf (aug 2025)](https://transport.ec.europa.eu/news-events/news/stronger-and-more-unified-enforcement-eu-rules-international-road-transport-smart-tachograph-2025-08-19_en)
- [CNV, Cao BGV 2026](https://www.cnv.nl/vervoer/vervoer-en-logistiek/cao-beroepsgoederenvervoer/01-01-2026_31-12-2026/)
- [CNV, Cao BGV roosters](https://www.cnv.nl/vervoer/vervoer-en-logistiek/cao-beroepsgoederenvervoer/nieuws/cao-bgv-ken-je-cao-2026-nr-6-roosters-2026-09-01/)
- [Rijksoverheid, vrachtwagenheffing van start](https://www.rijksoverheid.nl/actueel/nieuws/2026/07/01/vrachtwagenheffing-vandaag-van-start)
- [vrachtwagenheffing.nl, bedragen](https://www.vrachtwagenheffing.nl/dit-gaat-u-betalen)
- [RDW, tarieven vrachtwagenheffing 2027](https://www.rdw.nl/over-rdw/nieuws/2026/tarieven-vrachtwagenheffing-2027)
- [trans.info, Lkw-Maut 2027 (IRU)](https://trans.info/de/lkw-maut-2027-neue-regeln-fuer-europas-transporteure-507770)
- [Toll Collect, Mauttarife 2024](https://toll-collect.de/en/toll_collect/bezahlen/maut_tarife/p1745_mauttarife_07_2024.html)
- [WKO, Lkw-Maut in Deutschland](https://www.wko.at/transport/maut-lkw-deutschland)
- [Viapass, rates](https://viapass.be/en/rates/)
- [Op weg naar ZES, vrachtauto's](https://opwegnaarzes.nl/bedrijven/toegangsregels/vrachtauto-n2-en-n3-voertuigen-zwaarder-dan-3500-kg)
- [evofenedex, ADR-tunneloverzicht 2026](https://www.evofenedex.nl/api/v1/sharepoint/file/Shared%20Documents/Download%20Gevaarlijke%20Stoffen/ADR-tunneloverzicht%20Nederland%202026.pdf)
- [Ondernemersplein, gevaarlijke stoffen vervoeren](https://ondernemersplein.overheid.nl/wetten-en-regels/gevaarlijke-stoffen-vervoeren-over-de-weg/)

**Rotterdam**
- [Port of Rotterdam, node 1164](https://www.portofrotterdam.com/en/node/1164)
- [Port of Rotterdam, 2025 container year](https://www.portofrotterdam.com/en/news-and-press-releases/between-growth-and-pressure-rotterdams-2025-container-year-under-review)
- [Port of Rotterdam, mandatory container weighing](https://www.portofrotterdam.com/en/logistics/cargo/containers/mandatory-container-weighing-port-rotterdam)
- [Port of Rotterdam, terminals en depots (2021)](https://www.portofrotterdam.com/sites/default/files/2021-06/container-terminals-and-depots-in-the-rotterdam-port-area.pdf)
- [Port of Rotterdam, Container Exchange Route](https://portofrotterdam.com/en/node/1012)
- [Port of Rotterdam, off-peak transport](https://www.portofrotterdam.com/en/news-and-press-releases/peak-transport-makes-supply-chains-faster-and-more-reliable)
- [Port of Rotterdam, digital report 2025](https://publications.portofrotterdam.com/digital-report-2025/case-study-1)
- [Port of Rotterdam, digital report 2024 (Port Alert)](https://publications.portofrotterdam.com/digital-report-2024/port-alert)
- [ECT, road services](https://www.ect.nl/en/services/road-services)
- [ECT, news feed](https://www.ect.nl/en/news-feed)
- [ECT, TCMS (18 sep 2026)](https://www.ect.nl/en/news/news-feed/ect-introduces-truck-capacity-management-system)
- [ECT, TCMS update (18 nov 2026)](https://www.ect.nl/en/news/news-feed/update-truck-capacity-management-system-hutchison-ports-ect-rotterdam)
- [ECT, update 2 veiligheidstest](https://www.ect.nl/en/news/news-feed/update-2-mandatory-safety-test-drivers)
- [ECT, veiligheidsfolder](https://www.ect.nl/sites/d10p.ect.nl/files/2025-09/ECT_Veilig_En_Beveiligd_DT_1c_EN_hvnr8202.pdf)
- [ECT MyTerminal, timeslots](https://myterminal.ect.nl/help-center/features/pages/timeslots)
- [ECT MyTerminal, remote check-in](https://myterminal.ect.nl/news/period-validity-pre-announced-truck-visits-ect-terminals)
- [ECT MyTerminal, empty container delivery](https://myterminal.ect.nl/help-center/features/pages/empty-container-delivery)
- [ECT MyTerminal, truck charges](https://myterminal.ect.nl/help-center/registration/finance/truck-invoices)
- [ECT, export booking status API](https://myterminal-tst.ect.nl/api-products/export-booking-status)
- [ECT, digital services](https://www.ect.nl/en/services/digital-services)
- [Hutchison Ports Delta II](https://hutchisonports.com/ports/world/hutchison-ports-delta-ii/)
- [Seatrade Maritime, Hutchison en TIL](https://www.seatrade-maritime.com/terminals/hutchison-and-msc-to-develop-new-maasvlakte-i-box-terminal)
- [APM Terminals Maasvlakte](https://apmterminals.com/en/maasvlakte)
- [APMT, online services](https://www.apmterminals.com/en/maasvlakte/e-tools/online-services)
- [APMT, truck](https://www.apmterminals.com/en/maasvlakte/modalities/truck)
- [APMT, FAQ](https://www.apmterminals.com/en/maasvlakte/practical-information/faq)
- [APMT, nieuwsbrief februari 2026](https://www.apmterminals.com/en/maasvlakte/newsletter/20260209-newsletter-2026-02)
- [APMT, volgeboekte slots (juni 2026)](https://www.apmterminals.com/en/maasvlakte/about/news-and-updates/2026/260626-Fully-booked-timeslots-working-on-solutions)
- [Cyprus Shipping News, Hapag-Lloyd en APMT MVII](https://cyprusshippingnews.com/2026/11/10/hapag-lloyd-completes-acquisition-of-25-stake-in-apm-terminals-maasvlakte-ii/)
- [RWG](https://www.rwg.nl/en/about-rwg)
- [Portbase, HCN Road](https://www.portbase.com/en/services/hinterland-container-notification-road/)
- [Portbase, HCN API](https://hcn.pcs.portbase.com/api-documentation/connection_instructions.html)
- [Portbase, pre-notificatie terminals en depots](https://portbase.com/en/?p=10109)
- [Portbase, slottabel](https://support.portbase.com/en/?p=19733)
- [Portbase, Cargo Controller](https://support.portbase.com/en/services/cargo-controller-en/)
- [Portbase, Cargo Controller Import API](https://support.portbase.com/hc/en-gb/articles/32493593538450)
- [Portbase, Secure Chain](https://www.portbase.com/en/programs/secure-chain/)
- [Portbase, Secure Chain voor verladers](https://www.portbase.com/en/programs/secure-chain/shippers/)
- [Portbase, Clearance Transit Export](https://support.portbase.com/en/services/clearance-transit-export-containers)
- [Portbase, gate-in uitleg](https://support.portbase.com/en/kennis/my-container-is-at-the-terminal-but-it-does-not-have-a-gate-in-how-is-that-possible/)
- [Portbase, Road Planning System Interface (oud)](https://support.portbase.com/en/services/road-planning-system-interface/)
- [Belastingdienst, Container Release Message](https://belastingdienst.nl/wps/wcm/connect/en/customs/content/container-release-message-see-how-your-import-declaration-is-changing)
- [Maersk, import Nederland](https://www.maersk.com/local-information/europe/netherlands/import)
- [Hapag-Lloyd, NL import D&D (jan 2026)](https://www.hapag-lloyd.com/content/dam/website/downloads/pdf/netherlands_demurrage_detention_import_20260120_update.pdf)
- [Contargo, current customer information](https://www.contargo.net/en/business/business-news/current-customer-information/)
- [Rijkswaterstaat, A15 onderhoud](https://www.rijkswaterstaat.nl/wegen/projectenoverzicht/a15-onderhoud-maasvlakte-vaanplein/hinder-en-maatregelen)
- [Rijkswaterstaat, Botlekbrug](https://www.rijkswaterstaat.nl/wegen/projectenoverzicht/a15-botlekbrug-nieuwe-verbinding-weg-en-goederenspoorverkeer-scheepvaart-en-bromfietsers)
- [AJOT, eerste negen maanden 2026](https://www.ajot.com/news/throughput-in-the-port-of-rotterdam-rose-by-0.9-in-the-first-nine-months-of-the-year)
- [Welingelichte Kringen, staking](https://www.welingelichtekringen.nl/economie/havenbedrijf-impact-staking-op-rotterdamse-haven-is-beperkt)
- [Trans.info, port delays](https://trans.info/en/port-delays-congestion-498894)
- [FreshPlaza, when can I collect my container](https://www.freshplaza.com/article/9306281/when-can-i-collect-my-container/)
- [TU Delft MSc-scriptie (wachttijden, kosten)](https://repository.tudelft.nl/file/File_105b8c36-b4d0-4b76-9519-9ba2a3fd60dd?preview=1)

**Buiten Rotterdam**
- [Port of Antwerp-Bruges, factsheet 2025](https://newsroom.portofantwerpbruges.com/hubfs/260122_Factsheet_Jaarcijfers_2025_ENG.pdf?hsLang=en)
- [Port of Antwerp-Bruges, night logistics](https://www.portofantwerpbruges.com/en/business/transportation/road-transport/night-logistics)
- [Transport Journal, geen pincodes in Antwerpen](https://www.transportjournal.com/home/news/artikeldetail/no-more-pin-codes-in-antwerp.html?L=.)
- [NxtPort, CPu voor transport operators](https://documentation.nxtport.com/certified-pickup/cpu-for-transport-operators)
- [Maersk, CPu go-live](https://maersk.com/news/articles/2024/05/02/certified-pick-up-go-live-date-for-terminals-behind-the-locks)
- [PSA, TAMS guideline](https://www.psa-antwerp.be/sites/psa-antwerp/files/2025-05/eportal-guideline-tams.pdf)
- [PSA, distribution surcharge FAQ](https://psa-antwerp.be/en/faq-ds-en)
- [Kuehne+Nagel, PSA export window](https://mykn.kuehne-nagel.com/news/article/psa-antwerp-reduces-export-delivery-window-to-07-Apr-2025)
- [DP World Belgium, opening hours](https://www.dpworld.com/belgium/contact-us/opening-hours)
- [Contargo, serious delays Rotterdam en Antwerpen](https://www.contargo.net/en/business/business-news/detail-business/serious-delays-in-truck-handling-in-rotterdam-and-antwerp/)
- [Brussels Times, congestietoeslag Antwerpen](https://www.brusselstimes.com/1729204/antwerp-port-congestion-leads-transporters-to-introduce-heavy-surcharges)
- [Hellenic Shipping News, Antwerpen H1 2026](https://www.hellenicshippingnews.com/port-of-antwerp-bruges-stands-firm-in-a-challenging-first-half-of-2026/)
- [VRT, Liefkenshoektunnel](https://www.vrt.be/vrtnws/nl/2026/01/08/liefkenshoektunnel-tolvrij-gezakt-file-antwerpen/)
- [ECT, MCT Moerdijk](https://www.ect.nl/en/terminals/mct-moerdijk)
- [UIRR, CCT Moerdijk (gesponsord)](https://www.uirr.com/web-news/smart-carrier-chooses-multimodal-moerdijk)
- [Maersk, inland services Nederland](https://www.maersk.com/local-information/europe/netherlands/local-solutions/inland-services)
- [Port of Rotterdam, corridors (2021)](https://www.portofrotterdam.com/sites/default/files/2021-08/cooperation-in-the-corridor-port-of-rotterdam.pdf)
- [Port of Rotterdam, on water if possible](https://portofrotterdam.com/en/news-and-press-releases/water-if-possible-road-if-necessary)
- [Port of Rotterdam, optimising inland shipping](https://portofrotterdam.com/en/logistics/connections/intermodal-transportation/inland-shipping/optimising-inland)
- [Dredgewire, interview Hanna Stelzel](https://dredgewire.com/interview-with-hanna-stelzel-director-containers-port-of-rotterdam)
- [Contargo, rail capacity limitations](https://www.contargo.net/en/business/business-news/detail-business/rotterdam-rail-capacity-limitations-from-july-2026/)
- [UIRR, duisport 2025](https://www.uirr.com/web-news/duisport-closes-very-successful-2025)
- [duisport, terminals](https://duisport.de/en/terminals/)
- [Hapag-Lloyd, Rhine low water](https://www.hapag-lloyd.com/en/services-information/offices-localinfo/local-news/2026/07/germany--rhine-low-water-is-affecting-hinterland-transport.html)
- [S&P Global, 18 september 2026](https://www.spglobal.com/energy/en/news-research/latest-news/crude-oil/091826-rhine-water-levels-approach-zero-threaten-barge-transport)
- [S&P Global, 1 oktober 2026](https://www.spglobal.com/energy/en/news-research/latest-news/refined-products/100126-rhine-water-levels-fall-to-new-record-low-stalling-fuel-logistics)
- [VerkehrsRundschau, Niedrigwasser (14 aug 2026)](https://www.verkehrsrundschau.de/nachrichten/transport-logistik/historisches-niedrigwasser-und-seine-folgen-fuer-die-lieferketten-3890475)
- [Railmarket, Hupac 2025](https://zh.railmarket.com/news/freight-rail/55916-hupac-posts-profit-despite-rail-disruptions)
- [Breakbulk News, Dutch rail freight](https://breakbulk.news/dutch-rail-freight-faces-higher-costs-from-subsidy-gap/)
- [The Loadstar, greener or cheaper](https://theloadstar.com/greener-or-cheaper-intermodal-options-from-ports-of-rotterdam-and-antwerp)
- [business.gov.nl, subsidy modal shift](https://business.gov.nl/subsidy/subsidy-modal-shift)

**Kosten, markt en software**
- [KiM, kostenkengetallen wegvervoer](https://www.kimnet.nl/binaries/kimnet/documenten/notities/2023/03/30/kostenkengetallen-voor-het-goederenvervoer/Kostenkengetallen+voor+het+goederenvervoer_Wegvervoer.pdf)
- [EVO, kostenontwikkelingen wegvervoer 2024-2025](https://www.evofenedex.nl/api/v1/sharepoint/file/Shared%20Documents/Download%20Vervoer/Kostenontwikkelingen_in_het_wegvervoer_in_2024_en_2025.pdf)
- [Rabobank, investeringsruimte wegtransport](https://www.rabobank.nl/kennis/d011532908-investeringsruimte-wegtransport-staat-onder-druk-door-kostenstijgingen)
- [ABN AMRO, 2026 is kantelpunt voor wegtransport](https://www.abnamro.nl/nl/zakelijk/insights/sectoren-en-trends/logistiek/2026-is-kantelpunt-voor-wegtransport.html)
- [Upply, Dutch road freight sector](https://market-insights.upply.com/en/the-dutch-road-freight-sector-strives-to-maintain-its-competitiveness)
- [trans.info, road freight rates Q3 2026](https://trans.info/road-freight-rates-q3-2026-record-513960)
- [trans.info, insolvency pressure](https://trans.info/en/dutch-and-romanian-hauliers-face-mounting-insolvency-pressure-511121)
- [EUR, De opkomst van carrier logistics (dec 2025)](https://www.eur.nl/en/upt/media/2025-12-rapportde-opkomst-van-carrier-logistics201125-2)
- [EUR, thesis Vliet](https://thesis.eur.nl/pub/40373/Vliet-L-van-der-373098-MA-thesis.pdf)
- [arXiv 2012.06538, multi-shift drayage model](https://arxiv.org/pdf/2012.06538)
- [Modality](https://modality.nl/?p=1673)
- [ICT Intermodal TMS](https://www.ict.eu/en/products/intermodal-transport-management-system-tms)
- [Go4Logistics (AntwerpXL)](https://www.antwerpxl.com/products/container-transport-software-30180/)
- [CargoWise Profit Tools TMS](https://www.cargowise.com/landside/solutions/containers-by-road/drayage-tms/profit-tools-tms/)
- [Capterra, EasyTrans](https://www.capterra.com/p/167861/EasyTrans/)
- [DCSA, standards roadmap 2026](https://dcsa.org/newsroom/dcsa-standards-roadmap-2026)
- [Europese Commissie, eFTI](https://transport.ec.europa.eu/transport-themes/logistics-and-multimodal-transport/efti-regulation_en)


---


---

# Deel 3: Een planningssysteem dat het meeste zelf doet

*Peildatum: 23 november 2026. Hoort bij deel 1 (hoofdstuk 1 t/m 13) en deel 2 (hoofdstuk 14 t/m 25). Bureauonderzoek met openbare bronnen. Er is nog niet met een planner gesproken. Geen juridisch advies.*

## A. Het belangrijkste in 1 minuut

Het antwoord eerst: een systeem dat het meeste zelf doet kun je bouwen, maar in lagen en met een mens die de uitzonderingen afhandelt. Wat in de praktijk echt automatisch loopt, is administratie: orders inlezen, berichten naar de terminal, statusvolging en facturen. Het plannen zelf blijft bij alle gevonden containerpakketten een voorstel waar de planner op klikt. De planner wordt uitzonderingsbeheerder.

Mijn advies: bouw eerst een planbord met controles en een logboek. Voeg daarna orders inlezen (met controle door een mens), tijden en status en concept-facturen toe. Dan komen meldingen aan Portbase. Voorstellen van een solver (een rekenprogramma dat plannen maakt) komen als laatste. Gebruik een bestaande solver, bijvoorbeeld OR-Tools. Laat een taalmodel alleen lezen en uitleggen, nooit plannen. Vraag eerst een offerte bij Modality: de prijs is niet openbaar en het pakket doet al veel. De softwarekosten zijn laag. De echte kosten zijn jouw tijd, onderhoud en het risico bij fouten. Mijn schatting voor "het meeste automatisch" is een jaar of meer in deeltijd. Het grootste risico is niet de techniek. Er is geen bewijs dat het bedrijf dit wil, het bedrijf lijkt klein (0 - 9 medewerkers volgens één bron) en je bouwt alleen, naast school.

| Onderwerp | Kernpunt | Status |
|---|---|---|
| Wat is "het meeste automatisch"? | Routine op niveau 3 (automatisch binnen vaste regels, uitzonderingen naar de planner). Plannen zelf op niveau 2 (voorstel + akkoord). Niveau 4 (zonder mens) niet doen | **Schatting** (alle gevonden pakketten houden plannen interactief) |
| Solver | OR-Tools in Python voor voorstellen. Timefold-Python is gearchiveerd | **Bevestigd** ([GitHub](https://github.com/TimefoldAI/timefold-solver-python)) |
| Rekentijd op dit bedrijf | Geen meting op echte containerritten gevonden | **Open** |
| Portbase HCN Road | Zelf aansluiten kan. € 249,50 eenmalig, € 11,36 per maand, € 0,40 per volle container (per 1-1-2027: € 11,70 en € 0,41) | **Bevestigd** ([Portbase](https://www.portbase.com/en/services/hinterland-container-notification-road/)) |
| Slots bij ECT | Geen aparte slot-API. Het slot volgt uit de ETA in de pre-notificatie. 2-uursslots vanaf 25 nov 2026. De € 100 no-show wordt nog niet geheven | **Bevestigd** ([ECT](https://www.ect.nl/en/news/news-feed/update-truck-capacity-management-system-hutchison-ports-ect-rotterdam)) |
| Orders inlezen | AI leest, vaste controles (o.a. ISO 6346), mens bij twijfel. Geen onafhankelijk nauwkeurigheidscijfer gevonden | **Open** |
| E-factuur voor bedrijven | Pas voorgesteld per 1 juli 2030. Niet 2026 of 2027. Nog geen wet | **Bevestigd** ([Rijksoverheid](https://www.rijksoverheid.nl/actueel/nieuws/2026/09/11/kabinet-kiest-voor-invoering-e-facturatie-en-rapportage-voor-bedrijven)) |
| Bouwen of kopen | Eerst offerte Modality. Daarna hooguit een laag eromheen bouwen. Geen volledig TMS | **Schatting** |
| Kosten per maand | Grofweg € 50 - 200 voor eigen onderdelen. Portbase, telematica en WhatsApp komen erbij | **Schatting** |
| Tijd | Planbord + controles 3 - 6 maanden. "Het meeste automatisch" een jaar of meer | **Schatting** |
| Privacy en recht | AVG geldt altijd bij GPS. OR pas vanaf 50 medewerkers. Cbw waarschijnlijk niet van toepassing. AI Act voorlopig uitgesteld | **Schatting** en **Open** |
| Grootte van het bedrijf | 0 - 9 medewerkers (Kompass), 0 FTE (Liza.nl). Geen vlootgegevens | **Open** (deel 2, hoofdstuk 18) |

---

## B. Zo lees je dit deel

De drie labels zijn hetzelfde als in hoofdstuk 1. Er is één label bij.

| Label | Betekenis |
|---|---|
| **Bevestigd** | Staat in een bron. De link staat erbij. Veel bronnen zijn gelezen via een samenvatting van de pagina |
| **Schatting** | Mijn afleiding. Geen bronfeit. Kan fout zijn |
| **Open** | Niet gevonden, of de bronnen spreken elkaar tegen |
| **Vendor-claim** | Een leverancier zegt dit over zijn eigen product. Niet onafhankelijk getoetst |

Bedragen zijn zonder btw. Geen enkel getal over tijdwinst komt uit een onafhankelijke meting bij een klein containerbedrijf (C.3). Aanpassingen op hoofdstuk 13 staan in O. Tegenstrijdigheden staan in R.

**Nieuwe woorden**

| Woord | Uitleg |
|---|---|
| Solver | Rekenprogramma dat een plan zoekt binnen regels |
| Constraint (regel) | Iets wat het plan moet of liefst moet doen. Hard = mag nooit gebroken worden. Zacht = kost straf als het gebroken wordt |
| Doelfunctie | De som van straffen en kosten die de solver zo laag mogelijk probeert te maken |
| Geofence | Onzichtbare cirkel op de kaart. Het systeem merkt wanneer een truck erin of eruit rijdt |
| Idempotent | Hetzelfde bericht twee keer verwerken geeft hetzelfde resultaat als één keer |
| Audit log | Logboek: wie veranderde wat, wanneer, van wat naar wat |
| PWA | Website die je op het beginscherm van je telefoon zet en die als app werkt |
| Bus factor | Hoeveel mensen mogen wegvallen voordat niemand het systeem meer begrijpt. Bij jou: 1 |

---

## C. Wat betekent "het meeste automatisch"?

### C.1 Vijf niveaus

| Niveau | Naam | Wie beslist? | Voorbeeld |
|---|---|---|---|
| 0 | Handmatig | De mens. Het systeem bewaart alleen | De planner sleept een rit naar een trekker |
| 1 | Waarschuwen | De mens. Het systeem controleert | "Deze chauffeur heeft maar 1 uur rijtijd over" |
| 2 | Voorstel + akkoord | De mens keurt goed, per rit of in zijn geheel | Planvoorstel voor morgen |
| 3 | Automatisch binnen vaste regels | Het systeem, zolang alle regels groen zijn. De mens kijkt naar de uitzonderingenlijst en een steekproef. Noodstop aanwezig | Pre-notificatie sturen voor een standaardrit |
| 4 | Volledig autonoom | Alleen het systeem | Niet aan te raden (zie C.2) |

De **uitzonderingenlijst** is de lijst met alles wat het systeem niet zelf mocht of kon beslissen. Bijvoorbeeld: een order waarvan een controle faalt, een rit zonder oplossing, een vol slot, een ontbrekende release. Zo'n lijst houdt de planner scherp. Zonder lijst glijden dingen weg.

### C.2 Welk niveau voor welk onderdeel? (Schatting)

Dit is mijn oordeel, op basis van de bronnen in dit deel. Het is geen meting.

| Onderdeel | Veilig doel na ca. 1 jaar | Plafond | Waarom |
|---|---|---|---|
| Orders inlezen | 2 voor alles. 3 voor bekende afzenders als alle controles groen zijn | 3 | Vorm is te garanderen, inhoud niet. Een fout containernummer kost geld (E) |
| Ritten plannen | 2 | 3 voor standaard droge containers, na een schaduwproef | Alle gevonden pakketten houden plannen interactief (C.3) |
| Chauffeur, trekker en chassis toewijzen | 2. Voor tank en ADR niveau 1 | 3 voor standaard. Tank en ADR maximaal 2 | Harde regels (ADR, gewicht, rijtijd). Een fout is een juridisch en veiligheidsrisico |
| Portbase-melding | Status lezen: 3. Melden: eerst 2, daarna 3 voor standaardritten waarvan de release groen is | 3 | De kosten zijn laag, maar een fout raakt direct het slot (F) |
| Slots | ETA sturen: 2, later 3. Annuleren kort voor slotbegin: 2 | 3 voor ETA, 2 voor annuleren | Na slotbegin geldt een annulering als no-show (F.2) |
| Statusvolging | 3 | 3, en 4 voor puur registreren van tijden | Veiligste en best bewezen onderdeel (G.1) |
| Herplannen | 1, daarna 2 (voorstel bij vertraging) | 2. Niveau 3 alleen voor kleine wijzigingen, zoals een ETA doorgeven | Een plan dat steeds verschuift kost vertrouwen (D.5) |
| Facturatie | Concept automatisch (3). Versturen na akkoord (2) | 3 voor standaardtarieven. Afwijkingen naar de uitzonderingenlijst | Alleen contractuele tarieven toepassen (G.5) |

Niveau 4 staat nergens als doel. Reden: bij elk onderdeel kost een fout geld, tijd of veiligheid, en de bronnen laten zien dat mensen een systeem ofwel te veel vertrouwen ofwel laten liggen (L.3).

### C.3 Wat de bronnen echt zeggen over "automatisch"

- **Modality** beschrijft wegtransport als "interactief" plannen: tijdlijn, ritten splitsen en combineren, controle op geschiktheid van voertuig en chauffeur. Automatisch zijn volgens de leverancier o.a. EDI-voormelding bij de zeehavens, e-CMR, tijdstempels uit de truck-app, facturatie en inkoopcontrole. **Vendor-claim** ([Modality](https://www.modality.nl/?p=1673))
- **PortPro** (VS) stelt chauffeurs voor en laat de dispatcher alles aanpassen of vrijgeven. **Vendor-claim** ([PortPro](https://portpro.io/features/drayage-carrier/ai-dispatch-and-route-planner)). In hun casus (95 chauffeurs) zakt de dispatchtijd van ca. 5 minuten naar 15 seconden per load, zonder meetmethode. **Vendor-claim** ([PortPro casus](https://portpro.io/all-resources/case-studies/octs-boosts-cash-flow)). De winst lijkt uit communicatie, tracking en administratie te komen. **Schatting**
- **TVM Greenpaper Planner** (april 2026, sectorwhitepaper, geen peer review): planningen worden in 2026 bij veel organisaties "grotendeels automatisch gegenereerd" en de bottleneck verschuift naar uitzonderingen. In het MKB zit AI vaak als losse module bovenop Excel. "De planner blijft in the loop." Advies: begin klein ([TVM](https://www.tvm.nl/sites/default/files/2026-04/TVM_Greenpaper_Planner_A4_online.pdf)).
- **DrayFLEX** is de enige gevonden onafhankelijke evaluatie van een drayage-optimalisatietool (VS, $ 6 miljoen). Het pilotbedrijf nam de tool nooit volledig in gebruik. Tegenstrijdige aanbevelingen zorgden voor twijfel en de resultaten zijn gesimuleerd. De sector was volgens de rapportage "not ready for this level of optimization" ([DrayFLEX](https://ops-dr.fhwa.dot.gov/fastact/atcmtd/fy16awards/6065-218-ATCMTD_2025_DrayFLEX_Final_Report.pdf)). **Bevestigd**
- **TNO Talking Trucks** (ca. 9 trucks, 40 orders): alle orders op tijd, planners ca. 95%. Koppelen met bestaande ordersystemen kostte meer tijd dan verwacht ([TNO](https://publications.tno.nl/publication/34639406/BPCLln/TNO-2022-R10252.pdf)). **Bevestigd**, maar klein en niet tijdens uitvoering getest.
- **Cijfers**: Modality's binnenvaart-tool plant "80 tot 90%" automatisch (**Vendor-claim**, geen wegtransport, [Modality](https://www.modality.nl/en/blog-en/automated-barge-planning/)). Eén drayage-bedrijf reed in een proef van 2017 14% minder kilometers ([ITS](https://www.itskrs.its.dot.gov/2018-b01299)). Gebruik geen van deze getallen als belofte.

### C.4 Wat realistisch is en wat niet (Schatting)

**Realistisch in ca. een jaar, in deeltijd:**
- Planbord met controles, logboek en regels als data.
- Orders uit e-mail of PDF inlezen, met controle door een mens.
- Status en tijden uit een simpele app en/of telematica.
- Concept-facturen uit vaste tarieven.
- Meldingen aan Portbase, eerst met akkoord, later automatisch voor standaardritten.
- Planvoorstellen voor standaard containers, eerst in schaduwmodus.

**Niet realistisch:**
- Alles in drie maanden.
- Plannen zonder mens (niveau 4).
- Tank en ADR automatisch toewijzen.
- Koppelingen met rederij-API's: toegang voor een klein bedrijf is niet vast te stellen (F.3).
- Een slot "pakken". ECT bepaalt het slot en geeft bij een vol slot het volgende vrije.
- Wettelijke naleving beloven. De tachograaf is de waarheid, jij voorspelt (hoofdstuk 13.5 punt 8).
- Een besparingspercentage beloven.

---

## D. Hoe automatisch plannen werkt

### D.1 Het soort probleem

Wetenschappers noemen dit een "full-truckload pickup and delivery problem with time windows". In gewone taal: elke rit is één volle of lege container die binnen een tijdvenster van A naar B moet. Trekker, chassis en chauffeur zijn de middelen die je eraan koppelt. Lege containers en street turns (een lege container direct hergebruiken) horen in dezelfde berekening, dat is "significant" beter ([Braekers](https://documentserver.uhasselt.be/bitstream/1942/14547/1/PhD%20Kris%20Braekers%20-%20Final%20version.pdf)). **Bevestigd**, maar alleen de inhoudsopgave van dit proefschrift is gelezen.

Hoe groot kan het? Exacte methoden (wiskundige modellen die het bewezen beste plan zoeken) halen in papers ongeveer 25 - 200 klanten. Bij 80 taken vond CPLEX geen toelaatbare oplossing, hun heuristiek (slim zoeken zonder garantie op het beste) wel ([Zhang, Huang & Wang](https://hub.hku.hk/bitstream/10722/287150/1/content.pdf)). Heuristieken halen meer dan 1.000 verzoeken ([Xue e.a.](https://arxiv.org/pdf/2012.06538.pdf)). **Bevestigd.**

Een bedrijf met 20 - 200 ritten per dag heeft ruwweg 40 - 800 stops. Dat valt in de klasse waar heuristieken in seconden tot minuten bruikbare plannen geven. **Schatting.** Een rekentijd op een echte drayage-instantie van 5 - 50 trekkers is niet gevonden (**Open**), en er is geen open benchmark voor Rotterdamse drayage.

Een eerlijke kanttekening: bij 3 tot 5 trekkers is het plan zo klein dat een solver weinig toevoegt boven een goede planner. De winst zit dan in snelheid en controle. **Schatting.** Controleer dat tijdens het meekijken (Q).

### D.2 Welke solver? Let op de status

| Solver | Taal en licentie | Status en let op | Voor een beginner? |
|---|---|---|---|
| **OR-Tools** (Google) | Python, kern C++. Apache 2.0 | Pickup-delivery, tijdvensters en "laat deze order vallen met straf" zijn gedocumenteerd ([PD](https://developers.google.com/optimization/routing/pickup_delivery), [tijdvensters](https://developers.google.com/optimization/routing/vrptw), [straffen](https://developers.google.com/optimization/routing/penalties)). Docs alleen met harde tijdvensters. Bevriezen en warm starten niet onderzocht. Releasedatum niet bevestigd | Ja. Mijn eerste keus |
| **PyVRP** | Python, kern C++. MIT | Sterke kwaliteit volgens eigen paper en docs ([paper](https://arxiv.org/html/2403.13795v2)), maar de auteurs zijn belanghebbend. De README noemt pickup-and-delivery, de pagina "Why PyVRP" zet het op "niet ondersteund" ([README](https://raw.githubusercontent.com/PyVRP/PyVRP/main/README.md), [Why PyVRP](https://pyvrp.org/setup/why_pyvrp.html)). **Open** welke klopt. Pauzeplanning volgens EU-regels en compatibiliteitsregels alleen in de betaalde Enterprise-versie (prijs niet gevonden) | Tweede keus |
| **Timefold** | Java en Kotlin. Community Apache 2.0 | De officiële Python-versie is op 6 oktober 2025 gearchiveerd ([GitHub](https://github.com/TimefoldAI/timefold-solver-python)). De fork SolverForge is beta met één maintainer ([PyPI](https://pypi.org/project/solverforge-legacy/)). Wel sterk: bevriezen van stops en uitleg per regel ([modelleren](https://docs.timefold.ai/timefold-solver/latest/domain-modeling/modeling-planning-problems), [score](https://docs.timefold.ai/timefold-solver/latest/constraints-and-score/score-calculation)). Score-analyse is commercieel. Platform: Free € 0, Pro € 329 per maand, Enterprise vanaf € 6.000 per jaar ([prijzen](https://timefold.ai/pricing)) | Alleen als je een derde taal accepteert |
| **VROOM** | C++. BSD-2 | Ondersteunt shipments, skills en breaks ([GitHub](https://github.com/VROOM-Project/vroom)) | Niet nodig |

Status-uitspraken zijn **Bevestigd** op de aangegeven pagina's, releasedata **Open**. Gurobi en Hexaly zijn op offerte en niet nodig. Reinforcement learning is onderzoek, geen bewezen route voor een klein bedrijf (binnen een terminal ca. 6% slechter dan goede local search, [Nottingham](https://people.cs.nott.ac.uk/pszrq/files/EJOR23PortDRL.pdf)).

### D.3 Reistijden: zelf hosten of betalen?

| Optie | Vrachtwagenregels | Kosten | Let op |
|---|---|---|---|
| OSRM (zelf hosten) | De gelezen pagina noemt alleen een autoprofiel ([GitHub](https://github.com/Project-OSRM/osrm-backend)). Niet gelezen is niet hetzelfde als "bestaat niet" | Gratis software, wel een server | Graafbouw van 550 MB duurde ca. 30 min (voorbeeld Mexico) |
| Valhalla (zelf hosten) | Truckprofiel met hoogte, breedte, lengte, gewicht, aslast en hazmat ([docs](https://valhalla.github.io/valhalla/api/route/api-reference/)) | Gratis | Matrix-endpoint niet gelezen |
| openrouteservice (zelf hosten) | Profiel `driving-hgv` met dezelfde soort eisen ([docs](https://giscience.github.io/openrouteservice/api-reference/endpoints/directions/routing-options)) | Gratis. Licentie GPL/LGPL | Lees de licentie bij doorverkoop |
| TomTom | Truck en ADR-tunnelcodes ([docs](https://docs.tomtom.com/routing-api/documentation/tomtom-maps/calculate-route)) | 20.000 routes en 2.500 matrix-verzoeken per maand gratis ([prijzen](https://docs.tomtom.com/pricing)) | Prijs daarna niet gelezen |
| Google Routes | Truckroutering alleen in de VS beschikbaar. Nederland niet genoemd ([Google](https://developers.google.com/maps/documentation/routes/lvr)) | Essentials $ 5 per 1.000 (10.000 gratis). Pro $ 10 met verkeer (5.000 gratis) ([prijzen](https://developers.google.com/maps/billing-and-pricing/pricing)) | Matrix per element gefactureerd |

GraphHopper kost € 69 - 479 per maand met maximaal 30 - 200 locaties per verzoek, te krap bij veel trekkers ([prijzen](https://www.graphhopper.com/pricing/)). HERE kon niet worden opgehaald (**Open**).

Rekenvoorbeeld (**Schatting**): een verse matrix van 600 locaties heeft 600 x 600 = 360.000 elementen. Bij Google kost dat ca. $ 1.500, als je per element betaalt (controleer dit vooraf). Daarom: zelf hosten, of een tabel met vaste reistijden voor terminals, depots en vaste klanten die de planner kan corrigeren. Een ETA-berekening met verkeer is goedkoper: 30.000 verzoeken per maand op Essentials kost ca. $ 100 ((30.000 - 10.000) x $ 5 / 1.000).

### D.4 Harde en zachte regels en de doelfunctie

| Soort | Voorbeelden |
|---|---|
| **Hard** | Slot of tijdvenster. Cut-off. Chassis past bij container. Gewicht. ADR- en tankbevoegdheid. Rij- en rusttijden. Chauffeur en materieel beschikbaar. Geldige release |
| **Zacht** (kost straf) | Last free day (straf per dag). Voorkeurstijden van de klant. Wachttijd. Eerlijke verdeling. Zelfde chauffeur bij een vervolgrit |
| **Niet te plannen** | Een order die niet past krijgt een "ongepland"-straf. Zo crasht de solver niet en krijgt de planner een lijst "kan niet" |

De doelfunctie (**Schatting**, mijn voorstel): (1) zoveel mogelijk orders gepland en op tijd, met een zeer hoge straf op een order die vervalt of te laat is. (2) Zo laag mogelijke kosten: rijtijd, lege kilometers en wachttijd. (3) Tie-breakers: eerlijke verdeling en continuïteit. In de literatuur wegen vaste kosten per voertuig zwaar (400 : 1 tegen werktijd, [Zhang e.a.](https://hub.hku.hk/bitstream/10722/287150/1/content.pdf)). Met een vaste vloot valt dat weg.

Stop rij- en rusttijden in versie 1 niet volledig in de solver. Beter: de solver rekent met een benaderde limiet (9 uur rijden, 45 minuten pauze na 4,5 uur als vaste blokken) en een aparte controle toetst daarna volgens Verordening 561/2006 ([EC](https://transport.ec.europa.eu/transport-modes/road/social-provisions/driving-time-and-rest-periods_en)). Goel (2010) toont dat volledige controle voor een gegeven route kan ([Goel](https://econpapers.repec.org/RePEc:inm:ortrsc:v:44:y:2010:i:4:p:429-441)). **Bevestigd**, alleen de samenvatting gelezen. De gratis PyVRP heeft dit niet.

Begin met trekker en chassis als één eenheid en ontkoppel ze later (de wetenschap behandelt ze als aparte middelen). **Schatting.**

### D.5 Herplannen en stabiel houden

Drie lagen van vastheid per rit (**Schatting**, mijn ontwerp):

1. **Gestart.** De chauffeur is onderweg of heeft de container. Bevroren.
2. **Toegezegd.** Aan chauffeur, trekker en tijd gekoppeld en doorgegeven. De solver mag dit niet verschuiven tot de planner het vrijgeeft.
3. **Open.** De solver mag vrij schuiven.

Timefold heeft hiervoor `@PlanningPin` en `@PlanningPinToIndex` ([docs](https://docs.timefold.ai/timefold-solver/latest/domain-modeling/modeling-planning-problems)) en kan warm starten na een wijziging ([docs](https://docs.timefold.ai/timefold-solver/latest/responding-to-change/real-time-planning)). **Bevestigd.** Of OR-Tools dit ook kan, is niet onderzocht (**Open**).

Regels voor herplannen (**Schatting**):
- Herplannen als **voorstel**. Alleen automatisch doorvoeren binnen een kleine limiet, zoals een ETA doorgeven aan de terminal.
- Periodiek herberekenen (elke 5 - 15 minuten) plus bij een gebeurtenis, zoals een spoedorder of uitval. Modality's binnenvaart-tool rekent elke 15 minuten en legt geaccepteerde containers vast (**Vendor-claim**, [Modality](https://www.modality.nl/en/blog-en/automated-barge-planning/)).
- Nooit elke 10 minuten een nieuw rooster naar chauffeurs sturen. Conflicterende aanbevelingen kostten bij DrayFLEX vertrouwen ([DrayFLEX](https://ops-dr.fhwa.dot.gov/fastact/atcmtd/fy16awards/6065-218-ATCMTD_2025_DrayFLEX_Final_Report.pdf)).

### D.6 Uitleg per voorstel

Elk voorstel krijgt een korte uitleg: waarom deze chauffeur, welke regels zijn getoetst, hoe zeker is de schatting. Een eenvoudige geschreven uitleg gaf in een lab-studie het meeste begrip en vertrouwen, beter dan een flowchart of tabellen ([CMS Conferences](https://openaccess.cms-conferences.org/publications/book/978-1-958651-09-4/article/978-1-958651-09-4_1)). **Bevestigd**, alleen de samenvatting. Uitleg is geen bewijs van juistheid (L.3). Een voorbeeld staat in L.4. Timefold levert uitleg per regel mee. Bij OR-Tools bouw je de uitleg zelf uit de controle. **Schatting.**

### D.7 Wat taalmodellen (zoals Claude) wel en niet kunnen

| Wel | Niet |
|---|---|
| Orders uit e-mail en PDF lezen en omzetten naar velden (E) | Zelf plannen en rekenen |
| Een uitkomst van de solver in gewone taal uitleggen, met cijfers die de solver aanlevert | Zelf rij- en rusttijden of gewicht uitrekenen en daarop vertrouwen |
| Helpen bij het schrijven en testen van de code (door jou, niet tijdens het draaien) | Een feasibility-garantie geven. Dezelfde invoer geeft niet altijd dezelfde uitvoer |

Studies: GPT-4 haalde bij routeproblemen zonder solver 56% geldige oplossingen (met zelfcontrole ca. 72%), en zakte sterk bij meer voertuigen en steden ([From Words to Routes](https://arxiv.org/html/2403.10795v1)). Een overzicht uit 2026: directe routegeneratie wordt snel slechter (geen geldige routes bij 500 klanten). De betrouwbaarste systemen koppelen het taalmodel aan een solver of controle ([overzicht](https://arxiv.org/pdf/2607.00604)). Taalmodellen "cannot, by themselves, do planning or self-verification" ([Kambhampati e.a.](https://arxiv.org/abs/2402.01817)). **Bevestigd.** De benchmarks gebruiken oudere modellen, nieuwere scoren beter. De richting is stabiel: **de solver beslist, een vaste controle bewaakt de harde regels, het taalmodel leest en legt uit.** Dit geldt ook voor mij.

---

## E. Orders automatisch inlezen

### E.1 Hoe orders binnenkomen

Grote klanten (Maersk, MSC, DHL, Kuehne+Nagel) hebben eigen EDI-koppelingen en data moet vaak handmatig worden aangevuld. Modality noemt EDI of een API de voorkeur. Het omzetten van PDF, Excel en tekst-orders is volgens Modality zelf "more error-sensitive and unstable" en een gescand document kan verkeerd gelezen worden ([Modality](https://www.modality.nl/en/blog-en/automating-order-processing/), [Modality AI](https://www.modality.nl/en/blog-en/practical-ai-applications-container-logistics/)). **Vendor-claim.** Hoe orders bij dit bedrijf binnenkomen is **Open** (deel 2: telefoon, e-mail of formulier is een schatting). Meet eerst per kanaal. Telefoon en WhatsApp zijn niet onderzocht.

### E.2 De route in zes stappen (Schatting, mijn ontwerp)

1. **Ontvangen.** E-mail of upload komt in een wachtrij. Elke order krijgt een concept-status.
2. **Lezen.** Een taalmodel of document-AI zet de tekst om naar velden in een vast schema (JSON). De Claude API kan afdwingen dat de uitvoer altijd geldig JSON is volgens het schema. Dat garandeert de **vorm**, niet de **inhoud** ([Claude API](https://platform.claude.com/docs/en/build-with-claude/structured-outputs)). **Bevestigd.**
3. **Harde controles** (vaste code, geen taalmodel).
4. **Beslisregel.** Mens kijkt verplicht als een controle faalt, een veld ontbreekt, twee leespogingen verschillen, de afzender of opmaak nieuw is, of een bestaande order wordt gewijzigd.
5. **Reviewscherm.** Planner controleert, past aan, keurt goed. Dashdoc doet dit ook zo (**Vendor-claim**, [Dashdoc](https://www.dashdoc.com/en/blog/pdf-to-transport-orders-ai)).
6. **Order.** Pas daarna bestaat de order. Alle stappen komen in het logboek.

| Controle | Hoe |
|---|---|
| Containernummer | 3 letters eigenaar, 1 letter categorie, 6 cijfers, 1 controlecijfer (mod 11). Voorbeeld CSQU3054383 geeft controlecijfer 3. Dit is zelf met Python getest op deze beschrijving ([Wikipedia](https://en.wikipedia.org/wiki/ISO_6346)) |
| Maat en type | 20 of 40 ft past bij de type-code |
| Terminalcode | Uit een vaste lijst (Portbase Reference Data) |
| Datum en tijd | Niet in het verleden. Past bij een pre-notificatie (F.2) |
| Verplichte velden | Klantreferentie, boeking of B/L, locaties. Een lege container zonder nummer mag alleen waar de terminal "loading on size type" ondersteunt ([Portbase](https://hcn.pcs.portbase.com/api-documentation/connection_instructions.html)) |
| Dubbele order | Zelfde referentie al aanwezig |

### E.3 Wat de markt claimt, en wat niet bewezen is

| Wie | Claim | Status |
|---|---|---|
| Modality AI-OCR | PDF naar JSON naar boeking. In uitrolfase. Geen nauwkeurigheid genoemd | **Vendor-claim** |
| Rail-Flow | 95% van de orders automatisch, 2 uur naar 30 minuten per dag. Vloeistoflogistiek, 10 klant-templates ([Rail-Flow](https://rail-flow.com/case-studies/staalduinen-logistics)) | **Vendor-claim** |
| C.H. Robinson | Orders van vier uur naar minder dan 90 seconden. Mensen beoordelen ongebruikelijke gevallen ([NAM](https://nam.org/?p=38531)) | **Vendor-claim** |
| Klippa | "Bijna 100%" met menselijke validatie ([Klippa](https://klippa.com/en/dochorizon)) | **Vendor-claim** |

**Open:** er is geen onafhankelijk nauwkeurigheidscijfer gevonden voor het lezen van transportorders, laat staan voor Nederlandse e-mails met terminalverwijzingen. Azure legt uit wat een confidence-score is (0,95 betekent ongeveer 19 van 20 goed) en noemt zelf geen drempel voor automatisch accepteren ([Microsoft](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/concept/accuracy-confidence)). Elke drempel moet je dus op eigen documenten testen. De 95% van Rail-Flow geldt bij vaste templates. Een bedrijf met wisselende afzenders haalt waarschijnlijk minder zonder review. **Schatting.**

Kosten: Google Document AI Custom Extractor $ 30 per 1.000 pagina's, gewone OCR $ 1,50 ([Google](https://cloud.google.com/document-ai/pricing)). Bij 1.000 pagina's per maand is dat ca. $ 30. **Bevestigd** (prijs), de pagina's per order is mijn aanname. Prijzen voor taalmodel-API's zijn niet onderzocht (**Open**).

---

## F. Portbase en terminals automatisch

Wat Portbase, pre-notificatie en slots zijn, staat in hoofdstuk 7.2 en 7.5. Hier staat alleen wat nieuw is voor automatisering.

### F.1 HCN Road-API: aansluiten, kosten, wat het kan

**Aansluiten (klein bedrijf, direct).** Je hebt een EAN-nummer en een iAMconnected-account nodig. Dan: (1) aansluitformulier invullen, tekenen en opsturen. Alleen de klant doet dit, niet de softwarebouwer. (2) Client ID en secret van Portbase Integration Services. (3) Bouwen en valideren met testscenario's. (4) Testen in de testomgeving. (5) Na een goede test koppelt Integration Services je aan productie ([Portbase API](https://hcn.pcs.portbase.com/api-documentation/connection_instructions.html), [Portbase Support](https://support.portbase.com/hc/en-gb/articles/29950155564562), [HCN Road](https://www.portbase.com/en/services/hinterland-container-notification-road/)). **Bevestigd.** Een certificeringseis is niet gevonden.

**Techniek.** JSON. Drie soorten API's: Operator, Tracking en Reference Data. De Tracking-API werkt met long polling: jij luistert naar antwoorden, er is geen openstaande poort nodig. Je bevestigt verwerking met "Update position" en kunt zo updates opnieuw afspelen. `refdata/getTerminal` toont wat een terminal ondersteunt. **Bevestigd.** De poller moet netjes bevestigen en dubbele berichten aankunnen. **Schatting.**

**Kosten** (Portbase, [HCN Road](https://www.portbase.com/en/services/hinterland-container-notification-road/), [kosten](https://www.portbase.com/en/programs/hinterland/costs/)): € 249,50 eenmalig. € 11,36 per maand + € 0,40 per pre-notificatie van een volle container. Per 1-1-2027: € 11,70 en € 0,41. Gratis: statusverzoeken, bijwerken van pre-notificaties, lege containers. Gemiddeld 1,1 pre-notificatie per volle container. Voorbeeld (**Schatting**): 500 volle containers per maand is ca. € 231 per maand, zonder terminaltarieven. Dat betaalt een bedrijf met HCN Road waarschijnlijk ook zonder API. Het volume van dit bedrijf is **Open**.

**Wat het kan:** pre-notificatie van visit en cargo, status opvragen, realtime updates, ETA aanpassen, pre-notificatie wijzigen of annuleren (behalve waar terminals dat niet toestaan), en bij sommige terminals een slot aanvragen ([HCN Road](https://www.portbase.com/en/services/hinterland-container-notification-road/), [Portbase Support](https://support.portbase.com/en/services/road-planning-system-interface/)). Afwijzingscodes COR (rederij niet vrijgegeven), CDM (douanedocument ontbreekt) en BLT (terminal blokkeert) komen uit een pagina van 2020: controleer ze in de actuele API.

**Wat de service niet belooft:** Portbase levert een inspanningsverplichting (99,8% beschikbaarheidsdoel) en sluit aansprakelijkheid uit voor o.a. storingen en onjuiste informatie. Het document is van 11/2022 en "tijdelijk" ([Portbase](https://www.portbase.com/wp-content/uploads/2022/11/2022.11-EN-Service-Levels-HCN-vervoerders.pdf)). **Bevestigd.**

### F.2 Tijdsloten: geen slot-API, het slot volgt uit de ETA

Bij ECT Delta en Euromax kun je een slot niet los boeken. Je stuurt een pre-notificatie met een gewenste ETA. ECT koppelt die aan het eerste vrije slot, en bij een vol slot aan het volgende ([ECT](https://www.ect.nl/en/news/news-feed/ect-introduces-truck-capacity-management-system)). ECT biedt wel betaalde Premium Plus-API's (zie F.3) maar geen slot-API ([ECT](https://myterminal.ect.nl/premium-plus)). **Bevestigd.** "Slots automatisch boeken" is dus: pre-notificaties met ETA automatisch versturen en bijwerken.

**Stand 23 november 2026** (correctie op oudere berichten): TCMS draait sinds 5 - 7 oktober 2026 bij ECT Delta en Euromax, niet bij Delta II ([ECT](https://www.ect.nl/en/news/news-feed/go-live-truck-capacity-management-system)). Vanaf 25 november zijn de slots 2 uur met 30 minuten tolerantie. De € 100 voor no-show en te vroeg komen bestaan, maar worden voorlopig niet geheven. Er is geen einddatum van die vrijstelling genoemd. ECT meldt nog een "substantieel percentage no-shows" ([ECT 18 nov](https://www.ect.nl/en/news/news-feed/update-truck-capacity-management-system-hutchison-ports-ect-rotterdam)). **Bevestigd.**

**Regels voor je software** (feiten uit [ECT 18 nov](https://www.ect.nl/en/news/news-feed/update-truck-capacity-management-system-hutchison-ports-ect-rotterdam), [ECT FAQ](https://myterminal.ect.nl/help-center/truck-capacity/english), [ECT geldigheid](https://myterminal.ect.nl/news/period-validity-pre-announced-truck-visits-ect-terminals), [Portbase kosten](https://www.portbase.com/en/programs/hinterland/costs/); de conclusies zijn **Schatting**):

- **Reken terug vanaf het slotvenster.** Slot van 2 uur plus 30 minuten tolerantie aan beide kanten is een venster van ca. 3 uur. Plan niet op één vaste tijd.
- **Annuleren of wijzigen kan tot slotbegin.** Daarna is het een no-show. Bouw een alarm vóór slotbegin en laat een mens annuleren kort voor slotbegin.
- **ETA-wijziging:** minimaal 1 minuut verschil. Valt de nieuwe ETA in hetzelfde slot, dan blijft het slot. Na aanmaken of wijzigen heb je 30 minuten om te corrigeren.
- **ECT Delta en Euromax laten geen wijziging van HCN Road-pre-notificaties toe.** De omweg is annuleren, aanpassen en opnieuw sturen met behoud van het label (één betaling). Een fout hierin raakt direct het slot. Ook een gewijzigd containernummer na de melding kan het slot kosten (een update zonder slotverlies is gepland voor begin 2027). Vang het af vóór je meldt.
- **Geen "claim en annuleer".** ECT heeft een fix tegen vervoerders die herhaaldelijk met dezelfde ETA melden om vrijgekomen slots te pakken. Andere sancties zijn niet beschreven. Een verbod in de voorwaarden is **Open**.
- **Wie betaalt:** no-showkosten gaan naar de partij die de pre-notificatie deed, truck charges en early-arrival naar de uitvoerende partij. Je meldt maximaal 6 dagen vooruit.
- **ECT kan TCMS opschorten** (terug naar first-in-first-out). Bouw een terugvalmodus.
- **Terminals verschillen.** APMT Maasvlakte II werkt met TAR-codes en 30-minuten-slots met 45 minuten tolerantie (FAQ ongedateerd, [APMT](https://www.apmterminals.com/en/maasvlakte/practical-information/faq)). RWG rekent € 25,80 piektoeslag per slot, ook bij een niet-gebruikt slot ([RWG](https://www.rwg.nl/en/faq-time-slot-surcharge-during-peak-hours)). Slotlengte RWG en regels Delta II zijn **Open**. Bouw een laag per terminal met eigen regels en tarieven.

### F.3 Release, Secure Chain en rederijen

- **Digitale release** vervangt de pincode voor import in Rotterdam. De opdrachtgever machtigt de transporteur en de toestemming verschijnt als voorlopige pre-notificatie die jij afrondt. Het veld "Executing Charter" moet kloppen, anders heeft de uitvoerder geen toegang ([Portbase](https://www.portbase.com/en/programs/secure-chain/inland-operators/)). **Bevestigd.** Voor een trucker is HCN Road dus de praktische bron van release-informatie. **Schatting.**
- **Cargo Release Manager** is gratis, maar alleen via webschermen ([Portbase](https://www.portbase.com/en/services/cargo-release-manager/)).
- **Cargo Controller Import** (REST en webhooks met release, douane en lossing): € 249,50 eenmalig, € 79,57 per maand + € 0,44 per B/L ([Portbase](https://portbase.com/en/services/cargo-controller), [API](https://support.portbase.com/hc/en-gb/articles/32493593538450)). Het is gebouwd rond B/L-nummers, die een trucker meestal niet heeft. Of een transporteur rechtstreeks toegang krijgt, is **Open**.
- **ECT Import Container Status-API:** € 445 per maand (tot 1.000 containers, € 50 extra voor verwachte lostijd). Vereist een Premium Plus-contract. Documentatie "coming soon" ([ECT](https://myterminal.ect.nl/api-products/import-container-status)). Release- en douanevelden worden niet genoemd.
- **Rederijen:** DCSA-standaarden zijn openbaar ([DCSA](https://dcsa.org/standards/track-and-trace/standard-documentation-track-and-trace)). Maersk en Hapag-Lloyd hebben API's, onder meer voor demurrage en detention ([Maersk](https://www.maersk.com/digital-services/data-integrations/solutions), [Hapag-Lloyd](https://ams.hapag-lloyd.com/pt/services-information/data-solutions/api-portal.html)). Of een kleine transporteur zonder commerciële relatie toegang, voorwaarden en prijs krijgt, is niet vastgesteld (**Open**). De Maersk-developerportal was niet leesbaar.
- **Last free day:** in de gelezen bronnen heeft Portbase geen LFD-veld. Laat de klant de LFD in de order invullen en bewaak die automatisch. **Schatting.**

### F.4 Wat niet vast te stellen was

De volledige API-specificatie, endpoint-URL's, rate limits en auth-header (de developer portal was niet bereikbaar). De doorlooptijd van een nieuwe HCN Road-aansluiting. Een eventueel minimumvolume. Een verbod op slot hoarding in de voorwaarden. De datum waarop de € 100 gaat gelden. **Open.** De "12 weken" (4 - 8 met een bekende leverancier) in de bronnen gaat over de Cargo Controller Import-API, niet over HCN Road ([Portbase](https://www.portbase.com/en/?p=31339)).

---

## G. Statusvolging, app, telematica, berichten en facturen

### G.1 Statusvolging

Status komt uit drie bronnen: knoppen van de chauffeur, een geofence of telematica, en antwoorden van Portbase en de terminal. De statusflow staat in hoofdstuk 13.3. Dit is het onderdeel met het hoogste veilige niveau (C.2), omdat er alleen iets vastgelegd wordt. Houd "geleverd" bij de chauffeur: een geofence zegt dat een truck ergens was, niet dat de lading is afgeleverd. **Schatting.**

### G.2 Chauffeurs-app of PWA

Een PWA is goedkoper dan een native app. Beperkingen op iOS ([Firt](https://firt.dev/notes/pwa-ios/)): Web Push werkt alleen als de app op het beginscherm staat (sinds iOS 16.4). Service workers en IndexedDB worden ondersteund, dus knoppen, foto's en handtekening kunnen offline werken. Background Sync, Periodic Background Sync en Background Fetch worden niet ondersteund. De geïnstalleerde app deelt geen opslag met Safari. **Bevestigd.** Over GPS op de achtergrond zegt de bron niets (**Open**). Dus: versie 1 zonder achtergrond-GPS. Wil het bedrijf continu volgen, dan is telematica van de trekkers of een native app realistischer. **Schatting.**

### G.3 Telematica, geofencing, ETA en tachograaf

- **Webfleet** (.connect API): positie, geofencing, ETA, resterende rijtijd, werkorders. Prijs alleen op aanvraag ([Webfleet](https://www.webfleet.com/en_gb/webfleet/partners/integration)). **Vendor-claim.**
- **Geofence bij poorten** kan aankomst, vertrek en wachttijd meten. Er is geen bron over de nauwkeurigheid bij terminalpoorten (**Open**). Test de straal en wat "aankomst" is (poort of stack) in een pilot. **Schatting.**
- **ETA met verkeer:** Google Routes Pro (D.3), of een eigen tabel met vaste reistijden.
- **Tachograaf:** de werkgever moet de voertuigunit minstens elke 90 dagen en de bestuurderskaart minstens elke 28 dagen downloaden en de data minstens 1 jaar bewaren ([Business.gov.nl](https://business.gov.nl/regulation/digital-tachograph)). Webfleet biedt automatische downloads ([Webfleet](https://www.webfleet.com/en_gb/webfleet/blog/the-importance-of-tachograph-downloads-and-how-to-make-them-easier/)). **Bevestigd.** Een rijtijdsaldo in jouw systeem vraagt een koppeling of handmatige invoer. **Schatting.**

### G.4 Berichten naar chauffeurs en klanten

WhatsApp Business rekent sinds 1 juli 2025 per afgeleverd bericht, per categorie en land. Buiten het 24-uursvenster mag je alleen goedgekeurde templates sturen. Sinds 1 oktober 2026 kosten service-berichten boven 1.000 per nummer per maand en utility-berichten binnen een open venster geld ([Meta](https://developers.facebook.com/documentation/business-messaging/whatsapp/pricing)). **Bevestigd.** De Nederlandse tarieven zijn niet gelezen (**Open**). Start met push in de PWA of e-mail of sms (niet onderzocht) en gebruik WhatsApp pas als chauffeurs dat nodig hebben. **Schatting.**

### G.5 Facturatie en boekhouding

Ritdata naar factuur kan automatisch, mits de tarieven vastliggen: tarief, dieseltoeslag, wachturen, terminalheffing. Pas alleen toe wat contractueel is afgesproken. Bewaar per rit het bewijs (wachttijd uit geofence, POD). **Schatting.** Modality doet dit met tarieven, EDI-export en inkoopcontrole (**Vendor-claim**, [Modality](https://www.modality.nl/?p=1673)).

Koppelen:
- **Moneybird:** open API, token of OAuth, 150 verzoeken per 5 minuten per IP, sandbox, webhooks aanbevolen ([Moneybird](https://developer.moneybird.com/introduction)). **Bevestigd.**
- **Exact Online:** app registreren en laten goedkeuren (kan weken duren), 60 aanroepen per minuut en 5.000 per dag ([Apideck-blog](https://dev.to/apideck/the-complete-guide-to-exact-online-api-integration-in-2026-529c)). Een blog van een aanbieder, geen primaire documentatie: **Open.** Welk pakket het bedrijf gebruikt weten we niet.

### G.6 E-factuur, e-CMR en eFTI

**Correctie op een aanname:** een verplichte e-factuur voor bedrijven, ook binnenlands, is pas voorgesteld: start 1 juli 2030, rapportage 1 juli 2031, geen verplichting in 2026 of 2027. Het is nog geen wet. KOR-ondernemers zijn vrijgesteld ([Rijksoverheid](https://www.rijksoverheid.nl/actueel/nieuws/2026/09/11/kabinet-kiest-voor-invoering-e-facturatie-en-rapportage-voor-bedrijven)). Ook EDICOM noemt de tijdlijn een voorstel ([EDICOM](https://edicomgroup.com/blog/netherlands-electronic-invoicing-digital-reporting)). **Bevestigd.** Peppol of UBL-uitvoer is wel een verstandige voorbereiding. **Schatting.**

**eFTI:** vanaf 9 juli 2027 moeten autoriteiten informatie accepteren die bedrijven via gecertificeerde eFTI-platforms delen. De pagina noemt geen verplichting voor vervoerders ([EC](https://transport.ec.europa.eu/transport-themes/logistics-and-multimodal-transport/efti-regulation_en)). **Bevestigd.** Kies een e-CMR- of POD-leverancier die eFTI-gecertificeerd wil worden. Een eigen eFTI-platform bouwen is niet realistisch (certificering). **Schatting.** E-CMR wordt in Nederland al nationaal gebruikt. Dat staat in een secundaire bron van oktober 2025 ([Trans.info](https://trans.info/en/ecmr-in-2026-434860)). Kosten per document en ratificatiestatus zijn **Open**.

---

## H. Data: wat heb je nodig en wat ontbreekt?

**Drie lagen** (**Schatting**, mijn indeling):
1. **Harde feiten** die vooraf juist moeten zijn: containernummer en type, gewicht, release, terminal en slot, openingstijden, retourdepot, chassis- en trekkergegevens, ADR en code 95 van de chauffeur. Zie hoofdstuk 13.2.
2. **Schattingen die je kunt laten leren:** rijtijd per route en tijdstip, laad- en lostijd per klant, wachttijd per terminal per uur.
3. **Commerciële data:** tarieven, toeslagen, kostprijs per uur, demurrage- en detentionrisico per rederij.

**Koude start.** Een nieuw systeem heeft geen historie. Begin met standaardtijden van de planner met ruime marge. Log vanaf dag 1 echte tijden per stop (aankomst en vertrek). Gebruik later de mediaan en de P80 of P90 (de tijd waar 80 of 90% van de ritten onder blijft) per locatie en dagdeel. Pas daarna ML. Een bron voor het aantal benodigde metingen is niet gevonden. Mijn vuistregel (geen bronfeit): enkele tientallen per locatie en dagdeel. **Open.**

**Wachttijden zelf meten.** Je kunt terminalwachtrijen niet meten, wel je eigen aankomst en vertrek per bezoek. Dat is de goedkoopste en waardevolste dataset. TNO kwam in een bargecasus tot dezelfde conclusie: aankomst- en vertrektijden bij de terminal ontbraken en de data zat verspreid over Excel, WhatsApp en Portbase ([TNO](https://publications.tno.nl/publication/34637555/6xbWgu/TNO-2020-R11865.pdf)). **Bevestigd.** Bewaar bij elke meting de context (datum, terminal, storing). De haven noemt 2025 verstoord en verwacht vanaf 2027 minder wachttijd ([Port of Rotterdam](https://www.portofrotterdam.com/en/news-and-press-releases/between-growth-and-pressure-rotterdams-2025-container-year-under-review)). Een model dat op 2025 - 2026 leert, wordt dus mogelijk te pessimistisch. **Schatting.**

**Wat ontbreekt.** Geen Nederlandse benchmarks gevonden voor wachttijden, ritten per trekker per dag, bezettingsgraad of lege kilometers, en geen onafhankelijke voor-en-na-meting van planningssoftware in het MKB. Alleen een kostenijkpunt: € 66,84 per effectief uur en € 1,65 per km voor trekker + oplegger, prijspeil 2021 ([KiM](https://www.kimnet.nl/binaries/kimnet/documenten/notities/2023/03/30/kostenkengetallen-voor-het-goederenvervoer/Kostenkengetallen+voor+het+goederenvervoer_Wegvervoer.pdf)). **Open.** Rabobank en TVM: betrouwbare data is een voorwaarde en kleine bedrijven hebben vaak te weinig data voor eigen AI ([Rabobank](https://www.rabobank.nl/kennis/d011531409-nieuwe-mogelijkheden-met-ai-in-de-transport-en-logistiek), [TVM](https://www.ttm.nl/wp-content/uploads/2025/11/TVMSectorstudie2025A4HR.pdf)).

**Regels als aanpasbare data.** Zet elke regel in een tabel met "geldig van - tot" en een bron (hoofdstuk 13.5 punt 4). Planneropmerkingen als "laadt pas na 10:00" worden velden, geen vrije tekst. Rederijregels voor free time verschillen per rederij en contract, dus één vaste "LFD-regel" is fout. Maersk NL (vanaf 1 aug 2026) laat zien hoe de bedragen per dag oplopen ([Maersk](https://www.maersk.com/local-information/the-netherlands/import)). **Bevestigd** voor Maersk, andere rederijen niet gelezen.

---

## I. Bouwen of kopen?

### I.1 Wat er te koop is

| Pakket | Wat bekend is | Status |
|---|---|---|
| **Modality** (ICT) | TMS en TOS met koppelingen naar zeeterminals, rederijen, douane en Portbase. Orders via AI-OCR, EDI, API of klantportaal. Interactieve planning, truck-app, e-CMR, facturatie. Een Modality API bestaat. Prijs, klantaantal en doelgroepgrootte niet openbaar. Enige genoemde klant is een vendor-testimonial ([ICT](https://www.ict.eu/en/modality), [Modality](https://www.modality.nl/?p=1673)) | **Vendor-claim** |
| **Go4TMS** | Registratie en planning van containertransport, sinds 2010, op Business Central. Geen prijzen of details ([AntwerpXL](https://www.antwerpxl.com/exhibitors/go4logistics-196851/)) | **Vendor-claim** |
| **EasyTrans** | Vanaf $ 32,02 per gebruiker per maand. Vijf oude reviews. Geen containerfuncties genoemd ([Capterra](https://www.capterra.com/p/167861/EasyTrans/)) | **Bevestigd** (prijs), niet container-specifiek |
| **FiLogic** | Maandabonnement voor kleine vervoerders ([ABN AMRO](https://www.abnamro.nl/nl/zakelijk/insights/sectoren-en-trends/ondernemersverhalen/logistiek/tms-in-de-cloud-is-niet-eng-en-de-voordelen-zijn-groot.html)) | **Vendor-claim**, uit 2019 |

Algemene prijsindicaties zijn niet te gebruiken voor Modality. Een TMS-app voor logistiek kost € 40 - 50 per gebruiker per maand (0 reviews, [Capterra](https://www.capterra.com/p/10046514/TMS-for-Logistics-Service-Providers/)). Een concurrent-blog noemt eigen abonnementen van € 199 - 599 per maand en schattingen van € 6.000 tot € 300.000 per jaar voor anderen, geen offertes ([Cargoson](https://www.cargoson.com/nl/blog/transportmanagementsoftware-tms-prijs-kosten)). **Vendor-claim.** Reviews van MKB-transporteurs over de containerpakketten ontbreken, en niet gecontroleerd is of ze tank, ADR, kiepen en flexitank aankunnen (deel 2, hoofdstuk 24). **Open.**

### I.2 Eerlijke afweging

| | Kopen | Bouwen als laag eromheen | Zelf alles bouwen |
|---|---|---|---|
| Voordeel | De saaie, risicovolle delen zitten erin: voormelding, e-factuur, tarieven, app | Je leert het proces. Kleiner risico | Past precies op het bedrijf |
| Risico | Prijs onbekend. Overstap. Past tank en kiepwerk? | Alleen mogelijk als het pakket een API of export geeft | Jij draagt fouten, support, beveiliging en onderhoud. Bus factor 1 |
| Status | **Open** | **Schatting** | **Schatting** |

Risico's van maatwerk-IT: bij grote IT-projecten (boven $ 15 miljoen) vonden McKinsey en Oxford gemiddeld 45% boven budget en 56% minder waarde dan voorspeld. Niet direct vergelijkbaar met een klein project ([McKinsey](https://www.mckinsey.com/capabilities/operations/our-insights/delivering-large-scale-it-projects-on-time-on-budget-and-on-value)). Gall's law: een complex systeem van nul "never works", het groeit uit een eenvoudig werkend systeem ([Wikipedia](https://en.wikipedia.org/wiki/John_Gall_(author))). Een bedrijfskritisch systeem door één deeltijdbouwer met AI-hulp is een extra risico: support, beveiliging, continuïteit en aansprakelijkheid. **Schatting.**

### I.3 Mijn aanbeveling

**Bouw geen volledig TMS. Vraag eerst een offerte. Bouw daarna hooguit een laag eromheen of een klein planbord naast hun werkwijze.** Onderbouwing: de containerpakketten dekken al de delen waar een beginner het meest kan missen (Portbase-EDI, e-factuur, tarieven). Het eigen voordeel van maatwerk zit in de uitzonderingen van dit bedrijf (tank, kiepen, flexitank, eigen terrein), en juist daarvan is niet gecontroleerd of pakketten ze dekken. Een planbord met controles bouwt de kennis op die je bij elk scenario nodig hebt.

**Wat zou mijn aanbeveling veranderen?**
- Een offerte die laag is en tank, ADR, kiepen en flexitank dekt: dan **kopen**, en ik zou niets bouwen.
- Een pakket zonder API of export: een laag eromheen is dan niet mogelijk. Kopen, of een los klein hulpmiddel.
- Het bedrijf wil niet overstappen, wil wel meewerken, heeft een tweede persoon die de code en het hosting-account kan overnemen en betaalt voor onderhoud: dan kan **bouwen** verstandig zijn.
- Het bedrijf blijkt zeer klein (een paar trekkers): dan verdient bouwen zich minder snel terug en is een los hulpmiddel of niets bouwen eerlijker.
- Het is vooral een leerproject: prima, maar zeg dat tegen het bedrijf (deel 2, hoofdstuk 24.5).

Wat een ervaren iemand zou doen (**Schatting**): eerst offerte en API-check, dan klein bouwen, elk kwartaal 2 - 3 uur code laten reviewen, en vóór de eerste regel productiecode contract en verzekering regelen (K).

---

## J. Architectuur, techstack, hosting en AI-code

### J.1 Architectuur (Schatting, onderbouwd met bronnen)

- **Eén modulaire monoliet met PostgreSQL.** Bijna alle geslaagde microservice-verhalen begonnen als monoliet ([Fowler](https://martinfowler.com/bliki/MonolithFirst.html)). Kies saaie technologie ([McKinley](https://mcfunley.com/choose-boring-technology)). Niet kiezen: PocketBase (nog onder v1.0, geen garantie op compatibiliteit, [GitHub](https://github.com/pocketbase/pocketbase)), microservices, Kubernetes.
- **Eén hoofdtaal.** Variant A: TypeScript overal, later een klein Python-solverproces. Variant B: Python (FastAPI) en een JavaScript-planbord. Beide eindigen met twee talen. Welke beter is voor een beginner is niet te onderbouwen: kies er één en wissel niet halverwege. Mijn lichte voorkeur: A.
- **Solver als apart proces** dat voorstellen teruggeeft. Voorstel, akkoord, uitvoeren. Eerst nooit automatisch toewijzen.
- **Job queue in dezelfde Postgres** voor e-mail, Portbase-polling en solver. Idempotente verwerking.
- **Audit log vanaf dag 1.** Rollen (planner, chauffeur, admin) en 2FA voor planner en admin.
- **Noodprocedure:** elke avond een PDF of Excel van het rooster van morgen op de telefoon van planner en eigenaar, een telefoonlijst buiten het systeem en één A4 "wat doen we als het systeem uit is". Leg vast hoe lang uitval mag duren (RTO) en hoeveel data verloren mag gaan (RPO).

### J.2 Hosting en maandkosten

| Post | Bedrag | Status |
|---|---|---|
| Zelf hosten (Hetzner, kleine server, back-ups, domein, monitoring) | ca. € 15 - 30 per maand | **Schatting** |
| Beheerd (Supabase Pro) | $ 25 per maand. Herstel op elk moment (PITR) $ 100 extra. Free plan pauzeert na 1 week | **Bevestigd** ([Supabase](https://supabase.com/pricing.md)). EU-regio niet bevestigd |
| Portbase | Zie F.1 | **Bevestigd** |
| Kaart en ETA | € 0 (zelf hosten of binnen de gratis grens) tot ca. $ 100 per 30.000 verzoeken | **Schatting** |
| Orders lezen | ca. $ 30 per 1.000 pagina's (Google). Taalmodel-API niet onderzocht | **Bevestigd** en **Open** |
| WhatsApp, Webfleet, boekhoudpakket | Niet vastgesteld | **Open** |
| Code-review door ervaren ontwikkelaar | 2 - 3 uur per kwartaal. Prijs niet onderzocht | **Schatting** |
| Verzekering en juridische hulp | Niet onderzocht | **Open** |

Totaal eigen onderdelen: grofweg € 50 - 200 per maand, zonder Portbase, telematica en WhatsApp (**Schatting**). **Hetzner-prijzen zijn onzeker.** Hetzner heeft geen Nederlandse locatie (Duitsland, Finland, Singapore, VS). Per 15 juni 2026 zijn prijzen aangepast (CX23 € 5,49, CX33 € 8,49, CPX22 € 19,49). De overzichtspagina en de prijsaanpassing laten niet duidelijk dezelfde plannen zien en media melden verhogingen van "tot 37%" tot "tot 200%". IPv4 zit er niet in ([Hetzner](https://www.hetzner.com/cloud/), [prijsaanpassing](https://docs.hetzner.com/general/infrastructure-and-availability/price-adjustment/)). **Open.** Back-ups van Hetzner bevatten geen aangekoppelde Volumes ([Hetzner](https://docs.hetzner.com/cloud/servers/backups-snapshots/overview/)). Maak dus een aparte, geteste database-dump op een tweede plek en oefen het terugzetten. De grootste kostenpost is bouw- en onderhoudstijd (geen bron voor euro's of uren).

### J.3 Werken met AI-code: de waarschuwingen

| Studie | Resultaat | Let op |
|---|---|---|
| Veracode | In 45% van 80 taken kwetsbaarheden uit de OWASP Top 10 ([Veracode](https://www.veracode.com/press-release/ai-generated-code-poses-major-security-risks-in-nearly-half-of-all-development-tasks-veracode-research-reveals/)) | Verkoper van beveiligingstools, persbericht |
| Stanford | Deelnemers met AI-assistent schreven minder veilige code en dachten vaker dat die veilig was ([arXiv](https://arxiv.org/abs/2211.03622)) | Oud model (2022) |
| METR | 16 ervaren ontwikkelaars waren met AI 19% langer bezig, terwijl ze 24% sneller verwachtten ([METR](https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/)) | Kleine steekproef, ervaren mensen. METR zegt zelf dat het voor beginners anders kan zijn |
| DORA 2025 | AI versterkt sterke en zwakke organisaties. Instabiliteit stijgt ([InfoQ](https://www.infoq.com/news/2025/09/dora-state-of-ai-in-dev-2025)) | Secundair |

**Let op de bronnen.** Bijna alle studies zijn van 2021 - 2025, met oudere modellen en losse taken: waarschuwingen, geen voorspelling. De Stack Overflow-cijfers spreken elkaar tegen (29% tegen 33% vertrouwen, en "66%" en "45%" zijn in de bronnen verwisseld, [Stack Overflow](https://stackoverflow.blog/2025/07/29/developers-remain-willing-but-reluctant-to-use-ai-the-2025-developer-survey-results-are-here)). Gebruik ze niet voor een precieze bewering. Geen studie gevonden over beginners die een complete bedrijfsapp bouwen. **Open.**

**Werkwijze** (**Schatting**, gangbare praktijk, geen bron schrijft het exact voor): één kleine functie per keer met een "klaar-als"-lijst. Tests eerst voor regels en alles met geld of toegang, en lees de tests zelf. Git vanaf dag 1. Staging en productie gescheiden, met nepdata op staging. Sleutels nooit in de code, scan op uitgelekte sleutels. Foutmeldingen en een melding als de back-up faalt. Een README die jij kunt lezen: opstarten, back-up terugzetten, waar de sleutels staan. Plan niet op een verondersteld AI-tempo.

---

## K. Veiligheid, privacy en juridisch (geen juridisch advies)

| Onderwerp | Wat de bronnen zeggen | Wat het betekent |
|---|---|---|
| **AVG en GPS** | Een locatie die aan een chauffeur gekoppeld kan worden is personeelsmonitoring. Je hebt een legitiem belang en noodzaak nodig en moet medewerkers informeren. In privétijd wegen hun belangen meestal zwaarder ([AP](https://autoriteitpersoonsgegevens.nl/nl/onderwerpen/werk-uitkering/controle-van-personeel)). De tachograafplicht rechtvaardigt geen bewaring van ruwe GPS-data of chauffeur-scores ([Legiscope](https://www.legiscope.com/blog/avg-transport-logistiek.html), secundair, verkoper van AVG-software) | Ontwerp data-arm (Schatting): locatie alleen tijdens ritten, geen scores, korte bewaartermijn voor ruwe GPS, privémodus |
| **OR** | De OR heeft instemmingsrecht op personeelsvolgsystemen. "Geschikt zijn" is genoeg ([Dirkzwager](https://www.dirkzwager.nl/kennis/artikelen/instemmingsrecht-van-de-or-volgens-het-or-privacyboekje-van-de-ap)). OR verplicht vanaf 50 werknemers, bij 10 - 49 kan een PVT ([Rijksoverheid](https://www.rijksoverheid.nl/themas/werk/pensioen/vraag-en-antwoord/ondernemingsraad/wanneer-is-een-ondernemingsraad-or-verplicht)) | Bij 0 - 9 medewerkers (**Open**) waarschijnlijk geen OR. De AVG geldt altijd |
| **Verwerkers-overeenkomst** | Verplicht als anderen persoonsgegevens voor jou verwerken. Datalek melden binnen 72 uur ([Ondernemersplein](https://ondernemersplein.overheid.nl/bedrijfsvoering/juridische-zaken/privacywetgeving-avg-checklist-voor-ondernemers/)) | Het bedrijf is verantwoordelijke, jij bent verwerker, ook met je onderaannemers (Schatting) |
| **Cyberbeveiligingswet (NIS2)** | Van kracht sinds 15 augustus 2026 voor 18 sectoren, waaronder vervoer ([Rijksoverheid](https://www.rijksoverheid.nl/actueel/nieuws/2026/08/15/cyberbeveiligingswet-en-wet-weerbaarheid-kritieke-entiteiten-vanaf-vandaag-van-kracht)). Meestal vanaf middelgroot: 50 medewerkers of > € 10 miljoen ([business.gov.nl](https://business.gov.nl/amendment/nis2-directive-protects-network-information-systems/)). Wegvervoerders alleen indirect genoemd ([CMS](https://cms.law/en/nld/publication/cyberbeveiligingswet-voor-de-vervoerssector)) | **Waarschijnlijk niet direct van toepassing, niet officieel bevestigd.** Grote klanten kunnen eisen doorgeven ([RVO](https://www.rvo.nl/nieuws/wat-betekent-cyberbeveiligingswet-voor-uw-bedrijf)). Basis: 2FA, minimale rechten, versleutelde back-ups, sleutels buiten de code |
| **EU AI Act** | Annex III 4(b): taaktoewijzing op basis van gedrag of persoonlijke kenmerken en prestatiebewaking van werknemers is hoog risico. Een voorlopig akkoord van 7 mei 2026 stelt dit uit naar 2 december 2027 ([ActuIA](https://actuia.com/en/news/hr-tools-and-artificial-intelligence-europe-delays-high-risk-obligations-to-december-2027/)). Een andere bron noemt het uitstel een voorstel en noemt taaktoewijzing niet ([Morgan Lewis](https://www.morganlewis.com/pubs/2026/06/changes-to-eu-ai-act-deadlines-what-it-means-for-employers-and-hr-technology-providers)) | **Voorlopig uitgesteld, niet formeel bevestigd.** Wijs niet toe op "betrouwbaarheid" of "snelheid" per chauffeur, maar op kwalificaties, uren en locatie. Juridisch niet getoetst |
| **Aansprakelijkheid** | Een fout van je systeem schuift de aansprakelijkheid niet naar Portbase of de terminal. Portbase sluit schade door onjuiste informatie uit, no-showkosten gaan naar de boekende partij ([Portbase](https://www.portbase.com/wp-content/uploads/2022/11/2022.11-EN-Service-Levels-HCN-vervoerders.pdf), [ECT](https://myterminal.ect.nl/help-center/truck-capacity/english)). AVC 2002 beperkt aansprakelijkheid voor vervoer ([Ondernemersplein](https://ondernemersplein.overheid.nl/wetten-en-regels/algemene-vervoerscondities-avc-gebruiken/)) | Bescherm met validatie, menselijke review, logboek en contract (Schatting). AVC-bedragen en CMR-limiet zijn niet gelezen |
| **Eenmanszaak en verzekering** | Bij een eenmanszaak ben je privé verantwoordelijk voor zakelijke schulden ([KvK](https://www.kvk.nl/starten/de-eenmanszaak/)). Beroepsaansprakelijkheid voor software (Univé): standaard € 2.500.000 per aanspraak, maar geen dekking voor het herstellen van je eigen werk, alleen aanvullend op een AVB ([Univé](https://www.unive.nl/zakelijk/bedrijfsaansprakelijkheidsverzekering/beroepsaansprakelijkheidsverzekering/software-developer)) | Contract met aansprakelijkheidsplafond en verzekering wegen zwaarder dan de rechtsvorm (Schatting). "Ik herstel binnen X uur" hoort in een SLA. Cyberverzekering **Open**. Leg het voor aan een jurist of KvK-adviseur |
| **Jouw leeftijd** | Geen bron gelezen over ondernemen op je 18e. Algemeen is 18 meerderjarig in Nederland (niet gebronnen) | Vraag het na bij de KvK als je een bedrijf start |

**Bij het contract** (checklist, **Schatting**): wat het systeem wel en niet doet (planner blijft eindverantwoordelijk), eigendom van code en data, export van alle data, support en reactietijd, aansprakelijkheidsplafond, wat er gebeurt als jij uitvalt, prijs voor onderhoud. Portbase-credentials zijn kritiek: wie ze heeft kan pre-notificaties versturen of annuleren. Bewaar ze in een secret manager en roteer ze.

---

## L. Guardrails

### L.1 Wat het systeem nooit zelf mag doen (Schatting, ondersteund door bronnen)

| Soort | Voorbeelden |
|---|---|
| **Hard** (systeem stelt niet voor, publiceert niet, meldt niet) | Rij- en rusttijd (561/2006). Gewicht binnen grens met marge. ADR- en tankbevoegdheid. Geldige release (geen COR, CDM of BLT). Slot aanwezig. Chassis past. Toegang tot de terminal |
| **Waarschuwing** (planner bevestigt) | Strakke slot- of LFD-marge. Veel wachttijdrisico. Afwijkend gewicht. Chauffeur dicht bij de limiet. Nieuwe locatie zonder historie |
| **Goedkeuring bij onzekerheid** | Weinig historie. Conflicterende data. ADR- en tankritten in de beginperiode. Alles boven een kostendrempel |

Een planning die niet binnen de regels past mag niet naar chauffeurs. In de lopende cao-onderhandeling stelt TLN voor dat een werknemer zo'n rooster mag weigeren, en CNV wil dat de verantwoordelijkheid bij de werkgever blijft ([CNV](https://www.cnv.nl/vervoer/vervoer-en-logistiek/cao-beroepsgoederenvervoer/nieuws/cao-beroepsgoederenvervoer-2026-10-30/)). **Bevestigd** (stand 30 oktober, volgende ronde 26 november).

### L.2 Logboek, noodstop en handmatige modus

- **Audit log per voorstel:** invoerdata en versie, geldende regels, gekozen en afgewezen alternatieven, wie accepteerde of wijzigde, reden, tijdstip.
- **Overrides** zijn toegestaan, maar zichtbaar, met redencode en gereviewd. Routine-omzeiling moeilijk maken, noodgevallen mogelijk ([Umbrex](https://umbrex.com/resources/transportation-management-system-playbook/change-management-and-planner-enablement/)). Dit is een consultancy-bron zonder cijfers.
- **Noodstop:** één knop zet het systeem terug naar niveau 0 of 1. Dagelijkse export van het vastgestelde plan. Oefen een uitval.

### L.3 Automation bias en algorithm aversion

Twee tegengestelde valkuilen:
- **Te veel vertrouwen.** In een experiment volgde 36 - 50% van de deelnemers met een beslishulp bij de eerste fout het foute advies, tegenover 1 van 14 zonder hulp. Medium automatiseringsgraad is een goed compromis. Laat mensen fouten ervaren tijdens de introductie ([core.ac.uk](https://core.ac.uk/download/187203187.pdf)). **Bevestigd.** De titel van dit document stond niet in de bron (waarschijnlijk Manzey e.a., 2012). **Open.**
- **Te weinig vertrouwen.** Mensen kiezen na een zichtbare fout vaak liever een mens dan een algoritme, ook als het algoritme beter is ([Dietvorst e.a.](https://repository.upenn.edu/fnce_papers/58)). Mogen aanpassen helpt: 76% gebruikte het model als aanpassen mocht, tegen 32% zonder ([Wharton](https://marketing.wharton.upenn.edu/wp-content/uploads/2020/07/Dietvorst-Overcoming-Algorithm-Aversion.pdf)). **Bevestigd.**
- **Uitleg is geen bewijs.** Uitleg verhoogt de acceptatie van advies, ook van fout advies ([Bansal e.a.](https://arxiv.org/abs/2006.14779)). Bij prognoses (geen routeplanning) verbeterden grote aanpassingen vaker en kleine verslechterden vaak ([Fildes e.a.](https://research.manchester.ac.uk/en/publications/effective-forecasting-and-judgmental-adjustments-an-empirical-eva/)). Dat pleit voor redencodes en een maandelijkse evaluatie van overrides.

Maatregelen (**Schatting**): toon onzekerheid (ETA-bandbreedte, aantal vergelijkbare ritten), laat kleine aanpassingen toe, laat vroeg een fout zien, bespreek fouten openlijk, en voeg af en toe bewust een testfout toe om te meten of er nog gecontroleerd wordt.

### L.4 Voorbeeld van een uitleg bij een voorstel

Dit voorbeeld is **verzonnen** (ontwerp, geen echte data):

> **Voorstel: chauffeur A, trekker 12, chassis C-204.** Reden: heeft ADR-tank en nog 3 u 50 min rijtijd over (nu 5 u 10 van 9 u). Eindigt om 15:40, 6 km van het depot. Slot Maasvlakte 10:00 - 11:00 bevestigd. De laatste 8 bezoeken aan klant X duurden mediaan 52 min (P90: 1 u 25). **Zekerheid: gemiddeld (8 metingen).** Alternatief: chauffeur B (18 min meer leeg rijden). Regels getoetst: rijtijd OK, gewicht 43,2 t van 44 t OK, release OK, retour depot voor 17:00 OK.

Alle cijfers komen uit de solver en de controle. Een taalmodel mag ze alleen herhalen, nooit zelf bedenken.

---

## M. Tank, flexitank en kiepwerk

Deel 2 laat zien dat dit bedrijf deze werkzaamheden zegt te doen (hoofdstuk 17, 24). Hier staat wat er extra speelt. Voor tank en ADR geldt: begin met standaard 20- en 40-voets droge containers en voeg tank en ADR pas toe als de basis stabiel is. Het zijn de grootste juridische, veiligheids- en milieurisico's. **Schatting.**

| Onderdeel | Extra regels en data | Bron |
|---|---|---|
| **Tank: vorige lading en reiniging** | Per tank de laatste ladingen met bewijs, reinigingshistorie en een geldig reinigingsdocument. Reinigingsprogramma hangt af van vorige en volgende lading. "A cleaning certificate alone is not sufficient". Een station moet de lading mogen reinigen | **Bevestigd** ([FSSC](https://www.fssc.com/wp-content/uploads/2023/03/Guidance-Document-Transport-Tank-Cleaning-V6.pdf), [ITCO](https://international-tank-container.org/en/technical/tank-cleaning)) |
| **Digitaal reinigingsdocument** | eECD is de digitale versie van het EFTCO-reinigingsdocument. Open API's zijn gratis te koppelen. Welke velden erin staan is niet gevonden | **Bevestigd** ([ECTA](https://ecta.com/?p=11451)), velden **Open** |
| **Planning** | Volgorde lossen, reinigen, laden. Reinigingsstation, wachttijd en terugweg zijn onderdeel van de uren | **Schatting** |
| **ADR-chauffeur voor tank** | Aparte specialisatie op het basis-ADR, 5 jaar geldig | **Bevestigd** ([Ondernemersplein](https://ondernemersplein.overheid.nl/wetten-en-regels/adr-certificaat-voor-chauffeurs-aanvragen/)) |
| **SQAS** | Beoordelingsschema van Cefic voor wegtransportbedrijven en tankreinigingsstations. Criteria voor planning zelf niet gevonden | **Bevestigd** ([Cefic](https://cefic.org/guidance/transport-and-logistics/road-guidance)), criteria **Open** |
| **Flexitank** | Past in een 20 ft container, 10.000 - 24.000 liter ([MSC](https://www.msc.com/ru/lp/blog/solutions/flexitank-container-guide)). Fabrikant (vendor): container met CSC-goedkeuring, vloeistof max 60 C bij laden, max 97 - 103% gevuld, tarra flexitank 96 kg, container wegen, routes langer dan 60 dagen afgeraden ([Techno-Tanks](https://technogroupusa.com/brochures/Flexitank%20Installation%20EN.pdf)). Extra stap: inbouwen en inspecteren | **Bevestigd**, installatietijd **Open** |
| **Kiepwerk en reachstacker** | Niets bruikbaars gevonden: kipchassis, methode, locatie, tijd, wie de reachstacker bedient | **Open**. Vraag het de planner |

**Niet gevonden:** een lijst van toegestane en verboden vorige ladingen, reinigingstijden per product, flexitank-installatietijd, SQAS-eisen voor dispatch en keuringsintervallen van ADR-voertuigen en tankcontainers. Meet tijden per handeling zelf (deel 2, hoofdstuk 24.3).

---

## N. Bouwvolgorde, veilig testen en KPI's

### N.1 Fasen

Dit is mijn voorstel (**Schatting**). Ik wijk op drie punten af van hoofdstuk 13.6 (zie O). Elke fase gaat pas live als de planner hem echt gebruikt en je een meetpunt hebt.

| Fase | Wat | Niveau erna | Pas door als |
|---|---|---|---|
| 0 | Gesprek, toestemming, 2 weken meekijken, regels vastleggen, 20 - 30 anonieme testdagen, baseline meten (2 - 4 weken) | n.v.t. | Het bedrijf wil het en de planner doet mee |
| 1 | Planbord met tijdlijn, rollen, 2FA, logboek, regels als data, noodexport | 0 | De planner gebruikt het een week naast zijn eigen werkwijze |
| 2 | Waarschuwingen: dubbele boeking, rijtijd, chassis-fit, LFD | 1 | Het aantal planfouten per week daalt |
| 3 | Orders inlezen met controle door de planner | 2 | Minuten typen per dag dalen. Percentage ongewijzigd goedgekeurd |
| 4 | Status en tijden (PWA), wachttijdmeting, concept-facturen | 2 - 3 | Chauffeurs gebruiken de knoppen. Tijden zijn compleet |
| 5 | Portbase HCN Road: eerst lezen, dan melden met akkoord | 2 - 3 | Geen afwijzingen of no-shows door de software |
| 6 | Voorstellen (eerst eenvoudige regels, dan OR-Tools), schaduw 4 - 8 weken | 2 | Percentage voorstellen ongewijzigd. Afwijkingen verklaard |
| 7 | Herplannen als voorstel. Deels niveau 3 voor standaardritten. Tank en ADR blijven op 2 of lager | 2 - 3 | Meerdere weken stabiel |

**Tijd** (afleiding, geen bron, veel onzekerheid): fase 0 - 2 in deeltijd naast school ongeveer 3 - 6 maanden. Fase 3 - 6 nog eens 4 - 8 maanden (Portbase-aanvraag en bouw misschien 1 - 3 maanden, doorlooptijd HCN Road niet gevonden, F.4). Totaal voor "het meeste automatisch": **een jaar of meer**. Wie minder belooft: vraag waarop dat is gebaseerd.

### N.2 Veilig testen

1. **Terugspelen met oude dagen.** Laat het systeem 20 - 30 echte planningsdagen opnieuw plannen en vergelijk met de planner (ritten, lege kilometers, wachttijd, regelschendingen). Dit onthult ontbrekende regels zonder risico.
2. **Schaduwdraaien** 4 - 8 weken. Het systeem maakt elke ochtend een voorstel, de planner doet zijn eigen rooster. Noteer elke afwijking en waarom. Schaduwmodus zegt of het werkt, niet of het geld oplevert ([Lathia](https://nlathia.github.io/2020/07/Shadow-mode-deployments.html)). **Bevestigd**, de bron gaat over ML-systemen. De vertaling naar planning is mijn afleiding.
3. **Deels live** voor een afgebakend deel, bijvoorbeeld twee trekkers of één type rit zonder ADR of tank, met akkoord per voorstel.
4. **Terugvaloptie blijft** tot de metingen enkele weken stabiel zijn: de export van gisteren en de noodprocedure (J.1).
5. **Privacy:** gebruik pseudoniemen in testdata.

### N.3 KPI's (Schatting, mijn voorstel)

Planningstijd per dag. Percentage voorstellen ongewijzigd goedgekeurd en de override-redenen. Op-tijd-percentage per stop. Wachttijd per terminal en klant. Lege kilometers. Kosten per rit, inclusief demurrage, detention, slottoeslagen en no-shows. Fouten die geld kostten en bijna-fouten die een harde regel opving. Overuren per chauffeur. Chauffeurstevredenheid (kort, elk kwartaal). Ritten die na publicatie handmatig zijn aangepast. **Succescriterium vooraf afspreken**, bijvoorbeeld "80% ongewijzigd goedgekeurd gedurende 4 weken" (mijn voorbeeld, kies het samen met de planner). Meet vooraf een baseline, want de omgeving verandert (C.3, H).

---

## O. Wat verandert er in hoofdstuk 13?

Hoofdstuk 13 blijft het uitgangspunt. Het nieuwe onderzoek geeft reden voor deze aanpassingen.

| Onderdeel in hoofdstuk 13 | Wat verandert | Waarom |
|---|---|---|
| 13.1 "Optimaliseren: moeilijk, en het minst nodig" | Half bijgesteld. Een solver kan de schaal aan, het moeilijke zit in regels en data. "Minst nodig" blijft waarschijnlijk waar bij een kleine vloot | D.1 (Schatting) |
| 13.4 regel 7 (rijtijd), 3 (gewicht), 11 (release): "waarschuwing" | Voor een automatisch voorstel of een automatische melding zijn deze **hard**. Een planner mag handmatig overrulen met reden | L.1, cao-discussie |
| 13.5 punt 6: "stuur nooit automatisch opnieuw" | Bij ECT Delta en Euromax is annuleren en opnieuw sturen met behoud van het label de enige weg voor een wijziging. Doe dat alleen via één bewaakte functie, idempotent, met akkoord kort voor slotbegin. Nooit "claim en annuleer" | F.2 |
| 13.5 punt 5: "begin met handmatige invoer van TAR, slot en LFD" | Het slot is niet los te boeken. Toon slot en TAR als velden uit Portbase-antwoorden. De LFD blijft handmatig of komt van de klant | F.2, F.3 |
| 13.5 punt 3: "no-show bij ECT kan € 100 kosten" | Klopt, maar wordt nu nog niet geheven (stand 18 november). Het risico is de toekomstige heffing. RWG rekent ook een niet-gebruikt piekslot door | F.2 |
| 13.5 punt 12 (privacy) en punt 8 (tachograaf) | Nu deels onderzocht: AVG, OR, downloadplicht | K, G.3 |
| 13.2 entiteiten | Toevoegen: order-concept, voorstel, override met redencode, audit log, bericht-log (idempotentiesleutel), uitzonderingenlijst, handeling (kiepen, flexitank, wassen), tank-ladinghistorie, reinigingsbewijs | C, D, E, M |
| 13.3 statusflow | Toevoegen: order-concept (ontvangen, gelezen, te controleren, goedgekeurd), voorstel (berekend, voorgesteld, goedgekeurd of afgekeurd, gepubliceerd) en per rit de vastheid (open, toegezegd, gestart) | D.5, E.2 |
| 13.6 bouwvolgorde | Nieuw: orders inlezen en logboek/noodstop als eigen stappen. Portbase eerst alleen lezen. Solver pas na Portbase en tijdmeting | N.1 |
| Aanname "Peppol verplicht in 2026 of 2027" | Onjuist voor binnenlandse B2B. Voorgesteld: 1 juli 2030 | G.6 |

---

## P. Kritische punten

Je vroeg om eerlijkheid. Dit zijn de punten waar ik me als sparringpartner zorgen over maak, in volgorde van belang.

1. **Is het bedrijf groot genoeg?** Eén bron zegt 0 - 9 medewerkers, een andere 0 FTE, en vlootgegevens ontbreken (deel 2, hoofdstuk 18). Bij een paar trekkers verdient een eigen systeem zich langzaam terug, en een pakket van tientallen tot enkele honderden euro per maand is moeilijk te verslaan (**Schatting**, de Modality-prijs is onbekend). Vraag wat fouten de afgelopen 12 maanden kostten: dat bepaalt wat bouwen mag kosten.
2. **Is er toestemming en een echte planner?** Er is geen bewijs dat het bedrijf een systeem wil (deel 2, hoofdstuk 24.1). Zonder een planner die meewerkt bouw je op aannames. Een opiniestuk uit het VK beschrijft planners die terugvallen op Excel als ze een voorstel niet begrijpen ([Motor Transport](https://motortransport.co.uk/opinion/your-new-tms-went-live-on-monday-by-friday-the-planners-were-back-on-spreadsheets/90651.article)). Of dat hier geldt is **Open**.
3. **Jij bent 18 en bouwt dit naast school.** Dat is geen bezwaar op zich, maar het bepaalt wat realistisch is: beperkte uren, drukke schoolperiodes en één persoon die alles weet. Een bedrijf mag een bedrijfskritisch systeem niet van één deeltijdbouwer laten afhangen zonder terugval. Maak schriftelijke afspraken, beloof geen 24/7 support, regel een tweede persoon met toegang en export van alle data, en gebruik de noodprocedure uit J.1. **Schatting.**
4. **Houd de eerste versie klein.** Een planbord met controles en een logboek. "Alles automatisch" is een eindbeeld, geen startpunt (Gall, I.2).
5. **Data eerst.** Zonder eigen tijden per stop kan geen solver realistisch plannen (H).
6. **Plannen is waarschijnlijk niet de grootste tijdwinst.** De bewezen automatisering zit in orders, tijden, berichten en facturen (C.3). Bij een kleine vloot kosten typen, bellen en administreren waarschijnlijk meer tijd dan puzzelen (**Schatting**, controleer het tijdens het meekijken).
7. **Dit bedrijf doet vooral "speciaal werk".** Dit deel gaat grotendeels over standaard zeecontainers. Het bedrijf zegt vooral tank (chemie), kiepen en flexitanks te doen. De best te automatiseren klasse kan dus een minderheid zijn. De verdeling is **Open**.
8. **Regels veranderen snel.** ECT wijzigde slotlengte en heffingen in weken. Alles als data met "geldig van - tot".
9. **Eén bron, één sleutel.** Portbase-credentials, hosting-account en code liggen bij jou: een continuïteitsrisico (J.1, K).
10. **AI-tempo is geen belofte.** Bewijs dat AI jou sneller of betrouwbaarder maakt is er niet (J.3).

**Wat ik anders zou doen dan "het meeste automatisch" als doel:** eerst het bedrijf spreken, dan een offerte vragen, dan twee weken meekijken en pas dan beslissen. Daarna een kleine laag bouwen die orders inleest, tijden bewaart en waarschuwt. De solver als laatste en kleinste stap. Na elke fase meten, en bereid zijn te stoppen als het bedrijf liever een pakket koopt.

---

## Q. Wat je nu als eerste doet

### Q.1 De eerste acht stappen

1. **Bepaal wat dit is.** Een systeem voor het bedrijf, of een leerproject? Schrijf in één A4 wat je wilt bereiken. Zeg het eerlijk tegen het bedrijf (deel 2, hoofdstuk 24.5).
2. **Gesprek met eigenaar of planner, en toestemming.** Zie deel 2, hoofdstuk 25.3. Bouw niets met echte data zonder duidelijke toestemming. Werk met verzonnen testdata.
3. **Vraag om 2 weken mee te kijken.** De eerste 2 dagen zonder vragen te stellen. Leg echte dagen vast (WhatsApp, Excel, telefoonlog, portalen).
4. **Vraag een offerte** bij Modality, en eventueel Go4TMS of FiLogic. Vraag naar prijs, API of export, ondersteuning van tank, ADR, kiepen en flexitank, looptijd van het contract en data-export. Geef geen bedrijfsdata door.
5. **Leg de regels vast** als data: de lijst uit hoofdstuk 13.4 plus de tank-regels uit M. Maak 20 - 30 anonieme testdagen.
6. **Meet de baseline** (2 - 4 weken): planningstijd, fouten, wachttijd en wat fouten het afgelopen jaar kostten.
7. **Regel het zakelijke:** geheimhouding, verwerkersovereenkomst, wie de data bezit, aansprakelijkheidsplafond, verzekering, rechtsvorm. Laat een jurist of KvK-adviseur meekijken.
8. **Bouw dan alleen het planbord** (fase 1) met nepdata: Git, staging, README, logboek.

### Q.2 Korte interviewleidraad

De lange lijst staat in de onderzoeksnotities (bestand `data_invoering_risicos.md`, onderdeel 7) en in hoofdstuk 12 en 25.3. Werkwijze: vraag steeds naar "de laatste keer dat...".

**Eigenaar**
1. Wat moet het systeem opleveren, en wat is dat in geld waard?
2. Welke fouten kostten de laatste 12 maanden geld? Bedragen en hoe vaak.
3. Wat mag het systeem nooit zelf beslissen?
4. Hoeveel trekkers, chauffeurs, planners en chassis? Welke systemen en contracten bestaan al?
5. Wat is het budget? Wie is verantwoordelijk na oplevering? Wie bezit de data?

**Planner**
1. Loop de laatste werkdag stap voor stap door: order binnen tot factuur.
2. Welke informatie heb je nodig voor één rit, en hoe vaak mist of klopt die niet?
3. Hoe kies je chauffeur, trekker en chassis? Welke regels?
4. Hoe lang duurt een rit echt per klant en terminal? Waar staat dat opgeschreven?
5. Hoe regel je slots, TAR, annuleringen en no-shows? Hoe volg je LFD, demurrage en detention?
6. Welke uitzonderingen komen dagelijks voor, en wat is "normaal"?
7. Welke beslissingen blijf je zelf nemen? Wat zou een slecht voorstel zijn?
8. Wat staat alleen in je hoofd? Wie neemt het over bij ziekte?

**Chauffeurs (2 - 4 gesprekken):** Wat is het vervelendste aan de planning nu? Hoe geef je status door en wat moet een app doen? Wat vind je van GPS en wat mag het bedrijf met die data?

**Administratie en data:** Welke data uit de planning moet in de facturatie, en welke fouten ontstaan? Wie is eigenaar van welke velden? Wat doen jullie als het systeem uitvalt?

---

## R. Tegenstrijdigheden en gaten in dit deel

| Onderwerp | Wat de bronnen laten zien | Wat je ermee doet |
|---|---|---|
| **Portbase-dienst voor hauliers** | Eén onderzoeker vond geen dienst voor wegvervoerders. Een ander vond HCN Road met directe API-toegang op de Portbase-pagina's | De primaire pagina's winnen (F.1) |
| **Duur van een Portbase-aansluiting** | "12 weken" geldt voor de Cargo Controller Import-API. Voor HCN Road niets gevonden | Reken niet met 12 weken voor HCN Road (**Open**) |
| **PyVRP en pickup-delivery** | README ja, "Why PyVRP" nee | Test het zelf voor je kiest |
| **Portbase-tarief** | Kop € 0,40, voorbeelden op dezelfde pagina € 0,38 | Gebruik € 0,40 |
| **Hetzner-prijzen** | Overzichtspagina en prijsaanpassing passen niet duidelijk bij elkaar. Media melden "tot 37%" en "tot 200%" | Controleer live voor je kiest |
| **Stack Overflow-cijfers** | 29% (blog) tegen 33% (InfoQ). De getallen 66% en 45% zijn verwisseld | Niet gebruiken |
| **Modality-API** | "Booking API" in het ene artikel, "Modality API" in het andere | Vraag in de offerte welke bestaat |
| **ECT-veiligheidstest** | Een secundaire bron noemt 3 november 2026. Hoofdstuk 11 gebruikt de nieuwste ECT-bron | Gebruik hoofdstuk 11 |
| **Automation-bias-studie** | Auteurs en titel niet zichtbaar (waarschijnlijk Manzey e.a. 2012) | Verifieer voor je citeert |
| **Cbw en AI Act** | Cbw-drempels voor wegvervoerders niet officieel bevestigd. AI Act-uitstel een voorlopig akkoord | Vraag een jurist. Geen advies |

**Niet onderzocht of niet gelezen:** HERE-prijzen, Samsara, Geotab, Trimble, Twinfield, AFAS, SnelStart, Yuki, WhatsApp-tarieven voor Nederland, het Portbase-developerportaal, versies en releasedata van de solvers, rekentijd op echte drayage-data, kiepwerk en reachstacker, rederij-API-toegang voor kleine transporteurs, Rotterdamse wachttijden en ritten per trekker per dag. Geen onafhankelijke meting van nauwkeurigheid bij order-AI en geen voor-en-na-meting van planningssoftware in het MKB.

---

## Bronnenlijst deel 3

Alleen links die in dit deel zijn gebruikt. Alle links komen letterlijk uit de onderzoeksnotities. Vendor-pagina's zijn bedrijfsinformatie over het eigen product (Vendor-claim).

**Portbase, terminals en rederijen**

- [Portbase: Hinterland Container Notification Road (HCN Road)](https://www.portbase.com/en/services/hinterland-container-notification-road/)
- [Portbase: kosten Hinterland-programma](https://www.portbase.com/en/programs/hinterland/costs/)
- [Portbase: HCN API connection instructions](https://hcn.pcs.portbase.com/api-documentation/connection_instructions.html)
- [Portbase Support: create a system interface](https://support.portbase.com/hc/en-gb/articles/29950155564562)
- [Portbase Support: Road planning system interface](https://support.portbase.com/en/services/road-planning-system-interface/)
- [Portbase: Service Levels HCN voor vervoerders (2022)](https://www.portbase.com/wp-content/uploads/2022/11/2022.11-EN-Service-Levels-HCN-vervoerders.pdf)
- [Portbase: Secure Chain voor inland operators](https://www.portbase.com/en/programs/secure-chain/inland-operators/)
- [Portbase: Cargo Release Manager](https://www.portbase.com/en/services/cargo-release-manager/)
- [Portbase: Cargo Controller](https://portbase.com/en/services/cargo-controller)
- [Portbase Support: Cargo Controller Import API](https://support.portbase.com/hc/en-gb/articles/32493593538450)
- [Portbase: pagina over API-koppeling (looptijd 12 weken, Cargo Controller Import)](https://www.portbase.com/en/?p=31339)
- [ECT: Update Truck Capacity Management System (18 november 2026)](https://www.ect.nl/en/news/news-feed/update-truck-capacity-management-system-hutchison-ports-ect-rotterdam)
- [ECT: ECT introduces a Truck Capacity Management System](https://www.ect.nl/en/news/news-feed/ect-introduces-truck-capacity-management-system)
- [ECT: Go-live Truck Capacity Management System](https://www.ect.nl/en/news/news-feed/go-live-truck-capacity-management-system)
- [ECT MyTerminal: Truck capacity help center (FAQ)](https://myterminal.ect.nl/help-center/truck-capacity/english)
- [ECT MyTerminal: geldigheid van voorgemelde truckbezoeken](https://myterminal.ect.nl/news/period-validity-pre-announced-truck-visits-ect-terminals)
- [ECT MyTerminal: Premium Plus](https://myterminal.ect.nl/premium-plus)
- [ECT MyTerminal: Import container status API](https://myterminal.ect.nl/api-products/import-container-status)
- [APM Terminals Maasvlakte II: FAQ](https://www.apmterminals.com/en/maasvlakte/practical-information/faq)
- [RWG: FAQ time slot surcharge tijdens piekuren](https://www.rwg.nl/en/faq-time-slot-surcharge-during-peak-hours)
- [DCSA: Track and Trace standaard](https://dcsa.org/standards/track-and-trace/standard-documentation-track-and-trace)
- [Maersk: data integrations](https://www.maersk.com/digital-services/data-integrations/solutions)
- [Maersk Nederland: import, kosten en voorwaarden](https://www.maersk.com/local-information/the-netherlands/import)
- [Hapag-Lloyd: API-portaal](https://ams.hapag-lloyd.com/pt/services-information/data-solutions/api-portal.html)
- [Port of Rotterdam: terugblik containerjaar 2025](https://www.portofrotterdam.com/en/news-and-press-releases/between-growth-and-pressure-rotterdams-2025-container-year-under-review)

**Automatisch plannen: solvers, reistijden en onderzoek**

- [Google OR-Tools: pickup and delivery](https://developers.google.com/optimization/routing/pickup_delivery)
- [Google OR-Tools: tijdvensters (VRPTW)](https://developers.google.com/optimization/routing/vrptw)
- [Google OR-Tools: straffen en overgeslagen bezoeken](https://developers.google.com/optimization/routing/penalties)
- [PyVRP: paper (arXiv)](https://arxiv.org/html/2403.13795v2)
- [PyVRP: README](https://raw.githubusercontent.com/PyVRP/PyVRP/main/README.md)
- [PyVRP: Why choose PyVRP](https://pyvrp.org/setup/why_pyvrp.html)
- [Timefold Solver Python (GitHub, gearchiveerd)](https://github.com/TimefoldAI/timefold-solver-python)
- [SolverForge-legacy (PyPI)](https://pypi.org/project/solverforge-legacy/)
- [Timefold docs: modelleren van planningsproblemen](https://docs.timefold.ai/timefold-solver/latest/domain-modeling/modeling-planning-problems)
- [Timefold docs: score calculation](https://docs.timefold.ai/timefold-solver/latest/constraints-and-score/score-calculation)
- [Timefold docs: real-time planning](https://docs.timefold.ai/timefold-solver/latest/responding-to-change/real-time-planning)
- [Timefold: prijzen](https://timefold.ai/pricing)
- [VROOM (GitHub)](https://github.com/VROOM-Project/vroom)
- [OSRM (GitHub)](https://github.com/Project-OSRM/osrm-backend)
- [Valhalla: route API-referentie](https://valhalla.github.io/valhalla/api/route/api-reference/)
- [OpenRouteService: routing-opties](https://giscience.github.io/openrouteservice/api-reference/endpoints/directions/routing-options)
- [TomTom Routing API: calculate route](https://docs.tomtom.com/routing-api/documentation/tomtom-maps/calculate-route)
- [TomTom: prijzen](https://docs.tomtom.com/pricing)
- [Google Routes API: Large vehicle routing (vrachtwagenroutering, beschikbaarheid per regio)](https://developers.google.com/maps/documentation/routes/lvr)
- [Google Maps Platform: prijzen](https://developers.google.com/maps/billing-and-pricing/pricing)
- [GraphHopper: prijzen](https://www.graphhopper.com/pricing/)
- [Europese Commissie: rij- en rusttijden](https://transport.ec.europa.eu/transport-modes/road/social-provisions/driving-time-and-rest-periods_en)
- [Braekers: proefschrift over drayage (Hasselt)](https://documentserver.uhasselt.be/bitstream/1942/14547/1/PhD%20Kris%20Braekers%20-%20Final%20version.pdf)
- [Zhang, Huang & Wang: literatuuroverzicht container-drayage (HKU)](https://hub.hku.hk/bitstream/10722/287150/1/content.pdf)
- [Xue e.a.: multi-shift full-truckload drayage (arXiv)](https://arxiv.org/pdf/2012.06538.pdf)
- [Goel (2010): planning met rij- en werktijdregels in de EU (Transportation Science)](https://econpapers.repec.org/RePEc:inm:ortrsc:v:44:y:2010:i:4:p:429-441)
- [Nottingham: reinforcement learning voor poort-trucks (EJOR 2023)](https://people.cs.nott.ac.uk/pszrq/files/EJOR23PortDRL.pdf)
- [From Words to Routes: LLM's en routeproblemen (arXiv)](https://arxiv.org/html/2403.10795v1)
- [Overzichtsartikel over LLM's bij routeproblemen (arXiv, 2026)](https://arxiv.org/pdf/2607.00604)
- [Kambhampati e.a.: LLMs Can't Plan, But Can Help Planning (arXiv)](https://arxiv.org/abs/2402.01817)
- [DrayFLEX Final Report (USDOT)](https://ops-dr.fhwa.dot.gov/fastact/atcmtd/fy16awards/6065-218-ATCMTD_2025_DrayFLEX_Final_Report.pdf)
- [USDOT ITS: FRATIS-resultaten (benefits record)](https://www.itskrs.its.dot.gov/2018-b01299)
- [TNO: Talking Trucks (rapport 2022)](https://publications.tno.nl/publication/34639406/BPCLln/TNO-2022-R10252.pdf)
- [TNO: casus Van Berkel Logistics (rapport 2020)](https://publications.tno.nl/publication/34637555/6xbWgu/TNO-2020-R11865.pdf)

**Orders inlezen en documenten**

- [Claude API: structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs)
- [Dashdoc: PDF naar transportorders met AI](https://www.dashdoc.com/en/blog/pdf-to-transport-orders-ai)
- [Wikipedia: ISO 6346 (containernummers)](https://en.wikipedia.org/wiki/ISO_6346)
- [Klippa DocHorizon](https://klippa.com/en/dochorizon)
- [Microsoft Document Intelligence: accuracy en confidence](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/concept/accuracy-confidence)
- [Google Document AI: prijzen](https://cloud.google.com/document-ai/pricing)
- [Rail-Flow: casus Staalduinen Logistics](https://rail-flow.com/case-studies/staalduinen-logistics)
- [NAM: artikel over AI-agents bij C.H. Robinson](https://nam.org/?p=38531)

**Pakketten, markt en bouwen of kopen**

- [Modality: automatisering containerwegtransport](https://www.modality.nl/?p=1673)
- [Modality: automatische binnenvaartplanning (Barge Planning Optimizer)](https://www.modality.nl/en/blog-en/automated-barge-planning/)
- [Modality: automatisch orders verwerken](https://www.modality.nl/en/blog-en/automating-order-processing/)
- [Modality: praktische AI-toepassingen in containerlogistiek](https://www.modality.nl/en/blog-en/practical-ai-applications-container-logistics/)
- [ICT: Modality](https://www.ict.eu/en/modality)
- [AntwerpXL: Go4Logistics (Go4TMS)](https://www.antwerpxl.com/exhibitors/go4logistics-196851/)
- [Capterra: EasyTrans](https://www.capterra.com/p/167861/EasyTrans/)
- [Capterra: TMS for Logistics Service Providers](https://www.capterra.com/p/10046514/TMS-for-Logistics-Service-Providers/)
- [Cargoson: TMS-prijzen en kosten](https://www.cargoson.com/nl/blog/transportmanagementsoftware-tms-prijs-kosten)
- [PortPro: AI dispatch en route planner](https://portpro.io/features/drayage-carrier/ai-dispatch-and-route-planner)
- [PortPro: casus OCTS](https://portpro.io/all-resources/case-studies/octs-boosts-cash-flow)
- [ABN AMRO: TMS in de cloud](https://www.abnamro.nl/nl/zakelijk/insights/sectoren-en-trends/ondernemersverhalen/logistiek/tms-in-de-cloud-is-niet-eng-en-de-voordelen-zijn-groot.html)
- [Rabobank: nieuwe mogelijkheden met AI in transport en logistiek](https://www.rabobank.nl/kennis/d011531409-nieuwe-mogelijkheden-met-ai-in-de-transport-en-logistiek)
- [TVM: Greenpaper Planner (2026)](https://www.tvm.nl/sites/default/files/2026-04/TVM_Greenpaper_Planner_A4_online.pdf)
- [TVM: Sectorstudie 2025](https://www.ttm.nl/wp-content/uploads/2025/11/TVMSectorstudie2025A4HR.pdf)
- [KiM: kostenkengetallen goederenvervoer, wegvervoer](https://www.kimnet.nl/binaries/kimnet/documenten/notities/2023/03/30/kostenkengetallen-voor-het-goederenvervoer/Kostenkengetallen+voor+het+goederenvervoer_Wegvervoer.pdf)
- [McKinsey: grote IT-projecten op tijd en binnen budget](https://www.mckinsey.com/capabilities/operations/our-insights/delivering-large-scale-it-projects-on-time-on-budget-and-on-value)
- [Wikipedia: John Gall (Gall's wet)](https://en.wikipedia.org/wiki/John_Gall_(author))
- [Umbrex: change management en planners (TMS-playbook)](https://umbrex.com/resources/transportation-management-system-playbook/change-management-and-planner-enablement/)
- [Motor Transport: nieuw TMS live, planners terug op spreadsheets](https://motortransport.co.uk/opinion/your-new-tms-went-live-on-monday-by-friday-the-planners-were-back-on-spreadsheets/90651.article)

**Status, app, telematica, berichten en facturatie**

- [Firt: PWA's op iOS](https://firt.dev/notes/pwa-ios/)
- [Webfleet: integratiepartners](https://www.webfleet.com/en_gb/webfleet/partners/integration)
- [Webfleet: tachograafdownloads](https://www.webfleet.com/en_gb/webfleet/blog/the-importance-of-tachograph-downloads-and-how-to-make-them-easier/)
- [Business.gov.nl: digitale tachograaf](https://business.gov.nl/regulation/digital-tachograph)
- [Meta: WhatsApp Business Platform, prijzen](https://developers.facebook.com/documentation/business-messaging/whatsapp/pricing)
- [Moneybird: API-introductie](https://developer.moneybird.com/introduction)
- [Apideck: gids voor de Exact Online API (2026)](https://dev.to/apideck/the-complete-guide-to-exact-online-api-integration-in-2026-529c)
- [Rijksoverheid: kabinet kiest voor e-facturatie en rapportage (11 september 2026)](https://www.rijksoverheid.nl/actueel/nieuws/2026/09/11/kabinet-kiest-voor-invoering-e-facturatie-en-rapportage-voor-bedrijven)
- [EDICOM: e-facturering en digitale rapportage in Nederland](https://edicomgroup.com/blog/netherlands-electronic-invoicing-digital-reporting)
- [Europese Commissie: eFTI-verordening](https://transport.ec.europa.eu/transport-themes/logistics-and-multimodal-transport/efti-regulation_en)
- [Trans.info: eCMR in 2026](https://trans.info/en/ecmr-in-2026-434860)
- [CNV: nieuws over de cao beroepsgoederenvervoer (30 oktober 2026)](https://www.cnv.nl/vervoer/vervoer-en-logistiek/cao-beroepsgoederenvervoer/nieuws/cao-beroepsgoederenvervoer-2026-10-30/)

**Architectuur, hosting en AI-code**

- [Martin Fowler: Monolith First](https://martinfowler.com/bliki/MonolithFirst.html)
- [Dan McKinley: Choose Boring Technology](https://mcfunley.com/choose-boring-technology)
- [PocketBase (GitHub)](https://github.com/pocketbase/pocketbase)
- [Supabase: prijzen](https://supabase.com/pricing.md)
- [Hetzner Cloud](https://www.hetzner.com/cloud/)
- [Hetzner: prijsaanpassing](https://docs.hetzner.com/general/infrastructure-and-availability/price-adjustment/)
- [Hetzner: backups en snapshots](https://docs.hetzner.com/cloud/servers/backups-snapshots/overview/)
- [Veracode: persbericht over onveilige AI-code](https://www.veracode.com/press-release/ai-generated-code-poses-major-security-risks-in-nearly-half-of-all-development-tasks-veracode-research-reveals/)
- [Perry e.a. (Stanford): onveilige code met een AI-assistent (arXiv)](https://arxiv.org/abs/2211.03622)
- [METR: ervaren open-source-ontwikkelaars met AI (juli 2025)](https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/)
- [InfoQ: DORA State of AI in software development 2025](https://www.infoq.com/news/2025/09/dora-state-of-ai-in-dev-2025)
- [Stack Overflow: Developer Survey 2025](https://stackoverflow.blog/2025/07/29/developers-remain-willing-but-reluctant-to-use-ai-the-2025-developer-survey-results-are-here)

**Juridisch en regels (geen juridisch advies)**

- [Autoriteit Persoonsgegevens: controle van personeel](https://autoriteitpersoonsgegevens.nl/nl/onderwerpen/werk-uitkering/controle-van-personeel)
- [Legiscope: AVG in transport en logistiek](https://www.legiscope.com/blog/avg-transport-logistiek.html)
- [Dirkzwager: instemmingsrecht van de OR volgens het OR-privacyboekje](https://www.dirkzwager.nl/kennis/artikelen/instemmingsrecht-van-de-or-volgens-het-or-privacyboekje-van-de-ap)
- [Rijksoverheid: wanneer is een ondernemingsraad verplicht](https://www.rijksoverheid.nl/themas/werk/pensioen/vraag-en-antwoord/ondernemingsraad/wanneer-is-een-ondernemingsraad-or-verplicht)
- [Ondernemersplein: AVG-checklist voor ondernemers](https://ondernemersplein.overheid.nl/bedrijfsvoering/juridische-zaken/privacywetgeving-avg-checklist-voor-ondernemers/)
- [Rijksoverheid: Cyberbeveiligingswet en Wet weerbaarheid kritieke entiteiten van kracht](https://www.rijksoverheid.nl/actueel/nieuws/2026/08/15/cyberbeveiligingswet-en-wet-weerbaarheid-kritieke-entiteiten-vanaf-vandaag-van-kracht)
- [Business.gov.nl: NIS2-richtlijn](https://business.gov.nl/amendment/nis2-directive-protects-network-information-systems/)
- [CMS: Cyberbeveiligingswet voor de vervoerssector](https://cms.law/en/nld/publication/cyberbeveiligingswet-voor-de-vervoerssector)
- [RVO: wat betekent de Cyberbeveiligingswet voor uw bedrijf](https://www.rvo.nl/nieuws/wat-betekent-cyberbeveiligingswet-voor-uw-bedrijf)
- [ActuIA: Europa stelt verplichtingen voor hoog-risico-AI uit tot december 2027](https://actuia.com/en/news/hr-tools-and-artificial-intelligence-europe-delays-high-risk-obligations-to-december-2027/)
- [Morgan Lewis: wijzigingen in de deadlines van de EU AI Act (juni 2026)](https://www.morganlewis.com/pubs/2026/06/changes-to-eu-ai-act-deadlines-what-it-means-for-employers-and-hr-technology-providers)
- [Ondernemersplein: Algemene Vervoerscondities (AVC)](https://ondernemersplein.overheid.nl/wetten-en-regels/algemene-vervoerscondities-avc-gebruiken/)
- [KvK: de eenmanszaak](https://www.kvk.nl/starten/de-eenmanszaak/)
- [Univé: beroepsaansprakelijkheidsverzekering software developer](https://www.unive.nl/zakelijk/bedrijfsaansprakelijkheidsverzekering/beroepsaansprakelijkheidsverzekering/software-developer)

**Mens en systeem, guardrails en testen**

- [Automation-bias-studie (core.ac.uk; titel niet bevestigd, waarschijnlijk Manzey e.a. 2012)](https://core.ac.uk/download/187203187.pdf)
- [CMS Conferences: studie naar beslishulp bij routeplanning](https://openaccess.cms-conferences.org/publications/book/978-1-958651-09-4/article/978-1-958651-09-4_1)
- [Dietvorst e.a.: Algorithm Aversion (UPenn repository)](https://repository.upenn.edu/fnce_papers/58)
- [Dietvorst e.a.: Overcoming Algorithm Aversion (Wharton)](https://marketing.wharton.upenn.edu/wp-content/uploads/2020/07/Dietvorst-Overcoming-Algorithm-Aversion.pdf)
- [Bansal e.a. (CHI 2021): effect van AI-uitleg op beslissingen (arXiv)](https://arxiv.org/abs/2006.14779)
- [Fildes e.a.: aanpassingen in supply-chain-planning (Manchester)](https://research.manchester.ac.uk/en/publications/effective-forecasting-and-judgmental-adjustments-an-empirical-eva/)
- [Lathia: shadow mode deployments](https://nlathia.github.io/2020/07/Shadow-mode-deployments.html)

**Tank, flexitank en gevaarlijke stoffen**

- [FSSC: Transport Tank Cleaning guidance (V6)](https://www.fssc.com/wp-content/uploads/2023/03/Guidance-Document-Transport-Tank-Cleaning-V6.pdf)
- [ITCO: tank cleaning](https://international-tank-container.org/en/technical/tank-cleaning)
- [ECTA: elektronisch reinigingsdocument (eECD)](https://ecta.com/?p=11451)
- [Ondernemersplein: ADR-certificaat voor chauffeurs](https://ondernemersplein.overheid.nl/wetten-en-regels/adr-certificaat-voor-chauffeurs-aanvragen/)
- [Cefic: richtlijnen voor wegtransport (o.a. flexitanks)](https://cefic.org/guidance/transport-and-logistics/road-guidance)
- [MSC: flexitank container guide](https://www.msc.com/ru/lp/blog/solutions/flexitank-container-guide)
- [Techno-Tanks: flexitank installatie (brochure)](https://technogroupusa.com/brochures/Flexitank%20Installation%20EN.pdf)

