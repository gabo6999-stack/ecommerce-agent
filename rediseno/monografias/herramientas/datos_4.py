#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Moleculas 13 a 16."""
NR = ('no reportado en el resumen — pendiente de comprobar en el texto '
      'completo')
PC = 'PubChem PUG REST, consultado el 2026-09-22'
WADA = ('Lista de Prohibiciones WADA vigente 2026; lectura interna del PDF '
        'contrastada con USADA (2026-08-29). Revalidar cada 1 de enero.')

MOLECULAS = []

# ──────────────────────────────── 13. Retatrutida (producto 19)
MOLECULAS.append({
 'slug': 'retatrutida', 'nombre': 'Retatrutida',
 'producto': {'id': 19, 'nombre': 'Retatrutida',
              'url': 'https://peptidosysuplementos.mx/product/retatrutida',
              'presentacion': '30 mg'},
 'identidad': {
   'nombre_quimico': 'Agonista único de los receptores del polipéptido insulinotrópico '
                     'dependiente de glucosa (GIP), del GLP-1 y del glucagón',
   'inn': 'retatrutide',
   'sinonimos': ['Retatrutida', 'LY3437943'],
   'cas': NR,
   'formula_molecular': NR,
   'peso_molecular_da': NR,
   'secuencia_aminoacidos': NR,
   'pubchem_cid': None,
   'fuente_identidad': 'PubChem NO devuelve un registro de la molécula madre por los '
                       'nombres «retatrutide» ni «LY3437943» (consultado el 2026-09-22). '
                       'Una búsqueda en la base pccompound devuelve 10 aciertos, pero '
                       'todos son registros de IMPUREZAS («Retatrutide Impurity 6, 7, 8»), '
                       'no del principio activo. La identidad funcional (agonista triple '
                       'GIP/GLP-1/glucagón) la declara literalmente el resumen del '
                       'PMID 37366315.',
 },
 'estado_evidencia': {
   'escalon': 'fase 2 completada y fase 3 en curso, sin aprobación',
   'texto': 'Retatrutida está en desarrollo clínico avanzado y no está aprobada. En '
            'PubMed, la consulta «retatrutide OR LY3437943» devuelve 192 registros, de los '
            'que 8 están tipificados como ensayo clínico y 7 como ensayo aleatorizado '
            '(consulta del 22-sep-2026). El ensayo de fase 2 en obesidad y el de fase 3 en '
            'diabetes tipo 2 ya están publicados.',
   'consultas_pubmed': [
     {'consulta': 'retatrutide OR LY3437943', 'resultados': 192, 'fecha': '2026-09-22'},
     {'consulta': '(lo anterior) AND clinical trial[pt]', 'resultados': 8, 'fecha': '2026-09-22'},
   ],
 },
 'regulatorio': {
   'aprobacion': 'SIN aprobación en ninguna jurisdicción. Está en desarrollo clínico.',
   'wada': 'PROHIBIDA por la cláusula S0: está en desarrollo clínico sin aprobación '
           'sanitaria, así que cae aunque no esté nombrada en la lista. Es el contraste '
           'exacto con semaglutida y tirzepatida, que sí están aprobadas y no lo están.',
   'fuente_wada': WADA,
 },
 'protocolos': [
  {'estudio': 'Retatrutida para la obesidad (fase 2)',
   'pmid': '37366315',
   'modelo': 'Humanos; 338 adultos con IMC ≥ 30, o de 27 a menos de 30 con al menos una enfermedad relacionada con el peso; 51,8 % varones; doble ciego, controlado con placebo, aleatorización 2:1:1:1:1:2:2',
   'via': 'Subcutánea',
   'pauta': '1 mg; 4 mg con dosis inicial de 2 mg; 4 mg con dosis inicial de 4 mg; 8 mg con dosis inicial de 2 mg; 8 mg con dosis inicial de 4 mg; o 12 mg con dosis inicial de 2 mg, una vez por semana durante 48 semanas',
   'desenlace': 'Cambio porcentual del peso a 24 semanas (variable principal) y a 48 semanas. A 48 semanas: −8,7 % con 1 mg, −17,1 % con 4 mg, −22,8 % con 8 mg y −24,2 % con 12 mg, frente a −2,1 % con placebo. Eventos adversos gastrointestinales dependientes de la dosis; aumento de la frecuencia cardiaca dependiente de la dosis con pico a las 24 semanas'},
  {'estudio': 'Retatrutida en diabetes tipo 2 (fase 3)',
   'pmid': '42250575',
   'modelo': 'Humanos; 537 participantes aleatorizados de 930 cribados (296 mujeres y 241 varones), entre abril de 2024 y abril de 2025: 134 a 4 mg, 133 a 9 mg, 136 a 12 mg y 134 a placebo',
   'via': 'Subcutánea',
   'pauta': '4 mg, 9 mg o 12 mg una vez por semana, frente a placebo; aleatorización 1:1:1:1',
   'desenlace': 'Cambio medio de HbA1c desde el inicio: −1,69 % (EE 0,11) con 4 mg, −1,86 % (0,10) con 9 mg y −1,94 % (0,08) con 12 mg, frente a −0,81 % (0,12) con placebo; diferencia frente a placebo de −0,88 puntos porcentuales (IC 95 % −1,18 a −0,59) con 4 mg'},
  {'estudio': 'Composición corporal en diabetes tipo 2 (subestudio de fase 2)',
   'pmid': '40609566',
   'modelo': 'Humanos; 189 participantes del subestudio de composición corporal, dentro de un ensayo de fase 2 con aleatorización 2:2:2:1:1:1:1:2',
   'via': 'Subcutánea',
   'pauta': 'Una vez por semana: placebo, dulaglutida 1,5 mg, o retatrutida 0,5 mg, 4 mg (con dosis inicial de 2 mg), 4 mg (con dosis inicial de 4 mg), 8 mg (con dosis inicial de 2 mg), 8 mg (con dosis inicial de 4 mg) o 12 mg',
   'desenlace': 'Reducción porcentual de la masa grasa total desde el inicio: 4,9 % (EE 1,4) con 0,5 mg; 15,2 % (3,2) con 4 mg agrupado; 26,1 % (2,5) con 8 mg agrupado; 23,2 % (3,0) con 12 mg; 2,6 % (1,6) con dulaglutida y 4,5 % (1,2) con placebo'},
  {'estudio': 'Biomarcadores de riesgo cardiovascular en dos ensayos',
   'pmid': '42608321',
   'modelo': 'Humanos; estudio 1 en adultos con obesidad o sobrepeso y diabetes tipo 2; estudio 2 en adultos con obesidad clínica sin diabetes tipo 2',
   'via': 'Subcutánea',
   'pauta': 'Estudio 1: retatrutida 0,5 / 4 / 8 / 12 mg una vez por semana, dulaglutida 1,5 mg o placebo, durante 36 semanas. Estudio 2: retatrutida 1 / 4 / 8 / 12 mg o placebo durante 48 semanas',
   'desenlace': 'Biomarcadores de riesgo cardiovascular'},
  {'estudio': 'Ensayo TRANSCEND-CKD en enfermedad renal crónica (diseño y basal)',
   'pmid': '41160422',
   'modelo': 'Humanos; participantes con enfermedad renal crónica, con mediana basal del cociente albúmina/creatinina en orina de 14,0 mg/g (rango intercuartílico 6,0 a 69,0)',
   'via': 'Subcutánea',
   'pauta': 'Una vez por semana, a la dosis máxima tolerada hasta 12 mg, frente a placebo equiparado; aleatorización 1:1',
   'desenlace': 'Publicación de diseño y características basales; los desenlaces renales se reportarán al terminar el ensayo'},
 ],
 'avisos': [
   'Retatrutida NO está aprobada. Es la diferencia que explica por qué está prohibida en '
   'competición y semaglutida no: el criterio de la WADA es regulatorio, no farmacológico.',
 ],
 'pendientes': [
   'No hay CAS, fórmula molecular ni peso molecular verificables: PubChem solo tiene '
   'registros de impurezas. Si se quieren publicar, hay que citar otra fuente citable '
   '(por ejemplo la propuesta de DCI de la OMS). No inventarlos.',
 ],
})

