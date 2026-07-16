# Contexto — Integración DataForSEO en los agentes de Nodarishub

> Handoff para continuar en otra PC. Fecha: 15 julio 2026.
> Destilado de la conversación, no es un volcado literal del chat.

---

## 1. El problema que se estaba resolviendo

Los agentes de blogs y SEO (Railway) consultaban Google directamente para sacar
keywords, y a veces se les pasaban datos de Ubersuggest. Problema: Ubersuggest
está diseñado para uso manual en dashboard (su capa gratuita limita a ~3
búsquedas de keywords al día, 1 análisis de dominio al día, ~3 meses de
histórico). No sirve como fuente de datos para agentes.

**Decisión: DataForSEO.**

## 2. Por qué DataForSEO y no otra

- **Pago por uso, sin suscripción.** Depósito mínimo $50, precio desde ~$0.0001
  por request. Registro gratis y sin tarjeta con **$1 de crédito real** (datos
  de verdad, no mock) para probar antes de pagar.
- A volúmenes equivalentes sale **70–90% más barato** que Ahrefs ($129/mes Lite)
  o Semrush ($139.95/mes Pro), que cobran por acceso, no por consumo.
- **Servidor MCP oficial** (`https://mcp.dataforseo.com/mcp`) si se quiere hacer
  research conversacional desde Claude Code además del cliente Python.
- Base propia de **4.8B+ keywords**, cobertura 170+ países.
- Es infraestructura, no producto: no hay dashboard. Para este stack eso es
  ventaja, no defecto.

Alternativa evaluada y descartada por ahora: **SE Ranking** (~$129/mes, dashboard
+ API + MCP, modelo de créditos). Mejor si algún día se quiere interfaz visual
para clientes de la agencia. Para uso puramente programático, DataForSEO gana.

## 3. El hallazgo clave: nacional vs local

Esto define qué API se usa para qué. **No son intercambiables.**

| Necesidad | API | Alcance geográfico |
|---|---|---|
| Keywords nacionales (PYS, Arcade, Nodaris EC) | **Labs API** | **Solo países.** Por diseño. |
| Volumen por ciudad (SEO local) | **Keywords Data API** | Hasta City / Municipality / State (~94,933 ubicaciones) |
| Rank tracking local, local pack, Maps | **SERP API** | Ciudad, coordenadas GPS, código postal |

- **Labs solo soporta países** y no es un bug: DataForSEO explica que mantener
  bases a nivel ciudad dispararía tamaño, tiempo de actualización y precio.
  Para PYS y Arcade Motors (que son nacionales) esto es justo lo que se necesita.
- **Trampa documentada:** si pasas `location_coordinate` a Keywords Data,
  recibes el volumen del **país** al que pertenecen esas coordenadas. Google Ads
  no permite volumen por coordenadas exactas. Para local, siempre `location_code`
  de la ciudad.
- Un solo depósito de $50 cubre las tres APIs. Solo cambia el endpoint.

## 4. Location codes

Patrón: `2000 + código ISO 3166-1 numérico`.

| País | ISO num | location_code |
|---|---|---|
| México | 484 | **2484** |
| Ecuador | 218 | **2218** |
| Estados Unidos | 840 | 2840 |

`language_code`: `"es"` para los tres mercados actuales.

Verificar la lista completa (endpoint gratuito, `cost: 0`):
```
GET https://api.dataforseo.com/v3/dataforseo_labs/locations_and_languages
```

## 5. Mercados configurados en el cliente

| slug | Proyecto | Dominio | location | Competidor |
|---|---|---|---|---|
| `pys` | Péptidos y Suplementos | peptidosysuplementos.mx | 2484 MX | exomapeptides.mx |
| `arcade` | Arcade Motors MX | arcademotorsmx.com | 2484 MX | *pendiente* |
| `nodaris_ec` | Nodarishub Ecuador | *(env `NODARIS_EC_DOMAIN`)* | 2218 EC | *pendiente* |

Prioridad actual: **PYS y Arcade Motors** son los que más se quieren impulsar.

## 6. Endpoints de Labs usados (todos son `/live`)

Labs no tiene método task_post/task_get — solo entrega en vivo.

