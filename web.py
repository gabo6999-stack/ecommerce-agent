from flask import Flask, request, jsonify, redirect, session
import anthropic, os, requests, schedule, threading, json, secrets, time, uuid
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


def notify_nexus(action, detail=None, url=None):
    """Reporta una actividad a NEXUS (Centro de Comando). Solo corre si hay NEXUS_URL y NEXUS_KEY."""
    nexus_url = os.environ.get("NEXUS_URL")
    nexus_key = os.environ.get("NEXUS_KEY")
    if not nexus_url or not nexus_key:
        return
    try:
        requests.post(
            f"{nexus_url}/api/ingest",
            json={"agent": "Agente-SEO", "action": action, "detail": detail, "url": url},
            headers={"x-nexus-key": nexus_key},
            timeout=15,
        )
        print(f"[NEXUS] OK actividad reportada: {action}")
    except Exception as e:
        print(f"[NEXUS] No se pudo reportar a NEXUS: {e}")

# ─── Agente de Backlinks (módulo independiente, integración aditiva) ──────────
# Se importa de forma defensiva: si falla, el resto de la app sigue funcionando.
try:
    import backlinks_agent
    BACKLINKS_AVAILABLE = True
except Exception as _bl_err:
    backlinks_agent = None
    BACKLINKS_AVAILABLE = False
    print(f"[Backlinks] módulo no disponible: {_bl_err}")

# ─── Google Search Console config ────────────────────────────────────────────
GSC_CLIENT_ID          = os.environ.get("GOOGLE_CLIENT_ID", "")
GSC_CLIENT_SECRET      = os.environ.get("GOOGLE_CLIENT_SECRET", "")
GSC_REFRESH_TOKEN      = os.environ.get("GOOGLE_REFRESH_TOKEN", "")
GSC_SITE_URL           = os.environ.get("GSC_SITE_URL", "sc-domain:peptidosysuplementos.mx")
GSC_REDIRECT_URI       = os.environ.get("GSC_REDIRECT_URI", "https://web-production-3743c.up.railway.app/search-console/callback")
RADITECH_GSC_REFRESH_TOKEN  = os.environ.get("RADITECH_GSC_REFRESH_TOKEN", "")
RADITECH_GSC_REDIRECT_URI   = os.environ.get("RADITECH_GSC_REDIRECT_URI", "https://web-production-3743c.up.railway.app/search-console/raditech/callback")
PTM_GSC_REFRESH_TOKEN       = os.environ.get("PTM_GSC_REFRESH_TOKEN", "")
PTM_GSC_REDIRECT_URI        = os.environ.get("PTM_GSC_REDIRECT_URI", "https://web-production-3743c.up.railway.app/search-console/ptm/callback")
GSC_SCOPES             = ["https://www.googleapis.com/auth/webmasters.readonly"]

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
PTM_GSC_SITE_URL = os.environ.get("PTM_GSC_SITE_URL", "sc-domain:grupoptm.com")

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


# ─── Funciones Rank Math / Schema para PYS ───────────────────────────────────

def set_pys_rank_math_schema(object_id, schemas: dict):
    """Persiste schemas en PYS vía rankmath/v1/updateSchemas (Rank Math Pro).

    schemas = {"schema-XXXXX": {"@type": "FAQPage", "metadata": {...}, "mainEntity": [...]}}
    """
    try:
        r = requests.post(
            f"{WC_URL}/wp-json/rankmath/v1/updateSchemas",
            headers=jwt_headers(),
            json={"objectID": object_id, "objectType": "post", "schemas": schemas},
            timeout=20,
        )
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def set_pys_rank_math_meta(object_id, meta: dict):
    """Persiste campos rank_math_* en PYS vía rankmath/v1/updateMeta."""
    rank_math_meta = {k: v for k, v in (meta or {}).items() if k.startswith("rank_math")}
    if not rank_math_meta:
        return {"error": "no rank_math fields"}
    try:
        r = requests.post(
            f"{WC_URL}/wp-json/rankmath/v1/updateMeta",
            headers=jwt_headers(),
            json={"objectID": object_id, "objectType": "post", "meta": rank_math_meta},
            timeout=20,
        )
        return r.json()
    except Exception as e:
        return {"error": str(e)}


# ─── Funciones WordPress de Raditech ─────────────────────────────────────────

def set_raditech_rank_math_meta(object_id, meta):
    """Persiste campos rank_math_* en raditech vía el endpoint propio de Rank Math.

    IMPORTANTE: el campo `meta` del REST core (/wp/v2/posts|pages) NO persiste
    rank_math_* en raditech. El POST devuelve 200 con el objeto, pero Rank Math
    1.0.271.1 no registra esos meta para REST y los ignora silenciosamente. El
    único método que persiste de inmediato es rankmath/v1/updateMeta.
    Verificado el 2026-06-14 contra el HTML renderizado anónimo. objectType es
    siempre "post" (las páginas también son posts en WP). Ref: raditech_seo_fix5.py.
    """
    rank_math_meta = {k: v for k, v in (meta or {}).items() if k.startswith("rank_math")}
    if not rank_math_meta:
        return {"skipped": True}
    try:
        oid = int(object_id)
    except (TypeError, ValueError):
        oid = object_id
    try:
        r = requests.post(
            f"{RADITECH_URL}/wp-json/rankmath/v1/updateMeta",
            headers=raditech_jwt_headers(),
            json={"objectID": oid, "objectType": "post", "meta": rank_math_meta},
            timeout=20,
        )
        return {"status": r.status_code, "body": r.text[:200]}
    except Exception as e:
        return {"error": str(e)}


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
                         headers=raditech_jwt_headers(),
                         params={"context": "edit"}, timeout=15)
        p = r.json()
        if "id" not in p:
            return {"error": str(p)}
        meta = p.get("meta", {})
        return {
            "id": p["id"],
            "title": p.get("title", {}).get("rendered", ""),
            "slug": p.get("slug", ""),
            "link": p.get("link", ""),
            "content": p.get("content", {}).get("rendered", ""),
            "categories": p.get("categories", []),
            "featured_media": p.get("featured_media", 0),
            "rank_math_title": meta.get("rank_math_title", ""),
            "rank_math_description": meta.get("rank_math_description", ""),
            "rank_math_focus_keyword": meta.get("rank_math_focus_keyword", ""),
        }
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
        r = requests.post(f"{RADITECH_URL}/wp-json/wp/v2/posts",
                          json=data, headers=raditech_jwt_headers(), timeout=30)
        result = r.json()
        if "id" not in result:
            return {"error": str(result)}
        # rank_math_* no persiste vía el campo `meta` del REST core en raditech;
        # se escribe con el endpoint propio de Rank Math.
        if meta_description:
            set_raditech_rank_math_meta(result["id"], {"rank_math_description": meta_description})
        return {"success": True, "id": result["id"],
                "link": result.get("link", ""), "status": result.get("status")}
    except Exception as e:
        return {"error": str(e)}


def update_raditech_post(post_id, data):
    try:
        # Los rank_math_* no persisten vía el campo `meta` del REST core en
        # raditech: se separan y se escriben con el endpoint propio de Rank Math.
        data = dict(data)
        rank_math_meta = {}
        meta = data.get("meta")
        if isinstance(meta, dict):
            rank_math_meta = {k: v for k, v in meta.items() if k.startswith("rank_math")}
            remaining = {k: v for k, v in meta.items() if not k.startswith("rank_math")}
            if remaining:
                data["meta"] = remaining
            else:
                data.pop("meta", None)
        result = {}
        if data:
            r = requests.post(f"{RADITECH_URL}/wp-json/wp/v2/posts/{post_id}",
                              headers=raditech_jwt_headers(), json=data, timeout=30)
            result = r.json()
            if "id" not in result:
                return {"error": str(result)}
        if rank_math_meta:
            set_raditech_rank_math_meta(post_id, rank_math_meta)
        return {"success": True, "id": post_id, "link": result.get("link", "")}
    except Exception as e:
        return {"error": str(e)}