# ──────────────────────────────── 14. NAD+ (producto 1131) — plantilla corta
MOLECULAS.append({
 'slug': 'nad', 'nombre': 'NAD+', 'plantilla': 'corta',
 'producto': {'id': 1131, 'nombre': 'NAD+',
              'url': 'https://peptidosysuplementos.mx/product/nad-suplemento',
              'presentacion': '500 mg'},
 'identidad': {
   'nombre_quimico': 'Dinucleótido de nicotinamida y adenina (forma oxidada)',
   'inn': 'nadide',
   'sinonimos': ['NAD+', 'beta-NAD', 'Nadide', 'Coenzima I',
                 'Nucleótido de difosfopiridina', 'Cozimasa I'],
   'cas': '53-84-9',
   'formula_molecular': 'C21H27N7O14P2',
   'peso_molecular_da': '663.4',
   'secuencia_aminoacidos': 'No aplica: no es un péptido, es un dinucleótido',
   'pubchem_cid': 5892,
   'fuente_identidad': PC,
   'es_peptido': False,
 },
 'estado_evidencia': {
   'escalon': 'ensayos aleatorizados en personas, pero sobre los PRECURSORES (ribósido de '
              'nicotinamida y mononucleótido de nicotinamida), no sobre NAD+ administrado '
              'como tal',
   'texto': 'Este es el punto que decide cómo se lee toda la bibliografía de este producto. '
            'Los ensayos aleatorizados en personas se hicieron con precursores: ribósido de '
            'nicotinamida (NR) y mononucleótido de nicotinamida (NMN). No son ensayos de '
            'NAD+ administrado directamente. Cada fila de la tabla nombra la molécula que '
            'se administró de verdad. En PubMed, la consulta «"nicotinamide adenine '
            'dinucleotide" AND (supplement* OR "NAD+ precursor")» devuelve 1095 registros, '
            'de los que 46 están tipificados como ensayo clínico (consulta del 22-sep-2026).',
   'consultas_pubmed': [
     {'consulta': '"nicotinamide adenine dinucleotide" AND (supplement* OR "NAD+ precursor")',
      'resultados': 1095, 'fecha': '2026-09-22'},
     {'consulta': '(lo anterior) AND clinical trial[pt]', 'resultados': 46, 'fecha': '2026-09-22'},
   ],
 },
 'regulatorio': {
   'aprobacion': 'NAD+ y sus precursores se comercializan como suplementos alimenticios en '
                 'varios mercados, no como medicamentos. Comprobar el estatus en México '
                 'antes de afirmar nada.',
   'wada': 'No está en la Lista de Prohibiciones.',
   'fuente_wada': WADA,
 },
 'protocolos': [
  {'estudio': 'Mononucleótido de nicotinamida y grosor retiniano en diabetes',
   'pmid': '42082179',
   'modelo': 'Humanos; pacientes mayores con diabetes mellitus',
   'via': 'Oral',
   'pauta': 'MONONUCLEÓTIDO de nicotinamida (NMN), no NAD+: 250 mg/día durante 24 semanas, frente a placebo',
   'desenlace': 'Grosor retiniano'},
  {'estudio': 'Ribósido de nicotinamida e inflamación Th17',
   'pmid': '42048163',
   'modelo': 'Humanos; participantes con psoriasis, con muestras de sangre al inicio y tras la suplementación',
   'via': 'Oral',
   'pauta': 'RIBÓSIDO de nicotinamida (NR), no NAD+: 500 mg dos veces al día durante 4 semanas, frente a placebo equiparado',
   'desenlace': 'Señalización SLIT2/ROBO1 y atenuación de la inflamación mediada por Th17'},
  {'estudio': 'Ejercicio individualizado y precursor de NAD+ en ataxia de Friedreich',
   'pmid': '42009009',
   'modelo': 'Humanos; pacientes con ataxia de Friedreich, en un ensayo aleatorizado factorial 2 × 2 de un solo centro en Estados Unidos',
   'via': 'Oral',
   'pauta': 'RIBÓSIDO de nicotinamida (NR), no NAD+, con dosis según el peso: 300 mg (1 cápsula) de 24 a menos de 48 kg; 600 mg (2 cápsulas) de 48 a menos de 72 kg; y 900 mg (3 cápsulas) por encima de 72 kg. Frente a placebo',
   'desenlace': 'Seguridad y eficacia; consultar el resumen completo para las variables exactas'},
  {'estudio': 'Concentraciones sanguíneas de NAD tras NMN a tres dosis',
   'pmid': '41162813',
   'modelo': 'Humanos; participantes sanos de mediana edad; análisis post hoc de un ensayo aleatorizado y doble ciego',
   'via': 'Oral',
   'pauta': 'MONONUCLEÓTIDO de nicotinamida (NMN), no NAD+: 300, 600 o 900 mg al día, frente a placebo',
   'desenlace': 'Concentración sanguínea de dinucleótido de nicotinamida y adenina y su asociación con parámetros de laboratorio'},
  {'estudio': 'Ribósido de nicotinamida y ejercicio en hipertensión',
   'pmid': '40770531',
   'modelo': 'Humanos; 54 adultos sedentarios de 55 años o más con presión arterial sistólica diurna media ≥ 130 mmHg',
   'via': 'Oral',
   'pauta': 'RIBÓSIDO de nicotinamida (NR), no NAD+: 1000 mg/día durante 6 semanas, combinado con 3 sesiones semanales de 30 min de marcha supervisada; frente a placebo con el mismo ejercicio y frente a NR solo',
   'desenlace': 'Presión arterial sistólica diurna media'},
  {'estudio': 'Ribósido de nicotinamida en síndrome de Werner (cruzado, doble ciego)',
   'pmid': '40459998',
   'modelo': 'Humanos; pacientes con síndrome de Werner',
   'via': 'Oral',
   'pauta': 'RIBÓSIDO de nicotinamida (NR), no NAD+: 1000 mg en cápsulas, una vez al día durante 26 semanas, seguido de cruce al brazo opuesto otras 26 semanas',
   'desenlace': 'Consultar el resumen completo para las variables exactas'},
 ],
 'avisos': [
   'NINGUNA de estas filas administró NAD+ como tal: todas usaron un precursor. La '
   'monografía tiene que decirlo antes de la tabla, no en una nota al pie.',
   'NAD+ no es un péptido. Si la monografía va en un grupo titulado «péptidos», hay que '
   'decir qué es: un dinucleótido.',
 ],
 'pendientes': [
   'Buscar específicamente ensayos que administren NAD+ intacto (oral o intravenoso). Si '
   'no existen, eso mismo es el aviso de estado de la evidencia y hay que publicarlo con '
   'la consulta que lo demuestre.',
 ],
})

