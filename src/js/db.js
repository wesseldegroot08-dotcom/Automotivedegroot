// Lokale opslag op de telefoon (IndexedDB via Dexie). Niets gaat naar internet.

import Dexie from '../vendor/dexie.js';
import { STANDAARD_INSTELLINGEN } from './constants.js';
import { berekenBod } from './calc.js';

export const db = new Dexie('taxatie-app');

db.version(1).stores({
  autos: 'id, status, aangemaakt, bijgewerkt',
  fotos: 'id, autoId',
  meta: 'sleutel',
});

export function nieuwId() {
  if (globalThis.crypto?.randomUUID) return crypto.randomUUID();
  const b = crypto.getRandomValues(new Uint8Array(16));
  return [...b].map((x) => x.toString(16).padStart(2, '0')).join('');
}

// ---------- meta / instellingen ----------

export async function leesMeta(sleutel, standaard = null) {
  const rij = await db.meta.get(sleutel);
  return rij ? rij.waarde : standaard;
}

export function schrijfMeta(sleutel, waarde) {
  return db.meta.put({ sleutel, waarde });
}

export async function leesInstellingen() {
  const opgeslagen = (await leesMeta('instellingen')) ?? {};
  return {
    ...STANDAARD_INSTELLINGEN,
    ...opgeslagen,
    schadeStandaard: { ...STANDAARD_INSTELLINGEN.schadeStandaard, ...(opgeslagen.schadeStandaard ?? {}) },
  };
}

export function schrijfInstellingen(instellingen) {
  return schrijfMeta('instellingen', instellingen);
}

// ---------- auto's ----------

export function leegAuto() {
  const nu = Date.now();
  return {
    id: nieuwId(),
    status: 'concept', // 'concept' = nog bezig, 'archief' = opgeslagen
    aangemaakt: nu,
    bijgewerkt: nu,
    getaxeerdOp: null,
    kenteken: '',
    rdw: null,
    km: null,
    uitvoering: '',
    transmissie: null,
    opties: [],
    optiesAnders: '',
    advertentieUrl: '',
    vraagprijs: null,
    fotoIds: [],
    schades: [],
    notities: '',
    verkoopprijs: null,
    margeMin: null, // vastgelegd bij opslaan in archief
    margeMax: null,
    bodHoog: null,
    bodLaag: null,
  };
}

/** De taxatie waar je nu mee bezig bent (blijft bewaard als de app sluit). */
export async function haalConcept() {
  const id = await leesMeta('conceptId');
  if (id) {
    const auto = await db.autos.get(id);
    if (auto && auto.status === 'concept') return auto;
  }
  const auto = leegAuto();
  await db.autos.put(auto);
  await schrijfMeta('conceptId', auto.id);
  return auto;
}

/** Welke marge geldt voor deze auto? Concept: instellingen. Archief: de marge van toen. */
export function margeVoor(auto, instellingen) {
  if (auto.status === 'archief' && auto.margeMin !== null && auto.margeMax !== null) {
    return { min: auto.margeMin, max: auto.margeMax };
  }
  return { min: instellingen.margeMin, max: instellingen.margeMax };
}

export function bodVoor(auto, instellingen) {
  const marge = margeVoor(auto, instellingen);
  return berekenBod({ verkoopprijs: auto.verkoopprijs, schades: auto.schades, margeMin: marge.min, margeMax: marge.max });
}

export async function bewaarAuto(auto, instellingen) {
  const bod = bodVoor(auto, instellingen);
  auto.bodHoog = bod.compleet ? bod.bodHoog : null;
  auto.bodLaag = bod.compleet ? bod.bodLaag : null;
  auto.bijgewerkt = Date.now();
  await db.autos.put(auto);
}

export async function zetInArchief(auto, instellingen) {
  auto.status = 'archief';
  auto.getaxeerdOp = Date.now();
  auto.margeMin = instellingen.margeMin;
  auto.margeMax = instellingen.margeMax;
  await bewaarAuto(auto, instellingen);
  if ((await leesMeta('conceptId')) === auto.id) await db.meta.delete('conceptId');
}

export async function verwijderAuto(id) {
  await db.transaction('rw', db.autos, db.fotos, db.meta, async () => {
    await db.fotos.where('autoId').equals(id).delete();
    await db.autos.delete(id);
    if ((await leesMeta('conceptId')) === id) await db.meta.delete('conceptId');
  });
}

export function archief() {
  return db.autos.where('status').equals('archief').toArray();
}

// ---------- foto's ----------

export async function bewaarFoto(autoId, verkleind) {
  const id = nieuwId();
  await db.fotos.put({ id, autoId, ...verkleind, aangemaakt: Date.now() });
  return id;
}

export function haalFoto(id) {
  return db.fotos.get(id);
}

export function verwijderFoto(id) {
  return db.fotos.delete(id);
}

// ---------- opslag ----------

export async function vraagBlijvendeOpslag() {
  try {
    if (!navigator.storage?.persist) return null;
    if (await navigator.storage.persisted()) return true;
    return await navigator.storage.persist();
  } catch {
    return null;
  }
}

export async function opslagStatus() {
  const status = { blijvend: null, gebruikt: null };
  try {
    if (navigator.storage?.persisted) status.blijvend = await navigator.storage.persisted();
    if (navigator.storage?.estimate) status.gebruikt = (await navigator.storage.estimate()).usage ?? null;
  } catch {
    /* niet beschikbaar */
  }
  return status;
}
