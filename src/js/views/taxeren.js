// Scherm: Taxeren (nieuwe taxatie of een auto uit het archief bewerken).

import { h, leeg, icoon, getalVeld, veld, tekstvak, segmenten, toast, paneel, bevestig, vertraagd, isStandalone, leesLokaal, schrijfLokaal } from '../ui.js';
import { db, leesInstellingen, haalConcept, bewaarAuto, zetInArchief, verwijderAuto, bodVoor, bewaarFoto, haalFoto, verwijderFoto, nieuwId } from '../db.js';
import { OPTIES, SCHADE_TYPES, TRANSMISSIES, schadeLabel } from '../constants.js';
import { formatEuro, formatGetal, formatIsoDatum, formatDatumKort } from '../format.js';
import { formatKenteken, normaliseerKenteken } from '../kenteken.js';
import { zoekKenteken, tellerstandKleur } from '../rdw.js';
import { dealSignaal } from '../calc.js';
import { verkleinFoto, fotoUrl } from '../images.js';

const KW_NAAR_PK = 1.36;

export async function toonTaxeren(root, { id, herlaad }) {
  const instellingen = await leesInstellingen();
  const auto = id ? await db.autos.get(id) : await haalConcept();

  if (!auto) {
    leeg(
      root,
      h('header', { class: 'pagina-kop' }, h('h1', {}, 'Niet gevonden')),
      h('div', { class: 'kaart' }, h('p', {}, 'Deze taxatie bestaat niet (meer).'), h('a', { class: 'knop', href: '#/archief' }, 'Naar archief'))
    );
    return () => {};
  }

  const inArchief = auto.status === 'archief';
  const opruimers = [];
  const opslaan = vertraagd(() => bewaarAuto(auto, instellingen), 350);
  const wijzig = (fn) => {
    fn(auto);
    werkResultaatBij();
    opslaan();
  };

  // ---------- kop ----------
  const kop = inArchief
    ? h(
        'header',
        { class: 'pagina-kop' },
        h('a', { class: 'terug', href: '#/archief' }, icoon('links'), 'Archief'),
        h('h1', {}, 'Bewerken'),
        h('p', { class: 'pagina-sub' }, `Getaxeerd op ${formatDatumKort(auto.getaxeerdOp)}`)
      )
    : h('header', { class: 'pagina-kop' }, h('h1', {}, 'Taxeren'));

  // ---------- installeer-tip ----------
  let tip = null;
  if (!isStandalone() && !leesLokaal('tipVerborgen')) {
    tip = h(
      'div',
      { class: 'kaart tip' },
      h('button', { type: 'button', class: 'icoon-knop tip-sluit', 'aria-label': 'Tip sluiten', onClick: () => (schrijfLokaal('tipVerborgen', '1'), tip.remove()) }, icoon('sluit')),
      h('h2', {}, 'Zet de app op je beginscherm'),
      h('p', {}, 'Tik in Safari op ', icoon('deel', 'inline'), ' (Deel) en kies ', h('strong', {}, 'Zet op beginscherm'), '.'),
      h(
        'p',
        { class: 'klein' },
        'Gebruik de app daarna alleen vanaf je beginscherm. Gegevens in Safari en in de app zijn gescheiden, en Safari kan gegevens wissen als je de site 7 dagen niet gebruikt.'
      )
    );
  }

  // ---------- kenteken ----------
  const kentekenInput = h('input', {
    class: 'kenteken-input',
    type: 'text',
    value: formatKenteken(auto.kenteken),
    autocapitalize: 'characters',
    autocomplete: 'off',
    autocorrect: 'off',
    spellcheck: 'false',
    enterkeyhint: 'search',
    placeholder: 'AB-123-C',
    maxlength: '10',
    'aria-label': 'Kenteken',
  });
  const checkKnop = h('button', { type: 'button', class: 'knop' }, 'Check kenteken');
  const foutVak = h('div', { class: 'melding rood', role: 'alert', hidden: true });
  const rdwVak = h('div', { class: 'rdw' });

  kentekenInput.addEventListener('input', () => {
    wijzig((a) => (a.kenteken = normaliseerKenteken(kentekenInput.value)));
    toonRdw();
  });
  kentekenInput.addEventListener('blur', () => (kentekenInput.value = formatKenteken(kentekenInput.value)));
  kentekenInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      check();
    }
  });
  checkKnop.addEventListener('click', check);

  async function check() {
    const k = normaliseerKenteken(kentekenInput.value);
    foutVak.hidden = true;
    if (!k) {
      foutVak.textContent = 'Vul eerst een kenteken in.';
      foutVak.hidden = false;
      kentekenInput.focus();
      return;
    }
    kentekenInput.blur();
    kentekenInput.value = formatKenteken(k);
    checkKnop.disabled = true;
    checkKnop.textContent = 'Bezig met ophalen…';
    try {
      const gegevens = await zoekKenteken(k);
      wijzig((a) => {
        a.kenteken = k;
        a.rdw = gegevens;
      });
      opslaan.flush();
      toonRdw();
    } catch (e) {
      foutVak.textContent = e?.message || 'Er ging iets mis bij het ophalen. Probeer het opnieuw.';
      foutVak.hidden = false;
    } finally {
      checkKnop.disabled = false;
      checkKnop.textContent = 'Check kenteken';
    }
  }

  function toonRdw() {
    const r = auto.rdw;
    if (!r) return leeg(rdwVak);
    const vandaag = new Date().toISOString().slice(0, 10);
    const apkVerlopen = Boolean(r.apkVervaldatum && r.apkVervaldatum < vandaag);
    const anderKenteken = auto.kenteken && r.kenteken !== auto.kenteken;
    const brandstof = [...(r.brandstoffen ?? [])].sort((a, b) => (a === 'Elektriciteit') - (b === 'Elektriciteit'));
    const kleur = tellerstandKleur(r.tellerstandoordeel);

    const rijen = [
      ['Eerste toelating', formatIsoDatum(r.datumEersteToelating)],
      r.import ? ['In Nederland sinds', formatIsoDatum(r.datumEersteNL)] : null,
      ['Brandstof', brandstof.length ? brandstof.join(' + ') + (r.hybride ? ` (${r.hybride})` : '') : '–'],
      ['Vermogen', r.vermogenKw ? `${formatGetal(r.vermogenKw)} kW (${formatGetal(r.vermogenKw * KW_NAAR_PK)} pk)` : '–'],
      ['Motorinhoud', r.cilinderinhoud ? `${formatGetal(r.cilinderinhoud)} cc` : '–'],
      ['Kleur', r.kleur || '–'],
      ['Catalogusprijs', formatEuro(r.catalogusprijs)],
      ['APK geldig tot', formatIsoDatum(r.apkVervaldatum) + (apkVerlopen ? ' (verlopen)' : ''), apkVerlopen ? 'rood' : ''],
    ].filter(Boolean);

    leeg(
      rdwVak,
      anderKenteken ? h('div', { class: 'melding grijs' }, `Deze gegevens horen bij ${formatKenteken(r.kenteken)}. Tik op Check kenteken voor het nieuwe kenteken.`) : null,
      h('div', { class: 'rdw-titel' }, h('h3', {}, `${r.merk} ${r.model}`.trim() || 'Onbekend'), h('span', { class: 'rdw-jaar' }, r.bouwjaar ?? '')),
      r.voertuigsoort && r.voertuigsoort !== 'Personenauto' ? h('p', { class: 'klein' }, `Voertuigsoort: ${r.voertuigsoort}`) : null,
      h(
        'div',
        { class: `tellerstand ${kleur}` },
        h('div', { class: 'tellerstand-kop' }, h('span', { class: 'stip' }), `Tellerstand: ${(r.tellerstandoordeel ?? 'onbekend').toLowerCase()}`),
        r.tellerstandUitleg ? h('p', {}, r.tellerstandUitleg) : null,
        r.jaarLaatsteTellerstand ? h('p', { class: 'klein' }, `Laatste registratie: ${r.jaarLaatsteTellerstand}`) : null
      ),
      r.terugroepactie ? h('div', { class: 'melding rood' }, icoon('let_op', 'inline'), ' Openstaande terugroepactie volgens de RDW') : null,
      h(
        'dl',
        { class: 'gegevens' },
        rijen.map(([label, waarde, klasse]) => h('div', { class: `gegeven ${klasse ?? ''}` }, h('dt', {}, label), h('dd', {}, waarde)))
      ),
      h('p', { class: 'bron' }, `Bron: RDW Open Data · ${formatDatumKort(r.opgehaaldOp)}`)
    );
  }

  const kentekenKaart = h(
    'section',
    { class: 'kaart' },
    h('h2', {}, 'Kenteken'),
    h('div', { class: 'kenteken-rij' }, kentekenInput),
    checkKnop,
    foutVak,
    rdwVak
  );

  // ---------- auto ----------
  const autoKaart = h(
    'section',
    { class: 'kaart' },
    h('h2', {}, 'Auto'),
    veld('Kilometerstand', getalVeld({ waarde: auto.km, achtervoegsel: 'km', placeholder: '0', onWijzig: (v) => wijzig((a) => (a.km = v)) })),
    veld(
      'Uitvoering',
      h('input', {
        type: 'text',
        value: auto.uitvoering,
        placeholder: 'bijv. 1.5 TSI Highline',
        autocomplete: 'off',
        onInput: (e) => wijzig((a) => (a.uitvoering = e.target.value)),
      })
    ),
    h(
      'div',
      { class: 'veld' },
      h('span', { class: 'veld-label' }, 'Transmissie'),
      segmenten(TRANSMISSIES, auto.transmissie, (k) => wijzig((a) => (a.transmissie = k)))
    )
  );

  // ---------- opties ----------
  const chips = OPTIES.map((o) => {
    const chip = h('button', { type: 'button', class: 'chip', 'aria-pressed': 'false' }, o.label);
    const zet = () => {
      const aan = auto.opties.includes(o.key);
      chip.classList.toggle('aan', aan);
      chip.setAttribute('aria-pressed', String(aan));
    };
    chip.addEventListener('click', () => {
      wijzig((a) => (a.opties = a.opties.includes(o.key) ? a.opties.filter((k) => k !== o.key) : [...a.opties, o.key]));
      zet();
    });
    zet();
    return chip;
  });
  const optiesKaart = h(
    'section',
    { class: 'kaart' },
    h('h2', {}, 'Opties'),
    h('div', { class: 'chips' }, chips),
    veld(
      'Andere opties',
      h('input', {
        type: 'text',
        value: auto.optiesAnders,
        placeholder: 'bijv. head-up display, keyless',
        onInput: (e) => wijzig((a) => (a.optiesAnders = e.target.value)),
      })
    )
  );

  // ---------- advertentie ----------
  const urlInput = h('input', {
    type: 'url',
    inputmode: 'url',
    value: auto.advertentieUrl,
    placeholder: 'Plak hier de link',
    autocomplete: 'off',
    autocapitalize: 'off',
    spellcheck: 'false',
  });
  const openKnop = h('button', { type: 'button', class: 'knop knop-licht knop-klein', disabled: !auto.advertentieUrl }, icoon('extern'), 'Open');
  urlInput.addEventListener('input', () => {
    wijzig((a) => (a.advertentieUrl = urlInput.value.trim()));
    openKnop.disabled = !auto.advertentieUrl;
  });
  openKnop.addEventListener('click', () => {
    let url = auto.advertentieUrl;
    if (!url) return;
    if (!/^https?:\/\//i.test(url)) url = `https://${url}`;
    window.open(url, '_blank', 'noopener');
  });
  const plakKnop = h('button', { type: 'button', class: 'knop knop-licht knop-klein' }, 'Plak');
  plakKnop.addEventListener('click', async () => {
    try {
      const tekst = (await navigator.clipboard.readText()).trim();
      if (!tekst) return toast('Je klembord is leeg.');
      urlInput.value = tekst;
      urlInput.dispatchEvent(new Event('input'));
    } catch {
      toast('Plakken lukt niet. Houd het veld ingedrukt en kies Plak.');
    }
  });

  const advertentieKaart = h(
    'section',
    { class: 'kaart' },
    h('h2', {}, 'Advertentie'),
    veld('Link (Marktplaats, Gaspedaal, …)', urlInput),
    h('div', { class: 'knoppen-rij' }, plakKnop, openKnop),
    veld(
      'Vraagprijs (optioneel)',
      getalVeld({ waarde: auto.vraagprijs, voorvoegsel: '€', placeholder: '0', onWijzig: (v) => wijzig((a) => (a.vraagprijs = v)) }),
      'Dan zie je of de vraagprijs binnen je bod past.'
    )
  );

  // ---------- foto's ----------
  function fotoBlok(leesIds, zetIds, { compact = false } = {}) {
    const raster = h('div', { class: `foto-raster${compact ? ' compact' : ''}` });
    const status = h('p', { class: 'foto-status', hidden: true });
    let urls = [];
    let tekenNr = 0;

    const invoer = h('input', { type: 'file', accept: 'image/*', multiple: true, class: 'verborgen-invoer' });
    invoer.addEventListener('change', async () => {
      const bestanden = [...(invoer.files ?? [])];
      invoer.value = '';
      if (!bestanden.length) return;
      status.hidden = false;
      for (let i = 0; i < bestanden.length; i++) {
        status.textContent = bestanden.length > 1 ? `Foto ${i + 1} van ${bestanden.length} verwerken…` : 'Foto verwerken…';
        try {
          const verkleind = await verkleinFoto(bestanden[i]);
          const fotoId = await bewaarFoto(auto.id, verkleind);
          zetIds([...leesIds(), fotoId]);
          opslaan();
          await teken();
        } catch (e) {
          toast(e?.message || 'Foto toevoegen is mislukt.', 'fout');
        }
      }
      status.hidden = true;
      opslaan.flush();
    });

    async function teken() {
      const nr = ++tekenNr;
      const ids = leesIds();
      const fotos = await Promise.all(ids.map((fid) => haalFoto(fid)));
      if (nr !== tekenNr) return; // er is al een nieuwere tekening bezig
      urls.forEach((u) => URL.revokeObjectURL(u));
      urls = [];
      const tegels = fotos.map((foto, index) => {
        if (!foto) return null;
        const url = fotoUrl(foto, 'klein');
        urls.push(url);
        return h(
          'button',
          { type: 'button', class: 'foto-tegel', 'aria-label': `Foto ${index + 1} bekijken`, onClick: () => bekijk(index) },
          h('img', { src: url, alt: '', decoding: 'async' })
        );
      });
      leeg(
        raster,
        tegels,
        h('label', { class: 'foto-tegel foto-toevoegen' }, icoon('camera'), h('span', {}, compact ? 'Foto' : "Foto's"), invoer)
      );
    }

    function bekijk(start) {
      fotoViewer(leesIds(), start, async (fotoId) => {
        zetIds(leesIds().filter((x) => x !== fotoId));
        await verwijderFoto(fotoId);
        opslaan.flush();
        await teken();
      });
    }

    opruimers.push(() => urls.forEach((u) => URL.revokeObjectURL(u)));
    teken();
    return h('div', { class: 'foto-blok' }, raster, status);
  }

  const fotoKaart = h(
    'section',
    { class: 'kaart' },
    h('h2', {}, "Foto's"),
    fotoBlok(
      () => auto.fotoIds,
      (ids) => (auto.fotoIds = ids)
    )
  );

  // ---------- schade ----------
  const schadeLijst = h('div', { class: 'schade-lijst' });
  const schadeTotaal = h('strong', { class: 'bedrag' });

  function tekenSchades() {
    leeg(schadeLijst, auto.schades.length ? auto.schades.map(schadeItem) : h('p', { class: 'leeg-tekst' }, 'Nog geen schade toegevoegd.'));
  }

  function schadeItem(s) {
    const typeKeuze = h(
      'select',
      { class: 'schade-type', 'aria-label': 'Soort schade' },
      SCHADE_TYPES.map((t) => h('option', { value: t.key, selected: t.key === s.type }, t.label))
    );
    typeKeuze.addEventListener('change', () => wijzig(() => (s.type = typeKeuze.value)));

    const verwijder = async () => {
      const ok = await bevestig({ titel: 'Schade verwijderen?', tekst: `${schadeLabel(s.type)} · ${formatEuro(s.bedrag)}`, ja: 'Verwijderen', gevaar: true });
      if (!ok) return;
      for (const fid of s.fotoIds ?? []) await verwijderFoto(fid);
      wijzig((a) => (a.schades = a.schades.filter((x) => x.id !== s.id)));
      tekenSchades();
    };

    return h(
      'div',
      { class: 'schade-item', 'data-id': s.id },
      h('div', { class: 'schade-kop' }, typeKeuze, h('button', { type: 'button', class: 'icoon-knop', 'aria-label': 'Schade verwijderen', onClick: verwijder }, icoon('prullenbak'))),
      h(
        'div',
        { class: 'rij-2' },
        veld('Bedrag', getalVeld({ waarde: s.bedrag, voorvoegsel: '€', placeholder: '0', onWijzig: (v) => wijzig(() => (s.bedrag = v)) })),
        veld('Plek (optioneel)', h('input', { type: 'text', value: s.plek ?? '', placeholder: 'bijv. deur links', onInput: (e) => wijzig(() => (s.plek = e.target.value)) }))
      ),
      veld('Notitie', h('input', { type: 'text', value: s.notitie ?? '', placeholder: 'Korte notitie', onInput: (e) => wijzig(() => (s.notitie = e.target.value)) })),
      fotoBlok(
        () => s.fotoIds ?? [],
        (ids) => (s.fotoIds = ids),
        { compact: true }
      )
    );
  }

  function kiesSchadeType() {
    const sluit = paneel(
      h(
        'div',
        { class: 'keuze' },
        h('h2', {}, 'Soort schade'),
        h(
          'div',
          { class: 'keuze-raster' },
          SCHADE_TYPES.map((t) =>
            h(
              'button',
              {
                type: 'button',
                class: 'keuze-knop',
                onClick: () => {
                  sluit();
                  const nieuw = { id: nieuwId(), type: t.key, plek: '', notitie: '', bedrag: instellingen.schadeStandaard[t.key] ?? 0, fotoIds: [] };
                  wijzig((a) => a.schades.push(nieuw));
                  tekenSchades();
                  schadeLijst.querySelector(`[data-id="${nieuw.id}"]`)?.scrollIntoView({ behavior: 'smooth', block: 'center' });
                },
              },
              t.label
            )
          )
        )
      )
    );
  }

  const schadeKaart = h(
    'section',
    { class: 'kaart' },
    h('h2', {}, 'Schade'),
    schadeLijst,
    h('button', { type: 'button', class: 'knop knop-licht', onClick: kiesSchadeType }, icoon('plus'), 'Schade toevoegen'),
    h('div', { class: 'totaal-rij' }, h('span', {}, 'Totale schade'), schadeTotaal)
  );

  // ---------- notities ----------
  const notitieKaart = h(
    'section',
    { class: 'kaart' },
    h('h2', {}, 'Notities'),
    tekstvak({ value: auto.notities, placeholder: 'Bijzonderheden, onderhoud, gesprek met verkoper…', 'aria-label': 'Notities', onInput: (e) => wijzig((a) => (a.notities = e.target.value)) })
  );

  // ---------- verkoopprijs ----------
  const verkoopKaart = h(
    'section',
    { class: 'kaart' },
    h('h2', {}, 'Verwachte verkoopprijs'),
    getalVeld({ waarde: auto.verkoopprijs, voorvoegsel: '€', placeholder: '0', label: 'Verwachte verkoopprijs', onWijzig: (v) => wijzig((a) => (a.verkoopprijs = v)) }),
    h('p', { class: 'veld-hulp' }, 'Wat verwacht je dat de auto opbrengt? Later komt dit automatisch uit vergelijkbare auto’s op Gaspedaal.')
  );

  // ---------- resultaat ----------
  const resultaat = h('section', { class: 'resultaat', 'aria-live': 'polite' });
  const balkBedrag = h('strong', {});
  const bodBalk = h(
    'button',
    { type: 'button', class: 'bod-balk', onClick: () => resultaat.scrollIntoView({ behavior: 'smooth', block: 'center' }) },
    h('span', {}, 'Advies bod'),
    balkBedrag
  );
  let resultaatInBeeld = false;
  let toetsenbordOpen = false;
  let bodCompleet = false;
  const werkBalkBij = () => bodBalk.classList.toggle('toon', bodCompleet && !resultaatInBeeld && !toetsenbordOpen);

  function werkResultaatBij() {
    const bod = bodVoor(auto, instellingen);
    schadeTotaal.textContent = formatEuro(bod.schadeTotaal);
    bodCompleet = bod.compleet;
    const rij = (label, waarde, klasse = '') => h('div', { class: `res-rij ${klasse}` }, h('span', {}, label), h('span', { class: 'bedrag' }, waarde));

    if (!bod.compleet) {
      leeg(
        resultaat,
        h('h2', {}, 'Advies bod'),
        h('p', { class: 'res-leeg' }, 'Vul de verwachte verkoopprijs in. Dan zie je hier je bod.'),
        rij('Totale schade', formatEuro(bod.schadeTotaal)),
        rij('Marge', `${formatEuro(bod.margeMin)} – ${formatEuro(bod.margeMax)}`)
      );
      werkBalkBij();
      return;
    }

    const signaal = dealSignaal(auto.vraagprijs, bod);
    leeg(
      resultaat,
      h('h2', {}, 'Advies bod'),
      rij('Verwachte verkoopprijs', formatEuro(bod.verkoopprijs)),
      rij('− Totale schade', formatEuro(bod.schadeTotaal)),
      rij('= Waarde na schade', formatEuro(bod.waardeNaSchade), 'tussen'),
      rij('− Marge', `${formatEuro(bod.margeMin)} – ${formatEuro(bod.margeMax)}`),
      h(
        'div',
        { class: 'res-bod' },
        h('div', {}, h('span', { class: 'res-bod-label' }, 'Laagste bod'), h('span', { class: 'res-bod-bedrag' }, formatEuro(bod.bodLaag))),
        h('span', { class: 'res-bod-streep' }, '–'),
        h('div', {}, h('span', { class: 'res-bod-label' }, 'Hoogste bod'), h('span', { class: 'res-bod-bedrag' }, formatEuro(bod.bodHoog)))
      ),
      h('p', { class: 'res-uitleg' }, `Hoogste bod bij de laagste marge (${formatEuro(bod.margeMin)}), laagste bod bij de hoogste marge (${formatEuro(bod.margeMax)}).`),
      signaal === 'goed' ? h('div', { class: 'deal groen' }, icoon('vink', 'inline'), ` Vraagprijs ${formatEuro(auto.vraagprijs)} past binnen je bod`) : null,
      signaal === 'slecht'
        ? h('div', { class: 'deal rood' }, icoon('let_op', 'inline'), ` Vraagprijs ${formatEuro(auto.vraagprijs)} is ${formatEuro(auto.vraagprijs - bod.bodHoog)} hoger dan je hoogste bod`)
        : null,
      bod.bodHoog < 0 ? h('div', { class: 'deal rood' }, 'Schade en marge zijn hoger dan de verwachte verkoopprijs.') : null,
      inArchief ? h('p', { class: 'res-uitleg' }, 'Met de marge van het moment van taxeren.') : null
    );
    balkBedrag.textContent = `${formatEuro(bod.bodLaag)} – ${formatEuro(bod.bodHoog)}`;
    werkBalkBij();
  }

  const io = new IntersectionObserver(([e]) => {
    resultaatInBeeld = e.isIntersecting;
    werkBalkBij();
  });
  io.observe(resultaat);
  const opFocus = (e) => {
    if (e.target.matches('input, textarea, select')) {
      toetsenbordOpen = e.type === 'focusin';
      werkBalkBij();
    }
  };
  root.addEventListener('focusin', opFocus);
  root.addEventListener('focusout', opFocus);
  document.body.append(bodBalk);

  // ---------- acties ----------
  const acties = inArchief
    ? h(
        'section',
        { class: 'acties' },
        h('a', { class: 'knop knop-groot', href: '#/archief' }, 'Klaar'),
        h('p', { class: 'veld-hulp midden' }, 'Wijzigingen worden automatisch bewaard.'),
        h(
          'button',
          {
            type: 'button',
            class: 'knop knop-tekst gevaar',
            onClick: async () => {
              const ok = await bevestig({
                titel: 'Taxatie verwijderen?',
                tekst: 'Deze auto en alle foto’s worden van je telefoon verwijderd. Dit kan niet ongedaan worden gemaakt.',
                ja: 'Verwijderen',
                gevaar: true,
              });
              if (!ok) return;
              await verwijderAuto(auto.id);
              toast('Taxatie verwijderd');
              location.hash = '#/archief';
            },
          },
          icoon('prullenbak'),
          'Verwijderen'
        )
      )
    : h(
        'section',
        { class: 'acties' },
        h(
          'button',
          {
            type: 'button',
            class: 'knop knop-groot',
            onClick: async () => {
              if (!auto.kenteken) {
                const ok = await bevestig({ titel: 'Opslaan zonder kenteken?', tekst: 'Je hebt nog geen kenteken ingevuld.', ja: 'Toch opslaan' });
                if (!ok) return;
              }
              opslaan.flush();
              await zetInArchief(auto, instellingen);
              toast('Opgeslagen in archief');
              location.hash = '#/archief';
            },
          },
          'Opslaan in archief'
        ),
        h(
          'button',
          {
            type: 'button',
            class: 'knop knop-tekst',
            onClick: async () => {
              const ok = await bevestig({ titel: 'Formulier wissen?', tekst: 'Alles wat je hier hebt ingevuld, ook foto’s, wordt verwijderd.', ja: 'Wissen', gevaar: true });
              if (!ok) return;
              await verwijderAuto(auto.id);
              herlaad();
            },
          },
          'Wis formulier'
        )
      );

  leeg(root, kop, tip, kentekenKaart, autoKaart, optiesKaart, advertentieKaart, fotoKaart, schadeKaart, notitieKaart, verkoopKaart, resultaat, acties);
  toonRdw();
  tekenSchades();
  werkResultaatBij();

  // Direct opslaan als de app naar de achtergrond gaat (iOS kan hem dan afsluiten).
  const bijVerbergen = () => opslaan.flush();
  const bijZichtbaarheid = () => document.visibilityState === 'hidden' && opslaan.flush();
  window.addEventListener('pagehide', bijVerbergen);
  document.addEventListener('visibilitychange', bijZichtbaarheid);

  return () => {
    opslaan.flush();
    window.removeEventListener('pagehide', bijVerbergen);
    document.removeEventListener('visibilitychange', bijZichtbaarheid);
    io.disconnect();
    bodBalk.remove();
    opruimers.forEach((f) => f());
  };
}

