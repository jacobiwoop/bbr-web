"""Extrait les sources GLSL des matériaux et shaders compilés du jeu (Assets.apf du paquet).

    python3 -I web/tools/extraire_shaders.py [web/dist/bbr_jeu.zip] [web/dist/shaders.json]

Sortie locale seulement (données du jeu) : liste {nom, type: vs|fs, source}.
"""
import json, lzma, struct, sys, zipfile, zlib
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
paquet = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / 'dist/bbr_jeu.zip'
sortie = Path(sys.argv[2]) if len(sys.argv) > 2 else HERE / 'dist/shaders.json'

def decomp(blob, usize, flags):
    hi = flags >> 16 & 0xffff
    if hi == 0: return blob
    if hi == 1: return zlib.decompress(blob)
    if hi == 2:
        return lzma.LZMADecompressor(lzma.FORMAT_ALONE).decompress(blob[:5] + struct.pack('<Q', usize) + blob[5:])[:usize]
    raise ValueError(f'codec {hi}')

raw = zipfile.ZipFile(paquet).read('assets/Assets.apf')
assert raw[:4] == b'FPUV'
_v, doff, _n, dsize, _h = struct.unpack_from('<IIIII', raw, 4)
p, fin, res = doff, doff + dsize, []
while p < fin:
    z = raw.index(b'\0', p); nom = raw[p:z].decode('ascii', 'replace'); p = z + 1
    if p + 20 > fin: break
    off, us, cs, _hh, fl = struct.unpack_from('<IIIII', raw, p); p += 20
    if not nom.startswith(('VuMaterialAsset/', 'VuCompiledShaderAsset/')): continue
    d = decomp(raw[off:off + cs], us, fl)
    # chaînes préfixées par leur longueur (u32) contenant « main( »
    k = 0
    while k + 4 < len(d):
        n = struct.unpack_from('<I', d, k)[0]
        if 16 < n < 200000 and k + 4 + n <= len(d):
            s = d[k + 4:k + 4 + n]
            if b'main(' in s and all(32 <= c < 127 or c in (0, 9, 10, 13) for c in s):
                # un bloc = plusieurs sources séparées par des NUL
                for i, t in enumerate(x.decode() for x in s.split(b'\0') if b'main(' in x):
                    res.append({'nom': nom, 'bloc': k, 'i': i, 'type': 'vs' if 'gl_Position' in t else 'fs', 'source': t})
                k += 4 + n; continue
        k += 1
sortie.write_text(json.dumps(res))
print(f'{len(res)} shaders ({sum(r["type"]=="vs" for r in res)} vs) dans {len({r["nom"] for r in res})} assets -> {sortie}')
print('LavaFire :', [(r['type'], len(r['source'])) for r in res if 'LavaFire' in r['nom']])