# ──────────────────────────────── 15. Agua bacteriostática (producto 799) — corta
MOLECULAS.append({
 'slug': 'agua-bacteriostatica', 'nombre': 'Agua bacteriostática',
 'plantilla': 'corta',
 'producto': {'id': 799, 'nombre': 'Agua Bacteriostática',
              'url': 'https://peptidosysuplementos.mx/product/agua-bacteriostatica-3ml',
              'presentacion': '3 mL'},
 'identidad': {
   'nombre_quimico': 'Agua estéril para inyección que contiene uno o más agentes '
                     'antimicrobianos para suprimir el crecimiento de contaminantes '
                     'microbianos. El conservante habitual es alcohol bencílico',
   'inn': 'No aplica: es un diluyente, no un principio activo',
   'sinonimos': ['Agua bacteriostática para inyección', 'bWFI',
                 'Bacteriostatic Water for Injection'],
   'cas': {'agua': '7732-18-5', 'alcohol_bencilico': '100-51-6'},
   'formula_molecular': {'agua': 'H2O', 'alcohol_bencilico': 'C7H8O'},
   'peso_molecular_da': {'alcohol_bencilico': '108.14'},
   'secuencia_aminoacidos': 'No aplica: no es un péptido',
   'pubchem_cid': {'alcohol_bencilico': 244},
   'especificacion': 'La monografía de la Farmacopea de Estados Unidos (USP) describe el '
                     'agua bacteriostática para inyección con un pH de 4,5 a 7,0 '
                     '(PMID 36870668)',
   'fuente_identidad': PC,
   'es_peptido': False,
 },
 'estado_evidencia': {
   'escalon': 'no procede: es un excipiente farmacéutico con monografía de farmacopea, no '
              'una molécula en investigación. Lo que sí tiene literatura es la seguridad '
              'de su conservante',
   'texto': 'El agua bacteriostática no es una molécula de investigación y no tiene una '
            'tabla de protocolos que construir: es un diluyente con monografía de '
            'farmacopea. Lo que sí está documentado, y es lo que la monografía debe '
            'recoger, es la toxicidad del alcohol bencílico en recién nacidos, sobre todo '
            'prematuros, por inmadurez de la vía de detoxificación del ácido benzoico.',
   'consultas_pubmed': [
     {'consulta': '"bacteriostatic water"', 'resultados': 33, 'fecha': '2026-09-22'},
   ],
 },
 'regulatorio': {
   'aprobacion': 'Producto farmacéutico con monografía en la Farmacopea de Estados Unidos. '
                 'No está indicado para recién nacidos por su contenido de alcohol bencílico.',
   'wada': 'No aplica: es un diluyente, no una sustancia con efecto buscado.',
   'fuente_wada': WADA,
 },
 'protocolos': [
  {'estudio': 'Alcohol bencílico, kernicterus, hemorragia intraventricular y mortalidad',
   'pmid': '2783624',
   'modelo': 'Humanos; recién nacidos prematuros. 218 ingresados durante los últimos 18 meses de uso de alcohol bencílico, comparados con 232 ingresados en los primeros 18 meses tras su retirada',
   'via': 'Intravenosa (solución de lavado de catéteres intravasculares)',
   'pauta': 'Volumen de solución de lavado con alcohol bencílico estimado para cada paciente; los autores señalan que muchos de los casos recibieron volúmenes diarios pequeños. Cantidad en mg/kg ' + NR + '',
   'desenlace': 'Kernicterus (asociación significativa, p < 0,005) y hemorragia intraventricular (p < 0,0000005). Tras la retirada del alcohol bencílico no apareció kernicterus en ningún paciente. La retirada no tuvo efecto demostrable sobre la mortalidad'},
  {'estudio': 'Metabolismo y eliminación del alcohol bencílico en recién nacidos',
   'pmid': '3229281',
   'modelo': 'Humanos; 14 recién nacidos a término y 9 prematuros que recibían dosis de carga de fenobarbital con alcohol bencílico',
   'via': 'Intravenosa (como excipiente del fenobarbital)',
   'pauta': 'Dosis de carga de fenobarbital que contenían alcohol bencílico; cantidad concreta ' + NR,
   'desenlace': 'Ácido benzoico y ácido hipúrico en orina y suero por cromatografía de gases y HPLC. Mayor acumulación de ácido benzoico en prematuros (pico normalizado 2130,6 frente a 237,8; p < 0,001) y área bajo la curva mayor (1253,2 frente a 483,0; p < 0,01), con menor formación de ácido hipúrico'},
 ],
 'evidencia_extra': [
  {'pmid': '36870668',
   'modelo': 'Caracterización analítica, sin sujetos',
   'nota': 'Describe el agua bacteriostática para inyección como diluyente parenteral '
           'habitual, recoge el intervalo de pH de 4,5 a 7,0 de la monografía de la USP y '
           'explica por qué su baja fuerza iónica y su falta de capacidad tampón dificultan '
           'medir el pH de forma reproducible.',
   'motivo': 'Es un trabajo analítico de control de calidad, no un estudio con pauta en un '
             'modelo: aporta la especificación de farmacopea, no una fila.'},
 ],
 'avisos': [
   'La plantilla corta es la correcta aquí: forzar una tabla de «protocolos de '
   'investigación» sobre un diluyente sería inventar una categoría que no existe.',
   'El dato accionable de esta página es la contraindicación en recién nacidos, con sus '
   'dos referencias. Es información de seguridad real y verificable.',
 ],
 'pendientes': [
   'Confirmar la concentración exacta de alcohol bencílico del producto que se vende y que '
   'coincida con la especificación declarada en la ficha.',
 ],
})

