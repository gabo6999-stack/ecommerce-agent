# Retrofeed y plan de mejora — 6 proyectos

Fecha: 2026-08-27
Prioridad fijada por Antonio: **PYS → Telenzia → Nodaris → Raditech → CMLC → Arcade**

Fuentes: memoria del proyecto (94 notas), bóveda Obsidian, Site Audits de Ahrefs corridos hoy, mediciones DataForSEO y GSC de jul–ago 2026.

---

# PARTE 1 — RETROFEED

## 1.1 La lección transversal: medir la SERP antes de escribir

El patrón que más valor ha producido en los seis proyectos no es una técnica de redacción, es **verificar la composición real del top-10 antes de comprometer una pieza de contenido**. Cada vez que se saltó ese paso, se perdió trabajo:

| Caso | Lo que parecía | Lo que era | Costo evitado/pagado |
|---|---|---|---|
| `glutation` (PYS) | 6,600/mes libre | Mercado de cápsulas orales, no viales | Evitado |
| `péptidos` (PYS) | 27,100/mes del nicho | Consulta de **cosmética** (Vichy, Lancôme) | Evitado |
| `retatruida` (PYS) | 314 impr en pos 7.9 | SERP 100% informacional, cero tiendas | Evitado |
| `expediente clínico electrónico` (Raditech) | SERP de gobierno | 4 de 10 son proveedores comerciales | **Pagado** — se descartó mal el clúster más grande del sitio |
| `crear página web` (Nodaris) | 880/mes comercial | DIY/"gratis", no es el comprador de agencia | Evitado |
| `biohacking` (Telenzia) | 5,800/mes KD 0 | Informacional → blog, nunca home | Evitado |

**Regla destilada:** cuando ningún competidor directo aparece en una keyword de volumen alto, la hipótesis por defecto es *"no es tu mercado"*, no *"nadie la ha trabajado"*. Y al revés: ver dos `.gob.mx` en un SERP no lo cierra — hay que contar cuántos de los 10 son comerciales.

## 1.2 La otra lección: el techo casi nunca es lo que uno cree

Tres veces se diagnosticó mal el cuello de botella y hubo que corregirlo con datos:

- **PYS — "el techo es autoridad de dominio":** falso. `exomapeptides.mx` tiene **exactamente la misma autoridad (1 dominio referente)** y saca **94× más tráfico**. El cuello es **tipo-de-URL ↔ intención** y superficie de catálogo.
- **PYS — "hay que optimizar las fichas existentes":** insuficiente. PYS tiene 0 keywords en top-10, 0 en 11-20, y su mejor posición con volumen es la **28**. De 88 a 10 no es on-page.
- **Raditech — "el rival es edenmed":** falso, es `radiocare.mx`. Y el clúster grande no era PACS (1,500/mes) sino **HIS/expediente clínico: 33,170/mes, 22× más**.

## 1.3 Retrofeed por proyecto

### PYS — mucho ejecutado, techo estructural sin tocar

**Lo hecho y verificado:**
- Campaña Rank Math completa: promedio **64.2 → 82.6**, 56 de 65 contenidos en ≥81 (desde 0 confirmados).
- Clúster GLP-1 construido: hub `/glp-1/`, `/perdida-de-peso/`, 3 comparativas, landing NAD+, todo cross-enlazado con schema.
- Canibalización guía↔ficha de retatrutida resuelta dándole **un carril a cada una** (guía = precio, ficha = comprar).
- 248 enlaces PMID creados, schema médico por mu-plugin, funnel de agua bacteriostática, 72 enlaces internos repuntados.
- Tienda de Ecuador levantada en el `.com` con estética, header y footer clonados y enrutado por país verificado 8/8.

**Lo que NO funcionó y por qué:**
- **Merchant Center: rechazado y cuenta penalizada.** La hipótesis era que el agua bacteriostática pasaría por no ser fármaco. Google evalúa **el sitio, no la ficha**. Decisión tomada: no reintentar.
- **Content AI descartado** — el test `hasContentAI` solo comprueba que compraste el producto de pago; no mide contenido y Google no lo ve.
- **El typo `retatruida` (314 impr) es un espejismo** — SERP informacional; ninguna ficha puede ganar CTR ahí.

**El hueco que sigue abierto:** de 358,390 búsquedas/mes medidas, **96% es inalcanzable o de intención equivocada**. Lo ganable son 13,840/mes. Y de ese conjunto, **`ipamorelina` (1,900/mes, la keyword individual más grande) no tiene ficha propia** — solo existe dentro del combo CJC-1295+Ipamorelina.

