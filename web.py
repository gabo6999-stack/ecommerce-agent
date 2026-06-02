from flask import Flask, request, jsonify
import anthropic, os, requests, sqlite3, json
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession
from googleapiclient.discovery import build

app = Flask(__name__)
client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

WC_URL = os.environ.get("WOOCOMMERCE_URL", "")
WC_KEY = os.environ.get("WOOCOMMERCE_KEY", "")
WC_SECRET = os.environ.get("WOOCOMMERCE_SECRET", "")
DB_PATH = os.environ.get("DB_PATH", "memory.db")
GSC_SITE_URL = os.environ.get("GSC_SITE_URL", "https://peptidosysuplementos.mx/")

# ─── BASE DE DATOS ────────────────────────────────────────────────────────────

def init_db():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            role TEXT,
            content TEXT,
            created_at TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS decisions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT,
            key TEXT UNIQUE,
            value TEXT,
            created_at TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS instructions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE,
            value TEXT,
            created_at TEXT
        )
    """)
    con.commit()
    con.close()

init_db()

def save_messages(session_id, messages):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("DELETE FROM conversations WHERE session_id = ?", (session_id,))
    for m in messages:
        content = m["content"] if isinstance(m["content"], str) else json.dumps(m["content"])
        cur.execute("INSERT INTO conversations (session_id, role, content, created_at) VALUES (?,?,?,?)",
                    (session_id, m["role"], content, datetime.now().isoformat()))
    con.commit()
    con.close()

def load_messages(session_id):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT role, content FROM conversations WHERE session_id = ? ORDER BY id", (session_id,))
    rows = cur.fetchall()
    con.close()
    messages = []
    for role, content in rows:
        try:
            parsed = json.loads(content)
            messages.append({"role": role, "content": parsed})
        except Exception:
            messages.append({"role": role, "content": content})
    return messages

def save_decision(type_, key, value):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""INSERT INTO decisions (type, key, value, created_at) VALUES (?,?,?,?)
                   ON CONFLICT(key) DO UPDATE SET value=excluded.value, created_at=excluded.created_at""",
                (type_, key, json.dumps(value), datetime.now().isoformat()))
    con.commit()
    con.close()

def get_decisions(type_=None):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    if type_:
        cur.execute("SELECT type, key, value, created_at FROM decisions WHERE type = ? ORDER BY created_at DESC", (type_,))
    else:
        cur.execute("SELECT type, key, value, created_at FROM decisions ORDER BY created_at DESC")
    rows = cur.fetchall()
    con.close()
    return [{"type": r[0], "key": r[1], "value": json.loads(r[2]), "created_at": r[3]} for r in rows]

