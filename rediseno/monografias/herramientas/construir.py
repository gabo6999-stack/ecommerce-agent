#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Construye rediseno/monografias/datos/<slug>.json

REGLA DURA: ninguna fila sale al JSON si su PMID no se verifica contra PubMed
(efetch). Los campos titulo/autores/revista/anio NO se escriben a mano: se
copian de lo que devuelve PubMed. Si un PMID no responde, el script ABORTA.
"""
import json, os, sys, datetime
sys.stdout.reconfigure(encoding='utf-8')
from nlm import efetch

HOY = '2026-09-22'
SALIDA = r'C:\Users\gabom\Proyectos\ecommerce-agent\rediseno\monografias\datos'
os.makedirs(SALIDA, exist_ok=True)

PIE_CITA = ('Los valores anteriores son los que publican los autores en cada '
            'referencia. Describen lo que hicieron esos estudios, no son una '
            'recomendación, y las dosis de modelos animales no se extrapolan '
            'directamente a otras especies. El diseño de cualquier protocolo '
            'experimental queda a criterio del investigador responsable.')

NO_REPORTADO = ('no reportado en el resumen — pendiente de comprobar en el '
                'texto completo')

PALABRAS_PROHIBIDAS = ['farmacia', 'refrigeración durante el transporte',
                       'refrigeracion durante el transporte']
# Compuerta 6: nada de conversion a persona.
ROJAS = ['equivalente humano', 'alométric', 'alometric', 'factor de escalamiento',
         'para un adulto de', 'mg al día para', 'dosis recomendada',
         'se recomienda', 'tu protocolo', 'calibre de aguja']

_cache = {}


def verificar(pmids):
    """Devuelve dict pmid -> metadatos de PubMed. Aborta si falta alguno."""
    faltan = [p for p in pmids if p not in _cache]
    for i in range(0, len(faltan), 15):
        _cache.update(efetch(faltan[i:i + 15]))
    fallidos = [p for p in pmids if p not in _cache or not _cache[p]['titulo']]
    if fallidos:
        raise SystemExit('ABORTADO: PMID no verificables en PubMed: %s' % fallidos)
    return _cache


def guardas(obj, slug):
    """Compuertas 6, 7 y 14 sobre el texto que va al JSON."""
    txt = json.dumps(obj, ensure_ascii=False).lower()
    problemas = []
    for p in PALABRAS_PROHIBIDAS:
        if p in txt:
            problemas.append('PALABRA PROHIBIDA: %s' % p)
    for r in ROJAS:
        if r in txt:
            problemas.append('FRASE DE PAUTA/CONVERSION: %s' % r)
    if problemas:
        raise SystemExit('ABORTADO (%s): %s' % (slug, problemas))


def construir(m):
    slug = m['slug']
    pmids = [f['pmid'] for f in m.get('protocolos', [])] + \
            [e['pmid'] for e in m.get('evidencia_extra', [])]
    meta = verificar(sorted(set(pmids)))

    estudios, protocolos = [], []
    vistos = set()
    for f in m.get('protocolos', []):
        a = meta[f['pmid']]
        if f['pmid'] not in vistos:
            vistos.add(f['pmid'])
            estudios.append({
                'pmid': f['pmid'],
                'url': 'https://pubmed.ncbi.nlm.nih.gov/%s/' % f['pmid'],
                'titulo': a['titulo'], 'autores': a['autores'][:6],
                'revista': a['revista'], 'anio': a['anio'],
                'tipos_publicacion': a['tipos'],
                'especie_o_modelo': f['modelo'],
                'que_midieron': f['desenlace'],
                'verificado_en_pubmed': True,
                'fecha_verificacion': HOY,
            })
        protocolos.append({
            'estudio': f['estudio'],
            'pmid': f['pmid'],
            'pmid_url': 'https://pubmed.ncbi.nlm.nih.gov/%s/' % f['pmid'],
            'modelo': f['modelo'],
            'via': f['via'],
            'pauta_reportada': f['pauta'],
            'desenlace_medido': f['desenlace'],
        })
    for e in m.get('evidencia_extra', []):
        a = meta[e['pmid']]
        estudios.append({
            'pmid': e['pmid'],
            'url': 'https://pubmed.ncbi.nlm.nih.gov/%s/' % e['pmid'],
            'titulo': a['titulo'], 'autores': a['autores'][:6],
            'revista': a['revista'], 'anio': a['anio'],
            'tipos_publicacion': a['tipos'],
            'especie_o_modelo': e.get('modelo', 'n/a'),
            'que_midieron': e['nota'],
            'solo_seccion_evidencia': True,
            'motivo_fuera_de_tabla': e['motivo'],
            'verificado_en_pubmed': True,
            'fecha_verificacion': HOY,
        })

    out = {
        'slug': slug,
        'nombre': m['nombre'],
        'producto': m['producto'],
        'plantilla': m.get('plantilla', 'completa'),
        'identidad': m['identidad'],
        'estado_evidencia': m['estado_evidencia'],
        'regulatorio': m['regulatorio'],
        'estudios': estudios,
        'protocolos_investigacion_publicados': {
            'encabezado': 'Protocolos de investigación publicados',
            'columnas': ['Estudio', 'Modelo', 'Vía', 'Pauta reportada',
                         'Desenlace medido'],
            'filas': protocolos,
            'pie_de_cita': PIE_CITA,
        },
        'avisos': m.get('avisos', []),
        'pendientes': m.get('pendientes', []),
        'generado': HOY,
        'fuentes': ['PubMed E-utilities (esearch/efetch), NCBI, %s' % HOY,
                    'PubChem PUG REST, NCBI, %s' % HOY],
    }
    guardas(out, slug)
    p = os.path.join(SALIDA, slug + '.json')
    with open(p, 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print('%-22s %2d filas / %2d estudios -> %s' % (
        slug, len(protocolos), len(estudios), p))
    return out


if __name__ == '__main__':
    from datos_moleculas import MOLECULAS
    tot = []
    for m in MOLECULAS:
        tot.append(construir(m))
    print('\n%d moleculas escritas' % len(tot))
