// Back-up maken en terugzetten: alle auto's + foto's + instellingen in één ZIP-bestand.

import { db, leesInstellingen, schrijfInstellingen, schrijfMeta, leesMeta } from './db.js';
import { maakZip, leesZip, tekstUitBytes } from './zip.js';

const FORMAAT = 1;

// In de testversie binnen Claude mag de pagina zelf niets downloaden;
// dan biedt Claude het bestand aan via de "downloads"-functie.
const downloadsBelofte = (() => {
  try {
    return window.claude?.use ? window.claude.use('downloads').catch(() => null) : Promise.resolve(null);
  } catch {
    return Promise.resolve(null);
  }
})();

function datumVoorBestandsnaam(d = new Date()) {
  const p = (n) => String(n).padStart(2, '0');
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}`;
}

/** Maakt het back-upbestand klaar (nog niet delen). */
export async function maakBackup() {
  const [autos, fotos, instellingen] = await Promise.all([db.autos.toArray(), db.fotos.toArray(), leesInstellingen()]);

  const bestanden = [];
  const fotoInfo = [];
  for (const f of fotos) {
    const { groot, klein, ...rest } = f;
    fotoInfo.push(rest);
    bestanden.push({ naam: `fotos/${f.id}.jpg`, data: new Uint8Array(groot) });
    if (klein) bestanden.push({ naam: `fotos/${f.id}-klein.jpg`, data: new Uint8Array(klein) });
  }

  const inhoud = {
    app: 'taxatie-app',
    formaat: FORMAAT,
    gemaakt: new Date().toISOString(),
    instellingen,
    autos,
    fotos: fotoInfo,
  };
  bestanden.unshift({ naam: 'taxaties.json', data: JSON.stringify(inhoud) });

  const blob = maakZip(bestanden);
  const naam = `taxatie-backup-${datumVoorBestandsnaam()}.zip`;
  const bestand = new File([blob], naam, { type: 'application/zip' });
  return {
    bestand,
    aantalAutos: autos.filter((a) => a.status === 'archief').length,
    aantalFotos: fotos.length,
  };
}

/**
 * Deelt of downloadt het bestand. Moet direct vanuit een tik worden aangeroepen
 * (Safari staat delen anders niet toe).
 * @returns {Promise<boolean>} true als het gelukt is
 */
export async function deelBackup(bestand) {
  const downloads = await downloadsBelofte;
  if (downloads) {
    try {
      await downloads.save({ filename: bestand.name, data: bestand });
      await markeerBackup();
      return true;
    } catch (e) {
      if (e?.code === 'declined') return false;
      throw new Error('Opslaan lukt hier niet. Probeer het in de echte app.');
    }
  }
  if (navigator.canShare?.({ files: [bestand] })) {
    try {
      await navigator.share({ files: [bestand], title: bestand.name });
      await markeerBackup();
      return true;
    } catch (e) {
      if (e?.name === 'AbortError') return false; // gebruiker heeft geannuleerd
      // anders: val terug op downloaden
    }
  }
  const url = URL.createObjectURL(bestand);
  const a = document.createElement('a');
  a.href = url;
  a.download = bestand.name;
  document.body.append(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 60000);
  await markeerBackup();
  return true;
}

export function markeerBackup() {
  return schrijfMeta('laatsteBackup', Date.now());
}

export function laatsteBackup() {
  return leesMeta('laatsteBackup');
}

/** Leest een back-upbestand en geeft een samenvatting terug, zonder iets op te slaan. */
export async function leesBackup(bestand) {
  const inhoud = leesZip(await bestand.arrayBuffer());
  const json = inhoud.get('taxaties.json');
  if (!json) throw new Error('Dit is geen back-up van deze app.');
  const data = JSON.parse(tekstUitBytes(json));
  if (data.app !== 'taxatie-app') throw new Error('Dit is geen back-up van deze app.');
  if (data.formaat > FORMAAT) throw new Error('Deze back-up komt uit een nieuwere versie van de app. Werk de app eerst bij.');
  return { data, inhoud };
}

/** Zet een gelezen back-up terug. Auto's met hetzelfde ID worden overschreven, andere blijven staan. */
export async function zetBackupTerug({ data, inhoud }) {
  const fotos = [];
  for (const info of data.fotos ?? []) {
    const groot = inhoud.get(`fotos/${info.id}.jpg`);
    if (!groot) continue;
    const klein = inhoud.get(`fotos/${info.id}-klein.jpg`);
    fotos.push({
      ...info,
      groot: groot.buffer.slice(groot.byteOffset, groot.byteOffset + groot.byteLength),
      klein: klein ? klein.buffer.slice(klein.byteOffset, klein.byteOffset + klein.byteLength) : null,
    });
  }
  const autos = data.autos ?? [];

  await db.transaction('rw', db.autos, db.fotos, async () => {
    await db.autos.bulkPut(autos);
    await db.fotos.bulkPut(fotos);
  });
  if (data.instellingen) await schrijfInstellingen(data.instellingen);
  return { aantalAutos: autos.filter((a) => a.status === 'archief').length, aantalFotos: fotos.length };
}
