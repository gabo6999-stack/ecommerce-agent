#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Moleculas 8 a 16."""
NR = ('no reportado en el resumen — pendiente de comprobar en el texto '
      'completo')
PC = 'PubChem PUG REST, consultado el 2026-09-22'
WADA = ('Lista de Prohibiciones WADA vigente 2026; lectura interna del PDF '
        'contrastada con USADA (2026-08-29). Revalidar cada 1 de enero.')

MOLECULAS = []

# ──────────────────────────────── 8. Selank (producto 1699)
MOLECULAS.append({
 'slug': 'selank', 'nombre': 'Selank',
 'producto': {'id': 1699, 'nombre': 'Selank',
              'url': 'https://peptidosysuplementos.mx/product/selank-10-mg',
              'presentacion': '10 mg'},
 'identidad': {
   'nombre_quimico': 'Heptapéptido sintético: análogo del fragmento tuftsina con una '
                     'extensión Pro-Gly-Pro',
   'inn': 'No tiene DCI',
   'sinonimos': ['Selank', 'Selanc', 'TP-7', 'Thr-Lys-Pro-Arg-Pro-Gly-Pro'],
   'cas': '129954-34-3',
   'formula_molecular': 'C33H57N11O9',
   'peso_molecular_da': '751.9',
   'secuencia_aminoacidos': 'Thr-Lys-Pro-Arg-Pro-Gly-Pro (heptapéptido)',
   'pubchem_cid': 11765600,
   'fuente_identidad': PC,
 },
 'estado_evidencia': {
   'escalon': 'preclínica en roedores, más ensayos clínicos rusos pequeños de los que el '
              'resumen no declara la pauta',
   'texto': 'La bibliografía de Selank es mayoritariamente rusa y preclínica en roedores. '
            'En PubMed, «selank» devuelve 136 registros, de los que 6 están tipificados '
            'como ensayo clínico y 3 como aleatorizado (consulta del 22-sep-2026). Los dos '
            'ensayos comparativos localizados se publicaron en revistas rusas y sus '
            'resúmenes no declaran la dosis empleada, lo que impide construir una fila '
            'completa a partir de ellos.',
   'consultas_pubmed': [
     {'consulta': 'selank', 'resultados': 136, 'fecha': '2026-09-22'},
     {'consulta': 'selank AND clinical trial[pt]', 'resultados': 6, 'fecha': '2026-09-22'},
   ],
 },
 'regulatorio': {
   'aprobacion': 'Registrado en Rusia como ansiolítico peptídico. Sin aprobación en '
                 'Estados Unidos ni en la Unión Europea.',
   'wada': 'No está nombrado en la Lista de Prohibiciones. Queda sujeto a la cláusula S0 '
           'si no cuenta con aprobación sanitaria vigente aplicable: verificar caso a caso.',
   'fuente_wada': WADA,
 },
 'protocolos': [
  {'estudio': 'Deterioro de memoria inducido por etanol',
   'pmid': '31625062',
   'modelo': 'Rata no consanguínea que recibió etanol al 10 % como única fuente de líquido durante 30 semanas, evaluada a los 9 meses',
   'via': 'Intraperitoneal',
   'pauta': '0,3 mg/kg al día durante 7 días',
   'desenlace': 'Prueba de reconocimiento de objetos (efecto cognitivo-estimulante, p < 0,05; prevención de las alteraciones inducidas por etanol, p < 0,01); contenido de BDNF en hipocampo y corteza frontal ex vivo (p < 0,05)'},
  {'estudio': 'Signos aversivos de la abstinencia de morfina',
   'pmid': '36322304',
   'modelo': 'Rata no consanguínea dependiente de morfina, modelo de abstinencia precipitada con naloxona',
   'via': 'Intraperitoneal',
   'pauta': 'Inyección intraperitoneal única de 0,3 mg/kg. Comparador: diazepam 2 mg/kg',
   'desenlace': 'Índice total del síndrome de abstinencia (reducción del 39,6 % con Selank y del 49,3 % con diazepam); reacciones convulsivas, ptosis y alteraciones posturales (p < 0,0001); umbral de sensibilidad táctil (aumento de 9 veces con Selank y de 13 con diazepam)'},
  {'estudio': 'Comparación de la vía intranasal y la intraperitoneal en dos cepas de ratón',
   'pmid': '29787664',
   'modelo': 'Ratón consanguíneo BALB/c y C57BL/6',
   'via': 'Intraperitoneal e intranasal',
   'pauta': '300 µg/kg/día durante 5 días, por cada una de las dos vías',
   'desenlace': 'Conducta en laberinto elevado en cruz; unión de marcadores a receptores NMDA y GABA cerebrales. El efecto solo se observó en BALB/c. Por vía intraperitoneal aumentó un 38 % la unión a receptores GABA en corteza frontal; por vía intranasal aumentó un 23 % la unión a receptores NMDA en hipocampo'},
  {'estudio': 'Trastorno de ansiedad generalizada y neurastenia (aleatorizado)',
   'pmid': '18454096',
   'modelo': 'Humanos; 62 pacientes con trastorno de ansiedad generalizada y neurastenia: 30 con Selank y 32 con medazepam',
   'via': NR,
   'pauta': NR,
   'desenlace': 'Escalas psicométricas de Hamilton, Zung y CGI; actividad de encefalinas en suero y semivida de la leu-encefalina'},
  {'estudio': 'Comparación con fenazepam en trastornos de ansiedad',
   'pmid': '25176261',
   'modelo': 'Humanos; 60 pacientes con trastornos fóbico-ansiosos y somatomorfos (F40.2-9, F41.1-9, F45.0-1 de la CIE-10)',
   'via': NR,
   'pauta': NR,
   'desenlace': 'Efecto ansiolítico y tolerabilidad frente a fenazepam; persistencia del efecto una semana después de la última toma; calidad de vida'},
 ],
 'evidencia_extra': [
  {'pmid': '30255741',
   'modelo': 'In vitro; membranas plasmáticas de células cerebrales',
   'nota': 'Estudio de unión de radioligando que sitúa a Selank como modulador alostérico '
           'positivo de la unión de [3H]GABA, con interacción no aditiva frente a '
           'benzodiacepinas.',
   'motivo': 'El resumen no declara las concentraciones ensayadas: sin ese dato la fila '
             'quedaría con la celda de pauta vacía y sin valor.'},
 ],
 'avisos': [
   'Los dos ensayos en personas no declaran la dosis en el resumen. Si la monografía los '
   'cita, tiene que decir eso mismo, no rellenar el hueco con la dosis de los estudios en '
   'rata: son especies distintas y vías distintas.',
 ],
 'pendientes': [
   'Conseguir el texto completo de 18454096 y 25176261 (revistas rusas) para rellenar vía '
   'y pauta, o dejar las celdas con la fórmula literal de «no reportado».',
 ],
})

