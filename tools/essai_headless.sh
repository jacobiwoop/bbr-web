#!/bin/sh
# Essai du jeu dans un Chromium sans fenêtre (n'interfère pas avec le bureau) ; journal du jeu
# filtré sur la sortie. Prérequis : python3 -I web/serve.py 8080 lancé (web/dist complet).
# Usage : sh web/tools/essai_headless.sh [secondes] [paramètres d'URL en plus, ex. &env=BBR_TRACE_SDL=1]
T=${1:-60}
D=${TMPDIR:-/tmp}/bbr_chromium.$$
mkdir -p "$D"
timeout "$T" chromium --headless=new --user-data-dir="$D/profil" --enable-logging=stderr \
    --use-angle=swiftshader --enable-unsafe-swiftshader --remote-debugging-port=${CDP_PORT:-9333} \
    "http://localhost:8080/?auto&journal$2" 2>&1 | grep --line-buffered -E 'CONSOLE|RuntimeError|Uncaught' |
    sed -u -E 's/^.*CONSOLE[^"]*"//; s/", source: .*$//'
rm -rf "$D"