### Telenzia — producto listo, medición inexistente

**Lo hecho:** rebrand completo (dominio, marca libre en clase 44, sitio, app, portales), sistema Meridian en todo, HTML **−49%**, PageSpeed 99-100, Rank Math 73.9 → 81.9 con **20 de 21 tests en verde**, eslogan decidido, artículo de biohacking publicado con SERP medida antes de escribir.

**Lo que falta y es serio:** los pendientes de Telenzia **no son de SEO, son legales y de producto**:
1. Marca ante el IMPI sin solicitar (requiere e.firma).
2. El Aviso de Privacidad nombra como responsable a "Telenzia", que puede no ser la razón social registrada.
3. **`privacidad@telenzia.com` no existe** — es el canal de derechos ARCO que exige la LFPDPPP.
4. **La copy contradice su propia línea roja:** dice *"tus péptidos en la puerta"* cuando la plataforma declara que no vende, no surte, no almacena y no envía.

Y algo que salta hoy: **Telenzia no está en Ahrefs**. Los otros seis sí. No hay ninguna medición continua del sitio.

### Nodaris — infraestructura impecable, cero tracción

**Lo hecho:** migración binacional `/mx/` + `/ec/` con hreflang recíproco, 301s por mu-plugin, on-page de las 10 páginas de servicio con focus keywords elegidas por DataForSEO evitando trampas de intención, blog separado por país, consolidación de 6 entradas canibalizadas, realineación de focus keywords (blog **56 → 70**).

**El dato que enmarca todo:** `nodarishub.com` tiene **CERO posiciones en el top-100**, en Ecuador y en México. Validado contra un dominio de control. Toda la infraestructura está bien y no ha producido ranking.

**Lo que no se resolvió — y fue un error mío documentado:** al localizar EC y MX apliqué una **transformación espejo** (misma estructura, cambiando sustantivos). La similitud bajó a 89.8% con solo Ecuador hecho y **volvió a subir a 97.8-98.8%** al hacer México igual. *Fraseo paralelo no diferencia; solo diferencia la sustancia distinta.* El desbloqueo es material que no tengo: **casos de cliente reales por país**.

**Riesgo operativo vivo:** Rafa programa entradas a mano desde el editor, saltándose las compuertas del agente — salen cortas, sin portada y sin categoría de país (y sin país **se quedan en la raíz**).

### Raditech — el clúster grande apenas se tocó

**Lo hecho:** retitulado del clúster HIS/expediente, NOM-004 con 4 tablas de documentos por numeral (hueco que **ningún competidor cubría**), PACS/RIS de 639 → 1,219 palabras con el ángulo educativo correcto, CTAs auditados y añadidos donde faltaban, canibalización de blogs cerrada y verificada en GSC.

**Lo que quedó bloqueado:** la landing 890 `/sistema-his-medsi/` espera una **decisión de negocio sobre Medsi**. Raditech es reseller, no dueño de la marca — y perseguir "medsi" es tirar esfuerzo (1,863 impresiones en pos 6 con **0.1% de CTR**: quien busca la marca quiere el sitio de Medsi o su login).

**~~Dato nuevo preocupante: el tráfico cayó de ~245 a 84~~ — FALSO.** Era la estimación de Ahrefs. GSC (2026-08-29) dice **+21 clics y +1,680 impresiones**. Ver 4B.

### CMLC — el trabajo correcto, sin la palanca principal

**Lo hecho:** se descubrió que **el Perfil de Negocio de Google existe, sin reclamar y sin sitio web** (5.0★, 9 reseñas); sugerencia pública enviada; dos correos de corrección/reclamo a prensa y directorio; 3 enlaces dofollow desde nodarishub; dataset de dosis de radiación en HuggingFace con cero cifras inventadas; sitemap de Rank Math arreglado por SSH.

**El dato que enmarca todo:** Google **conoce 5 de las 11 URLs y ha rastreado 2**. Las demás están en *"Descubierta: actualmente sin indexar"* con último rastreo N/D. La verificación técnica salió toda verde. **La causa es ausencia de enlaces entrantes**, no un problema técnico. Pedir indexación URL por URL es un parche con cuota de ~9-10 al día.

**El descubrimiento que más vale:** un competidor local, *Delia Barraza Laboratorios*, **ya tiene funcionando una estrategia de contenido de salud en prensa sinaloense** con enlaces editoriales dofollow (bieninformado.mx rank 382, miciudad.mx rank 169). Es replicable y vale más que los directorios.