# ──────────────────────────────── 9. Semaglutida (productos 1518 y 1689)
MOLECULAS.append({
 'slug': 'semaglutida', 'nombre': 'Semaglutida',
 'producto': {'id': [1689, 1518], 'nombre': 'Semaglutida 5 mg y 20 mg',
              'url': 'https://peptidosysuplementos.mx/product/semaglutida-5-mg',
              'presentacion': '5 mg y 20 mg',
              'nota': 'El plan de rediseño contempla fusionar estas dos fichas'},
 'identidad': {
   'nombre_quimico': 'Análogo acilado del péptido similar al glucagón tipo 1 (GLP-1)',
   'inn': 'semaglutide',
   'sinonimos': ['Semaglutida', 'Semaglutidum', 'Ozempic', 'Wegovy', 'Rybelsus',
                 'NN9535', 'NNC 0113-0217'],
   'cas': '910463-68-2',
   'formula_molecular': 'C187H291N45O59',
   'peso_molecular_da': '4114',
   'secuencia_aminoacidos': '31 residuos con sustituciones Aib8 y Arg34 sobre GLP-1(7-37), '
                            'y una cadena de ácido graso C18 diácido unida a Lys26 mediante '
                            'un espaciador de ácido gamma-glutámico y dos unidades de AEEA',
   'pubchem_cid': 56843331,
   'inchikey': 'DLSWIYLPEUIQAV-CCUURXOWSA-N',
   'atc': 'A10BJ06',
   'fuente_identidad': PC,
 },
 'estado_evidencia': {
   'escalon': 'medicamento aprobado, con ensayos de fase 3 y de desenlaces '
              'cardiovasculares de decenas de miles de participantes',
   'texto': 'Semaglutida es un medicamento aprobado y uno de los fármacos más estudiados '
            'de su clase. En PubMed, «semaglutide» devuelve 5705 registros, de los que 349 '
            'están tipificados como ensayo clínico y 318 como ensayo aleatorizado '
            '(consulta del 22-sep-2026). Las dosis que aparecen en la tabla son las de los '
            'ensayos y se reportan tal cual, con su población y su duración.',
   'consultas_pubmed': [
     {'consulta': 'semaglutide', 'resultados': 5705, 'fecha': '2026-09-22'},
     {'consulta': 'semaglutide AND clinical trial[pt]', 'resultados': 349, 'fecha': '2026-09-22'},
     {'consulta': 'semaglutide AND randomized controlled trial[pt]', 'resultados': 318, 'fecha': '2026-09-22'},
   ],
 },
 'regulatorio': {
   'aprobacion': 'Aprobada por agencias reguladoras para diabetes tipo 2 y para el manejo '
                 'crónico del peso, con distintas marcas y presentaciones. Código ATC A10BJ06.',
   'wada': 'NO prohibida: tiene aprobación regulatoria y no figura en la sección S2. Está '
           'en el Programa de Monitoreo y no requiere autorización de uso terapéutico. El '
           'criterio de la WADA aquí es regulatorio, no farmacológico.',
   'fuente_wada': WADA,
 },
 'protocolos': [
  {'estudio': 'Semaglutida semanal en adultos con sobrepeso u obesidad (STEP 1)',
   'pmid': '33567185',
   'modelo': 'Humanos; 1961 adultos sin diabetes con IMC ≥ 30, o ≥ 27 con al menos una enfermedad concomitante relacionada con el peso; doble ciego, aleatorización 2:1',
   'via': 'Subcutánea',
   'pauta': '2,4 mg una vez por semana durante 68 semanas, junto con intervención sobre el estilo de vida, frente a placebo',
   'desenlace': 'Cambio porcentual del peso corporal y reducción de al menos el 5 %. Cambio medio a la semana 68: −14,9 % con semaglutida frente a −2,4 % con placebo (diferencia −12,4 puntos porcentuales; IC 95 % −13,4 a −11,5). Náuseas y diarrea fueron los eventos adversos más frecuentes'},
  {'estudio': 'Desenlaces cardiovasculares en diabetes tipo 2 (SUSTAIN-6)',
   'pmid': '27633186',
   'modelo': 'Humanos; 3297 pacientes con diabetes tipo 2 en tratamiento estándar',
   'via': 'Subcutánea',
   'pauta': '0,5 mg o 1,0 mg una vez por semana durante 104 semanas, frente a placebo',
   'desenlace': 'Primer episodio de muerte cardiovascular, infarto de miocardio no mortal o ictus no mortal (variable compuesta); hipótesis de no inferioridad con margen de 1,8 para el límite superior del IC 95 % del cociente de riesgos'},
  {'estudio': 'Desenlaces cardiovasculares en obesidad sin diabetes (SELECT)',
   'pmid': '37952131',
   'modelo': 'Humanos; 17 604 pacientes de 45 años o más con enfermedad cardiovascular previa e IMC ≥ 27, sin antecedentes de diabetes; 8803 a semaglutida y 8801 a placebo',
   'via': 'Subcutánea',
   'pauta': '2,4 mg una vez por semana; exposición media de 34,2 ± 13,7 meses y seguimiento medio de 39,8 ± 9,4 meses',
   'desenlace': 'Compuesto de muerte cardiovascular, infarto de miocardio no mortal o ictus no mortal: 6,5 % frente a 8,0 % (cociente de riesgos 0,80; IC 95 % 0,72 a 0,90; p < 0,001). Suspensión permanente por eventos adversos: 16,6 % frente a 8,2 %'},
  {'estudio': 'Semaglutida como comparador activo frente a tirzepatida (SURPASS-2)',
   'pmid': '34170647',
   'modelo': 'Humanos; 1879 pacientes con diabetes tipo 2, HbA1c media basal 8,28 %, edad media 56,6 años, peso medio 93,7 kg; ensayo abierto de fase 3',
   'via': 'Subcutánea',
   'pauta': 'Semaglutida 1 mg una vez por semana durante 40 semanas, frente a tirzepatida 5, 10 o 15 mg, con aleatorización 1:1:1:1',
   'desenlace': 'Cambio de HbA1c desde el inicio hasta la semana 40: −1,86 puntos porcentuales con semaglutida. Reducción de peso corporal y eventos adversos gastrointestinales (náuseas 18 %, diarrea 12 %, vómitos 8 %)'},
 ],
 'avisos': [
   'Los estudios en personas SÍ entran, con su n y su diseño: lo que no entra nunca es '
   'convertir esas cifras a una pauta para el lector.',
 ],
 'pendientes': [],
})

