# Ejecución Raditech — pasos 1 a 7

Fecha de ejecución: 2026-08-05  
Mercado medido: Google México, español, desktop  
Estado: ejecutado y verificado  
Protección comercial: no se publicaron nombres, logotipos ni datos nuevos de clientes.

## Resumen ejecutivo

- Se midieron 21 consultas con DataForSEO SERP Live Advanced.
- Raditech ocupa el top 20 en 15 de 21 consultas y el top 10 en 8.
- Mejor posición actual: #4.
- Frente al barrido del 31 de julio, la muestra pasó de 13 a 15 consultas en top 20, de 5 a 8 en top 10 y de una mejor posición #5 a #4. Es una comparación temporal, no una atribución causal.
- Se detectaron 15 quick wins entre posiciones 4 y 20; `servidor pacs` quedó apenas fuera, en #22.
- No se tocaron title ni H1 de las páginas que ya están ganando posiciones. Cambiarlos ahora introduciría riesgo y dificultaría medir el efecto del trabajo reciente.
- Se corrigieron enlaces internos que todavía pasaban por redirecciones antiguas y se añadieron tres enlaces contextuales nuevos hacia `/sistema-pacs-ris/`.
- Las páginas del sitemap que enlazan contextualmente a la landing PACS/RIS pasaron de 23 a 30 de 34.
- La verificación pública pasó 27 de 27 comprobaciones.
- La línea base de rankings quedó capturada. La de leads y cotizaciones no puede reconstruirse honestamente con el acceso e instrumentación actuales; quedó registrada como no medible, no como cero.

---

## Paso 1. Actualizar medición de keywords y SERPs

Método:

- Endpoint: DataForSEO SERP Live Advanced.
- 21 tareas enviadas y 21 resultados utilizables.
- Ubicación 2484, idioma `es`, desktop, profundidad solicitada 20.
- Costo real reportado: USD 0.084.
- Se preservó la respuesta cruda antes de resumirla.

### Línea base

| Indicador | 2026-07-31 | 2026-08-05 | Variación |
|---|---:|---:|---:|
| Keywords en top 20 | 13 | 15 | +2 |
| Keywords en top 10 | 5 | 8 | +3 |
| Mejor posición | 5 | 4 | +1 posición |

`servidor pacs` apareció en #22. Se separó correctamente de la métrica top 20; el primer resumen lo contaba por haber sido devuelto por la API y el script fue corregido y reconstruido desde el crudo, sin incurrir en una segunda consulta pagada.

### Visibilidad competitiva en la misma muestra

| Dominio | Top 20 | Top 10 | Mejor posición |
|---|---:|---:|---:|
| raditech.mx | 15 | 8 | 4 |
| radiocare.mx | 11 | 7 | 2 |
| nubix.cloud | 11 | 8 | 5 |
| technodomus.com | 10 | 7 | 2 |

Interpretación: Raditech ya aparece para más consultas de la muestra, pero Radiocare y Technodomus conservan posiciones máximas más altas. Nubix mantiene una presencia informativa comparable en top 10. La prioridad no es publicar más texto por volumen, sino mover consultas comerciales que ya están cerca.

---

## Paso 2. Detectar y priorizar páginas en posiciones 4–20

### Prioridad A — defender y empujar top 10

| Keyword | Posición | URL |
|---|---:|---|
| servicio de teleradiología | 4 | `/teleradiologia-alta-especialidad/` |
| teleradiología México | 4 | `/teleradiologia-alta-especialidad/` |
| monitores para radiología | 5 | `/monitores-medicos-radiologia/` |
| monitores médicos | 6 | `/monitores-medicos-radiologia/` |
| software PACS | 7 | `/sistema-pacs-ris/` |
| PACS RIS | 8 | `/sistema-pacs-ris/` |
| PACS México | 9 | `/pacs-teleradiologia/` |
| sistema PACS RIS | 10 | `/sistema-pacs-ris/` |

Acción: no alterar title/H1 durante las próximas dos mediciones semanales; reforzar señales internas y autoridad externa.

### Prioridad B — mover segunda página hacia top 10

| Keyword | Posición | URL |
|---|---:|---|
| empresas de teleradiología | 13 | `/teleradiologia-alta-especialidad/` |
| software hospitalario | 13 | `/sistema-his-medsi/` |
| sistema HIS | 15 | `/sistema-his-medsi/` |
| teleradiología | 18 | `/teleradiologia-alta-especialidad/` |
| sistema PACS | 19 | `/sistema-pacs-ris/` |
| monitor grado médico | 19 | `/monitores-medicos-radiologia/` |
| PACS | 20 | `/sistema-pacs-ris/` |

Acción: enlaces contextuales, mejor arquitectura y enlaces externos; evitar perseguir `PACS` como principal KPI porque su SERP es ambigua y mezcla marca, producto e intención informativa.

