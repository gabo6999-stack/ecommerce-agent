# Export de la sesión — para pasar a Hermes

Transcript textual de la sesión de SEO sobre **raditech.mx**, **PYS** y **nodarishub**
(30 de julio – 3 de agosto de 2026). Exportado del registro de Claude Code:
3,406 registros · 83 turnos de usuario · 386 respuestas.

## Qué archivo mandar

| archivo | contenido | ¿compartible? |
|---|---|---|
| **`conversacion-dialogo-REDACTADA.md`** | Solo lo que se dijo: turnos de usuario y respuestas. Sin ruido de herramientas. **0.33 MB** | ✅ **Este es el que conviene mandar** |
| `conversacion-completa-REDACTADA.md` | Todo: mensajes, razonamiento interno, cada llamada a herramienta y su resultado. 3.12 MB | ✅ Sí, si Hermes necesita el detalle de ejecución |
| `conversacion-dialogo.md` | Igual que la redactada, **pero con las credenciales en claro** | ⛔ No compartir |
| `conversacion-completa.md` | Igual que la redactada, **pero con las credenciales en claro** | ⛔ No compartir |

## Por qué hay versiones redactadas

El transcript original contiene **credenciales vivas** que se pegaron durante la
sesión. Se sustituyeron por etiquetas que dicen qué era cada cosa, para que el
texto siga entendiéndose:

| qué | cuántas veces aparecía |
|---|---:|
| Consumer key / secret de WooCommerce | 54 |
| Contraseñas de aplicación de WordPress | 18 |
| Contraseña FTP de PYS | 11 |
| Contraseña de cuenta | 8 |
| Variables de entorno con `PASSWORD` / `SECRET` / `TOKEN` | 6 |
| Clave de API de Anthropic | 1 |

Verificado tras redactar: **cero credenciales conocidas** en las versiones
`-REDACTADA`. El resto del texto queda idéntico al original.

## Si de todas formas quieres mandar el original

Las credenciales que aparecen ahí siguen siendo válidas. Antes de compartirlo
convendría rotar al menos la contraseña FTP de PYS y las dos contraseñas de
aplicación de WordPress (PropertyLedger y nodarishub), porque una contraseña de
aplicación se revoca y se vuelve a generar en un minuto desde
**wp-admin → Usuarios → Perfil**.

## Contexto que le ahorra tiempo a Hermes

Los tres resúmenes visuales de la sesión, uno por sitio, están publicados como
artefactos privados. Y el material de referencia vive en:

- `docs/playbook-maestro-raditech.md` — el plan completo de raditech, con las
  correcciones de método marcadas en el propio texto.
- `docs/playbook-fichas-pys.md` — la metodología por ficha y el retrofeed de 8 compuertas.
- `backups/raditech-2026-07-31/` — 43 archivos: respaldos previos a cada cambio,
  SERPs crudos, comparaciones 1 a 1 y el script del barrido.
- Bóveda Obsidian: `04 - Sesiones/2026-07-31 — Raditech playbook maestro` y la
  sección de diagnóstico transversal en `MOC SEO`.
