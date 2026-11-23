import { test } from 'node:test';
import assert from 'node:assert/strict';

import { formatEuro, formatKm, parseBedrag, rdwDatumNaarIso, formatIsoDatum, netteNaam, dagenTussen } from '../src/js/format.js';
import { normaliseerKenteken, formatKenteken, isGeldigKenteken } from '../src/js/kenteken.js';
import { berekenBod, totaleSchade, dealSignaal } from '../src/js/calc.js';
import { leesVoertuig, tellerstandKleur, zoekKenteken, RdwFout } from '../src/js/rdw.js';
import { maakZip, leesZip, crc32, tekstUitBytes } from '../src/js/zip.js';

const zonderNbsp = (s) => s.replace(/ /g, ' ');

test('bedragen in euro met punt als duizendtal', () => {
  assert.equal(zonderNbsp(formatEuro(12500)), '€ 12.500');
  assert.equal(zonderNbsp(formatEuro(9400)), '€ 9.400');
  assert.equal(zonderNbsp(formatEuro(0)), '€ 0');
  assert.equal(formatEuro(null), '–');
  assert.equal(zonderNbsp(formatKm(125000)), '125.000 km');
});

test('ingetypte bedragen lezen', () => {
  assert.equal(parseBedrag('12.500'), 12500);
  assert.equal(parseBedrag('€ 12.500,50'), 12500);
  assert.equal(parseBedrag('12500'), 12500);
  assert.equal(parseBedrag(' 1 500 '), 1500);
  assert.equal(parseBedrag(''), null);
  assert.equal(parseBedrag('abc'), null);
  assert.equal(parseBedrag(null), null);
  assert.equal(parseBedrag(750), 750);
});

test('datums', () => {
  assert.equal(rdwDatumNaarIso('20240329'), '2024-03-29');
  assert.equal(rdwDatumNaarIso(''), null);
  assert.equal(rdwDatumNaarIso(undefined), null);
  assert.equal(formatIsoDatum('2024-03-29'), '29-03-2024');
  assert.equal(dagenTussen('2026-01-01T00:00:00Z', '2026-01-15T00:00:00Z'), 14);
});

test('nette namen uit RDW-hoofdletters', () => {
  assert.equal(netteNaam('MERCEDES-BENZ'), 'Mercedes-Benz');
  assert.equal(netteNaam('VOLKSWAGEN'), 'Volkswagen');
  assert.equal(netteNaam('BMW'), 'BMW');
  assert.equal(netteNaam('RAV4'), 'RAV4');
  assert.equal(netteNaam('GOLF VARIANT'), 'Golf Variant');
  assert.equal(netteNaam('ID.3 PRO S 150 KW'), 'ID.3 PRO S 150 KW');
  assert.equal(netteNaam('ZWART'), 'Zwart');
});

test('kenteken opschonen en opmaken', () => {
  assert.equal(normaliseerKenteken('52-bdv-4'), '52BDV4');
  assert.equal(normaliseerKenteken(' 52 BDV 4 '), '52BDV4');
  assert.equal(formatKenteken('52BDV4'), '52-BDV-4'); // sidecode 7
  assert.equal(formatKenteken('z174gk'), 'Z-174-GK'); // sidecode 10
  assert.equal(formatKenteken('GXB12P'), 'GXB-12-P'); // sidecode 11
  assert.equal(formatKenteken('00GBG3'), '00-GBG-3'); // sidecode 7
  assert.equal(formatKenteken('AB1234'), 'AB-12-34'); // sidecode 1
  assert.equal(formatKenteken('1ABC23'), '1-ABC-23'); // sidecode 8
  assert.equal(formatKenteken('ABC'), 'ABC');
  assert.equal(isGeldigKenteken('52-BDV-4'), true);
  assert.equal(isGeldigKenteken('123456'), false);
});

