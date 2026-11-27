#!/bin/sh
# Compile le jeu en WebAssembly 64 bits (Memory64) avec emscripten. À lancer SUR aiko, dans
# ~/bbr_web/recomp (copie de work/recomp SANS game_libs/ ni pc_data/, mais AVEC out/gen/*/fns_*.c,
# out/gen/*/ftab.c, out/gen/*/decls.h, out/gen/link/*.c).
#   . ~/bbr_web/emsdk/emsdk_env.sh && sh web/build_web.sh
# Sortie : web/dist/ (index.html, bbr.js, bbr.wasm) à servir avec COOP/COEP (web/serve.py).
set -e
cd "$(dirname "$0")/.."
G=out/gen
O=web/obj
mkdir -p $O web/dist
JOBS=${JOBS:-$(nproc)}
# -ffp-contract=off obligatoire (DESIGN.md) ; Memory64 : pointeurs 64 bits comme le jeu (LP64).
# Par défaut : WebAssembly 32 bits (-sMEMORY64=2 à l'édition de liens : le C garde des pointeurs de
# 8 octets comme le jeu, binaryen abaisse en wasm32) et SANS JSPI (boucle image par image,
# translate.CEDER) -> Safari/iPhone aussi. JSPI=1 : ancienne version wasm64 + JSPI (Chrome seulement).
if [ -n "${JSPI:-}" ]; then LIEN="-sMEMORY64=1 -sJSPI=1 -sMAXIMUM_MEMORY=4GB"; DJSPI=-DRECOMP_JSPI
else LIEN="-sMEMORY64=2 -sMAXIMUM_MEMORY=2GB"; DJSPI=; fi
CF="-O2 -sMEMORY64=1 -pthread -fno-strict-aliasing -ffp-contract=off -fwrapv -w -I rt --use-port=sdl3 -sUSE_ZLIB=1"
echo "== objets des bibliothèques traduites ($JOBS travaux)"
IDS="main cxx fmod fstudio"
[ -f $G/lan/ftab.c ] && IDS="$IDS lan"      # module LAN traduit (pc/build_pc.sh LAN=1)
for id in $IDS; do
    mkdir -p $O/$id
    ls $G/$id/fns_*.c $G/$id/ftab.c
done | xargs -P "$JOBS" -I{} sh -c '
    src={}; id=$(basename $(dirname $src)); o='"$O"'/$id/$(basename $src .c).o
    [ "$o" -nt "$src" ] || emcc '"$CF"' -I '"$G"'/$id -c "$src" -o "$o" || exit 255'
# TRACE_MAIN=1 : libmain compilée avec la trace des fonctions (anneau ; BBR_TRACE_N=<n> pour l'afficher
# lors d'un arrêt ou d'une boîte de message). Objets à part : web/obj/main_trace.
MAIN_O=$O/main
if [ -n "${TRACE_MAIN:-}" ]; then
    MAIN_O=$O/main_trace
    mkdir -p $MAIN_O
    ls $G/main/fns_*.c $G/main/ftab.c | xargs -P "$JOBS" -I{} sh -c '
        src={}; o='"$MAIN_O"'/$(basename $src .c).o
        [ "$o" -nt "$src" ] || emcc '"$CF"' -DRECOMP_TRACE_ON -DRECOMP_LIB_ID=0 -I '"$G"'/main -c "$src" -o "$o" || exit 255'
fi
echo "== runtime et ponts"
mkdir -p $O/rt
for f in rt/*.c $G/link/glue.c $G/link/host_table.c; do
    o=$O/rt/$(basename "$f" .c).o
    [ "$o" -nt "$f" ] && [ "$o" -nt web/build_web.sh ] || emcc $CF $DJSPI -c "$f" -o "$o"
done
echo "== édition de liens"
emcc $CF $LIEN ${LDEXTRA:-} -o web/dist/bbr.js $O/rt/*.o $MAIN_O/*.o $O/cxx/*.o $O/fmod/*.o $O/fstudio/*.o $([ -f $G/lan/ftab.c ] && ls $O/lan/*.o) \
    -sMAX_WEBGL_VERSION=2 -sMIN_WEBGL_VERSION=2 -sFULL_ES3=1 -sGL_ENABLE_GET_PROC_ADDRESS=1 -lEGL \
    -sALLOW_MEMORY_GROWTH=1 -sINITIAL_MEMORY=512MB \
    -sSTACK_SIZE=8MB -sDEFAULT_PTHREAD_STACK_SIZE=2MB -sPTHREAD_POOL_SIZE=24 \
    -sINVOKE_RUN=0 -sEXIT_RUNTIME=0 -sENVIRONMENT=web,worker \
    -sEXPORTED_RUNTIME_METHODS=FS,ENV,callMain,IDBFS \
    -lidbfs.js \
    -sERROR_ON_UNDEFINED_SYMBOLS=1
cp web/index.html web/sw.js web/manifest.webmanifest web/dist/ && cp web/icone* web/dist/ 2>/dev/null || true
ls -la web/dist
