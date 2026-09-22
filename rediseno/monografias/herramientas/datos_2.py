#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Moleculas 3 a 9."""
NR = ('no reportado en el resumen — pendiente de comprobar en el texto '
      'completo')
PC = 'PubChem PUG REST, consultado el 2026-09-22'
WADA = ('Lista de Prohibiciones WADA vigente 2026; lectura interna del PDF '
        'contrastada con USADA (2026-08-29). Revalidar cada 1 de enero.')

MOLECULAS = []

# ──────────────────────────────── 3. BPC-157 + TB-500 (producto 795)
MOLECULAS.append({
 'slug': 'bpc-157-tb-500', 'nombre': 'BPC-157 + TB-500',
 'producto': {'id': 795, 'nombre': 'BPC-157 + TB-500',
              'url': 'https://peptidosysuplementos.mx/product/bpc-157-tb-500',
              'presentacion': '5 mg'},
 'identidad': {
   'nombre_quimico': 'Mezcla de dos péptidos distintos: el pentadecapéptido BPC-157 y '
                     'el heptapéptido acetilado TB-500 (Ac-LKKTETQ)',
   'inn': 'Ninguno de los dos tiene DCI',
   'sinonimos': ['BPC-157 + TB-500', 'TB500', 'TB 500',
                 'N-acetil-L-leucil-L-lisil-L-lisil-L-treonil-L-glutamil-L-treonil-L-glutamina'],
   'cas': {'BPC-157': '137525-51-0', 'TB-500': '885340-08-9',
           'timosina_beta-4_completa': 'no consta en la lista de sinónimos de PubChem'},
   'formula_molecular': {'BPC-157': 'C62H98N16O22', 'TB-500': 'C38H68N10O14',
                         'timosina_beta-4_completa': 'C212H350N56O78S'},
   'peso_molecular_da': {'BPC-157': '1419.5', 'TB-500': '889.0',
                         'timosina_beta-4_completa': '4963'},
   'secuencia_aminoacidos': {'BPC-157': 'GEPPPGKPADDAGLV (15 aminoácidos)',
                             'TB-500': 'Ac-Leu-Lys-Lys-Thr-Glu-Thr-Gln-OH (7 aminoácidos, N-acetilado)'},
   'pubchem_cid': {'BPC-157': 9941957, 'TB-500': 62707662,
                   'timosina_beta-4_completa': 45382195},
   'fuente_identidad': PC,
 },
 'estado_evidencia': {
   'escalon': 'preclínica para BPC-157; para TB-500, la mayor parte de la literatura '
              'es sobre la timosina beta-4 COMPLETA, no sobre el fragmento; la '
              'combinación apenas se ha estudiado y el único estudio que la probó no '
              'encontró beneficio adicional',
   'texto': 'Hay que separar tres cosas que se confunden constantemente. Primero, '
            'BPC-157: preclínico, cero ensayos clínicos indexados. Segundo, TB-500: es '
            'el heptapéptido acetilado Ac-LKKTETQ (889 Da), no la timosina beta-4 '
            'completa (43 aminoácidos, 4963 Da); casi toda la bibliografía que se le '
            'atribuye se hizo con la proteína completa. Tercero, la combinación: en el '
            'único estudio publicado que la comparó de frente, combinar los dos péptidos '
            'no aportó beneficio adicional frente a cualquiera de ellos por separado '
            '(PMID 42542926).',
   'consultas_pubmed': [
     {'consulta': '"BPC 157" AND clinical trial[pt]', 'resultados': 0, 'fecha': '2026-09-22'},
     {'consulta': '"TB-500" OR "thymosin beta 4"', 'resultados': 1203, 'fecha': '2026-09-22'},
   ],
 },
 'regulatorio': {
   'aprobacion': 'Ninguno de los dos componentes está aprobado.',
   'wada': 'BPC-157: prohibido por S0, citado por nombre. TB-500 y timosina beta-4: '
           'prohibidos por S2.3 (factores de crecimiento), citados por nombre.',
   'fuente_wada': WADA,
 },
 'protocolos': [
  {'estudio': 'Reparación de tendón de Aquiles: BPC-157, TB-500 y su combinación',
   'pmid': '42542926',
   'modelo': 'Rata Sprague-Dawley macho; 32 animales de 12 semanas y unos 330 g, con sección y reparación estandarizada del tendón de Aquiles, repartidos en 4 grupos de 8: control, BPC-157, TB-500 y combinación',
   'via': 'Intraperitoneal',
   'pauta': 'BPC-157 10 µg/kg/día y TB-500 60 µg/kg/día, solos o combinados, durante 4 semanas tras la cirugía',
   'desenlace': 'Carga máxima hasta la falla; puntuaciones de Bonar y Movin; birrefringencia con rojo sirio; colágeno I y III por inmunohistoquímica. La carga máxima alcanzó significación solo en el grupo TB-500 (p < 0,05); la combinación no aportó beneficio adicional frente a cualquiera de los dos por separado'},
  {'estudio': 'Timosina beta-4 completa en un modelo de inflamación cerebral',
   'pmid': '36878045',
   'modelo': 'Ratón APP/PS1 macho de 12,5 meses (n = 30) y sus compañeros de camada silvestres (n = 29), retados con lipopolisacárido 100 µg/kg por vía intravenosa',
   'via': 'Intravenosa',
   'pauta': 'Timosina beta-4 COMPLETA (no TB-500) 5 mg/kg por vía intravenosa, inmediatamente después del reto y a las 2 y 4 h, y luego una vez al día durante 6 días (n = 7–8 por grupo)',
   'desenlace': 'Carga de placa amiloide; rendimiento en enterramiento de comida, memoria de trabajo espacial y campo abierto'},
  {'estudio': 'Timosina beta-4 en células madre derivadas de tejido adiposo',
   'pmid': '38409346',
   'modelo': 'In vitro; células madre humanas derivadas de tejido adiposo',
   'via': 'In vitro',
   'pauta': 'Timosina beta-4 COMPLETA a 100 ng/mL y 1000 ng/mL frente a control de 0 ng/mL',
   'desenlace': 'Proliferación celular desde el día 1 (p = 0,0171 a 100 ng/mL; p = 0,0054 a 1000 ng/mL); capacidad antiapoptótica; ARNm de genes de angiogénesis y de la vía Hippo'},
 ],
 'avisos': [
   'La distinción TB-500 (7 aminoácidos, 889 Da) frente a timosina beta-4 completa '
   '(43 aminoácidos, 4963 Da) es la que decide si una cita vale o no. Toda fila que '
   'use la proteína completa debe decirlo dentro de la propia celda, como aquí.',
   'El único estudio que comparó la combinación de frente concluyó que NO hubo efecto '
   'aditivo. Un producto combinado cuya monografía calle ese dato es un problema.',
 ],
 'pendientes': [
   'Faltan filas de TB-500 propiamente dicho (el heptapéptido). Solo se localizó una '
   '(42542926). Hay que buscar específicamente «Ac-SDKP» y «LKKTETQ» en el texto '
   'completo, no por el nombre comercial.',
 ],
})