def save_instruction(key, value):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""INSERT INTO instructions (key, value, created_at) VALUES (?,?,?)
                   ON CONFLICT(key) DO UPDATE SET value=excluded.value, created_at=excluded.created_at""",
                (key, value, datetime.now().isoformat()))
    con.commit()
    con.close()

def get_instructions():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT key, value FROM instructions ORDER BY created_at DESC")
    rows = cur.fetchall()
    con.close()
    return {r[0]: r[1] for r in rows}

def build_memory_context():
    parts = []
    instructions = get_instructions()
    if instructions:
        parts.append("=== INSTRUCCIONES PERMANENTES ===")
        for k, v in instructions.items():
            parts.append(f"- {k}: {v}")
    decisions = get_decisions()
    if decisions:
        parts.append("\n=== HISTORIAL DE CAMBIOS APLICADOS ===")
        for d in decisions[-20:]:
            parts.append(f"- [{d['created_at'][:10]}] {d['type']} | {d['key']}: {json.dumps(d['value'])}")
    return "\n".join(parts)

# ─── WOOCOMMERCE ──────────────────────────────────────────────────────────────

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
            json=data, timeout=15
        )
        result = r.json()
        if "id" in result:
            save_decision("producto_optimizado", f"producto_{product_id}", {
                "id": product_id, "name": result.get("name"), "changes": list(data.keys())
            })
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
            json=data, timeout=15
        )
        result = r.json()
        if "id" in result:
            save_decision("categoria_optimizada", f"categoria_{category_id}", {
                "id": category_id, "name": result.get("name"), "changes": list(data.keys())
            })
            return {"success": True, "id": category_id, "name": result.get("name")}
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

def create_post(title, content, slug="", meta_description="", status="publish"):
    try:
        data = {"title": title, "content": content, "slug": slug, "status": status}
        if meta_description:
            data["meta"] = {"_yoast_wpseo_metadesc": meta_description}
        r = requests.post(
            f"{WC_URL}/wp-json/wp/v2/posts",
            json=data, auth=HTTPBasicAuth(WC_KEY, WC_SECRET), timeout=30
        )
        result = r.json()
        if "id" in result:
            save_decision("blog_publicado", f"post_{result['id']}", {
                "id": result["id"], "title": title, "slug": slug,
                "link": result.get("link",""), "status": status
            })
            return {"success": True, "id": result["id"], "link": result.get("link",""), "status": result.get("status")}
        return {"error": str(result)}
    except Exception as e:
        return {"error": str(e)}

# ─── GOOGLE SEARCH CONSOLE ───────────────────────────────────────────────────

def _gsc_creds():
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
    try:
        service = build("searchconsole", "v1", credentials=_gsc_creds())
        end = datetime.now().strftime("%Y-%m-%d")
        start = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        resp = service.searchanalytics().query(
            siteUrl=GSC_SITE_URL,
            body={
                "startDate": start, "endDate": end,
                "dimensions": ["query"], "rowLimit": limit,
                "orderBy": [{"field": "CLICKS", "sortOrder": "DESCENDING"}]
            }
        ).execute()
        return [
            {
                "query": r["keys"][0],
                "clicks": r.get("clicks", 0),
                "impressions": r.get("impressions", 0),
                "ctr_pct": round(r.get("ctr", 0) * 100, 1),
                "position": round(r.get("position", 0), 1)
            }
            for r in resp.get("rows", [])
        ]
    except Exception as e:
        return {"error": str(e)}

def gsc_page_performance(days=28, limit=10):
    try:
        service = build("searchconsole", "v1", credentials=_gsc_creds())
        end = datetime.now().strftime("%Y-%m-%d")
        start = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        resp = service.searchanalytics().query(
            siteUrl=GSC_SITE_URL,
            body={
                "startDate": start, "endDate": end,
                "dimensions": ["page"], "rowLimit": limit,
                "orderBy": [{"field": "CLICKS", "sortOrder": "DESCENDING"}]
            }
        ).execute()
        return [
            {
                "page": r["keys"][0],
                "clicks": r.get("clicks", 0),
                "impressions": r.get("impressions", 0),
                "ctr_pct": round(r.get("ctr", 0) * 100, 1),
                "position": round(r.get("position", 0), 1)
            }
            for r in resp.get("rows", [])
        ]
    except Exception as e:
        return {"error": str(e)}

def gsc_inspect_url(url):
    try:
        authed = AuthorizedSession(_gsc_creds())
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
            "user_canonical": idx.get("userDeclaredCanonical", ""),
        }
    except Exception as e:
        return {"error": str(e)}

def gsc_request_indexing(url):
    try:
        authed = AuthorizedSession(_gsc_creds())
        resp = authed.post(
            "https://indexing.googleapis.com/v3/urlNotifications:publish",
            json={"url": url, "type": "URL_UPDATED"}
        )
        resp.raise_for_status()
        notify_time = resp.json().get("urlNotificationMetadata", {}).get("latestUpdate", {}).get("notifyTime", "")
        return {"success": True, "url": url, "notify_time": notify_time}
    except Exception as e:
        return {"error": str(e)}


def remember_instruction(key, value):
    save_instruction(key, value)
    return {"success": True, "saved": key}

def recall_memory():
    return {
        "instructions": get_instructions(),
        "recent_decisions": get_decisions()[-10:]
    }

# ─── SISTEMA ──────────────────────────────────────────────────────────────────

BASE_SYSTEM = """Eres un agente SEO especializado para peptidosysuplementos.mx.

Puedes optimizar productos, categorias, crear articulos de blog, y RECORDAR instrucciones permanentes.

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
- Estructura con H2 y H3 en HTML
- Incluir minimo 5 links externos a fuentes de autoridad
- Incluir minimo 8 links internos a productos de la tienda
- Meta descripcion entre 150-160 caracteres
- Contenido en HTML valido para WordPress

MEMORIA:
- Usa remember_instruction para guardar reglas permanentes que el usuario pida
- Usa recall_memory para revisar que cambios ya se hicieron antes de repetir trabajo
- Antes de optimizar productos/categorias, consulta recall_memory para no duplicar trabajo

GOOGLE SEARCH CONSOLE:
- gsc_top_queries: ver qué búsquedas traen tráfico real → optimiza títulos/meta descriptions para esas keywords exactas
- gsc_page_performance: ver qué páginas rinden mejor → aprende qué estructura y temas funcionan
- gsc_inspect_url: verificar si una URL está indexada antes de optimizarla o reportar problema
- gsc_request_indexing: después de publicar un blog nuevo, solicita indexación inmediata a Google
- Cuando el usuario pida "analiza el SEO" o "qué keywords tenemos", empieza siempre con gsc_top_queries + gsc_page_performance