def get_or_create_raditech_category(name: str, slug: str = None):
    try:
        slug = slug or name.lower().replace(" ", "-")
        search = requests.get(
            f"{RADITECH_URL}/wp-json/wp/v2/categories",
            headers=raditech_jwt_headers(),
            params={"search": name},
            timeout=10
        )
        results = search.json()
        if results:
            return {"id": results[0]["id"], "name": results[0]["name"], "created": False}
        create = requests.post(
            f"{RADITECH_URL}/wp-json/wp/v2/categories",
            headers=raditech_jwt_headers(),
            json={"name": name, "slug": slug},
            timeout=10
        )
        create.raise_for_status()
        cat = create.json()
        return {"id": cat["id"], "name": cat["name"], "created": True}
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
        # Los rank_math_* no persisten vía el campo `meta` del REST core en
        # raditech: se separan y se escriben con el endpoint propio de Rank Math.
        data = dict(data)
        rank_math_meta = {}
        meta = data.get("meta")
        if isinstance(meta, dict):
            rank_math_meta = {k: v for k, v in meta.items() if k.startswith("rank_math")}
            remaining = {k: v for k, v in meta.items() if not k.startswith("rank_math")}
            if remaining:
                data["meta"] = remaining
            else:
                data.pop("meta", None)
        result = {}
        if data:
            r = requests.post(f"{RADITECH_URL}/wp-json/wp/v2/pages/{page_id}",
                              headers=raditech_jwt_headers(), json=data, timeout=30)
            result = r.json()
            if "id" not in result:
                return {"error": str(result)}
        if rank_math_meta:
            set_raditech_rank_math_meta(page_id, rank_math_meta)
        return {"success": True, "id": page_id, "link": result.get("link", "")}
    except Exception as e:
        return {"error": str(e)}


def create_raditech_page(title, content, slug="", seo_title="", meta_description="", focus_keyword="", status="publish"):
    try:
        data = {
            "title": title,
            "content": content,
            "slug": slug,
            "status": status,
        }
        r = requests.post(f"{RADITECH_URL}/wp-json/wp/v2/pages",
                          headers=raditech_jwt_headers(), json=data, timeout=30)
        result = r.json()
        if "id" not in result:
            return {"error": str(result)}
        page_id = result["id"]
        # rank_math_* se persiste vía el endpoint propio de Rank Math; el campo
        # `meta` del REST core no lo registra en raditech (se ignora en silencio).
        meta = {}
        if seo_title:
            meta["rank_math_title"] = seo_title
        if meta_description:
            meta["rank_math_description"] = meta_description
        if focus_keyword:
            meta["rank_math_focus_keyword"] = focus_keyword
        if meta:
            set_raditech_rank_math_meta(page_id, meta)
        return {"success": True, "id": page_id, "link": result.get("link", ""), "status": result.get("status")}
    except Exception as e:
        return {"error": str(e)}


def delete_raditech_page(page_id, force=True):
    try:
        r = requests.delete(
            f"{RADITECH_URL}/wp-json/wp/v2/pages/{page_id}",
            headers=raditech_jwt_headers(),
            params={"force": force},
            timeout=15
        )
        if r.status_code in (200, 201):
            return {"success": True, "deleted": page_id}
        return {"error": r.text[:300], "status": r.status_code}
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

def set_pys_rank_math_meta(object_id, meta):
    """Persiste campos rank_math_* en PYS (peptidosysuplementos.mx) vía el endpoint
    propio de Rank Math.

    Mismo bug que raditech: el campo `meta` del REST core (/wp/v2/posts|pages) NO
    persiste rank_math_* (Rank Math no los registra para REST; el POST devuelve 200
    pero los ignora en silencio). Verificado el 2026-06-14 contra el HTML renderizado
    anónimo. objectType siempre "post" (las páginas también son posts en WP).
    NOTA: esto aplica a posts/pages vía wp/v2. Los PRODUCTOS vía wc/v3 usan
    `meta_data` (HTTPBasicAuth), que SÍ persiste y NO se toca.
    """
    rank_math_meta = {k: v for k, v in (meta or {}).items() if k.startswith("rank_math")}
    if not rank_math_meta:
        return {"skipped": True}
    try:
        oid = int(object_id)
    except (TypeError, ValueError):
        oid = object_id
    try:
        r = requests.post(
            f"{WC_URL}/wp-json/rankmath/v1/updateMeta",
            headers=jwt_headers(),
            json={"objectID": oid, "objectType": "post", "meta": rank_math_meta},
            timeout=20,
        )
        return {"status": r.status_code, "body": r.text[:200]}
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
        r = requests.post(url, json=data, headers=jwt_headers(), timeout=30)
        result = r.json()
        if "id" not in result:
            return {"error": str(result)}
        # rank_math_* no persiste vía el campo `meta` del REST core; se escribe
        # con el endpoint propio de Rank Math.
        if meta_description:
            set_pys_rank_math_meta(result["id"], {"rank_math_description": meta_description})
        return {"success": True, "id": result["id"], "link": result.get("link", ""), "status": result.get("status")}
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
        # Los rank_math_* no persisten vía el campo `meta` del REST core en PYS:
        # se separan y se escriben con el endpoint propio de Rank Math. Otros meta
        # (p. ej. _elementor_edit_mode) sí persisten por REST y se conservan.
        data = dict(data)
        rank_math_meta = {}
        meta = data.get("meta")
        if isinstance(meta, dict):
            rank_math_meta = {k: v for k, v in meta.items() if k.startswith("rank_math")}
            remaining = {k: v for k, v in meta.items() if not k.startswith("rank_math")}
            if remaining:
                data["meta"] = remaining
            else:
                data.pop("meta", None)
        result = {}
        if data:
            r = requests.post(f"{WC_URL}/wp-json/wp/v2/pages/{page_id}",
                              headers=jwt_headers(), json=data, timeout=30)
            result = r.json()
            if "id" not in result:
                return {"error": str(result)}
        if rank_math_meta:
            set_pys_rank_math_meta(page_id, rank_math_meta)
        return {"success": True, "id": page_id, "link": result.get("link", "")}
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


def get_orders(status=None, customer_email=None, limit=20, after=None, before=None):
    try:
        params = {"per_page": min(int(limit), 100)}
        if status:
            params["status"] = status
        if customer_email:
            params["search"] = customer_email
        if after:
            params["after"] = after
        if before:
            params["before"] = before
        r = requests.get(
            f"{WC_URL}/wp-json/wc/v3/orders",
            auth=HTTPBasicAuth(WC_KEY, WC_SECRET),
            params=params,
            timeout=30
        )
        r.raise_for_status()
        orders = r.json()
        if not isinstance(orders, list):
            return {"error": str(orders)}
        return [
            {
                "id": o["id"],
                "status": o["status"],
                "date_created": o["date_created"],
                "total": o["total"],
                "currency": o["currency"],
                "customer_email": o["billing"].get("email"),
                "customer_name": f"{o['billing'].get('first_name','')} {o['billing'].get('last_name','')}".strip(),
                "items": [{"name": i["name"], "quantity": i["quantity"], "total": i["total"]} for i in o["line_items"]],
            }
            for o in orders
        ]
    except Exception as e:
        return {"error": str(e)}


