from flask import Flask, request, jsonify, redirect, session
import anthropic, os, requests, schedule, threading, json, secrets
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", secrets.token_hex(32))
client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

# ─── Google Search Console config ────────────────────────────────────────────
GSC_CLIENT_ID     = os.environ.get("GOOGLE_CLIENT_ID", "")
GSC_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")
GSC_REFRESH_TOKEN = os.environ.get("GOOGLE_REFRESH_TOKEN", "")
GSC_SITE_URL      = os.environ.get("GSC_SITE_URL", "sc-domain:peptidosysuplementos.mx")
GSC_REDIRECT_URI  = os.environ.get("GSC_REDIRECT_URI", "https://web-production-3743c.up.railway.app/search-console/callback")
GSC_SCOPES        = ["https://www.googleapis.com/auth/webmasters.readonly"]

WC_URL = os.environ.get("WOOCOMMERCE_URL", "")
WC_KEY = os.environ.get("WOOCOMMERCE_KEY", "")
WC_SECRET = os.environ.get("WOOCOMMERCE_SECRET", "")
WP_USER = os.environ.get("WP_USER", "")
WP_PASSWORD = os.environ.get("WP_PASSWORD", "")

def get_products(per_page=10):
    try:
        r = requests.get(
            f"{WC_URL}/wp-json/wc/v3/products",
            auth=HTTPBasicAuth(WC_KEY, WC_SECRET),
            params={"per_page": per_page, "status": "publish", "_fields": "id,name,short_description,slug"},
            timeout=15
        )
        return [{"id": p.get("id"), "name": p.get("name"), "short_description": p.get("short_description","")[:150], "slug": p.get("slug")} for p in r.json()]
    except Exception as e:
        return {"error": str(e)}

def update_product(product_id, data):
    try:
        r = requests.put(
            f"{WC_URL}/wp-json/wc/v3/products/{product_id}",
            auth=HTTPBasicAuth(WC_KEY, WC_SECRET),
            json=data,
            timeout=15
        )
        result = r.json()
        if "id" in result:
            return {"success": True, "id": product_id, "name": result.get("name")}
        return {"error": str(result)}
    except Exception as e:
        return {"error": str(e)}

def get_categories(per_page=20):
    try:
        r = requests.get(
            f"{WC_URL}/wp-json/wc/v3/products/categories",
            auth=HTTPBasicAuth(WC_KEY, WC_SECRET),
            params={"per_page": per_page, "_fields": "id,name,description,slug,count"},
            timeout=15
        )
        return [{"id": c.get("id"), "name": c.get("name"), "description": c.get("description","")[:150], "slug": c.get("slug"), "count": c.get("count")} for c in r.json()]
    except Exception as e:
        return {"error": str(e)}

def update_category(category_id, data):
    try:
        r = requests.put(
            f"{WC_URL}/wp-json/wc/v3/products/categories/{category_id}",
            auth=HTTPBasicAuth(WC_KEY, WC_SECRET),
            json=data,
            timeout=15
        )
        result = r.json()
        if "id" in result:
            return {"success": True, "id": category_id, "name": result.get("name")}
        return {"error": str(result)}
    except Exception as e:
        return {"error": str(e)}

def create_post(title, content, slug="", meta_description="", status="publish"):
    try:
        url = f"{WC_URL}/wp-json/wp/v2/posts"
        auth = HTTPBasicAuth(WC_KEY, WC_SECRET)
        data = {
            "title": title,
            "content": content,
            "slug": slug,
            "status": status,
        }
        if meta_description:
            data["meta"] = {"_yoast_wpseo_metadesc": meta_description}
        r = requests.post(url, json=data, auth=auth, timeout=30)
        result = r.json()
        if "id" in result:
            return {"success": True, "id": result["id"], "link": result.get("link", ""), "status": result.get("status")}
        return {"error": str(result)}
    except Exception as e:
        return {"error": str(e)}

def get_posts(per_page=10):
    try:
        r = requests.get(
            f"{WC_URL}/wp-json/wp/v2/posts",
            auth=HTTPBasicAuth(WC_KEY, WC_SECRET),
            params={"per_page": per_page, "_fields": "id,title,slug,status,link,date"},
            timeout=15
        )
        return [{"id": p.get("id"), "title": p.get("title",{}).get("rendered",""), "slug": p.get("slug"), "status": p.get("status"), "link": p.get("link"), "date": p.get("date")} for p in r.json()]
    except Exception as e:
        return {"error": str(e)}


def get_post_content(post_id):
    try:
        auth = HTTPBasicAuth(WP_USER, WP_PASSWORD) if WP_USER else HTTPBasicAuth(WC_KEY, WC_SECRET)
        r = requests.get(
            f"{WC_URL}/wp-json/wp/v2/posts/{post_id}",
            auth=auth,
            timeout=15
        )
        p = r.json()
        if "id" not in p:
            return {"error": str(p)}
        return {
            "id": p["id"],
            "title": p.get("title", {}).get("rendered", ""),
            "slug": p.get("slug", ""),
            "link": p.get("link", ""),
            "content": p.get("content", {}).get("rendered", "")
        }
    except Exception as e:
        return {"error": str(e)}


def get_all_posts_catalog(per_page=100):
    try:
        auth = HTTPBasicAuth(WP_USER, WP_PASSWORD) if WP_USER else HTTPBasicAuth(WC_KEY, WC_SECRET)
        r = requests.get(
            f"{WC_URL}/wp-json/wp/v2/posts",
            auth=auth,
            params={"per_page": per_page, "_fields": "id,title,slug,link", "status": "publish"},
            timeout=15
        )
        posts = r.json()
        if not isinstance(posts, list):
            return {"error": str(posts)}
        return [
            {
                "id": p.get("id"),
                "title": p.get("title", {}).get("rendered", ""),
                "slug": p.get("slug", ""),
                "link": p.get("link", ""),
            }
            for p in posts
        ]
    except Exception as e:
        return {"error": str(e)}


