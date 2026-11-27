// Service worker de Beach Buggy Racing (PWA) : rend la page et le code du jeu disponibles hors
// ligne. Stratégie « réseau d'abord » (le serveur local répond vite, et on suit ainsi chaque
// nouvelle version), copie de secours dans le cache. Une copie n'est réécrite que si la version
// (Last-Modified + taille) change : bbr.wasm fait 44 Mo.
// Le paquet du jeu (bbr_jeu.zip) n'est pas géré ici : la page le garde elle-même (cache
// « bbr-paquet »), avec sa barre de progression.
const CACHE = 'bbr-appli';
const COQUILLE = ['./', 'index.html', 'bbr.js', 'bbr.wasm', 'manifest.webmanifest',
                  'icone.svg', 'icone-192.png', 'icone-512.png'];

self.addEventListener('install', e => { self.skipWaiting(); });
self.addEventListener('activate', e => { e.waitUntil(self.clients.claim()); });

const version = r => (r.headers.get('Last-Modified') || '') + '|' + (r.headers.get('Content-Length') || '');

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== location.origin) return;
  // Page (avec ou sans ?auto, ?journal...) -> une seule entrée « index.html ».
  let cle = url.pathname.split('/').pop() || 'index.html';
  if (req.mode === 'navigate') cle = 'index.html';
  if (!COQUILLE.includes(cle) || cle === 'bbr_jeu.zip') return;
  e.respondWith((async () => {
    const cache = await caches.open(CACHE);
    try {
      const r = await fetch(req);
      if (r.ok && r.status === 200) {
        const garde = await cache.match(cle);
        // Lu en entier puis rangé : cache.put() d'une réponse en flux échoue avec le serveur
        // local (« Cache.put() encountered a network error »), pas avec un tampon.
        if (!garde || version(garde) !== version(r)) {
          const copie = r.clone();
          e.waitUntil(copie.arrayBuffer().then(b => cache.put(cle, new Response(b, { status: 200, headers: copie.headers }))).catch(() => {}));
        }
      }
      return r;
    } catch (err) {
      const garde = await cache.match(cle);
      if (garde) return garde;
      throw err;
    }
  })());
});
