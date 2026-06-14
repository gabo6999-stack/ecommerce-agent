# Estrategia de Backlinks — Raditech · PTM Novo · PYS

Playbook que respalda a [`backlinks_agent.py`](backlinks_agent.py). Basado en la política
vigente de Google (2025-2026) y tácticas seguras por nicho. Investigado el 2026-06-13.

> **Regla de oro:** calidad > cantidad. La mejor estrategia no es *perseguir* enlaces, es
> *merecerlos*. Casi todo lo que Google penaliza es perseguir enlaces; casi nada penaliza ganarlos.

**Cómo acceder:** CLI (`python backlinks_agent.py`) o desde el chat web (botón **🔗 Backlinks** en el
agente SEO → ruta `/backlinks`). Ambos usan la misma lógica y persistencia (`backlinks_data/`).

---

## 1. Cómo enforce Google hoy (lo que cambia toda la estrategia)

- **SpamBrain NEUTRALIZA, no penaliza.** Desde el *link spam update* de dic-2022, Google detecta
  enlaces no naturales y los "apaga" (no pasan PageRank). La mayoría de los enlaces comprados/spam
  hoy **simplemente no hacen nada** — dinero y esfuerzo desperdiciados, no una sentencia de muerte.
- **El peligro real es la ACCIÓN MANUAL** ("Unnatural links to your site"), revisada por humanos,
  visible en Search Console, que exige limpieza + reconsideración. Se gatilla con esquemas evidentes
  y a escala creados por el propio sitio.
- **Site reputation abuse (marzo-2024):** contenido patrocinado/parasitario *fuera de tema* en un
  sitio reputado, hecho para pedir prestada autoridad, ahora es violación. No buscar "patrocinios"
  en medios off-topic.
- **Atributos obligatorios:** todo enlace pagado/regalado/auto-colocado debe llevar `rel="sponsored"`
  o `rel="nofollow"` (y `rel="ugc"` en contenido de usuario). No ayuda al ranking, pero es 100% seguro
  y sirve para marca, tráfico y E-E-A-T.

## 2. Qué EVITAR (violaciones explícitas)