def update_post(post_id, data):
    try:
        auth = HTTPBasicAuth(WC_KEY, WC_SECRET)
        r = requests.post(
            f"{WC_URL}/wp-json/wp/v2/posts/{post_id}",
            auth=auth,
            json=data,
            timeout=30
        )
        result = r.json()
        if "id" in result:
            return {"success": True, "id": post_id, "link": result.get("link", "")}
        return {"error": str(result)}
    except Exception as e:
        return {"error": str(e)}

SYSTEM = """Eres un agente SEO especializado para peptidosysuplementos.mx.

Puedes optimizar productos, categorias, y CREAR Y PUBLICAR ARTICULOS DE BLOG en WordPress.

REGLAS PARA TITULOS DE PRODUCTOS:
- Maximo 60 caracteres
- Palabra clave principal al inicio
- Sin caracteres especiales innecesarios

REGLAS PARA DESCRIPCIONES CORTAS:
- Entre 130-160 caracteres
- Texto plano sin markdown ni asteriscos
- Incluir palabra clave, beneficio y llamada a accion

REGLAS PARA ARTICULOS DE BLOG SEO:
- Minimo 1000 palabras
- Estructura con H2 y H3
- Incluir minimo 5 links externos a fuentes de autoridad (NEJM, FDA, PubMed, Mayo Clinic, etc.)
- Incluir minimo 8 links internos a productos de la tienda
- Meta descripcion entre 150-160 caracteres
- Slug en minusculas con guiones
- Keyword principal en titulo, primer parrafo, H2s y conclusion
- Contenido en HTML valido para WordPress (usar <h2>, <h3>, <p>, <strong>, <a href="">, <ul>, <li>)

FLUJO PARA ARTICULOS:
1. Genera el articulo completo en HTML
2. Muestra titulo, meta descripcion, slug y preview del contenido
3. Pide confirmacion antes de publicar
4. Usa create_post para publicar en WordPress
5. Confirma con el link del articulo publicado

REGLAS PARA INTERLINKS Y LINKS EXTERNOS:
- Links inter-blog (entre artículos del blog):
  • Usa get_all_posts_catalog() para ver todos los artículos publicados
  • Agrega 3-6 links a otros posts del blog que sean temáticamente relevantes
  • Formato: <a href="URL_DEL_POST">Título o texto descriptivo</a>
- Links a productos de la tienda:
  • Usa get_products() para obtener slugs
  • Agrega 4-8 links a productos relevantes al tema del artículo
  • Formato: <a href="URL_PRODUCTO">Nombre del producto</a>
- Links externos a fuentes de autoridad:
  • Sitios válidos: PubMed (pubmed.ncbi.nlm.nih.gov), examine.com, NIH (nih.gov), FDA (fda.gov), NEJM (nejm.org), Mayo Clinic, Healthline, WebMD
  • Agrega 3-5 links externos relevantes al tema
  • Formato: <a href="URL" target="_blank" rel="noopener noreferrer">Texto descriptivo</a>
- Insertar los links de forma NATURAL dentro del texto, no todos juntos al final
- Flujo para agregar/mejorar links en un blog existente:
  1. get_post_content(post_id) → leer el contenido HTML actual
  2. get_all_posts_catalog() → mapa completo de interlinks disponibles
  3. get_products(per_page=30) → productos para linkear
  4. Genera el HTML completo con los links integrados naturalmente
  5. Muestra resumen de links que agregarás y pide confirmación
  6. update_post(post_id, {content: HTML_optimizado}) → actualiza el post

GOOGLE SEARCH CONSOLE:
- gsc_top_queries: qué búsquedas traen tráfico real → optimiza títulos/meta para esas keywords exactas
- gsc_page_performance: qué páginas rinden mejor → aprende qué estructura y temas funcionan
- gsc_inspect_url: verificar si una URL está indexada antes de reportar problema o después de publicar
- gsc_request_indexing: después de publicar un blog nuevo, solicita indexación inmediata a Google
- Cuando el usuario pida "analiza el SEO" o "qué keywords tenemos", empieza con gsc_top_queries + gsc_page_performance

Siempre usa las herramientas para obtener datos reales antes de proponer cambios.
Pide confirmacion antes de aplicar cualquier cambio.
Responde siempre en espanol."""

