// Test de hele app in een browser die zich voordoet als iPhone.
// Gebruik: npm run build && node scripts/serve.mjs 8080 &  dan  node scripts/e2e.mjs [kenteken]
// Let op: het opzoeken van het kenteken gebruikt echte RDW-gegevens (internet nodig).

import { createRequire } from 'node:module';
import { mkdirSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import assert from 'node:assert/strict';

const require = createRequire(import.meta.url);
const { chromium, devices } = require('playwright');

const BASIS = process.env.APP_URL ?? 'http://localhost:8080/';
const KENTEKEN = process.argv[2] ?? 'Z-174-GK';
const UIT = process.env.SCREENSHOTS ?? join(new URL('..', import.meta.url).pathname, 'test-results');
mkdirSync(UIT, { recursive: true });

// Klein test-JPEG (effen grijs), gemaakt zonder extra pakketten via de browser zelf.
async function maakTestFoto(pagina) {
  const base64 = await pagina.evaluate(() => {
    const c = document.createElement('canvas');
    c.width = 3000;
    c.height = 2000;
    const ctx = c.getContext('2d');
    ctx.fillStyle = '#888';
    ctx.fillRect(0, 0, 3000, 2000);
    ctx.fillStyle = '#222';
    ctx.fillRect(500, 500, 2000, 1000);
    return c.toDataURL('image/jpeg', 0.9).split(',')[1];
  });
  return { name: 'auto.jpg', mimeType: 'image/jpeg', buffer: Buffer.from(base64, 'base64') };
}

const tekst = (s) => s.replace(/ /g, ' ').trim();
const fouten = [];

const browser = await chromium.launch();
const context = await browser.newContext({ ...devices['iPhone 15'], acceptDownloads: true, serviceWorkers: 'allow' });
const pagina = await context.newPage();
pagina.on('pageerror', (e) => fouten.push(`pageerror: ${e.message}`));
pagina.on('console', (m) => m.type() === 'error' && fouten.push(`console: ${m.text()}`));

const stap = (naam) => console.log(`• ${naam}`);

try {
  stap('App openen');
  await pagina.goto(BASIS);
  await pagina.getByRole('heading', { name: 'Taxeren', level: 1 }).waitFor();
  await pagina.screenshot({ path: join(UIT, '01-leeg.png'), fullPage: false });

  stap(`Kenteken ${KENTEKEN} opzoeken bij RDW`);
  await pagina.getByLabel('Kenteken').fill(KENTEKEN.toLowerCase());
  await pagina.getByRole('button', { name: 'Check kenteken' }).click();
  await pagina.locator('.rdw-titel h3').waitFor({ timeout: 20000 });
  console.log('   RDW:', tekst(await pagina.locator('.rdw-titel').innerText()), '|', tekst(await pagina.locator('.tellerstand-kop').innerText()));
  await pagina.screenshot({ path: join(UIT, '02-rdw.png'), fullPage: false });

  stap('Onbekend kenteken geeft nette melding');
  await pagina.getByLabel('Kenteken').fill('QQ-999-Q');
  await pagina.getByRole('button', { name: 'Check kenteken' }).click();
  await pagina.locator('.melding.rood[role=alert]').waitFor({ state: 'visible', timeout: 20000 });
  console.log('   Melding:', await pagina.locator('.melding.rood[role=alert]').innerText());
  await pagina.getByLabel('Kenteken').fill(KENTEKEN);
  await pagina.getByRole('button', { name: 'Check kenteken' }).click();
  await pagina.locator('.melding.rood[role=alert]').waitFor({ state: 'hidden', timeout: 20000 });

  stap('Auto-gegevens en opties invullen');
  await pagina.locator('.veld', { hasText: 'Kilometerstand' }).locator('input').fill('125000');
  assert.equal(await pagina.locator('.veld', { hasText: 'Kilometerstand' }).locator('input').inputValue(), '125.000');
  await pagina.getByPlaceholder('bijv. 1.5 TSI Highline').fill('2.5 Plug-in Hybrid Style');
  await pagina.getByRole('button', { name: 'Automaat' }).click();
  await pagina.getByRole('button', { name: 'Panoramadak' }).click();
  await pagina.getByRole('button', { name: 'Trekhaak' }).click();
  await pagina.getByPlaceholder('Plak hier de link').fill('https://www.gaspedaal.nl/voorbeeld');

  stap('Foto toevoegen (wordt verkleind)');
  const foto = await maakTestFoto(pagina);
  await pagina.locator('section', { has: pagina.getByRole('heading', { name: "Foto's" }) }).locator('input[type=file]').setInputFiles(foto);
  await pagina.locator('section', { has: pagina.getByRole('heading', { name: "Foto's" }) }).locator('.foto-tegel img').first().waitFor();
  const afmeting = await pagina.evaluate(async () => {
    const { db } = await import('./js/db.js');
    const f = (await db.fotos.toArray())[0];
    return { b: f.breedte, h: f.hoogte, kb: Math.round(f.groot.byteLength / 1024) };
  });
  console.log(`   Opgeslagen foto: ${afmeting.b}×${afmeting.h}, ${afmeting.kb} kB`);
  assert.equal(Math.max(afmeting.b, afmeting.h), 1600);

  stap('Schade toevoegen (2×) en bedragen invullen');
  for (const [soort, bedrag] of [
    ['Kras', '400'],
    ['Velg / stoeprandschade', '200'],
  ]) {
    await pagina.getByRole('button', { name: 'Schade toevoegen' }).click();
    await pagina.locator('.keuze-knop', { hasText: soort }).click();
    await pagina.locator('.paneel-laag').waitFor({ state: 'detached' });
    await pagina.locator('.schade-item').last().locator('.veld', { hasText: 'Bedrag' }).locator('input').fill(bedrag);
  }
  assert.equal(tekst(await pagina.locator('.totaal-rij strong').innerText()), '€ 600');

  stap('Verkoopprijs → advies bod (voorbeeld uit het plan)');
  await pagina.getByLabel('Verwachte verkoopprijs').fill('12000');
  const bedragen = (await pagina.locator('.res-bod-bedrag').allInnerTexts()).map(tekst);
  console.log('   Advies bod:', bedragen.join(' – '));
  assert.deepEqual(bedragen, ['€ 9.400', '€ 9.900']);

  await pagina.locator('.veld', { hasText: 'Vraagprijs' }).locator('input').fill('10500');
  console.log('   Deal:', tekst(await pagina.locator('.deal').innerText()));
  await pagina.locator('.resultaat').scrollIntoViewIfNeeded();
  await pagina.screenshot({ path: join(UIT, '03-resultaat.png'), fullPage: false });
  await pagina.screenshot({ path: join(UIT, '04-taxeren-volledig.png'), fullPage: true });

  stap('Herladen: concept blijft bewaard');
  await pagina.waitForTimeout(600);
  await pagina.reload();
  await pagina.locator('.res-bod-bedrag').first().waitFor();
  assert.equal(await pagina.locator('.veld', { hasText: 'Kilometerstand' }).locator('input').inputValue(), '125.000');
  assert.equal(await pagina.locator('.schade-item').count(), 2);

  stap('Opslaan in archief');
  await pagina.getByRole('button', { name: 'Opslaan in archief' }).click();
  await pagina.getByRole('heading', { name: 'Archief', level: 1 }).waitFor();
  await pagina.locator('.archief-item').first().waitFor();
  console.log('   Archief-item:', tekst(await pagina.locator('.archief-item').first().innerText()).replace(/\n/g, ' | '));
  await pagina.waitForTimeout(300);
  await pagina.screenshot({ path: join(UIT, '05-archief.png'), fullPage: false });

  stap('Zoeken in archief');
  await pagina.getByLabel('Zoeken').fill('zzzz');
  assert.equal(await pagina.locator('.archief-item').count(), 0);
  await pagina.getByLabel('Zoeken').fill(KENTEKEN.slice(0, 3));
  assert.equal(await pagina.locator('.archief-item').count(), 1);

  stap('Nieuw taxatieformulier is leeg');
  await pagina.getByRole('link', { name: 'Taxeren' }).click();
  await pagina.getByRole('heading', { name: 'Taxeren', level: 1 }).waitFor();
  assert.equal(await pagina.getByLabel('Kenteken').inputValue(), '');

  stap('Instellingen: marge wijzigen en back-up maken');
  await pagina.getByRole('link', { name: 'Instellingen' }).click();
  await pagina.getByRole('heading', { name: 'Instellingen', level: 1 }).waitFor();
  await pagina.screenshot({ path: join(UIT, '06-instellingen.png'), fullPage: false });
  await pagina.locator('.lijst-veld', { hasText: 'Kras' }).locator('input').fill('150');
  const downloadBelofte = pagina.waitForEvent('download');
  await pagina.getByRole('button', { name: 'Exporteer alles' }).click();
  await pagina.getByRole('button', { name: 'Bewaar back-up' }).click();
  const download = await downloadBelofte;
  const backupPad = join(UIT, download.suggestedFilename());
  await download.saveAs(backupPad);
  console.log('   Back-up:', download.suggestedFilename());
  await pagina.locator('.melding.groen', { hasText: 'vandaag' }).waitFor();

  stap('Archief-item openen en verwijderen');
  await pagina.getByRole('link', { name: 'Archief' }).click();
  await pagina.locator('.archief-item').first().click();
  await pagina.getByRole('heading', { name: 'Bewerken' }).waitFor();
  await pagina.getByRole('button', { name: 'Verwijderen' }).last().click();
  await pagina.locator('.paneel').getByRole('button', { name: 'Verwijderen' }).click();
  await pagina.getByRole('heading', { name: 'Archief', level: 1 }).waitFor();
  await pagina.locator('.leeg-staat').waitFor();

  stap('Back-up terugzetten');
  await pagina.getByRole('link', { name: 'Instellingen' }).click();
  await pagina.locator('input[type=file][accept*=zip]').setInputFiles(backupPad);
  await pagina.locator('.paneel').getByRole('button', { name: 'Terugzetten' }).click();
  await pagina.getByRole('link', { name: 'Archief' }).click();
  await pagina.locator('.archief-item').first().waitFor();
  const fotoAantal = await pagina.evaluate(async () => (await import('./js/db.js')).db.fotos.count());
  assert.equal(fotoAantal, 1);
  console.log('   Teruggezet: 1 auto met foto');

  stap('Offline openen (service worker)');
  await pagina.evaluate(() => navigator.serviceWorker.ready);
  await pagina.reload();
  await pagina.waitForTimeout(500);
  await context.setOffline(true);
  await pagina.reload();
  await pagina.getByRole('heading', { name: 'Archief', level: 1 }).waitFor();
  console.log('   Offline geopend: ja');
  await context.setOffline(false);

  stap('Smal scherm (iPhone SE)');
  const se = await browser.newContext({ ...devices['iPhone SE'] });
  const sePagina = await se.newPage();
  await sePagina.goto(BASIS + '#/taxeren');
  await sePagina.getByRole('heading', { name: 'Taxeren', level: 1 }).waitFor();
  const breedte = await sePagina.evaluate(() => document.documentElement.scrollWidth);
  assert.ok(breedte <= 375, `pagina is te breed: ${breedte}px`);
  await se.close();
} catch (e) {
  await pagina.screenshot({ path: join(UIT, 'fout.png'), fullPage: true }).catch(() => {});
  console.error('\nTEST MISLUKT:', e.message);
  process.exitCode = 1;
} finally {
  const echteFouten = fouten.filter((f) => !/Failed to load resource.*(404|ERR_INTERNET_DISCONNECTED)/.test(f));
  if (echteFouten.length) {
    console.error('\nFouten in de browser:\n' + echteFouten.join('\n'));
    process.exitCode = 1;
  }
  writeFileSync(join(UIT, 'browser-fouten.txt'), fouten.join('\n'));
  await browser.close();
}
if (!process.exitCode) console.log('\nAlles gelukt ✓');