### Arcade — el cuello no es SEO

**Lo hecho:** infraestructura de páginas de ubicación con **indexación condicional** (noindex si <3 anuncios, se auto-indexa al crecer), 3 guías de oferta publicadas, H1 de fichas arreglado, compartir en grupos de Facebook habilitado.

**La verdad medida:** la base de datos tenía **4 anuncios activos**. El "46 autos" del home es catálogo de vanidad. **El cuello de botella es INVENTARIO, no SEO** — por eso deliberadamente NO se construyeron 30 páginas de ciudad vacías.

## 1.4 Lo que Ahrefs añadió hoy (y que no teníamos)

Tres cosas que la caja de herramientas anterior (DataForSEO + GSC) no daba:

1. **Detección de spam de enlaces etiquetada.** Cinco dominios propios están recibiendo una ráfaga de enlaces basura desde julio. En nodarishub: **192 de 195 dominios de referencia son nofollow spam**; solo quedan 2 enlaces reales (clientes) y 1 spam dofollow.
2. **Crawl técnico propio.** 42 meta descriptions duplicadas en PYS, 35 páginas de Propertyledger enlazando a una rota, 26 páginas casi huérfanas en Arcade — nada de esto salía en las auditorías previas.
3. **Backlinks de competidores.** El Backlink Checker público funciona sobre cualquier dominio y ya produjo prospectos reales y replicables para Raditech.

---

# PARTE 2 — PLAN DE MEJORA

Orden = prioridad de Antonio. Dentro de cada proyecto, orden por ROI.

---

## PRIORIDAD 1 — PYS

> **Tesis:** el on-page ya está hecho y bien. Lo que queda es **superficie de catálogo** (fichas que no existen), **higiene técnica** (lo que salió hoy) y **la única palanca nunca trabajada: enlaces**. DR 2 con 2 dominios de referencia.

### 1A. Higiene técnica — barato y medible (esta semana)

| # | Acción | Detalle | Fuente |
|---|---|---|---|
| 1 | **42 meta descriptions duplicadas** | Firma clásica de Rank Math + tema/LiteSpeed emitiendo ambas. Localizar el segundo emisor y apagarlo | Site Audit hoy |
| 2 | **5 páginas con múltiples H1** | Mismo patrón ya visto en la guía 1647 (tema + H1 en contenido) | Site Audit hoy |
| 3 | **19 páginas indexables fuera del sitemap** | + **11 redirects 3XX dentro del sitemap** que hay que sacar | Site Audit hoy |
| 4 | **80 páginas indexables enlazan a redirects** | Contradice la auditoría de "0 hops" — verificar si son redirects nuevos y repuntar al destino final | Site Audit hoy |
| 5 | **5 imágenes rotas** + 4 páginas afectadas | | Site Audit hoy |
| 6 | **1 error de validación schema.org** | | Site Audit hoy |
| 7 | **AhrefsBot recibe 403** | 92 de 332 páginas dan 4XX en el índice público de Ahrefs pero solo 6 de 673 en el crawl propio → el edge bloquea. Degrada los datos públicos | Site Explorer hoy |

> Ojo con el orden: al tocar `_elementor_data` recordar que hay que escribir en **los dos sitios** (`content.raw` y `_elementor_data`), escapar comillas antes del PUT y validar con `json.loads()` — el HTTP 200 no detecta el JSON roto.

### 1B. La ficha que falta — el mayor retorno individual

**Crear ficha propia de `ipamorelina`.** 1,900/mes, la keyword individual más grande del conjunto ganable, y hoy solo existe dentro del combo CJC-1295+Ipamorelina. Es demanda medida sin página que la atienda.

Formato: **ficha de producto**, no blog — la regla ya establecida es transaccional (precio/comprar/méxico/mg) = ficha; y el H1 va al **nombre pelado** del compuesto (`Ipamorelina`), no keyword-stuffed. Esa es la diferencia exacta que hace ganar a exoma.

### 1C. Decisión de inventario (requiere a Antonio)

**4,910/mes de demanda medida que PYS no puede atender por no tener el producto:**

| Compuesto | Vol/mes | Posición de exoma |
|---|---|---|
| tesamorelina | 3,600 | 4 |
| kisspeptina | 720 | 10 |
| pt-141 | 590 | 2 |

No es una decisión de contenido, es de compra. **El techo de superficie de PYS lo determina el tamaño del catálogo.**