# ──────────────────────────────── 10. Tirzepatida (producto 1525)
MOLECULAS.append({
 'slug': 'tirzepatida', 'nombre': 'Tirzepatida',
 'producto': {'id': 1525, 'nombre': 'Tirzepatida',
              'url': 'https://peptidosysuplementos.mx/product/tirzepatida',
              'presentacion': '30 mg y 60 mg'},
 'identidad': {
   'nombre_quimico': 'Agonista dual de los receptores del polipéptido insulinotrópico '
                     'dependiente de glucosa (GIP) y del GLP-1, acilado',
   'inn': 'tirzepatide',
   'sinonimos': ['Tirzepatida', 'Mounjaro', 'Zepbound', 'LY3298176'],
   'cas': '2023788-19-2',
   'formula_molecular': 'C225H348N48O68',
   'peso_molecular_da': '4813',
   'secuencia_aminoacidos': '39 residuos derivados de la secuencia del GIP, con un ácido '
                            'graso C20 diácido unido a Lys20. Secuencia literal ' + NR,
   'pubchem_cid': 166567236,
   'inchikey': 'BTSOGEDATSQOAF-MCNPHUAVSA-N',
   'fuente_identidad': PC,
 },
 'estado_evidencia': {
   'escalon': 'medicamento aprobado, con programa de fase 3 (SURPASS y SURMOUNT) de miles '
              'de participantes',
   'texto': 'Tirzepatida es un medicamento aprobado. En PubMed, «tirzepatide» devuelve '
            '2538 registros, de los que 146 están tipificados como ensayo clínico y 135 '
            'como ensayo aleatorizado (consulta del 22-sep-2026).',
   'consultas_pubmed': [
     {'consulta': 'tirzepatide', 'resultados': 2538, 'fecha': '2026-09-22'},
     {'consulta': 'tirzepatide AND clinical trial[pt]', 'resultados': 146, 'fecha': '2026-09-22'},
   ],
 },
 'regulatorio': {
   'aprobacion': 'Aprobada por agencias reguladoras para diabetes tipo 2 y para el manejo '
                 'crónico del peso, con distintas marcas.',
   'wada': 'NO prohibida: tiene aprobación regulatoria y no figura en la sección S2. Está '
           'en el Programa de Monitoreo y no requiere autorización de uso terapéutico.',
   'fuente_wada': WADA,
 },
 'protocolos': [
  {'estudio': 'Tirzepatida semanal para el tratamiento de la obesidad (SURMOUNT-1)',
   'pmid': '35658024',
   'modelo': 'Humanos; 2539 adultos con IMC ≥ 30, o ≥ 27 con al menos una complicación relacionada con el peso, excluida la diabetes; peso medio basal 104,8 kg e IMC medio 38,0',
   'via': 'Subcutánea',
   'pauta': '5 mg, 10 mg o 15 mg una vez por semana durante 72 semanas, con un periodo de escalada de dosis de 20 semanas; aleatorización 1:1:1:1 frente a placebo',
   'desenlace': 'Cambio porcentual del peso a la semana 72: −15,0 % con 5 mg, −19,5 % con 10 mg, −20,9 % con 15 mg y −3,1 % con placebo (p < 0,001 en todas las comparaciones). Reducción de peso ≥ 20 %: 50 % y 57 % en los grupos de 10 y 15 mg frente al 3 % con placebo'},
  {'estudio': 'Tirzepatida frente a semaglutida en diabetes tipo 2 (SURPASS-2)',
   'pmid': '34170647',
   'modelo': 'Humanos; 1879 pacientes con diabetes tipo 2, HbA1c media basal 8,28 %; ensayo abierto de fase 3',
   'via': 'Subcutánea',
   'pauta': '5 mg, 10 mg o 15 mg una vez por semana durante 40 semanas, frente a semaglutida 1 mg; aleatorización 1:1:1:1',
   'desenlace': 'Cambio de HbA1c a la semana 40: −2,01, −2,24 y −2,30 puntos porcentuales con 5, 10 y 15 mg frente a −1,86 con semaglutida. Diferencias de peso frente a semaglutida: −1,9 kg, −3,6 kg y −5,5 kg (p < 0,001). Hipoglucemia (< 54 mg/dL) en 0,6 %, 0,2 % y 1,7 %'},
  {'estudio': 'Monoterapia en pacientes chinos con diabetes tipo 2 temprana',
   'pmid': '42296968',
   'modelo': 'Humanos; adultos chinos con diabetes tipo 2 que no habían recibido antidiabéticos en los 90 días previos; aleatorización 1:1:1:1',
   'via': 'Subcutánea',
   'pauta': '5, 10 o 15 mg una vez por semana durante 40 semanas, frente a placebo',
   'desenlace': 'Reducción de HbA1c desde el inicio hasta la semana 40 (−2,17 %, −2,06 % y −2,15 % con 5, 10 y 15 mg) y reducción de peso corporal, ambas mayores que con placebo'},
 ],
 'evidencia_extra': [
  {'pmid': '42594122',
   'modelo': 'Humanos; análisis post hoc del programa SURMOUNT (SURMOUNT-1 a 4)',
   'nota': 'Análisis post hoc de la proporción de participantes que alcanzaron a la vez '
           'reducción de peso, reducción de presión arterial sistólica ≥ 5 mmHg y colesterol '
           'no-HDL < 130 mg/dL: 32 %–38 % con tirzepatida frente a 2 %–8 % con placebo.',
   'motivo': 'Es un análisis post hoc de ensayos ya citados, no un estudio primario con '
             'pauta propia.'},
 ],
 'avisos': [],
 'pendientes': [
   'Añadir al menos una fila de SURPASS-CVOT o SURMOUNT-2 para cubrir desenlaces '
   'cardiovasculares y población con diabetes.',
   'La secuencia literal de los 39 residuos no se obtuvo en formato citable.',
 ],
})

