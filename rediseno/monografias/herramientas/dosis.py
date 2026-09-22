#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""dosis.py "<consulta>" [n]
Baja resumenes y deja solo los que declaran una pauta con unidad.
Imprime la FRASE que contiene la dosis, para poder citarla literal."""
import sys, re
sys.stdout.reconfigure(encoding='utf-8')
from nlm import esearch, efetch

q = sys.argv[1]
n = int(sys.argv[2]) if len(sys.argv) > 2 else 60
DOSIS = re.compile(
    r'\d[\d.,\s]*\s*(?:mg|µg|μg|ug|ng|pg|nmol|µmol|μmol|mmol|IU|U)\s*'
    r'(?:/|·|\s?per\s)\s*(?:kg|g|ml|mL|L|day|d\b)', re.I)
UNI = re.compile(r'\d[\d.,]*\s*(?:mg|µg|μg|ng|nmol|µmol)\b', re.I)

cnt, ids = esearch(q, n)
print('CONSULTA: %s  COUNT=%d  bajados=%d' % (q, cnt, len(ids)))
print('=' * 78)
for i in ids:
    a = efetch([i]).get(i)
    if not a or not a['abstract']:
        continue
    frases = re.split(r'(?<=[.;]) +', a['abstract'])
    hit = [f for f in frases if DOSIS.search(f) or UNI.search(f)]
    if not hit:
        continue
    tp = 'REVIEW' if 'Review' in a['tipos'] else (
        'ENSAYO' if any('Trial' in t for t in a['tipos']) else 'art')
    print('PMID %-9s %-4s %-6s %s' % (i, a['anio'], tp, a['titulo'][:95]))
    print('   %s | %s' % (a['revista'][:45], ', '.join(a['autores'][:3])))
    for f in hit[:3]:
        print('   >> %s' % f.strip()[:330])
    print()
