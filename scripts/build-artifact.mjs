// Maakt een testversie van de app als één HTML-bestand, om te openen als artifact in Claude.
//   node scripts/build-artifact.mjs
// Resultaat: dist-artifact/taxatie-app.html
//
// Verschil met de echte app: alles staat in één bestand (CSS, JavaScript, lettertype),
// er is geen offline-ondersteuning, en de kenteken-check werkt niet (de artifact-pagina
// mag geen andere websites bereiken). Zie window.TAXATIE_PREVIEW in de code.

import { execFileSync } from 'node:child_process';
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

const root = new URL('..', import.meta.url).pathname;
const src = join(root, 'src');
const uitMap = join(root, 'dist-artifact');
mkdirSync(uitMap, { recursive: true });

// 1. JavaScript bundelen tot één bestand (esbuild, vaste versie).
const bundel = join(uitMap, 'app.bundle.js');
execFileSync(
  'npx',
  ['--yes', 'esbuild@0.24.0', join(src, 'js', 'app.js'), '--bundle', '--format=esm', '--minify', '--target=es2020,safari15', `--outfile=${bundel}`],
  { stdio: 'inherit', cwd: root }
);
let commit = 'lokaal';
try {
  commit = execFileSync('git', ['rev-parse', '--short', 'HEAD'], { cwd: root }).toString().trim();
} catch {
  /* geen git */
}
let js = readFileSync(bundel, 'utf8').replace(/<\/script/gi, '<\\/script');
if (!js.includes('"ontwikkel"')) throw new Error('Versie-tekst niet gevonden in de bundel');
js = js.replace('"ontwikkel"', JSON.stringify(`Testversie ${new Date().toISOString().slice(0, 10)} · ${commit}`));

// 2. CSS met het lettertype erin (als data-URI).
const font = readFileSync(join(src, 'fonts', 'inter-var-latin.woff2')).toString('base64');
let css = readFileSync(join(src, 'css', 'app.css'), 'utf8');
const fontUrl = "url('../fonts/inter-var-latin.woff2')";
if (!css.includes(fontUrl)) throw new Error('Lettertype-verwijzing niet gevonden in app.css');
css = css.replace(fontUrl, `url(data:font/woff2;base64,${font})`);
// De artifact-omgeving houdt zelf al rekening met de notch bovenaan.
css += '\n.app { padding-top: 10px; }\n';

// 3. Eén pagina. Geen <html>/<head>/<body>: die zet Claude er zelf omheen.
const html = `<title>Taxatie-app</title>
<style>
${css}
</style>
<main id="app" class="app">
  <div class="scherm laden"><p>App laden…</p></div>
</main>
<nav id="tabbar" class="tabbar" aria-label="Hoofdmenu"></nav>
<script>window.TAXATIE_PREVIEW = true;</script>
<script type="module">
${js}
</script>
`;

const uit = join(uitMap, 'taxatie-app.html');
writeFileSync(uit, html);
console.log(`Klaar: ${uit} (${Math.round(html.length / 1024)} kB)`);
