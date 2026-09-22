#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Estado de la evidencia por molecula: conteos en PubMed."""
import sys, json
sys.stdout.reconfigure(encoding='utf-8')
from nlm import esearch

MOL = {
    'ghk-cu':        '"GHK-Cu" OR "glycyl-histidyl-lysine" OR "copper tripeptide"',
    'bpc-157':       '"BPC 157"',
    'tb-500':        '"TB-500" OR "TB4 fragment" OR "Ac-SDKP" OR "thymosin beta 4"',
    'cagrilintida':  'cagrilintide',
    'cjc-1295':      '"CJC-1295"',
    'ipamorelina':   'ipamorelin',
    'sermorelina':   'sermorelin OR "GHRH(1-29)"',
    'timosina-a1':   '"thymosin alpha 1" OR thymalfasin',
    'selank':        'selank',
    'semaglutida':   'semaglutide',
    'tirzepatida':   'tirzepatide',
    'igf-1-lr3':     '"long R3 IGF-I" OR "LR3 IGF-I" OR "IGF-1 LR3"',
    'mots-c':        '"MOTS-c"',
    'retatrutida':   'retatrutide OR LY3437943',
    'nad':           '"nicotinamide adenine dinucleotide" AND (supplement* OR "NAD+ precursor")',
    'glutation':     'glutathione AND (intravenous OR oral supplementation)',
    'agua-bact':     '"bacteriostatic water" OR ("benzyl alcohol" AND preservative AND injection)',
}
res = {}
for k, q in MOL.items():
    tot = esearch(q, 0)[0]
    ct = esearch('(%s) AND clinical trial[pt]' % q, 0)[0]
    rct = esearch('(%s) AND randomized controlled trial[pt]' % q, 0)[0]
    hum = esearch('(%s) AND humans[mh]' % q, 0)[0]
    res[k] = {'consulta': q, 'total': tot, 'clinical_trial_pt': ct,
              'rct_pt': rct, 'humans_mh': hum}
    print('%-14s total=%-6s CT=%-5s RCT=%-5s humanos=%-6s  << %s' % (k, tot, ct, rct, hum, q))
json.dump(res, open('estado_evidencia.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