TOOLS = [
    {
        "name": "get_products",
        "description": "Obtiene productos de WooCommerce",
        "input_schema": {
            "type": "object",
            "properties": {
                "per_page": {"type": "integer", "default": 10}
            }
        }
    },
    {
        "name": "update_product",
        "description": "Actualiza titulo y/o descripcion corta de un producto",
        "input_schema": {
            "type": "object",
            "required": ["product_id"],
            "properties": {
                "product_id": {"type": "integer"},
                "name": {"type": "string", "description": "Nuevo titulo (max 60 chars)"},
                "short_description": {"type": "string", "description": "Nueva descripcion corta (130-160 chars, texto plano)"}
            }
        }
    },
    {
        "name": "get_categories",
        "description": "Obtiene categorias de productos de WooCommerce",
        "input_schema": {
            "type": "object",
            "properties": {
                "per_page": {"type": "integer", "default": 20}
            }
        }
    },
    {
        "name": "update_category",
        "description": "Actualiza nombre y/o descripcion de una categoria",
        "input_schema": {
            "type": "object",
            "required": ["category_id"],
            "properties": {
                "category_id": {"type": "integer"},
                "name": {"type": "string", "description": "Nuevo nombre de la categoria"},
                "description": {"type": "string", "description": "Nueva descripcion (130-160 chars, texto plano)"}
            }
        }
    },
    {
        "name": "get_posts",
        "description": "Obtiene los posts de blog existentes en WordPress",
        "input_schema": {
            "type": "object",
            "properties": {
                "per_page": {"type": "integer", "default": 10}
            }
        }
    },
    {
        "name": "create_post",
        "description": "Crea y publica un articulo de blog en WordPress",
        "input_schema": {
            "type": "object",
            "required": ["title", "content"],
            "properties": {
                "title": {"type": "string", "description": "Titulo SEO del articulo (max 60 chars)"},
                "content": {"type": "string", "description": "Contenido completo en HTML valido para WordPress"},
                "slug": {"type": "string", "description": "URL amigable en minusculas con guiones"},
                "meta_description": {"type": "string", "description": "Meta descripcion 150-160 chars"},
                "status": {"type": "string", "description": "publish o draft", "default": "publish"}
            }
        }
    },
    {
        "name": "update_post",
        "description": "Actualiza el contenido, título o meta description de un post de blog existente en WordPress",
        "input_schema": {
            "type": "object",
            "required": ["post_id"],
            "properties": {
                "post_id": {"type": "integer", "description": "ID del post en WordPress"},
                "title": {"type": "string", "description": "Nuevo título (opcional)"},
                "content": {"type": "string", "description": "Nuevo contenido HTML completo (opcional)"},
                "meta_description": {"type": "string", "description": "Nueva meta description 150-160 chars (opcional)"}
            }
        }
    },
    {
        "name": "fetch_url",
        "description": "Obtiene el contenido de una URL: título, meta description, H1, H2s, cantidad de palabras y preview del texto. Úsala para revisar artículos publicados, verificar contenido de páginas o analizar la competencia.",
        "input_schema": {
            "type": "object",
            "required": ["url"],
            "properties": {
                "url": {"type": "string", "description": "URL completa a inspeccionar"}
            }
        }
    },
    {
        "name": "gsc_top_queries",
        "description": "Google Search Console: top búsquedas que traen tráfico real al sitio (clicks, impresiones, CTR, posición promedio). Úsala cuando el usuario pregunte por keywords, tráfico o qué busca la gente.",
        "input_schema": {
            "type": "object",
            "properties": {
                "days": {"type": "integer", "default": 28, "description": "Últimos N días"},
                "limit": {"type": "integer", "default": 10}
            }
        }
    },
    {
        "name": "gsc_page_performance",
        "description": "Google Search Console: qué páginas/URLs del sitio reciben más clicks desde Google.",
        "input_schema": {
            "type": "object",
            "properties": {
                "days": {"type": "integer", "default": 28},
                "limit": {"type": "integer", "default": 10}
            }
        }
    },
    {
        "name": "gsc_inspect_url",
        "description": "Google Search Console: verifica si una URL está indexada por Google y su estado de cobertura. Requiere GOOGLE_SERVICE_ACCOUNT_JSON en Railway.",
        "input_schema": {
            "type": "object",
            "required": ["url"],
            "properties": {
                "url": {"type": "string", "description": "URL completa a inspeccionar, ej: https://peptidosysuplementos.mx/bpc-157/"}
            }
        }
    },
    {
        "name": "gsc_request_indexing",
        "description": "Solicita a Google que indexe inmediatamente una URL nueva o actualizada. Úsala después de publicar un blog nuevo. Requiere GOOGLE_SERVICE_ACCOUNT_JSON con permisos Owner en GSC.",
        "input_schema": {
            "type": "object",
            "required": ["url"],
            "properties": {
                "url": {"type": "string", "description": "URL completa a indexar"}
            }
        }
    },
    {
        "name": "get_post_content",
        "description": "Obtiene el contenido HTML completo de un post de blog específico. Úsala SIEMPRE antes de editar un post para leer su contenido actual y no perder texto existente.",
        "input_schema": {
            "type": "object",
            "required": ["post_id"],
            "properties": {
                "post_id": {"type": "integer", "description": "ID del post en WordPress"}
            }
        }
    },
    {
        "name": "get_all_posts_catalog",
        "description": "Obtiene TODOS los artículos del blog publicados con sus URLs completas. Úsala para construir el mapa de interlinks: así sabes qué otros artículos existen y puedes linkear entre ellos de forma relevante.",
        "input_schema": {
            "type": "object",
            "properties": {
                "per_page": {"type": "integer", "default": 100, "description": "Máximo de posts a obtener (hasta 100)"}
            }
        }
    }
]

def run_tool(name, inputs):
    if name == "get_products":
        return get_products(inputs.get("per_page", 10))
    elif name == "update_product":
        data = {k: inputs[k] for k in ["name", "short_description"] if k in inputs}
        return update_product(inputs["product_id"], data)
    elif name == "get_categories":
        return get_categories(inputs.get("per_page", 20))
    elif name == "update_category":
        data = {k: inputs[k] for k in ["name", "description"] if k in inputs}
        return update_category(inputs["category_id"], data)
    elif name == "get_posts":
        return get_posts(inputs.get("per_page", 10))
    elif name == "create_post":
        return create_post(
            title=inputs["title"],
            content=inputs["content"],
            slug=inputs.get("slug", ""),
            meta_description=inputs.get("meta_description", ""),
            status=inputs.get("status", "publish")
        )
    elif name == "update_post":
        data = {k: inputs[k] for k in ["title", "content"] if k in inputs}
        if "meta_description" in inputs:
            data["meta"] = {"_yoast_wpseo_metadesc": inputs["meta_description"]}
        return update_post(inputs["post_id"], data)
    elif name == "fetch_url":
        return fetch_url(inputs["url"])
    elif name == "gsc_top_queries":
        return gsc_top_queries(inputs.get("days", 28), inputs.get("limit", 10))
    elif name == "gsc_page_performance":
        return gsc_page_performance(inputs.get("days", 28), inputs.get("limit", 10))
    elif name == "gsc_inspect_url":
        return gsc_inspect_url(inputs["url"])
    elif name == "gsc_request_indexing":
        return gsc_request_indexing(inputs["url"])
    elif name == "get_post_content":
        return get_post_content(inputs["post_id"])
    elif name == "get_all_posts_catalog":
        return get_all_posts_catalog(inputs.get("per_page", 100))
    return {"error": "herramienta desconocida"}

@app.route("/")
def index():
    return open("templates/index.html").read()

