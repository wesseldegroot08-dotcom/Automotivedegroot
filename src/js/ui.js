// Kleine hulpfuncties voor de schermen: elementen maken, meldingen, vragen.

import { formatGetal, parseBedrag } from './format.js';

const PROPS = new Set(['value', 'checked', 'disabled', 'selected', 'hidden']);

/** Maakt een element: h('button', { class: 'knop', onClick }, 'Tekst') */
export function h(tag, props = {}, ...kinderen) {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(props ?? {})) {
    if (v === null || v === undefined || v === false) continue;
    if (k === 'class') el.className = v;
    else if (k.startsWith('on') && typeof v === 'function') el.addEventListener(k.slice(2).toLowerCase(), v);
    else if (PROPS.has(k)) el[k] = v;
    else el.setAttribute(k, v === true ? '' : String(v));
  }
  voegToe(el, kinderen);
  return el;
}

function voegToe(el, kinderen) {
  for (const kind of kinderen.flat(Infinity)) {
    if (kind === null || kind === undefined || kind === false) continue;
    el.append(kind instanceof Node ? kind : document.createTextNode(String(kind)));
  }
}

export function leeg(el, ...kinderen) {
  el.replaceChildren();
  voegToe(el, kinderen);
  return el;
}

// ---------- iconen (eigen, eenvoudige lijn-iconen) ----------

const PADEN = {
  taxeren:
    '<rect x="5" y="3" width="14" height="18" rx="2.5"/><path d="M8.5 7.5h7"/><circle cx="9" cy="12" r="1" fill="currentColor" stroke="none"/><circle cx="12" cy="12" r="1" fill="currentColor" stroke="none"/><circle cx="15" cy="12" r="1" fill="currentColor" stroke="none"/><circle cx="9" cy="16" r="1" fill="currentColor" stroke="none"/><circle cx="12" cy="16" r="1" fill="currentColor" stroke="none"/><circle cx="15" cy="16" r="1" fill="currentColor" stroke="none"/>',
  archief: '<rect x="3" y="4" width="18" height="4.5" rx="1.2"/><path d="M5 8.5V19a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V8.5"/><path d="M10 12.5h4"/>',
  instellingen:
    '<path d="M4 7h9"/><path d="M17 7h3"/><circle cx="15" cy="7" r="2"/><path d="M4 17h3"/><path d="M11 17h9"/><circle cx="9" cy="17" r="2"/>',
  plus: '<path d="M12 5v14"/><path d="M5 12h14"/>',
  sluit: '<path d="M6 6l12 12"/><path d="M18 6L6 18"/>',
  links: '<path d="M15 18l-6-6 6-6"/>',
  rechts: '<path d="M9 6l6 6-6 6"/>',
  prullenbak:
    '<path d="M4 7h16"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M6 7l1 12a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2l1-12"/><path d="M9 7V4.5h6V7"/>',
  camera:
    '<path d="M4 8h3l1.6-2.4A1.5 1.5 0 0 1 9.9 5h4.2a1.5 1.5 0 0 1 1.3.6L17 8h3a1 1 0 0 1 1 1v10a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V9a1 1 0 0 1 1-1z"/><circle cx="12" cy="13.5" r="3.5"/>',
  extern: '<path d="M14 4h6v6"/><path d="M20 4l-9 9"/><path d="M18 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h5"/>',
  zoek: '<circle cx="11" cy="11" r="6.5"/><path d="M20 20l-4.2-4.2"/>',
  auto:
    '<path d="M3.5 16.5v-3.2a2 2 0 0 1 .6-1.4L6 10l1.8-3.4A2 2 0 0 1 9.6 5.5h4.8a2 2 0 0 1 1.8 1.1L18 10l1.9 1.9a2 2 0 0 1 .6 1.4v3.2"/><path d="M6 10h12"/><rect x="3.5" y="16" width="17" height="2.5" rx="1"/><circle cx="7.5" cy="13.5" r="1" fill="currentColor" stroke="none"/><circle cx="16.5" cy="13.5" r="1" fill="currentColor" stroke="none"/>',
  let_op: '<path d="M12 4l9 16H3z"/><path d="M12 10v4"/><circle cx="12" cy="17" r="1" fill="currentColor" stroke="none"/>',
  vink: '<path d="M5 12.5l4.5 4.5L19 7.5"/>',
  deel: '<path d="M12 3v12"/><path d="M8 7l4-4 4 4"/><path d="M6 11H5a1 1 0 0 0-1 1v8a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-8a1 1 0 0 0-1-1h-1"/>',
};

export function icoon(naam, klasse = '') {
  const span = document.createElement('span');
  span.className = `icoon ${klasse}`.trim();
  span.setAttribute('aria-hidden', 'true');
  span.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">${PADEN[naam] ?? ''}</svg>`;
  return span;
}

// ---------- invoervelden ----------