# ──────────────────────────────── 16. Glutation (producto 2234) — EL HALLAZGO
MOLECULAS.append({
 'slug': 'glutation', 'nombre': 'Glutatión',
 'producto': {'id': 2234, 'nombre': 'Glutatión 1500 mg',
              'url': 'https://peptidosysuplementos.mx/product/glutation-1500mg',
              'presentacion': '1500 mg'},
 'identidad': {
   'nombre_quimico': 'γ-L-glutamil-L-cisteinil-glicina (glutatión reducido, GSH)',
   'inn': 'glutathione',
   'sinonimos': ['Glutatión', 'Glutatión reducido', 'GSH', 'L-Glutathione reduced',
                 'Glutathion', 'Tathion'],
   'cas': '70-18-8',
   'formula_molecular': 'C10H17N3O6S',
   'peso_molecular_da': '307.33',
   'secuencia_aminoacidos': 'Glu-Cys-Gly, con enlace peptídico gamma entre el glutamato y '
                            'la cisteína (TRIPÉPTIDO)',
   'pubchem_cid': 124886,
   'fuente_identidad': PC,
   'es_peptido': True,
 },
 'estado_evidencia': {
   'escalon': 'ensayos aleatorizados en personas, mayoritariamente pequeños y con '
              'desenlaces intermedios; la biodisponibilidad oral sigue siendo discutida',
   'texto': 'El glutatión tiene bastante literatura clínica, pero con dos salvedades que '
            'la monografía debe declarar. La primera es que su disponibilidad sistémica '
            'tras la administración oral sigue siendo discutida y depende de la '
            'formulación. La segunda es que muchos ensayos lo miden como desenlace '
            '(cuánto glutatión sube en sangre tras dar otra cosa) en vez de administrarlo. '
            'En PubMed, la consulta «glutathione AND (intravenous OR oral supplementation)» '
            'devuelve 3120 registros, de los que 342 están tipificados como ensayo clínico '
            '(consulta del 22-sep-2026).',
   'consultas_pubmed': [
     {'consulta': 'glutathione AND (intravenous OR oral supplementation)',
      'resultados': 3120, 'fecha': '2026-09-22'},
     {'consulta': '(lo anterior) AND clinical trial[pt]', 'resultados': 342, 'fecha': '2026-09-22'},
   ],
 },
 'regulatorio': {
   'aprobacion': 'Se comercializa como suplemento alimenticio. Comprobar el estatus en '
                 'México antes de afirmar nada.',
   'wada': 'No está en la Lista de Prohibiciones.',
   'fuente_wada': WADA,
 },
 'protocolos': [
  {'estudio': 'Farmacocinética comparada de dos formulaciones orales',
   'pmid': '42392376',
   'modelo': 'Humanos; participantes de un estudio comparativo entre una película bucodispersable y un comprimido convencional',
   'via': 'Oral',
   'pauta': 'Estudio II: 100 mg/día durante 4 semanas, en película bucodispersable o en comprimido',
   'desenlace': 'Concentración plasmática de glutatión, con diferencias significativas a las 4 y 6 horas a favor de la película'},
  {'estudio': 'Glutatión oral, óxido nítrico e IL-1α',
   'pmid': '41014073',
   'modelo': 'Humanos; 40 participantes aleatorizados, 22 a glutatión y 18 a placebo',
   'via': 'Oral',
   'pauta': '500 mg una vez al día durante 4 semanas, frente a placebo',
   'desenlace': 'Concentraciones de óxido nítrico e interleucina-1α'},
  {'estudio': 'Suplementación oral prolongada y microbiota intestinal en diabetes tipo 2',
   'pmid': '37935462',
   'modelo': 'Humanos; personas con diabetes tipo 2 incluidas en un ensayo clínico aleatorizado',
   'via': 'Oral',
   'pauta': '500 mg una vez al día durante 6 meses',
   'desenlace': 'Composición de la microbiota intestinal por secuenciación metagenómica del ARNr 16S en muestra fecal matutina'},
  {'estudio': 'Citrulina con glutatión y función endotelial en mujeres posmenopáusicas',
   'pmid': '37049398',
   'modelo': 'Humanos; 44 mujeres posmenopáusicas sanas aleatorizadas a tres brazos',
   'via': 'Oral',
   'pauta': 'Citrulina 6 g; citrulina 2 g más glutatión 200 mg; o placebo, durante 4 semanas',
   'desenlace': 'Función endotelial y presión arterial'},
 ],
 'avisos': [
   'HALLAZGO DE CATÁLOGO: el glutatión es químicamente un TRIPÉPTIDO '
   '(γ-glutamil-cisteinil-glicina). El plan de construcción lo había agrupado con los '
   'suplementos Nutricost y lo dejaba fuera de las monografías. Por composición pertenece '
   'al grupo peptídico, y además su ficha ya está categorizada en la tienda como '
   '«Péptidos Bienestar General». Es la molécula número 16.',
   'Distinguir siempre entre administrar glutatión y medirlo como desenlace de otra cosa. '
   'Varios de los ensayos que aparecen al buscar «glutatión» dan astaxantina, aronia o '
   'juçara y miden el glutatión que sube.',
 ],
 'pendientes': [
   'Falta al menos una fila por vía intravenosa o liposomal, que es como se promociona '
   'habitualmente.',
   'Ninguna de las filas usa la dosis de 1500 mg de la presentación que se vende. Conviene '
   'localizar un ensayo a esa dosis o decir explícitamente que no se localizó.',
 ],
})
