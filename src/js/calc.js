// De berekening van het advies-bod.

const getal = (n) => (typeof n === 'number' && Number.isFinite(n) ? n : null);

/** Telt de bedragen van alle schades op. */
export function totaleSchade(schades = []) {
  return schades.reduce((som, s) => som + (getal(s?.bedrag) ?? 0), 0);
}

/**
 * Verwachte verkoopprijs − schade = waarde na schade.
 * Waarde na schade − marge = advies bod.
 * Hoogste bod hoort bij de laagste marge, laagste bod bij de hoogste marge.
 */
export function berekenBod({ verkoopprijs, schades = [], margeMin, margeMax }) {
  const schadeTotaal = totaleSchade(schades);
  const prijs = getal(verkoopprijs);
  let mMin = getal(margeMin) ?? 0;
  let mMax = getal(margeMax) ?? mMin;
  if (mMin > mMax) [mMin, mMax] = [mMax, mMin];

  if (prijs === null) {
    return { compleet: false, schadeTotaal, margeMin: mMin, margeMax: mMax };
  }
  const waardeNaSchade = prijs - schadeTotaal;
  return {
    compleet: true,
    verkoopprijs: prijs,
    schadeTotaal,
    waardeNaSchade,
    margeMin: mMin,
    margeMax: mMax,
    bodHoog: waardeNaSchade - mMin,
    bodLaag: waardeNaSchade - mMax,
  };
}

/**
 * Vergelijkt de vraagprijs met het hoogste bod.
 * 'goed'  = vraagprijs past binnen het bod
 * 'slecht' = vraagprijs ligt boven het hoogste bod
 * null    = niet te bepalen
 */
export function dealSignaal(vraagprijs, bod) {
  const v = getal(vraagprijs);
  if (v === null || !bod?.compleet) return null;
  return v <= bod.bodHoog ? 'goed' : 'slecht';
}
