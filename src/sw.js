// Service worker: zorgt dat de app ook zonder internet opent.
// VERSIE en BESTANDEN worden bij het publiceren ingevuld door scripts/build.mjs.

const VERSIE = 'ontwikkel';
const BESTANDEN = ['./', 'index.html'];
const CACHE = `taxatie-${VERSIE}`;

self.addEventListener('install', (event) => {
  event.waitUntil(caches.open(CACHE).then((cache) => cache.addAll(BESTANDEN)));
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((namen) => Promise.all(namen.filter((n) => n.startsWith('taxatie-') && n !== CACHE).map((n) => caches.delete(n))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('message', (event) => {
  if (event.data === 'skipWaiting') self.skipWaiting();
});

self.addEventListener('fetch', (event) => {
  const verzoek = event.request;
  const url = new URL(verzoek.url);
  // Alleen eigen bestanden uit de cache. RDW en andere sites gaan altijd via internet.
  if (verzoek.method !== 'GET' || url.origin !== self.location.origin) return;

  if (verzoek.mode === 'navigate') {
    event.respondWith(
      caches.match(new URL('index.html', self.registration.scope)).then((antwoord) => antwoord || fetch(verzoek))
    );
    return;
  }
  event.respondWith(caches.match(verzoek, { ignoreSearch: true }).then((antwoord) => antwoord || fetch(verzoek)));
});
