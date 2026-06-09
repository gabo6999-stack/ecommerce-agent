from flask import Flask, request, jsonify, redirect, session
import anthropic, os, requests, schedule, threading, json, secrets, time
from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
from anthropic.types.messages.batch_create_params import Request as BatchRequest
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

# ─── Configuración PTM ───────────────────────────────────────────────────────
PTM_URL      = os.environ.get("PTM_URL", "https://grupoptm.com")
PTM_WP_USER  = os.environ.get("PTM_WP_USER", "")
PTM_WP_PASSWORD = os.environ.get("PTM_WP_PASSWORD", "")

# ─── Configuración Raditech ──────────────────────────────────────────────────
RADITECH_URL          = os.environ.get("RADITECH_URL", "https://raditech.mx")
RADITECH_WP_USER      = os.environ.get("RADITECH_WP_USER", "")
RADITECH_WP_PASSWORD  = os.environ.get("RADITECH_WP_PASSWORD", "")
RADITECH_GSC_SITE_URL = os.environ.get("RADITECH_GSC_SITE_URL", "sc-domain:raditech.mx")

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


# ─── Autenticación JWT para PTM ──────────────────────────────────────────────

_ptm_jwt_cache = {"token": None, "expires": 0}

def get_ptm_jwt_token():
    global _ptm_jwt_cache
    if _ptm_jwt_cache["token"] and time.time() < _ptm_jwt_cache["expires"]:
        return _ptm_jwt_cache["token"]
    if not PTM_WP_USER or not PTM_WP_PASSWORD:
        print("[PTM-JWT] PTM_WP_USER o PTM_WP_PASSWORD no configurados")
        return None
    try:
        r = requests.post(
            f"{PTM_URL}/wp-json/jwt-auth/v1/token",
            json={"username": PTM_WP_USER, "password": PTM_WP_PASSWORD},
            timeout=15
        )
        data = r.json()
        token = data.get("token") or data.get("data", {}).get("token")
        if not token:
            print(f"[PTM-JWT] Error obteniendo token: {data}")
            return None
        _ptm_jwt_cache = {"token": token, "expires": time.time() + 6 * 24 * 3600}
        print("[PTM-JWT] Token obtenido correctamente")
        return token
    except Exception as e:
        print(f"[PTM-JWT] Excepción: {e}")
        return None

def ptm_jwt_headers():
    token = get_ptm_jwt_token()
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


# ─── Autenticación JWT para Raditech ─────────────────────────────────────────

_raditech_jwt_cache = {"token": None, "expires": 0}

def get_raditech_jwt_token():
    global _raditech_jwt_cache
    if _raditech_jwt_cache["token"] and time.time() < _raditech_jwt_cache["expires"]:
        return _raditech_jwt_cache["token"]
    if not RADITECH_WP_USER or not RADITECH_WP_PASSWORD:
        print("[RADITECH-JWT] RADITECH_WP_USER o RADITECH_WP_PASSWORD no configurados")
        return None
    try:
        r = requests.post(
            f"{RADITECH_URL}/wp-json/jwt-auth/v1/token",
            json={"username": RADITECH_WP_USER, "password": RADITECH_WP_PASSWORD},
            timeout=15
        )
        data = r.json()
        token = data.get("token") or data.get("data", {}).get("token")
        if not token:
            print(f"[RADITECH-JWT] Error obteniendo token: {data}")
            return None
        _raditech_jwt_cache = {"token": token, "expires": time.time() + 6 * 24 * 3600}
        print("[RADITECH-JWT] Token obtenido correctamente")
        return token
    except Exception as e:
        print(f"[RADITECH-JWT] Excepción: {e}")
        return None

def raditech_jwt_headers():
    token = get_raditech_jwt_token()
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


# ─── Funciones WordPress de PTM ──────────────────────────────────────────────

def get_ptm_posts(per_page=10):
    try:
        r = requests.get(
            f"{PTM_URL}/wp-json/wp/v2/posts",
            headers=ptm_jwt_headers(),
            params={"per_page": per_page, "_fields": "id,title,slug,status,link,date", "status": "publish"},
            timeout=15
        )
        return [{"id": p.get("id"), "title": p.get("title", {}).get("rendered", ""),
                 "slug": p.get("slug"), "status": p.get("status"),
                 "link": p.get("link"), "date": p.get("date")} for p in r.json()]
    except Exception as e:
        return {"error": str(e)}


def get_ptm_post_content(post_id):
    try:
        r = requests.get(f"{PTM_URL}/wp-json/wp/v2/posts/{post_id}",
                         headers=ptm_jwt_headers(), timeout=15)
        p = r.json()
        if "id" not in p:
            return {"error": str(p)}
        return {"id": p["id"], "title": p.get("title", {}).get("rendered", ""),
                "slug": p.get("slug", ""), "link": p.get("link", ""),
                "content": p.get("content", {}).get("rendered", "")}
    except Exception as e:
        return {"error": str(e)}


def get_ptm_all_posts_catalog(per_page=100):
    try:
        r = requests.get(
            f"{PTM_URL}/wp-json/wp/v2/posts",
            headers=ptm_jwt_headers(),
            params={"per_page": per_page, "_fields": "id,title,slug,link", "status": "publish"},
            timeout=15
        )
        posts = r.json()
        if not isinstance(posts, list):
            return {"error": str(posts)}
        return [{"id": p.get("id"), "title": p.get("title", {}).get("rendered", ""),
                 "slug": p.get("slug", ""), "link": p.get("link", "")} for p in posts]
    except Exception as e:
        return {"error": str(e)}


def create_ptm_post(title, content, slug="", meta_description="", status="publish"):
    try:
        data = {"title": title, "content": content, "slug": slug, "status": status}
        if meta_description:
            data["meta"] = {"rank_math_description": meta_description}
        r = requests.post(f"{PTM_URL}/wp-json/wp/v2/posts",
                          json=data, headers=ptm_jwt_headers(), timeout=30)
        result = r.json()
        if "id" in result:
            return {"success": True, "id": result["id"],
                    "link": result.get("link", ""), "status": result.get("status")}
        return {"error": str(result)}
    except Exception as e:
        return {"error": str(e)}


def create_ptm_page(title, content, slug="", seo_title="", meta_description="", status="publish"):
    try:
        data = {"title": title, "content": content, "slug": slug, "status": status}
        meta = {}
        if seo_title:
            meta["rank_math_title"] = seo_title
        if meta_description:
            meta["rank_math_description"] = meta_description
        if meta:
            data["meta"] = meta
        r = requests.post(f"{PTM_URL}/wp-json/wp/v2/pages",
                          json=data, headers=ptm_jwt_headers(), timeout=30)
        result = r.json()
        if "id" in result:
            return {"success": True, "id": result["id"],
                    "link": result.get("link", ""), "status": result.get("status")}
        return {"error": str(result)}
    except Exception as e:
        return {"error": str(e)}


def delete_ptm_page(page_id, force=True):
    try:
        params = {"force": "true"} if force else {}
        r = requests.delete(f"{PTM_URL}/wp-json/wp/v2/pages/{page_id}",
                            headers=ptm_jwt_headers(), params=params, timeout=30)
        result = r.json()
        if "deleted" in result or "id" in result:
            return {"success": True, "deleted": True, "id": page_id}
        return {"error": str(result)}
    except Exception as e:
        return {"error": str(e)}


def update_ptm_post(post_id, data):
    try:
        r = requests.post(f"{PTM_URL}/wp-json/wp/v2/posts/{post_id}",
                          headers=ptm_jwt_headers(), json=data, timeout=30)
        result = r.json()
        if "id" in result:
            return {"success": True, "id": post_id, "link": result.get("link", "")}
        return {"error": str(result)}
    except Exception as e:
        return {"error": str(e)}


