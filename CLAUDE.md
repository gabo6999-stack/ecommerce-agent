# Ecommerce Agent — peptidosysuplementos.mx

Agente con acceso a WooCommerce para consultar productos, órdenes, clientes e inventario.
Genera reportes PDF. Deploy en Railway.

## Stack
- Claude API (tool use) — `agent.py`
- WooCommerce REST API v3
- fpdf2 para reportes PDF
- `web.py` — interfaz web

## Variables de entorno
```
WC_STORE_URL=https://peptidosysuplementos.mx
WC_CONSUMER_KEY=ck_xxx
WC_CONSUMER_SECRET=cs_xxx
ANTHROPIC_API_KEY=sk-ant-xxx

# Acceso a web.py. Sin estas dos la aplicación se cierra (503) en vez de
# quedar abierta: expone ~40 POST que escriben en sitios en vivo.
PANEL_PASSWORD=...        # para entrar por el navegador en /login
API_TOKEN=...             # para las llamadas con cabecera X-API-Key
FLASK_SECRET_KEY=...      # fija, o cada despliegue cierra la sesión de todos
```

Comprobar la puerta: `python3 scripts/prueba_acceso.py`

## Herramientas disponibles
- `get_products` — buscar por nombre, categoría, popularidad
- `get_orders` — por estado (pending, processing, completed)
- `get_customers` — clientes
- Reportes PDF con fpdf2