@app.route("/chat", methods=["POST"])
def chat():
    try:
        messages = request.json.get("messages", [])
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=8192,
            system=SYSTEM,
            tools=TOOLS,
            messages=messages
        )
        while response.stop_reason == "tool_use":
            ac = []
            for b in response.content:
                if b.type == "tool_use":
                    ac.append({"type": "tool_use", "id": b.id, "name": b.name, "input": b.input})
                elif hasattr(b, "text"):
                    ac.append({"type": "text", "text": b.text})
            tr = []
            for b in response.content:
                if b.type == "tool_use":
                    tr.append({"type": "tool_result", "tool_use_id": b.id, "content": str(run_tool(b.name, b.input))})
            messages = messages + [
                {"role": "assistant", "content": ac},
                {"role": "user", "content": tr}
            ]
            response = client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=8192,
                system=SYSTEM,
                tools=TOOLS,
                messages=messages
            )
        reply = "".join(b.text for b in response.content if hasattr(b, "text"))
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"reply": f"Error: {str(e)}"}), 500

REPORT_FILE = "last_report.json"
_last_report = {}


def get_all_products():
    try:
        r = requests.get(
            f"{WC_URL}/wp-json/wc/v3/products",
            auth=HTTPBasicAuth(WC_KEY, WC_SECRET),
            params={"per_page": 100, "status": "publish", "_fields": "id,name,short_description,slug"},
            timeout=30
        )
        return r.json() if isinstance(r.json(), list) else []
    except Exception:
        return []


def generate_seo_report():
    products = get_all_products()
    optimized, pending = [], []

    for p in products:
        name = p.get("name", "")
        desc = p.get("short_description", "")
        issues = []

        if len(name) > 60:
            issues.append(f"título muy largo ({len(name)} chars, máx 60)")
        if not (130 <= len(desc) <= 160):
            if len(desc) == 0:
                issues.append("sin descripción corta")
            elif len(desc) < 130:
                issues.append(f"descripción muy corta ({len(desc)} chars, mín 130)")
            else:
                issues.append(f"descripción muy larga ({len(desc)} chars, máx 160)")

        entry = {"id": p.get("id"), "name": name, "slug": p.get("slug", "")}
        if issues:
            entry["issues"] = issues
            pending.append(entry)
        else:
            optimized.append(entry)

    report = {
        "generated_at": datetime.now().isoformat(),
        "total": len(products),
        "optimized": len(optimized),
        "pending": len(pending),
        "pct_optimized": round(len(optimized) / len(products) * 100) if products else 0,
        "pending_products": pending,
    }

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    global _last_report
    _last_report = report
    print(f"[Reporte] ✅ {report['optimized']}/{report['total']} optimizados ({report['pct_optimized']}%)")
    return report


def load_last_report():
    global _last_report
    if _last_report:
        return _last_report
    if os.path.exists(REPORT_FILE):
        with open(REPORT_FILE, "r", encoding="utf-8") as f:
            _last_report = json.load(f)
    return _last_report


@app.route("/report")
def report_json():
    return jsonify(load_last_report() or {"message": "Sin reporte aún. Visita /report/generate para generar uno."})


@app.route("/report/generate")
def report_generate():
    report = generate_seo_report()
    return jsonify(report)


@app.route("/reporte")
def report_html():
    report = load_last_report()
    if not report:
        report = generate_seo_report()

    generated = report.get("generated_at", "")[:16].replace("T", " ")
    pct = report.get("pct_optimized", 0)
    bar_color = "#22c55e" if pct >= 80 else "#f59e0b" if pct >= 50 else "#ef4444"

    pending_rows = ""
    for p in report.get("pending_products", []):
        issues_html = "".join(f'<li>{i}</li>' for i in p.get("issues", []))
        pending_rows += f"""
        <tr>
            <td style="padding:10px;border-bottom:1px solid #2a2a2a;">
                <strong>{p['name']}</strong><br>
                <span style="font-size:12px;color:#888;">/producto/{p['slug']}</span>
            </td>
            <td style="padding:10px;border-bottom:1px solid #2a2a2a;">
                <ul style="margin:0;padding-left:16px;color:#f59e0b;font-size:13px;">{issues_html}</ul>
            </td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Reporte SEO — peptidosysuplementos.mx</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; background: #0f0f0f; color: #eee; }}
        h1 {{ color: #7c3aed; }} h2 {{ color: #aaa; font-size: 16px; font-weight: normal; }}
        .cards {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin: 24px 0; }}
        .card {{ background: #1a1a1a; border-radius: 10px; padding: 20px; text-align: center; }}
        .num {{ font-size: 36px; font-weight: bold; }}
        .label {{ font-size: 12px; color: #888; margin-top: 4px; }}
        .bar-bg {{ background: #2a2a2a; border-radius: 99px; height: 12px; margin: 24px 0; }}
        .bar {{ background: {bar_color}; height: 12px; border-radius: 99px; width: {pct}%; }}
        table {{ width: 100%; border-collapse: collapse; background: #1a1a1a; border-radius: 10px; overflow: hidden; }}
        th {{ background: #2a2a2a; padding: 12px 10px; text-align: left; font-size: 13px; color: #aaa; }}
        a {{ color: #818cf8; }} .btn {{ display:inline-block; background:#7c3aed; color:white; padding:10px 20px; border-radius:8px; text-decoration:none; margin-top:16px; }}
    </style>
</head>
<body>
    <h1>📊 Reporte SEO</h1>
    <h2>peptidosysuplementos.mx — Generado: {generated}</h2>

    <div class="cards">
        <div class="card"><div class="num">{report.get('total', 0)}</div><div class="label">Total productos</div></div>
        <div class="card"><div class="num" style="color:#22c55e">{report.get('optimized', 0)}</div><div class="label">Optimizados</div></div>
        <div class="card"><div class="num" style="color:#ef4444">{report.get('pending', 0)}</div><div class="label">Pendientes</div></div>
        <div class="card"><div class="num" style="color:{bar_color}">{pct}%</div><div class="label">% completado</div></div>
    </div>

    <div class="bar-bg"><div class="bar"></div></div>

    <h2 style="margin-top:32px;">⚠️ Productos pendientes de optimizar</h2>
    {'<p style="color:#666;">¡Todos los productos están optimizados! 🎉</p>' if not report.get('pending_products') else f'''
    <table>
        <thead><tr><th>Producto</th><th>Problemas</th></tr></thead>
        <tbody>{pending_rows}</tbody>
    </table>'''}

    <br>
    <a href="/report/generate" class="btn">🔄 Actualizar reporte</a>
    &nbsp;
    <a href="/" class="btn" style="background:#1a1a1a;border:1px solid #444;">← Volver al agente</a>
</body>
</html>"""
    return html


