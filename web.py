from flask import Flask, request, jsonify, redirect, session
import anthropic, os, requests, schedule, threading, json, secrets, time
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
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "")

# ─── JWT Auth ────────────────────────────────────────────────────────────────

_jwt_cache = {"token": None, "expires": 0}

def get_jwt_token():
    global _jwt_cache
    if _jwt_cache["token"] and time.time() < _jwt_cache["expires"]:
        return _jwt_cache["token"]
    try:
        r = requests.post(
            f"{WC_URL}/wp-json/jwt-auth/v1/token",
            json={"username": WP_USER, "password": WP_PASSWORD},
            timeout=15
        )
        data = r.json()
        token = data.get("token") or data.get("data", {}).get("token")
        if not token:
            print(f"[JWT] Error obteniendo token: {data}")
            return None
        _jwt_cache = {"token": token, "expires": time.time() + 6 * 24 * 3600}
        print("[JWT] Token obtenido correctamente")
        return token
    except Exception as e:
        print(f"[JWT] Excepción: {e}")
        return None

def jwt_headers():
    token = get_jwt_token()
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


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
        data = {
            "title": title,
            "content": content,
            "slug": slug,
            "status": status,
        }
        if meta_description:
            data["meta"] = {"_yoast_wpseo_metadesc": meta_description}
        r = requests.post(url, json=data, headers=jwt_headers(), timeout=30)
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
        r = requests.get(
            f"{WC_URL}/wp-json/wp/v2/posts/{post_id}",
            headers=jwt_headers(),
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
        r = requests.get(
            f"{WC_URL}/wp-json/wp/v2/posts",
            headers=jwt_headers(),
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


def get_all_pages():
    try:
        r = requests.get(
            f"{WC_URL}/wp-json/wp/v2/pages",
            headers=jwt_headers(),
            params={"per_page": 100, "_fields": "id,title,slug,link,status", "status": "publish"},
            timeout=15
        )
        pages = r.json()
        if not isinstance(pages, list):
            return {"error": str(pages)}
        return [{"id": p.get("id"), "title": p.get("title", {}).get("rendered", ""),
                 "slug": p.get("slug", ""), "link": p.get("link", ""), "type": "page"}
                for p in pages]
    except Exception as e:
        return {"error": str(e)}


def get_page_content(page_id):
    try:
        r = requests.get(f"{WC_URL}/wp-json/wp/v2/pages/{page_id}",
                         headers=jwt_headers(), timeout=15)
        p = r.json()
        if "id" not in p:
            return {"error": str(p)}
        return {"id": p["id"], "title": p.get("title", {}).get("rendered", ""),
                "slug": p.get("slug", ""), "link": p.get("link", ""),
                "content": p.get("content", {}).get("rendered", ""), "type": "page"}
    except Exception as e:
        return {"error": str(e)}


def update_page(page_id, data):
    try:
        r = requests.post(f"{WC_URL}/wp-json/wp/v2/pages/{page_id}",
                          headers=jwt_headers(), json=data, timeout=30)
        result = r.json()
        if "id" in result:
            return {"success": True, "id": page_id, "link": result.get("link", "")}
        return {"error": str(result)}
    except Exception as e:
        return {"error": str(e)}


def convert_elementor_to_gutenberg(post_id, post_type="post"):
    from bs4 import BeautifulSoup, Comment

    # 1. Obtener URL del post o page
    post_meta = get_page_content(post_id) if post_type == "page" else get_post_content(post_id)
    if "error" in post_meta:
        return post_meta
    url = post_meta.get("link", "")
    title = post_meta.get("title", "")
    if not url:
        return {"error": "No se pudo obtener la URL del post"}

    # 2. Cargar la página live con User-Agent de browser
    try:
        r = requests.get(url, timeout=20, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120"
        })
        r.raise_for_status()
    except Exception as e:
        return {"error": f"No se pudo cargar la pagina: {e}"}

    soup = BeautifulSoup(r.text, "html.parser")

    # 3. Eliminar ruido: scripts, estilos, nav, footer, header, comentarios
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "noscript"]):
        tag.decompose()
    for comment in soup.find_all(string=lambda t: isinstance(t, Comment)):
        comment.extract()

    # 4. Extraer contenido de Elementor (soporta text-editor clásico y contenedores modernos e-con)
    content_blocks = []

    # Widgets de texto clásicos
    for widget in soup.find_all("div", class_=lambda c: c and "elementor-widget-text-editor" in c):
        content_blocks.append(widget.decode_contents())

    # Headings de Elementor
    for widget in soup.find_all("div", class_=lambda c: c and "elementor-widget-heading" in c):
        h = widget.find(["h1", "h2", "h3", "h4"])
        if h:
            text = h.get_text(strip=True)
            if len(text) > 3:
                content_blocks.append(str(h))

    # Contenedores modernos e-con-inner: extraer todos los tags semánticos con contenido
    if not content_blocks:
        for con in soup.find_all("div", class_=lambda c: c and "e-con-inner" in c):
            for tag in con.find_all(["h1", "h2", "h3", "h4", "p", "ul", "ol", "li", "table", "blockquote"]):
                text = tag.get_text(strip=True)
                if len(text) > 20:
                    content_blocks.append(str(tag))

    # Fallback: article o entry-content
    if not content_blocks:
        article = soup.find("article") or soup.find("div", class_="entry-content") or soup.find("main")
        if article:
            for tag in article.find_all(["h2", "h3", "h4", "p", "ul", "ol", "table", "blockquote"]):
                text = tag.get_text(strip=True)
                if len(text) > 20:
                    content_blocks.append(str(tag))

    if not content_blocks:
        return {"error": "No se pudo extraer contenido del post Elementor"}

    # 5. Construir HTML limpio — conservar encabezados sueltos también
    all_headings = []
    for widget in soup.find_all("div", class_=lambda c: c and "elementor-widget-heading" in c):
        h = widget.find(["h1", "h2", "h3", "h4"])
        if h:
            all_headings.append((widget, str(h)))

    raw_html = "\n".join(content_blocks)
    clean_soup = BeautifulSoup(raw_html, "html.parser")

    # Limpiar atributos Elementor (class, id, data-*) de los tags internos
    for tag in clean_soup.find_all(True):
        elementor_classes = [c for c in tag.get("class", []) if "elementor" in c or "e-" in c]
        remaining = [c for c in tag.get("class", []) if c not in elementor_classes]
        if remaining:
            tag["class"] = remaining
        elif "class" in tag.attrs and not remaining:
            del tag["class"]
        for attr in list(tag.attrs):
            if attr.startswith("data-"):
                del tag[attr]

    clean_html = str(clean_soup)

    if len(clean_html.strip()) < 200:
        return {"error": f"Contenido extraido muy corto ({len(clean_html)} chars), posiblemente renderizado por JS"}

    # 6. Guardar en WordPress con Elementor desactivado
    payload = {"content": clean_html, "meta": {"_elementor_edit_mode": ""}}
    result = update_page(post_id, payload) if post_type == "page" else update_post(post_id, payload)

    if result.get("success"):
        return {
            "success": True,
            "post_id": post_id,
            "post_type": post_type,
            "title": title,
            "content_chars": len(clean_html),
            "url": result.get("link", url),
            "message": f"{post_type.capitalize()} convertido de Elementor a Gutenberg."
        }
    return result