### 1D. Enlaces — la palanca que nunca se trabajó

PYS tiene **DR 2 y 2 dominios de referencia**. Es lo único del stack que no se ha atacado nunca. Ahora hay herramienta gratis:

1. Correr el **Backlink Checker público** sobre exomapeptides.mx, zelara.com.mx, biopeptidos.mx y viupeptides.com.mx. Cosechar los donantes limpios (perfiles de empresa, directorios, citas editoriales).
2. **Reseñas de producto**: `reviews_allowed` ya está activo y el rating es 0/0. El schema `AggregateRating` se auto-genera con reseñas reales. **No fabricar ninguna** — pedirlas a clientes reales.
3. Recordar la regla ya zanjada: HuggingFace y GitHub son **siempre nofollow**. No sirven para autoridad.

### 1E. Ecuador — 6 pendientes que bloquean vender

La tienda está técnicamente lista y **no puede cobrar**:

1. **Datos bancarios de `bacs`** — sin ellos el cliente recibe un pedido sin instrucciones de pago. Es el #1.
2. Razón social, RUC y dirección fiscal (las páginas legales llevan un recuadro rojo visible; no se inventó ninguno a propósito, y deberían pasar por abogado en Ecuador).
3. ¿Hay RUC? Decide si entra Payphone/Datafast o se queda en transferencia. MercadoPago y Stripe **no operan en Ecuador**.
4. IVA de Ecuador (15%): definir si los $250 lo incluyen.
5. Envío: hoy es `free_shipping` como placeholder.
6. hreflang `es-MX` ↔ `es-EC` entre la ficha del `.mx` (id 19) y la del `.com` (id 11), al encender `blog_public`.

### 1F. Medición programada

La revisión de GSC del **2026-09-09** (línea base 2,239 impr / 16 clics / 0.71%) es el insumo para la decisión aplazada sobre **landings de intención en raíz** — el 2º mejor rendidor medido en exoma (41 landings → 7 en top-10; PYS tiene 6). No decidir antes.

Vigilar también la **consolidación de tirzepatida**: 465 impresiones en posiciones 10-13 pasaron detrás de un 301 y la URL destino estaba en posición 46.5. Si en 4-6 semanas no recupera, la consolidación salió cara.

---

## PRIORIDAD 2 — TELENZIA

> **Tesis:** el producto y el sitio están listos y son buenos. Lo que bloquea son **cuatro pendientes legales/de copy** y la ausencia total de medición. Nada de esto es trabajo de SEO.

### 2A. Legal y cumplimiento — antes que nada

| # | Acción | Por qué es serio |
|---|---|---|
| 1 | **Crear el buzón `privacidad@telenzia.com`** | Es el canal de derechos ARCO que exige la LFPDPPP. Sin buzón el aviso declara un canal que no existe |
| 2 | **Definir el nombre legal del responsable** en el Aviso de Privacidad | Hoy dice "Telenzia"; si la sociedad sigue registrada como Peptide Technologies México, el aviso nombra a un responsable que puede no ser el registrado |
| 3 | **Corregir la copy que contradice la línea roja** | El landing dice *"tus péptidos en la puerta"* y la metadescripción *"tus péptidos en casa"*. La plataforma declara que **no vende, no surte, no almacena, no envía**. Es exactamente la defensa legal del modelo |
| 4 | **Quitar el cross-link a PYS del schema** | Misma razón: embudar PTM → producto PYS rompe la defensa de "solo plataforma" |
| 5 | **Solicitar la marca ante el IMPI**, clase 44 | Vía libre confirmada (0 anterioridades). Requiere e.firma SAT. ~$3,000-3,500/clase, 4-6 meses. Confirmar antes en Marcanet (fonética) |

### 2B. Empezar a medir

1. **Añadir telenzia.com como proyecto verificado en Ahrefs.** Es gratis, hay cupo, y hoy es el único de los sitios activos sin ninguna medición continua. Desbloquea Site Audit + backlinks + keywords orgánicas.
2. Conectar Search Console si no lo está, y fijar una línea base.

### 2C. Contenido — el clúster ya medido

El clúster de biohacking son **~5,800/mes con KD 0** y solo hay **un artículo publicado**. La parte ganable con credibilidad:

- **`biohacking mx` + `biohacking mexico` = 1,180/mes** — el ángulo local, y ninguna plataforma médica mexicana está en ese SERP.
- `biohacking que es` (880), `biohacking detox` (320, ya abordado desmontándolo).