def run_weekly_report():
    schedule.every().monday.at("09:00").do(generate_seo_report)
    while True:
        schedule.run_pending()
        threading.Event().wait(60)


# ─── BATCH OPTIMIZATION ───────────────────────────────────────────────────────

_batch_status = {"running": False, "total": 0, "done": 0, "errors": 0, "results": [], "started_at": None, "finished_at": None}


def get_products_by_category(category_id=None):
    params = {"per_page": 100, "status": "publish", "_fields": "id,name,short_description,slug,categories"}
    if category_id and category_id != "all":
        params["category"] = category_id
    try:
        r = requests.get(f"{WC_URL}/wp-json/wc/v3/products", auth=HTTPBasicAuth(WC_KEY, WC_SECRET), params=params, timeout=30)
        return r.json() if isinstance(r.json(), list) else []
    except Exception as e:
        return []


def needs_optimization(p):
    name = p.get("name", "")
    desc = p.get("short_description", "")
    return len(name) > 60 or not (130 <= len(desc) <= 160)


def claude_optimize_batch(products):
    product_list = json.dumps(
        [{"id": p["id"], "name": p["name"], "short_description": p.get("short_description", "")} for p in products],
        ensure_ascii=False, indent=2
    )
    prompt = f"""Eres experto SEO para peptidosysuplementos.mx (tienda de péptidos y suplementos en México).

Optimiza los siguientes productos según estas reglas:
- Título (name): máximo 60 caracteres, palabra clave principal al inicio, sin caracteres especiales
- Descripción corta (short_description): entre 130 y 160 caracteres, texto plano sin HTML ni markdown, incluir keyword + beneficio + llamada a la acción

Productos a optimizar:
{product_list}

Devuelve ÚNICAMENTE un JSON válido con este formato exacto, sin explicaciones ni markdown:
[{{"id": 123, "name": "Título optimizado", "short_description": "Descripción optimizada"}}, ...]"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )
    text = response.content[0].text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    return json.loads(text)


def run_batch_optimize(category_id=None):
    global _batch_status
    _batch_status = {"running": True, "total": 0, "done": 0, "errors": 0, "results": [], "started_at": datetime.now().isoformat(), "finished_at": None}

    try:
        products = get_products_by_category(category_id)
        pending = [p for p in products if needs_optimization(p)]
        _batch_status["total"] = len(pending)

        if not pending:
            _batch_status["running"] = False
            _batch_status["finished_at"] = datetime.now().isoformat()
            print("[Batch] No hay productos pendientes de optimizar.")
            return

        print(f"[Batch] Optimizando {len(pending)} productos con Claude...")

        # Procesar en grupos de 20 para no exceder el contexto
        chunk_size = 20
        for i in range(0, len(pending), chunk_size):
            chunk = pending[i:i + chunk_size]
            try:
                optimized = claude_optimize_batch(chunk)
                for item in optimized:
                    pid = item.get("id")
                    data = {k: item[k] for k in ("name", "short_description") if k in item}
                    result = update_product(pid, data)
                    if result.get("success"):
                        _batch_status["done"] += 1
                        _batch_status["results"].append({"id": pid, "name": item.get("name"), "status": "ok"})
                        print(f"[Batch] ✅ {pid} — {item.get('name')}")
                    else:
                        _batch_status["errors"] += 1
                        _batch_status["results"].append({"id": pid, "status": "error", "error": result.get("error")})
            except Exception as e:
                _batch_status["errors"] += len(chunk)
                print(f"[Batch] ❌ Error en chunk: {e}")

    except Exception as e:
        print(f"[Batch] ❌ Error general: {e}")
    finally:
        _batch_status["running"] = False
        _batch_status["finished_at"] = datetime.now().isoformat()
        generate_seo_report()
        print(f"[Batch] Finalizado — {_batch_status['done']} ok, {_batch_status['errors']} errores")


@app.route("/batch-optimize", methods=["POST"])
def batch_optimize():
    if _batch_status["running"]:
        return jsonify({"error": "Ya hay una optimización en proceso"}), 409
    data = request.json or {}
    category_id = data.get("category_id", "all")
    thread = threading.Thread(target=run_batch_optimize, args=(category_id,), daemon=True)
    thread.start()
    return jsonify({"status": "started", "category_id": category_id})


@app.route("/batch-status")
def batch_status():
    return jsonify(_batch_status)


@app.route("/categories")
def categories_endpoint():
    return jsonify(get_categories(per_page=50))


@app.route("/add-links", methods=["POST"])
def add_links():
    """Optimiza un post existente agregando interlinks, links a productos y links externos.
    Solo requiere post_id — el contenido se obtiene automáticamente desde WordPress."""
    try:
        data = request.json or {}
        post_id = data.get("post_id")
        if not post_id:
            return jsonify({"error": "post_id es requerido"}), 400

        post = get_post_content(post_id)
        if "error" in post:
            return jsonify({"error": f"No se pudo obtener el post: {post['error']}"}), 500

        title = post.get("title", "")
        content = post.get("content", "")
        url = post.get("link", "")

        if not content:
            return jsonify({"error": "El post no tiene contenido"}), 400

        products = get_products(per_page=30)
        products_list = "\n".join(
            f"- {p['name']} ({WC_URL}/producto/{p['slug']})"
            for p in products if isinstance(p, dict) and "name" in p
        )

        all_posts = get_all_posts_catalog(per_page=100)
        other_posts = [
            p for p in all_posts
            if isinstance(p, dict) and str(p.get("id", "")) != str(post_id)
        ]
        posts_list = "\n".join(
            f"- {p['title']} ({p['link']})"
            for p in other_posts if isinstance(p, dict) and p.get("title")
        )

        prompt = f"""Eres un experto SEO. Tienes este artículo de blog en peptidosysuplementos.mx:

