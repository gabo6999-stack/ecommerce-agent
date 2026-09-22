#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""triage.py "<consulta>" [n]  -> lista compacta para elegir candidatos."""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from nlm import esearch, efetch

q = sys.argv[1]
n = int(sys.argv[2]) if len(sys.argv) > 2 else 25
cnt, ids = esearch(q, n)
print('CONSULTA: %s   COUNT=%d  (mostrando %d)' % (q, cnt, len(ids)))
d = efetch(ids)
for i in ids:
    a = d.get(i)
    if not a:
        continue
    tp = 'REVIEW' if 'Review' in a['tipos'] else ('CT' if any('Trial' in t for t in a['tipos']) else 'art')
    print('%-9s %-4s %-6s %-28s %s' % (i, a['anio'], tp, a['revista'][:28], a['titulo'][:105]))
