// Scherm: Instellingen (marge, standaardbedragen schade, back-up).

import { h, leeg, icoon, getalVeld, veld, toast, paneel, bevestig, vertraagd, isStandalone } from '../ui.js';
import { leesInstellingen, schrijfInstellingen, opslagStatus, vraagBlijvendeOpslag } from '../db.js';
import { SCHADE_TYPES, BACKUP_HERINNERING_DAGEN } from '../constants.js';
import { formatDatumKort, dagenTussen } from '../format.js';
import { maakBackup, deelBackup, laatsteBackup, leesBackup, zetBackupTerug } from '../backup.js';
import { VERSIE } from '../versie.js';

function formatGrootte(bytes) {
  if (bytes === null || bytes === undefined) return 'onbekend';
  if (bytes < 1024 * 1024) return `${Math.max(1, Math.round(bytes / 1024))} kB`;
  return `${(bytes / 1024 / 1024).toFixed(1).replace('.', ',')} MB`;
}

export async function toonInstellingen(root, { herlaad }) {
  const instellingen = await leesInstellingen();
  const opslaan = vertraagd(() => schrijfInstellingen(instellingen), 300);

  // ---------- marge ----------
  const margeFout = h('div', { class: 'melding rood', hidden: true }, 'Het minimum is hoger dan het maximum. De app draait ze om bij het rekenen.');
  const controleerMarge = () => (margeFout.hidden = !(instellingen.margeMin > instellingen.margeMax));
  const margeKaart = h(
    'section',
    { class: 'kaart' },
    h('h2', {}, 'Marge'),
    h('p', { class: 'veld-hulp' }, 'Wat je minimaal en maximaal wilt verdienen aan een auto. Dit gaat van de waarde af.'),
    h(
      'div',
      { class: 'rij-2' },
      veld(
        'Minimum',
        getalVeld({
          waarde: instellingen.margeMin,
          voorvoegsel: '€',
          onWijzig: (v) => {
            instellingen.margeMin = v ?? 0;
            controleerMarge();
            opslaan();
          },
        })
      ),
      veld(
        'Maximum',
        getalVeld({
          waarde: instellingen.margeMax,
          voorvoegsel: '€',
          onWijzig: (v) => {
            instellingen.margeMax = v ?? 0;
            controleerMarge();
            opslaan();
          },
        })
      )
    ),
    margeFout
  );
  controleerMarge();

  // ---------- standaard schadebedragen ----------
  const schadeKaart = h(
    'section',
    { class: 'kaart' },
    h('h2', {}, 'Standaardbedragen schade'),
    h('p', { class: 'veld-hulp' }, 'Dit bedrag staat al ingevuld als je schade toevoegt. Per auto kun je het aanpassen.'),
    h(
      'div',
      { class: 'lijst-velden' },
      SCHADE_TYPES.map((t) =>
        h(
          'label',
          { class: 'lijst-veld' },
          h('span', {}, t.label),
          getalVeld({
            waarde: instellingen.schadeStandaard[t.key] ?? 0,
            voorvoegsel: '€',
            label: `Standaardbedrag ${t.label}`,
            onWijzig: (v) => {
              instellingen.schadeStandaard[t.key] = v ?? 0;
              opslaan();
            },
          })
        )
      )
    )
  );

  // ---------- back-up ----------
  const backupStatus = h('div', {});
  async function tekenBackupStatus() {
    const laatste = await laatsteBackup();
    const dagen = laatste ? dagenTussen(laatste) : null;
    const teLang = dagen === null || dagen > BACKUP_HERINNERING_DAGEN;
    leeg(
      backupStatus,
      h(
        'div',
        { class: `melding ${teLang ? 'rood' : 'groen'}` },
        teLang ? icoon('let_op', 'inline') : icoon('vink', 'inline'),
        laatste
          ? ` Laatste back-up: ${formatDatumKort(laatste)}${dagen === 0 ? ' (vandaag)' : dagen === 1 ? ' (gisteren)' : ` (${dagen} dagen geleden)`}`
          : ' Nog nooit een back-up gemaakt'
      )
    );
  }

  const exportKnop = h('button', { type: 'button', class: 'knop' }, icoon('deel'), 'Exporteer alles');
  exportKnop.addEventListener('click', async () => {
    exportKnop.disabled = true;
    exportKnop.lastChild.textContent = 'Back-up maken…';
    try {
      const { bestand, aantalAutos, aantalFotos } = await maakBackup();
      // Delen moet direct na een tik, daarom een tweede knop.
      const sluit = paneel(
        h(
          'div',
          { class: 'bevestig' },
          h('h2', {}, 'Back-up is klaar'),
          h('p', {}, `${aantalAutos} ${aantalAutos === 1 ? 'auto' : "auto's"} · ${aantalFotos} foto's · ${formatGrootte(bestand.size)}`),
          h('p', { class: 'klein' }, 'Kies daarna “Bewaar in Bestanden” en zet hem bijvoorbeeld in iCloud Drive.'),
          h(
            'button',
            {
              type: 'button',
              class: 'knop',
              onClick: async () => {
                const gelukt = await deelBackup(bestand);
                if (gelukt) {
                  sluit();
                  toast('Back-up opgeslagen');
                  tekenBackupStatus();
                }
              },
            },
            icoon('deel'),
            'Bewaar back-up'
          ),
          h('button', { type: 'button', class: 'knop knop-licht', onClick: () => sluit() }, 'Annuleren')
        )
      );
    } catch (e) {
      toast(e?.message || 'Back-up maken is mislukt.', 'fout');
    } finally {
      exportKnop.disabled = false;
      exportKnop.lastChild.textContent = 'Exporteer alles';
    }
  });

  const importInvoer = h('input', { type: 'file', accept: '.zip,application/zip', class: 'verborgen-invoer' });
  importInvoer.addEventListener('change', async () => {
    const bestand = importInvoer.files?.[0];
    importInvoer.value = '';
    if (!bestand) return;
    try {
      const gelezen = await leesBackup(bestand);
      const autos = (gelezen.data.autos ?? []).filter((a) => a.status === 'archief').length;
      const ok = await bevestig({
        titel: 'Back-up terugzetten?',
        tekst: `Back-up van ${formatDatumKort(gelezen.data.gemaakt)} met ${autos} ${autos === 1 ? 'auto' : "auto's"}. Auto's die al op je telefoon staan, worden overschreven door de versie uit de back-up. Andere auto's blijven staan. Je instellingen worden ook teruggezet.`,
        ja: 'Terugzetten',
      });
      if (!ok) return;
      const resultaat = await zetBackupTerug(gelezen);
      toast(`${resultaat.aantalAutos} ${resultaat.aantalAutos === 1 ? 'auto' : "auto's"} teruggezet`);
      herlaad();
    } catch (e) {
      toast(e?.message || 'Dit bestand kan niet worden gelezen.', 'fout');
    }
  });

  const backupKaart = h(
    'section',
    { class: 'kaart' },
    h('h2', {}, 'Back-up'),
    h('p', { class: 'veld-hulp' }, `Al je taxaties staan alleen op deze telefoon. Maak minstens elke ${BACKUP_HERINNERING_DAGEN} dagen een back-up.`),
    backupStatus,
    exportKnop,
    h('label', { class: 'knop knop-licht' }, 'Importeer back-up', importInvoer)
  );

  // ---------- opslag & app ----------
  const opslagVak = h('dl', { class: 'gegevens' });
  async function tekenOpslag() {
    const s = await opslagStatus();
    leeg(
      opslagVak,
      h('div', { class: 'gegeven' }, h('dt', {}, 'Geïnstalleerd op beginscherm'), h('dd', {}, isStandalone() ? 'Ja' : 'Nee')),
      h('div', { class: `gegeven ${s.blijvend === false ? 'rood' : ''}` }, h('dt', {}, 'Blijvende opslag'), h('dd', {}, s.blijvend === null ? 'Onbekend' : s.blijvend ? 'Aan' : 'Uit')),
      h('div', { class: 'gegeven' }, h('dt', {}, 'Gebruikte opslag'), h('dd', {}, formatGrootte(s.gebruikt))),
      h('div', { class: 'gegeven' }, h('dt', {}, 'Versie'), h('dd', {}, VERSIE))
    );
  }
  const persistKnop = h('button', { type: 'button', class: 'knop knop-licht' }, 'Vraag blijvende opslag aan');
  persistKnop.addEventListener('click', async () => {
    const r = await vraagBlijvendeOpslag();
    toast(r ? 'Blijvende opslag staat aan' : 'Safari staat dit nu niet toe. Installeer de app op je beginscherm.');
    tekenOpslag();
  });

  const appKaart = h(
    'section',
    { class: 'kaart' },
    h('h2', {}, 'Opslag'),
    opslagVak,
    persistKnop,
    h('p', { class: 'veld-hulp' }, 'Je gegevens gaan nooit naar internet. Alleen het opzoeken van een kenteken gebruikt internet (RDW).')
  );

  leeg(root, h('header', { class: 'pagina-kop' }, h('h1', {}, 'Instellingen')), margeKaart, schadeKaart, backupKaart, appKaart);
  tekenBackupStatus();
  tekenOpslag();

  return () => opslaan.flush();
}
