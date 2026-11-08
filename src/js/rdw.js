// Ophalen en uitlezen van RDW Open Data (gratis, geen sleutel nodig).
// Datasets en veldnamen gecontroleerd op opendata.rdw.nl (november 2026):
//   m9d7-ebf2  Gekentekende_voertuigen          (basisgegevens)
//   8ys7-d773  Gekentekende_voertuigen_brandstof (brandstof + vermogen)
//   jqs4-4kvw  Tellerstandoordeel Trend Toelichting (uitleg per code)

import { normaliseerKenteken } from './kenteken.js';
import { netteNaam, rdwDatumNaarIso } from './format.js';

const BASIS_URL = 'https://opendata.rdw.nl/resource/';
export const DATASETS = {
  voertuigen: 'm9d7-ebf2',
  brandstof: '8ys7-d773',
  tellerstandUitleg: 'jqs4-4kvw',
};

export class RdwFout extends Error {
  constructor(soort, bericht) {
    super(bericht);
    this.soort = soort; // 'niet-gevonden' | 'netwerk' | 'server'
  }
}

const getal = (v) => {
  if (v === undefined || v === null || v === '') return null;
  const n = Number(v);
  return Number.isFinite(n) ? n : null;
};

const HYBRIDE_KLASSE = {
  'OVC-HEV': 'plug-in hybride',
  'NOVC-HEV': 'hybride',
  'OVC-FCHV': 'waterstof (plug-in)',
  'NOVC-FCHV': 'waterstof',
};

/** Kleur van het tellerstandoordeel in de app. */
export function tellerstandKleur(oordeel) {
  if (oordeel === 'Logisch') return 'groen';
  if (oordeel === 'Onlogisch') return 'rood';
  return 'grijs';
}

/** Haalt het merk van de voorkant van de handelsbenaming af: "TOYOTA RAV4" -> "RAV4". */
function modelZonderMerk(merk, handelsbenaming) {
  const m = String(merk ?? '').trim().toUpperCase();
  const h = String(handelsbenaming ?? '').trim();
  if (m && h.toUpperCase().startsWith(m + ' ')) return h.slice(m.length + 1).trim();
  return h;
}

/**
 * Zet de ruwe RDW-rijen om naar de gegevens die de app gebruikt.
 * Alles wat de RDW niet geeft, wordt null.
 */
export function leesVoertuig(rij, brandstofRijen = [], uitlegRijen = []) {
  const brandstoffen = [...brandstofRijen].sort(
    (a, b) => (getal(a.brandstof_volgnummer) ?? 0) - (getal(b.brandstof_volgnummer) ?? 0)
  );

  const namen = brandstoffen.map((b) => b.brandstof_omschrijving).filter(Boolean);
  const klasse = brandstoffen.map((b) => b.klasse_hybride_elektrisch_voertuig).find(Boolean) ?? null;

  // Vermogen: motorvermogen (brandstofmotor). Alleen elektrisch? Dan het elektrische vermogen.
  const motorKw = brandstoffen
    .filter((b) => b.brandstof_omschrijving !== 'Elektriciteit')
    .map((b) => getal(b.nettomaximumvermogen))
    .filter((n) => n !== null);
  const elektrischKw = brandstoffen
    .map((b) => getal(b.netto_max_vermogen_elektrisch))
    .filter((n) => n !== null);
  const vermogenKw = motorKw.length ? Math.max(...motorKw) : elektrischKw.length ? Math.max(...elektrischKw) : null;

  const code = rij.code_toelichting_tellerstandoordeel ?? null;
  const uitleg = uitlegRijen.find((u) => u.code_toelichting_tellerstandoordeel === code);

  const eersteToelating = rdwDatumNaarIso(rij.datum_eerste_toelating);
  const eersteNL = rdwDatumNaarIso(rij.datum_eerste_tenaamstelling_in_nederland);

  return {
    kenteken: rij.kenteken,
    voertuigsoort: rij.voertuigsoort ?? null,
    merk: netteNaam(rij.merk),
    model: netteNaam(modelZonderMerk(rij.merk, rij.handelsbenaming)),
    merkRuw: rij.merk ?? null,
    handelsbenaming: rij.handelsbenaming ?? null,
    datumEersteToelating: eersteToelating,
    datumEersteNL: eersteNL,
    bouwjaar: eersteToelating ? Number(eersteToelating.slice(0, 4)) : null,
    // Eerder buiten Nederland toegelaten (import)? Dan verschillen de twee datums.
    import: Boolean(eersteToelating && eersteNL && eersteToelating !== eersteNL),
    brandstoffen: namen,
    hybride: klasse ? HYBRIDE_KLASSE[klasse] ?? klasse : null,
    kleur: rij.eerste_kleur ? netteNaam(rij.eerste_kleur) : null,
    catalogusprijs: getal(rij.catalogusprijs),
    apkVervaldatum: rdwDatumNaarIso(rij.vervaldatum_apk),
    tellerstandoordeel: rij.tellerstandoordeel ?? null,
    tellerstandCode: code,
    tellerstandUitleg: uitleg?.toelichting_tellerstandoordeel ?? null,
    jaarLaatsteTellerstand: getal(rij.jaar_laatste_registratie_tellerstand),
    cilinderinhoud: getal(rij.cilinderinhoud),
    vermogenKw,
    inrichting: rij.inrichting ?? null,
    terugroepactie: rij.openstaande_terugroepactie_indicator === 'Ja',
    opgehaaldOp: new Date().toISOString(),
  };
}

async function haalJson(url, fetchImpl, signal) {
  let antwoord;
  try {
    antwoord = await fetchImpl(url, { signal, headers: { Accept: 'application/json' } });
  } catch (e) {
    if (e?.name === 'AbortError') throw e;
    throw new RdwFout('netwerk', 'Geen verbinding met de RDW. Controleer je internet en probeer het opnieuw.');
  }
  if (!antwoord.ok) {
    throw new RdwFout('server', `De RDW gaf een fout terug (code ${antwoord.status}). Probeer het later opnieuw.`);
  }
  return antwoord.json();
}

/** Haalt alle gegevens van één kenteken op bij de RDW. */
export async function zoekKenteken(invoer, { fetchImpl = globalThis.fetch.bind(globalThis), signal } = {}) {
  const kenteken = normaliseerKenteken(invoer);
  if (!kenteken) throw new RdwFout('niet-gevonden', 'Vul eerst een kenteken in.');
  const q = encodeURIComponent(kenteken);

  const [voertuigen, brandstof, uitleg] = await Promise.all([
    haalJson(`${BASIS_URL}${DATASETS.voertuigen}.json?kenteken=${q}`, fetchImpl, signal),
    haalJson(`${BASIS_URL}${DATASETS.brandstof}.json?kenteken=${q}`, fetchImpl, signal),
    // Kleine tabel (9 regels); mag mislukken zonder dat de rest stopt.
    haalJson(`${BASIS_URL}${DATASETS.tellerstandUitleg}.json`, fetchImpl, signal).catch((e) => {
      if (e?.name === 'AbortError') throw e;
      return [];
    }),
  ]);

  if (!Array.isArray(voertuigen) || voertuigen.length === 0) {
    throw new RdwFout('niet-gevonden', `Kenteken ${kenteken} is niet gevonden bij de RDW. Klopt het kenteken?`);
  }
  return leesVoertuig(voertuigen[0], brandstof, uitleg);
}