test('berekening advies bod (voorbeeld uit het plan)', () => {
  const bod = berekenBod({
    verkoopprijs: 12000,
    schades: [{ bedrag: 400 }, { bedrag: 200 }],
    margeMin: 1500,
    margeMax: 2000,
  });
  assert.equal(bod.compleet, true);
  assert.equal(bod.schadeTotaal, 600);
  assert.equal(bod.waardeNaSchade, 11400);
  assert.equal(bod.bodHoog, 9900); // hoogste bod = laagste marge
  assert.equal(bod.bodLaag, 9400); // laagste bod = hoogste marge
});

test('berekening zonder verkoopprijs, lege schade en omgedraaide marges', () => {
  const zonder = berekenBod({ verkoopprijs: null, schades: [{ bedrag: 100 }], margeMin: 1500, margeMax: 2000 });
  assert.equal(zonder.compleet, false);
  assert.equal(zonder.schadeTotaal, 100);

  assert.equal(totaleSchade([{ bedrag: null }, {}, { bedrag: 50 }]), 50);

  const omgedraaid = berekenBod({ verkoopprijs: 10000, schades: [], margeMin: 2000, margeMax: 1500 });
  assert.equal(omgedraaid.bodHoog, 8500);
  assert.equal(omgedraaid.bodLaag, 8000);
});

test('deal-signaal: vraagprijs tegenover hoogste bod', () => {
  const bod = berekenBod({ verkoopprijs: 12000, schades: [], margeMin: 1500, margeMax: 2000 });
  assert.equal(dealSignaal(10500, bod), 'goed');
  assert.equal(dealSignaal(10501, bod), 'slecht');
  assert.equal(dealSignaal(null, bod), null);
});

// Echte RDW-antwoorden (opgehaald november 2026), ingekort.
const RAV4 = {
  kenteken: 'Z174GK', voertuigsoort: 'Personenauto', merk: 'TOYOTA', handelsbenaming: 'TOYOTA RAV4',
  vervaldatum_apk: '20280329', eerste_kleur: 'ZWART', cilinderinhoud: '2487', datum_eerste_toelating: '20240329',
  datum_eerste_tenaamstelling_in_nederland: '20240329', catalogusprijs: '64090', openstaande_terugroepactie_indicator: 'Nee',
  jaar_laatste_registratie_tellerstand: '2026', tellerstandoordeel: 'Logisch', code_toelichting_tellerstandoordeel: '00',
};
const RAV4_BRANDSTOF = [
  { kenteken: 'Z174GK', brandstof_volgnummer: '1', brandstof_omschrijving: 'Elektriciteit', netto_max_vermogen_elektrisch: '174.00', klasse_hybride_elektrisch_voertuig: 'OVC-HEV' },
  { kenteken: 'Z174GK', brandstof_volgnummer: '2', brandstof_omschrijving: 'Benzine', nettomaximumvermogen: '136.00', klasse_hybride_elektrisch_voertuig: 'OVC-HEV' },
];
const UITLEG = [
  { code_toelichting_tellerstandoordeel: '00', toelichting_tellerstandoordeel: 'De geregistreerde tellerstand is steeds hoger dan de daarvoor geregistreerde tellerstand. Wij oordelen dan dat de tellerstand logisch verklaarbaar is.' },
];

test('RDW-gegevens uitlezen (plug-in hybride)', () => {
  const v = leesVoertuig(RAV4, RAV4_BRANDSTOF, UITLEG);
  assert.equal(v.merk, 'Toyota');
  assert.equal(v.model, 'RAV4');
  assert.equal(v.bouwjaar, 2024);
  assert.equal(v.datumEersteToelating, '2024-03-29');
  assert.equal(v.import, false);
  assert.deepEqual(v.brandstoffen, ['Elektriciteit', 'Benzine']);
  assert.equal(v.hybride, 'plug-in hybride');
  assert.equal(v.vermogenKw, 136); // motorvermogen, niet elektrisch
  assert.equal(v.cilinderinhoud, 2487);
  assert.equal(v.catalogusprijs, 64090);
  assert.equal(v.kleur, 'Zwart');
  assert.equal(v.apkVervaldatum, '2028-03-29');
  assert.equal(v.tellerstandoordeel, 'Logisch');
  assert.match(v.tellerstandUitleg, /logisch verklaarbaar/);
  assert.equal(v.terugroepactie, false);
});

