# Auditoría competitiva SEO de PYS — 2026-08-03

## Alcance y evidencia

- Mercado: México (`location_code=2484`), idioma español, escritorio.
- Fuente: DataForSEO SERP Live.
- Consultas: 12/12 de la línea base.
- Resultados orgánicos del top 10: 120/120.
- Profundidad adicional: hasta 100 resultados para localizar PYS.
- Páginas visibles comparadas: 25/25 con HTTP 200.
- Costo real registrado: USD $0.214.
- Producción modificada: no.

Datos:

- `docs/data/audit-pys-serps-live-2026-08-03.json`
- `docs/data/audit-pys-pages-live-2026-08-03.json`

## Hallazgos confirmados

### Composición agregada del top 10

| Tipo | Resultados |
|---|---:|
| Competidores comerciales directos | 30/120 (25.0%) |
| Marketplaces y retail general | 22/120 (18.3%) |
| Otros actores comerciales | 22/120 (18.3%) |
| Editoriales, médicos y redes sociales | 41/120 (34.2%) |
| Entidades públicas o académicas | 5/120 (4.2%) |

### Competidores por coincidencia real

| Dominio | Consultas cubiertas | Apariciones top 10 | Papel |
|---|---:|---:|---|
| exomapeptides.mx | 9/12 (75%) | 11/120 (9.2%) | Benchmark principal |
| peptide.com.mx | 3/12 (25%) | 7/120 (5.8%) | Rival secundario |
| zelara.com.mx | 3/12 (25%) | 3/120 (2.5%) | Rival secundario |

Criterio falsable: el benchmark directo debe aparecer repetidamente en consultas comerciales medidas y ofrecer producto o página comparable. Exoma cumple en 9/12 consultas.

### Situación por consulta

| Consulta | Mejor presencia de PYS | Denominador SERP | Decisión |
|---|---:|---:|---|
| `bpc 157 precio` | fuera del top 100 | 10/10 | Trabajar solo si habrá BPC-157 individual |
| `selank` | 59 | 10/10 | Observar |
| `cagrilintida` | fuera del top 100 | 10/10 | Descartar esta intención para ficha comercial |
| `retatrutide precio` | post 60; producto fuera | 10/10 | Prioridad comercial; esperar maduración |
| `agua bacteriostatica` | 66 | 10/10 | Seguimiento |
| `mots-c` | 86 | 10/10 | Observar |
| `ipamorelina` | fuera del top 100 | 10/10 | Resolver oferta individual vs. combo |
| `igf-1 lr3` | 73 | 10/10 | Observar |
| `sermorelin` | fuera del top 100 | 10/10 | Experimento pequeño de grafía |
| `thymosin alpha 1` | fuera del top 100 | 10/10 | Observar; SERP mixto |
| `tirzepatida precio mexico` | fuera del top 100 | 10/10 | Descartar: intención Mounjaro |
| `nad iv` | fuera del top 100 | 10/10 | Descartar para ficha: intención clínica/terapia |

PYS apareció dentro del top 100 en 5/12 consultas y dentro del top 10 en 0/12.

### Longitud visible y técnica

En las 9 consultas donde Exoma apareció dentro del top 10, PYS tuvo más texto visible en 7/9 comparaciones. Exoma fue más largo solo en BPC-157 (2,504 vs. 3,344 palabras) e ipamorelina (3,046 vs. 3,527). No se justifica otra expansión general de contenido.

En 12/12 fichas de PYS se confirmó HTTP 200, `index,follow`, self-canonical e inclusión en `product-sitemap.xml`. Para retatrutida también se confirmó el 301 antiguo hacia la ficha, seis enlaces desde el post posicionado, title comercial y H1 limpio. No se confirmó un bloqueo técnico básico.

## Hipótesis pendientes

- Las optimizaciones del 2026-07-30 tenían cuatro días al medir; la ausencia de mejora todavía no falsifica la táctica.
- Google podría sustituir gradualmente el post de retatrutida por la ficha comercial.
- Añadir `Sermorelin` al title y la introducción podría mejorar correspondencia lingüística.
- Si la muestra madura no mejora, autoridad y enlaces podrían ser una palanca mayor que más contenido.

## Prioridades

1. No reescribir de nuevo las doce fichas; proteger el experimento.
2. Vigilar consulta–URL e indexación en GSC, especialmente retatrutida.
3. Decidir si habrá BPC-157 e ipamorelina individuales; el desajuste no se resuelve con más texto.
4. Preparar, sin publicar sin autorización, un experimento aislado para `Sermorelin`.
5. No invertir en las intenciones `cagrilintida`, `tirzepatida precio mexico` y `nad iv` para las fichas actuales.

## Calendario y umbral

- Línea base de publicación: 2026-07-30.
- Señal inicial, semana 4: 2026-08-27.
- Decisión madura, semana 8: 2026-09-24.
- Umbral: si en semana 8 menos del 50% de las fichas maduras mejora al menos 10 posiciones, no repetir expansión de contenido; medir autoridad/enlaces y reconsiderar consulta–oferta.

Mantener las mismas 12 consultas, México/escritorio, y reportar numeradores/denominadores. No modificar producción sin autorización explícita.