Comprar/vender enlaces que pasen ranking · niche edits/advertorials pagados sin nofollow ·
guest posting a escala con anchors exact-match · press releases con anchors optimizados · PBNs ·
granjas de enlaces · intercambios recíprocos excesivos · spam de comentarios/foros/perfiles ·
widgets/infografías con enlaces sembrados · directorios masivos de baja calidad · enlaces sitewide
en footer/plantilla · dominios expirados por su autoridad · automatización de enlaces ·
**anchors exact-match comerciales repetidos a escala** (señal #1 de patrón manipulado).

## 3. Qué SÍ hacer (white-hat, por prioridad)

1. **Activos linkables:** datos/estudios originales, guías profundas, herramientas/calculadoras.
2. **Digital PR:** historias y datos noticiables ofrecidos a periodistas (la táctica mejor valorada).
3. **Plataformas de fuentes expertas:** Featured (sucesor de HARO), Qwoted, SourceBottle.
4. **Reclamo de menciones de marca sin enlace; broken-link building; colaboraciones genuinas.**
5. **Citaciones locales** con NAP idéntico (Google Business Profile + directorios serios).
6. **Internal linking** con anchors descriptivos (100% bajo tu control, palanca real).

### 3b. Prospección por intersección (`link_intersect`) — la de mayor ROI

Encuentra los dominios que enlazan a tus **competidores pero no a ti** ("link gap"). Es la táctica
más precisa y de cero riesgo: no inventa fuentes, te muestra sitios que **ya enlazan a tu nicho**.

1. Exporta los backlinks de 1-3 competidores (gratis en **Ahrefs Free Backlink Checker**, **Ubersuggest**,
   **Semrush**, **Moz**, o el reporte de **Enlaces** de Google Search Console).
2. (Opcional) Exporta también tus propios backlinks para excluir a quien ya te enlaza.
3. El agente cruza los CSVs, descarta spam y ordena por **cuántos competidores** enlazan cada dominio
   (más competidores = prospecto más fuerte). Sube `min_competitors` a **2** para quedarte con la élite.
4. Cada dominio resultante pasa por el flujo normal `fetch_url → score_prospect → save_prospect`.

> El agente **sugiere esta táctica por su cuenta** cuando pides backlinks, mencionas competidores, o la
> búsqueda web se queda corta.

### 3c. Planificador de activos linkables (`score_asset_idea` → `save_asset_idea`)

La forma **más segura y de mayor ROI** de ganar enlaces: crear recursos que los atraen solos.
Un *activo linkable* gana enlaces por sí mismo (datos/estudios originales, guías de referencia,
herramientas/calculadoras, comparativas, glosarios, encuestas). **Un blog normal NO lo es.**

El agente puntúa cada idea (0-100) para no disfrazar contenido genérico de activo:

| Dimensión | Máx |
|---|---|
| Atractivo para enlazar | 30 |
| Originalidad / dato propio | 25 |
| Gancho de PR (noticiable) | 20 |
| Valor perdurable (evergreen) | 10 |
| Factibilidad de producción | 15 |

Veredictos: **BUILD** ≥70 · **CONSIDER** 45-69 · **SKIP** <45. Guardia: si el atractivo o la
originalidad son muy bajos → **SKIP** automático (es contenido, no activo). Pipeline de estados:
`idea → briefed → in_production → published → promoting → earned`, con conteo de enlaces ganados.

**Arquetipos por sitio:**
- **raditech:** "Estado de la teleradiología en México 2026" (encuesta) · guía de cumplimiento NOM /
  interoperabilidad DICOM-HL7 · calculadora de ROI vs estudio in-house · glosario PACS/RIS/DICOM.
- **grupoptm / PTM Novo:** encuesta de acceso a telemedicina (datos no clínicos = PR seguro) · guía
  "cómo funciona la consulta" · glosario de péptidos/hormonas revisado médicamente (E-E-A-T).
- **pys:** guía de dosificación de péptidos basada en evidencia (E-E-A-T) · encuesta a la comunidad
  fitness/biohacking MX · calculadora de macros/recuperación · infografías citables con atribución.

> La **producción** del contenido la hace tu agente de blogs/SEO (`web.py`) o tú; el planificador
> define qué crear, lo prioriza y fija el gancho de PR y a quién pitchearlo.

## 4. Anchor text

Mayoría **de marca** / URL desnuda / genéricos naturales ("ver aquí"). Los exact-match comerciales,
una minoría pequeña. Nunca repetir el mismo anchor comercial en muchos sitios.

## 5. Rubro de calificación (determinista, en `score_prospect`)

| Dimensión | Máx |
|---|---|
| Relevancia temática | 30 |
| Autoridad/calidad del dominio | 25 |
| Estándar editorial | 15 |
| Contexto del enlace | 10 |
| Ajuste idioma/geo | 10 |
| **Penalización spam (flags suaves)** | hasta −40 |

Veredictos: **PURSUE** ≥70 · **REVIEW** 45-69 · **REJECT** <45.
**Flags críticos → REJECT automático:** `sells_links, pbn, deindexed, malware, cloaking,
irrelevant_niche, link_farm, adult_gambling_pharma_spam, scraped_content`.

## 6. Disavow — regla de dos partes (máxima restricción)

Solo hacer disavow si **AMBAS** son ciertas:
1. Tienes (o esperas con evidencia fuerte) una **acción manual** por enlaces no naturales, **Y**
2. los enlaces son **auto-construidos/comprados** y **no puedes quitarlos** en la fuente.

Para spam orgánico, comment/scraper y **ataques de SEO negativo** en un sitio limpio → **NO disavow**
(SpamBrain ya los neutraliza). Los "toxicity scores" de Semrush/Ahrefs/Moz **no los usa Google**;
no desautorizar solo por un puntaje rojo. Primero intentar **remover** en la fuente. Ante la duda, NO.

> Nota: Google ya casi no necesita el disavow y Mueller anticipó (2024) que podrían **retirar la
> herramienta**. El agente genera solo un **borrador** que el dueño revisa y sube manualmente.

## 6b. Monitor anti-SEO-negativo (`monitor_backlinks`)

Como GSC no expone backlinks por API, el monitor compara **snapshots** de tus exports en el tiempo.
Detecta señales de ataque: **pico de velocidad** de enlaces, **dominios tóxicos nuevos** y **anchors
spam súbitos** (ej. "comprar viagra" apuntando a tu sitio). La 1ª corrida fija la línea base.

> **No cundir el pánico.** Un pico de enlaces basura casi siempre es SEO negativo que **SpamBrain
> neutraliza solo** → **no es motivo de disavow**. Si no hay acción manual en GSC y tu historial es
> limpio: documenta y vigila, no toques los enlaces. Solo escala a disavow si llega una acción manual.

**Uso en chat:** *"Monitorea los backlinks de raditech"* y pegas tu CSV.

**Programarlo (headless)** — corre semanal/quincenal y te avisa solo si hay alertas:
```powershell
python backlinks_agent.py monitor raditech "C:\ruta\backlinks_raditech.csv"
```
Exit code **0** = sin novedad · **1** = alertas (úsalo en Task Scheduler para disparar una notificación)
· **2** = error de uso. Snapshots e historial en `backlinks_data/snapshots/` y `monitor_*_<site>.json`.
Flujo recomendado: exportas el CSV fresco a una ruta fija → una tarea programada de Windows corre el
comando sobre esa ruta cada semana.

## 7. Playbooks por sitio

### raditech.mx — B2B imagen médica (México/LATAM)
Asociaciones/colegios de radiología e informática médica · directorios serios de healthcare-IT y
proveedores hospitalarios · prensa B2B de tecnología y salud en español · partnerships con
clínicas/hospitales (casos de éxito) · listados de expositores en congresos/expos médicas ·
liderazgo de pensamiento en LinkedIn · co-marketing con fabricantes/integradores no competidores.
Inglés OK para directorios médicos internacionales serios. Evitar directorios B2B pay-to-list genéricos.

### grupoptm.com / PTM Novo — telemedicina (YMYL)
- **Doctoralia MX** (`pro.doctoralia.com.mx`) — perfil verificado gratis por cada médico, ~48h.
- **Google Business Profile** (config. telesalud) con NAP idéntico — señal local #1.
- **Sociedad Mexicana de Telemedicina, Telesalud y Medicina Digital** (`soctelmed.com`) — membresía.
- Marco **CENETEC / Salud Digital** (NOM-036-SSA3-2015) — alineación + citación relevante.
- Digital PR con **datos originales no clínicos** (acceso a telesalud en México); páginas linkables
  (cómo funciona la consulta, privacidad de datos). Autoría médica acreditada en cada página clínica.
- Horizonte: 6+ meses, velocidad de enlaces estable, anchors de marca.

### peptidosysuplementos.mx (PYS) — ecommerce péptidos/suplementos (YMYL restringido)
Nicho restringido: los medios mainstream casi no enlazan; casi todo enlace "follow" que aparece suele
ser pagado (riesgo). **No forzar enlaces de baja calidad.** Apóyate en: blogs/medios de fitness,
nutrición y biohacking en español · reseñas de creadores reales (con `rel=sponsored` si hay pago/producto)
· partnerships de marca (distribuidor autorizado), gimnasios, entrenadores, nutriólogos · citaciones
locales (GBP, Sección Amarilla, Cylex MX) · podcasts/YouTube · recursos linkables basados en evidencia.
Aceptar que muchos enlaces legítimos serán y deben ser nofollow/sponsored.

## 8. Reglas de marca (obligatorias)
- Nunca "farmacia" → usar **"Tienda en línea"**.
- Nunca la frase de refrigeración para garantizar integridad del producto en transporte.

---

## Fuentes clave

- Google Search Central — Spam Policies (Link spam): https://developers.google.com/search/docs/essentials/spam-policies
- December 2022 link spam update (SpamBrain): https://developers.google.com/search/blog/2022/12/december-22-link-spam-update
- March 2024 core update & new spam policies: https://developers.google.com/search/blog/2024/03/core-update-spam-policies
- Disavow links — GSC Help (la mayoría no lo necesita): https://support.google.com/webmasters/answer/2648487
- Manual actions report — GSC Help: https://support.google.com/webmasters/answer/9044175
- "Most sites don't need to disavow" — Search Engine Roundtable: https://www.seroundtable.com/google-disavow-advice-41042.html
- High-Quality Link Building for YMYL Sites (2025) — Ranktracker: https://www.ranktracker.com/blog/high-quality-link-building-for-ymyl-sites-2025/
- Link building para telehealth sin tácticas riesgosas — Bask Health: https://bask.health/blog/best-link-building-strategies
- Doctoralia MX (perfil gratuito): https://pro.doctoralia.com.mx/
- Sociedad Mexicana de Telemedicina, Telesalud y Medicina Digital: https://soctelmed.com/telesalud