# ──────────────────────────────── 11. IGF-1 LR3 (producto 1128)
MOLECULAS.append({
 'slug': 'igf-1-lr3', 'nombre': 'IGF-1 LR3',
 'producto': {'id': 1128, 'nombre': 'IGF-1 LR3',
              'url': 'https://peptidosysuplementos.mx/product/igf-1-lr3-1mg',
              'presentacion': '1 mg'},
 'identidad': {
   'nombre_quimico': 'Análogo del factor de crecimiento similar a la insulina tipo 1 con '
                     'baja afinidad por las proteínas de unión a IGF y alta afinidad por '
                     'el receptor de IGF-1',
   'inn': 'No tiene DCI',
   'sinonimos': ['Long R3 IGF-I', 'LR3 IGF-I', 'IGF-1 LR3'],
   'cas': NR,
   'formula_molecular': NR,
   'peso_molecular_da': NR,
   'secuencia_aminoacidos': NR,
   'pubchem_cid': None,
   'fuente_identidad': 'PubChem NO devuelve ningún registro para «IGF-1 LR3», «long R3 '
                       'IGF-I» ni «mecasermin» por nombre (consultado el 2026-09-22). La '
                       'descripción funcional del análogo sí la dan literalmente los '
                       'resúmenes de los PMID 39679943 y 33938236.',
 },
 'estado_evidencia': {
   'escalon': 'preclínica; sin ensayos clínicos indexados con esa denominación. La serie '
              'principal es en feto ovino y su resultado más reciente es negativo',
   'texto': 'En PubMed, la consulta «"long R3 IGF-I" OR "LR3 IGF-I" OR "IGF-1 LR3"» '
            'devuelve 79 registros y NINGUNO tipificado como ensayo clínico ni como ensayo '
            'aleatorizado (consulta del 22-sep-2026). La serie experimental más consistente '
            'es de infusión en feto ovino de gestación tardía, y su publicación más reciente '
            'concluye que el tratamiento NO mejoró el crecimiento en fetos con restricción '
            'del crecimiento.',
   'consultas_pubmed': [
     {'consulta': '"long R3 IGF-I" OR "LR3 IGF-I" OR "IGF-1 LR3"', 'resultados': 79, 'fecha': '2026-09-22'},
     {'consulta': '(lo anterior) AND clinical trial[pt]', 'resultados': 0, 'fecha': '2026-09-22'},
   ],
 },
 'regulatorio': {
   'aprobacion': 'Sin aprobación. Se produce y se vende como reactivo de investigación '
                 'bioquímica y como suplemento de medios de cultivo celular.',
   'wada': 'PROHIBIDO. Sección S2.3 (factores de crecimiento): el IGF-1 y sus análogos '
           'están nombrados.',
   'fuente_wada': WADA,
 },
 'protocolos': [
  {'estudio': 'Infusión de una semana en feto ovino con restricción del crecimiento (resultado negativo)',
   'pmid': '39679943',
   'modelo': 'Feto ovino de gestación tardía con restricción del crecimiento por insuficiencia placentaria; 7 con tratamiento y 7 con vehículo',
   'via': 'Infusión directa en la circulación fetal',
   'pauta': '1,17 ± 0,12 µg·kg⁻¹·h⁻¹ durante 1 semana',
   'desenlace': 'Peso corporal fetal, insulina, glucosa, oxígeno y aminoácidos plasmáticos antes y al final; secreción de insulina estimulada por glucosa el último día. No hubo diferencias en peso, insulina, glucosa, oxígeno ni en la secreción de insulina; los aminoácidos circulantes descendieron (p = 0,0232)'},
  {'estudio': 'Infusión de una semana en feto ovino normal: efecto sobre el islote',
   'pmid': '33938236',
   'modelo': 'Feto ovino de gestación tardía normal; 8 con IGF-1 LR3 y 9 control',
   'via': 'Infusión directa en la circulación fetal',
   'pauta': 'Infusión durante 1 semana; valor numérico de la dosis ' + NR,
   'desenlace': 'Insulina y glucosa plasmáticas (p = 0,0135 y p = 0,0012); secreción de insulina estimulada por glucosa con pinzamiento hiperglucémico (p = 0,0453); secreción de insulina en islotes fetales aislados en incubación estática (p = 0,0447), sin diferencias en el contenido pancreático de insulina'},
  {'estudio': 'Crecimiento de órganos y transferencia de nutrientes',
   'pmid': '33427051',
   'modelo': 'Feto ovino de gestación tardía cateterizado; 8 con LR3 IGF-1 y 8 con salino',
   'via': 'Intravenosa (infusión)',
   'pauta': 'Infusión intravenosa durante 1 semana; valor numérico de la dosis ' + NR,
   'desenlace': 'Peso fetal (3,260 ± 0,211 kg frente a 3,682 ± 0,183; p = 0,15); peso de corazón, glándula suprarrenal y bazo (p < 0,05); flujo uterino y umbilical; captación umbilical de glucosa, lactato, oxígeno y aminoácidos; cinética de proteínas fetales; proliferación de mioblastos en músculo esquelético'},
  {'estudio': 'Infusión aguda de 90 minutos',
   'pmid': '37114757',
   'modelo': 'Feto ovino de gestación tardía; 10 animales en la fase in vivo y 6 más 6 en la de islotes aislados',
   'via': 'Infusión directa en la circulación fetal',
   'pauta': 'Infusión de 90 minutos; valor numérico de la dosis ' + NR,
   'desenlace': 'Insulina plasmática fetal (p < 0,05) y secreción de insulina durante pinzamiento hiperglucémico (66 % menor que el control, p < 0,0001); secreción de insulina en islotes aislados tras la infusión, que no difirió'},
 ],
 'evidencia_extra': [
  {'pmid': '20675162',
   'modelo': 'Análisis de un vial de producto incautado',
   'nota': 'Caracterización por espectrometría de masas de alta resolución de un vial de '
           'mercado negro: contenía Long-R³-IGF-I con una etiqueta de seis histidinas unida '
           'al extremo C-terminal mediante los aminoácidos enlazadores Leu-Glu. Los autores '
           'señalan que ese material se produce para estudios bioquímicos y que los efectos '
           'de la forma con etiqueta de histidinas en personas no se han descrito.',
   'motivo': 'Es un informe analítico de un producto, no un estudio con pauta: va en la '
             'sección de evidencia, con su valor de calidad y trazabilidad.'},
 ],
 'avisos': [
   'El resultado más reciente de la serie es NEGATIVO. Una monografía que solo cite los '
   'trabajos de 2021 y omita el de 2025 estaría seleccionando la evidencia.',
   'Esta molécula cierra el punto pendiente de la Fase 4: la ficha 1128 tiene una fila '
   'con «6,6 µg·kg⁻¹·h⁻¹, 1 semana, fetos ovinos normales» SIN PMID. Ver «pendientes».',
 ],
 'pendientes': [
   'LA FILA SIN CITA DE LA FICHA 1128: la cifra de 6,6 µg·kg⁻¹·h⁻¹ en feto ovino normal '
   'durante 1 semana aparece literalmente en el resumen del PMID 39679943, donde los '
   'autores describen SU PROPIO trabajo anterior, que es el PMID 33938236. Es decir: la '
   'fuente de la fila es 33938236, pero el número no está en el resumen de 33938236 sino '
   'en el del artículo posterior. Antes de publicarla hay que confirmarlo en el texto '
   'completo de 33938236. Mientras tanto, la fila de 33938236 lleva la fórmula literal de '
   '«no reportado». NO se debe atribuir el número a 39679943, cuya dosis propia es '
   '1,17 µg·kg⁻¹·h⁻¹.',
   'No hay CAS, fórmula ni peso molecular verificables en PubChem. No inventarlos.',
 ],
})