TÍTULO: {title}
URL: {url}
POST ID: {post_id}

CONTENIDO ACTUAL (HTML):
{content[:5000]}

OTROS ARTÍCULOS DEL BLOG (para interlinks entre posts):
{posts_list[:2000] if posts_list else "No hay otros artículos disponibles aún."}

PRODUCTOS DE LA TIENDA (para links internos a productos):
{products_list[:2000]}

Tu tarea — agrega los siguientes links de forma NATURAL dentro del texto existente:
1. INTERLINKS (3-6 links): enlaza a otros artículos del blog que sean temáticamente relevantes.
   Formato: <a href="URL_DEL_POST">texto descriptivo</a>
2. LINKS A PRODUCTOS (4-8 links): enlaza a productos relevantes de la tienda.
   Formato: <a href="URL_PRODUCTO">nombre del producto</a>
3. LINKS EXTERNOS (3-5 links): enlaza a fuentes científicas de autoridad relevantes al tema
   (PubMed, examine.com, NIH, FDA, NEJM, Mayo Clinic). Solo URLs reales y verificables.
   Formato: <a href="URL" target="_blank" rel="noopener noreferrer">texto descriptivo</a>
4. NO inventes productos ni posts que no estén en las listas anteriores.
5. Devuelve ÚNICAMENTE el HTML optimizado completo, sin explicaciones ni markdown extra.

Devuelve solo el HTML listo para WordPress."""

        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=8192,
            messages=[{"role": "user", "content": prompt}]
        )

        optimized_content = response.content[0].text.strip()
        if optimized_content.startswith("```"):
            optimized_content = optimized_content.split("\n", 1)[1].rsplit("```", 1)[0].strip()

        result = update_post(post_id, {"content": optimized_content})

        if result.get("success"):
            return jsonify({
                "success": True,
                "post_id": post_id,
                "title": title,
                "url": result.get("link", url),
                "other_posts_available": len(other_posts),
                "products_available": len(products),
            })
        return jsonify({"error": result.get("error", "Error al actualizar post")}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/optimize-blog", methods=["POST"])
def optimize_blog():
    try:
        data = request.json or {}
        post_id = data.get("post_id")
        title = data.get("title", "")
        content = data.get("content", "")
        url = data.get("url", "")

        if not post_id or not content:
            return jsonify({"error": "post_id y content son requeridos"}), 400

        products = get_products(per_page=30)
        products_list = "\n".join(
            f"- {p['name']} ({WC_URL}/producto/{p['slug']})"
            for p in products if isinstance(p, dict) and "name" in p
        )

        all_posts = get_all_posts_catalog(per_page=100)
        other_posts = [
            p for p in all_posts
            if isinstance(p, dict) and str(p.get("id", "")) != str(post_id)
        ]
        posts_list = "\n".join(
            f"- {p['title']} ({p['link']})"
            for p in other_posts if isinstance(p, dict) and p.get("title")
        )

        prompt = f"""Eres un experto SEO. Tienes este artículo de blog en peptidosysuplementos.mx:

TÍTULO: {title}
URL: {url}
POST ID: {post_id}

CONTENIDO ACTUAL (HTML):
{content[:5000]}

OTROS ARTÍCULOS DEL BLOG (para interlinks):
{posts_list[:2000] if posts_list else "No hay otros artículos disponibles aún."}

PRODUCTOS DE LA TIENDA (para links internos a productos):
{products_list[:2000]}

Tu tarea — agrega los siguientes links de forma NATURAL dentro del texto existente:
1. INTERLINKS (3-6 links): enlaza a otros artículos del blog que sean temáticamente relevantes.
   Formato: <a href="URL_DEL_POST">texto descriptivo</a>
2. LINKS A PRODUCTOS (4-8 links): enlaza a productos relevantes de la tienda.
   Formato: <a href="URL_PRODUCTO">nombre del producto</a>
3. LINKS EXTERNOS (3-5 links): enlaza a fuentes científicas de autoridad relevantes al tema
   (PubMed, examine.com, NIH, FDA, NEJM, Mayo Clinic). Solo URLs reales y verificables.
   Formato: <a href="URL" target="_blank" rel="noopener noreferrer">texto descriptivo</a>
4. Asegúrate de que el contenido tenga al menos un H2 y una conclusión con llamada a la acción.
5. NO inventes productos ni posts que no estén en las listas anteriores.
6. Devuelve ÚNICAMENTE el HTML optimizado completo, sin explicaciones ni markdown extra.

