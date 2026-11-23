// Scherm: Archief (alle getaxeerde auto's).

import { h, leeg, icoon, leesLokaal, schrijfLokaal } from '../ui.js';
import { archief, haalFoto, naamVan, bouwjaarVan } from '../db.js';
import { formatEuro, formatKm, formatDatumKort, dagenTussen } from '../format.js';
import { formatKenteken, normaliseerKenteken } from '../kenteken.js';
import { fotoUrl } from '../images.js';
import { laatsteBackup } from '../backup.js';
import { BACKUP_HERINNERING_DAGEN } from '../constants.js';

const SORTERINGEN = [
  { key: 'datum-nieuw', label: 'Nieuwste eerst' },
  { key: 'datum-oud', label: 'Oudste eerst' },
  { key: 'bod-hoog', label: 'Hoogste bod eerst' },
  { key: 'bod-laag', label: 'Laagste bod eerst' },
];

function sorteer(lijst, key) {
  const datum = (a) => a.getaxeerdOp ?? a.aangemaakt ?? 0;
  const bod = (a) => a.bodHoog;
  const metBod = (f, richting) => (a, b) => {
    // Auto's zonder bod altijd onderaan
    if (bod(a) === null && bod(b) === null) return datum(b) - datum(a);
    if (bod(a) === null) return 1;
    if (bod(b) === null) return -1;
    return richting * (f(a) - f(b));
  };
  const kopie = [...lijst];
  if (key === 'datum-oud') return kopie.sort((a, b) => datum(a) - datum(b));
  if (key === 'bod-hoog') return kopie.sort(metBod(bod, -1));
  if (key === 'bod-laag') return kopie.sort(metBod(bod, 1));
  return kopie.sort((a, b) => datum(b) - datum(a));
}

function past(auto, zoek) {
  if (!zoek) return true;
  const z = zoek.toLowerCase().trim();
  const zKenteken = normaliseerKenteken(zoek);
  if (zKenteken && (auto.kenteken ?? '').includes(zKenteken)) return true;
  const tekst = [naamVan(auto), auto.uitvoering].filter(Boolean).join(' ').toLowerCase();
  return z.split(/\s+/).every((woord) => tekst.includes(woord));
}

export async function toonArchief(root) {
  const [autos, laatste] = await Promise.all([archief(), laatsteBackup()]);
  const urls = [];
  let zoek = '';
  let sortering = leesLokaal('sortering') ?? 'datum-nieuw';

  const lijst = h('div', { class: 'archief-lijst' });
  const teller = h('p', { class: 'pagina-sub' });

  const zoekveld = h('input', {
    type: 'search',
    placeholder: 'Zoek op kenteken, merk of model',
    autocomplete: 'off',
    autocorrect: 'off',
    enterkeyhint: 'search',
    'aria-label': 'Zoeken',
  });
  zoekveld.addEventListener('input', () => {
    zoek = zoekveld.value;
    teken();
  });
  zoekveld.addEventListener('keydown', (e) => e.key === 'Enter' && zoekveld.blur());

  const sorteerKeuze = h(
    'select',
    { class: 'sorteer', 'aria-label': 'Sorteren' },
    SORTERINGEN.map((s) => h('option', { value: s.key, selected: s.key === sortering }, s.label))
  );
  sorteerKeuze.addEventListener('change', () => {
    sortering = sorteerKeuze.value;
    schrijfLokaal('sortering', sortering);
    teken();
  });

  // Seintje als de laatste back-up te lang geleden is.
  let backupSein = null;
  const dagen = laatste ? dagenTussen(laatste) : null;
  if (autos.length && (dagen === null || dagen > BACKUP_HERINNERING_DAGEN)) {
    backupSein = h(
      'a',
      { class: 'melding rood link', href: '#instellingen' },
      icoon('let_op', 'inline'),
      dagen === null ? ' Je hebt nog nooit een back-up gemaakt. ' : ` Laatste back-up is ${dagen} dagen geleden. `,
      h('strong', {}, 'Maak een back-up')
    );
  }

  function item(auto) {
    const thumb = h('div', { class: 'thumb' }, icoon('auto'));
    const eersteFoto = auto.fotoIds?.[0];
    if (eersteFoto) {
      haalFoto(eersteFoto).then((foto) => {
        if (!foto) return;
        const url = fotoUrl(foto, 'klein');
        urls.push(url);
        leeg(thumb, h('img', { src: url, alt: '', decoding: 'async' }));
      });
    }
    const titel = naamVan(auto) || 'Onbekende auto';
    const regel = [bouwjaarVan(auto), auto.km !== null && auto.km !== undefined ? formatKm(auto.km) : null, auto.uitvoering || null].filter(Boolean).join(' · ');
    const bod = auto.bodHoog !== null && auto.bodHoog !== undefined ? `${formatEuro(auto.bodLaag)} – ${formatEuro(auto.bodHoog)}` : 'Geen bod';

    return h(
      'a',
      { class: 'archief-item', href: `#auto-${auto.id}` },
      thumb,
      h(
        'div',
        { class: 'archief-info' },
        h('div', { class: 'archief-titel-rij' }, h('h3', {}, titel), auto.kenteken ? h('span', { class: 'kenteken-klein' }, formatKenteken(auto.kenteken)) : null),
        regel ? h('p', { class: 'archief-regel' }, regel) : null,
        h('div', { class: 'archief-onder' }, h('span', { class: 'archief-datum' }, formatDatumKort(auto.getaxeerdOp)), h('strong', { class: 'archief-bod' }, bod))
      )
    );
  }

  function teken() {
    const gefilterd = sorteer(autos.filter((a) => past(a, zoek)), sortering);
    teller.textContent = autos.length === 1 ? '1 auto' : `${autos.length} auto's`;
    if (!autos.length) {
      leeg(
        lijst,
        h(
          'div',
          { class: 'kaart leeg-staat' },
          icoon('archief', 'groot'),
          h('h2', {}, 'Nog geen taxaties'),
          h('p', {}, 'Taxeer een auto en tik op “Opslaan in archief”. Dan staat hij hier.'),
          h('a', { class: 'knop', href: '#taxeren' }, 'Naar taxeren')
        )
      );
      return;
    }
    leeg(lijst, gefilterd.length ? gefilterd.map(item) : h('p', { class: 'leeg-tekst midden' }, `Niets gevonden voor “${zoek}”.`));
  }

  leeg(
    root,
    h('header', { class: 'pagina-kop' }, h('h1', {}, 'Archief'), teller),
    backupSein,
    autos.length ? h('div', { class: 'zoek-rij' }, h('div', { class: 'zoekveld' }, icoon('zoek'), zoekveld), sorteerKeuze) : null,
    lijst
  );
  teken();

  return () => urls.forEach((u) => URL.revokeObjectURL(u));
}
