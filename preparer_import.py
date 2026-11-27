#!/usr/bin/env python3
"""Fichiers à importer dans la page publiée sans le jeu (GitHub Pages) :
    python3 -I web/preparer_import.py [--complet]

Par défaut, produit deux archives dans web/dist/ pour limiter la taille des transferts :
  - bbr_code.zip (compressé DEFLATE 9) : bbr.js, bbr.wasm, libmain.so et libbbrlan.so ;
  - bbr_donnees.zip (SANS compression) : Assets.apf, libc++_shared.so, libfmod.so, libfmodstudio.so.
L'option --complet produit l'ancien fichier unique web/dist/bbr_navigateur.zip (STORED).

Ces fichiers contiennent le jeu : ils restent chez le joueur, on ne les publie jamais.
"""
import sys
import zipfile
from pathlib import Path

def main():
    D = Path(__file__).resolve().parent / 'dist'
    args = sys.argv[1:]
    complet = '--complet' in args
    if complet:
        args.remove('--complet')
        out = Path(args[0]) if args else D / 'bbr_navigateur.zip'
        tmp = out.with_suffix('.part')
        with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_STORED) as z:
            for n in ('bbr.js', 'bbr.wasm', 'bbr_jeu.zip'):
                p = D / n
                z.write(p, n)
                print(f'  {n} ({p.stat().st_size / 1e6:.1f} Mo)')
        tmp.replace(out)
        print(f'{out} ({out.stat().st_size / 1e6:.1f} Mo)')
        return

    code_out = D / 'bbr_code.zip'
    donnees_out = D / 'bbr_donnees.zip'
    jeu_zip = D / 'bbr_jeu.zip'

    if not jeu_zip.exists():
        sys.exit(f'Erreur : {jeu_zip} introuvable')

    with zipfile.ZipFile(jeu_zip) as zj:
        # 1. bbr_code.zip (compressé DEFLATE niveau 9)
        tmp_code = code_out.with_suffix('.part')
        with zipfile.ZipFile(tmp_code, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zc:
            for n in ('bbr.js', 'bbr.wasm'):
                p = D / n
                zc.write(p, n)
                print(f'  {n} ({p.stat().st_size / 1e6:.1f} Mo)')
            for n in ('lib/arm64-v8a/libmain.so', 'lib/arm64-v8a/libbbrlan.so'):
                if n in zj.namelist():
                    data = zj.read(n)
                    zc.writestr(n, data)
                    print(f'  {n} ({len(data) / 1e6:.1f} Mo)')
        tmp_code.replace(code_out)
        print(f'{code_out} ({code_out.stat().st_size / 1e6:.1f} Mo)\n')

        # 2. bbr_donnees.zip (STORED)
        tmp_donnees = donnees_out.with_suffix('.part')
        donnees = (
            'assets/Assets.apf',
            'lib/arm64-v8a/libc++_shared.so',
            'lib/arm64-v8a/libfmod.so',
            'lib/arm64-v8a/libfmodstudio.so',
        )
        with zipfile.ZipFile(tmp_donnees, 'w', zipfile.ZIP_STORED) as zd:
            for n in donnees:
                data = zj.read(n)
                zd.writestr(n, data)
                print(f'  {n} ({len(data) / 1e6:.1f} Mo)')
        tmp_donnees.replace(donnees_out)
        print(f'{donnees_out} ({donnees_out.stat().st_size / 1e6:.1f} Mo)')

if __name__ == '__main__':
    main()
