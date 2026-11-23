// Kleine webserver om dist/ lokaal te testen: node scripts/serve.mjs [poort]

import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { extname, join, normalize } from 'node:path';

const map = join(new URL('..', import.meta.url).pathname, process.env.SERVE_DIR ?? 'dist');
const poort = Number(process.argv[2] ?? 8080);
const TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.json': 'application/json',
  '.webmanifest': 'application/manifest+json',
  '.png': 'image/png',
  '.svg': 'image/svg+xml',
  '.woff2': 'font/woff2',
  '.txt': 'text/plain; charset=utf-8',
};

createServer(async (req, res) => {
  let pad = decodeURIComponent(new URL(req.url, 'http://x').pathname);
  if (pad.endsWith('/')) pad += 'index.html';
  const bestand = normalize(join(map, pad));
  if (!bestand.startsWith(map)) {
    res.writeHead(403).end();
    return;
  }
  try {
    const data = await readFile(bestand);
    res.writeHead(200, { 'Content-Type': TYPES[extname(bestand)] ?? 'application/octet-stream', 'Cache-Control': 'no-cache' });
    res.end(data);
  } catch {
    res.writeHead(404).end('Niet gevonden');
  }
}).listen(poort, () => console.log(`http://localhost:${poort}/`));
