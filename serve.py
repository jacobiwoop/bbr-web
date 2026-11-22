"""Mini serveur du jeu : sert web/dist (index.html, bbr.js, bbr.wasm, bbr_jeu.zip) avec les en-têtes
COOP/COEP exigés par les threads WebAssembly (SharedArrayBuffer).

    python3 -I web/serve.py [port]          puis http://localhost:8080/

Écoute sur 127.0.0.1 seulement : bbr_jeu.zip contient les fichiers du jeu et ne doit pas être
exposé sur le réseau.
"""
import http.server
import sys
from functools import partial
from pathlib import Path


class H(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cross-Origin-Opener-Policy', 'same-origin')
        self.send_header('Cross-Origin-Embedder-Policy', 'require-corp')
        self.send_header('Cache-Control', 'no-cache')
        super().end_headers()

    def log_message(self, fmt, *args):      # journal court : seulement les erreurs
        if args and str(args[1])[:1] in '45':
            super().log_message(fmt, *args)


H.extensions_map['.wasm'] = 'application/wasm'
H.extensions_map['.webmanifest'] = 'application/manifest+json'
H.extensions_map['.svg'] = 'image/svg+xml'
port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
d = Path(__file__).resolve().parent / 'dist'
for f in ('index.html', 'bbr.js', 'bbr.wasm', 'bbr_jeu.zip'):
    if not (d / f).exists():
        print(f'manque : {d / f}' + ('  (python3 -I web/preparer_paquet.py base.apk split.apk)' if f == 'bbr_jeu.zip' else ''))
print(f'http://localhost:{port}/', flush=True)
http.server.ThreadingHTTPServer(('127.0.0.1', port), partial(H, directory=str(d))).serve_forever()
