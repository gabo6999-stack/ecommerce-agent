#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Datos curados a mano, molecula por molecula.

Cada 'pauta' se copio del RESUMEN del articulo cuyo PMID va en la misma fila.
Ningun numero de este archivo procede de una revision, de un resumen de
terceros ni de una conversion. Los campos titulo/autores/revista NO estan aqui:
los rellena construir.py desde PubMed, para que no se puedan inventar.

NR = 'no reportado en el resumen - pendiente de comprobar en el texto completo'
"""
NR = ('no reportado en el resumen — pendiente de comprobar en el texto '
      'completo')
PC = 'PubChem PUG REST, consultado el 2026-09-22'

MOLECULAS = []

# ───────────────────────────────────────────── 1. GHK-Cu (producto 2823)
MOLECULAS.append({
 'slug': 'ghk-cu', 'nombre': 'GHK-Cu',
 'producto': {'id': 2823, 'nombre': 'GHK-Cu',
              'url': 'https://peptidosysuplementos.mx/product/ghk-cu',
              'presentacion': '100 mg'},
 'identidad': {
   'nombre_quimico': 'Complejo de cobre(II) con el tripéptido glicil-L-histidil-L-lisina',
   'inn': 'No tiene DCI. El péptido libre GHK aparece en registros como «prezatide»; '
          'la sal de cobre, como «prezatide acetato de cobre»',
   'sinonimos': ['GHK-Cu', 'Copper tripeptide-1', 'Copper peptide',
                 'Gly-His-Lys-Cu(II)',
                 '[N2-(N-glicil-L-histidil)-L-lisinato(2-)]cobre'],
   'cas': {'peptido_libre_GHK': '49557-75-7', 'complejo_de_cobre': NR},
   'formula_molecular': {'complejo_GHK-Cu': 'C14H21CuN6O4-',
                         'peptido_libre_GHK': 'C14H24N6O4'},
   'peso_molecular_da': {'complejo_GHK-Cu': '400.90', 'peptido_libre_GHK': '340.38'},
   'secuencia_aminoacidos': 'Gly-His-Lys (tripéptido)',
   'pubchem_cid': {'complejo': 139035031, 'peptido_libre': 73587},
   'fuente_identidad': PC,
 },
 'estado_evidencia': {
   'escalon': 'preclínica amplia + ensayos clínicos tópicos pequeños, con resultados negativos en los desenlaces objetivos',
   'texto': 'La investigación de GHK-Cu es sobre todo preclínica y tópica. En PubMed, '
            'la consulta «"GHK-Cu" OR "glycyl-histidyl-lysine" OR "copper tripeptide"» '
            'devuelve 198 registros, de los que solo 3 están tipificados como ensayo '
            'clínico (consulta del 22-sep-2026). De esos ensayos, los dos hechos en '
            'personas midieron desenlaces objetivos y no encontraron diferencia frente '
            'al comparador.',
   'consultas_pubmed': [
     {'consulta': '"GHK-Cu" OR "glycyl-histidyl-lysine" OR "copper tripeptide"',
      'resultados': 198, 'fecha': '2026-09-22'},
     {'consulta': '(lo anterior) AND clinical trial[pt]', 'resultados': 3,
      'fecha': '2026-09-22'},
   ],
 },
 'regulatorio': {
   'aprobacion': 'Sin aprobación como medicamento. Se usa como ingrediente cosmético tópico.',
   'wada': 'No nombrado en la Lista de Prohibiciones. Queda sujeto a la cláusula S0 '
           '(sustancia sin aprobación sanitaria vigente para uso humano) si se administra '
           'por vía sistémica. Verificar caso por caso.',
   'fuente_wada': 'Lista de Prohibiciones WADA vigente 2026, secciones S0 y S2; '
                  'lectura interna del PDF contrastada con USADA (2026-08-29). '
                  'La lista cambia cada 1 de enero: revalidar antes de publicar.',
 },
 'protocolos': [
  {'estudio': 'Fibrosis pulmonar inducida por bleomicina',
   'pmid': '31809714',
   'modelo': 'Ratón C57BL/6j; fibrosis pulmonar inducida con bleomicina 3 mg/kg por instilación traqueal',
   'via': 'Intraperitoneal',
   'pauta': '0,2, 2 y 20 µg/g/día en 0,5 mL de PBS, en días alternos; evaluación a los 21 días del reto con bleomicina',
   'desenlace': 'Histología pulmonar; TNF-α, IL-6 y actividad de MPO en lavado broncoalveolar; depósito de colágeno; marcadores de transición epitelio-mesénquima (α-SMA, fibronectina); vías NF-κB p65, Nrf2 y TGFβ1/Smad2/3'},
  {'estudio': 'Reconstrucción de ligamento cruzado anterior',
   'pmid': '25731775',
   'modelo': 'Rata; 72 animales con reconstrucción unilateral de LCA, aleatorizados a salino, 0,3 mg/mL o 3 mg/mL (n = 24 por grupo)',
   'via': 'Intraarticular',
   'pauta': '0,3 o 3 mg/mL, una vez por semana durante 4 semanas, empezando en la semana 2 tras la cirugía; extracción a las 6 o 12 semanas',
   'desenlace': 'Diferencia lado a lado en laxitud de rodilla, rigidez y carga última del complejo del injerto en prueba de arrancamiento, análisis de marcha e histología. Comparador: salino'},
  {'estudio': 'Colgajo dorsal irradiado (resultado negativo)',
   'pmid': '23744835',
   'modelo': 'Rata Sprague-Dawley; colgajo dorsal de 2 × 8 cm de base craneal, tras irradiación dorsal y 28 días de recuperación; 13 tratadas y 10 control',
   'via': 'Tópica (gel)',
   'pauta': 'Gel de GHK-Cu dos veces al día durante 10 días; concentración ' + NR,
   'desenlace': 'Área isquémica por análisis digital de imagen; vasos teñidos con caveolina-1 y área luminal media; expresión de VEGF en fibroblastos. Comparador: pomada aquafílica. Sin diferencias significativas en ningún desenlace'},
  {'estudio': 'Piel tras resurfacing con láser de CO2 (ensayo aleatorizado)',
   'pmid': '16847171',
   'modelo': 'Humanos; 13 pacientes que completaron el estudio, aleatorizados con o sin GHK-Cu tras resurfacing periorbicular con láser de CO2',
   'via': 'Tópica (productos de cuidado de la piel)',
   'pauta': 'Régimen postratamiento con o sin GHK-Cu; evaluación a 12 semanas. Concentración y frecuencia ' + NR,
   'desenlace': 'Eritema medido por software y por evaluadores cegados; mejoría de arrugas y calidad global de la piel a 12 semanas; cuestionario validado. Sin diferencias objetivas entre grupos; la satisfacción declarada por el paciente sí difirió (p = 0,04)'},
  {'estudio': 'Úlceras de estasis venosa (ensayo aleatorizado con evaluador cegado)',
   'pmid': '1495150',
   'modelo': 'Humanos; 86 pacientes evaluables con úlceras de estasis venosa crónicas',
   'via': 'Tópica (crema)',
   'pauta': 'Crema con complejo tripéptido-cobre al 0,4 %, frente a sulfadiazina de plata al 1 % y frente a vehículo inerte',
   'desenlace': 'Reducción del tamaño de la úlcera. La sulfadiazina de plata redujo el tamaño de forma estadísticamente significativa frente a las otras dos; no hubo diferencia entre el complejo de cobre y el placebo'},
  {'estudio': 'Fibroblastos dérmicos humanos normales e irradiados',
   'pmid': '15655171',
   'modelo': 'In vitro; líneas primarias de fibroblastos dérmicos humanos obtenidos de pacientes irradiados por cáncer de cabeza y cuello, y de controles normales, en medio sin suero ni factores de crecimiento',
   'via': 'In vitro',
   'pauta': 'GHK-Cu 1 × 10⁻⁹ mol/L',
   'desenlace': 'Recuento celular y tiempo de duplicación poblacional; producción autocrina de bFGF, TGF-β1 y VEGF'},
 ],
 'avisos': [
   'Los dos ensayos en personas de esta lista (PMID 16847171 y 1495150) NO encontraron '
   'diferencia frente al comparador en los desenlaces objetivos. La monografía debe '
   'decirlo con esas palabras: es el dato que distingue una página honesta de un folleto.',
   'La mayoría de la literatura de GHK-Cu es tópica o de vehículos (hidrogeles, '
   'liposomas, microagujas). No confundir una formulación con la molécula.',
 ],
 'pendientes': [
   'El número CAS del COMPLEJO GHK-Cu no aparece en la lista de sinónimos de PubChem '
   '(CID 139035031). El 49557-75-7 corresponde al péptido libre GHK. No publicar un CAS '
   'para el complejo hasta confirmarlo en una fuente citable.',
   'Las concentraciones de los estudios tópicos (23744835, 16847171) no constan en el '
   'resumen. Si se quieren en la tabla, hay que sacarlas del texto completo.',
 ],
})

# ───────────────────────────────────────────── 2. BPC-157 (producto 2464)
MOLECULAS.append({
 'slug': 'bpc-157', 'nombre': 'BPC-157',
 'producto': {'id': 2464, 'nombre': 'BPC-157',
              'url': 'https://peptidosysuplementos.mx/product/bpc-157',
              'presentacion': '5 mg y 10 mg'},
 'identidad': {
   'nombre_quimico': 'Pentadecapéptido derivado de una proteína del jugo gástrico humano',
   'inn': 'No tiene DCI',
   'sinonimos': ['BPC 157', 'Pentadecapeptide BPC 157', 'Bepecin', 'BPC 15',
                 'PL-10', 'PLD-116', 'PL-14736', 'Body protection compound 157'],
   'cas': '137525-51-0',
   'formula_molecular': 'C62H98N16O22',
   'peso_molecular_da': '1419.5',
   'secuencia_aminoacidos': 'Gly-Glu-Pro-Pro-Pro-Gly-Lys-Pro-Ala-Asp-Asp-Ala-Gly-Leu-Val (GEPPPGKPADDAGLV)',
   'pubchem_cid': 9941957,
   'inchikey': 'HEEWEZGQMLZMFE-RKGINYAYSA-N',
   'fuente_identidad': PC + '; la secuencia y el peso molecular (1419) los repite '
                            'literalmente el resumen del PMID 14554208',
 },
 'estado_evidencia': {
   'escalon': 'solo preclínica; sin ningún ensayo clínico indexado',
   'texto': 'La investigación de BPC-157 es preclínica. Una búsqueda en PubMed del '
            'término «BPC 157» restringida a ensayos clínicos no devuelve ningún '
            'registro (0 de 230, consulta del 22-sep-2026). Una revisión de 2026 sobre '
            'su desarrollo farmacéutico lo resume así: pese a más de tres décadas de '
            'investigación preclínica, no hay formulación aprobada, ni régimen de '
            'dosificación validado, ni un ensayo de fase II completado; los datos en '
            'personas proceden de menos de 30 sujetos repartidos en tres estudios piloto '
            'no controlados.',
   'consultas_pubmed': [
     {'consulta': '"BPC 157"', 'resultados': 230, 'fecha': '2026-09-22'},
     {'consulta': '"BPC 157" AND clinical trial[pt]', 'resultados': 0, 'fecha': '2026-09-22'},
     {'consulta': '"BPC 157" AND randomized controlled trial[pt]', 'resultados': 0, 'fecha': '2026-09-22'},
   ],
 },
 'regulatorio': {
   'aprobacion': 'Sin aprobación en ninguna jurisdicción. No hay formulación farmacéutica '
                 'validada (PMID 42198317).',
   'wada': 'PROHIBIDO. Sección S0 (sustancias no aprobadas), citado por nombre. No es '
           'agente anabólico ni factor de crecimiento, un error muy extendido.',
   'fuente_wada': 'Lista de Prohibiciones WADA vigente 2026, sección S0; lectura interna '
                  'del PDF contrastada con USADA (2026-08-29). Revalidar cada 1 de enero.',
 },
 'protocolos': [
  {'estudio': 'Tendón de Aquiles seccionado',
   'pmid': '14554208',
   'modelo': 'Rata; tendón de Aquiles derecho seccionado 5 mm proximal a su inserción calcánea, con defecto entre los extremos',
   'via': 'Intraperitoneal',
   'pauta': '10 µg, 10 ng o 10 pg por kg de peso corporal, una vez al día; primera aplicación 30 min después de la cirugía, última 24 h antes de la autopsia; evaluación en los días 1, 4, 7, 10 y 14',
   'desenlace': 'Carga de falla, carga de falla por área y módulo de Young; índice funcional de Aquiles; histología y tamaño del defecto. Comparador: salino 5,0 mL/kg'},
  {'estudio': 'Úlcera gástrica aguda y crónica',
   'pmid': '15052688',
   'modelo': 'Rata; modelos de úlcera inducida, incluidos ligadura de píloro y úlcera crónica por acetato',
   'via': 'Intramuscular e intragástrica',
   'pauta': '200, 400 y 800 ng/kg; administración inicial única o continua, antes del inductor en el modelo agudo y después en el crónico',
   'desenlace': 'Área de la úlcera y tasa de inhibición de su formación (45,7 %–65,6 %); reconstrucción del epitelio glandular y tejido de granulación. Comparador: famotidina (60,8 %, 57,2 % y 34,3 % en los tres modelos)'},
  {'estudio': 'Farmacocinética, distribución, metabolismo y excreción',
   'pmid': '36588717',
   'modelo': 'Rata y perro beagle',
   'via': 'Intravenosa e intramuscular',
   'pauta': 'Una administración intravenosa única; administraciones intramusculares únicas a tres dosis crecientes; y administración intramuscular repetida. Valores numéricos de cada nivel de dosis ' + NR,
   'desenlace': 'Semivida de eliminación del BPC157 inalterado inferior a 30 min y cinética lineal en ambas especies; biodisponibilidad absoluta media por vía intramuscular de 14 %–19 % en rata y 45 %–51 % en beagle; excreción urinaria y biliar verificada con BPC157 marcado con tritio'},
  {'estudio': 'Reparación de tendón de Aquiles, comparado con TB-500',
   'pmid': '42542926',
   'modelo': 'Rata Sprague-Dawley macho; 32 animales de 12 semanas y unos 330 g, con sección y reparación estandarizada del tendón de Aquiles, repartidos en 4 grupos de 8 (control, BPC-157, TB-500, combinación)',
   'via': 'Intraperitoneal',
   'pauta': 'BPC-157 10 µg/kg/día durante 4 semanas tras la cirugía',
   'desenlace': 'Carga máxima hasta la falla; puntuaciones histopatológicas de Bonar y Movin; birrefringencia con rojo sirio; expresión inmunohistoquímica de colágeno I y III. El grupo BPC-157 mostró puntuaciones numéricamente menores sin alcanzar significación en las totales'},
  {'estudio': 'Síntesis regional de serotonina en el cerebro',
   'pmid': '15531385',
   'modelo': 'Rata; medición por autorradiografía con α-[14C]metil-L-triptófano',
   'via': 'Intraperitoneal (dosis única) y subcutánea (tratamiento repetido)',
   'pauta': 'Dosis única de 10 µg/kg por vía intraperitoneal 40 min antes del trazador; en la segunda serie, 10 µg/kg por vía subcutánea durante 7 días',
   'desenlace': 'Tasa regional de síntesis de serotonina en tálamo dorsal, hipocampo, cuerpo geniculado lateral, hipotálamo, sustancia negra, núcleos del rafe y otras regiones'},
  {'estudio': 'Fibroblastos tendinosos: migración y supervivencia',
   'pmid': '21030672',
   'modelo': 'In vitro y ex vivo; explantes de tendón y fibroblastos tendinosos derivados de tendón de Aquiles de rata',
   'via': 'In vitro',
   'pauta': 'Efecto dependiente de la dosis en migración y extensión celular; concentraciones ensayadas ' + NR,
   'desenlace': 'Crecimiento desde el explante; supervivencia celular bajo estrés con H₂O₂; migración en cámara de filtro; formación de F-actina; fosforilación de FAK y paxilina por Western blot. La proliferación directa no se modificó'},
  {'estudio': 'Receptor de hormona de crecimiento en fibroblastos tendinosos',
   'pmid': '25415472',
   'modelo': 'In vitro; fibroblastos tendinosos aislados de tendón de Aquiles de rata Sprague-Dawley macho',
   'via': 'In vitro',
   'pauta': 'Efecto dependiente de dosis y de tiempo; concentraciones ensayadas ' + NR,
   'desenlace': 'Expresión del receptor de hormona de crecimiento (ARNm y proteína) por RT-PCR en tiempo real y Western blot; proliferación por MTT y PCNA al añadir hormona de crecimiento; activación de JAK2'},
 ],
 'evidencia_extra': [
  {'pmid': '42198317',
   'nota': 'Revisión narrativa de 2026 sobre el desarrollo farmacéutico de BPC-157. Es la '
           'fuente del aviso de estado de la evidencia: sin formulación aprobada, sin régimen '
           'de dosificación validado y sin ensayo de fase II completado; datos clínicos de '
           'menos de 30 sujetos en tres pilotos no controlados, ninguno con preparación '
           'farmacéutica estandarizada.',
   'motivo': 'Es una revisión, no un estudio primario: no aporta fila ni dosis (regla 9).'},
  {'pmid': '40789979',
   'nota': 'Revisión narrativa de 2025 en medicina musculoesquelética. Confirma que solo tres '
           'estudios piloto han examinado BPC-157 en personas (dolor intraarticular de rodilla, '
           'cistitis intersticial y seguridad/farmacocinética intravenosa) y concluye que debe '
           'considerarse investigacional.',
   'motivo': 'Es una revisión, no un estudio primario.'},
 ],
 'avisos': [
   'Cero ensayos clínicos indexados es el dato que debe encabezar la monografía. El vacío '
   'también es un dato y se publica con la consulta que lo demuestra.',
   'La afirmación de terceros de «sin toxicidad significativa hasta 1000× la dosis efectiva» '
   'NO se pudo verificar contra ningún PMID. No se publica.',
 ],
 'pendientes': [
   'PMID 34324435 (revisión retrospectiva de expedientes de 17 pacientes con inyección '
   'intraarticular) no se incluyó en este archivo: si se quiere en la sección de evidencia, '
   'hay que verificarlo y describirlo con sus limitaciones (sin instrumentos validados, '
   'seguimiento telefónico). Nunca en la tabla.',
   'Los niveles de dosis concretos del estudio de farmacocinética (36588717) no constan en '
   'el resumen; están en el texto completo.',
 ],
})

# ── Resto de moleculas, en archivos aparte por tamano ──────────────────
from datos_2 import MOLECULAS as _M2
from datos_3 import MOLECULAS as _M3
from datos_4 import MOLECULAS as _M4
MOLECULAS += _M2 + _M3 + _M4