Devuelve solo el HTML listo para WordPress."""

        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=8192,
            messages=[{"role": "user", "content": prompt}]
        )

        optimized_content = response.content[0].text.strip()
        if optimized_content.startswith("```"):
            optimized_content = optimized_content.split("\n", 1)[1].rsplit("```", 1)[0].strip()

        result = update_post(post_id, {"content": optimized_content})

        if result.get("success"):
            return jsonify({
                "success": True,
                "post_id": post_id,
                "url": result.get("link", url),
                "interlinks_added": len(other_posts) > 0,
                "products_linked": len(products) > 0,
            })
        return jsonify({"error": result.get("error", "Error al actualizar post")}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─── FETCH URL ───────────────────────────────────────────────────────────────

def fetch_url(url: str) -> dict:
    try:
        from bs4 import BeautifulSoup
        r = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        title = soup.title.string.strip() if soup.title else ""
        meta_desc = ""
        meta_tag = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", attrs={"property": "og:description"})
        if meta_tag:
            meta_desc = meta_tag.get("content", "").strip()

        h1s = [h.get_text(strip=True) for h in soup.find_all("h1")]
        h2s = [h.get_text(strip=True) for h in soup.find_all("h2")]

        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        text = soup.get_text(separator=" ", strip=True)
        word_count = len(text.split())
        preview = text[:500]

        return {
            "url": url,
            "title": title,
            "meta_description": meta_desc,
            "h1": h1s,
            "h2s": h2s[:8],
            "word_count": word_count,
            "content_preview": preview,
            "status_code": r.status_code,
        }
    except Exception as e:
        return {"error": str(e), "url": url}


# ─── GSC TOOLS PARA CLAUDE ───────────────────────────────────────────────────

def _gsc_sa_creds():
    """Service account credentials para URL Inspection e Indexing API."""
    sa_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON", "")
    if not sa_json:
        raise ValueError("GOOGLE_SERVICE_ACCOUNT_JSON no configurado en Railway")
    return service_account.Credentials.from_service_account_info(
        json.loads(sa_json),
        scopes=[
            "https://www.googleapis.com/auth/webmasters",
            "https://www.googleapis.com/auth/indexing"
        ]
    )

def gsc_top_queries(days=28, limit=10):
    """Top búsquedas por clicks — usa OAuth existente."""
    if not GSC_REFRESH_TOKEN:
        return {"error": "GSC no autenticado. Visita /search-console/auth"}
    try:
        rows = fetch_gsc_data("query", days)
        return [
            {
                "query": r["keys"][0],
                "clicks": r.get("clicks", 0),
                "impressions": r.get("impressions", 0),
                "ctr_pct": round(r.get("ctr", 0) * 100, 1),
                "position": round(r.get("position", 0), 1)
            }
            for r in rows[:limit]
        ]
    except Exception as e:
        return {"error": str(e)}

def gsc_page_performance(days=28, limit=10):
    """Rendimiento por página — usa OAuth existente."""
    if not GSC_REFRESH_TOKEN:
        return {"error": "GSC no autenticado. Visita /search-console/auth"}
    try:
        rows = fetch_gsc_data("page", days)
        return [
            {
                "page": r["keys"][0].replace("https://peptidosysuplementos.mx", ""),
                "clicks": r.get("clicks", 0),
                "impressions": r.get("impressions", 0),
                "ctr_pct": round(r.get("ctr", 0) * 100, 1),
                "position": round(r.get("position", 0), 1)
            }
            for r in rows[:limit]
        ]
    except Exception as e:
        return {"error": str(e)}

def gsc_inspect_url(url):
    """Verifica estado de indexación de una URL — usa Service Account."""
    try:
        authed = AuthorizedSession(_gsc_sa_creds())
        resp = authed.post(
            "https://searchconsole.googleapis.com/v1/urlInspectionResult:inspect",
            json={"inspectionUrl": url, "siteUrl": GSC_SITE_URL}
        )
        resp.raise_for_status()
        idx = resp.json().get("inspectionResult", {}).get("indexStatusResult", {})
        return {
            "url": url,
            "verdict": idx.get("verdict", "UNKNOWN"),
            "coverage_state": idx.get("coverageState", ""),
            "indexing_state": idx.get("indexingState", ""),
            "last_crawl": idx.get("lastCrawlTime", "no disponible"),
            "google_canonical": idx.get("googleCanonical", ""),
        }
    except Exception as e:
        return {"error": str(e)}

def gsc_request_indexing(url):
    """Solicita indexación inmediata de una URL — usa Service Account (requiere Owner en GSC)."""
    try:
        authed = AuthorizedSession(_gsc_sa_creds())
        resp = authed.post(
            "https://indexing.googleapis.com/v3/urlNotifications:publish",
            json={"url": url, "type": "URL_UPDATED"}
        )
        resp.raise_for_status()
        notify_time = resp.json().get("urlNotificationMetadata", {}).get("latestUpdate", {}).get("notifyTime", "")
        return {"success": True, "url": url, "notify_time": notify_time}
    except Exception as e:
        return {"error": str(e)}


# ─── GOOGLE SEARCH CONSOLE ───────────────────────────────────────────────────

def get_gsc_service():
    creds = Credentials(
        token=None,
        refresh_token=GSC_REFRESH_TOKEN,
        client_id=GSC_CLIENT_ID,
        client_secret=GSC_CLIENT_SECRET,
        token_uri="https://oauth2.googleapis.com/token",
        scopes=GSC_SCOPES
    )
    return build("searchconsole", "v1", credentials=creds, cache_discovery=False)


def fetch_gsc_data(dimension, days=28):
    service = get_gsc_service()
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    result = service.searchanalytics().query(
        siteUrl=GSC_SITE_URL,
        body={
            "startDate": start_date,
            "endDate": end_date,
            "dimensions": [dimension],
            "rowLimit": 10,
            "orderBy": [{"fieldName": "clicks", "sortOrder": "DESCENDING"}]
        }
    ).execute()
    return result.get("rows", [])


@app.route("/search-console/auth")
def gsc_auth():
    if not GSC_CLIENT_ID or not GSC_CLIENT_SECRET:
        return "Faltan variables GOOGLE_CLIENT_ID y GOOGLE_CLIENT_SECRET en Railway.", 400
    import urllib.parse
    params = {
        "client_id": GSC_CLIENT_ID,
        "redirect_uri": GSC_REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(GSC_SCOPES),
        "access_type": "offline",
        "prompt": "consent"
    }
    auth_url = "https://accounts.google.com/o/oauth2/auth?" + urllib.parse.urlencode(params)
    return redirect(auth_url)


@app.route("/search-console/callback")
def gsc_callback():
    try:
        code = request.args.get("code")
        if not code:
            return "<pre style='color:red;padding:20px'>Error: no se recibió código de autorización</pre>", 400
        token_resp = requests.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": GSC_CLIENT_ID,
                "client_secret": GSC_CLIENT_SECRET,
                "redirect_uri": GSC_REDIRECT_URI,
                "grant_type": "authorization_code"
            }
        )
        token_data = token_resp.json()
        refresh_token = token_data.get("refresh_token", "")
        if not refresh_token:
            return f"<pre style='color:red;padding:20px'>Error al obtener token: {token_data}</pre>", 400
    except Exception as e:
        return f"<pre style='color:red;padding:20px'>Error en callback: {e}</pre>", 500
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Search Console conectado</title>
<style>body{{font-family:Arial;max-width:600px;margin:60px auto;padding:20px;background:#0f0f0f;color:#eee}}
.box{{background:#1a1a1a;border-radius:10px;padding:24px;border-left:4px solid #22c55e}}
code{{background:#2a2a2a;padding:4px 10px;border-radius:6px;font-size:13px;word-break:break-all}}
.btn{{display:inline-block;background:#7c3aed;color:white;padding:10px 20px;border-radius:8px;text-decoration:none;margin-top:16px}}</style>
</head><body>
<h2>✅ Google Search Console conectado</h2>
<div class="box">
<p>Copia este <strong>Refresh Token</strong> y agrégalo en Railway como variable de entorno:</p>
<p><strong>Variable:</strong> <code>GOOGLE_REFRESH_TOKEN</code></p>
<p><strong>Valor:</strong><br><code>{refresh_token}</code></p>
</div>
<p style="color:#aaa;font-size:13px;margin-top:16px;">Una vez que agregues la variable en Railway y el servicio se reinicie, el Search Console estará activo.</p>
<a href="/search-console" class="btn">Ver Search Console</a>
</body></html>"""