**No perseguir:** `biohacking spa` (buscan un lugar físico), `biohacking center` (navegacional), `biohacking suplementos` (es territorio de PYS y cruzarlo rompe la línea roja).

Todo va en **blog**, nunca en home ni en página de servicio — la intención es informacional en todo el clúster de volumen.

### 2D. Decisión menor pendiente

`/nosotros/` (76) y `/blog/` (75) no llegan a 81 solo por `keywordInPermalink`. Cambiar el slug implica 301 y tocar el menú. **Decisión de Antonio** — mi recomendación es dejarlos: 76 y 75 no frenan nada y el 301 sí cuesta.

---

## PRIORIDAD 3 — NODARIS

> **Tesis:** la infraestructura está completa y correcta, y el sitio sigue en **cero posiciones top-100**. Lo que falta no es más arquitectura: es **contenido genuinamente distinto por país** y **los primeros enlaces reales**.

### 3A. Limpiar la deuda de la consolidación 301

**40 páginas indexables enlazan a redirecciones** (+51 no indexables), con 28 redirects 3XX y 1 cadena. Los 301 del mu-plugin funcionan, pero **los enlaces internos siguen apuntando a las URLs viejas**. Cada salto diluye autoridad y gasta crawl budget. Reescribir al destino final.

También: **47 páginas noindex** (revisar si todas deben serlo) y **1 hreflang de auto-referencia faltante**.

### 3B. El desbloqueo real: casos de cliente por país

La similitud EC vs MX sigue en **97.8-98.8%** después de dos rondas. Ya está probado que el fraseo paralelo no la baja. Lo que hace falta es material que solo Antonio y Rafa tienen:

- **2-3 casos de cliente por país**, aunque sean sin nombre ("una clínica dental en Quito", "un despacho contable en Guadalajara").
- **Las industrias donde de verdad operan** en cada mercado.

Con eso se reescriben las secciones de evidencia y la similitud baja de forma legítima. **Sin ese material, cualquier reescritura produce el mismo espejo.** Este es el pendiente que más tiempo lleva parado.

### 3C. Enlaces — arrancar de dos

Solo hay **2 dominios de referencia dofollow reales** (kravetpet.com y magnosbi.com, ambos clientes). El resto es spam nofollow.

1. **Sistematizar el patrón que ya funciona:** los clientes enlazan de vuelta desde "Confían en nosotros". Cada cliente nuevo = pedirle el enlace como parte del cierre.
2. Considerar **disavow de `kaila.biz`** (DR 17, SPAM, el único spam dofollow). Los otros 192 son nofollow: ruido inofensivo, **no vale la pena desautorizarlos**.
3. **GBP por país** (Rafa EC / Antonio MX) — sigue pendiente desde julio.
4. Registrar `nodaris.ec` **defensivo y estacionado**, nunca redirigido.

### 3D. Cerrar el bypass de Rafa

Las entradas que Rafa programa a mano se saltan las compuertas: cortas, sin portada, sin país. **Va a volver a pasar.** Dos opciones:
- Revisar las programadas antes de cada lunes/viernes (recordar: auditar con `status=publish,future,draft`, no solo `publish`).
- O un mu-plugin en `transition_post_status` que rechace o marque las entradas sin categoría de país.

Recomiendo el mu-plugin: es una vez y no depende de acordarse.

### 3E. Blog → páginas de dinero

El Blog Agent ya elige temas por país. Falta que **los posts enlacen a las páginas de servicio** para pasarles autoridad. Es el mecanismo que ya se validó como sano en la auditoría anti-canibalización de EC.

---

## PRIORIDAD 4 — RADITECH

> **Tesis:** hay **tres keywords KD 0 a un empujón del top 3** y un clúster 22× más grande esperando una decisión de negocio. Y el tráfico está cayendo.

### 4A. Los empujones baratos (primero)

| Keyword | Vol/mes | KD | Pos hoy | URL |
|---|---|---|---|---|
| **ris pacs** | 150 | 0 | **7** | `/sistema-pacs-ris/` |
| **monitores medicos** | 90 | 0 | **8** | `/monitores-medicos-radiologia/` |
| ris/pacs | 40 | 0 | 5 | `/sistema-pacs-ris/` |
| pacs mexico | 20 | 0 | 10 | `/teleradiologia/` ⚠️ |

Todo KD 0 y en el fondo de la página 1. Es el mejor ROI disponible en todo el portafolio de seis sitios.