Siempre pide confirmacion antes de aplicar cualquier cambio.
Responde siempre en espanol."""

TOOLS = [
    {
        "name": "get_products",
        "description": "Obtiene productos de WooCommerce",
        "input_schema": {"type": "object", "properties": {"per_page": {"type": "integer", "default": 10}}}
    },
    {
        "name": "update_product",
        "description": "Actualiza titulo y/o descripcion corta de un producto",
        "input_schema": {
            "type": "object", "required": ["product_id"],
            "properties": {
                "product_id": {"type": "integer"},
                "name": {"type": "string"},
                "short_description": {"type": "string"}
            }
        }
    },
    {
        "name": "get_categories",
        "description": "Obtiene categorias de WooCommerce",
        "input_schema": {"type": "object", "properties": {"per_page": {"type": "integer", "default": 20}}}
    },
    {
        "name": "update_category",
        "description": "Actualiza nombre y/o descripcion de una categoria",
        "input_schema": {
            "type": "object", "required": ["category_id"],
            "properties": {
                "category_id": {"type": "integer"},
                "name": {"type": "string"},
                "description": {"type": "string"}
            }
        }
    },
    {
        "name": "get_posts",
        "description": "Obtiene posts de blog existentes en WordPress",
        "input_schema": {"type": "object", "properties": {"per_page": {"type": "integer", "default": 10}}}
    },
    {
        "name": "create_post",
        "description": "Crea y publica un articulo de blog en WordPress",
        "input_schema": {
            "type": "object", "required": ["title", "content"],
            "properties": {
                "title": {"type": "string"},
                "content": {"type": "string", "description": "HTML valido para WordPress"},
                "slug": {"type": "string"},
                "meta_description": {"type": "string"},
                "status": {"type": "string", "default": "publish"}
            }
        }
    },
    {
        "name": "remember_instruction",
        "description": "Guarda una instruccion permanente (tono, reglas de negocio, preferencias)",
        "input_schema": {
            "type": "object", "required": ["key", "value"],
            "properties": {
                "key": {"type": "string"},
                "value": {"type": "string"}
            }
        }
    },
    {
        "name": "recall_memory",
        "description": "Consulta instrucciones permanentes e historial de cambios ya aplicados",
        "input_schema": {"type": "object", "properties": {}}
    },
    {
        "name": "gsc_top_queries",
        "description": "Google Search Console: top búsquedas que traen tráfico al sitio (clicks, impresiones, CTR, posición promedio)",
        "input_schema": {
            "type": "object",
            "properties": {
                "days": {"type": "integer", "default": 28, "description": "Últimos N días"},
                "limit": {"type": "integer", "default": 10, "description": "Número de queries a retornar"}
            }
        }
    },
    {
        "name": "gsc_page_performance",
        "description": "Google Search Console: rendimiento por página — qué URLs reciben más clicks desde Google",
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
        "description": "Google Search Console: verifica si una URL está indexada por Google y su estado de cobertura",
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
        "description": "Solicita a Google que indexe una URL nueva o actualizada (blogs recién publicados). Requiere que la Service Account sea Owner en GSC.",
        "input_schema": {
            "type": "object",
            "required": ["url"],
            "properties": {
                "url": {"type": "string", "description": "URL completa a indexar"}
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
            title=inputs["title"], content=inputs["content"],
            slug=inputs.get("slug",""), meta_description=inputs.get("meta_description",""),
            status=inputs.get("status","publish")
        )
    elif name == "remember_instruction":
        return remember_instruction(inputs["key"], inputs["value"])
    elif name == "recall_memory":
        return recall_memory()
    elif name == "gsc_top_queries":
        return gsc_top_queries(inputs.get("days", 28), inputs.get("limit", 10))
    elif name == "gsc_page_performance":
        return gsc_page_performance(inputs.get("days", 28), inputs.get("limit", 10))
    elif name == "gsc_inspect_url":
        return gsc_inspect_url(inputs["url"])
    elif name == "gsc_request_indexing":
        return gsc_request_indexing(inputs["url"])
    return {"error": "herramienta desconocida"}

# ─── RUTAS ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return open("templates/index.html").read()

@app.route("/chat", methods=["POST"])
def chat():
    try:
        session_id = request.json.get("session_id", "default")
        new_messages = request.json.get("messages", [])

        saved = load_messages(session_id)
        if saved and new_messages:
            messages = saved + [new_messages[-1]]
        elif saved:
            messages = saved
        else:
            messages = new_messages

        memory_ctx = build_memory_context()
        system = BASE_SYSTEM + ("\n\n" + memory_ctx if memory_ctx else "")

        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=8192,
            system=system,
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
                system=system,
                tools=TOOLS,
                messages=messages
            )

        reply = "".join(b.text for b in response.content if hasattr(b, "text"))
        messages.append({"role": "assistant", "content": reply})
        save_messages(session_id, messages)

        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"reply": f"Error: {str(e)}"}), 500

@app.route("/memory", methods=["GET"])
def memory_view():
    return jsonify({
        "instructions": get_instructions(),
        "decisions": get_decisions()
    })

@app.route("/memory/clear", methods=["POST"])
def memory_clear():
    session_id = request.json.get("session_id", "default")
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("DELETE FROM conversations WHERE session_id = ?", (session_id,))
    con.commit()
    con.close()
    return jsonify({"success": True, "cleared": session_id})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))