def get_products_full(per_page=10):
    try:
        r = requests.get(
            f"{WC_URL}/wp-json/wc/v3/products",
            auth=HTTPBasicAuth(WC_KEY, WC_SECRET),
            params={"per_page": per_page, "status": "publish",
                    "_fields": "id,name,short_description,description,slug,images,meta_data"},
            timeout=15
        )
        result = []
        for p in r.json():
            meta = {m["key"]: m["value"] for m in p.get("meta_data", [])
                    if m["key"] in ["_yoast_wpseo_title", "_yoast_wpseo_metadesc"]}
            images = p.get("images", [])
            result.append({
                "id": p.get("id"),
                "name": p.get("name"),
                "short_description": p.get("short_description", "")[:150],
                "description": p.get("description", "")[:300],
                "slug": p.get("slug"),
                "yoast_title": meta.get("_yoast_wpseo_title", ""),
                "yoast_metadesc": meta.get("_yoast_wpseo_metadesc", ""),
                "image_alt": images[0].get("alt", "") if images else "",
                "image_id": images[0].get("id") if images else None,
            })
        return result
    except Exception as e:
        return {"error": str(e)}


def update_product_full(product_id, data):
    try:
        payload = {}
        for field in ("name", "short_description", "description"):
            if field in data:
                payload[field] = data[field]
        if "image_alt" in data:
            r_get = requests.get(
                f"{WC_URL}/wp-json/wc/v3/products/{product_id}",
                auth=HTTPBasicAuth(WC_KEY, WC_SECRET),
                params={"_fields": "images"}, timeout=15
            )
            images = r_get.json().get("images", [])
            if images:
                payload["images"] = [{"id": img["id"], "alt": data["image_alt"]} for img in images]
        meta_updates = {}
        if "yoast_title" in data:
            meta_updates["_yoast_wpseo_title"] = data["yoast_title"]
        if "yoast_metadesc" in data:
            meta_updates["_yoast_wpseo_metadesc"] = data["yoast_metadesc"]
        if meta_updates:
            payload["meta_data"] = [{"key": k, "value": v} for k, v in meta_updates.items()]
        r = requests.put(
            f"{WC_URL}/wp-json/wc/v3/products/{product_id}",
            auth=HTTPBasicAuth(WC_KEY, WC_SECRET),
            json=payload, timeout=15
        )
        result = r.json()
        if "id" in result:
            return {"success": True, "id": product_id, "name": result.get("name")}
        return {"error": str(result)}
    except Exception as e:
        return {"error": str(e)}