@app.route("/search-console/data")
def gsc_data():
    if not GSC_REFRESH_TOKEN:
        return jsonify({"error": "No autenticado. Visita /search-console/auth"}), 401
    try:
        queries = fetch_gsc_data("query")
        pages   = fetch_gsc_data("page")
        return jsonify({"queries": queries, "pages": pages})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/search-console")
def gsc_dashboard():
    if not GSC_CLIENT_ID:
        return """<html><body style="font-family:Arial;max-width:600px;margin:60px auto;background:#0f0f0f;color:#eee;padding:20px">
        <h2>⚙️ Search Console no configurado</h2>
        <p>Agrega estas variables en Railway primero:</p>
        <ul><li>GOOGLE_CLIENT_ID</li><li>GOOGLE_CLIENT_SECRET</li><li>GSC_SITE_URL</li></ul>
        </body></html>"""

    if not GSC_REFRESH_TOKEN:
        return redirect("/search-console/auth")

    try:
        queries = fetch_gsc_data("query")
        pages   = fetch_gsc_data("page")
        error_html = ""
    except Exception as e:
        queries, pages = [], []
        import html as _html
        error_html = f'<div style="background:#1a1a1a;border-left:4px solid #ef4444;padding:16px;border-radius:8px;margin:16px 0"><p style="color:#ef4444">Error: {_html.escape(str(e))}</p></div>'

    def rows_html(rows, dimension):
        if not rows:
            return '<tr><td colspan="5" style="padding:12px;color:#666;">Sin datos</td></tr>'
        html = ""
        for r in rows:
            keys = r.get("keys", [""])
            val = keys[0]
            if dimension == "page":
                val = val.replace("https://peptidosysuplementos.mx", "")
            clicks = r.get("clicks", 0)
            impr   = r.get("impressions", 0)
            ctr    = f"{r.get('ctr', 0)*100:.1f}%"
            pos    = f"{r.get('position', 0):.1f}"
            pos_color = "#22c55e" if float(r.get('position',99)) <= 10 else "#f59e0b" if float(r.get('position',99)) <= 20 else "#ef4444"
            html += f"<tr><td style='padding:10px;border-bottom:1px solid #2a2a2a;font-size:13px'>{val}</td><td style='padding:10px;border-bottom:1px solid #2a2a2a;text-align:center'>{clicks}</td><td style='padding:10px;border-bottom:1px solid #2a2a2a;text-align:center'>{impr}</td><td style='padding:10px;border-bottom:1px solid #2a2a2a;text-align:center'>{ctr}</td><td style='padding:10px;border-bottom:1px solid #2a2a2a;text-align:center;color:{pos_color};font-weight:bold'>{pos}</td></tr>"
        return html

    table_style = "width:100%;border-collapse:collapse;background:#1a1a1a;border-radius:10px;overflow:hidden;font-size:14px"
    th_style = "background:#2a2a2a;padding:10px;text-align:left;font-size:12px;color:#aaa"
    th_c = "background:#2a2a2a;padding:10px;text-align:center;font-size:12px;color:#aaa"

    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Search Console — peptidosysuplementos.mx</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>body{{font-family:Arial;max-width:900px;margin:40px auto;padding:20px;background:#0f0f0f;color:#eee}}
h1{{color:#7c3aed}}h2{{color:#aaa;font-size:15px;font-weight:normal;margin:32px 0 12px}}
.btn{{display:inline-block;background:#7c3aed;color:white;padding:10px 20px;border-radius:8px;text-decoration:none;margin-top:8px;font-size:14px}}
.btn-sec{{background:#1a1a1a;border:1px solid #444}}</style>
</head><body>
<h1>🔍 Google Search Console</h1>
<p style="color:#aaa">peptidosysuplementos.mx — Últimos 28 días</p>
{error_html}
<h2>🔑 Top 10 Keywords</h2>
<table style="{table_style}">
<thead><tr><th style="{th_style}">Keyword</th><th style="{th_c}">Clicks</th><th style="{th_c}">Impresiones</th><th style="{th_c}">CTR</th><th style="{th_c}">Posición</th></tr></thead>
<tbody>{rows_html(queries, "query")}</tbody></table>

<h2>📄 Top 10 Páginas</h2>
<table style="{table_style}">
<thead><tr><th style="{th_style}">URL</th><th style="{th_c}">Clicks</th><th style="{th_c}">Impresiones</th><th style="{th_c}">CTR</th><th style="{th_c}">Posición</th></tr></thead>
<tbody>{rows_html(pages, "page")}</tbody></table>

<br>
<a href="/" class="btn btn-sec">← Volver al agente</a>
&nbsp;
<a href="/search-console" class="btn" style="background:#1a1a2e">🔄 Actualizar</a>
</body></html>"""


scheduler_thread = threading.Thread(target=run_weekly_report, daemon=True)
scheduler_thread.start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
