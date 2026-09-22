#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audita los JSON emitidos contra la lista de 16 comprobaciones,
en todo lo que se puede comprobar por codigo."""
import json, os, re, sys, glob
sys.stdout.reconfigure(encoding='utf-8')

D = r'C:\Users\gabom\Proyectos\ecommerce-agent\rediseno\monografias\datos'
NR = 'no reportado en el resumen'
ROJAS = ['equivalente humano', 'alométric', 'alometric', 'factor de escalamiento',
         'mg al día para', 'dosis recomendada', 'se recomienda', 'tu protocolo',
         'calibre de aguja', 'ciclos de tratamiento', 'semanas de ciclo',
         'ciclo de descanso', 'entre ciclos', 'semanas de descanso', 'farmacia',
         'refrigeración durante el transporte']
UNIDAD = re.compile(r'\d[\d.,\s×⁻⁰¹²³⁴⁵⁶⁷⁸⁹^-]*\s*(?:mg|µg|μg|ng|pg|g|nmol|µmol|mmol|mol|UI|IU|Gy|%)', re.I)
ESPECIE = re.compile(r'rat[óa]|rat[oa]s|rat\b|ratón|ratones|humanos?|perro|beagle|'
                     r'cerdo|ovino|feto|in vitro|c[ée]lulas|fibroblast|neonat|'
                     r'reci[ée]n nacid|pacientes|adultos|ni[ñn]os|varones|mujeres', re.I)

fallos, avisos, filas_tot, sin_unidad = [], [], 0, 0
resumen = []

for p in sorted(glob.glob(os.path.join(D, '*.json'))):
    d = json.load(open(p, encoding='utf-8'))
    slug = d['slug']
    bloque = d['protocolos_investigacion_publicados']
    filas = bloque['filas']
    filas_tot += len(filas)
    con_unidad = 0
    nr_celdas = 0

    # C13: pie de cita literal
    if not bloque['pie_de_cita'].startswith('Los valores anteriores son los que publican'):
        fallos.append('%s: pie de cita alterado' % slug)
    # C10: cabeceras y orden
    if bloque['columnas'] != ['Estudio', 'Modelo', 'Vía', 'Pauta reportada',
                             'Desenlace medido']:
        fallos.append('%s: columnas fuera de plantilla' % slug)
    # C12: aviso de estado con consulta que lo demuestre
    ee = d.get('estado_evidencia', {})
    if not ee.get('texto') or not ee.get('consultas_pubmed'):
        fallos.append('%s: falta aviso de estado de la evidencia o su consulta' % slug)

    for f in filas:
        # C1 y C2: PMID presente y enlazado
        if not f.get('pmid') or not f['pmid_url'].startswith(
                'https://pubmed.ncbi.nlm.nih.gov/'):
            fallos.append('%s: fila sin PMID enlazado (%s)' % (slug, f['estudio'][:40]))
        # C3: especie o in vitro en la columna Modelo
        if not ESPECIE.search(f['modelo']):
            fallos.append('%s: Modelo sin especie -> %s' % (slug, f['modelo'][:70]))
        # C11: ninguna celda vacia ni con guion suelto
        for k in ('estudio', 'modelo', 'via', 'pauta', 'desenlace'):
            v = f.get(k if k != 'pauta' else 'pauta_reportada',
                      f.get(k if k != 'desenlace' else 'desenlace_medido', ''))
        for k, v in f.items():
            if isinstance(v, str) and (not v.strip() or v.strip() in ('-', '—')):
                fallos.append('%s: celda vacia %s' % (slug, k))
        # C5: pauta con unidad, o la formula literal de "no reportado"
        pa = f['pauta_reportada']
        if UNIDAD.search(pa):
            con_unidad += 1
        elif NR in pa:
            nr_celdas += 1
        else:
            avisos.append('%s: pauta sin unidad ni formula NR -> %s' % (slug, pa[:80]))
        if NR in f['via']:
            nr_celdas += 1

    # C6, C7, C14: barrido de frases rojas sobre TODO el archivo
    txt = json.dumps(d, ensure_ascii=False).lower()
    for r in ROJAS:
        if r in txt:
            fallos.append('%s: FRASE ROJA "%s"' % (slug, r))

    # C1 bis: estudios verificados
    nv = [e['pmid'] for e in d['estudios'] if not e.get('verificado_en_pubmed')]
    if nv:
        fallos.append('%s: estudios sin verificar %s' % (slug, nv))

    sin_unidad += nr_celdas
    resumen.append((slug, len(filas), con_unidad, nr_celdas,
                    len(d['estudios']), len(d.get('pendientes', [])),
                    d.get('plantilla', 'completa')))

print('%-22s %5s %6s %5s %8s %10s  %s' % (
    'molecula', 'filas', 'c/dosis', 'NR', 'estudios', 'pendientes', 'plantilla'))
print('-' * 84)
for r in resumen:
    print('%-22s %5d %6d %5d %8d %10d  %s' % r)
print('-' * 84)
print('TOTAL: %d filas, %d estudios verificados en PubMed' % (
    filas_tot, sum(r[4] for r in resumen)))
print('       %d filas con dosis/unidad explicita, %d celdas con la formula NR' % (
    sum(r[2] for r in resumen), sin_unidad))
print()
print('FALLOS (%d):' % len(fallos))
for f in fallos:
    print('  X %s' % f)
print('AVISOS (%d):' % len(avisos))
for a in avisos:
    print('  ! %s' % a)
