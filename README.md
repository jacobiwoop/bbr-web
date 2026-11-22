# bbr-web — sauvegarde

BBR1 (v220) dans le navigateur : le vrai `libmain.so` recompilé ARM64 → C → WebAssembly.
Copie de sauvegarde de `bbracing/work/recomp/web` (le code source du recompilateur reste dans
`bbracing/work/recomp/`, suivi dans `SUIVI_WEB.md`).

## Lancer

```sh
python3 -I serve.py 8080      # sert dist/ avec COOP/COEP, sur 127.0.0.1 seulement
```

puis ouvrir `http://localhost:8080/` (Chrome, Chromium ou Brave ; WebGL 2).
Options d'URL : `?auto` (lance sans clic), `?journal` (journal à l'écran), `?env=NOM=val,...`.

## Contenu

| Fichier | Rôle |
|---|---|
| `dist/` | ce qui est servi : `index.html`, `bbr.js`, `bbr.wasm`, `bbr_jeu.zip`, `sw.js`, manifeste, icônes, `shaders.json` |
| `index.html`, `sw.js`, `manifest.webmanifest`, icônes | sources de la page (copiées dans `dist/` par `build_web.sh`) |
| `serve.py` | mini serveur local avec les en-têtes COOP/COEP (threads WebAssembly) |
| `build_web.sh` | construction emscripten (sur le serveur aiko, `~/bbr_web/recomp`) |
| `preparer_paquet.py` | fabrique `dist/bbr_jeu.zip` depuis l'APK |
| `tools/` | outils de diagnostic (extraction des shaders…) |

Sauvegarde du 2026-11-22.
