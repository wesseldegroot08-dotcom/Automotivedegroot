// Minimale ZIP-schrijver en -lezer (zonder compressie) voor back-ups.
// Foto's zijn al JPEG, dus compressie levert bijna niets op.
// Zo kunnen veel foto's in één bestand zonder het geheugen van de iPhone vol te zetten.

const encoder = new TextEncoder();
const decoder = new TextDecoder();

const CRC_TABEL = (() => {
  const t = new Uint32Array(256);
  for (let n = 0; n < 256; n++) {
    let c = n;
    for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
    t[n] = c >>> 0;
  }
  return t;
})();

export function crc32(bytes) {
  let c = 0xffffffff;
  for (let i = 0; i < bytes.length; i++) c = CRC_TABEL[(c ^ bytes[i]) & 0xff] ^ (c >>> 8);
  return (c ^ 0xffffffff) >>> 0;
}

function dosTijd(d) {
  const tijd = (d.getHours() << 11) | (d.getMinutes() << 5) | Math.floor(d.getSeconds() / 2);
  const datum = ((Math.max(1980, d.getFullYear()) - 1980) << 9) | ((d.getMonth() + 1) << 5) | d.getDate();
  return { tijd, datum };
}

const naarBytes = (data) =>
  typeof data === 'string' ? encoder.encode(data) : data instanceof Uint8Array ? data : new Uint8Array(data);

/**
 * Maakt een ZIP-bestand.
 * @param {{naam: string, data: string|Uint8Array|ArrayBuffer}[]} bestanden
 * @returns {Blob}
 */
export function maakZip(bestanden, datum = new Date()) {
  const delen = [];
  const centraal = [];
  let positie = 0;
  const { tijd, datum: dosDatum } = dosTijd(datum);

  for (const b of bestanden) {
    const naam = encoder.encode(b.naam);
    const data = naarBytes(b.data);
    const crc = crc32(data);

    const lokaal = new DataView(new ArrayBuffer(30));
    lokaal.setUint32(0, 0x04034b50, true);
    lokaal.setUint16(4, 20, true); // versie
    lokaal.setUint16(6, 0x0800, true); // UTF-8 namen
    lokaal.setUint16(8, 0, true); // geen compressie
    lokaal.setUint16(10, tijd, true);
    lokaal.setUint16(12, dosDatum, true);
    lokaal.setUint32(14, crc, true);
    lokaal.setUint32(18, data.length, true);
    lokaal.setUint32(22, data.length, true);
    lokaal.setUint16(26, naam.length, true);
    lokaal.setUint16(28, 0, true);
    delen.push(lokaal.buffer, naam, data);

    const c = new DataView(new ArrayBuffer(46));
    c.setUint32(0, 0x02014b50, true);
    c.setUint16(4, 20, true);
    c.setUint16(6, 20, true);
    c.setUint16(8, 0x0800, true);
    c.setUint16(10, 0, true);
    c.setUint16(12, tijd, true);
    c.setUint16(14, dosDatum, true);
    c.setUint32(16, crc, true);
    c.setUint32(20, data.length, true);
    c.setUint32(24, data.length, true);
    c.setUint16(28, naam.length, true);
    c.setUint32(42, positie, true);
    centraal.push(c.buffer, naam);

    positie += 30 + naam.length + data.length;
  }

  const centraalGrootte = centraal.reduce((s, d) => s + d.byteLength, 0);
  const eind = new DataView(new ArrayBuffer(22));
  eind.setUint32(0, 0x06054b50, true);
  eind.setUint16(8, bestanden.length, true);
  eind.setUint16(10, bestanden.length, true);
  eind.setUint32(12, centraalGrootte, true);
  eind.setUint32(16, positie, true);

  return new Blob([...delen, ...centraal, eind.buffer], { type: 'application/zip' });
}

/**
 * Leest een ZIP-bestand dat met maakZip is gemaakt.
 * @param {ArrayBuffer} buffer
 * @returns {Map<string, Uint8Array>}
 */
export function leesZip(buffer) {
  const bytes = new Uint8Array(buffer);
  const view = new DataView(buffer);
  let eind = -1;
  for (let i = bytes.length - 22; i >= Math.max(0, bytes.length - 22 - 65535); i--) {
    if (view.getUint32(i, true) === 0x06054b50) {
      eind = i;
      break;
    }
  }
  if (eind < 0) throw new Error('Dit is geen geldig back-upbestand (geen ZIP).');

  const aantal = view.getUint16(eind + 10, true);
  let p = view.getUint32(eind + 16, true);
  const resultaat = new Map();

  for (let i = 0; i < aantal; i++) {
    if (view.getUint32(p, true) !== 0x02014b50) throw new Error('Back-upbestand is beschadigd.');
    const methode = view.getUint16(p + 10, true);
    const crc = view.getUint32(p + 16, true);
    const grootte = view.getUint32(p + 20, true);
    const naamLengte = view.getUint16(p + 28, true);
    const extraLengte = view.getUint16(p + 30, true);
    const commentLengte = view.getUint16(p + 32, true);
    const lokaalStart = view.getUint32(p + 42, true);
    const naam = decoder.decode(bytes.subarray(p + 46, p + 46 + naamLengte));

    if (methode !== 0) throw new Error('Dit back-upbestand is ingepakt door een ander programma en kan niet worden gelezen.');
    const lNaam = view.getUint16(lokaalStart + 26, true);
    const lExtra = view.getUint16(lokaalStart + 28, true);
    const start = lokaalStart + 30 + lNaam + lExtra;
    const data = bytes.slice(start, start + grootte);
    if (crc32(data) !== crc) throw new Error(`Back-upbestand is beschadigd (${naam}).`);
    resultaat.set(naam, data);

    p += 46 + naamLengte + extraLengte + commentLengte;
  }
  return resultaat;
}

export const tekstUitBytes = (bytes) => decoder.decode(bytes);