**Arreglo puntual:** `pacs mexico` rankea con `/teleradiologia/` en vez de `/sistema-pacs-ris/`. Es desajuste consulta↔página — el cuello ya diagnosticado en este sitio. Reapuntar.

### 4B. ~~Investigar la caída de tráfico~~ → RESUELTO 2026-08-29: **no hubo caída**

**El token de GSC nunca estuvo roto** (refresca 200, permiso `siteFullUser` sobre `sc-domain:raditech.mx`) y los datos reales desmienten a Ahrefs:

| | clics | impresiones |
|---|---|---|
| actual (30 jul-26 ago) | **165** | **8,829** |
| previo (2-29 jul) | 144 | 7,149 |
| cambio | **+21** | **+1,680** |

El "84 / -161" de Ahrefs es una **estimacion modelada**, no un dato. Para un sitio propio manda GSC.

**Lo que si paso, y es la noticia buena del portafolio:** colapso `medsi` (1,524 -> 85 impr, con la posicion *mejorando* de 6.5 a 5.9 - o sea cayo la demanda de la consulta, no el ranking) y **desperto el cluster HIS/expediente**:

| | antes | ahora |
|---|---|---|
| query `his` | 142 | **1,402** |
| `/expediente-clinico-electronico-mexico-guia/` | 459 | **2,358** |
| `/ris-radiologia-sistema-informacion-radiologica/` | 82 | 408 |

Perder `medsi` no costo ni un clic (era 0.1% de CTR de marca ajena). **El retitulado de julio esta funcionando.**

**El problema nuevo, y es el que hay que atacar:** las 2,358 impresiones de la guia de expediente estan en **posicion 8.4 con CERO clics**. Ya no es problema de contenido ni de descubrimiento - es pasar de posicion 8-10 al top 3. De los 165 clics del sitio, 73 son de marca (`raditech`, `ptm pacs`, `radiotech`).

WARNING **Contradiccion a resolver antes de actuar sobre 4A:** Ahrefs pone `ris pacs` en posicion 7 con 150/mes; **GSC dice que paso de 59 impresiones a CERO**. Para el sitio propio manda GSC - verificar antes de invertir ahi.

### 4C. La decisión de negocio que bloquea el clúster grande

**El clúster HIS/expediente clínico son 33,170/mes** — 22× todo el volumen comercial de PACS + teleradiología junto. Los activos ya existen y están bien escritos (945 con 3,476 palabras y 5 tablas de la NOM-004, 1076, 1023, 1087, 890).

Lo que falta: **decidir qué hacer con Medsi**. Raditech es reseller, no dueño. Ese tráfico traería clínicas buscando cumplimiento de expediente, no hospitales comprando PACS. **Es una decisión de a qué cliente se quiere atender**, y no debería moverse la landing 890 antes de tomarla.

Nota lateral pendiente: la 890 usa "Farmacia y laboratorio" como nombre de un **módulo hospitalario**. La regla global prohíbe esa palabra, pero aquí es un departamento clínico, no el sustituto de "tienda en línea" (que sería absurdo). **Falta decidir si la regla excluye el contexto hospitalario de Raditech.**

### 4D. Enlaces — prospectos ya identificados

Del perfil de `radiocare.mx` (DR 5, 670 backlinks pero solo 7-8% dofollow y buena parte comprada a granjas — **no copiar eso**), los donantes limpios y replicables:

| Donante | DR | Cómo | Esfuerzo |
|---|---|---|---|
| **actualpacs.com** | 49 | **Caso de éxito publicado por su proveedor PACS** — Raditech es reseller de Medsi, se pide el equivalente | ⭐ El mejor |
| centromedicoabc.com | 56 | Cita editorial junto a MedlinePlus e INCMNSZ | Alto valor |
| crunchbase.com | 91 | Perfil de empresa | Gratis |
| glassdoor.com.mx | 63 | Perfil de empleador — **encaja con el ángulo de reclutamiento de radiólogos** | Gratis |
| startupeable.com | 45 | Directorio de startups LatAm | Gratis |
| healthcaretechoutlook.com | 64 | Premio "Top Radiology Solution" | Postularse |
| medium.com | 94 | Blog propio (radiocare lo hace) | Trivial |

---

## PRIORIDAD 5 — CMLC

> **Tesis:** una sola acción vale más que todo lo demás junto, y no es de SEO.

### 5A. Reclamar el Perfil de Negocio de Google

**Es la acción de mayor retorno de los seis proyectos.** El perfil ya existe con **5.0★ y 9 reseñas**, NAP y horario correctos — y está **sin reclamar y sin sitio web**.