def update_post(post_id, data):
    try:
        r = requests.post(
            f"{WC_URL}/wp-json/wp/v2/posts/{post_id}",
            headers=jwt_headers(),
            json=data,
            timeout=30
        )
        result = r.json()
        if "id" in result:
            return {"success": True, "id": post_id, "link": result.get("link", "")}
        return {"error": str(result)}
    except Exception as e:
        return {"error": str(e)}

def blogs_audit():
    from bs4 import BeautifulSoup
    site_domain = WC_URL.replace("https://", "").replace("http://", "").split("/")[0]
    posts = get_all_posts_catalog(per_page=100)
    if isinstance(posts, dict) and "error" in posts:
        return posts
    results = []
    for post in posts:
        if not isinstance(post, dict):
            continue
        post_data = get_post_content(post["id"])
        if "error" in post_data:
            results.append({"id": post["id"], "title": post["title"], "link": post.get("link", ""), "error": post_data["error"]})
            continue
        content = post_data.get("content", "")
        soup = BeautifulSoup(content, "html.parser")
        links = soup.find_all("a", href=True)
        internal = [l["href"] for l in links if site_domain in l.get("href", "")]
        external = [l["href"] for l in links if l.get("href", "").startswith("http") and site_domain not in l.get("href", "")]
        product_links = [l for l in internal if "/producto/" in l]
        interlinks = [l for l in internal if "/producto/" not in l and l != post.get("link", "")]
        has_schema = "application/ld+json" in content
        results.append({
            "id": post["id"],
            "title": post["title"],
            "link": post.get("link", ""),
            "interlinks": len(interlinks),
            "product_links": len(product_links),
            "external_links": len(external),
            "has_schema": has_schema,
            "needs_attention": len(interlinks) < 3 or len(external) < 2 or len(product_links) < 2,
        })
    return results


def check_broken_links(post_id):
    from bs4 import BeautifulSoup
    post = get_post_content(post_id)
    if "error" in post:
        return post
    soup = BeautifulSoup(post.get("content", ""), "html.parser")
    urls = list({a["href"] for a in soup.find_all("a", href=True) if a["href"].startswith("http")})
    results = []
    for url in urls:
        try:
            r = requests.head(url, timeout=8, allow_redirects=True, headers={"User-Agent": "Mozilla/5.0"})
            results.append({"url": url, "status": r.status_code, "ok": r.status_code < 400})
        except Exception as e:
            results.append({"url": url, "status": None, "ok": False, "error": str(e)})
    broken = [r for r in results if not r["ok"]]
    return {"post_id": post_id, "title": post.get("title", ""), "total": len(results), "broken_count": len(broken), "broken": broken}


def add_schema_markup(post_id, schema_type="Article"):
    post = get_post_content(post_id)
    if "error" in post:
        return post
    content = post.get("content", "")
    if "application/ld+json" in content:
        return {"error": "El post ya tiene schema markup. Usa update_post para modificarlo si necesitas."}
    title = post.get("title", "")
    url = post.get("link", "")
    if schema_type == "Article":
        schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": title,
            "url": url,
            "publisher": {"@type": "Organization", "name": "Peptidos y Suplementos", "url": WC_URL}
        }
    elif schema_type == "FAQPage":
        schema = {"@context": "https://schema.org", "@type": "FAQPage", "name": title, "url": url, "mainEntity": []}
    else:
        schema = {"@context": "https://schema.org", "@type": schema_type, "name": title, "url": url}
    schema_tag = f'\n<script type="application/ld+json">\n{json.dumps(schema, ensure_ascii=False, indent=2)}\n</script>'
    return update_post(post_id, {"content": content + schema_tag})


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
- gsc_ctr_opportunities: keywords con muchas impresiones pero CTR bajo — mejora títulos/meta para subir clicks
- gsc_keyword_cannibalization: detecta si dos páginas compiten por la misma keyword → consolida o diferencia
- gsc_position_drops: páginas que bajaron de posición en Google esta semana vs la anterior
- gsc_inspect_url: verificar si una URL está indexada antes de reportar problema o después de publicar
- gsc_request_indexing: después de publicar un blog nuevo, solicita indexación inmediata a Google
- Cuando el usuario pida "analiza el SEO" o "qué keywords tenemos", empieza con gsc_top_queries + gsc_ctr_opportunities

AUDITORÍA DE BLOGS:
- blogs_audit: antes de optimizar links, usa esto para ver qué blogs tienen menos interlinks/links externos — prioriza por necesidad
- check_broken_links: verifica links rotos en un post específico antes de reportarlo como problema
- add_schema_markup: agrega JSON-LD (Article o FAQPage) a posts que aún no tienen — mejora featured snippets

SEO AVANZADO DE PRODUCTOS:
- get_products_full: obtiene yoast_title, yoast_metadesc, descripción larga e imagen alt
- update_product_full: actualiza meta title, meta description, descripción larga e alt text de imagen
- Prioriza: primero short_description y title, luego yoast_title/metadesc, luego description larga y alt text