# ──────────────────────────────── 4. Cagrilintida (producto 2240)
MOLECULAS.append({
 'slug': 'cagrilintida', 'nombre': 'Cagrilintida',
 'producto': {'id': 2240, 'nombre': 'Cagrilintida',
              'url': 'https://peptidosysuplementos.mx/product/cagrilintida-10mg',
              'presentacion': '10 mg'},
 'identidad': {
   'nombre_quimico': 'Análogo de amilina de acción prolongada, acilado',
   'inn': 'cagrilintide',
   'sinonimos': ['Cagrilintide', 'AM833', 'NNC0174-0833'],
   'cas': 'ver cas_candidatos en la consulta de PubChem; no se fijó uno solo',
   'formula_molecular': 'C194H312N54O59S2',
   'peso_molecular_da': '4409',
   'secuencia_aminoacidos': NR + ' (PubChem da el nombre IUPAC completo, no la secuencia en código de tres letras)',
   'pubchem_cid': 171397054,
   'inchikey': 'LDERDVMBIYGIOI-IZVMHKDJSA-N',
   'fuente_identidad': PC,
 },
 'estado_evidencia': {
   'escalon': 'ensayos de fase 2 y fase 3 en personas, casi siempre coadministrada con semaglutida',
   'texto': 'Cagrilintida se ha estudiado en personas hasta fase 3. En PubMed, la '
            'consulta «cagrilintide» devuelve 100 registros, de los que 15 están '
            'tipificados como ensayo clínico y 15 como ensayo aleatorizado (consulta del '
            '22-sep-2026). La mayor parte del programa clínico la estudia junto a '
            'semaglutida, no sola: al leer cualquier resultado hay que mirar primero si '
            'el brazo era cagrilintida en monoterapia o la combinación.',
   'consultas_pubmed': [
     {'consulta': 'cagrilintide', 'resultados': 100, 'fecha': '2026-09-22'},
     {'consulta': 'cagrilintide AND clinical trial[pt]', 'resultados': 15, 'fecha': '2026-09-22'},
   ],
 },
 'regulatorio': {
   'aprobacion': 'Sin aprobación vigente como producto independiente en el momento de '
                 'esta revisión. Está en desarrollo clínico avanzado.',
   'wada': 'PROHIBIDA por la cláusula S0: está en fase 3 sin aprobación sanitaria, así '
           'que cae aunque no esté nombrada en la lista.',
   'fuente_wada': WADA,
 },
 'protocolos': [
  {'estudio': 'Cagrilintida sola, semaglutida sola y la combinación en diabetes tipo 2 (fase 2)',
   'pmid': '37364590',
   'modelo': 'Humanos; 92 adultos con diabetes tipo 2 e IMC ≥ 27 kg/m² en tratamiento con metformina, con o sin inhibidor de SGLT2, en 17 centros de Estados Unidos',
   'via': 'Subcutánea',
   'pauta': 'Una vez por semana durante 32 semanas, con escalada hasta 2,4 mg, en tres brazos: cagrilintida + semaglutida (n = 31), semaglutida (n = 31) o cagrilintida sola (n = 30)',
   'desenlace': 'Cambio de HbA1c desde el inicio (cagrilintida sola: −0,9 puntos porcentuales; combinación: −2,2; semaglutida: −1,8); peso corporal (cagrilintida sola: −8,1 %; combinación: −15,6 %; semaglutida: −5,1 %); glucosa plasmática en ayunas y tiempo en rango por monitorización continua'},
  {'estudio': 'Cagrilintida para el control de peso (fase 2)',
   'pmid': '34798060',
   'modelo': 'Humanos; adultos con sobrepeso y obesidad, estudio multicéntrico aleatorizado',
   'via': 'Subcutánea',
   'pauta': 'Una vez por semana; niveles de dosis concretos ' + NR,
   'desenlace': 'Control del peso corporal; consultar el resumen completo para los desenlaces exactos'},
  {'estudio': 'Cagrilintida-semaglutida frente a cada componente en diabetes tipo 2 (fase 3, REIMAGINE 2)',
   'pmid': '42251859',
   'modelo': 'Humanos; 2713 adultos con diabetes tipo 2 mal controlada (HbA1c 7,0 %–10,5 %) en tratamiento con metformina, con o sin inhibidor de SGLT2, e IMC ≥ 25 kg/m²',
   'via': 'Subcutánea',
   'pauta': 'Una vez por semana durante 68 semanas: cagrilintida 2,4 mg + semaglutida 2,4 mg, frente a semaglutida 2,4 mg y frente a cagrilintida, con aleatorización 8:8:2:8:8:1:1',
   'desenlace': 'Cambio de HbA1c desde el inicio hasta la semana 68 de la combinación (2,4 mg cada uno) frente a semaglutida 2,4 mg'},
  {'estudio': 'Cagrilintida-semaglutida añadida a insulina basal (fase 3, REIMAGINE 3)',
   'pmid': '42251856',
   'modelo': 'Humanos; 274 adultos con diabetes tipo 2 (HbA1c 7,0 %–10,5 %) con insulina basal estable una vez al día, con o sin metformina',
   'via': 'Subcutánea',
   'pauta': 'Una vez por semana: cagrilintida 2,4 mg + semaglutida 2,4 mg, o cagrilintida 1,0 mg + semaglutida 1,0 mg, con aleatorización 2:2:1:1',
   'desenlace': 'Control glucémico y seguridad como añadido a insulina basal'},
  {'estudio': 'Farmacocinética en insuficiencia renal o hepática',
   'pmid': '42228334',
   'modelo': 'Humanos; participantes adultos clasificados en cuatro grupos según función renal o hepática (normal, leve, moderada, grave), en dos estudios',
   'via': 'Subcutánea',
   'pauta': 'Dosis únicas de cagrilintida; valores concretos ' + NR,
   'desenlace': 'Farmacocinética, seguridad y tolerabilidad. La insuficiencia renal o hepática no afectó a la farmacocinética'},
 ],
 'avisos': [
   'Casi todos los resultados de peso que circulan como «de cagrilintida» son en realidad '
   'de la combinación con semaglutida. En la tabla, el brazo tiene que ir dentro de la '
   'celda, como aquí.',
 ],
 'pendientes': [
   'El resumen del PMID 34798060 (fase 2 en monoterapia) no se leyó entero: hay que '
   'sacar de él los niveles de dosis y el desenlace exacto antes de publicar esa fila.',
   'PubChem no fija un CAS único para cagrilintida en su lista de sinónimos.',
   'La secuencia de aminoácidos no se obtuvo en formato citable.',
 ],
})