### Próxima oportunidad

- `servidor pacs`: #22 hacia `/sistema-pacs-ris/`.

### Consultas sin Raditech en top 20

- `qué es pacs`
- `visor dicom`
- `interpretación de estudios radiológicos`
- `sistema ris`
- `expediente clínico electrónico`

Estas no deben recibir el mismo presupuesto. `qué es pacs`, `visor dicom` y `sistema ris` son oportunidades de contenido y autoridad; `expediente clínico electrónico` pertenece al clúster HIS y tiene mucha competencia informativa.

---

## Paso 3. Auditar keyword–intención–title–H1–contenido

| URL | Señal actual | Decisión |
|---|---|---|
| `/sistema-pacs-ris/` | Title: `Sistema PACS RIS | Software de Radiología | Raditech`; H1: `Sistema PACS-RIS` | Alineación correcta. No cambiar. |
| `/pacs-teleradiologia/` | Title y H1 orientados a PACS y teleradiología | Mantener para `PACS México`; no fusionar mientras conserve top 10. |
| `/teleradiologia-alta-especialidad/` | Title incluye teleradiología; H1 es más operacional | Está #4 en dos consultas comerciales. Congelar antes de experimentar con H1. |
| `/monitores-medicos-radiologia/` | Title y H1 contienen monitores médicos/radiología | Alineación correcta; está #5–#6. No cambiar. |
| `/sistema-his-medsi/` | Title actual orientado a software hospitalario; H1 a sistema HIS | Correcto. Google muestra una variante de título distinta; esperar recrawl y dos mediciones antes de tocar. |

Conclusión: no se encontró un error de title/H1 suficientemente claro que justificara arriesgar páginas ya ascendentes. La corrección ejecutada se concentró en arquitectura e interlinks, donde sí había defectos verificables.

---

## Paso 4. Reforzar `/sistema-pacs-ris/` como landing central

Se realizó una limpieza dirigida de destinos internos obsoletos:

- Objetos revisados y respaldados: IDs 10, 358, 636, 842, 862, 871, 879, 881 y 883.
- Destinos antiguos sustituidos por las URLs finales de PACS/RIS, teleradiología, HIS, monitores y alta especialidad.
- Se corrigieron 54 ocurrencias de almacenamiento entre `post_content` y `_elementor_data`. Varias eran copias del mismo enlace visual guardadas en ambas capas de Elementor; no representan 54 enlaces distintos en pantalla.
- Se conservaron títulos, H1, diseño, slugs y textos comerciales.
- Se limpiaron cachés de Elementor y del sitio.

Resultado arquitectónico:

- Fuentes contextuales hacia `/sistema-pacs-ris/`: 23 antes, 30 después.
- Solo quedaron sin enlazar la propia landing y tres páginas de baja relevancia directa: índice del blog, contacto y teleradiografía.
- No se añadieron enlaces por cumplir una cuota; se evitó sobreoptimizar páginas sin contexto PACS/RIS.
- El pilar recibió dos enlaces salientes hacia guías educativas existentes: `qué es un sistema PACS y cómo funciona` y `guía de implementación de un sistema PACS`.
- El crawl final revisó 38 destinos internos únicos: cero destinos vía 301 y cero destinos 404.

---

## Paso 5. Organizar interlinks desde guías técnicas

Se añadieron tres enlaces contextuales visibles y naturales:

1. Artículo de teleradiología estratégica, en el párrafo de integración DICOM/HL7.
2. FAQ, dentro de la respuesta de presentación y demo PACS.
3. Artículo de radiología a distancia, sobre el concepto de sistema PACS.

Anchor texts utilizados:

- `el sistema PACS-RIS`
- `solución PACS-RIS de Raditech`
- `sistema PACS`

No se usó el mismo anchor exacto en los tres casos. Tampoco se añadieron enlaces a todos los artículos de manera mecánica.

Verificación pública:

- 11 páginas revisadas en versión normal y con cache-busting.
- Cinco destinos finales comprobados con HTTP 200.
- Cero URLs obsoletas en las páginas verificadas.
- Marcadores de los tres enlaces contextuales presentes.
- Resultado automatizado ampliado: 29/29, `PASS`.
- Verificación visual anónima: portada y FAQ mantienen encabezado, hero, acordeones, CTA, formulario y pie de página sin HTML roto ni desbordamientos. La captura completa requirió desplazar la página para activar contenido diferido; tras hacerlo, las secciones aparecieron correctamente.

---

## Paso 6. Diseñar autoridad sin revelar clientes

Se creó un plan específico que prohíbe revelar cartera y prioriza activos que puedan obtener enlaces por utilidad técnica:

1. Matriz de evaluación PACS-RIS.
2. Calculadora de almacenamiento y ancho de banda PACS.
3. Diagrama DICOM–HL7–RIS–PACS.
4. Checklist normativo con fuentes primarias.
5. Guía neutral de selección de monitores médicos.
6. Benchmark operativo agregado y anonimizado, solo cuando exista un mínimo suficiente de casos.

Meta inicial propuesta para 90 días:

- Dos activos enlazables publicados.
- 30 contactos de outreach relevantes y personalizados.
- Entre 5 y 8 dominios de referencia nuevos y temáticamente relevantes.

Protecciones:

- No nombres, logotipos, ubicaciones, contactos ni fotografías identificables.
- Métricas agrupadas y redondeadas.
- Eliminación de metadatos.
- Revisión de riesgo de reidentificación antes de publicar.

Riesgo detectado: la portada ya muestra tres testimonios con nombres propios. No se modificaron porque no estaba confirmado si corresponden a personal interno, colaboradores autorizados o personas asociadas a clientes. Debe resolverse antes de reutilizarlos en nuevos activos.

Documento: `docs/estrategia-autoridad-raditech-sin-clientes-2026-08-05.md`.

---

## Paso 7. Capturar rankings, leads y cotizaciones

### Rankings

Línea base válida capturada:

- 21 keywords.
- 15 en top 20.
- 8 en top 10.
- Mejor posición #4.

Frecuencia recomendada: semanal, conservando la misma ubicación, idioma, dispositivo y conjunto de keywords.

### GSC y GA4

Hallazgos:

- Etiqueta GA4 detectada: `G-B3DKMWLLJ5`.
- Site Kit tiene Search Console y Analytics 4 activos y conectados.
- El usuario técnico utilizado para la auditoría carece de los scopes OAuth necesarios para leer reportes agregados:
  - `webmasters`
  - `analytics.readonly`
- En la portada se detectaron seis enlaces de WhatsApp.
- No se detectaron eventos personalizados `whatsapp_click`, `generate_lead` ni `form_submit`.
- Existe un formulario HubSpot en la FAQ.

### Estado honesto de la línea base comercial

No fue posible obtener un número fiable de leads orgánicos, cotizaciones o contratos de los últimos 28 días. El valor se registra como `null / no medible`, no como cero.

Para comenzar a medir correctamente deben instrumentarse, sin datos personales:

- `whatsapp_click`
- `lead_form_submit`
- `demo_request`
- `quote_request`

Después deben cruzarse mensualmente con el CRM:

1. Leads orgánicos calificados.
2. Cotizaciones originadas por búsqueda orgánica.
3. Contratos y valor comercial generado.

La primera línea base comercial limpia podrá calcularse 28 días después de reautorizar los reportes e instrumentar los eventos.

Archivo estructurado: `docs/data/raditech-baseline-seo-leads-2026-08-05.json`.

---

## Archivos de evidencia

- `docs/data/raditech-serps-live-2026-08-05.json`
- `docs/data/raditech-quickwins-2026-08-05.json`
- `docs/data/raditech-arquitectura-pacs-ris-2026-08-05.json`
- `docs/data/raditech-verificacion-interlinks-2026-08-05.json`
- `docs/data/raditech-sitekit-discovery-2026-08-05.json`
- `docs/data/raditech-baseline-seo-leads-2026-08-05.json`
- `docs/estrategia-autoridad-raditech-sin-clientes-2026-08-05.md`
- `backups/raditech-2026-08-05-internal-links-before.json`
- `backups/raditech-2026-08-05-elementor-links-before.json`
- `backups/raditech-2026-08-05-vira-links-before.json`
- `backups/raditech-2026-08-05-vira-elementor-links-before.json`
- `backups/raditech-2026-08-05-interlink-candidates-before.json`
- `backups/raditech-2026-08-05-contextual-interlinks-apply-before.json`
- `backups/raditech-2026-08-05-home-high-specialty-links-before.json`
- `backups/raditech-2026-08-05-home-high-specialty-elementor-before.json`
- `backups/raditech-2026-08-05-landing-high-specialty-links-before.json`
- `backups/raditech-2026-08-05-landing-high-specialty-elementor-before.json`
- `backups/raditech-2026-08-05-remaining-internal-destinations-before.json`
- `backups/raditech-2026-08-05-pillar-outbound-links-before.json`

## Próxima decisión requerida

Antes de crear nuevos contenidos o modificar páginas que ya están en top 10:

1. Confirmar si los testimonios con nombres propios de la portada son internos/autorizados o deben anonimizarse.
2. Elegir el primer activo enlazable: matriz PACS-RIS o calculadora de capacidad PACS.
3. Autorizar la instrumentación de eventos GA4 y la reautorización de scopes de Site Kit.