Instrucciones exactas:
- **Buscar el nombre REAL del perfil, no la marca:** `Radiología e Imagen Rx Doctor Pedro Gavito` (Place ID `/g/11h714svkn`).
- ⚠️ **Si se busca "Centro Médico Las Conchas", Google no encontrará nada y ofrecerá CREAR un negocio nuevo** → quedaría un duplicado compitiendo con el que ya tiene las reseñas. Los duplicados de GBP tardan mucho en fusionarse.
- ❌ **No renombrar el perfil a "Centro Médico Las Conchas":** eso es el **edificio**, una plaza médica con seis inquilinos independientes. El laboratorio de Teresita ya tiene ficha propia en el mismo domicilio y cualquier inquilino podría reportarlo.
- ✅ **Sí cambiar la categoría** tras reclamar: de *"Centro médico"* (genérica) a **"Centro de diagnóstico por imagen"** principal y **"Radiólogo"** secundaria.
- Usar siempre **CP 82126** (confirmado por el Dr. Pedro Gavito). Google Maps, Facebook y el geocoder de Places dicen 82123 y **están equivocados los tres**. Desconfiar del autocompletado de Places, que lo sobrescribe sin avisar.

### 5B. Prensa sinaloense — copiar la jugada del competidor

*Delia Barraza Laboratorios* ya tiene enlaces editoriales dofollow de contenido de salud en medios sinaloenses. Objetivos verificados:

- **miciudad.mx** (rank 169) — publicó un artículo de prevención de cáncer de próstata enlazando a Delia Barraza.
- **bieninformado.mx** (rank 382) — mismo patrón.
- Adicionales: losnoticieristas.com (122), culiacandigital.mx (70), miradas.mx (57), mochisdigital.mx (44).

El ángulo que ya funcionó una vez: **pedir el enlace junto con una corrección real**. Con Noroeste se usó que la nota de 2015 dice "servicio las 24 horas" y hoy es lunes a sábado 7:30-18:30. Darle al medio una razón editorial pesa más que pedir el enlace a secas.

### 5C. Seguimiento de los correos enviados

Dos reclamos siguen sin respuesta desde el 26-ago:
- `contacto@noroeste.com` (ojo: **sin `.mx`**) — si hay que insistir, el contacto pertinente es **Héctor Castro, Editor**.
- `steelyhead@vivaldi.net` (midoctormazatlan) — canal alterno: el formulario Jetpack de `/sample-page/`.

⚠️ La ficha de midoctormazatlan tiene comentarios abiertos: **no usarlos para sembrar el enlace**, es spam de comentarios y está marcado como violación explícita en el playbook.

### 5D. Lo que NO hay que hacer

- **No perseguir más indexación URL por URL.** La cuota real son ~9-10 al día y es un parche: la causa es la falta de enlaces entrantes. Reenviar el sitemap no consume cuota y da el 80% del valor.
- **No buscar más colegios de radiología** como fuente de enlaces: son dofollow pero no tienen padrón que enlace a clínicas (CMRI da 404, SMRI no lista miembros, FMRI solo enlaza colegios). Sirven para E-E-A-T on-page, no para enlaces.
- **Más datasets en HuggingFace no dan autoridad** — es nofollow, verificado dos veces en vivo.

### 5E. Pendiente de negocio

Antonio va a confirmar con Pedro **qué médicos consultan en el edificio** para evaluar una página de "Consultorios del centro". No son competencia (endodoncia, ortopedia, medicina familiar, nutrición, laboratorio) y capturaría las búsquedas del nombre del edificio, que hoy llegan al sitio y no encuentran nada.

---

## PRIORIDAD 6 — ARCADE

> **Tesis:** el SEO está más adelantado que el negocio. **No construir más páginas hasta que haya autos.**

### 6A. Lo único que importa: inventario

La base de datos tenía **4 anuncios activos**. Sin oferta, las páginas no rankean ni convierten, y construir 30 páginas de ciudad vacías sería thin content que **daña**. La infraestructura ya está lista y **se auto-indexa cuando crezca** (noindex si <3 anuncios).

Palancas de oferta por ROI, ya definidas:
1. **Lotes chicos/semi-pro** — 1 lote = 20-50 autos, y no pagan Kavak. Densidad en UNA plaza (Puebla) > cobertura.
2. **Grupos de Facebook** de compra-venta con el wedge "gratis, sin comisiones" — la función de compartir a grupos ya está construida.
3. Interceptar `kavak vender mi auto` (590/mes) — las 3 guías ya publicadas atacan esto.

