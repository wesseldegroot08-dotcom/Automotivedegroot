// Maakt de map dist/ klaar voor publicatie:
// - kopieert src/ naar dist/
// - vult het versienummer in (zodat iPhones de nieuwe versie ophalen)
// - zet de lijst met bestanden in de service worker (voor offline gebruik)

import { cpSync, readdirSync, readFileSync, rmSync, statSync, writeFileSync } from 'node:fs';
import { join, relative, sep } from 'node:path';
import { execSync } from 'node:child_process';

const root = new URL('..', import.meta.url).pathname;
const src = join(root, 'src');
const dist = join(root, 'dist');

function commit() {
  if (process.env.GITHUB_SHA) return process.env.GITHUB_SHA.slice(0, 7);
  try {
    return execSync('git rev-parse --short HEAD', { cwd: root }).toString().trim();
  } catch {
    return 'lokaal';
  }
}

const nu = new Date();
const datum = nu.toISOString().slice(0, 10);
const versie = `${datum} · ${commit()}`;
const cacheSleutel = `${commit()}-${nu.getTime()}`;

rmSync(dist, { recursive: true, force: true });
cpSync(src, dist, { recursive: true });

function alleBestanden(map) {
  return readdirSync(map).flatMap((naam) => {
    const pad = join(map, naam);
    return statSync(pad).isDirectory() ? alleBestanden(pad) : [pad];
  });
}

const bestanden = alleBestanden(dist)
  .map((p) => relative(dist, p).split(sep).join('/'))
  .filter((p) => p !== 'sw.js' && !p.endsWith('.txt'))
  .sort();

function vervang(bestand, oud, nieuw) {
  const pad = join(dist, bestand);
  const inhoud = readFileSync(pad, 'utf8');
  if (!inhoud.includes(oud)) throw new Error(`"${oud}" niet gevonden in ${bestand}`);
  writeFileSync(pad, inhoud.replace(oud, nieuw));
}

vervang('sw.js', "const VERSIE = 'ontwikkel';", `const VERSIE = ${JSON.stringify(cacheSleutel)};`);
vervang('sw.js', "const BESTANDEN = ['./', 'index.html'];", `const BESTANDEN = ${JSON.stringify(['./', ...bestanden])};`);
vervang('js/versie.js', "export const VERSIE = 'ontwikkel';", `export const VERSIE = ${JSON.stringify(versie)};`);

console.log(`Klaar: dist/ met ${bestanden.length} bestanden, versie ${versie}`);