def get_ptm_pages():
    try:
        r = requests.get(
            f"{PTM_URL}/wp-json/wp/v2/pages",
            headers=ptm_jwt_headers(),
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


def strip_wpautop_artifacts(html):
    """Remove wpautop-injected tags from script/style/anchor card structures."""
    import re as _re

    def clean_tag(m):
        tag, attrs, inner = m.group(1), m.group(2), m.group(3)
        inner = inner.replace('<br />', '\n').replace('<br/>', '\n').replace('<br>', '\n')
        # Also remove <p> and </p> tags wpautop injects inside script/style blocks
        inner = _re.sub(r'</p>', '', inner)
        inner = _re.sub(r'<p[^>]*>', '', inner)
        return f'<{tag}{attrs}>{inner}</{tag}>'

    # Clean <br /> from inside <script> and <style>
    html = _re.sub(r'<(script|style)([^>]*)>(.*?)</\1>',
                   clean_tag, html, flags=_re.DOTALL | _re.IGNORECASE)
    # Remove <p> wrappers around <script> tags
    html = _re.sub(r'<p>\s*(<script[^>]*>.*?</script>)\s*</p>',
                   r'\1', html, flags=_re.DOTALL | _re.IGNORECASE)
    # Fix stray </p> right after any opening tag close:  href="..."></p>  →  href="...">
    html = _re.sub(r'((?:href|src|style|class)="[^"]*">)\s*</p>', r'\1', html)
    # Fix <p> with only whitespace immediately before </a>  →  </a>
    html = _re.sub(r'<p>\s*</a>', r'</a>', html)
    # Fix </a><br /> separating adjacent anchor tags  →  </a>\n
    html = _re.sub(r'(</a>)\s*<br />\s*(<a\b)', r'\1\n\2', html)
    # Fix stray </p> between .ptm-faq-q button and .ptm-faq-a div
    html = _re.sub(r'(</button>)\s*</p>(\s*\n?\s*<div[^>]+ptm-faq-a)',
                   r'\1\2', html, flags=_re.IGNORECASE)
    # Fix general stray </p> after any block-opening tag where it causes nesting issues:
    # <div/section/span ...></p>  →  <div/section/span ...>
    html = _re.sub(r'(<(?:div|section|span|header|footer|nav|article|aside|main)[^>]*>)\s*</p>',
                   r'\1', html, flags=_re.IGNORECASE)
    # Fix </a></p>\n<p><a → </a>\n<a  (</p><p> injected between adjacent anchor elements)
    html = _re.sub(r'(</a>)\s*</p>\s*\n?\s*<p>\s*(<a\b)',
                   r'\1\n\2', html, flags=_re.IGNORECASE)
    # Remove <br /> right after opening <a> tag (wpautop adds it after href attributes)
    html = _re.sub(r'(<a\b[^>]*>)\s*<br\s*/?>\s*', r'\1', html, flags=_re.IGNORECASE)
    # Remove <br /> right before closing </a> tag
    html = _re.sub(r'\s*<br\s*/?>\s*(</a>)', r'\1', html, flags=_re.IGNORECASE)
    return html


def get_ptm_page_content(page_id):
    try:
        r = requests.get(f"{PTM_URL}/wp-json/wp/v2/pages/{page_id}",
                         headers=ptm_jwt_headers(),
                         params={"context": "edit"},
                         timeout=15)
        p = r.json()
        if "id" not in p:
            return {"error": str(p)}
        raw = p.get("content", {}).get("raw", "") or p.get("content", {}).get("rendered", "")
        # Strip wp:html block wrapper if present so callers get clean HTML
        raw = raw.strip()
        if raw.startswith("<!-- wp:html -->"):
            raw = raw[len("<!-- wp:html -->"):].strip()
        if raw.endswith("<!-- /wp:html -->"):
            raw = raw[:-len("<!-- /wp:html -->")].strip()
        return {"id": p["id"], "title": p.get("title", {}).get("rendered", ""),
                "slug": p.get("slug", ""), "link": p.get("link", ""),
                "content": raw, "type": "page"}
    except Exception as e:
        return {"error": str(e)}


def update_ptm_page(page_id, data):
    try:
        payload = dict(data)
        if "content" in payload:
            content = payload["content"]
            if content and "<!-- wp:html -->" not in content:
                payload["content"] = f"<!-- wp:html -->\n{content}\n<!-- /wp:html -->"
        r = requests.post(f"{PTM_URL}/wp-json/wp/v2/pages/{page_id}",
                          headers=ptm_jwt_headers(), json=payload, timeout=30)
        result = r.json()
        if "id" in result:
            return {"success": True, "id": page_id, "link": result.get("link", "")}
        return {"error": str(result)}
    except Exception as e:
        return {"error": str(e)}


def replace_in_ptm_page(page_id, find_html, replace_html):
    """Finds and replaces a specific HTML fragment in a PTM page (raw content)."""
    try:
        r = requests.get(f"{PTM_URL}/wp-json/wp/v2/pages/{page_id}",
                         headers=ptm_jwt_headers(), params={"context": "edit"}, timeout=15)
        p = r.json()
        if "id" not in p:
            return {"error": str(p)}
        raw = p.get("content", {}).get("raw", "")
        if find_html not in raw:
            return {"error": "find_html not found in page content", "hint": "El fragmento no existe exactamente en el contenido"}
        updated = raw.replace(find_html, replace_html, 1)
        r2 = requests.post(f"{PTM_URL}/wp-json/wp/v2/pages/{page_id}",
                           headers=ptm_jwt_headers(), json={"content": updated}, timeout=30)
        result = r2.json()
        if "id" in result:
            return {"success": True, "id": page_id, "link": result.get("link", "")}
        return {"error": str(result)}
    except Exception as e:
        return {"error": str(e)}


def append_to_ptm_page(page_id, html_to_append):
    """Appends HTML to an existing PTM page without regenerating the full content."""
    try:
        r = requests.get(f"{PTM_URL}/wp-json/wp/v2/pages/{page_id}",
                         headers=ptm_jwt_headers(), params={"context": "edit"}, timeout=15)
        p = r.json()
        if "id" not in p:
            return {"error": str(p)}
        current_content = p.get("content", {}).get("raw", "") or p.get("content", {}).get("rendered", "")
        updated_content = current_content + "\n" + html_to_append
        r2 = requests.post(f"{PTM_URL}/wp-json/wp/v2/pages/{page_id}",
                           headers=ptm_jwt_headers(), json={"content": updated_content}, timeout=30)
        result = r2.json()
        if "id" in result:
            return {"success": True, "id": page_id, "link": result.get("link", ""), "appended_chars": len(html_to_append)}
        return {"error": str(result)}
    except Exception as e:
        return {"error": str(e)}


# ─── Funciones WordPress de Raditech ─────────────────────────────────────────

def get_raditech_posts(per_page=10):
    try:
        r = requests.get(
            f"{RADITECH_URL}/wp-json/wp/v2/posts",
            headers=raditech_jwt_headers(),
            params={"per_page": per_page, "_fields": "id,title,slug,status,link,date", "status": "publish"},
            timeout=15
        )
        return [{"id": p.get("id"), "title": p.get("title", {}).get("rendered", ""),
                 "slug": p.get("slug"), "status": p.get("status"),
                 "link": p.get("link"), "date": p.get("date")} for p in r.json()]
    except Exception as e:
        return {"error": str(e)}


def get_raditech_post_content(post_id):
    try:
        r = requests.get(f"{RADITECH_URL}/wp-json/wp/v2/posts/{post_id}",
                         headers=raditech_jwt_headers(), timeout=15)
        p = r.json()
        if "id" not in p:
            return {"error": str(p)}
        return {"id": p["id"], "title": p.get("title", {}).get("rendered", ""),
                "slug": p.get("slug", ""), "link": p.get("link", ""),
                "content": p.get("content", {}).get("rendered", "")}
    except Exception as e:
        return {"error": str(e)}


def get_raditech_all_posts_catalog(per_page=100):
    try:
        r = requests.get(
            f"{RADITECH_URL}/wp-json/wp/v2/posts",
            headers=raditech_jwt_headers(),
            params={"per_page": per_page, "_fields": "id,title,slug,link", "status": "publish"},
            timeout=15
        )
        posts = r.json()
        if not isinstance(posts, list):
            return {"error": str(posts)}
        return [{"id": p.get("id"), "title": p.get("title", {}).get("rendered", ""),
                 "slug": p.get("slug", ""), "link": p.get("link", "")} for p in posts]
    except Exception as e:
        return {"error": str(e)}


def create_raditech_post(title, content, slug="", meta_description="", status="publish"):
    try:
        data = {"title": title, "content": content, "slug": slug, "status": status}
        if meta_description:
            data["meta"] = {"rank_math_description": meta_description}
        r = requests.post(f"{RADITECH_URL}/wp-json/wp/v2/posts",
                          json=data, headers=raditech_jwt_headers(), timeout=30)
        result = r.json()
        if "id" in result:
            return {"success": True, "id": result["id"],
                    "link": result.get("link", ""), "status": result.get("status")}
        return {"error": str(result)}
    except Exception as e:
        return {"error": str(e)}


def update_raditech_post(post_id, data):
    try:
        r = requests.post(f"{RADITECH_URL}/wp-json/wp/v2/posts/{post_id}",
                          headers=raditech_jwt_headers(), json=data, timeout=30)
        result = r.json()
        if "id" in result:
            return {"success": True, "id": post_id, "link": result.get("link", "")}
        return {"error": str(result)}
    except Exception as e:
        return {"error": str(e)}


def get_raditech_pages():
    try:
        r = requests.get(
            f"{RADITECH_URL}/wp-json/wp/v2/pages",
            headers=raditech_jwt_headers(),
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


def get_raditech_page_content(page_id):
    try:
        r = requests.get(f"{RADITECH_URL}/wp-json/wp/v2/pages/{page_id}",
                         headers=raditech_jwt_headers(),
                         params={"context": "edit"}, timeout=15)
        p = r.json()
        if "id" not in p:
            return {"error": str(p)}
        raw = p.get("content", {}).get("raw", "") or p.get("content", {}).get("rendered", "")
        return {"id": p["id"], "title": p.get("title", {}).get("rendered", ""),
                "slug": p.get("slug", ""), "link": p.get("link", ""),
                "content": raw, "type": "page"}
    except Exception as e:
        return {"error": str(e)}


def update_raditech_page(page_id, data):
    try:
        r = requests.post(f"{RADITECH_URL}/wp-json/wp/v2/pages/{page_id}",
                          headers=raditech_jwt_headers(), json=data, timeout=30)
        result = r.json()
        if "id" in result:
            return {"success": True, "id": page_id, "link": result.get("link", "")}
        return {"error": str(result)}
    except Exception as e:
        return {"error": str(e)}


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
            data["meta"] = {"rank_math_description": meta_description}
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
                    if m["key"] in ["rank_math_title", "rank_math_description"]}
            images = p.get("images", [])
            result.append({
                "id": p.get("id"),
                "name": p.get("name"),
                "short_description": p.get("short_description", "")[:150],
                "description": p.get("description", "")[:300],
                "slug": p.get("slug"),
                "rank_math_title": meta.get("rank_math_title", ""),
                "rank_math_description": meta.get("rank_math_description", ""),
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
        if "seo_title" in data:
            meta_updates["rank_math_title"] = data["seo_title"]
        if "seo_description" in data:
            meta_updates["rank_math_description"] = data["seo_description"]
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


def _extract_faq_from_html(content):
    """Parse <h3> questions + next <p> answer pairs from HTML."""
    import re
    faq_items = []
    h3_pattern = re.compile(
        r'<h3[^>]*>(.*?)</h3>([\s\S]*?)<p[^>]*>([\s\S]*?)</p>',
        re.IGNORECASE
    )
    for match in h3_pattern.finditer(content):
        question = re.sub(r'<[^>]+>', '', match.group(1)).strip()
        answer = re.sub(r'<[^>]+>', '', match.group(3)).strip()
        if '?' in question and len(answer) > 20:
            faq_items.append({
                "@type": "Question",
                "name": question,
                "acceptedAnswer": {"@type": "Answer", "text": answer[:600]}
            })
    return faq_items


def add_schema_markup(post_id, schema_type="Article"):
    import re
    post = get_post_content(post_id)
    if "error" in post:
        return post
    content = post.get("content", "")
    title = post.get("title", "")
    url = post.get("link", "")

    # Remove existing schema so it can be replaced with a correct one
    content_clean = re.sub(
        r'\s*<script type="application/ld\+json">[\s\S]*?</script>',
        '',
        content
    ).strip()

    if schema_type == "Article":
        schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": title,
            "url": url,
            "publisher": {"@type": "Organization", "name": "Peptidos y Suplementos", "url": WC_URL}
        }
    elif schema_type == "FAQPage":
        faq_items = _extract_faq_from_html(content_clean)
        schema = {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "name": title,
            "url": url,
            "mainEntity": faq_items
        }
    else:
        schema = {"@context": "https://schema.org", "@type": schema_type, "name": title, "url": url}

    schema_tag = f'\n<script type="application/ld+json">\n{json.dumps(schema, ensure_ascii=False, indent=2)}\n</script>'
    result = update_post(post_id, {"content": content_clean + schema_tag})
    if schema_type == "FAQPage":
        result["faq_items_found"] = len(faq_items)
    return result


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
- get_products_full: obtiene seo_title, seo_description, descripción larga e imagen alt
- update_product_full: actualiza meta title, meta description, descripción larga e alt text de imagen
- Prioriza: primero short_description y title, luego seo_title/metadesc, luego description larga y alt text

MEMORIA:
- remember_instruction: guarda reglas, preferencias o contexto que debes recordar entre sesiones
- recall_memory: recupera lo que guardaste anteriormente antes de responder preguntas de estrategia

Siempre usa las herramientas para obtener datos reales antes de proponer cambios.
Pide confirmacion antes de aplicar cualquier cambio.
Responde siempre en espanol.

GRUPO PTM — SEGUNDO SITIO (grupoptm.com):
peptidosysuplementos.mx (PYS) y grupoptm.com (PTM) son sitios hermanos del mismo negocio.
PTM es la plataforma de telemedicina: consultas médicas especializadas en péptidos.
Tienes acceso completo a ambos sitios para leer y escribir contenido.

HERRAMIENTAS DE PTM:
- create_ptm_page: crea una nueva landing page en grupoptm.com con título, slug y SEO inicial
- append_to_ptm_page: agrega HTML al final de una página PTM existente sin reescribir todo el contenido (usa para schema, interlinks, notas)
- replace_in_ptm_page: reemplaza un fragmento HTML específico en el contenido raw de una página PTM (find & replace quirúrgico, sin tocar el resto)
- get_ptm_pages: obtiene todas las páginas de PTM (landing pages de tratamientos)
- get_ptm_page_content: lee el HTML de una página de PTM antes de editarla
- update_ptm_page: actualiza contenido, SEO title o meta description de una página de PTM
- get_ptm_posts: lista los blogs de PTM
- get_ptm_post_content: lee el HTML de un blog de PTM
- get_ptm_all_posts_catalog: mapa completo de blogs de PTM para interlinks
- create_ptm_post: crea y publica un artículo en el blog de PTM
- update_ptm_post: actualiza un blog existente de PTM

MAPA DE PÁGINAS DE PTM (landing pages SEO):
- Pérdida de peso / GLP-1 / semaglutida / tirzepatida / Ozempic
  → https://grupoptm.com/perdida-de-peso
- Longevidad / anti-aging / Epithalon / GHK-Cu / MOTS-c
  → https://grupoptm.com/longevidad-antiaging
- Rendimiento / recuperación deportiva / BPC-157 / TB-500 / IGF-1
  → https://grupoptm.com/rendimiento-recuperacion
- Salud hormonal / TRT / testosterona / péptidos hormonales
  → https://grupoptm.com/salud-hormonal

REGLAS DE CROSS-LINKING BIDIRECCIONAL:
- En blogs de PYS que traten estos temas, agrega al final un CTA hacia la página PTM correspondiente.
- En páginas y blogs de PTM, agrega links a los productos relevantes de PYS (usa get_products para obtener slugs).
- Formato del CTA de PYS → PTM:
<div style="background:#f0fdf4;border-left:4px solid #22c55e;padding:16px;margin:24px 0;border-radius:8px;">
<p style="margin:0;"><strong>¿Buscas orientación médica personalizada?</strong><br>
En <a href="URL_PTM" target="_blank" rel="noopener noreferrer">Grupo PTM</a> contamos con médicos especializados en péptidos que pueden guiarte en tu tratamiento.</p>
</div>
- Formato del CTA de PTM → PYS:
<p>Puedes adquirir <a href="URL_PRODUCTO_PYS">nombre del producto</a> directamente en nuestra tienda.</p>
- Máximo 1 CTA de cross-linking por artículo. Anchor text siempre descriptivo, nunca "click aquí".

RADITECH — TERCER SITIO (raditech.mx):
Empresa mexicana de software médico con 20+ años, 400+ clientes, 40,000+ estudios/mes.
Productos: VIRA PACS, Teleradiología 24/7, Medsi HIS, Monitores médicos de diagnóstico.
Audiencia B2B: directores médicos, jefes de radiología, gerentes TI hospitalario.
SEO orientado a capturar tráfico de decisores evaluando PACS, RIS, HIS o teleradiología.

HERRAMIENTAS DE RADITECH:
- get_raditech_posts: lista blogs publicados en raditech.mx
- get_raditech_post_content: lee HTML de un blog de Raditech antes de editarlo
- get_raditech_all_posts_catalog: mapa completo de blogs de Raditech para interlinks
- create_raditech_post: crea y publica artículo B2B en raditech.mx
- update_raditech_post: actualiza blog existente en Raditech
- get_raditech_pages: lista páginas de raditech.mx (landings de servicios)
- get_raditech_page_content: lee HTML de una página de Raditech antes de editarla
- update_raditech_page: actualiza título, SEO title, meta description o contenido de una página

HERRAMIENTAS GSC DE RADITECH:
- gsc_raditech_top_queries: keywords que traen tráfico a raditech.mx (clicks, impresiones, CTR, posición)
- gsc_raditech_page_performance: páginas de raditech.mx con mejor rendimiento en Google
- gsc_raditech_ctr_opportunities: keywords con muchas impresiones pero CTR bajo en raditech.mx

REGLAS SEO PARA RADITECH:
- Contenido B2B técnico-institucional (NO consumidor final)
- Keywords objetivo: PACS México, teleradiología, sistema HIS hospital, DICOM, RIS radiología
- Links externos de autoridad: RSNA, HIMSS, pubmed.ncbi.nlm.nih.gov, acr.org, hl7.org
- Mínimo 4 links internos a otras páginas/servicios de Raditech
- Rank Math: rank_math_title y rank_math_description (igual que PYS y PTM)
- NO cruzar contenido con PYS ni PTM — son nichos distintos (B2B médico vs B2C wellness)"""

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
        "description": "Actualiza el contenido, título, SEO title o meta description de un post de blog existente en WordPress",
        "input_schema": {
            "type": "object",
            "required": ["post_id"],
            "properties": {
                "post_id": {"type": "integer", "description": "ID del post en WordPress"},
                "title": {"type": "string", "description": "Nuevo título visible del post (H1, opcional)"},
                "content": {"type": "string", "description": "Nuevo contenido HTML completo (opcional)"},
                "meta_description": {"type": "string", "description": "Nueva meta description 150-160 chars (opcional)"},
                "seo_title": {"type": "string", "description": "SEO title para Google (max 60 chars), aparece en los resultados de búsqueda. Diferente al título visible del post."}
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
        "description": "Obtiene productos con campos SEO completos: seo_title, seo_description, description larga e image alt text. Usa esta en lugar de get_products cuando necesites optimizar SEO avanzado de productos.",
        "input_schema": {
            "type": "object",
            "properties": {
                "per_page": {"type": "integer", "default": 10, "description": "Cantidad de productos"}
            }
        }
    },
    {
        "name": "update_product_full",
        "description": "Actualiza campos SEO completos de un producto: titulo, descripcion corta, descripcion larga, seo_title (meta title), seo_description y alt text de imagen principal.",
        "input_schema": {
            "type": "object",
            "required": ["product_id"],
            "properties": {
                "product_id": {"type": "integer"},
                "name": {"type": "string", "description": "Titulo (max 60 chars)"},
                "short_description": {"type": "string", "description": "Descripcion corta (130-160 chars, texto plano)"},
                "description": {"type": "string", "description": "Descripcion larga en HTML"},
                "seo_title": {"type": "string", "description": "Meta title para Google (max 60 chars)"},
                "seo_description": {"type": "string", "description": "Meta description para Google (130-160 chars)"},
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
        "description": "Actualiza titulo, meta description, Rank Math SEO title o contenido de una PAGE de WordPress. Usar seo_title para el titulo que aparece en Google (puede ser diferente al titulo de la pagina).",
        "input_schema": {
            "type": "object",
            "required": ["page_id"],
            "properties": {
                "page_id": {"type": "integer", "description": "ID de la page en WordPress"},
                "title": {"type": "string", "description": "Titulo visible de la pagina (browser tab, breadcrumbs)"},
                "seo_title": {"type": "string", "description": "SEO title para Google (max 60 chars). Ejemplo: 'Tirzepatida en Mexico 2026 | PyS MX'"},
                "meta_description": {"type": "string", "description": "Meta description para Google (150-160 chars)"},
                "slug": {"type": "string", "description": "Slug de la URL (sin slashes). Ej: 'precio-de-retatrutida-en-mexico'. ADVERTENCIA: cambia la URL publica de la pagina."},
                "content": {"type": "string", "description": "Contenido HTML completo (opcional)"}
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
    },
    {
        "name": "get_ptm_posts",
        "description": "Obtiene los posts de blog publicados en grupoptm.com (WordPress de PTM).",
        "input_schema": {
            "type": "object",
            "properties": {
                "per_page": {"type": "integer", "default": 10}
            }
        }
    },
    {
        "name": "get_ptm_post_content",
        "description": "Obtiene el contenido HTML completo de un post de blog de grupoptm.com. Úsala siempre antes de editar.",
        "input_schema": {
            "type": "object",
            "required": ["post_id"],
            "properties": {
                "post_id": {"type": "integer", "description": "ID del post en WordPress de PTM"}
            }
        }
    },
    {
        "name": "get_ptm_all_posts_catalog",
        "description": "Obtiene TODOS los artículos publicados de grupoptm.com con sus URLs. Úsala para construir el mapa de interlinks de PTM.",
        "input_schema": {
            "type": "object",
            "properties": {
                "per_page": {"type": "integer", "default": 100}
            }
        }
    },
    {
        "name": "create_ptm_post",
        "description": "Crea y publica un artículo de blog en grupoptm.com.",
        "input_schema": {
            "type": "object",
            "required": ["title", "content"],
            "properties": {
                "title": {"type": "string", "description": "Título SEO (max 60 chars)"},
                "content": {"type": "string", "description": "Contenido HTML para WordPress"},
                "slug": {"type": "string", "description": "URL amigable en minúsculas con guiones"},
                "meta_description": {"type": "string", "description": "Meta descripción 150-160 chars"},
                "status": {"type": "string", "default": "publish", "description": "publish o draft"}
            }
        }
    },
    {
        "name": "update_ptm_post",
        "description": "Actualiza el contenido, título o meta description de un post de blog en grupoptm.com.",
        "input_schema": {
            "type": "object",
            "required": ["post_id"],
            "properties": {
                "post_id": {"type": "integer", "description": "ID del post en WordPress de PTM"},
                "title": {"type": "string", "description": "Nuevo título (opcional)"},
                "content": {"type": "string", "description": "Nuevo contenido HTML completo (opcional)"},
                "meta_description": {"type": "string", "description": "Nueva meta description 150-160 chars (opcional)"},
                "seo_title": {"type": "string", "description": "SEO title para Google (max 60 chars, opcional)"}
            }
        }
    },
    {
        "name": "delete_ptm_page",
        "description": "Elimina permanentemente una página de grupoptm.com. Úsala para borrar páginas duplicadas o de prueba.",
        "input_schema": {
            "type": "object",
            "required": ["page_id"],
            "properties": {
                "page_id": {"type": "integer", "description": "ID de la página a eliminar"}
            }
        }
    },
    {
        "name": "create_ptm_page",
        "description": "Crea y publica una nueva página (landing page) en grupoptm.com.",
        "input_schema": {
            "type": "object",
            "required": ["title", "content"],
            "properties": {
                "title": {"type": "string", "description": "Título de la página"},
                "content": {"type": "string", "description": "Contenido HTML de la página"},
                "slug": {"type": "string", "description": "Slug URL de la página (opcional)"},
                "seo_title": {"type": "string", "description": "SEO title para Rank Math (max 60 chars, opcional)"},
                "meta_description": {"type": "string", "description": "Meta description 150-160 chars (opcional)"},
                "status": {"type": "string", "description": "Estado: publish o draft (default: publish)"}
            }
        }
    },
    {
        "name": "get_ptm_pages",
        "description": "Obtiene todas las páginas publicadas de grupoptm.com (landing pages de tratamientos, etc.).",
        "input_schema": {"type": "object", "properties": {}}
    },
    {
        "name": "get_ptm_page_content",
        "description": "Obtiene el contenido HTML completo de una página de grupoptm.com. Úsala siempre antes de editar una landing page.",
        "input_schema": {
            "type": "object",
            "required": ["page_id"],
            "properties": {
                "page_id": {"type": "integer", "description": "ID de la página en WordPress de PTM"}
            }
        }
    },
    {
        "name": "update_ptm_page",
        "description": "Actualiza título, contenido, SEO title o meta description de una página de grupoptm.com. Ideal para optimizar las landing pages de tratamientos.",
        "input_schema": {
            "type": "object",
            "required": ["page_id"],
            "properties": {
                "page_id": {"type": "integer", "description": "ID de la página en WordPress de PTM"},
                "title": {"type": "string", "description": "Título visible de la página (opcional)"},
                "seo_title": {"type": "string", "description": "SEO title para Google (max 60 chars, opcional)"},
                "meta_description": {"type": "string", "description": "Meta description para Google 150-160 chars (opcional)"},
                "content": {"type": "string", "description": "Contenido HTML completo (opcional)"}
            }
        }
    },
    {
        "name": "replace_in_ptm_page",
        "description": "Reemplaza un fragmento HTML específico dentro del contenido raw de una página PTM. Úsala para corregir o actualizar partes específicas del HTML sin reescribir toda la página. Retorna error si el fragmento no se encuentra exactamente.",
        "input_schema": {
            "type": "object",
            "required": ["page_id", "find_html", "replace_html"],
            "properties": {
                "page_id": {"type": "integer", "description": "ID de la página en WordPress de PTM"},
                "find_html": {"type": "string", "description": "Fragmento HTML exacto a buscar en el contenido (debe ser exacto, incluyendo espacios y saltos de línea)"},
                "replace_html": {"type": "string", "description": "HTML que reemplazará al fragmento encontrado"}
            }
        }
    },
    {
        "name": "append_to_ptm_page",
        "description": "Agrega HTML al final de una página existente de grupoptm.com SIN reescribir el contenido completo. Ideal para añadir secciones (interlinks, schema JSON-LD, notas SEO) a páginas grandes.",
        "input_schema": {
            "type": "object",
            "required": ["page_id", "html_to_append"],
            "properties": {
                "page_id": {"type": "integer", "description": "ID de la página en WordPress de PTM"},
                "html_to_append": {"type": "string", "description": "HTML a agregar al final del contenido existente"}
            }
        }
    },
    # ── Raditech tools ────────────────────────────────────────────────────────
    {
        "name": "get_raditech_posts",
        "description": "Lista blogs publicados en raditech.mx.",
        "input_schema": {"type": "object", "properties": {"per_page": {"type": "integer", "default": 10}}}
    },
    {
        "name": "get_raditech_post_content",
        "description": "Obtiene el HTML completo de un blog de raditech.mx. Úsala siempre antes de editar.",
        "input_schema": {
            "type": "object", "required": ["post_id"],
            "properties": {"post_id": {"type": "integer", "description": "ID del post en WordPress de Raditech"}}
        }
    },
    {
        "name": "get_raditech_all_posts_catalog",
        "description": "Mapa completo de todos los blogs publicados en raditech.mx (IDs, títulos, URLs). Úsala para construir interlinks.",
        "input_schema": {"type": "object", "properties": {"per_page": {"type": "integer", "default": 100}}}
    },
    {
        "name": "create_raditech_post",
        "description": "Crea y publica un artículo de blog B2B en raditech.mx.",
        "input_schema": {
            "type": "object", "required": ["title", "content"],
            "properties": {
                "title": {"type": "string", "description": "Título SEO (max 60 chars)"},
                "content": {"type": "string", "description": "Contenido HTML para WordPress"},
                "slug": {"type": "string", "description": "URL amigable en minúsculas con guiones"},
                "meta_description": {"type": "string", "description": "Meta descripción 150-160 chars"},
                "status": {"type": "string", "default": "publish"}
            }
        }
    },
    {
        "name": "update_raditech_post",
        "description": "Actualiza contenido, título, SEO title o meta description de un blog de raditech.mx.",
        "input_schema": {
            "type": "object", "required": ["post_id"],
            "properties": {
                "post_id": {"type": "integer"},
                "title": {"type": "string"},
                "content": {"type": "string"},
                "meta_description": {"type": "string"},
                "seo_title": {"type": "string", "description": "SEO title para Google (max 60 chars)"}
            }
        }
    },
    {
        "name": "get_raditech_pages",
        "description": "Lista páginas publicadas en raditech.mx (landings de servicios: PACS, teleradiología, HIS, monitores).",
        "input_schema": {"type": "object", "properties": {}}
    },
    {
        "name": "get_raditech_page_content",
        "description": "Obtiene el HTML completo de una página de raditech.mx. Úsala antes de editar.",
        "input_schema": {
            "type": "object", "required": ["page_id"],
            "properties": {"page_id": {"type": "integer"}}
        }
    },
    {
        "name": "update_raditech_page",
        "description": "Actualiza título, SEO title, meta description o contenido de una página de raditech.mx.",
        "input_schema": {
            "type": "object", "required": ["page_id"],
            "properties": {
                "page_id": {"type": "integer"},
                "title": {"type": "string"},
                "seo_title": {"type": "string", "description": "SEO title para Google (max 60 chars)"},
                "meta_description": {"type": "string", "description": "Meta description 150-160 chars"},
                "content": {"type": "string", "description": "HTML completo (opcional)"}
            }
        }
    },
    {
        "name": "gsc_raditech_top_queries",
        "description": "Google Search Console: top keywords que traen tráfico a raditech.mx (clicks, impresiones, CTR, posición).",
        "input_schema": {
            "type": "object",
            "properties": {
                "days": {"type": "integer", "default": 28},
                "limit": {"type": "integer", "default": 10}
            }
        }
    },
    {
        "name": "gsc_raditech_page_performance",
        "description": "Google Search Console: páginas de raditech.mx con mejor rendimiento orgánico.",
        "input_schema": {
            "type": "object",
            "properties": {
                "days": {"type": "integer", "default": 28},
                "limit": {"type": "integer", "default": 10}
            }
        }
    },
    {
        "name": "gsc_raditech_ctr_opportunities",
        "description": "Google Search Console: keywords de raditech.mx con muchas impresiones pero CTR bajo — oportunidades para mejorar títulos y meta descriptions.",
        "input_schema": {
            "type": "object",
            "properties": {
                "days": {"type": "integer", "default": 28},
                "min_impressions": {"type": "integer", "default": 50},
                "limit": {"type": "integer", "default": 15}
            }
        }
    },
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
        meta = {}
        if "meta_description" in inputs:
            meta["rank_math_description"] = inputs["meta_description"]
        if "seo_title" in inputs:
            meta["rank_math_title"] = inputs["seo_title"]
        if meta:
            data["meta"] = meta
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
        data = {k: inputs[k] for k in ["title", "content", "slug"] if k in inputs}
        meta = {}
        if "meta_description" in inputs:
            meta["rank_math_description"] = inputs["meta_description"]
        if "seo_title" in inputs:
            meta["rank_math_title"] = inputs["seo_title"]
        if meta:
            data["meta"] = meta
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
    elif name == "get_ptm_posts":
        return get_ptm_posts(inputs.get("per_page", 10))
    elif name == "get_ptm_post_content":
        return get_ptm_post_content(inputs["post_id"])
    elif name == "get_ptm_all_posts_catalog":
        return get_ptm_all_posts_catalog(inputs.get("per_page", 100))
    elif name == "create_ptm_post":
        return create_ptm_post(
            title=inputs["title"],
            content=inputs["content"],
            slug=inputs.get("slug", ""),
            meta_description=inputs.get("meta_description", ""),
            status=inputs.get("status", "publish")
        )
    elif name == "delete_ptm_page":
        return delete_ptm_page(inputs["page_id"])
    elif name == "create_ptm_page":
        return create_ptm_page(
            title=inputs["title"],
            content=inputs["content"],
            slug=inputs.get("slug", ""),
            seo_title=inputs.get("seo_title", ""),
            meta_description=inputs.get("meta_description", ""),
            status=inputs.get("status", "publish")
        )
    elif name == "update_ptm_post":
        data = {k: inputs[k] for k in ["title", "content"] if k in inputs}
        meta = {}
        if "meta_description" in inputs:
            meta["rank_math_description"] = inputs["meta_description"]
        if "seo_title" in inputs:
            meta["rank_math_title"] = inputs["seo_title"]
        if meta:
            data["meta"] = meta
        return update_ptm_post(inputs["post_id"], data)
    elif name == "get_ptm_pages":
        return get_ptm_pages()
    elif name == "get_ptm_page_content":
        return get_ptm_page_content(inputs["page_id"])
    elif name == "update_ptm_page":
        data = {k: inputs[k] for k in ["title", "content", "slug"] if k in inputs}
        meta = {}
        if "meta_description" in inputs:
            meta["rank_math_description"] = inputs["meta_description"]
        if "seo_title" in inputs:
            meta["rank_math_title"] = inputs["seo_title"]
        if meta:
            data["meta"] = meta
        return update_ptm_page(inputs["page_id"], data)
    elif name == "replace_in_ptm_page":
        return replace_in_ptm_page(inputs["page_id"], inputs["find_html"], inputs["replace_html"])
    elif name == "append_to_ptm_page":
        return append_to_ptm_page(inputs["page_id"], inputs["html_to_append"])
    # ── Raditech dispatchers ──────────────────────────────────────────────────
    elif name == "get_raditech_posts":
        return get_raditech_posts(inputs.get("per_page", 10))
    elif name == "get_raditech_post_content":
        return get_raditech_post_content(inputs["post_id"])
    elif name == "get_raditech_all_posts_catalog":
        return get_raditech_all_posts_catalog(inputs.get("per_page", 100))
    elif name == "create_raditech_post":
        return create_raditech_post(
            title=inputs["title"], content=inputs["content"],
            slug=inputs.get("slug", ""), meta_description=inputs.get("meta_description", ""),
            status=inputs.get("status", "publish")
        )
    elif name == "update_raditech_post":
        data = {k: inputs[k] for k in ["title", "content"] if k in inputs}
        meta = {}
        if "meta_description" in inputs:
            meta["rank_math_description"] = inputs["meta_description"]
        if "seo_title" in inputs:
            meta["rank_math_title"] = inputs["seo_title"]
        if meta:
            data["meta"] = meta
        return update_raditech_post(inputs["post_id"], data)
    elif name == "get_raditech_pages":
        return get_raditech_pages()
    elif name == "get_raditech_page_content":
        return get_raditech_page_content(inputs["page_id"])
    elif name == "update_raditech_page":
        data = {k: inputs[k] for k in ["title", "content", "slug"] if k in inputs}
        meta = {}
        if "meta_description" in inputs:
            meta["rank_math_description"] = inputs["meta_description"]
        if "seo_title" in inputs:
            meta["rank_math_title"] = inputs["seo_title"]
        if meta:
            data["meta"] = meta
        return update_raditech_page(inputs["page_id"], data)
    elif name == "gsc_raditech_top_queries":
        return gsc_raditech_top_queries(inputs.get("days", 28), inputs.get("limit", 10))
    elif name == "gsc_raditech_page_performance":
        return gsc_raditech_page_performance(inputs.get("days", 28), inputs.get("limit", 10))
    elif name == "gsc_raditech_ctr_opportunities":
        return gsc_raditech_ctr_opportunities(inputs.get("days", 28), inputs.get("min_impressions", 50), inputs.get("limit", 15))
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


@app.route("/save-as-gutenberg", methods=["POST"])
def save_as_gutenberg():
    """Guarda contenido HTML como Gutenberg y deshabilita Elementor para ese post/page.
    Body: {post_id, content, title?, meta_description?, post_type: 'post'|'page'}"""
    data = request.json or {}
    post_id = data.get("post_id")
    content = data.get("content", "")
    post_type = data.get("post_type", "post")
    if not post_id or not content:
        return jsonify({"error": "post_id y content son requeridos"}), 400

    payload = {"content": content, "meta": {"_elementor_edit_mode": ""}}
    if data.get("title"):
        payload["title"] = data["title"]
    if data.get("meta_description"):
        payload["meta"] = {**payload["meta"], "rank_math_description": data["meta_description"]}

    result = update_page(post_id, payload) if post_type == "page" else update_post(post_id, payload)
    if result.get("success"):
        return jsonify({"success": True, "post_id": post_id, "post_type": post_type,
                        "url": result.get("link", ""), "elementor": "disabled"})
    return jsonify({"error": result.get("error", "Error al guardar")}), 500


@app.route("/set-elementor-mode", methods=["POST"])
def set_elementor_mode():
    """Habilita o deshabilita Elementor para una page sin tocar el contenido.
    Body: {page_id, mode: 'builder' (activar) | '' (desactivar/Gutenberg)}"""
    data = request.json or {}
    page_id = data.get("page_id")
    mode = data.get("mode", "")
    if not page_id:
        return jsonify({"error": "page_id es requerido"}), 400
    r = requests.post(
        f"{WC_URL}/wp-json/wp/v2/pages/{page_id}",
        headers=jwt_headers(),
        json={"meta": {"_elementor_edit_mode": mode}},
        timeout=15
    )
    result = r.json()
    if "id" in result:
        return jsonify({"success": True, "page_id": page_id,
                        "elementor": "enabled" if mode == "builder" else "disabled"})
    return jsonify({"error": str(result)}), 500


@app.route("/restore-elementor-pages", methods=["POST"])
def restore_elementor_pages():
    """Restaura _elementor_edit_mode=builder en todas las pages para recuperar el diseño visual."""
    data = request.json or {}
    page_ids = data.get("page_ids")  # opcional: lista de IDs específicos

    pages = get_all_pages()
    if not isinstance(pages, list):
        return jsonify({"error": "No se pudieron obtener las pages"}), 500

    if page_ids:
        pages = [p for p in pages if p["id"] in page_ids]

    restored, errors = [], []
    for page in pages:
        try:
            r = requests.post(
                f"{WC_URL}/wp-json/wp/v2/pages/{page['id']}",
                headers=jwt_headers(),
                json={"meta": {"_elementor_edit_mode": "builder"}},
                timeout=15
            )
            result = r.json()
            if "id" in result:
                restored.append({"id": page["id"], "title": page.get("title", "")})
                print(f"[RestoreElementor] ✅ {page['id']} — {page.get('title', '')}")
            else:
                errors.append({"id": page["id"], "error": str(result)})
        except Exception as e:
            errors.append({"id": page["id"], "error": str(e)})

    return jsonify({
        "restored": len(restored),
        "errors": len(errors),
        "pages": restored,
        "failed": errors
    })


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


# ─── BATCH OPTIMIZATION (Anthropic Batch API — 50% descuento) ─────────────────

_batch_status = {
    "running": False, "phase": None, "batch_id": None,
    "total": 0, "done": 0, "errors": 0,
    "results": [], "started_at": None, "finished_at": None
}


def get_products_by_category(category_id=None):
    params = {"per_page": 100, "status": "publish", "_fields": "id,name,short_description,slug,categories"}
    if category_id and category_id != "all":
        params["category"] = category_id
    try:
        r = requests.get(f"{WC_URL}/wp-json/wc/v3/products", auth=HTTPBasicAuth(WC_KEY, WC_SECRET), params=params, timeout=30)
        return r.json() if isinstance(r.json(), list) else []
    except Exception:
        return []


def needs_optimization(p):
    name = p.get("name", "")
    desc = p.get("short_description", "")
    return len(name) > 60 or not (130 <= len(desc) <= 160)


def make_product_prompt(p):
    return f"""Eres experto SEO para peptidosysuplementos.mx (tienda de péptidos y suplementos en México).

Optimiza este producto:
- Título (name): máximo 60 caracteres, keyword principal al inicio, sin caracteres especiales
- Descripción corta (short_description): 130-160 caracteres, texto plano sin HTML, keyword + beneficio + CTA

ID: {p['id']}
Nombre actual: {p['name']}
Descripción actual: {p.get('short_description', '')}

Devuelve ÚNICAMENTE JSON válido sin markdown:
{{"id": {p['id']}, "name": "Título optimizado", "short_description": "Descripción optimizada"}}"""


def run_batch_optimize(category_id=None):
    global _batch_status
    _batch_status = {
        "running": True, "phase": "fetching", "batch_id": None,
        "total": 0, "done": 0, "errors": 0,
        "results": [], "started_at": datetime.now().isoformat(), "finished_at": None
    }

    try:
        products = get_products_by_category(category_id)
        pending = [p for p in products if needs_optimization(p)]
        _batch_status["total"] = len(pending)

        if not pending:
            print("[Batch] No hay productos pendientes de optimizar.")
            return

        print(f"[Batch] Enviando {len(pending)} requests al Anthropic Batch API...")
        _batch_status["phase"] = "submitting"

        batch_requests = [
            BatchRequest(
                custom_id=str(p["id"]),
                params=MessageCreateParamsNonStreaming(
                    model="claude-sonnet-4-6",
                    max_tokens=512,
                    messages=[{"role": "user", "content": make_product_prompt(p)}]
                )
            )
            for p in pending
        ]

        batch = client.messages.batches.create(requests=batch_requests)
        _batch_status["batch_id"] = batch.id
        _batch_status["phase"] = "processing"
        print(f"[Batch] Batch enviado: {batch.id} — esperando resultados...")

        # Poll cada 30s hasta que termine
        while True:
            time.sleep(30)
            batch = client.messages.batches.retrieve(batch.id)
            print(f"[Batch] {batch.processing_status} — procesando: {batch.request_counts.processing}/{_batch_status['total']}")
            if batch.processing_status == "ended":
                break

        # Aplicar resultados a WooCommerce
        _batch_status["phase"] = "applying"
        print("[Batch] Aplicando resultados a WooCommerce...")

        for result in client.messages.batches.results(batch.id):
            pid = int(result.custom_id)
            if result.result.type == "succeeded":
                try:
                    text = result.result.message.content[0].text.strip()
                    if text.startswith("```"):
                        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
                    item = json.loads(text)
                    data = {k: item[k] for k in ("name", "short_description") if k in item}
                    r = update_product(pid, data)
                    if r.get("success"):
                        _batch_status["done"] += 1
                        _batch_status["results"].append({"id": pid, "name": item.get("name"), "status": "ok"})
                        print(f"[Batch] ✅ {pid} — {item.get('name')}")
                    else:
                        _batch_status["errors"] += 1
                        _batch_status["results"].append({"id": pid, "status": "error", "error": r.get("error")})
                except Exception as e:
                    _batch_status["errors"] += 1
                    _batch_status["results"].append({"id": pid, "status": "error", "error": str(e)})
            else:
                _batch_status["errors"] += 1
                error_type = result.result.type if hasattr(result.result, "type") else "unknown"
                _batch_status["results"].append({"id": pid, "status": "error", "error": error_type})

    except Exception as e:
        print(f"[Batch] ❌ Error: {e}")
    finally:
        _batch_status["running"] = False
        _batch_status["phase"] = "done"
        _batch_status["finished_at"] = datetime.now().isoformat()
        generate_seo_report()
        print(f"[Batch] Finalizado — {_batch_status['done']} ok, {_batch_status['errors']} errores")


@app.route("/batch-optimize", methods=["POST"])
def batch_optimize():
    if _batch_status["running"]:
        return jsonify({"error": "Ya hay una optimización en proceso", "batch_id": _batch_status.get("batch_id")}), 409
    data = request.json or {}
    category_id = data.get("category_id", "all")
    thread = threading.Thread(target=run_batch_optimize, args=(category_id,), daemon=True)
    thread.start()
    return jsonify({"status": "started", "category_id": category_id, "info": "Usando Anthropic Batch API (50% descuento). Consulta /batch-status para el progreso."})


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
5. FAQ SCHEMA JSON-LD: si el artículo tiene sección FAQ, añade al final del HTML:
   <script type="application/ld+json">
   {{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{{"@type":"Question","name":"Pregunta","acceptedAnswer":{{"@type":"Answer","text":"Respuesta"}}}}]}}
   </script>
   Usa las preguntas y respuestas reales del artículo. Respuestas en texto plano sin HTML.
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


_batch_links_status = {
    "running": False, "phase": None, "batch_id": None,
    "total": 0, "done": 0, "errors": 0,
    "results": [], "started_at": None, "finished_at": None
}


def run_batch_add_links(post_ids):
    global _batch_links_status
    _batch_links_status = {
        "running": True, "phase": "fetching", "batch_id": None,
        "total": len(post_ids), "done": 0, "errors": 0,
        "results": [], "started_at": datetime.now().isoformat(), "finished_at": None
    }
    try:
        # Pre-fetch shared data once
        products = get_products(per_page=30)
        products_list = "\n".join(
            f"- {p['name']} ({WC_URL}/producto/{p['slug']})"
            for p in products if isinstance(p, dict) and "name" in p
        )
        all_posts = get_all_posts_catalog(per_page=100)

        # Pre-fetch each post's content
        posts_data = {}
        for post_id in post_ids:
            post = get_post_content(post_id)
            if "error" in post:
                _batch_links_status["errors"] += 1
                _batch_links_status["results"].append({"post_id": post_id, "status": "error", "error": post["error"]})
                continue
            if not post.get("content"):
                _batch_links_status["errors"] += 1
                _batch_links_status["results"].append({"post_id": post_id, "status": "error", "error": "sin contenido"})
                continue
            posts_data[post_id] = post

        pending = list(posts_data.keys())
        if not pending:
            print("[BatchLinks] No hay posts válidos para procesar.")
            return

        print(f"[BatchLinks] Enviando {len(pending)} requests al Anthropic Batch API...")
        _batch_links_status["phase"] = "submitting"

        batch_requests = []
        for post_id in pending:
            post = posts_data[post_id]
            title = post.get("title", "")
            content = post.get("content", "")
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
            batch_requests.append(
                BatchRequest(
                    custom_id=str(post_id),
                    params=MessageCreateParamsNonStreaming(
                        model="claude-sonnet-4-6",
                        max_tokens=16384,
                        messages=[{"role": "user", "content": prompt}]
                    )
                )
            )

        batch = client.messages.batches.create(requests=batch_requests)
        _batch_links_status["batch_id"] = batch.id
        _batch_links_status["phase"] = "processing"
        print(f"[BatchLinks] Batch enviado: {batch.id} — esperando resultados...")

        while True:
            time.sleep(30)
            batch = client.messages.batches.retrieve(batch.id)
            print(f"[BatchLinks] {batch.processing_status} — procesando: {batch.request_counts.processing}/{len(pending)}")
            if batch.processing_status == "ended":
                break

        _batch_links_status["phase"] = "applying"
        print("[BatchLinks] Aplicando resultados a WordPress...")

        for result in client.messages.batches.results(batch.id):
            post_id = int(result.custom_id)
            post = posts_data.get(post_id, {})
            title = post.get("title", "")
            if result.result.type == "succeeded":
                try:
                    optimized = result.result.message.content[0].text.strip()
                    if optimized.startswith("```"):
                        optimized = optimized.split("\n", 1)[1].rsplit("```", 1)[0].strip()
                    r = update_post(post_id, {"content": optimized})
                    if r.get("success"):
                        _batch_links_status["done"] += 1
                        _batch_links_status["results"].append({"post_id": post_id, "title": title, "status": "ok", "url": r.get("link", "")})
                        print(f"[BatchLinks] ✅ {post_id} — {title}")
                    else:
                        _batch_links_status["errors"] += 1
                        _batch_links_status["results"].append({"post_id": post_id, "title": title, "status": "error", "error": r.get("error", "")})
                except Exception as e:
                    _batch_links_status["errors"] += 1
                    _batch_links_status["results"].append({"post_id": post_id, "title": title, "status": "error", "error": str(e)})
            else:
                _batch_links_status["errors"] += 1
                error_type = result.result.type if hasattr(result.result, "type") else "unknown"
                _batch_links_status["results"].append({"post_id": post_id, "title": title, "status": "error", "error": error_type})
                print(f"[BatchLinks] ❌ {post_id}: {error_type}")

    except Exception as e:
        print(f"[BatchLinks] ❌ Error global: {e}")
    finally:
        _batch_links_status["running"] = False
        _batch_links_status["phase"] = "done"
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
6. FAQ SCHEMA JSON-LD: si el artículo tiene sección FAQ, añade al final del HTML:
   <script type="application/ld+json">
   {{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{{"@type":"Question","name":"Pregunta","acceptedAnswer":{{"@type":"Answer","text":"Respuesta"}}}}]}}
   </script>
   Usa las preguntas y respuestas reales del artículo. Respuestas en texto plano sin HTML.
7. Devuelve ÚNICAMENTE el HTML optimizado completo, sin explicaciones ni markdown extra.

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


@app.route("/optimize-raditech-blog", methods=["POST"])
def optimize_raditech_blog():
    try:
        data = request.json or {}
        post_id = data.get("post_id")
        title = data.get("title", "")
        content = data.get("content", "")
        url = data.get("url", "")

        if not post_id:
            return jsonify({"error": "post_id es requerido"}), 400

        if not content:
            fetched = get_raditech_post_content(post_id)
            if "error" in fetched:
                return jsonify({"error": f"No se pudo obtener el post {post_id}: {fetched['error']}"}), 404
            title = title or fetched.get("title", "")
            content = fetched.get("content", "")
            url = url or fetched.get("link", "")

        all_posts = get_raditech_all_posts_catalog(per_page=100)
        other_posts = [
            p for p in all_posts
            if isinstance(p, dict) and str(p.get("id", "")) != str(post_id)
        ]
        posts_list = "\n".join(
            f"- {p['title']} ({p['link']})"
            for p in other_posts if isinstance(p, dict) and p.get("title")
        )

        pages = get_raditech_pages()
        service_pages = [p for p in pages if isinstance(p, dict) and p.get("title") and p.get("link")]
        pages_list = "\n".join(
            f"- {p['title']} ({p['link']})"
            for p in service_pages
        )

        prompt = f"""Eres un experto en SEO B2B para el sector de tecnología médica en México.
Tienes este artículo de blog en raditech.mx:

TÍTULO: {title}
URL: {url}
POST ID: {post_id}

CONTENIDO ACTUAL (HTML):
{content}

OTROS ARTÍCULOS DEL BLOG (para interlinks):
{posts_list if posts_list else "No hay otros artículos disponibles aún."}

PÁGINAS DE SERVICIOS DE RADITECH (para links internos a servicios):
{pages_list if pages_list else "No hay páginas de servicios disponibles."}

Tu tarea — enriquece el contenido añadiendo de forma NATURAL:

1. INTERLINKS A OTROS BLOGS (2-4 links): enlaza a artículos del blog temáticamente relacionados.
   Formato: <a href="URL_DEL_POST">texto descriptivo</a>

2. LINKS A PÁGINAS DE SERVICIOS (2-3 links): enlaza a páginas de servicios relevantes de raditech.mx.
   Formato: <a href="URL_SERVICIO">nombre del servicio</a>

3. LINKS EXTERNOS DE AUTORIDAD (3-5 links): enlaza a fuentes técnicas reconocidas del sector salud/radiología:
   RSNA (rsna.org), ACR (acr.org), HIMSS (himss.org), PubMed (pubmed.ncbi.nlm.nih.gov),
   HL7 (hl7.org), IHE (ihe.net), SIIM (siim.org). Solo URLs reales y verificables.
   Formato: <a href="URL" target="_blank" rel="noopener noreferrer">texto descriptivo</a>

4. SECCIÓN FAQ al final del artículo (si no existe ya): agrega 3 preguntas frecuentes que haría
   un director médico, jefe de radiología o gerente de TI hospitalario sobre el tema del artículo.
   Formato HTML: <h2>Preguntas frecuentes</h2> seguido de <h3> por pregunta y <p> por respuesta.

5. CTA final (si no existe): termina con un párrafo de cierre con llamada a la acción institucional
   como "Solicita una demostración de VIRA PACS" o "Conoce nuestras soluciones de teleradiología".

6. FAQ SCHEMA JSON-LD: siempre que el artículo tenga (o tú agregues) una sección FAQ,
   añade al final del HTML el siguiente bloque con las preguntas y respuestas reales del artículo:
   <script type="application/ld+json">
   {{
     "@context": "https://schema.org",
     "@type": "FAQPage",
     "mainEntity": [
       {{
         "@type": "Question",
         "name": "Pregunta 1",
         "acceptedAnswer": {{"@type": "Answer", "text": "Respuesta 1"}}
       }}
     ]
   }}
   </script>
   Incluye todas las preguntas de la sección FAQ. Las respuestas deben ser texto plano (sin HTML).
   Este bloque permite que Google muestre rich snippets en los resultados de búsqueda.

REGLAS:
- No inventes posts ni páginas que no estén en las listas anteriores.
- Mantén el tono técnico-institucional B2B, sin lenguaje de ventas agresivo.
- No modifiques el contenido existente, solo agrega los elementos solicitados de forma natural.
- Devuelve ÚNICAMENTE el HTML optimizado completo, sin explicaciones ni markdown extra."""

        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=16384,
            messages=[{"role": "user", "content": prompt}]
        )

        optimized_content = response.content[0].text.strip()
        if optimized_content.startswith("```"):
            optimized_content = optimized_content.split("\n", 1)[1].rsplit("```", 1)[0].strip()

        result = update_raditech_post(post_id, {"content": optimized_content})

        if result.get("success"):
            return jsonify({
                "success": True,
                "post_id": post_id,
                "url": result.get("link", url),
                "interlinks_added": len(other_posts) > 0,
                "service_pages_linked": len(service_pages) > 0,
            })
        return jsonify({"error": result.get("error", "Error al actualizar post")}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/optimize-ptm-blog", methods=["POST"])
def optimize_ptm_blog():
    try:
        data = request.json or {}
        post_id = data.get("post_id")
        title = data.get("title", "")
        content = data.get("content", "")
        url = data.get("url", "")

        if not post_id:
            return jsonify({"error": "post_id es requerido"}), 400

        # Si no se pasó content, lo buscamos directamente de WordPress PTM
        if not content:
            fetched = get_ptm_post_content(post_id)
            if "error" in fetched:
                return jsonify({"error": f"No se pudo obtener el post {post_id}: {fetched['error']}"}), 404
            title = title or fetched.get("title", "")
            content = fetched.get("content", "")
            url = url or fetched.get("link", "")

        # Interlinks: otros posts publicados en grupoptm.com
        all_ptm_posts = get_ptm_all_posts_catalog(per_page=100)
        other_ptm_posts = [
            p for p in all_ptm_posts
            if isinstance(p, dict) and str(p.get("id", "")) != str(post_id)
        ]
        ptm_posts_list = "\n".join(
            f"- {p['title']} ({p['link']})"
            for p in other_ptm_posts if isinstance(p, dict) and p.get("title")
        )

        # Cross-links: productos de peptidosysuplementos.mx (tienda hermana PTM→PYS)
        products = get_products(per_page=30)
        products_list = "\n".join(
            f"- {p['name']} ({WC_URL}/producto/{p['slug']})"
            for p in products if isinstance(p, dict) and "name" in p
        )

        prompt = f"""Eres un experto SEO. Tienes este artículo de blog en grupoptm.com (plataforma de telemedicina especializada en péptidos y salud hormonal):

TÍTULO: {title}
URL: {url}
POST ID: {post_id}

CONTENIDO ACTUAL (HTML):
{content}

OTROS ARTÍCULOS DEL BLOG DE GRUPOPTM.COM (para interlinks):
{ptm_posts_list if ptm_posts_list else "No hay otros artículos disponibles aún."}

PRODUCTOS DE PEPTIDOSYSUPLEMENTOS.MX (farmacia hermana — para cross-links):
{products_list}

Tu tarea — agrega los siguientes links de forma NATURAL dentro del texto existente:
1. INTERLINKS (2-4 links): enlaza a otros artículos del blog de grupoptm.com que sean temáticamente relevantes.
   Formato: <a href="URL_DEL_POST">texto descriptivo</a>
2. CROSS-LINKS A PEPTIDOSYSUPLEMENTOS.MX (2-3 links): enlaza a productos relevantes de la farmacia con contexto clínico natural.
   Usa textos como "disponible en nuestra farmacia", "péptidos certificados", "puedes adquirirlo en peptidosysuplementos.mx".
   Formato: <a href="URL_PRODUCTO" target="_blank">texto descriptivo</a>
3. LINKS EXTERNOS CIENTÍFICOS (3-5 links): enlaza a fuentes de autoridad científica relevantes al tema del artículo
   (PubMed, NIH, Mayo Clinic, NEJM, Examine.com). Solo URLs reales y verificables.
   Formato: <a href="URL" target="_blank" rel="noopener noreferrer">texto descriptivo</a>
4. Asegúrate de que el contenido tenga al menos un H2 y que la conclusión incluya un CTA hacia agendar una consulta médica en grupoptm.com.
5. NO inventes productos ni posts que no estén en las listas anteriores.
6. FAQ SCHEMA JSON-LD: si el artículo tiene sección FAQ, añade al final del HTML:
   <script type="application/ld+json">
   {{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{{"@type":"Question","name":"Pregunta","acceptedAnswer":{{"@type":"Answer","text":"Respuesta"}}}}]}}
   </script>
   Usa las preguntas y respuestas reales del artículo. Respuestas en texto plano sin HTML.
7. Devuelve ÚNICAMENTE el HTML optimizado completo, sin explicaciones ni markdown extra.

Devuelve solo el HTML listo para WordPress."""

        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=16384,
            messages=[{"role": "user", "content": prompt}]
        )

        optimized_content = response.content[0].text.strip()
        if optimized_content.startswith("```"):
            optimized_content = optimized_content.split("\n", 1)[1].rsplit("```", 1)[0].strip()

        result = update_ptm_post(post_id, {"content": optimized_content})

        if result.get("success"):
            return jsonify({
                "success": True,
                "post_id": post_id,
                "url": result.get("link", url),
                "interlinks_added": len(other_ptm_posts) > 0,
                "cross_links_added": len(products) > 0,
            })
        return jsonify({"error": result.get("error", "Error al actualizar post PTM")}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/fix-ptm-related-cards/<int:page_id>", methods=["POST"])
def fix_ptm_related_cards(page_id):
    """
    Wraps naked ptm-card-ico / h3 / p elements in ptm-grid3 with proper <a class="ptm-card"> containers.
    Receives JSON body: {"cards": [{"href": "...", "svg": "...", "title": "...", "desc": "..."}]}
    Finds the existing broken grid and replaces with properly wrapped cards.
    """
    try:
        import re as _re
        data = request.json or {}
        cards = data.get("cards", [])
        if not cards:
            return jsonify({"error": "cards array required"}), 400

        # Get raw content
        r = requests.get(f"{PTM_URL}/wp-json/wp/v2/pages/{page_id}",
                         headers=ptm_jwt_headers(), params={"context": "edit"}, timeout=15)
        p = r.json()
        if "id" not in p:
            return jsonify({"error": str(p)}), 404

        raw = p.get("content", {}).get("raw", "")

        # Build the correct replacement grid
        card_html = ""
        for card in cards:
            svg = card.get("svg", "")
            card_html += (
                f'\n<a class="ptm-card" style="text-decoration:none;display:block;" href="{card["href"]}">'
                f'\n<div class="ptm-card-ico">{svg}</div>'
                f'\n<h3>{card["title"]}</h3>'
                f'\n<p>{card["desc"]}</p>'
                f'\n</a>'
            )

        new_grid = f'<div class="ptm-grid3">{card_html}\n</div>'

        # Find and replace any ptm-grid3 in the related section that has naked card-ico elements
        # Match pattern: ptm-grid3 block where cards have no wrapper (ptm-card-ico directly inside grid)
        pattern = r'<div class="ptm-grid3">\s*(?:<div class="ptm-card-ico">.*?</div>\s*<h3>.*?</h3>\s*<p>.*?</p>\s*)+</div>'
        if not _re.search(pattern, raw, flags=_re.DOTALL):
            return jsonify({"error": "Pattern not found in raw content"}), 404

        updated = _re.sub(pattern, new_grid, raw, count=1, flags=_re.DOTALL)

        # Save (update_ptm_page adds wp:html wrapper)
        result = update_ptm_page(page_id, {"content": updated})
        if result.get("success"):
            return jsonify({"success": True, "page_id": page_id, "url": result.get("link", "")})
        return jsonify({"error": result.get("error")}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/repair-ptm-page/<int:page_id>", methods=["POST"])
def repair_ptm_page(page_id):
    """
    Repara una landing page de grupoptm.com dañada por wpautop:
    - Elimina <br /> dentro de <script> y <style>
    - Elimina <p> wrappers alrededor de <script>
    - Corrige </p> sueltos en estructura FAQ
    - Agrega <span class="pm"> a botones FAQ si falta
    - Guarda con <!-- wp:html --> para prevenir daño futuro
    """
    try:
        import re as _re
        r = requests.get(f"{PTM_URL}/wp-json/wp/v2/pages/{page_id}",
                         headers=ptm_jwt_headers(),
                         params={"context": "edit"}, timeout=15)
        p = r.json()
        if "id" not in p:
            return jsonify({"error": str(p)}), 404

        raw = p.get("content", {}).get("raw", "")
        raw = raw.strip()
        if raw.startswith("<!-- wp:html -->"):
            raw = raw[len("<!-- wp:html -->"):].strip()
        if raw.endswith("<!-- /wp:html -->"):
            raw = raw[:-len("<!-- /wp:html -->")].strip()

        cleaned = strip_wpautop_artifacts(raw)

        # Add <span class="pm"></span> to FAQ buttons if missing
        def add_pm_span(m):
            btn_text = m.group(1)
            if '<span class="pm">' in btn_text:
                return m.group(0)
            return f'<button class="ptm-faq-q">{btn_text} <span class="pm"></span></button>'
        cleaned = _re.sub(r'<button class="ptm-faq-q">(.*?)</button>',
                          add_pm_span, cleaned, flags=_re.DOTALL)

        result = update_ptm_page(page_id, {"content": cleaned})
        if result.get("success"):
            return jsonify({"success": True, "page_id": page_id,
                            "url": result.get("link", ""),
                            "message": "Página reparada: wpautop artifacts eliminados, guardada con wp:html wrapper"})
        return jsonify({"error": result.get("error", "Error desconocido")}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/fix-blog-thumbnails", methods=["POST"])
def fix_blog_thumbnails():
    """
    Habilita la imagen destacada en el bloque wp:latest-posts de la página Blog (ID 22007).
    Agrega displayFeaturedImage:true, featuredImageSizeSlug:medium al bloque.
    """
    import re as _re
    BLOG_PAGE_ID = 22007
    try:
        r = requests.get(
            f"{PTM_URL}/wp-json/wp/v2/pages/{BLOG_PAGE_ID}",
            headers=ptm_jwt_headers(),
            params={"context": "edit"},
            timeout=15
        )
        p = r.json()
        if "id" not in p:
            return jsonify({"error": str(p)}), 404

        raw = p.get("content", {}).get("raw", "")

        def upgrade_latest_posts_block(m):
            attrs_str = m.group(1).strip() if m.group(1) else ""
            try:
                attrs = json.loads(attrs_str) if attrs_str else {}
            except Exception:
                attrs = {}
            attrs["displayFeaturedImage"] = True
            attrs["featuredImageSizeSlug"] = "medium"
            attrs.setdefault("displayPostDate", True)
            attrs.setdefault("displayAuthor", False)
            attrs.setdefault("excerptLength", 20)
            return f"<!-- wp:latest-posts {json.dumps(attrs)} /-->"

        new_raw = _re.sub(
            r'<!-- wp:latest-posts\s*(\{[^}]*\})?\s*/-->',
            upgrade_latest_posts_block,
            raw
        )

        if new_raw == raw:
            return jsonify({"ok": False, "message": "No se encontró bloque wp:latest-posts en la página"}), 404

        upd = requests.post(
            f"{PTM_URL}/wp-json/wp/v2/pages/{BLOG_PAGE_ID}",
            headers={**ptm_jwt_headers(), "Content-Type": "application/json"},
            json={"content": new_raw},
            timeout=20
        )
        if upd.status_code in (200, 201):
            return jsonify({"ok": True, "message": "Thumbnails habilitados en bloque latest-posts", "page_id": BLOG_PAGE_ID})
        return jsonify({"ok": False, "status": upd.status_code, "response": upd.text[:300]}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/delete-ptm-post/<int:post_id>", methods=["DELETE", "POST"])
def delete_ptm_post(post_id):
    try:
        r = requests.delete(
            f"{PTM_URL}/wp-json/wp/v2/posts/{post_id}",
            headers=ptm_jwt_headers(),
            params={"force": True},
            timeout=15
        )
        if r.status_code in (200, 201):
            return jsonify({"ok": True, "deleted": post_id, "result": r.json()})
        return jsonify({"ok": False, "status": r.status_code, "response": r.text[:500]}), r.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/optimize-ptm-page", methods=["POST"])
def optimize_ptm_page():
    """
    Optimiza una landing page de grupoptm.com:
    - NO reescribe la estructura (respeta JS, acordeones, schema JSON-LD)
    - Inserta 3-5 links científicos externos naturalmente en párrafos existentes
    - Agrega interlinks a blogs de grupoptm.com donde sea relevante
    - Actualiza rank_math_title, rank_math_description, rank_math_focus_keyword
    """
    try:
        data = request.json or {}
        page_id = data.get("page_id")
        if not page_id:
            return jsonify({"error": "page_id es requerido"}), 400

        # Obtener contenido actual de la página
        fetched = get_ptm_page_content(page_id)
        if "error" in fetched:
            return jsonify({"error": f"No se pudo obtener la página {page_id}: {fetched['error']}"}), 404

        title = fetched.get("title", "")
        content = fetched.get("content", "")
        url = fetched.get("link", "")

        # Blogs de grupoptm.com para interlinks
        ptm_blogs = get_ptm_all_posts_catalog(per_page=100)
        blogs_list = "\n".join(
            f"- {p['title']} ({p['link']})"
            for p in ptm_blogs if isinstance(p, dict) and p.get("title")
        )

        # Páginas PTM para interlinks entre landings
        ptm_pages = get_ptm_pages()
        other_pages = [
            p for p in ptm_pages
            if isinstance(p, dict) and str(p.get("id", "")) != str(page_id)
        ]
        pages_list = "\n".join(
            f"- {p['title']} ({p['link']})"
            for p in other_pages if isinstance(p, dict) and p.get("title")
        )

        prompt = f"""Eres un experto SEO. Tienes esta landing page de grupoptm.com (plataforma de telemedicina de péptidos):

TÍTULO: {title}
URL: {url}
PAGE ID: {page_id}

CONTENIDO ACTUAL (HTML):
{content}

BLOGS DE GRUPOPTM.COM (para interlinks):
{blogs_list if blogs_list else "No hay blogs aún."}

OTRAS LANDINGS DE GRUPOPTM.COM (para interlinks entre páginas):
{pages_list if pages_list else "No hay otras páginas."}

Tu tarea es MEJORAR el contenido SIN romper la estructura existente:

REGLAS CRÍTICAS — OBLIGATORIAS:
1. NO modifiques ni elimines ningún script JavaScript, acordeón, schema JSON-LD ni estructura de grid/card
2. NO reescribas párrafos completos — solo inserta links dentro del texto existente
3. CONSERVA todos los botones CTA, badges y estilos inline existentes
4. NO toques los links a productos PYS que ya existen

ACCIONES PERMITIDAS:
1. LINKS CIENTÍFICOS EXTERNOS (3-5): Inserta anchors a PubMed, NIH, Mayo Clinic, NEJM, FDA dentro
   de palabras o frases relevantes ya existentes en los párrafos de texto.
   Formato: <a href="URL_REAL" target="_blank" rel="noopener noreferrer">texto existente</a>
   Solo URLs reales y verificables.

2. INTERLINKS A BLOGS PTM (2-3): Inserta links a artículos del blog de grupoptm.com donde el tema
   sea relevante al texto existente.
   Formato: <a href="URL_BLOG">texto existente o frase natural</a>

3. INTERLINKS A OTRAS LANDINGS (1-2): Si hay una landing de grupoptm.com temáticamente relacionada,
   agrega un link natural al final de alguna sección.

4. SEO METADATA: Proporciona los valores optimizados para:
   - rank_math_title (60 chars máx, incluir keyword + "México")
   - rank_math_description (155 chars máx, atractivo y con keyword)
   - rank_math_focus_keyword (keyword principal)

Responde ÚNICAMENTE con JSON válido:
{{
  "content": "HTML completo con los links insertados (misma estructura, solo links añadidos)",
  "rank_math_title": "...",
  "rank_math_description": "...",
  "rank_math_focus_keyword": "..."
}}"""

        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=16384,
            messages=[{"role": "user", "content": prompt}]
        )

        raw = response.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()

        import json as _json
        result_data = _json.loads(raw)

        update_payload = {"content": result_data["content"]}
        if result_data.get("rank_math_title") or result_data.get("rank_math_description"):
            update_payload["meta"] = {
                "rank_math_title": result_data.get("rank_math_title", ""),
                "rank_math_description": result_data.get("rank_math_description", ""),
                "rank_math_focus_keyword": result_data.get("rank_math_focus_keyword", ""),
            }

        result = update_ptm_page(page_id, update_payload)

        if result.get("success"):
            return jsonify({
                "success": True,
                "page_id": page_id,
                "url": result.get("link", url),
                "rank_math_title": result_data.get("rank_math_title", ""),
                "rank_math_focus_keyword": result_data.get("rank_math_focus_keyword", ""),
            })
        return jsonify({"error": result.get("error", "Error al actualizar página PTM")}), 500

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


def fetch_gsc_data(dimension, days=28, limit=10, site_url=None):
    service = get_gsc_service()
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    result = service.searchanalytics().query(
        siteUrl=site_url or GSC_SITE_URL,
        body={
            "startDate": start_date,
            "endDate": end_date,
            "dimensions": [dimension],
            "rowLimit": limit,
            "orderBy": [{"fieldName": "clicks", "sortOrder": "DESCENDING"}]
        }
    ).execute()
    return result.get("rows", [])


def gsc_raditech_top_queries(days=28, limit=10):
    """Top búsquedas de raditech.mx por clicks en GSC."""
    if not GSC_REFRESH_TOKEN:
        return {"error": "GSC no autenticado. Visita /search-console/auth"}
    try:
        rows = fetch_gsc_data("query", days, limit, site_url=RADITECH_GSC_SITE_URL)
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


def gsc_raditech_page_performance(days=28, limit=10):
    """Páginas de raditech.mx con más clicks en GSC."""
    if not GSC_REFRESH_TOKEN:
        return {"error": "GSC no autenticado. Visita /search-console/auth"}
    try:
        rows = fetch_gsc_data("page", days, limit, site_url=RADITECH_GSC_SITE_URL)
        return [
            {
                "page": r["keys"][0].replace("https://raditech.mx", ""),
                "clicks": r.get("clicks", 0),
                "impressions": r.get("impressions", 0),
                "ctr_pct": round(r.get("ctr", 0) * 100, 1),
                "position": round(r.get("position", 0), 1)
            }
            for r in rows[:limit]
        ]
    except Exception as e:
        return {"error": str(e)}


def gsc_raditech_ctr_opportunities(days=28, min_impressions=50, limit=15):
    """Keywords de raditech.mx con CTR bajo — oportunidades de mejora de títulos."""
    if not GSC_REFRESH_TOKEN:
        return {"error": "GSC no autenticado. Visita /search-console/auth"}
    try:
        rows = fetch_gsc_data("query", days, 500, site_url=RADITECH_GSC_SITE_URL)
        opportunities = [
            {
                "query": r["keys"][0],
                "impressions": r.get("impressions", 0),
                "clicks": r.get("clicks", 0),
                "ctr_pct": round(r.get("ctr", 0) * 100, 1),
                "position": round(r.get("position", 0), 1)
            }
            for r in rows
            if r.get("impressions", 0) >= min_impressions and r.get("ctr", 0) < 0.03
        ]
        return sorted(opportunities, key=lambda x: x["impressions"], reverse=True)[:limit]
    except Exception as e:
        return {"error": str(e)}


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
