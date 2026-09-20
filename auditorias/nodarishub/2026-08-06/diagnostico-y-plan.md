# Diagnóstico y plan de trabajo SEO — NodarisHub Ecuador y México

Fecha de medición: 2026-08-06 local / 2026-08-07 UTC

## 1. Alcance y fuentes

- 12/12 URLs regionales del sitemap examinadas mediante HTML público anónimo.
- 6/6 pares Ecuador–México comparados.
- 12/12 consultas medidas con DataForSEO SERP Live:
  - Ecuador: `location_code=2218`, idioma español, escritorio.
  - México: `location_code=2484`, idioma español, escritorio.
- 120/120 primeros resultados orgánicos clasificados por tipo.
- 94/120 de esos resultados también estaban dentro de `rank_absolute ≤10`: 47/60 EC y 47/60 MX; los demás fueron desplazados por módulos SERP.
- Profundidad adicional aproximada de 30 resultados orgánicos por consulta para localizar NodarisHub.
- 12/12 ganadores orgánicos descargados y comparados con la URL propietaria de NodarisHub.
- Volumen y dificultad solicitados para 12/12 consultas.
- DataForSEO Labs `ranked_keywords` consultado para ambos mercados.
- Costo DataForSEO registrado de esta línea base: USD 0.30144.
- Search Console, GA4 y CrUX no están configurados en el runtime actual; por tanto, no se afirma indexación ni rendimiento a partir de datos de Google propietario.
- No se modificó WordPress ni producción.

## 2. Hallazgos confirmados

### 2.1 Infraestructura internacional

- HTTP 200: 12/12 URLs.
- Canonical self-referencing correcto: 12/12.
- `hreflang` con `es-EC`, `es-MX` y `x-default`: 12/12.
- `noindex`: 0/12.
- H1 presente: 12/12.
- Meta description presente: 12/12.
- Imágenes sin `alt`: 4/44; las cuatro están en las dos páginas de inicio.

Conclusión: el bloqueo principal no es un fallo básico de canonical, hreflang o indexabilidad declarada.

### 2.2 Similitud Ecuador–México

- Promedio de similitud secuencial visible: 94.02%.
- Pares por encima de 90%: 6/6.
- Pares por encima de 95%: 3/6.

| Par | Similitud secuencial |
|---|---:|
| Inicio EC/MX | 96.76% |
| Software EC/MX | 96.75% |
| Diseño web EC/MX | 95.45% |
| Marketing EC/MX | 92.79% |
| Crear página web EC/MX | 91.63% |
| SEO EC/MX | 90.73% |

La localización actual distingue H1, title, moneda y algunas referencias geográficas, pero conserva la misma estructura y la mayor parte del discurso. Esto confirma que el problema histórico sigue parcialmente abierto.

La revisión independiente de headings confirmó además:

- H2 comparables idénticos: 33/33 posiciones entre los seis pares.
- Similitud media de H1: 92.75%.
- Similitud media de titles: 85.47%.
- Similitud media de meta descriptions: 85.48%.
- En 5/6 pares, el H1 cambia esencialmente el país; el sexto añade solo una variación gramatical menor.

Errores editoriales live confirmados:

- Los H1 de SEO prometían llevar el negocio a la “primera página de Google”; la promesa fue sustituida por formulaciones no garantistas en el lote publicado el 2026-08-08 UTC.
- `/mx/diseno-web/` contenía una referencia a “precios de páginas web en Ecuador” cuyo destino histórico redirigía a una página EC. Se corrigió a `/mx/crear-pagina-web/` en el lote publicado el 2026-08-08 UTC.
- La aparente separación antes del punto/coma en los H1 de portada y diseño era un artefacto del extractor de texto al cruzar un `</span>`: el HTML fuente usa `</span>.` y `</span>,` correctamente. No se publicó ninguna corrección de puntuación.

### 2.3 Visibilidad medida

- NodarisHub apareció en 0/12 consultas dentro de la profundidad devuelta por DataForSEO, aproximadamente 30 orgánicos por consulta.
- DataForSEO Labs devolvió 0 keywords posicionadas para `nodarishub.com` en Ecuador y 0 en México dentro del filtro de posición absoluta ≤100.
- Esto confirma ausencia en las fuentes medidas, pero no sustituye Search Console ni demuestra desindexación.

## 3. Composición del SERP

### Ecuador — 60/60 resultados

- Agencias comerciales directas: 40/60 (66.7%).
- Directorios o páginas editoriales: 15/60 (25.0%).
- Proveedores de software en la consulta correspondiente: 5/60 (8.3%).