// ---------- foto bekijken (volledig scherm) ----------

function fotoViewer(startIds, start, onVerwijder) {
  let ids = [...startIds];
  let index = start;
  let url = null;
  const img = h('img', { class: 'viewer-img', alt: '' });
  const teller = h('span', { class: 'viewer-teller' });
  const vorige = h('button', { type: 'button', class: 'rond-knop', 'aria-label': 'Vorige foto' }, icoon('links'));
  const volgende = h('button', { type: 'button', class: 'rond-knop', 'aria-label': 'Volgende foto' }, icoon('rechts'));
  const laag = h(
    'div',
    { class: 'viewer', role: 'dialog', 'aria-modal': 'true' },
    h('div', { class: 'viewer-boven' }, teller, h('button', { type: 'button', class: 'rond-knop', 'aria-label': 'Sluiten', onClick: () => sluit() }, icoon('sluit'))),
    h('div', { class: 'viewer-midden' }, img),
    h(
      'div',
      { class: 'viewer-onder' },
      vorige,
      h('button', { type: 'button', class: 'knop knop-gevaar', onClick: () => verwijder() }, icoon('prullenbak'), 'Verwijderen'),
      volgende
    )
  );

  async function toon() {
    const foto = await haalFoto(ids[index]);
    if (url) URL.revokeObjectURL(url);
    url = foto ? fotoUrl(foto, 'groot') : null;
    img.src = url ?? '';
    teller.textContent = `${index + 1} / ${ids.length}`;
    vorige.disabled = index === 0;
    volgende.disabled = index >= ids.length - 1;
  }
  function sluit() {
    if (url) URL.revokeObjectURL(url);
    laag.remove();
  }
  async function verwijder() {
    const ok = await bevestig({ titel: 'Foto verwijderen?', ja: 'Verwijderen', gevaar: true });
    if (!ok) return;
    const fotoId = ids[index];
    await onVerwijder(fotoId);
    ids = ids.filter((x) => x !== fotoId);
    if (!ids.length) return sluit();
    index = Math.min(index, ids.length - 1);
    toon();
  }
  vorige.addEventListener('click', () => index > 0 && (index--, toon()));
  volgende.addEventListener('click', () => index < ids.length - 1 && (index++, toon()));

  // Vegen naar links/rechts
  let startX = null;
  img.addEventListener('touchstart', (e) => (startX = e.touches[0].clientX), { passive: true });
  img.addEventListener('touchend', (e) => {
    if (startX === null) return;
    const dx = e.changedTouches[0].clientX - startX;
    startX = null;
    if (dx > 50 && index > 0) (index--, toon());
    else if (dx < -50 && index < ids.length - 1) (index++, toon());
  });

  document.body.append(laag);
  toon();
}
