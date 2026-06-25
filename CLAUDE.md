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
```

## Herramientas disponibles
- `get_products` — buscar por nombre, categoría, popularidad
- `get_orders` — por estado (pending, processing, completed)
- `get_customers` — clientes
- Reportes PDF con fpdf2
