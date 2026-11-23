// Kentekens: invoer opschonen en weergeven met streepjes (Nederlandse sidecodes).

/** "52-bdv-4" of "52 BDV 4" -> "52BDV4" */
export function normaliseerKenteken(invoer) {
  return String(invoer ?? '')
    .toUpperCase()
    .replace(/[^A-Z0-9]/g, '');
}

// Patroon (L = letter, C = cijfer) en de groepsgroottes van de Nederlandse sidecodes 1 t/m 14.
const SIDECODES = [
  ['LLCCCC', [2, 2, 2]], // 1  XX-99-99
  ['CCCCLL', [2, 2, 2]], // 2  99-99-XX
  ['CCLLCC', [2, 2, 2]], // 3  99-XX-99
  ['LLCCLL', [2, 2, 2]], // 4  XX-99-XX
  ['LLLLCC', [2, 2, 2]], // 5  XX-XX-99
  ['CCLLLL', [2, 2, 2]], // 6  99-XX-XX
  ['CCLLLC', [2, 3, 1]], // 7  99-XXX-9
  ['CLLLCC', [1, 3, 2]], // 8  9-XXX-99
  ['LLCCCL', [2, 3, 1]], // 9  XX-999-X
  ['LCCCLL', [1, 3, 2]], // 10 X-999-XX
  ['LLLCCL', [3, 2, 1]], // 11 XXX-99-X
  ['LCCLLL', [1, 2, 3]], // 12 X-99-XXX
  ['CLLCCC', [1, 2, 3]], // 13 9-XX-999
  ['CCCLLC', [3, 2, 1]], // 14 999-XX-9
];

function patroon(k) {
  return k.replace(/[A-Z]/g, 'L').replace(/[0-9]/g, 'C');
}

/** "52BDV4" -> "52-BDV-4". Onbekend patroon -> zonder streepjes. */
export function formatKenteken(invoer) {
  const k = normaliseerKenteken(invoer);
  if (k.length !== 6) return k;
  const p = patroon(k);
  const match = SIDECODES.find(([sc]) => sc === p);
  if (!match) return k;
  const [a, b] = match[1];
  return `${k.slice(0, a)}-${k.slice(a, a + b)}-${k.slice(a + b)}`;
}

/** Ziet dit eruit als een Nederlands kenteken? (6 tekens, bekend patroon) */
export function isGeldigKenteken(invoer) {
  const k = normaliseerKenteken(invoer);
  return k.length === 6 && SIDECODES.some(([sc]) => sc === patroon(k));
}