# ──────────────────────────────── 12. MOTS-c (productos 790 y 793)
MOLECULAS.append({
 'slug': 'mots-c', 'nombre': 'MOTS-c',
 'producto': {'id': [790, 793], 'nombre': 'MOTS-c 10 mg y 40 mg',
              'url': 'https://peptidosysuplementos.mx/product/mots-c-10mg',
              'presentacion': '10 mg y 40 mg',
              'nota': 'La ficha de 40 mg canoniza a la de 10 mg'},
 'identidad': {
   'nombre_quimico': 'Péptido de 16 aminoácidos codificado por un marco de lectura abierto '
                     'corto del ARN ribosómico 12S mitocondrial',
   'inn': 'No tiene DCI',
   'sinonimos': ['MOTS-c', 'Mitochondrial open reading frame of the 12S rRNA-c',
                 'Péptido mitocondrial MOTS-c'],
   'cas': '1627580-64-6',
   'formula_molecular': 'C101H152N28O22S2',
   'peso_molecular_da': '2174.6',
   'secuencia_aminoacidos': 'Met-Arg-Trp-Gln-Glu-Met-Gly-Tyr-Ile-Phe-Tyr-Pro-Arg-Lys-Leu-Arg '
                            '(MRWQEMGYIFYPRKLR, 16 aminoácidos)',
   'pubchem_cid': 146675088,
   'fuente_identidad': PC,
 },
 'estado_evidencia': {
   'escalon': 'preclínica abundante en roedores; en personas, casi toda la literatura mide '
              'MOTS-c como BIOMARCADOR en sangre, no lo administra',
   'texto': 'Hay que distinguir dos literaturas. La preclínica administra MOTS-c a '
            'roedores y mide desenlaces. La humana, mucho más numerosa, mide la '
            'concentración de MOTS-c circulante en distintas enfermedades: son estudios de '
            'asociación, no de administración. En PubMed, «MOTS-c» devuelve 258 registros, '
            'de los que 5 están tipificados como ensayo clínico (consulta del 22-sep-2026); '
            'al revisarlos, los que involucran personas miden el péptido endógeno.',
   'consultas_pubmed': [
     {'consulta': '"MOTS-c"', 'resultados': 258, 'fecha': '2026-09-22'},
     {'consulta': '"MOTS-c" AND clinical trial[pt]', 'resultados': 5, 'fecha': '2026-09-22'},
   ],
 },
 'regulatorio': {
   'aprobacion': 'Sin aprobación en ninguna jurisdicción.',
   'wada': 'No está nombrado en la Lista de Prohibiciones. Queda sujeto a la cláusula S0 '
           '(sustancia sin aprobación sanitaria vigente para uso humano).',
   'fuente_wada': WADA,
 },
 'protocolos': [
  {'estudio': 'Modelo de autismo inducido por ácido valproico',
   'pmid': '41706383',
   'modelo': 'Cría de rata Sprague-Dawley, hembra y macho, de madres que recibieron 500 mg/kg de ácido valproico por vía intraperitoneal en el día embrionario 12',
   'via': 'Intraperitoneal',
   'pauta': '0,5 mg/kg/día desde el día posnatal 21 hasta el 46, frente a salino',
   'desenlace': 'Efectos terapéuticos conductuales y papel de la tetrahidrobiopterina; consultar el resumen completo para la lista exacta'},
  {'estudio': 'Lesión por isquemia-reperfusión miocárdica en corazón aislado',
   'pmid': '41593376',
   'modelo': 'Corazón de rata aislado y perfundido en montaje de Langendorff, sometido a 30 min de isquemia global y 60 min de reperfusión',
   'via': 'Perfusión en tampón de Krebs-Henseleit',
   'pauta': '0,25 a 0,7 mg/kg administrados durante los primeros 10 min de reperfusión',
   'desenlace': 'Tamaño del infarto (reducción del 73 % con 0,5 mg/kg frente a isquemia-reperfusión sola); frecuencia cardiaca, presión desarrollada del ventrículo izquierdo, producto presión-frecuencia y presión telediastólica'},
  {'estudio': 'Cebado metabólico de la corteza suprarrenal',
   'pmid': '41811086',
   'modelo': 'Rata Wistar macho adulta; 16 animales',
   'via': 'Subcutánea, con bombas microosmóticas',
   'pauta': '0,1 µmol cada 24 h en infusión continua durante 24 horas, frente a salino',
   'desenlace': 'Vías metabólicas de la corteza suprarrenal y esteroidogénesis'},
  {'estudio': 'Lesión cerebral asociada a un modelo experimental',
   'pmid': '40753494',
   'modelo': 'Ratón',
   'via': NR,
   'pauta': '20 mg/kg administrados cuatro horas antes de establecer el modelo',
   'desenlace': 'Efecto protector frente a la lesión cerebral; consultar el resumen completo para la lista exacta de desenlaces'},
  {'estudio': 'Análogo modificado R13A-MOTS-c en lesión pulmonar por radiación',
   'pmid': '42142418',
   'modelo': 'Ratón C57BL/6 expuesto a 20 Gy de irradiación torácica. ATENCIÓN: el compuesto ensayado es el ANÁLOGO MODIFICADO R13A-MOTS-c, no MOTS-c',
   'via': 'Intraperitoneal',
   'pauta': 'R13A-MOTS-c 5 mg/kg al día durante 2 semanas',
   'desenlace': 'Inflamación pulmonar, estrés oxidativo y disfunción mitocondrial inducidos por radiación; activación de Nrf2 y transporte mediado por LAT1'},
 ],
 'evidencia_extra': [
  {'pmid': '25738459',
   'modelo': 'Ratón',
   'nota': 'Artículo fundacional que describe el marco de lectura abierto corto del ARNr 12S '
           'que codifica MOTS-c, identifica el músculo esquelético como su órgano diana '
           'principal y describe la inhibición del ciclo del folato y la activación de AMPK. '
           'Informa que el tratamiento en ratón previno la resistencia a la insulina '
           'dependiente de la edad y la inducida por dieta alta en grasa, y la obesidad '
           'inducida por dieta.',
   'motivo': 'El resumen no declara ni la vía ni la pauta: sin esos dos datos la fila '
             'quedaría con dos celdas vacías. Va en la sección de evidencia.'},
 ],
 'avisos': [
   'La distinción entre administrar MOTS-c y medirlo como biomarcador es la más importante '
   'de esta molécula. Un estudio que encuentra MOTS-c bajo en una enfermedad no dice nada '
   'sobre administrarlo.',
   'La fila de 42142418 es de un ANÁLOGO MODIFICADO (R13A), no de MOTS-c. Va etiquetado '
   'dentro de la propia celda.',
 ],
 'pendientes': [
   'Verificar la especie y la vía del PMID 41268602 (5 mg/kg en restricción del crecimiento '
   'intrauterino por hipoxia) antes de añadirlo como fila.',
   'Los desenlaces exactos de 41706383 y 40753494 hay que anotarlos del resumen completo.',
 ],
})