# ──────────────────────────────── 5. CJC-1295 + Ipamorelina (producto 2232)
MOLECULAS.append({
 'slug': 'cjc-1295-ipamorelina', 'nombre': 'CJC-1295 (no-DAC) + Ipamorelina',
 'producto': {'id': 2232, 'nombre': 'CJC-1295 (no-DAC) + Ipamorelina',
              'url': 'https://peptidosysuplementos.mx/product/cjc-1295-ipamorelina-5mg',
              'presentacion': '5 mg'},
 'identidad': {
   'nombre_quimico': 'Mezcla de un análogo de GHRH (CJC-1295) y un pentapéptido '
                     'secretagogo de hormona de crecimiento (ipamorelina)',
   'inn': 'ipamorelin (DCI). CJC-1295 no tiene DCI.',
   'sinonimos': ['CJC 1295', 'GRF 1-29 (CJC1295)', 'Ipamorelin', 'NNC-26-0161'],
   'cas': {'CJC-1295_con_DAC': '446262-90-4', 'ipamorelina': '170851-70-4',
           'CJC-1295_sin_DAC': 'no localizado en PubChem por ese nombre'},
   'formula_molecular': {'CJC-1295_con_DAC': 'C165H269N47O46',
                         'ipamorelina': 'C38H49N9O5'},
   'peso_molecular_da': {'CJC-1295_con_DAC': '3647.2', 'ipamorelina': '711.9'},
   'secuencia_aminoacidos': {
     'ipamorelina': 'Aib-His-D-2-Nal-D-Phe-Lys-NH2 (pentapéptido)',
     'CJC-1295': 'Análogo de 30 residuos de GHRH(1-29) con sustituciones D-Ala², Gln⁸, '
                 'Ala¹⁵ y Leu²⁷ y una lisina terminal'},
   'pubchem_cid': {'CJC-1295_con_DAC': 91971820, 'ipamorelina': 9831659},
   'fuente_identidad': PC + '. El nombre IUPAC del CID 91971820 contiene el grupo '
                            '2,5-dioxopirrol (maleimida): ese registro es la forma CON DAC.',
 },
 'estado_evidencia': {
   'escalon': 'ensayos de fase temprana en personas para la forma CON DAC; el producto '
              'que se vende es la forma SIN DAC, para la que no existe un ensayo equivalente',
   'texto': 'Este es el punto que más se confunde de todo el catálogo. Los dos ensayos '
            'en personas que se citan habitualmente para «CJC-1295» (PMID 16352683 y '
            '17018654) se hicieron con la forma unida a albúmina mediante el enlazador '
            'maleimida, cuya semivida estimada es de 5,8 a 8,1 días. El producto que aquí '
            'se describe es la forma SIN ese enlazador. No es la misma molécula y no le '
            'corresponde esa farmacocinética. La literatura de ipamorelina, en cambio, es '
            'mayoritariamente preclínica: 50 registros, 2 tipificados como ensayo clínico '
            '(consulta del 22-sep-2026).',
   'consultas_pubmed': [
     {'consulta': '"CJC-1295"', 'resultados': 33, 'fecha': '2026-09-22'},
     {'consulta': '"CJC-1295" AND clinical trial[pt]', 'resultados': 2, 'fecha': '2026-09-22'},
     {'consulta': 'ipamorelin', 'resultados': 50, 'fecha': '2026-09-22'},
     {'consulta': 'ipamorelin AND clinical trial[pt]', 'resultados': 2, 'fecha': '2026-09-22'},
   ],
 },
 'regulatorio': {
   'aprobacion': 'Ninguno de los dos componentes está aprobado como medicamento.',
   'wada': 'PROHIBIDOS. Sección S2.2.4 (factores liberadores de hormona de crecimiento y '
           'secretagogos), ambos citados por nombre.',
   'fuente_wada': WADA,
 },
 'protocolos': [
  {'estudio': 'CJC-1295 unido a albúmina en adultos sanos (dosis ascendentes)',
   'pmid': '16352683',
   'modelo': 'Humanos; sujetos sanos de 21 a 61 años, en dos ensayos aleatorizados, doble ciego y controlados con placebo, de 28 y 49 días, en dos centros. FORMA CON ENLAZADOR (DAC), no la que se vende aquí',
   'via': 'Subcutánea',
   'pauta': 'Cuatro dosis únicas ascendentes en el primer estudio; dos o tres dosis semanales o quincenales en el segundo. Los autores destacan en sus conclusiones las dosis de 30 y 60 µg/kg',
   'desenlace': 'Concentración máxima y área bajo la curva de hormona de crecimiento e IGF-I; semivida estimada del compuesto de 5,8 a 8,1 días; IGF-I por encima del valor basal hasta 28 días tras dosis múltiples'},
  {'estudio': 'Pulsatilidad de la hormona de crecimiento bajo estímulo continuo',
   'pmid': '17018654',
   'modelo': 'Humanos; varones sanos de 20 a 40 años. FORMA CON ENLAZADOR (DAC)',
   'via': 'Subcutánea',
   'pauta': 'Inyección única de 60 o 90 µg/kg; muestreo sanguíneo cada 20 min durante 12 h nocturnas, antes y una semana después de la inyección',
   'desenlace': 'Frecuencia y magnitud de los pulsos de hormona de crecimiento (sin cambios); concentración basal o valle (aumento de 7,5 veces, p < 0,0001); media de hormona de crecimiento (+46 %, p < 0,01) e IGF-I (+45 %, p < 0,001)'},
  {'estudio': 'Caracterización de ipamorelina como secretagogo selectivo',
   'pmid': '9849822',
   'modelo': 'Células hipofisarias primarias de rata in vitro; ratas anestesiadas con pentobarbital; y cerdos conscientes',
   'via': 'In vitro y parenteral en animales',
   'pauta': 'In vitro, CE50 de 1,3 ± 0,4 nmol/L; en rata anestesiada, DE50 de 80 ± 42 nmol/kg; en cerdo consciente, DE50 de 2,3 ± 0,03 nmol/kg. Se ensayaron dosis hasta más de 200 veces la DE50 para la prueba de especificidad',
   'desenlace': 'Liberación de hormona de crecimiento y eficacia máxima frente a GHRP-6 y GHRP-2; concentraciones plasmáticas de FSH, LH, prolactina, TSH, ACTH y cortisol en cerdo. Ipamorelina no elevó ACTH ni cortisol por encima de lo observado con GHRH'},
  {'estudio': 'Ipamorelina en un modelo de íleo posoperatorio',
   'pmid': '19289567',
   'modelo': 'Rata macho en ayunas, sometida a laparotomía y manipulación intestinal',
   'via': 'Intravenosa (bolo)',
   'pauta': 'Ipamorelina de 0,01 a 1 mg/kg, en dosis única o en pauta repetida de 2 días (cuatro dosis al día a intervalos de 3 h). Comparador: GHRP-6 20 µg/kg o salino',
   'desenlace': 'Tiempo hasta la primera deposición; producción acumulada de pellets fecales; ingesta de alimento y ganancia de peso corporal medidos durante 48 h tras la cirugía'},
 ],
 'avisos': [
   'AVISO CENTRAL DE ESTA MOLÉCULA: los dos ensayos humanos son de la forma CON '
   'enlazador de albúmina. El producto es la forma SIN enlazador. La semivida de 5,8–8,1 '
   'días NO le corresponde. Si la monografía copia ese dato sin la distinción, publica un '
   'error de hecho.',
 ],
 'pendientes': [
   'Falta el CAS, la fórmula y el peso molecular de la forma SIN enlazador (modified '
   'GRF 1-29). PubChem no la devuelve por ese nombre.',
 ],
})