/** Invoerveld voor bedragen of kilometers: toont "12.500", bewaart 12500. */
export function getalVeld({ waarde, onWijzig, voorvoegsel = null, achtervoegsel = null, placeholder = '', id, label }) {
  const input = h('input', {
    id,
    type: 'text',
    inputmode: 'numeric',
    autocomplete: 'off',
    enterkeyhint: 'done',
    placeholder,
    'aria-label': label,
    value: waarde === null || waarde === undefined ? '' : formatGetal(waarde),
  });
  input.addEventListener('input', () => {
    const getal = parseBedrag(input.value);
    // Live opmaak met punten, cursor naar het einde.
    const nieuw = getal === null ? '' : formatGetal(getal);
    if (input.value !== nieuw) input.value = nieuw;
    onWijzig(getal);
  });
  input.addEventListener('focus', () => setTimeout(() => input.select?.(), 0));
  return h(
    'div',
    { class: 'veld-getal' },
    voorvoegsel ? h('span', { class: 'voor' }, voorvoegsel) : null,
    input,
    achtervoegsel ? h('span', { class: 'na' }, achtervoegsel) : null
  );
}

export function veld(labelTekst, invoer, hulp = null) {
  return h('label', { class: 'veld' }, h('span', { class: 'veld-label' }, labelTekst), invoer, hulp ? h('span', { class: 'veld-hulp' }, hulp) : null);
}

/** Groeiend tekstvak. */
export function tekstvak(props) {
  const ta = h('textarea', { rows: 3, ...props });
  const pas = () => {
    ta.style.height = 'auto';
    ta.style.height = `${ta.scrollHeight + 2}px`;
  };
  ta.addEventListener('input', pas);
  requestAnimationFrame(pas);
  return ta;
}

/** Keuzeknoppen naast elkaar (bijv. Handgeschakeld / Automaat). */
export function segmenten(opties, gekozen, onKies) {
  const knoppen = opties.map((o) =>
    h(
      'button',
      {
        type: 'button',
        class: `segment${o.key === gekozen ? ' aan' : ''}`,
        'aria-pressed': String(o.key === gekozen),
        onClick: () => {
          const nieuw = o.key === gekozen ? null : o.key; // nogmaals tikken = wissen
          gekozen = nieuw;
          knoppen.forEach((k, i) => {
            const aan = opties[i].key === nieuw;
            k.classList.toggle('aan', aan);
            k.setAttribute('aria-pressed', String(aan));
          });
          onKies(nieuw);
        },
      },
      o.label
    )
  );
  return h('div', { class: 'segmenten', role: 'group' }, knoppen);
}

// ---------- meldingen ----------

let toastTimer;
export function toast(tekst, soort = '') {
  let el = document.querySelector('.toast');
  if (!el) {
    el = h('div', { class: 'toast', role: 'status', 'aria-live': 'polite' });
    document.body.append(el);
  }
  el.className = `toast ${soort}`.trim();
  el.textContent = tekst;
  requestAnimationFrame(() => el.classList.add('zichtbaar'));
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => el.classList.remove('zichtbaar'), 2600);
}

/** Paneel dat van onderen inschuift. Geeft een functie terug om het te sluiten. */
export function paneel(inhoud, { onSluit } = {}) {
  const achtergrond = h('div', { class: 'paneel-achtergrond' });
  const vel = h('div', { class: 'paneel', role: 'dialog', 'aria-modal': 'true' }, h('div', { class: 'paneel-greep' }), inhoud);
  const laag = h('div', { class: 'paneel-laag' }, achtergrond, vel);
  let gesloten = false;
  const sluit = () => {
    if (gesloten) return;
    gesloten = true;
    laag.classList.remove('open');
    setTimeout(() => laag.remove(), 250);
    onSluit?.();
  };
  achtergrond.addEventListener('click', sluit);
  document.body.append(laag);
  requestAnimationFrame(() => requestAnimationFrame(() => laag.classList.add('open')));
  return sluit;
}

/** Vraagt bevestiging. Geeft true of false terug. */
export function bevestig({ titel, tekst = '', ja = 'Ja', nee = 'Annuleren', gevaar = false }) {
  return new Promise((resolve) => {
    let antwoord = false;
    const sluit = paneel(
      h(
        'div',
        { class: 'bevestig' },
        h('h2', {}, titel),
        tekst ? h('p', {}, tekst) : null,
        h('button', { type: 'button', class: `knop ${gevaar ? 'knop-gevaar' : ''}`, onClick: () => ((antwoord = true), sluit()) }, ja),
        h('button', { type: 'button', class: 'knop knop-licht', onClick: () => sluit() }, nee)
      ),
      { onSluit: () => resolve(antwoord) }
    );
  });
}

/** Wacht met opslaan tot er even niet getypt wordt; flush() slaat direct op. */
export function vertraagd(fn, ms = 400) {
  let timer = null;
  const uitvoeren = () => {
    clearTimeout(timer);
    timer = null;
    return fn();
  };
  const wrapper = () => {
    clearTimeout(timer);
    timer = setTimeout(uitvoeren, ms);
  };
  wrapper.flush = () => (timer ? uitvoeren() : undefined);
  return wrapper;
}

export function isStandalone() {
  return window.matchMedia?.('(display-mode: standalone)').matches || window.navigator.standalone === true;
}

// ---------- kleine voorkeuren (alleen op dit toestel, mag mislukken) ----------

export function leesLokaal(sleutel) {
  try {
    return localStorage.getItem(`taxatie:${sleutel}`);
  } catch {
    return null;
  }
}

export function schrijfLokaal(sleutel, waarde) {
  try {
    localStorage.setItem(`taxatie:${sleutel}`, waarde);
  } catch {
    /* niet erg */
  }
}
