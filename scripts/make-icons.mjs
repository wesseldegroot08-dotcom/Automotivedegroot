// Maakt de app-iconen (PNG) uit één SVG. Alleen nodig als het icoon verandert:
//   node scripts/make-icons.mjs
// Gebruikt Playwright/Chromium om de SVG scherp te tekenen.

import { createRequire } from 'node:module';
import { writeFileSync } from 'node:fs';
import { join } from 'node:path';

const require = createRequire(import.meta.url);
const { chromium } = require('playwright');

const uit = join(new URL('..', import.meta.url).pathname, 'src', 'icons');

function svg(grootte, schaal) {
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${grootte}" height="${grootte}" viewBox="0 0 1024 1024">
  <rect width="1024" height="1024" fill="#0b0b0c"/>
  <g transform="translate(512 520) scale(${schaal}) translate(-32 -33)" fill="none" stroke="#fff" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round">
    <path d="M12.6 41H9a2 2 0 0 1-2-2v-5a3 3 0 0 1 2.4-2.9L17 29.5l6.2-7.6A4 4 0 0 1 26.3 20.5h11.6a4 4 0 0 1 3 1.4L48 29.5l6.6 1.5A3 3 0 0 1 57 34v5a2 2 0 0 1-2 2h-3.6"/>
    <path d="M23.4 41h17.2"/>
    <path d="M17 29.5h31"/>
    <path d="M32 20.8v8.7"/>
    <circle cx="18" cy="41" r="5"/>
    <circle cx="46" cy="41" r="5"/>
  </g>
</svg>`;
}

const ICONEN = [
  { naam: 'apple-touch-icon.png', grootte: 180, schaal: 13 },
  { naam: 'icon-192.png', grootte: 192, schaal: 13 },
  { naam: 'icon-512.png', grootte: 512, schaal: 13 },
  { naam: 'icon-maskable-512.png', grootte: 512, schaal: 10.5 },
];

const browser = await chromium.launch();
const pagina = await browser.newPage();
for (const i of ICONEN) {
  await pagina.setViewportSize({ width: i.grootte, height: i.grootte });
  await pagina.setContent(`<html><body style="margin:0">${svg(i.grootte, i.schaal)}</body></html>`);
  const png = await pagina.locator('svg').screenshot({ type: 'png' });
  writeFileSync(join(uit, i.naam), png);
  console.log('gemaakt:', i.naam);
}
await browser.close();