test('RDW-gegevens uitlezen (volledig elektrisch, import)', () => {
  const v = leesVoertuig(
    { kenteken: 'GZS80K', merk: 'TESLA', handelsbenaming: 'MODEL Y', datum_eerste_toelating: '20230105', datum_eerste_tenaamstelling_in_nederland: '20240210', tellerstandoordeel: 'Niet geregistreerd', code_toelichting_tellerstandoordeel: 'NG', openstaande_terugroepactie_indicator: 'Ja' },
    [{ brandstof_volgnummer: '1', brandstof_omschrijving: 'Elektriciteit', netto_max_vermogen_elektrisch: '378.00' }],
    []
  );
  assert.equal(v.merk, 'Tesla');
  assert.equal(v.model, 'Model Y');
  assert.equal(v.vermogenKw, 378);
  assert.equal(v.cilinderinhoud, null);
  assert.equal(v.hybride, null);
  assert.equal(v.import, true);
  assert.equal(v.terugroepactie, true);
  assert.equal(v.tellerstandUitleg, null);
});

test('kleur van het tellerstandoordeel', () => {
  assert.equal(tellerstandKleur('Logisch'), 'groen');
  assert.equal(tellerstandKleur('Onlogisch'), 'rood');
  assert.equal(tellerstandKleur('Geen oordeel'), 'grijs');
  assert.equal(tellerstandKleur('Niet geregistreerd'), 'grijs');
  assert.equal(tellerstandKleur(null), 'grijs');
});

function nepFetch(antwoorden) {
  const urls = [];
  const fn = async (url) => {
    urls.push(url);
    const sleutel = Object.keys(antwoorden).find((k) => url.includes(k));
    const body = sleutel ? antwoorden[sleutel] : [];
    if (body instanceof Error) throw body;
    return { ok: true, status: 200, json: async () => body };
  };
  fn.urls = urls;
  return fn;
}

test('zoekKenteken gebruikt de juiste datasets en kenteken zonder streepjes', async () => {
  const f = nepFetch({ 'm9d7-ebf2': [RAV4], '8ys7-d773': RAV4_BRANDSTOF, 'jqs4-4kvw': UITLEG });
  const v = await zoekKenteken('z-174-gk', { fetchImpl: f });
  assert.equal(v.kenteken, 'Z174GK');
  assert.ok(f.urls.some((u) => u === 'https://opendata.rdw.nl/resource/m9d7-ebf2.json?kenteken=Z174GK'));
  assert.ok(f.urls.some((u) => u === 'https://opendata.rdw.nl/resource/8ys7-d773.json?kenteken=Z174GK'));
});

test('zoekKenteken: niet gevonden en geen internet', async () => {
  await assert.rejects(zoekKenteken('XX-99-99', { fetchImpl: nepFetch({}) }), (e) => e instanceof RdwFout && e.soort === 'niet-gevonden');
  const offline = async () => {
    throw new TypeError('Load failed');
  };
  await assert.rejects(
    zoekKenteken('XX-99-99', { fetchImpl: offline }),
    (e) => e instanceof RdwFout && e.soort === 'netwerk' && /niet bereikbaar|geen internet/.test(e.message)
  );
});

test('zip: schrijven en weer lezen geeft dezelfde inhoud', async () => {
  assert.equal(crc32(new TextEncoder().encode('123456789')), 0xcbf43926);
  const foto = new Uint8Array(5000).map((_, i) => i % 251);
  const blob = maakZip([
    { naam: 'taxaties.json', data: JSON.stringify({ hallo: 'wereld', prijs: '€ 12.500' }) },
    { naam: 'fotos/abc.jpg', data: foto },
  ]);
  const terug = leesZip(await blob.arrayBuffer());
  assert.deepEqual(JSON.parse(tekstUitBytes(terug.get('taxaties.json'))), { hallo: 'wereld', prijs: '€ 12.500' });
  assert.deepEqual(terug.get('fotos/abc.jpg'), foto);
});

test('zip: kapot bestand geeft duidelijke fout', () => {
  assert.throws(() => leesZip(new Uint8Array(100).buffer), /geen geldig back-upbestand/);
});
