#!/usr/bin/env python3
"""Prépare le paquet du jeu pour la version navigateur, à partir des APK du joueur.

    python3 -I web/preparer_paquet.py <base.apk> <split_config.arm64_v8a.apk> [sortie.zip]

Ne garde que l'essentiel :
  - assets/Assets.apf       : toutes les données du jeu (circuits, voitures, sons...) ;
  - lib/arm64-v8a/<4 .so>   : le code est déjà traduit dans bbr.wasm, mais leurs données
                              (tables, valeurs initiales) sont lues dans ces fichiers.
Zip sans compression (Assets.apf est déjà compressé) : le jeu lit les entrées en place.
Sortie par défaut : web/dist/bbr_jeu.zip. Ce paquet contient les fichiers du jeu : il reste chez
le joueur, on ne le publie jamais.
"""
import hashlib
import sys
import zipfile
from pathlib import Path

LIBS = ('libmain.so', 'libc++_shared.so', 'libfmod.so', 'libfmodstudio.so')
ASSETS = ('assets/Assets.apf',)
# Empreinte de libmain.so de la version traduite (v220, 2026.11.02) : le .wasm ne marche qu'avec elle.
LIBMAIN_SHA256 = '260d0054'

def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    base, split = Path(sys.argv[1]), Path(sys.argv[2])
    out = Path(sys.argv[3]) if len(sys.argv) > 3 else Path(__file__).resolve().parent / 'dist' / 'bbr_jeu.zip'
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix('.part')
    with zipfile.ZipFile(base) as zb, zipfile.ZipFile(split) as zs, \
         zipfile.ZipFile(tmp, 'w', zipfile.ZIP_STORED) as zo:
        for name in ASSETS:
            with zb.open(name) as src, zo.open(name, 'w') as dst:
                while blk := src.read(1 << 20):
                    dst.write(blk)
            print(f'  {name}')
        for lib in LIBS:
            data = zs.read(f'lib/arm64-v8a/{lib}')
            if lib == 'libmain.so' and not hashlib.sha256(data).hexdigest().startswith(LIBMAIN_SHA256):
                sys.exit('libmain.so ne correspond pas à la version traduite (v220 attendue)')
            zo.writestr(f'lib/arm64-v8a/{lib}', data)
            print(f'  lib/arm64-v8a/{lib}')
    tmp.replace(out)
    print(f'paquet : {out} ({out.stat().st_size / 1e6:.1f} Mo)')

if __name__ == '__main__':
    main()