Los seis SERP tienen intención compatible con las páginas de servicio. Competidores por solapamiento real:

- `agenciadigital.com.ec`: 5/6 SERPs.
- `innovacenter.ec`: 4/6.
- `hellomediaec.com`: 3/6.
- Varios dominios aparecen en 2/6.

La prioridad histórica de Ecuador queda confirmada por intención: no es un SERP dominado por plataformas globales o entidades públicas.

### México — 60/60 resultados

- Agencias comerciales directas: 23/60 (38.3%).
- Directorios/editoriales: 17/60 (28.3%).
- Público/académico: 9/60 (15.0%).
- Plataformas DIY: 4/60 (6.7%).
- Proveedores de software: 5/60 (8.3%).
- Otros/sociales: 2/60 (3.3%).

No existe un único rival transversal fuerte: los dominios con mayor solapamiento aparecen solo en 2/6 SERPs. México está mucho más fragmentado: 55 dominios únicos en 60 resultados, frente a 36/60 en Ecuador. En las seis parejas EC/MX hubo 0/6 con el mismo dominio competidor, por lo que cada país requiere su propia lista competitiva.

Desajustes confirmados:

1. `agencia digital mexico`: 8/10 resultados pertenecen a entidades públicas, 1/10 es editorial y solo 1/10 corresponde a una agencia comercial. La consulta se interpreta mayormente como entidad gubernamental.
2. `crear pagina web mexico`: 4/10 plataformas DIY, 4/10 editoriales y solo 2/10 servicios directos. No es una buena consulta principal para una agencia hecha-a-medida.

Consultas alineadas con servicios:

- `diseño de paginas web mexico`: 7/10 servicios directos.
- `agencia de marketing digital mexico`: 7/10 servicios directos.
- `agencia seo mexico`: 6/10 servicios directos, 3/10 editoriales y 1/10 otro/social.
- `desarrollo de software a medida mexico`: 5/10 proveedores directos, 4/10 editoriales y 1/10 entidad académica.

## 4. Volumen y dificultad observados

| Mercado | Consulta | Volumen | Dificultad |
|---|---|---:|---:|
| EC | agencia digital ecuador | 30 | sin dato |
| EC | crear pagina web ecuador | 10 | sin dato |
| EC | diseño de paginas web ecuador | 70 | 100 |
| EC | agencia de marketing digital ecuador | 110 | 89 |
| EC | agencia seo ecuador | 90 | sin dato |
| EC | desarrollo de software a medida ecuador | sin dato | sin dato |
| MX | agencia digital mexico | 140 | 36, pero intención incorrecta |
| MX | crear pagina web mexico | 10 | sin dato, intención DIY |
| MX | diseño de paginas web mexico | 40 | 100 |
| MX | agencia de marketing digital mexico | 480 | 100 |
| MX | agencia seo mexico | 170 | 54 |
| MX | desarrollo de software a medida mexico | sin dato | sin dato |

Los valores nulos significan que el endpoint no devolvió una métrica utilizable, no volumen cero. La dificultad es un indicador de DataForSEO y no una garantía de resultado.

## 5. Comparación con ganadores

- Ganadores descargados correctamente: 12/12.
- El ganador es más corto que NodarisHub en 6/12 consultas.
- El ganador es más largo en 6/12.

Ejemplos que falsan “añadir más texto” como receta universal:

- MX diseño web: ganador 388 palabras vs NodarisHub 1,165.
- MX software: 360 vs 1,177.
- EC crear página web: 854 vs 1,168.
- EC software: 1,133 vs 1,159.

Ejemplos donde el ganador sí ofrece mayor superficie o prueba:

- EC agencia digital: 8,823 vs 943 palabras y 10 vs 6 H2.
- EC diseño web: 5,633 vs 1,142 y 13 vs 6 H2.
- EC marketing: 2,664 vs 1,111 y 12 vs 5 H2.
- MX SEO: 2,534 vs 1,304 y 16 vs 5 H2.

La diferencia útil no es solo longitud. Los ganadores muestran industrias, portafolio, experiencia, proceso, metodología, oficinas, certificaciones, clientes o prueba operativa. NodarisHub necesita prueba local real, no relleno ni una transformación espejo.

## 6. Prioridades

### Prioridad 0 — Correcciones editoriales y de targeting confirmadas

Lote quirúrgico publicado el 2026-08-08 UTC:

1. `/mx/diseno-web/` (ID 183): referencia regional corregida y enlace cambiado a `/mx/crear-pagina-web/`.
2. `/mx/seo/` (ID 195): H1 no garantista — “Posicionamiento SEO para PyMEs en México: técnica, contenido y medición”.
3. `/ec/seo/` (ID 196): H1 no garantista — “Agencia SEO en Ecuador para mejorar visibilidad, tráfico y medición”.
4. No se tocaron portadas ni puntuación, porque la inspección de `content.raw` demostró que el supuesto defecto era un falso positivo del extractor.
5. Canonical, hreflang, títulos WordPress y `rank_math_title` se conservaron.

Verificación del lote:

- Respaldo fresco previo: 6/6 páginas candidatas; solo 3 se modificaron.
- Dry run: 3/3 páginas sin Elementor y con títulos sin cambios.
- API read-back: 6/6 comprobaciones de hash/título pasaron.
- HTML público normal y cache-bust: 45/45 comprobaciones pasaron (15 por página).
- Screenshot anónimo: 3/3 páginas con H1/bloque visible y diseño de cabecera intacto; las zonas con animaciones diferidas aparecen vacías en capturas full-page sin scroll, comportamiento preexistente no causado por el lote.
- Rollback: no requerido.

### Prioridad 1 — Ecuador: prueba local y diferenciación sustantiva

Primer lote recomendado:

1. `/ec/marketing/` — volumen 110; 8/10 resultados directos; similitud con MX 92.79%.
2. `/ec/seo/` — volumen 90; 7/10 resultados directos; similitud 90.73%.
3. `/ec/` — consulta compatible; rival transversal visible en 5/6 SERPs; similitud crítica 96.76%.

Intervención propuesta:

- Añadir módulos exclusivamente ecuatorianos con industrias reales, forma de trabajo desde Quito, alcance operativo verificable, moneda/facturación, proceso comercial y casos anonimizados.
- Cambiar ejemplos y FAQ según objeciones reales de Ecuador, no por sustitución de nombres geográficos.
- Conservar H1, title, canonical y hreflang mientras no exista evidencia para alterarlos.

Criterio de refutación:

- Si, tras indexación y periodo de medición, las páginas maduras siguen sin impresiones/posiciones y la similitud baja sustancialmente, la causa principal no era la localización; habrá que priorizar autoridad, enlaces o selección de consulta.

### Prioridad 2 — México: corregir targeting antes de escribir

1. Dejar de tratar `agencia digital mexico` como consulta principal de la portada; el SERP es gubernamental en 9/10 resultados si se incluyen redes institucionales.
2. No optimizar `/mx/crear-pagina-web/` para competir frontalmente con “crear pagina web mexico”; el SERP es DIY/plataformas en 7/10 al incluir comunidad.
3. Mantener como candidatas:
   - `/mx/seo/`: volumen 170, dificultad 54, intención directa 7/10.
   - `/mx/marketing/`: volumen 480, dificultad 100, intención directa 7/10; oportunidad de demanda, pero competencia alta.
   - `/mx/diseno-web/`: intención directa 7/10, dificultad 100.
4. Antes de modificar title/H1, ampliar keywords de agencia/servicio y elegir una consulta propietaria distinta para portada y crear-página-web.

### Prioridad 3 — Imágenes de portada

- Corregir 4/44 imágenes sin alt, concentradas en `/ec/` y `/mx/`.
- Es una mejora de accesibilidad/on-page, no la explicación de la falta de visibilidad.

## 7. Datos humanos indispensables

Para redactar sin inventar hacen falta, por país:

1. Dos o tres proyectos reales o casos anonimizables.
2. Industria del cliente.
3. Problema inicial.
4. Servicio prestado.
5. Resultado real que pueda publicarse; si no hay métrica, usar un resultado cualitativo comprobable.
6. Ciudad o alcance geográfico que pueda mencionarse.
7. Quién atendió el proyecto y desde dónde.
8. Moneda, método de pago, tiempos y proceso comercial reales.
9. Herramientas, certificaciones, alianzas o metodología que puedan demostrarse.
10. Diferencias reales entre la operación de Ecuador y México.

No se publicarán nombres, cifras, clientes, oficinas, certificaciones ni presencia local sin confirmación.

## 8. Próximo ciclo seguro

1. Recibir los datos humanos del primer lote.
2. Exportar y respaldar los tres objetos WordPress antes de editar.
3. Preparar cambios quirúrgicos dentro de los bloques `wp:html`, conservando CSS y estructura.
4. Ejecutar diff semántico y controles de no invención.
5. Mostrar el borrador/diff antes de publicar.
6. Publicar solo con autorización explícita.
7. Verificar HTML anónimo, URL normal y cache-bust, responsive y screenshot.
8. Registrar la nueva similitud y línea base.
9. Medir impresiones/posiciones después del intervalo acordado; no declarar éxito al publicar.