```
POST /v3/dataforseo_labs/google/keyword_ideas/live          # misma categoría que las semillas
POST /v3/dataforseo_labs/google/keyword_suggestions/live    # long-tail que contiene la semilla (max 1000, default 100)
POST /v3/dataforseo_labs/google/related_keywords/live       # bloque "búsquedas relacionadas", hasta 4680 con depth
POST /v3/dataforseo_labs/google/keywords_for_site/live      # keywords relevantes a un dominio
POST /v3/dataforseo_labs/google/ranked_keywords/live        # donde el dominio YA rankea
POST /v3/dataforseo_labs/google/bulk_keyword_difficulty/live
POST /v3/dataforseo_labs/google/search_intent/live          # hasta 1,000 keywords
```

Notas de implementación que ya están resueltas en el cliente:

- **Filtros anidados vs planos.** `keyword_ideas`, `keyword_suggestions` y
  `keywords_for_site` filtran con `keyword_info.search_volume`. Pero
  `related_keywords` y `ranked_keywords` anidan todo bajo `keyword_data`, así
  que el filtro es `keyword_data.keyword_info.search_volume`. El método
  `_flatten()` normaliza ambos casos.
- **status_code 20000 = OK**, y hay que revisarlo en dos niveles: la respuesta
  raíz y cada task.
- El costo real viene en `response["cost"]`. El cliente lo acumula en
  `client.total_cost`.
- Límites: hasta 2,000 llamadas por minuto, máx 30 simultáneas, `limit` máx 1000.

## 7. Costos de referencia

- Related Keywords: $0.012 por task + $0.00012 por keyword → 100 keywords = **$0.024**
- Una llamada típica de keyword_ideas: ~**$0.011**
- Labs en general: desde ~$1.10 por 10,000 keywords
- SERP API: ~$0.60 por 1,000 SERPs (~$0.0006 por query standard; live ~$0.002)

Con el $1 gratis alcanza de sobra para probar los tres mercados.

## 8. Estado actual y próximos pasos

Hecho:
- [x] Módulo `dataforseo_client.py` escrito, con los 3 mercados registrados
- [x] Métodos: `blog_topics()`, `content_gap()` + los 7 endpoints de Labs

Siguiente (en este orden):
1. [ ] Registrarse en dataforseo.com — gratis, sin tarjeta, viene con $1
2. [ ] Copiar *API login* y *API password* de `app.dataforseo.com/api-access`
       (la API password NO es la contraseña de la cuenta; se genera ahí)
3. [ ] Probar en local, no en Railway:
       `export DATAFORSEO_USERNAME=... && export DATAFORSEO_PASSWORD=...`
       `python dataforseo_client.py pys`
4. [ ] Leer el costo que imprime al final y proyectarlo al ritmo real
       (PYS publica ~4 artículos/semana) antes de gastar
5. [ ] Si cuadra: recargar $50 y meter las env vars en Railway
6. [ ] Calibrar los filtros de `blog_topics()` con datos reales de México
       (min_volume=20, max_difficulty=35 son valores de arranque, no medidos)
7. [ ] Conectar la salida al Blog Agent (`agente-blogs-production.up.railway.app`)
       y al SEO Agent (repo `ecommerce-agent`)

Pendientes de información:
- [ ] **Dominio real de Nodarishub Ecuador** (ahora default `nodarishub.com` vía env var)
- [ ] Competidores reales de Arcade Motors MX
- [ ] Semillas reales para `arcade` y `nodaris_ec` (las del `__main__` son a ojo)

## 9. Idea de flujo completo (pendiente de armar)

Google Search Console API (gratis, ya en uso en PYS) detecta queries donde el
sitio aparece en posición 5–15 → DataForSEO valida volumen y dificultad y saca
el gap contra el competidor → el Blog Agent escribe el artículo. GSC da el dato
real de lo que ya pasa; DataForSEO da el dato de mercado. Se complementan.

## 10. Contexto del stack

- Agentes en Railway: Blog Agent, SEO Agent (repo `ecommerce-agent`), Social Video Agent
- PYS publica ~4 artículos/semana; el SEO Agent maneja títulos y descripciones
  de producto WooCommerce vía REST API
- Dominio PYS nuevo (~3 meses), DR bajo — de ahí que `max_difficulty=35` en
  `blog_topics()` sea deliberado
- Nodarishub sirve PyMEs en México y Ecuador; Rafael Mena es el socio en Ecuador
