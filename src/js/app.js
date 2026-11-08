// Start van de app: tabbladen, navigatie en offline-ondersteuning.

import { h, leeg, icoon, toast } from './ui.js';
import { vraagBlijvendeOpslag } from './db.js';
import { toonTaxeren } from './views/taxeren.js';
import { toonArchief } from './views/archief.js';
import { toonInstellingen } from './views/instellingen.js';

const main = document.getElementById('app');
const TABS = [
  { key: 'taxeren', label: 'Taxeren', icoon: 'taxeren' },
  { key: 'archief', label: 'Archief', icoon: 'archief' },
  { key: 'instellingen', label: 'Instellingen', icoon: 'instellingen' },
];
const SCHERMEN = { taxeren: toonTaxeren, archief: toonArchief, instellingen: toonInstellingen };

// ---------- onderbalk ----------
const tabKnoppen = TABS.map((t) =>
  h('a', { class: 'tab', href: `#/${t.key}`, 'data-tab': t.key }, icoon(t.icoon), h('span', {}, t.label))
);
document.getElementById('tabbar').replaceChildren(...tabKnoppen);

// ---------- navigatie ----------
let opruimen = null;
let bezig = 0;

function leesRoute() {
  const [scherm, id] = location.hash.replace(/^#\/?/, '').split('/');
  return { scherm: SCHERMEN[scherm] ? scherm : 'taxeren', id: id ? decodeURIComponent(id) : null };
}

async function toon() {
  const nr = ++bezig;
  const { scherm, id } = leesRoute();
  tabKnoppen.forEach((k) => {
    const actief = k.dataset.tab === scherm;
    k.classList.toggle('actief', actief);
    if (actief) k.setAttribute('aria-current', 'page');
    else k.removeAttribute('aria-current');
  });

  try {
    await opruimen?.();
  } catch (e) {
    console.error(e);
  }
  opruimen = null;
  if (nr !== bezig) return;

  const inhoud = h('div', { class: 'scherm' });
  try {
    const klaar = await SCHERMEN[scherm](inhoud, { id, herlaad: toon });
    if (nr !== bezig) {
      klaar?.();
      return;
    }
    opruimen = klaar;
    leeg(main, inhoud);
    window.scrollTo(0, 0);
  } catch (e) {
    console.error(e);
    leeg(
      main,
      h(
        'div',
        { class: 'scherm' },
        h('header', { class: 'pagina-kop' }, h('h1', {}, 'Oeps')),
        h('div', { class: 'kaart' }, h('p', {}, 'Er ging iets mis bij het openen van dit scherm.'), h('p', { class: 'klein' }, String(e?.message ?? e)))
      )
    );
  }
}

window.addEventListener('hashchange', toon);
if (!location.hash) history.replaceState(null, '', '#/taxeren');
toon();

// Tik op het actieve tabblad = terug naar boven.
tabKnoppen.forEach((k) =>
  k.addEventListener('click', () => {
    if (k.classList.contains('actief') && location.hash === `#/${k.dataset.tab}`) window.scrollTo({ top: 0, behavior: 'smooth' });
  })
);

// ---------- blijvende opslag ----------
vraagBlijvendeOpslag();

// ---------- offline & updates ----------
if ('serviceWorker' in navigator && window.isSecureContext) {
  // Alleen herladen als de gebruiker zelf op "bijwerken" tikt
  // (niet bij de allereerste installatie).
  let updateGevraagd = false;

  navigator.serviceWorker
    .register('sw.js')
    .then((reg) => {
      if (!reg) return;
      let balk = null;
      const toonUpdate = (worker) => {
        if (balk) return;
        balk = h(
          'button',
          {
            type: 'button',
            class: 'update-balk',
            onClick: () => {
              updateGevraagd = true;
              balk.textContent = 'Bijwerken…';
              worker.postMessage('skipWaiting');
            },
          },
          'Nieuwe versie beschikbaar · ',
          h('strong', {}, 'Tik om bij te werken')
        );
        document.body.append(balk);
      };
      if (reg.waiting && navigator.serviceWorker.controller) toonUpdate(reg.waiting);
      reg.addEventListener('updatefound', () => {
        const nieuw = reg.installing;
        nieuw?.addEventListener('statechange', () => {
          if (nieuw.state === 'installed' && navigator.serviceWorker.controller) toonUpdate(nieuw);
        });
      });
      document.addEventListener('visibilitychange', () => document.visibilityState === 'visible' && reg.update().catch(() => {}));
    })
    .catch((e) => console.warn('Offline-ondersteuning niet beschikbaar:', e));

  navigator.serviceWorker.addEventListener('controllerchange', () => {
    if (!updateGevraagd) return;
    updateGevraagd = false;
    location.reload();
  });
}

window.addEventListener('unhandledrejection', (e) => {
  console.error(e.reason);
  if (e.reason?.name === 'QuotaExceededError') toast('Je telefoon heeft geen ruimte meer voor nieuwe gegevens.', 'fout');
});
