from flask import Flask, request, jsonify
import anthropic, os, requests, schedule, threading, json
from requests.auth import HTTPBasicAuth
from datetime import datetime

app = Flask(__name__)
client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

WC_URL = os.environ.get("WOOCOMMERCE_URL", "")
WC_KEY = os.environ.get("WOOCOMMERCE_KEY", "")
WC_SECRET = os.environ.get("WOOCOMMERCE_SECRET", "")

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


def update_post(post_id, data):
    try:
        r = requests.post(
            f"{WC_URL}/wp-json/wp/v2/posts/{post_id}",
            auth=HTTPBasicAuth(WC_KEY, WC_SECRET),
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
            f"- {p['name']} (slug: {p['slug']})" for p in products if isinstance(p, dict) and "name" in p
        )

        prompt = f"""Eres un experto SEO. Tienes este artículo de blog recién publicado en peptidosysuplementos.mx:

TÍTULO: {title}
URL: {url}
POST ID: {post_id}

CONTENIDO ACTUAL (HTML):
{content[:6000]}

PRODUCTOS DISPONIBLES EN LA TIENDA:
{products_list}

Tu tarea:
1. Agrega entre 4 y 8 links internos a productos relevantes de la lista. Usa el formato: <a href="{WC_URL}/producto/SLUG">Nombre del producto</a>
2. Asegúrate de que el contenido tenga al menos un H2 y una conclusión con llamada a la acción
3. Devuelve ÚNICAMENTE el HTML optimizado completo, sin explicaciones ni markdown extra

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
            return jsonify({"success": True, "post_id": post_id, "url": result.get("link", url)})
        return jsonify({"error": result.get("error", "Error al actualizar post")}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


scheduler_thread = threading.Thread(target=run_weekly_report, daemon=True)
scheduler_thread.start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