### 6B. Higiene técnica del Site Audit (rápido, hazlo mientras)

Cero errores de servidor. Lo que salió es estructural:

| Acción | Cantidad |
|---|---|
| **Páginas con un solo enlace interno entrante** | **26 de 61** (43% del sitio) |
| **Páginas huérfanas** sin ningún enlace entrante | 3 |
| Títulos demasiado largos | 13 |
| Meta descriptions largas (13) / cortas (5) | 18 |
| Páginas indexables fuera del sitemap | 13 |
| Open Graph incompleto | 32 |
| Imágenes sin alt | 5 |

Para un marketplace donde **las categorías y filtros son el motor** (90% del volumen), que el 43% de las páginas tenga un solo enlace entrante es exactamente el cuello. Densificar el interlinking hub-and-spoke: guías → categorías → fichas + "anuncios relacionados".

### 6C. Fase 2 — solo cuando haya inventario

Páginas de MODELO (`/marca/{marca}/{modelo}/`), combos precio+ciudad, y carrocerías a URL limpia (`/suv/` en vez de `/buscar.php?carroceria=suv`).

---

# PARTE 3 — ACCIONES TRANSVERSALES

### 3.1 Instalar el Ahrefs SEO Toolbar

Es el mayor desbloqueo de la cuenta gratuita: da **DR/UR de cualquier sitio mientras navegas** y superpone métricas en la SERP. Es el único modo de ver datos de competidores con este plan.

### 3.2 No reportar "referring domains" sin filtrar dofollow

En cinco de los seis dominios el conteo está inflado por spam nofollow. **Nodarishub: 195 → 3 al filtrar.** Usarlo crudo como métrica de progreso es engañarse.

### 3.3 Auditar los otros dos sitios spameados

Propertyledger (208 dominios), CMLC (203), Arcade (380) y Tlaollin (397) muestran la misma firma. Verificar dofollow en cada uno antes de decidir si hay algo que desautorizar. La expectativa razonable, por el patrón de nodarishub, es que sea todo nofollow y no haya nada que hacer.

### 3.4 ~~Reautenticar el GSC de Raditech~~ - no hacia falta

Verificado 2026-08-29: el token funciona. La nota de memoria que decia `invalid_grant` era de julio, de cuando la app OAuth estaba en modo *Testing* y los refresh tokens morian a los 7 dias; eso se arreglo al publicar la app a produccion el 12-jul.

**Regla que sale de esto:** antes de regenerar credenciales, probarlas. `railway run python` con un POST `grant_type=refresh_token` + un `GET /webmasters/v3/sites` cuesta 30 segundos y evita un flujo OAuth innecesario.

### 3.5 Limpiar los pendientes rancios del vault

La bóveda Obsidian tiene ~30 pendientes abiertos de junio que **ya están resueltos** según la memoria del proyecto (redirects de Raditech, indexaciones, H1s). Están generando ruido. Vale una pasada de cierre.

Y dos que sí siguen vivos y contradicen el estado actual:
- *"Activar cross-links PTM ↔ PYS"* aparece 4 veces — **está invertido**: hoy la decisión es **desactivarlos**, y es la defensa legal del modelo de Telenzia.
- *"Reconciliar el modelo de monetización"* ($1,500 nuevo vs $500 viejo) sigue abierto.

---

# RESUMEN — qué haría primero

Si solo se pudieran hacer cinco cosas este mes, en este orden:

1. **CMLC: reclamar el Perfil de Negocio de Google.** Máximo retorno, mínimo esfuerzo, y hay riesgo de crear un duplicado si alguien lo intenta mal.
2. **Telenzia: crear `privacidad@telenzia.com` y corregir la copy de "tus péptidos en la puerta".** Es exposición legal, no SEO.
3. **Raditech: empujar la guia de expediente clinico** - 2,358 impresiones en posicion 8.4 con cero clics. El cluster de 33,170/mes ya esta entrando solo; falta convertirlo.
4. **PYS: arreglar las 42 meta descriptions duplicadas y crear la ficha de ipamorelina.** Higiene + la demanda medida más grande sin página.
5. **Nodaris: conseguir 2-3 casos de cliente por país.** Es el pendiente que lleva más tiempo parado y el único que desbloquea la localización.

Tres de los cinco **no son trabajo de SEO** — son decisiones y material que solo Antonio puede aportar. Eso, más que cualquier otra cosa, es lo que el retrofeed deja claro.
