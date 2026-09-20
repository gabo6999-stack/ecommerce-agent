# Site Audits — nodarishub, propertyledger, arcademotors

Fecha: 2026-08-27 · Primer crawl de la historia en los tres proyectos.
Complementa [ahrefs-cuenta-gratis-2026-08-27.md](ahrefs-cuenta-gratis-2026-08-27.md).

## Resumen

| Sitio | Health | URLs | Con errores | Issues | Veredicto |
|---|---|---|---|---|---|
| nodarishub.com | **98%** | 120 | 4 | 22 | Sano. Deuda de enlaces internos por la consolidación 301 |
| arcademotorsmx.com | **98%** | 61 | 3 | 13 | Sano. Problema de arquitectura de enlaces internos |
| propertyledger.us | **73%** | 55 | 41 | 24 | El 73% es engañoso — ver abajo |

---

## 1. propertyledger.us — el health score es casi todo un falso positivo

**46 enlaces internos rotos apuntando a solo 4 páginas.** Desglose por nº de enlaces entrantes:

| URL rota | Inlinks | Enlazada desde | ¿Real? |
|---|---|---|---|
| `/cdn-cgi/l/email-protection` | **40** | `/` (home) | ❌ **FALSO POSITIVO** |
| `/hoa-condo-accounting/` | 3 | `/category/trust-accounting/` | ✅ Real |
| `/setting-up-a-property-management-chart-of-accounts-the-right-way/` | 2 | `/category/property-management-accounting/` | ✅ Real |
| `/bank-reconciliation-property-portfolios-explained/` | 1 | `/why-clean-reconciliations-matter-property-management/` | ✅ Real |

### El falso positivo (40 de los 46 enlaces)

`/cdn-cgi/l/email-protection` es el **ofuscador de correo de Cloudflare**. Cuando la opción *Email Obfuscation* está activa, Cloudflare sustituye los `mailto:` por un enlace a esa ruta que se resuelve por JavaScript. Los crawlers que no ejecutan ese JS lo ven como 404.

**No hay nada roto en el sitio.** Es el email del footer/contacto replicado en 40 páginas. Opciones:
- Dejarlo así (Google lo entiende; no es un problema de ranking), **o**
- Excluir `/cdn-cgi/` en Crawl settings del proyecto de Ahrefs para que el health score deje de mentir, **o**
- Apagar Email Obfuscation en Cloudflare (pierdes protección anti-scraping del correo).

> **Recomendado: excluir `/cdn-cgi/` del crawl.** Arregla la métrica sin tocar el sitio. Con eso el health debería subir de 73% a ~90%.

### Lo que sí hay que arreglar (6 enlaces, 3 páginas)

Dos de las tres 404 reales están enlazadas **desde páginas de categoría**, lo que encaja con el historial de artículos que cayeron en categorías equivocadas. O se crean esas páginas o se quitan los enlaces.

### Resto de hallazgos de propertyledger

- **1 página 5XX** — error de servidor, revisar
- 5 páginas 404 en total, 5 páginas 4XX
- **22 páginas indexables fuera del sitemap** (de 55 → el 40% del sitio)
- **35 páginas bloqueadas a algunos bots de búsqueda con IA** + política inconsistente de bots de entrenamiento IA en las mismas 35. Relevante si se quiere visibilidad en ChatGPT/Perplexity.
- 2 páginas con múltiples H1 · 3 sin meta description · 4 demasiado largas
- 2 errores de validación schema.org
- 1 página huérfana · 9 redirects 3XX · 2 páginas lentas
- 6 páginas con Open Graph incompleto

---

## 2. nodarishub.com — health 98%, pero arrastra deuda de la consolidación 301

Técnicamente el sitio está bien. El hallazgo importante es otro:

- **40 páginas indexables enlazan a redirecciones** (+51 no indexables) y hay **28 redirects 3XX** y 1 cadena de redirección.

Esto es el residuo de la consolidación 301 del blog: los 301 del mu-plugin funcionan, pero **los enlaces internos siguen apuntando a las URLs viejas**. Cada salto es autoridad que se diluye y crawl budget desperdiciado. Hay que reescribir los enlaces internos al destino final.

Otros:
- **47 páginas noindex** (revisar si todas deben serlo)
- **1 hreflang de auto-referencia faltante** ← relevante para el binacional EC/MX
- 36 páginas no indexables con un solo enlace interno dofollow
- 4 páginas indexables sin meta description
- 1 página 404 · 3 imágenes sin alt · 1 página indexable fuera del sitemap · 1 redirect 3XX dentro del sitemap

---

## 3. arcademotorsmx.com — health 98%, el problema es arquitectura de enlaces

Cero errores graves. Ni 404, ni 4XX, ni 5XX. Lo que sale es estructural:

- **26 páginas con un solo enlace interno dofollow entrante** (de 61 URLs → el 43% del sitio)
- **3 páginas huérfanas** sin ningún enlace interno entrante

Para un marketplace donde las categorías y los filtros son el motor de SEO, esto es exactamente el cuello de botella: los listados no se están enlazando entre sí.

Otros:
- **13 títulos demasiado largos** + 13 meta descriptions largas + 5 cortas
- 1 página cuyo título no coincide con el que muestra la SERP
- **13 páginas indexables fuera del sitemap** (de 61)
- 32 páginas con Open Graph incompleto
- 5 imágenes sin alt · 3 redirects 3XX · 1 cadena de redirección

---

## Prioridades

1. **propertyledger** — excluir `/cdn-cgi/` del crawl (5 min, arregla la métrica) y revisar la página 5XX
2. **propertyledger** — crear o desenlazar las 3 páginas 404 reales
3. **nodarishub** — reescribir los enlaces internos que apuntan a redirects (40 páginas)
4. **arcademotors** — enlazar las 3 huérfanas y densificar los enlaces entre listados/categorías
5. **Los tres** — meter al sitemap las indexables que faltan (22 + 13 + 1)
6. **arcademotors** — acortar los 13 títulos largos

## Notas de operación

- Cuota del plan gratis: **5,000 créditos de rastreo/mes**, **10,000 páginas internas máx. por proyecto**. Nodarishub consumió 91 páginas facturadas; los tres crawls juntos apenas rozan la cuota.
- Los crawls tardan ~20-25 min en el plan gratis (van throttled). La lista de Site Audit cachea las cifras; el dato en vivo está en `/site-audit/<id>/crawl-log`.
- Ya estaban los 7 proyectos con crawl semanal programado los viernes 12:00 GMT-6.