# ──────────────────────────────── 6. Sermorelina (producto 2231)
MOLECULAS.append({
 'slug': 'sermorelina', 'nombre': 'Sermorelina',
 'producto': {'id': 2231, 'nombre': 'Sermorelina',
              'url': 'https://peptidosysuplementos.mx/product/sermorelina-10mg',
              'presentacion': '10 mg'},
 'identidad': {
   'nombre_quimico': 'Amida de los 29 primeros aminoácidos de la hormona liberadora de '
                     'hormona de crecimiento humana, GHRH(1-29)NH2',
   'inn': 'sermorelin',
   'sinonimos': ['Sermorelina', 'Sermoreline', 'Sermorelinum', 'Geref',
                 'Groliberin', 'hGHRH(1-29)NH2', 'GHRH(1-29)NH2'],
   'cas': '86168-78-7',
   'formula_molecular': 'C149H246N44O42S',
   'peso_molecular_da': '3357.9',
   'secuencia_aminoacidos': 'Tyr-Ala-Asp-Ala-Ile-Phe-Thr-Asn-Ser-Tyr-Arg-Lys-Val-Leu-Gly-'
                            'Gln-Leu-Ser-Ala-Arg-Lys-Leu-Leu-Gln-Asp-Ile-Met-Ser-Arg-NH2 '
                            '(29 aminoácidos, C-terminal amidado)',
   'pubchem_cid': 16132413,
   'fuente_identidad': PC,
 },
 'estado_evidencia': {
   'escalon': 'ensayos clínicos en personas, incluidos estudios multicéntricos; fue un '
              'medicamento comercializado',
   'texto': 'Sermorelina es la molécula con historia regulatoria más sólida de este grupo: '
            'se comercializó como Geref para el diagnóstico y el tratamiento del déficit '
            'de hormona de crecimiento en la infancia, y ya no está disponible en varios '
            'mercados. En PubMed, la consulta «sermorelin OR "GHRH(1-29)"» devuelve 449 '
            'registros, de los que 65 están tipificados como ensayo clínico y 38 como '
            'ensayo aleatorizado (consulta del 22-sep-2026).',
   'consultas_pubmed': [
     {'consulta': 'sermorelin OR "GHRH(1-29)"', 'resultados': 449, 'fecha': '2026-09-22'},
     {'consulta': '(lo anterior) AND clinical trial[pt]', 'resultados': 65, 'fecha': '2026-09-22'},
   ],
 },
 'regulatorio': {
   'aprobacion': 'Tuvo aprobación como medicamento (Geref) para diagnóstico y tratamiento '
                 'del déficit de hormona de crecimiento; su comercialización se '
                 'descontinuó en varios mercados. Comprobar el estatus vigente en el país '
                 'antes de afirmar nada.',
   'wada': 'PROHIBIDA. Sección S2.2.4 (factores liberadores de hormona de crecimiento), '
           'citada por nombre.',
   'fuente_wada': WADA,
 },
 'protocolos': [
  {'estudio': 'Tratamiento de un año en niños con déficit de hormona de crecimiento (multicéntrico)',
   'pmid': '8772599',
   'modelo': 'Humanos; 110 niños prepuberales con déficit de hormona de crecimiento no tratados previamente, de los que 86 fueron evaluables; estudio multicéntrico abierto',
   'via': 'Subcutánea',
   'pauta': '30 µg/kg/día de GHRH-(1-29), al acostarse, hasta 1 año; seguimiento cada 3 a 6 meses',
   'desenlace': 'Velocidad de crecimiento (de 4,1 ± 0,9 cm/año al inicio a 8,0 ± 1,5 a los 6 meses y 7,2 ± 1,3 a los 12 meses); progresión de la edad ósea frente a la edad-talla; bioquímica clínica, glucosa en ayunas e IGF-I'},
  {'estudio': 'Talla baja idiopática y disfunción neurosecretora',
   'pmid': '10905389',
   'modelo': 'Humanos; 16 niños prepuberales con talla baja idiopática y 8 con disfunción neurosecretora de hormona de crecimiento, de crecimiento lento',
   'via': 'Subcutánea',
   'pauta': '30 µg/kg de GHRH 1-29, en una inyección nocturna, durante 6 meses, con seguimiento trimestral hasta el año',
   'desenlace': 'Tasa de crecimiento durante y después del tratamiento. Ambos grupos respondieron de forma similar; al suspender, las tasas volvieron a no diferir de las previas al tratamiento'},
  {'estudio': 'Inyecciones nocturnas en varones mayores sanos',
   'pmid': '9005976',
   'modelo': 'Humanos; 11 varones sanos, ambulatorios y no obesos, de 64 a 76 años, con valores basales bajos de IGF-I',
   'via': 'Subcutánea (autoinyección domiciliaria)',
   'pauta': '2 mg de GHRH(1-29) por la noche, durante 6 semanas',
   'desenlace': 'Consultar el resumen para la lista completa de desenlaces medidos'},
  {'estudio': 'GHRH continua frente a somatostatina intermitente en la generación de pulsos de GH',
   'pmid': '10594518',
   'modelo': 'Humanos; individuos normales y post-irradiación craneal de más de 30 Gy (2,5 años de mediana tras la radioterapia), con 6 controles pareados',
   'via': 'Subcutánea (infusión continua)',
   'pauta': 'GHRH(1-29)NH2 en infusión subcutánea continua de 60 ng/kg/minuto durante 24 h',
   'desenlace': 'Concentraciones séricas de hormona de crecimiento en perfiles espontáneos de 24 h y durante tres estudios de pinzamiento, para separar el papel de la GHRH continua del de la somatostatina(1-14) intermitente en la generación de pulsos de GH'},
 ],
 'evidencia_extra': [
  {'pmid': '18031173',
   'nota': 'Revisión sobre el uso de sermorelina en el diagnóstico y tratamiento del '
           'déficit idiopático de hormona de crecimiento en la infancia. Describe la '
           'prueba diagnóstica intravenosa de 1 µg/kg y sitúa el tratamiento subcutáneo '
           'en 30 µg/kg/día; también señala que el aumento de velocidad de crecimiento fue '
           'menor que con somatropina a la misma cifra por kilo.',
   'motivo': 'Es una revisión, no un estudio primario: no aporta fila ni dosis (regla 9). '
             'Sus cifras coinciden con las de los estudios primarios ya citados.'},
 ],
 'avisos': [
   'Ojo con la comparación implícita: la propia revisión señala que, a igual cifra por '
   'kilo, la velocidad de crecimiento aumentó MENOS con sermorelina que con somatropina.',
 ],
 'pendientes': [
   'El resumen del PMID 9005976 no se leyó entero: falta anotar sus desenlaces exactos.',
 ],
})

