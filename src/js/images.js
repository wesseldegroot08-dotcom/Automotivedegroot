// Foto's verkleinen voordat ze worden opgeslagen, zodat de opslag niet volloopt.

const MAX_GROOT = 1600; // langste zijde in pixels
const MAX_KLEIN = 400; // voorbeeldje voor lijsten
const KWALITEIT_GROOT = 0.82;
const KWALITEIT_KLEIN = 0.72;

function laadAfbeelding(bestand) {
  return new Promise((resolve, reject) => {
    const url = URL.createObjectURL(bestand);
    const img = new Image();
    img.onload = () => {
      URL.revokeObjectURL(url);
      resolve(img);
    };
    img.onerror = () => {
      URL.revokeObjectURL(url);
      reject(new Error('Deze foto kan niet worden gelezen.'));
    };
    img.src = url;
  });
}

function naarJpeg(img, maxZijde, kwaliteit) {
  const schaal = Math.min(1, maxZijde / Math.max(img.naturalWidth, img.naturalHeight));
  const breedte = Math.max(1, Math.round(img.naturalWidth * schaal));
  const hoogte = Math.max(1, Math.round(img.naturalHeight * schaal));
  const canvas = document.createElement('canvas');
  canvas.width = breedte;
  canvas.height = hoogte;
  const ctx = canvas.getContext('2d');
  ctx.fillStyle = '#fff';
  ctx.fillRect(0, 0, breedte, hoogte);
  ctx.imageSmoothingQuality = 'high';
  ctx.drawImage(img, 0, 0, breedte, hoogte);
  return new Promise((resolve, reject) => {
    canvas.toBlob(
      (blob) => {
        // Geheugen van het canvas direct vrijgeven (belangrijk op de iPhone).
        canvas.width = 0;
        canvas.height = 0;
        if (!blob) return reject(new Error('Foto verkleinen is mislukt.'));
        blob.arrayBuffer().then((data) => resolve({ data, breedte, hoogte }), reject);
      },
      'image/jpeg',
      kwaliteit
    );
  });
}

/** Geeft een verkleinde JPEG (max. 1600 px) en een klein voorbeeld terug. */
export async function verkleinFoto(bestand) {
  const img = await laadAfbeelding(bestand);
  const groot = await naarJpeg(img, MAX_GROOT, KWALITEIT_GROOT);
  const klein = await naarJpeg(img, MAX_KLEIN, KWALITEIT_KLEIN);
  return {
    type: 'image/jpeg',
    groot: groot.data,
    klein: klein.data,
    breedte: groot.breedte,
    hoogte: groot.hoogte,
  };
}

/** Maakt een tijdelijke link naar een opgeslagen foto om te tonen. */
export function fotoUrl(foto, formaat = 'klein') {
  const data = formaat === 'groot' ? foto.groot : foto.klein ?? foto.groot;
  return URL.createObjectURL(new Blob([data], { type: foto.type || 'image/jpeg' }));
}
