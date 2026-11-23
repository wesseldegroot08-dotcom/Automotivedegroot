// Vaste lijsten van de app.

export const SCHADE_TYPES = [
  { key: 'kras', label: 'Kras' },
  { key: 'deuk', label: 'Deuk' },
  { key: 'velg', label: 'Velg / stoeprandschade' },
  { key: 'ruit', label: 'Ruit / sterretje' },
  { key: 'bumper', label: 'Bumper' },
  { key: 'lak', label: 'Lak / roest' },
  { key: 'interieur', label: 'Interieur' },
  { key: 'banden', label: 'Banden' },
  { key: 'techniek', label: 'Techniek / motor' },
  { key: 'anders', label: 'Anders' },
];

export const OPTIES = [
  { key: 'navigatie', label: 'Navigatie' },
  { key: 'panoramadak', label: 'Panoramadak' },
  { key: 'leder', label: 'Leder' },
  { key: 'cruise', label: 'Cruise control' },
  { key: 'acc', label: 'Adaptieve cruise control' },
  { key: 'trekhaak', label: 'Trekhaak' },
  { key: 'camera', label: 'Achteruitrijcamera' },
  { key: 'stoelverwarming', label: 'Stoelverwarming' },
  { key: 'led', label: 'LED / xenon' },
  { key: 'parkeersensoren', label: 'Parkeersensoren' },
  { key: 'carplay', label: 'Apple CarPlay / Android Auto' },
];

export const TRANSMISSIES = [
  { key: 'handgeschakeld', label: 'Handgeschakeld' },
  { key: 'automaat', label: 'Automaat' },
];

export const schadeLabel = (key) => SCHADE_TYPES.find((t) => t.key === key)?.label ?? 'Schade';
export const optieLabel = (key) => OPTIES.find((o) => o.key === key)?.label ?? key;

// Standaardbedragen per schadetype beginnen op € 0: de gebruiker vult ze zelf in.
export const STANDAARD_INSTELLINGEN = {
  margeMin: 1500,
  margeMax: 2000,
  schadeStandaard: Object.fromEntries(SCHADE_TYPES.map((t) => [t.key, 0])),
};

export const BACKUP_HERINNERING_DAGEN = 14;