# ──────────────────────────────── 7. Timosina Alfa-1 (producto 2230)
MOLECULAS.append({
 'slug': 'timosina-alfa-1', 'nombre': 'Timosina Alfa-1',
 'producto': {'id': 2230, 'nombre': 'Timosina Alfa-1',
              'url': 'https://peptidosysuplementos.mx/product/thymosin-alpha-1-10mg',
              'presentacion': '10 mg'},
 'identidad': {
   'nombre_quimico': 'Péptido de 28 aminoácidos con el extremo N-terminal acetilado, '
                     'derivado de la protimosina alfa',
   'inn': 'thymalfasin',
   'sinonimos': ['Timalfasina', 'Thymalfasin', 'Thymosin alpha 1', 'Tα1',
                 'Zadaxin', 'alpha1-Thymosin'],
   'cas': '62304-98-7',
   'formula_molecular': 'C129H215N33O55',
   'peso_molecular_da': '3108.3',
   'secuencia_aminoacidos': '28 aminoácidos, N-terminal acetilado. Secuencia literal ' + NR,
   'pubchem_cid': 16130571,
   'fuente_identidad': PC,
 },
 'estado_evidencia': {
   'escalon': 'ensayos aleatorizados en personas, incluidos multicéntricos de varios '
              'cientos de pacientes; es un medicamento aprobado en varios países',
   'texto': 'Es, con diferencia, el péptido con más respaldo clínico de este catálogo. En '
            'PubMed, la consulta «"thymosin alpha 1" OR thymalfasin» devuelve 868 '
            'registros, de los que 94 están tipificados como ensayo clínico y 64 como '
            'ensayo aleatorizado (consulta del 22-sep-2026). La pauta que se repite en '
            'casi todos ellos es 1,6 mg por vía subcutánea dos veces por semana.',
   'consultas_pubmed': [
     {'consulta': '"thymosin alpha 1" OR thymalfasin', 'resultados': 868, 'fecha': '2026-09-22'},
     {'consulta': '(lo anterior) AND clinical trial[pt]', 'resultados': 94, 'fecha': '2026-09-22'},
     {'consulta': '(lo anterior) AND randomized controlled trial[pt]', 'resultados': 64, 'fecha': '2026-09-22'},
   ],
 },
 'regulatorio': {
   'aprobacion': 'Aprobada y comercializada como Zadaxin en varios países para hepatitis '
                 'B y C crónicas y como adyuvante inmunológico. No cuenta con aprobación '
                 'de la FDA de Estados Unidos. Comprobar el estatus vigente en México '
                 'antes de afirmar nada.',
   'wada': 'NO está nombrada en la Lista de Prohibiciones. Es una molécula distinta de la '
           'timosina beta-4, con la que se confunde a menudo. Su situación depende de si '
           'existe aprobación sanitaria vigente aplicable (cláusula S0): verificar caso a caso.',
   'fuente_wada': WADA,
 },
 'protocolos': [
  {'estudio': 'Hepatitis C que no respondió al tratamiento previo (aleatorizado, multicéntrico)',
   'pmid': '22233415',
   'modelo': 'Humanos; 552 pacientes con hepatitis C que no respondieron a peginterferón alfa-2a o 2b con ribavirina, aleatorizados a timosina alfa-1 (n = 275) o placebo (n = 277)',
   'via': 'Subcutánea',
   'pauta': 'Timosina alfa-1 1,6 mg dos veces por semana durante 48 semanas, sobre una base de peginterferón alfa-2a 180 µg/semana con ribavirina 800–1200 mg/día',
   'desenlace': 'Respuesta virológica en pacientes no respondedores'},
  {'estudio': 'Pancreatitis aguda necrosante grave prevista (multicéntrico)',
   'pmid': '35713670',
   'modelo': 'Humanos; pacientes con predicción de pancreatitis aguda necrosante grave, estudio multicéntrico',
   'via': 'Subcutánea',
   'pauta': 'Tα1 1,6 mg cada 12 h durante los primeros 7 días y 1,6 mg una vez al día los 7 días siguientes, frente a placebo de salino',
   'desenlace': 'Refuerzo inmunitario y desenlaces clínicos en pancreatitis grave'},
  {'estudio': 'Prevención de covid-19 en pacientes en diálisis renal (piloto aleatorizado)',
   'pmid': '36881981',
   'modelo': 'Humanos; 194 pacientes en diálisis renal aleatorizados 1:1',
   'via': 'Subcutánea',
   'pauta': 'Grupo A: Tα1 1,6 mg dos veces por semana durante 8 semanas. Grupo B: control sin Tα1',
   'desenlace': 'Infección por covid-19 y morbilidad asociada'},
  {'estudio': 'Combinación con peginterferón en hepatitis B con HBeAg positivo',
   'pmid': '22726105',
   'modelo': 'Humanos; 51 pacientes repartidos en combinación (n = 26) y monoterapia (n = 25)',
   'via': 'Subcutánea',
   'pauta': 'Timosina alfa-1 1,6 mg dos veces por semana durante las primeras 12 semanas, sobre peginterferón alfa-2a 180 µg semanales durante 48 semanas',
   'desenlace': 'Respuesta combinada definida como seroconversión de HBeAg, supresión del ADN del VHB y normalización de la ALT: 15,4 % frente a 12,0 % al final del tratamiento (p = 0,725)'},
  {'estudio': 'Monoterapia a dos niveles de dosis en hepatitis B',
   'pmid': '21227010',
   'modelo': 'Humanos; 25 pacientes con hepatitis B y antígeno e positivo, aleatorizados a tres grupos',
   'via': 'No especificada en el resumen',
   'pauta': 'Monoterapia durante 52 semanas: 1,6 mg de Tα1 activa (grupo A), 1,6 mg de Tα1 recombinante (grupo B) o 3,2 mg de Tα1 recombinante (grupo C)',
   'desenlace': 'Síntesis de citocinas por linfocitos T colaboradores de tipo 1 y de tipo 2'},
 ],
 'avisos': [
   'No confundir timosina ALFA-1 con timosina BETA-4 (TB-500). Son moléculas distintas, '
   'con literatura distinta y con estatus distinto en la lista de la WADA.',
   'La pauta de 1,6 mg dos veces por semana se repite en casi todo el programa clínico. '
   'Eso NO la convierte en una recomendación: es el diseño de esos ensayos y así debe leerse.',
 ],
 'pendientes': [
   'La secuencia literal de los 28 aminoácidos no se obtuvo de PubChem en formato '
   'citable. Conviene sacarla de UniProt antes de publicarla.',
   'Confirmar el estatus regulatorio vigente en México (COFEPRIS) antes de decir nada '
   'sobre aprobación en la monografía.',
 ],
})