def get_sales_report(period="month", date_min=None, date_max=None):
    try:
        params = {"period": period}
        if date_min:
            params["date_min"] = date_min
        if date_max:
            params["date_max"] = date_max
        r = requests.get(
            f"{WC_URL}/wp-json/wc/v3/reports/sales",
            auth=HTTPBasicAuth(WC_KEY, WC_SECRET),
            params=params,
            timeout=30
        )
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def get_top_sellers(period="month", limit=10):
    try:
        params = {"period": period, "per_page": min(int(limit), 100)}
        r = requests.get(
            f"{WC_URL}/wp-json/wc/v3/reports/top_sellers",
            auth=HTTPBasicAuth(WC_KEY, WC_SECRET),
            params=params,
            timeout=30
        )
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def compare_mexico_prices(query, limit=5):
    try:
        r = requests.get(
            "https://api.mercadolibre.com/sites/MLM/search",
            params={"q": query, "limit": limit, "condition": "new"},
            timeout=15,
        )
        r.raise_for_status()
        data = r.json()
        results = [
            {
                "title": item["title"],
                "price_mxn": item["price"],
                "seller": item.get("seller", {}).get("nickname", ""),
                "sold_quantity": item.get("sold_quantity", 0),
                "url": item["permalink"],
            }
            for item in data.get("results", [])[:int(limit)]
        ]
        return {"query": query, "market": "MercadoLibre Mexico", "listings": results}
    except Exception as e:
        return {"error": str(e)}


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
        if "focus_keyword" in data:
            meta_updates["rank_math_focus_keyword"] = data["focus_keyword"]
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
        # Los rank_math_* no persisten vía el campo `meta` del REST core en PYS:
        # se separan y se escriben con el endpoint propio de Rank Math.
        data = dict(data)
        rank_math_meta = {}
        meta = data.get("meta")
        if isinstance(meta, dict):
            rank_math_meta = {k: v for k, v in meta.items() if k.startswith("rank_math")}
            remaining = {k: v for k, v in meta.items() if not k.startswith("rank_math")}
            if remaining:
                data["meta"] = remaining
            else:
                data.pop("meta", None)
        result = {}
        if data:
            r = requests.post(
                f"{WC_URL}/wp-json/wp/v2/posts/{post_id}",
                headers=jwt_headers(),
                json=data,
                timeout=30
            )
            result = r.json()
            if "id" not in result:
                return {"error": str(result)}
        if rank_math_meta:
            set_pys_rank_math_meta(post_id, rank_math_meta)
        return {"success": True, "id": post_id, "link": result.get("link", "")}
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
    date_published = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S+00:00")

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
            "datePublished": date_published,
            "dateModified": date_published,
            "author": {
                "@type": "Person",
                "name": "Equipo Péptidos y Suplementos",
                "url": WC_URL
            },
            "publisher": {
                "@type": "Organization",
                "name": "Péptidos y Suplementos MX",
                "url": WC_URL,
                "logo": {"@type": "ImageObject", "url": f"{WC_URL}/wp-content/uploads/logo.png"}
            },
            "description": "",
            "mainEntityOfPage": {"@type": "WebPage", "@id": url}
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

PALABRA PROHIBIDA — NUNCA usar en ningún contenido, título, descripción, blog, página, meta tag ni en ninguna comunicación:
- "farmacia" (ni en singular, ni plural, ni con mayúscula, ni como parte de otra palabra)
Sustituto obligatorio: "Tienda en línea"

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
- Titulo del blog: maximo 60 caracteres (igual que productos)
- Estructura con H2 y H3 (un H2 cada ~300 palabras aprox.)
- Incluir minimo 5 links externos a fuentes de autoridad (NEJM, FDA, PubMed, Mayo Clinic, etc.)
- Incluir minimo 8 links internos a productos de la tienda
- Meta descripcion entre 150-160 caracteres
- Slug en minusculas con guiones, maximo 5 palabras
- Keyword principal en titulo, primer parrafo, al menos un H2 y en la conclusion
- Contenido en HTML valido para WordPress (usar <h2>, <h3>, <p>, <strong>, <a href="">, <ul>, <li>)
- Incluir seccion de FAQ al final con minimo 4 preguntas en formato <h3>¿Pregunta?</h3><p>Respuesta</p>

FLUJO PARA ARTICULOS:
1. Antes de escribir: usa gsc_keyword_cannibalization para verificar que no existe ya una pagina rankeando por la misma keyword
2. Genera el articulo completo en HTML (con seccion FAQ al final)
3. Muestra titulo, meta descripcion, slug y preview del contenido
4. Pide confirmacion antes de publicar
5. Usa create_post para publicar en WordPress
6. Aplica add_schema_markup(post_id, "Article") — y si el articulo tiene FAQs, aplica tambien add_schema_markup(post_id, "FAQPage")
7. Llama a gsc_request_indexing con la URL del articulo publicado
8. Confirma con el link del articulo publicado

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

ANÁLISIS DE VENTAS Y SOPORTE (PYS):
- get_orders: busca órdenes por estado, email del cliente o rango de fechas — úsala para soporte al cliente o análisis de ventas
- get_sales_report: ingresos totales, número de órdenes y ticket promedio por período (week/month/last_month/year)
- get_top_sellers: productos más vendidos por unidades — úsala para priorizar stock, campañas o interlinks
- compare_mexico_prices: compara precios de PYS vs MercadoLibre México — úsala cuando el usuario pregunte si los precios son competitivos

Siempre usa las herramientas para obtener datos reales antes de proponer cambios.
Pide confirmacion antes de aplicar cualquier cambio.
Responde siempre en espanol.

GRUPO PTM — SEGUNDO SITIO (grupoptm.com):
grupoptm.com (PTM Novo) es una empresa INDEPENDIENTE de PYS, NO un sitio hermano ni parte del mismo negocio. Es plataforma de telemedicina que cobra únicamente la consulta médica; queda fuera de la venta de producto. NO existe embudo entre PTM y PYS.
PTM es la plataforma de telemedicina: consultas médicas especializadas en péptidos.
Audiencia: pacientes mexicanos buscando orientación médica sobre péptidos, GLP-1, hormonas y longevidad.
Tono: médico-confiable, empático, orientado al paciente — NO lenguaje técnico de laboratorio.
Tienes acceso completo al sitio para gestionar y publicar contenido (gestión SEO). PROHIBIDO crear CTAs, banners o links que crucen pacientes entre PTM y PYS en cualquier dirección — eso rompe la defensa legal de PTM como "solo plataforma".

REGLAS SEO PARA BLOGS DE PTM:
- Titulo: maximo 60 caracteres, keyword al inicio
- Minimo 800 palabras, estructura H2/H3
- Meta description: 150-160 caracteres con keyword + beneficio + CTA ("Agenda tu consulta")
- Slug en minusculas con guiones, maximo 5 palabras
- Keyword principal en titulo, primer parrafo, al menos un H2 y en conclusion
- Minimo 3 links internos a otras paginas/blogs de PTM (usar get_ptm_all_posts_catalog)
- Minimo 2 links externos a fuentes medicas de autoridad (PubMed, NIH, Mayo Clinic)
- Incluir seccion FAQ al final con minimo 3 preguntas <h3>/<p>

REGLAS SEO PARA LANDING PAGES DE PTM:
- Minimo 600 palabras de texto visible
- seo_title: maximo 60 chars — "Tratamiento con [Peptido] en Mexico | PTM"
- meta_description: 150-160 chars — condicion + diferenciador + CTA
- Minimo 4 links internos a otras paginas de PTM
- Seccion FAQ con minimo 4 preguntas

FLUJO PARA BLOGS DE PTM:
1. Genera el articulo completo en HTML con seccion FAQ al final
2. Muestra titulo, meta descripcion, slug y preview
3. Pide confirmacion antes de publicar
4. Usa create_ptm_post para publicar
5. Usa update_ptm_post para agregar seo_title y meta_description via Rank Math
6. Confirma con el link publicado

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

HERRAMIENTAS GSC DE PTM (grupoptm.com):
- gsc_ptm_top_queries: keywords que traen tráfico a grupoptm.com (clicks, impresiones, CTR, posición)
- gsc_ptm_page_performance: páginas de grupoptm.com con mejor rendimiento en Google
- gsc_ptm_ctr_opportunities: keywords con muchas impresiones pero CTR bajo en grupoptm.com