MEMORIA:
- remember_instruction: guarda reglas, preferencias o contexto que debes recordar entre sesiones
- recall_memory: recupera lo que guardaste anteriormente antes de responder preguntas de estrategia

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
    },
    {
        "name": "get_products_full",
        "description": "Obtiene productos con campos SEO completos: yoast_title, yoast_metadesc, description larga e image alt text. Usa esta en lugar de get_products cuando necesites optimizar SEO avanzado de productos.",
        "input_schema": {
            "type": "object",
            "properties": {
                "per_page": {"type": "integer", "default": 10, "description": "Cantidad de productos"}
            }
        }
    },
    {
        "name": "update_product_full",
        "description": "Actualiza campos SEO completos de un producto: titulo, descripcion corta, descripcion larga, yoast_title (meta title), yoast_metadesc y alt text de imagen principal.",
        "input_schema": {
            "type": "object",
            "required": ["product_id"],
            "properties": {
                "product_id": {"type": "integer"},
                "name": {"type": "string", "description": "Titulo (max 60 chars)"},
                "short_description": {"type": "string", "description": "Descripcion corta (130-160 chars, texto plano)"},
                "description": {"type": "string", "description": "Descripcion larga en HTML"},
                "yoast_title": {"type": "string", "description": "Meta title para Google (max 60 chars)"},
                "yoast_metadesc": {"type": "string", "description": "Meta description para Google (130-160 chars)"},
                "image_alt": {"type": "string", "description": "Texto alternativo de la imagen principal"}
            }
        }
    },
    {
        "name": "blogs_audit",
        "description": "Audita TODOS los blogs publicados: cuenta interlinks, links a productos, links externos y si tienen schema markup. Devuelve cuales necesitan atencion. Usala antes de decidir que blogs optimizar primero.",
        "input_schema": {"type": "object", "properties": {}}
    },
    {
        "name": "check_broken_links",
        "description": "Verifica que los links externos e internos de un post especifico esten activos (responden HTTP 200). Devuelve lista de links rotos.",
        "input_schema": {
            "type": "object",
            "required": ["post_id"],
            "properties": {
                "post_id": {"type": "integer", "description": "ID del post a verificar"}
            }
        }
    },
    {
        "name": "add_schema_markup",
        "description": "Agrega schema markup JSON-LD a un post para mejorar featured snippets en Google. Tipos: Article (default), FAQPage.",
        "input_schema": {
            "type": "object",
            "required": ["post_id"],
            "properties": {
                "post_id": {"type": "integer"},
                "schema_type": {"type": "string", "description": "Article o FAQPage", "default": "Article"}
            }
        }
    },
    {
        "name": "gsc_ctr_opportunities",
        "description": "Encuentra keywords con muchas impresiones pero CTR bajo (menor al 3%) — son las mejores oportunidades para mejorar titulos y meta descriptions y aumentar clicks sin mejorar posicion.",
        "input_schema": {
            "type": "object",
            "properties": {
                "days": {"type": "integer", "default": 28},
                "min_impressions": {"type": "integer", "default": 50, "description": "Minimo de impresiones para considerar"},
                "limit": {"type": "integer", "default": 15}
            }
        }
    },
    {
        "name": "gsc_keyword_cannibalization",
        "description": "Detecta canibalización de keywords: keywords para las que dos o mas paginas del sitio compiten en Google. Esto divide el link juice y reduce el ranking de ambas.",
        "input_schema": {
            "type": "object",
            "properties": {
                "days": {"type": "integer", "default": 28}
            }
        }
    },
    {
        "name": "gsc_position_drops",
        "description": "Detecta paginas que cayeron de posicion en Google comparando snapshots semanales. Requiere al menos 2 semanas de historial.",
        "input_schema": {
            "type": "object",
            "properties": {
                "threshold": {"type": "integer", "default": 5, "description": "Caida minima de posiciones para reportar"}
            }
        }
    },
    {
        "name": "get_page_content",
        "description": "Obtiene el contenido HTML completo de una PAGE de WordPress (no un post de blog). Usala para leer landing pages, paginas de categorias, etc. antes de editarlas.",
        "input_schema": {
            "type": "object",
            "required": ["page_id"],
            "properties": {
                "page_id": {"type": "integer", "description": "ID de la page en WordPress"}
            }
        }
    },
    {
        "name": "update_page",
        "description": "Actualiza el contenido, titulo o meta description de una PAGE de WordPress (landing pages, paginas de categoria, etc.). Diferente de update_post que es para blogs.",
        "input_schema": {
            "type": "object",
            "required": ["page_id"],
            "properties": {
                "page_id": {"type": "integer", "description": "ID de la page en WordPress"},
                "title": {"type": "string", "description": "Nuevo titulo (opcional)"},
                "content": {"type": "string", "description": "Nuevo contenido HTML completo (opcional)"},
                "meta_description": {"type": "string", "description": "Nueva meta description 150-160 chars (opcional)"}
            }
        }
    },
    {
        "name": "get_all_pages",
        "description": "Obtiene todas las pages publicadas de WordPress (landing pages, paginas de categorias, etc.) con sus IDs y URLs.",
        "input_schema": {"type": "object", "properties": {}}
    },
    {
        "name": "convert_elementor_to_gutenberg",
        "description": "Convierte un post construido con Elementor a Gutenberg/HTML estandar de WordPress. Carga la pagina live, extrae el contenido limpio, desactiva Elementor para ese post y lo guarda via REST API. Usala cuando update_post o add-links no funcionen por ser un post Elementor. Despues de convertir, /add-links funcionara correctamente.",
        "input_schema": {
            "type": "object",
            "required": ["post_id"],
            "properties": {
                "post_id": {"type": "integer", "description": "ID del post Elementor a convertir"}
            }
        }
    },
    {
        "name": "remember_instruction",
        "description": "Guarda una instrucción o dato importante en la memoria persistente del agente. Úsala cuando el usuario te dé una preferencia, regla o contexto que debe recordarse entre sesiones.",
        "input_schema": {
            "type": "object",
            "required": ["key", "value"],
            "properties": {
                "key": {"type": "string", "description": "Identificador corto, ej: 'tono_escritura', 'keyword_principal'"},
                "value": {"type": "string", "description": "El contenido a recordar"}
            }
        }
    },
    {
        "name": "recall_memory",
        "description": "Recupera instrucciones o datos guardados previamente en la memoria persistente del agente.",
        "input_schema": {
            "type": "object",
            "properties": {
                "key": {"type": "string", "description": "Clave específica a recuperar. Si se omite, devuelve toda la memoria."}
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
    elif name == "get_page_content":
        return get_page_content(inputs["page_id"])
    elif name == "update_page":
        data = {k: inputs[k] for k in ["title", "content"] if k in inputs}
        if "meta_description" in inputs:
            data["meta"] = {"_yoast_wpseo_metadesc": inputs["meta_description"]}
        return update_page(inputs["page_id"], data)
    elif name == "get_all_pages":
        return get_all_pages()
    elif name == "convert_elementor_to_gutenberg":
        return convert_elementor_to_gutenberg(inputs["post_id"])
    elif name == "get_products_full":
        return get_products_full(inputs.get("per_page", 10))
    elif name == "update_product_full":
        return update_product_full(inputs["product_id"], {k: inputs[k] for k in inputs if k != "product_id"})
    elif name == "blogs_audit":
        return blogs_audit()
    elif name == "check_broken_links":
        return check_broken_links(inputs["post_id"])
    elif name == "add_schema_markup":
        return add_schema_markup(inputs["post_id"], inputs.get("schema_type", "Article"))
    elif name == "gsc_ctr_opportunities":
        return gsc_ctr_opportunities(inputs.get("days", 28), inputs.get("min_impressions", 50), inputs.get("limit", 15))
    elif name == "gsc_keyword_cannibalization":
        return gsc_keyword_cannibalization(inputs.get("days", 28))
    elif name == "gsc_position_drops":
        return gsc_position_drops(inputs.get("threshold", 5))
    elif name == "remember_instruction":
        return remember_instruction(inputs["key"], inputs["value"])
    elif name == "recall_memory":
        return recall_memory(inputs.get("key"))
    return {"error": "herramienta desconocida"}

@app.route("/")
def index():
    return open("templates/index.html").read()

@app.route("/chat", methods=["POST"])
def chat():
    try:
        messages = request.json.get("messages", [])
        response = client.messages.create(
            model="claude-sonnet-4-6",
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
                model="claude-sonnet-4-6",
                max_tokens=8192,
                system=SYSTEM,
                tools=TOOLS,
                messages=messages
            )
        reply = "".join(b.text for b in response.content if hasattr(b, "text"))
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"reply": f"Error: {str(e)}"}), 500

_db_path = os.environ.get("DB_PATH", "memory.db")
_data_dir = os.path.dirname(os.path.abspath(_db_path))
REPORT_FILE = os.path.join(_data_dir, "last_report.json")
MEMORY_FILE = os.path.join(_data_dir, "agent_memory.json")
_last_report = {}


def remember_instruction(key, value):
    try:
        memory = {}
        if os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                memory = json.load(f)
        memory[key] = {"value": value, "saved_at": datetime.now().isoformat()}
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(memory, f, ensure_ascii=False, indent=2)
        return {"success": True, "key": key}
    except Exception as e:
        return {"error": str(e)}


def recall_memory(key=None):
    try:
        if not os.path.exists(MEMORY_FILE):
            return {"memory": {}}
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            memory = json.load(f)
        if key:
            return {"key": key, "value": memory.get(key, {}).get("value", "No encontrado")}
        return {"memory": {k: v["value"] for k, v in memory.items()}}
    except Exception as e:
        return {"error": str(e)}


GSC_HISTORY_FILE = os.path.join(_data_dir, "gsc_history.json")


def send_webhook_notification(payload):
    if not WEBHOOK_URL:
        return
    try:
        requests.post(WEBHOOK_URL, json=payload, timeout=10)
        print("[Webhook] Notificacion enviada")
    except Exception as e:
        print(f"[Webhook] Error: {e}")


def save_gsc_snapshot():
    if not GSC_REFRESH_TOKEN:
        return {}
    try:
        rows = fetch_gsc_data("page", 7, 50)
        snapshot = {
            "date": datetime.now().isoformat(),
            "pages": {
                r["keys"][0]: {
                    "clicks": r.get("clicks", 0),
                    "impressions": r.get("impressions", 0),
                    "position": round(r.get("position", 0), 1)
                }
                for r in rows
            }
        }
        history = []
        if os.path.exists(GSC_HISTORY_FILE):
            with open(GSC_HISTORY_FILE, "r", encoding="utf-8") as f:
                history = json.load(f)
        history.append(snapshot)
        history = history[-12:]
        with open(GSC_HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        return snapshot
    except Exception as e:
        print(f"[GSC History] Error: {e}")
        return {}


def gsc_position_drops(threshold=5):
    if not os.path.exists(GSC_HISTORY_FILE):
        return {"error": "Sin historial aun. El snapshot se genera cada lunes automaticamente."}
    try:
        with open(GSC_HISTORY_FILE, "r", encoding="utf-8") as f:
            history = json.load(f)
        if len(history) < 2:
            return {"error": "Se necesitan al menos 2 snapshots para comparar. Vuelve la proxima semana."}
        prev = history[-2]["pages"]
        curr = history[-1]["pages"]
        drops = []
        for url, curr_data in curr.items():
            if url in prev:
                drop = curr_data["position"] - prev[url]["position"]
                if drop >= threshold:
                    drops.append({
                        "url": url.replace("https://peptidosysuplementos.mx", ""),
                        "prev_position": prev[url]["position"],
                        "curr_position": curr_data["position"],
                        "drop": round(drop, 1),
                        "clicks": curr_data["clicks"]
                    })
        return sorted(drops, key=lambda x: x["drop"], reverse=True)
    except Exception as e:
        return {"error": str(e)}


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


@app.route("/memory")
def memory_get():
    mem = recall_memory()
    return jsonify({"instructions": mem.get("memory", {})})


@app.route("/memory/clear", methods=["POST"])
def memory_clear():
    try:
        if os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE, "w", encoding="utf-8") as f:
                json.dump({}, f)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/blogs/audit")
def blogs_audit_endpoint():
    return jsonify(blogs_audit())


@app.route("/convert-to-gutenberg", methods=["POST"])
def convert_to_gutenberg_endpoint():
    data = request.json or {}
    post_id = data.get("post_id")
    post_type = data.get("post_type", "post")
    if not post_id:
        return jsonify({"error": "post_id es requerido"}), 400
    return jsonify(convert_elementor_to_gutenberg(post_id, post_type))


@app.route("/convert-all-elementor", methods=["POST"])
def convert_all_elementor():
    """Detecta y convierte todos los posts Y pages Elementor a Gutenberg automaticamente."""
    results = {"converted": [], "skipped": [], "errors": []}

    def check_and_convert(items, item_type):
        for item in items:
            url = item.get("link", "")
            if not url:
                continue
            try:
                html = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"}).text
                if any(m in html for m in ("elementor-widget-text-editor", "elementor-element", "e-con-inner")):
                    result = convert_elementor_to_gutenberg(item["id"], item_type)
                    if result.get("success"):
                        results["converted"].append({
                            "id": item["id"], "title": item.get("title", ""),
                            "type": item_type, "url": url,
                            "content_chars": result.get("content_chars", 0)
                        })
                    else:
                        results["errors"].append({
                            "id": item["id"], "type": item_type,
                            "error": result.get("error", "desconocido")
                        })
                else:
                    results["skipped"].append({
                        "id": item["id"], "title": item.get("title", ""),
                        "type": item_type, "reason": "Gutenberg"
                    })
            except Exception as e:
                results["errors"].append({"id": item["id"], "type": item_type, "error": str(e)})

    posts = get_all_posts_catalog(per_page=100)
    if isinstance(posts, list):
        check_and_convert(posts, "post")

    pages = get_all_pages()
    if isinstance(pages, list):
        check_and_convert(pages, "page")

    results["summary"] = {
        "converted": len(results["converted"]),
        "skipped_gutenberg": len(results["skipped"]),
        "errors": len(results["errors"])
    }
    return jsonify(results)


def run_weekly_report():
    def weekly_job():
        report = generate_seo_report()
        save_gsc_snapshot()
        send_webhook_notification({
            "type": "weekly_report",
            "date": datetime.now().isoformat(),
            "total": report.get("total", 0),
            "optimized": report.get("optimized", 0),
            "pending": report.get("pending", 0),
            "pct_optimized": report.get("pct_optimized", 0),
        })
    schedule.every().monday.at("09:00").do(weekly_job)
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
    dry_run=true devuelve preview del HTML sin publicar en WordPress."""
    try:
        data = request.json or {}
        post_id = data.get("post_id")
        dry_run = data.get("dry_run", False)
        if not post_id:
            return jsonify({"error": "post_id es requerido"}), 400

        # Intentar como post, si falla intentar como page
        post = get_post_content(post_id)
        is_page = False
        if "error" in post:
            post = get_page_content(post_id)
            is_page = True
        if "error" in post:
            return jsonify({"error": f"No se pudo obtener el contenido: {post['error']}"}), 500

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
{content}

OTROS ARTÍCULOS DEL BLOG (para interlinks entre posts):
{posts_list if posts_list else "No hay otros artículos disponibles aún."}

PRODUCTOS DE LA TIENDA (para links internos a productos):
{products_list}

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
            max_tokens=16384,
            messages=[{"role": "user", "content": prompt}]
        )

        optimized_content = response.content[0].text.strip()
        if optimized_content.startswith("```"):
            optimized_content = optimized_content.split("\n", 1)[1].rsplit("```", 1)[0].strip()

        if dry_run:
            return jsonify({
                "dry_run": True,
                "post_id": post_id,
                "title": title,
                "url": url,
                "optimized_content": optimized_content,
                "other_posts_available": len(other_posts),
                "products_available": len(products),
            })

        result = update_page(post_id, {"content": optimized_content}) if is_page else update_post(post_id, {"content": optimized_content})

        if result.get("success"):
            return jsonify({
                "success": True,
                "post_id": post_id,
                "post_type": "page" if is_page else "post",
                "title": title,
                "url": result.get("link", url),
                "other_posts_available": len(other_posts),
                "products_available": len(products),
            })
        return jsonify({"error": result.get("error", "Error al actualizar post")}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


_batch_links_status = {"running": False, "total": 0, "done": 0, "errors": 0, "results": [], "started_at": None, "finished_at": None}


def run_batch_add_links(post_ids):
    global _batch_links_status
    _batch_links_status = {"running": True, "total": len(post_ids), "done": 0, "errors": 0, "results": [], "started_at": datetime.now().isoformat(), "finished_at": None}

    for post_id in post_ids:
        try:
            post = get_post_content(post_id)
            if "error" in post:
                _batch_links_status["errors"] += 1
                _batch_links_status["results"].append({"post_id": post_id, "status": "error", "error": post["error"]})
                continue

            title = post.get("title", "")
            content = post.get("content", "")
            if not content:
                _batch_links_status["errors"] += 1
                _batch_links_status["results"].append({"post_id": post_id, "status": "error", "error": "sin contenido"})
                continue

            products = get_products(per_page=30)
            products_list = "\n".join(
                f"- {p['name']} ({WC_URL}/producto/{p['slug']})"
                for p in products if isinstance(p, dict) and "name" in p
            )
            all_posts = get_all_posts_catalog(per_page=100)
            other_posts = [p for p in all_posts if isinstance(p, dict) and str(p.get("id", "")) != str(post_id)]
            posts_list = "\n".join(
                f"- {p['title']} ({p['link']})"
                for p in other_posts if isinstance(p, dict) and p.get("title")
            )

            prompt = f"""Eres un experto SEO. Tienes este artículo de blog en peptidosysuplementos.mx:

TÍTULO: {title}
POST ID: {post_id}

CONTENIDO ACTUAL (HTML):
{content}

OTROS ARTÍCULOS DEL BLOG (para interlinks entre posts):
{posts_list if posts_list else "No hay otros artículos disponibles aún."}

PRODUCTOS DE LA TIENDA (para links internos a productos):
{products_list}

Agrega links de forma NATURAL dentro del texto existente:
1. INTERLINKS (3-6): otros artículos del blog temáticamente relevantes. <a href="URL_DEL_POST">texto</a>
2. LINKS A PRODUCTOS (4-8): productos relevantes de la tienda. <a href="URL_PRODUCTO">nombre</a>
3. LINKS EXTERNOS (3-5): PubMed, examine.com, NIH, FDA, NEJM, Mayo Clinic. <a href="URL" target="_blank" rel="noopener noreferrer">texto</a>
4. NO inventes productos ni posts que no estén en las listas.
5. Devuelve ÚNICAMENTE el HTML completo listo para WordPress, sin explicaciones."""

            response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=16384,
                messages=[{"role": "user", "content": prompt}]
            )
            optimized = response.content[0].text.strip()
            if optimized.startswith("```"):
                optimized = optimized.split("\n", 1)[1].rsplit("```", 1)[0].strip()

            result = update_post(post_id, {"content": optimized})
            if result.get("success"):
                _batch_links_status["done"] += 1
                _batch_links_status["results"].append({"post_id": post_id, "title": title, "status": "ok", "url": result.get("link", "")})
                print(f"[BatchLinks] ✅ {post_id} — {title}")
            else:
                _batch_links_status["errors"] += 1
                _batch_links_status["results"].append({"post_id": post_id, "title": title, "status": "error", "error": result.get("error", "")})

        except Exception as e:
            _batch_links_status["errors"] += 1
            _batch_links_status["results"].append({"post_id": post_id, "status": "error", "error": str(e)})
            print(f"[BatchLinks] ❌ {post_id}: {e}")

    _batch_links_status["running"] = False
    _batch_links_status["finished_at"] = datetime.now().isoformat()
    print(f"[BatchLinks] Finalizado — {_batch_links_status['done']} ok, {_batch_links_status['errors']} errores")


@app.route("/batch-add-links", methods=["POST"])
def batch_add_links():
    """Agrega interlinks, links a productos y links externos a múltiples blogs.
    Body: {"post_ids": [1,2,3]} o {"all": true} para procesar todos los blogs publicados."""
    if _batch_links_status["running"]:
        return jsonify({"error": "Ya hay un proceso en curso"}), 409
    data = request.json or {}
    if data.get("all"):
        posts = get_all_posts_catalog(per_page=100)
        post_ids = [p["id"] for p in posts if isinstance(p, dict) and p.get("id")]
    else:
        post_ids = data.get("post_ids", [])
    if not post_ids:
        return jsonify({"error": "Envía post_ids o all:true"}), 400
    thread = threading.Thread(target=run_batch_add_links, args=(post_ids,), daemon=True)
    thread.start()
    return jsonify({"status": "started", "total": len(post_ids)})


@app.route("/batch-links-status")
def batch_links_status():
    return jsonify(_batch_links_status)


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
{content}

OTROS ARTÍCULOS DEL BLOG (para interlinks):
{posts_list if posts_list else "No hay otros artículos disponibles aún."}

PRODUCTOS DE LA TIENDA (para links internos a productos):
{products_list}

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
            max_tokens=16384,
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
        rows = fetch_gsc_data("query", days, limit)
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
        rows = fetch_gsc_data("page", days, limit)
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


def fetch_gsc_data_multi(dimensions, days=28, limit=100):
    service = get_gsc_service()
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    result = service.searchanalytics().query(
        siteUrl=GSC_SITE_URL,
        body={
            "startDate": start_date,
            "endDate": end_date,
            "dimensions": dimensions,
            "rowLimit": limit,
            "orderBy": [{"fieldName": "clicks", "sortOrder": "DESCENDING"}]
        }
    ).execute()
    return result.get("rows", [])


def gsc_ctr_opportunities(days=28, min_impressions=50, limit=15):
    if not GSC_REFRESH_TOKEN:
        return {"error": "GSC no autenticado"}
    try:
        rows = fetch_gsc_data("query", days, 100)
        opportunities = [
            {
                "query": r["keys"][0],
                "impressions": r.get("impressions", 0),
                "clicks": r.get("clicks", 0),
                "ctr_pct": round(r.get("ctr", 0) * 100, 1),
                "position": round(r.get("position", 0), 1),
                "potential_clicks": round(r.get("impressions", 0) * 0.05) - r.get("clicks", 0),
            }
            for r in rows
            if r.get("impressions", 0) >= min_impressions and r.get("ctr", 0) < 0.03
        ]
        return sorted(opportunities, key=lambda x: x["impressions"], reverse=True)[:limit]
    except Exception as e:
        return {"error": str(e)}


def gsc_keyword_cannibalization(days=28):
    if not GSC_REFRESH_TOKEN:
        return {"error": "GSC no autenticado"}
    try:
        rows = fetch_gsc_data_multi(["query", "page"], days, 200)
        query_pages = {}
        for r in rows:
            query = r["keys"][0]
            page = r["keys"][1].replace("https://peptidosysuplementos.mx", "")
            impressions = r.get("impressions", 0)
            if impressions < 10:
                continue
            if query not in query_pages:
                query_pages[query] = []
            query_pages[query].append({
                "page": page,
                "clicks": r.get("clicks", 0),
                "impressions": impressions,
                "position": round(r.get("position", 0), 1)
            })
        cannibalized = [
            {"query": q, "pages": pages, "total_impressions": sum(p["impressions"] for p in pages)}
            for q, pages in query_pages.items() if len(pages) > 1
        ]
        return sorted(cannibalized, key=lambda x: x["total_impressions"], reverse=True)[:20]
    except Exception as e:
        return {"error": str(e)}


def fetch_gsc_data(dimension, days=28, limit=10):
    service = get_gsc_service()
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    result = service.searchanalytics().query(
        siteUrl=GSC_SITE_URL,
        body={
            "startDate": start_date,
            "endDate": end_date,
            "dimensions": [dimension],
            "rowLimit": limit,
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
