// Opmaak van bedragen, getallen en datums (Nederlandse notatie).

const euroFmt = new Intl.NumberFormat('nl-NL', {
  style: 'currency',
  currency: 'EUR',
  maximumFractionDigits: 0,
  minimumFractionDigits: 0,
});
const getalFmt = new Intl.NumberFormat('nl-NL', { maximumFractionDigits: 0 });
const datumKortFmt = new Intl.DateTimeFormat('nl-NL', { day: 'numeric', month: 'short', year: 'numeric' });

const isGetal = (n) => typeof n === 'number' && Number.isFinite(n);

/** 12500 -> "€ 12.500" (met vaste spatie). Leeg -> "–". */
export function formatEuro(n) {
  if (!isGetal(n)) return '–';
  return euroFmt.format(Math.round(n));
}

/** 125000 -> "125.000" */
export function formatGetal(n) {
  if (!isGetal(n)) return '';
  return getalFmt.format(Math.round(n));
}

/** 125000 -> "125.000 km" */
export function formatKm(n) {
  if (!isGetal(n)) return '–';
  return `${formatGetal(n)} km`;
}

/**
 * Leest een bedrag of getal dat de gebruiker intypt.
 * "12.500" -> 12500, "€ 12.500,50" -> 12500, "12500" -> 12500, "" -> null.
 * Alleen hele euro's/kilometers; centen worden weggelaten.
 */
export function parseBedrag(invoer) {
  if (invoer === null || invoer === undefined) return null;
  if (typeof invoer === 'number') return isGetal(invoer) ? Math.max(0, Math.round(invoer)) : null;
  const tekst = String(invoer).split(',')[0]; // alles na de komma zijn centen
  const cijfers = tekst.replace(/[^0-9]/g, '');
  if (!cijfers) return null;
  return parseInt(cijfers, 10);
}

/** RDW-datum "20240329" -> "2024-03-29" (of null). */
export function rdwDatumNaarIso(rdw) {
  const s = String(rdw ?? '');
  if (!/^\d{8}$/.test(s)) return null;
  return `${s.slice(0, 4)}-${s.slice(4, 6)}-${s.slice(6, 8)}`;
}

/** "2024-03-29" -> "29-03-2024" */
export function formatIsoDatum(iso) {
  if (!iso || !/^\d{4}-\d{2}-\d{2}/.test(iso)) return '–';
  const [j, m, d] = iso.slice(0, 10).split('-');
  return `${d}-${m}-${j}`;
}

/** Tijdstempel (ms of ISO) -> "8 nov 2026" */
export function formatDatumKort(tijd) {
  if (!tijd) return '–';
  const d = new Date(tijd);
  if (Number.isNaN(d.getTime())) return '–';
  return datumKortFmt.format(d);
}

/** Aantal hele dagen tussen twee tijdstippen. */
export function dagenTussen(van, tot = Date.now()) {
  const a = new Date(van).getTime();
  const b = new Date(tot).getTime();
  if (Number.isNaN(a) || Number.isNaN(b)) return null;
  return Math.floor((b - a) / 86400000);
}

/** Zet RDW-hoofdletters om naar nette tekst: "MERCEDES-BENZ" -> "Mercedes-Benz", "RAV4" blijft "RAV4". */
export function netteNaam(tekst) {
  if (!tekst) return '';
  return String(tekst)
    .trim()
    .split(/\s+/)
    .map((woord) => {
      if (/\d/.test(woord) || woord.length <= 3) return woord.toUpperCase();
      return woord
        .split('-')
        .map((deel) => (deel ? deel[0].toUpperCase() + deel.slice(1).toLowerCase() : deel))
        .join('-');
    })
    .join(' ');
}