MAPA DE PÁGINAS DE PTM (landing pages SEO):
- Pérdida de peso / GLP-1 / semaglutida / tirzepatida / Ozempic
  → https://grupoptm.com/perdida-de-peso
- Longevidad / anti-aging / Epithalon / GHK-Cu / MOTS-c
  → https://grupoptm.com/longevidad-antiaging
- Rendimiento / recuperación deportiva / BPC-157 / TB-500 / IGF-1
  → https://grupoptm.com/rendimiento-recuperacion
- Salud hormonal / TRT / testosterona / péptidos hormonales
  → https://grupoptm.com/salud-hormonal

SEPARACIÓN PTM / PYS (regla absoluta):
- NUNCA agregues CTAs, banners ni links que manden pacientes de PTM hacia productos de PYS, ni de PYS hacia consultas de PTM. Son empresas independientes.
- El cross-linking entre PTM y PYS está PROHIBIDO: embudar paciente PTM → producto PYS rompe la defensa legal de PTM como "solo plataforma".
- El interlinking interno (PTM→PTM y PYS→PYS) sí es bienvenido; el cruce entre los dos sitios no.

RADITECH — TERCER SITIO (raditech.mx):
Empresa mexicana de software médico con 20+ años, 400+ clientes, 40,000+ estudios/mes.
Productos: VIRA PACS-RIS, Teleradiología 24/7, Medsi HIS, Monitores médicos de diagnóstico, X-Card.
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
- update_raditech_page: actualiza título, SEO title, meta description, slug, status o contenido de una página
- create_raditech_page: crea una nueva página en raditech.mx con contenido Gutenberg y metadatos SEO completos
- delete_raditech_page: elimina una página de Raditech permanentemente (force=true)

HERRAMIENTAS GSC DE RADITECH:
- gsc_raditech_top_queries: keywords que traen tráfico a raditech.mx (clicks, impresiones, CTR, posición)
- gsc_raditech_page_performance: páginas de raditech.mx con mejor rendimiento en Google
- gsc_raditech_ctr_opportunities: keywords con muchas impresiones pero CTR bajo en raditech.mx
- gsc_request_indexing: solicita indexación de una URL a Google Search Console

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DISEÑO VISUAL RADITECH — ESTÁNDAR OBLIGATORIO PARA TODAS LAS LANDINGS Y BLOGS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Cuando crees una landing con create_raditech_page, USA SIEMPRE este HTML embebido en <!-- wp:html -->.
Este diseño replica el estándar visual actual de raditech.mx basado en las páginas ya publicadas.

PALETA DE COLORES OBLIGATORIA:
  --rt-bg: #061423          (fondo principal)
  --rt-bg-2: #0a1d31        (fondo alternativo)
  --rt-card: #0d2138        (fondo cards)
  --rt-card-2: #132c48      (fondo cards alt)
  --rt-orange: #f09a37      (naranja principal)
  --rt-orange-2: #ffb65c    (naranja claro / hover)
  --rt-muted: #b8c6d8       (texto secundario)
  --rt-text: #eaf1f8        (texto principal)

CSS BASE OBLIGATORIO (namespace .rt-page — cambia el sufijo por slug, ej: .rt-his, .rt-tele):
  - Fondo: radial-gradient(circle at 82% 12%, rgba(240,154,55,.13), transparent 26%), linear-gradient(135deg, #04111d, #07192b, #091c2f)
  - Grid de fondo: líneas 1px rgba(255,255,255,.026) cada 42px con mask-image hacia abajo
  - Botón primario (.rtp-btn.primary): pill (border-radius:999px), bg linear-gradient(var(--rt-orange), var(--rt-orange-2)), color:#071423, font-weight:900, min-height:52px, shine animation en ::after
  - Botón ghost (.rtp-btn.secondary): pill, border 1px rgba(255,255,255,.16), bg rgba(255,255,255,.06), backdrop-filter:blur(14px), color:#fff
  - Eyebrow badge (.rtp-eyebrow): pill con punto naranja pulsante a la izquierda, border rgba(240,154,55,.28), bg rgba(240,154,55,.12), texto naranja-2, font-weight:900, uppercase
  - Headings H1: font-size clamp(46px,7vw,92px), font-weight:950, letter-spacing:-0.07em, line-height:0.92 — con span en gradient naranja→naranja-2→blanco via background-clip:text
  - Headings H2: font-size clamp(32px,4vw,52px), font-weight:950, letter-spacing:-0.05em
  - Cards: background linear-gradient(180deg, #132c48, #0d2138), border 1px rgba(255,255,255,.08), border-radius:20-30px, box-shadow 0 28px 80px rgba(0,0,0,.34)

ESTRUCTURA OBLIGATORIA DE SECCIONES (en este orden exacto):

  1. HERO (min-height:720px, padding:76px 0 88px)
     - Izquierda: logo Raditech small (opcional) → eyebrow badge → H1 enorme con span naranja → párrafo muted → 2 botones pill (primary + secondary)
     - Derecha: imagen principal en card glass (border-radius:36px, box-shadow glow naranja) con animación float + card flotante inferior izquierda con número grande naranja + texto muted

  2. QUICK NAV BOX (margin-top:-52px, z-index:5)
     - Grid 2 partes separadas por 1px rgba(255,255,255,.08):
       * Izquierda (0.78fr): título bold grande + descripción muted
       * Derecha: grid 4 columnas con links — cada uno con título bold + sublink naranja con "→"

  3. STATS ROW (padding:34px 0 0)
     - Grid 4 columnas: cada stat tiene número grande naranja (font-size:2.6rem, weight:950) + label muted uppercase + descripción small
     - Stats típicas: "Web / BASE FLEXIBLE", "24/7 / SOPORTE REMOTO", "365 / DÍAS AL AÑO", "∞ / ALMACENAMIENTO"

  4. SECCIÓN PRINCIPAL OSCURA (padding:100px 0, background radial-gradient oscuro)
     - H2 enorme izquierda (0.9fr) + párrafo descriptivo derecha (1.1fr) + descripción larga
     - Abajo: grid 5 cards numeradas 01→05, cada una con badge cuadrado naranja + h3 + p muted

  5. HERRAMIENTAS / TABS (padding:100px 0)
     - Eyebrow badge + H2 grande + párrafo introducción
     - Grid 2 columnas: izquierda lista de tabs con botón activo (indicator naranja) | derecha panel con imagen + h3 + p + lista de checks con círculo naranja
     - Tabs: Visualización, Control de tiempos, Entrega digital, Usuarios y soporte (o equivalentes del servicio)

  6. PERFILES DE AUDIENCIA / VALOR (padding:100px 0, background oscuro)
     - Eyebrow badge + H2 izquierda + descripción derecha
     - Grid 4 cards: cada una con círculo naranja + abreviatura (RX/PA/JA/TI o equivalente) + h3 + p muted

  7. FLUJO / ESTUDIO DIGITAL (padding:100px 0)
     - Grid 2 columnas: imagen izquierda (card glass) | eyebrow + H2 + párrafo + grid 2x2 de feature-chips (fondo card, border naranja, ícono + texto)
     - Feature chips típicos: Visualizador avanzado web, Semáforo de tiempos, Envío correo/WhatsApp, Soporte remoto 24/7

  8. CTA FINAL (padding:80px 0, background muy oscuro)
     - Grid 2 columnas: H2 enorme bold + párrafo muted | 2 botones apilados (WhatsApp primary + Cotizar secondary)
     - Texto: "Sin costo de instalación, capacitación y mantenimiento."

  9. SERVICIOS RELACIONADOS (padding:80px 0)
     - Eyebrow + H2 "Servicios relacionados"
     - Grid 3 cards con links internos a otras páginas de Raditech (ver mapa abajo)
     - SIN sección de footer-links — nunca agregar barra de links al pie

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PROTOCOLO SEO COMPLETO PARA RADITECH (aplicar en TODA página o blog)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

METADATOS (siempre configurar vía update_raditech_page o create_raditech_page):
  - seo_title: máx 55 chars — "Keyword Principal | Raditech México"
  - meta_description: 150-160 chars — keyword + diferenciador + CTA ("Cotiza" / "Solicita demo")
  - focus_keyword: keyword sin marca (ej: "sistema pacs ris", "teleradiologia mexico")
  - slug: minúsculas con guiones, sin artículos innecesarios, máx 5 palabras

LONGITUD DE CONTENIDO:
  - Landings: mínimo 1,500 palabras / ~9,000 caracteres de texto visible
  - Blogs: mínimo 1,200 palabras / ~7,500 caracteres
  - Cada sección debe tener párrafos descriptivos, no solo títulos con bullets vacíos

LINKS INTERNOS OBLIGATORIOS (mínimo 4 por página, usar estas URLs exactas):
  Mapa de páginas publicadas de Raditech:
  - Teleradiología general:        https://raditech.mx/servicio-teleradiologia/
  - Teleradiología alta esp.:      https://raditech.mx/teleradiologia-alta-especialidad/
  - Sistema PACS-RIS:              https://raditech.mx/sistema-pacs-ris/
  - Monitores médicos radiología:  https://raditech.mx/monitores-medicos-radiologia/
  - Portal X-Card:                 https://raditech.mx/portal-x-card/
  - Contacto:                      https://raditech.mx/contacto/
  - Blog:                          https://raditech.mx/blog/
  IMPORTANTE: Nunca usar URLs viejas (/pacs-ris/, /monitores-grado-medico/, /x-card/, etc.)

LINKS EXTERNOS DE AUTORIDAD (mínimo 3 por página, target="_blank" rel="noopener noreferrer"):
  - DICOM standard:   https://www.dicomstandard.org/
  - HL7 standard:     https://www.hl7.org/
  - RSNA:             https://www.rsna.org/
  - ACR:              https://www.acr.org/
  - HIMSS:            https://www.himss.org/
  - Colegio Mexicano de Radiología: https://www.cmr.org.mx/
  - COFEPRIS:         https://www.cofepris.gob.mx/
  - AAPM:             https://www.aapm.org/
  - PubMed (artículo relevante al tema cuando aplique)

FAQs Y SCHEMA (obligatorio en toda página y blog):
  - Mínimo 6 preguntas FAQ en tarjetas visuales dentro de la página
  - Mínimo 2 de las FAQs deben contener links internos o externos dentro de la respuesta
  - Siempre incluir script FAQPage JSON-LD al final del HTML:
    {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[...]}
  - Respuestas del schema: mínimo 30 palabras cada una, sin HTML (solo texto plano)
  - Para blogs largos agregar también Article schema con author, datePublished, description

SECCIÓN SERVICIOS RELACIONADOS (obligatoria, siempre al final antes del cierre):
  - 3 cards con links a otras páginas de Raditech temáticamente relacionadas
  - Cada card: ícono emoji + título + descripción 1-2 líneas
  - Nunca incluir la propia página en los relacionados
  - No incluir sección de "footer-links" — está eliminada del template

WHATSAPP CTA: siempre https://wa.me/525537959441
INDEXACIÓN: después de publicar cualquier página o blog, llamar a gsc_request_indexing con la URL

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PARÁMETROS PARA BLOGS DE RADITECH
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  - Mínimo 1,200 palabras, estructura H2/H3 (H2 cada ~300 palabras)
  - Audiencia: directores médicos, jefes de radiología, gerentes TI hospitalario
  - Tono: técnico-institucional B2B, orientado a ROI — NO lenguaje B2C ni wellness
  - Categorías disponibles: Teleradiología (27), Diagnóstico por Imagen (28), Gestión Hospitalaria (29), Tecnología Médica (30), Medicina General (31)
  - Autor público: "Dr. Antonio Gavito Hernández - Médico Radiólogo"
  - Contenido en HTML válido: <h2>, <h3>, <p>, <strong>, <a href="">, <ul>, <li>
  - Incluir mínimo 4 links internos a páginas de Raditech (usar mapa de URLs de arriba)
  - Incluir mínimo 3 links externos de autoridad (lista de arriba)
  - Incluir FAQ section al final del blog con mínimo 4 preguntas + FAQPage schema
  - Llamar a /optimize-raditech-blog después de publicar

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ESTADO DE MIGRACIÓN (páginas ya completadas — NO recrear)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ✅ /servicio-teleradiologia/           (ID 871)
  ✅ /teleradiologia-alta-especialidad/  (ID 874)
  ✅ /monitores-medicos-radiologia/      (ID 879)
  ✅ /portal-x-card/                     (ID 881)
  ✅ /sistema-pacs-ris/                  (ID 883)
  ⏳ /sistema-his-medsi/                 (pendiente crear)
  ⏳ /teleradiologia-resonancia-cardiovascular/ (pendiente crear)
  ⏳ /teleradiologia-tomografia-cardiaca/ (pendiente crear)

REGLAS GENERALES DE RADITECH:
  - NUNCA borrar página vieja sin confirmar que la nueva está publicada y con status=publish
  - NUNCA mencionar "Grupo PTM" en ninguna página — el rebranding es "Raditech"
  - NUNCA incluir sección de footer-links al pie de las páginas
  - Links internos: usar SIEMPRE las nuevas URLs del mapa, nunca las URLs viejas
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
    {
        "name": "gsc_ptm_top_queries",
        "description": "Google Search Console: top keywords que traen tráfico a grupoptm.com (clicks, impresiones, CTR, posición).",
        "input_schema": {
            "type": "object",
            "properties": {
                "days": {"type": "integer", "default": 28},
                "limit": {"type": "integer", "default": 10}
            }
        }
    },
    {
        "name": "gsc_ptm_page_performance",
        "description": "Google Search Console: páginas de grupoptm.com con mejor rendimiento orgánico.",
        "input_schema": {
            "type": "object",
            "properties": {
                "days": {"type": "integer", "default": 28},
                "limit": {"type": "integer", "default": 10}
            }
        }
    },
    {
        "name": "gsc_ptm_ctr_opportunities",
        "description": "Google Search Console: keywords de grupoptm.com con muchas impresiones pero CTR bajo — oportunidades para mejorar títulos y meta descriptions.",
        "input_schema": {
            "type": "object",
            "properties": {
                "days": {"type": "integer", "default": 28},
                "min_impressions": {"type": "integer", "default": 50},
                "limit": {"type": "integer", "default": 15}
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
        "description": "Actualiza contenido, título, SEO title, meta description o categorías (categories) de un blog de raditech.mx.",
        "input_schema": {
            "type": "object", "required": ["post_id"],
            "properties": {
                "post_id": {"type": "integer"},
                "title": {"type": "string"},
                "content": {"type": "string"},
                "meta_description": {"type": "string"},
                "seo_title": {"type": "string", "description": "SEO title para Google (max 60 chars)"},
                "categories": {"type": "array", "items": {"type": "integer"}, "description": "Lista de IDs de categorías a asignar"},
                "focus_keyword": {"type": "string", "description": "Keyword principal para Rank Math"}
            }
        }
    },
    {
        "name": "get_or_create_raditech_category",
        "description": "Crea una categoría en raditech.mx si no existe, o devuelve la existente. Úsala para asignar categorías a posts.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Nombre de la categoría, ej: 'Tecnología Médica'"},
                "slug": {"type": "string", "description": "Slug opcional, ej: 'tecnologia-medica'"}
            },
            "required": ["name"]
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
        "description": "Actualiza título, slug, SEO title, meta description, focus_keyword o contenido de una página de raditech.mx.",
        "input_schema": {
            "type": "object", "required": ["page_id"],
            "properties": {
                "page_id": {"type": "integer"},
                "title": {"type": "string"},
                "slug": {"type": "string", "description": "Nuevo slug URL (ej: pacs-vira-ris). Minúsculas con guiones, sin slashes."},
                "seo_title": {"type": "string", "description": "SEO title para Google (max 60 chars)"},
                "meta_description": {"type": "string", "description": "Meta description 150-160 chars"},
                "content": {"type": "string", "description": "HTML completo (opcional)"},
                "focus_keyword": {"type": "string", "description": "Keyword principal para Rank Math"},
                "status": {"type": "string", "description": "publish o draft (opcional)"}
            }
        }
    },
    {
        "name": "create_raditech_page",
        "description": "Crea una nueva página en raditech.mx con contenido Gutenberg, título, slug y metadatos SEO (seo_title, meta_description, focus_keyword). Usa PATCH automático para guardar rank_math después de crear.",
        "input_schema": {
            "type": "object", "required": ["title", "content"],
            "properties": {
                "title": {"type": "string"},
                "content": {"type": "string", "description": "HTML/Gutenberg blocks para el cuerpo de la página"},
                "slug": {"type": "string", "description": "URL slug (sin slashes)"},
                "seo_title": {"type": "string", "description": "SEO title Rank Math (max 60 chars)"},
                "meta_description": {"type": "string", "description": "Meta description 150-160 chars"},
                "focus_keyword": {"type": "string", "description": "Keyword principal para Rank Math"},
                "status": {"type": "string", "enum": ["publish", "draft"], "default": "publish"}
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
    {
        "name": "delete_raditech_page",
        "description": "ELIMINA permanentemente una página de raditech.mx. Irreversible. Solo usar después de confirmar que la página nueva ya está publicada y los redirects 301 están en su lugar.",
        "input_schema": {
            "type": "object",
            "required": ["page_id"],
            "properties": {
                "page_id": {"type": "integer", "description": "ID de la página a eliminar permanentemente"}
            }
        }
    },
    # ── Herramientas analíticas WooCommerce ───────────────────────────────────
    {
        "name": "get_orders",
        "description": "Obtiene órdenes de la tienda PYS. Filtra por estado (pending, processing, completed, cancelled, refunded), email del cliente o rango de fechas. Úsala para soporte al cliente o análisis de ventas.",
        "input_schema": {
            "type": "object",
            "properties": {
                "status": {"type": "string", "description": "pending | processing | on-hold | completed | cancelled | refunded | failed"},
                "customer_email": {"type": "string", "description": "Email del cliente para buscar sus órdenes"},
                "limit": {"type": "integer", "default": 20, "description": "Número de órdenes (máx 100)"},
                "after": {"type": "string", "description": "Fecha inicio ISO 8601, ej: 2026-01-01T00:00:00"},
                "before": {"type": "string", "description": "Fecha fin ISO 8601"}
            }
        }
    },
    {
        "name": "get_sales_report",
        "description": "Reporte agregado de ventas PYS: ingresos totales, número de órdenes y valor promedio de orden por período.",
        "input_schema": {
            "type": "object",
            "properties": {
                "period": {"type": "string", "description": "week | month | last_month | year", "default": "month"},
                "date_min": {"type": "string", "description": "Fecha inicio YYYY-MM-DD"},
                "date_max": {"type": "string", "description": "Fecha fin YYYY-MM-DD"}
            }
        }
    },
    {
        "name": "get_top_sellers",
        "description": "Productos más vendidos de PYS por unidades en un período. Úsala para identificar bestsellers y priorizar stock o campañas.",
        "input_schema": {
            "type": "object",
            "properties": {
                "period": {"type": "string", "description": "week | month | last_month | year", "default": "month"},
                "limit": {"type": "integer", "default": 10}
            }
        }
    },
    {
        "name": "compare_mexico_prices",
        "description": "Busca un producto en MercadoLibre México y devuelve precios actuales de mercado para comparar competitividad de precios de PYS.",
        "input_schema": {
            "type": "object",
            "required": ["query"],
            "properties": {
                "query": {"type": "string", "description": "Nombre o keywords del producto a buscar"},
                "limit": {"type": "integer", "description": "Número de listados a comparar", "default": 5}
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
    elif name == "gsc_ptm_top_queries":
        return gsc_ptm_top_queries(inputs.get("days", 28), inputs.get("limit", 10))
    elif name == "gsc_ptm_page_performance":
        return gsc_ptm_page_performance(inputs.get("days", 28), inputs.get("limit", 10))
    elif name == "gsc_ptm_ctr_opportunities":
        return gsc_ptm_ctr_opportunities(inputs.get("days", 28), inputs.get("min_impressions", 50), inputs.get("limit", 15))
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
        if "categories" in inputs:
            data["categories"] = inputs["categories"]
        meta = {}
        if "meta_description" in inputs:
            meta["rank_math_description"] = inputs["meta_description"]
        if "seo_title" in inputs:
            meta["rank_math_title"] = inputs["seo_title"]
        if "focus_keyword" in inputs:
            meta["rank_math_focus_keyword"] = inputs["focus_keyword"]
        if meta:
            data["meta"] = meta
        return update_raditech_post(inputs["post_id"], data)
    elif name == "get_or_create_raditech_category":
        return get_or_create_raditech_category(inputs["name"], inputs.get("slug"))
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
        if "focus_keyword" in inputs:
            meta["rank_math_focus_keyword"] = inputs["focus_keyword"]
        if meta:
            data["meta"] = meta
        return update_raditech_page(inputs["page_id"], data)
    elif name == "create_raditech_page":
        return create_raditech_page(
            title=inputs["title"],
            content=inputs["content"],
            slug=inputs.get("slug", ""),
            seo_title=inputs.get("seo_title", ""),
            meta_description=inputs.get("meta_description", ""),
            focus_keyword=inputs.get("focus_keyword", ""),
            status=inputs.get("status", "publish"),
        )
    elif name == "gsc_raditech_top_queries":
        return gsc_raditech_top_queries(inputs.get("days", 28), inputs.get("limit", 10))
    elif name == "gsc_raditech_page_performance":
        return gsc_raditech_page_performance(inputs.get("days", 28), inputs.get("limit", 10))
    elif name == "gsc_raditech_ctr_opportunities":
        return gsc_raditech_ctr_opportunities(inputs.get("days", 28), inputs.get("min_impressions", 50), inputs.get("limit", 15))
    elif name == "delete_raditech_page":
        return delete_raditech_page(inputs["page_id"])
    elif name == "get_orders":
        return get_orders(
            status=inputs.get("status"),
            customer_email=inputs.get("customer_email"),
            limit=inputs.get("limit", 20),
            after=inputs.get("after"),
            before=inputs.get("before"),
        )
    elif name == "get_sales_report":
        return get_sales_report(inputs.get("period", "month"), inputs.get("date_min"), inputs.get("date_max"))
    elif name == "get_top_sellers":
        return get_top_sellers(inputs.get("period", "month"), inputs.get("limit", 10))
    elif name == "compare_mexico_prices":
        return compare_mexico_prices(inputs["query"], inputs.get("limit", 5))
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


# ─── Modo Backlinks (prospector + auditoría, seguro por diseño) ───────────────
@app.route("/backlinks")
def backlinks_page():
    if not BACKLINKS_AVAILABLE:
        return ("<h2>Agente de Backlinks no disponible</h2>"
                "<p>El módulo backlinks_agent no se pudo cargar. Revisa los logs del servidor.</p>"), 503
    return open("templates/backlinks.html", encoding="utf-8").read()


@app.route("/backlinks/chat", methods=["POST"])
def backlinks_chat():
    if not BACKLINKS_AVAILABLE:
        return jsonify({"reply": "El agente de backlinks no está disponible en el servidor."}), 503
    try:
        messages = request.json.get("messages", [])
        result = backlinks_agent.web_respond(messages)
        return jsonify(result)
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
    notify_nexus(
        action="Generó el reporte SEO",
        detail=f"{report['optimized']}/{report['total']} productos optimizados ({report['pct_optimized']}%)",
    )
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
            notify_nexus(
                action="Optimizó un blog (SEO)",
                detail=title or f"post {post_id}",
                url=result.get("link", url),
            )
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


def _pys_get_or_create_brand(name="PyS"):
    """Devuelve el ID del término product_brand `name`, creándolo si no existe.
    Usa el endpoint nativo de WooCommerce Brands (wc/v3/products/brands)."""
    try:
        r = requests.get(
            f"{WC_URL}/wp-json/wc/v3/products/brands",
            auth=HTTPBasicAuth(WC_KEY, WC_SECRET),
            params={"per_page": 100, "search": name},
            timeout=20,
        )
        for t in (r.json() if isinstance(r.json(), list) else []):
            if t.get("name", "").strip().lower() == name.strip().lower():
                return t["id"], False
        # No existe → crear
        c = requests.post(
            f"{WC_URL}/wp-json/wc/v3/products/brands",
            auth=HTTPBasicAuth(WC_KEY, WC_SECRET),
            json={"name": name},
            timeout=20,
        )
        cj = c.json()
        if "id" in cj:
            return cj["id"], True
        return None, False
    except Exception as e:
        return None, False


@app.route("/pys-assign-house-brand", methods=["POST"])
def pys_assign_house_brand():
    """Asigna la marca propia (default 'PyS') a todo producto publicado que hoy
    no tenga ninguna brand asignada. Idempotente: no toca los que ya tienen brand."""
    try:
        data = request.json or {}
        brand_name = data.get("brand_name", "PyS")
        dry_run = bool(data.get("dry_run", False))

        brand_id, created = _pys_get_or_create_brand(brand_name)
        if not brand_id:
            return jsonify({"error": f"no se pudo obtener/crear la marca '{brand_name}'"}), 500

        # Listar productos con su campo brands
        r = requests.get(
            f"{WC_URL}/wp-json/wc/v3/products",
            auth=HTTPBasicAuth(WC_KEY, WC_SECRET),
            params={"per_page": 100, "status": "publish", "_fields": "id,name,brands"},
            timeout=30,
        )
        products = r.json() if isinstance(r.json(), list) else []

        to_assign = [p for p in products if not p.get("brands")]
        assigned, errors = [], []

        if not dry_run:
            for p in to_assign:
                res = update_product(p["id"], {"brands": [{"id": brand_id}]})
                if res.get("success"):
                    assigned.append({"id": p["id"], "name": p.get("name")})
                else:
                    errors.append({"id": p["id"], "error": res.get("error")})

        return jsonify({
            "brand": brand_name, "brand_id": brand_id, "brand_created": created,
            "total_products": len(products),
            "already_branded": len(products) - len(to_assign),
            "needed_brand": len(to_assign),
            "assigned": assigned, "errors": errors,
            "dry_run": dry_run,
            "candidates": [{"id": p["id"], "name": p.get("name")} for p in to_assign] if dry_run else None,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/pys-product-update", methods=["POST"])
def pys_product_update():
    """Actualiza SEO meta y/o schema de un producto/página de PYS sin pasar por el agente IA."""
    try:
        data = request.json or {}
        post_id = data.get("post_id")
        if not post_id:
            return jsonify({"error": "post_id required"}), 400

        results = {}

        # SEO meta (title, description, focus keyword)
        meta = {}
        if "seo_title" in data:
            meta["rank_math_title"] = data["seo_title"]
        if "meta_description" in data:
            meta["rank_math_description"] = data["meta_description"]
        if "focus_keyword" in data:
            meta["rank_math_focus_keyword"] = data["focus_keyword"]
        if meta:
            results["meta"] = set_pys_rank_math_meta(post_id, meta)

        # Schema (FAQPage u otro tipo vía updateSchemas — solo posts/pages con JWT)
        if "schemas" in data:
            results["schema"] = set_pys_rank_math_schema(post_id, data["schemas"])

        # Para PRODUCTOS WooCommerce el schema de Rank Math se persiste como
        # post meta (rank_math_schema_*) vía wc/v3 meta_data + HTTPBasicAuth
        # (el JWT no tiene permiso de edición sobre productos → 401).
        if "faq_main_entity" in data:
            faq_value = {
                "@type": "FAQPage",
                "metadata": {
                    "title": "FAQ",
                    "type": "template",
                    "shortcode": f"s-{uuid.uuid4().hex[:13]}",
                    "isPrimary": 0,
                    "reviewLocation": "custom",
                },
                "mainEntity": data["faq_main_entity"],
            }
            results["faq_schema"] = update_product(
                post_id,
                {"meta_data": [{"key": "rank_math_schema_FAQPage", "value": faq_value}]},
            )

        # Passthrough genérico de meta_data para productos.
        if "product_meta_data" in data:
            results["product_meta"] = update_product(
                post_id, {"meta_data": data["product_meta_data"]}
            )

        # Asignación de brand a un producto concreto (WooCommerce native Brands).
        if "brand_id" in data:
            results["brands"] = update_product(
                post_id, {"brands": [{"id": data["brand_id"]}]}
            )

        results["post_id"] = post_id
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/raditech-page-update", methods=["POST"])
def raditech_page_update_direct():
    """Direct endpoint to update a raditech page without going through the AI agent."""
    try:
        data = request.json or {}
        page_id = data.get("page_id")
        if not page_id:
            return jsonify({"error": "page_id required"}), 400
        payload = {}
        if "content" in data:
            payload["content"] = data["content"]
        if "title" in data:
            payload["title"] = data["title"]
        if "status" in data:
            payload["status"] = data["status"]
        if "slug" in data:
            payload["slug"] = data["slug"]
        if "author" in data:
            payload["author"] = data["author"]
        # rank_math_* viaja en payload["meta"]; update_raditech_page lo desvía
        # al endpoint propio de Rank Math (el campo `meta` del REST core no persiste).
        meta = {}
        if "seo_title" in data:
            meta["rank_math_title"] = data["seo_title"]
        if "meta_description" in data:
            meta["rank_math_description"] = data["meta_description"]
        if "focus_keyword" in data:
            meta["rank_math_focus_keyword"] = data["focus_keyword"]
        if meta:
            payload["meta"] = meta
        result = update_raditech_page(page_id, payload)
        return jsonify(result)
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

        prompt = f"""Eres un experto SEO. Tienes este artículo de blog en grupoptm.com (plataforma de telemedicina especializada en péptidos y salud hormonal):

TÍTULO: {title}
URL: {url}
POST ID: {post_id}

CONTENIDO ACTUAL (HTML):
{content}

OTROS ARTÍCULOS DEL BLOG DE GRUPOPTM.COM (para interlinks):
{ptm_posts_list if ptm_posts_list else "No hay otros artículos disponibles aún."}

Tu tarea — agrega los siguientes links de forma NATURAL dentro del texto existente:
1. INTERLINKS (2-4 links): enlaza a otros artículos del blog de grupoptm.com que sean temáticamente relevantes.
   Formato: <a href="URL_DEL_POST">texto descriptivo</a>
2. LINKS EXTERNOS CIENTÍFICOS (3-5 links): enlaza a fuentes de autoridad científica relevantes al tema del artículo
   (PubMed, NIH, Mayo Clinic, NEJM, Examine.com). Solo URLs reales y verificables.
   Formato: <a href="URL" target="_blank" rel="noopener noreferrer">texto descriptivo</a>
3. Asegúrate de que el contenido tenga al menos un H2 y que la conclusión incluya un CTA hacia agendar una consulta médica en grupoptm.com.
4. NO inventes posts que no estén en la lista anterior. NO enlaces a peptidosysuplementos.mx ni a ningún producto de PYS — PTM y PYS son independientes.
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


@app.route("/delete-raditech-page/<int:page_id>", methods=["DELETE", "POST"])
def delete_raditech_page_route(page_id):
    try:
        result = delete_raditech_page(page_id)
        if result.get("success"):
            return jsonify({"ok": True, "deleted": page_id})
        return jsonify({"ok": False, **result}), 400
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
4. NO agregues links a peptidosysuplementos.mx ni a productos de PYS — PTM y PYS son empresas independientes, sin embudo entre ambos

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

def get_gsc_service(refresh_token=None):
    creds = Credentials(
        token=None,
        refresh_token=refresh_token or GSC_REFRESH_TOKEN,
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


def fetch_gsc_data(dimension, days=28, limit=10, site_url=None, refresh_token=None):
    service = get_gsc_service(refresh_token=refresh_token)
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
    if not RADITECH_GSC_REFRESH_TOKEN:
        return {"error": "GSC Raditech no autenticado. Visita /search-console/raditech/auth"}
    try:
        rows = fetch_gsc_data("query", days, limit, site_url=RADITECH_GSC_SITE_URL, refresh_token=RADITECH_GSC_REFRESH_TOKEN)
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
    if not RADITECH_GSC_REFRESH_TOKEN:
        return {"error": "GSC Raditech no autenticado. Visita /search-console/raditech/auth"}
    try:
        rows = fetch_gsc_data("page", days, limit, site_url=RADITECH_GSC_SITE_URL, refresh_token=RADITECH_GSC_REFRESH_TOKEN)
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
    if not RADITECH_GSC_REFRESH_TOKEN:
        return {"error": "GSC Raditech no autenticado. Visita /search-console/raditech/auth"}
    try:
        rows = fetch_gsc_data("query", days, 500, site_url=RADITECH_GSC_SITE_URL, refresh_token=RADITECH_GSC_REFRESH_TOKEN)
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


def gsc_ptm_top_queries(days=28, limit=10):
    """Top búsquedas de grupoptm.com por clicks en GSC."""
    if not PTM_GSC_REFRESH_TOKEN:
        return {"error": "GSC PTM no autenticado. Visita /search-console/ptm/auth"}
    try:
        rows = fetch_gsc_data("query", days, limit, site_url=PTM_GSC_SITE_URL, refresh_token=PTM_GSC_REFRESH_TOKEN)
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


def gsc_ptm_page_performance(days=28, limit=10):
    """Páginas de grupoptm.com con más clicks en GSC."""
    if not PTM_GSC_REFRESH_TOKEN:
        return {"error": "GSC PTM no autenticado. Visita /search-console/ptm/auth"}
    try:
        rows = fetch_gsc_data("page", days, limit, site_url=PTM_GSC_SITE_URL, refresh_token=PTM_GSC_REFRESH_TOKEN)
        return [
            {
                "page": r["keys"][0].replace("https://grupoptm.com", ""),
                "clicks": r.get("clicks", 0),
                "impressions": r.get("impressions", 0),
                "ctr_pct": round(r.get("ctr", 0) * 100, 1),
                "position": round(r.get("position", 0), 1)
            }
            for r in rows[:limit]
        ]
    except Exception as e:
        return {"error": str(e)}


def gsc_ptm_ctr_opportunities(days=28, min_impressions=50, limit=15):
    """Keywords de grupoptm.com con CTR bajo — oportunidades de mejora de títulos."""
    if not PTM_GSC_REFRESH_TOKEN:
        return {"error": "GSC PTM no autenticado. Visita /search-console/ptm/auth"}
    try:
        rows = fetch_gsc_data("query", days, 500, site_url=PTM_GSC_SITE_URL, refresh_token=PTM_GSC_REFRESH_TOKEN)
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


@app.route("/search-console/raditech/auth")
def gsc_raditech_auth():
    if not GSC_CLIENT_ID or not GSC_CLIENT_SECRET:
        return "Faltan variables GOOGLE_CLIENT_ID y GOOGLE_CLIENT_SECRET en Railway.", 400
    import urllib.parse
    params = {
        "client_id": GSC_CLIENT_ID,
        "redirect_uri": RADITECH_GSC_REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(GSC_SCOPES),
        "access_type": "offline",
        "prompt": "consent"
    }
    auth_url = "https://accounts.google.com/o/oauth2/auth?" + urllib.parse.urlencode(params)
    return redirect(auth_url)


@app.route("/search-console/raditech/callback")
def gsc_raditech_callback():
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
                "redirect_uri": RADITECH_GSC_REDIRECT_URI,
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
<html><head><meta charset="utf-8"><title>Search Console Raditech conectado</title>
<style>body{{font-family:Arial;max-width:600px;margin:60px auto;padding:20px;background:#0f0f0f;color:#eee}}
.box{{background:#1a1a1a;border-radius:10px;padding:24px;border-left:4px solid #f97316}}
code{{background:#2a2a2a;padding:4px 10px;border-radius:6px;font-size:13px;word-break:break-all}}
.btn{{display:inline-block;background:#f97316;color:white;padding:10px 20px;border-radius:8px;text-decoration:none;margin-top:16px}}</style>
</head><body>
<h2>✅ Google Search Console Raditech conectado</h2>
<div class="box">
<p>Copia este <strong>Refresh Token</strong> y agrégalo en Railway como variable de entorno:</p>
<p><strong>Variable:</strong> <code>RADITECH_GSC_REFRESH_TOKEN</code></p>
<p><strong>Valor:</strong><br><code>{refresh_token}</code></p>
</div>
<p style="color:#aaa;font-size:13px;margin-top:16px;">Una vez que agregues la variable en Railway y el servicio se reinicie, el Search Console de Raditech estará activo.</p>
</body></html>"""


@app.route("/search-console/ptm/auth")
def gsc_ptm_auth():
    if not GSC_CLIENT_ID or not GSC_CLIENT_SECRET:
        return "Faltan variables GOOGLE_CLIENT_ID y GOOGLE_CLIENT_SECRET en Railway.", 400
    import urllib.parse
    params = {
        "client_id": GSC_CLIENT_ID,
        "redirect_uri": PTM_GSC_REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(GSC_SCOPES),
        "access_type": "offline",
        "prompt": "consent"
    }
    auth_url = "https://accounts.google.com/o/oauth2/auth?" + urllib.parse.urlencode(params)
    return redirect(auth_url)


@app.route("/search-console/ptm/callback")
def gsc_ptm_callback():
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
                "redirect_uri": PTM_GSC_REDIRECT_URI,
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
<html><head><meta charset="utf-8"><title>Search Console PTM conectado</title>
<style>body{{font-family:Arial;max-width:600px;margin:60px auto;padding:20px;background:#0f0f0f;color:#eee}}
.box{{background:#1a1a1a;border-radius:10px;padding:24px;border-left:4px solid #7c3aed}}
code{{background:#2a2a2a;padding:4px 10px;border-radius:6px;font-size:13px;word-break:break-all}}
.btn{{display:inline-block;background:#7c3aed;color:white;padding:10px 20px;border-radius:8px;text-decoration:none;margin-top:16px}}</style>
</head><body>
<h2>✅ Google Search Console PTM conectado</h2>
<div class="box">
<p>Copia este <strong>Refresh Token</strong> y agrégalo en Railway como variable de entorno:</p>
<p><strong>Variable:</strong> <code>PTM_GSC_REFRESH_TOKEN</code></p>
<p><strong>Valor:</strong><br><code>{refresh_token}</code></p>
</div>
<p style="color:#aaa;font-size:13px;margin-top:16px;">Una vez que agregues la variable en Railway y el servicio se reinicie, el Search Console de grupoptm.com estará activo.</p>
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
