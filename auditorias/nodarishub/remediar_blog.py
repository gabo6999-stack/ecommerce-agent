"""
Remediación del blog de nodarishub (2026-08-12).

Dos arreglos sobre los posts ya publicados:

1. Metas de Rank Math. El agente las mandaba en el campo `meta` de /wp/v2/posts,
   que Rank Math descarta en silencio, así que ningún post tenía focus keyword
   guardada y el plugin no tenía nada que analizar (puntaje 0 en 19 de 20). Se
   reescriben por `rankmath/v1/updateMeta`, que sí persiste.

2. Imagen de portada. Nueve entradas salieron sin `featured_media` y el listado
   las muestra con el recuadro gris "NDH". Se les busca una foto en Unsplash que
   no esté usada ya en el blog y se sube con alt en español.

Uso:
    python auditorias/nodarishub/remediar_blog.py --dry-run
    python auditorias/nodarishub/remediar_blog.py --metas
    python auditorias/nodarishub/remediar_blog.py --imagenes
"""
import sys, os, re, time, json, base64, argparse, unicodedata
sys.stdout.reconfigure(encoding="utf-8")
import requests
from bs4 import BeautifulSoup

BASE = "https://nodarishub.com"
RAIZ = os.path.join(os.path.dirname(__file__), "..", "..")


def _cargar_env():
    datos = {}
    for ruta, claves in [
        (os.path.join(RAIZ, "ecommerce-agent__.env"), ["NODARIS_WP_USER", "NODARIS_WP_APP_PASSWORD"]),
        (os.path.join(RAIZ, "..", "agente-blogs", "agente-blogs__.env"), ["UNSPLASH_ACCESS_KEY"]),
    ]:
        if not os.path.exists(ruta):
            continue
        for linea in open(ruta, encoding="utf-8"):
            if "=" not in linea or linea.startswith("#"):
                continue
            k, v = linea.split("=", 1)
            if k.strip() in claves:
                datos[k.strip()] = v.strip()
    return datos


ENV = _cargar_env()
USER = os.environ.get("NODARIS_WP_USER") or ENV.get("NODARIS_WP_USER", "")
PW = os.environ.get("NODARIS_WP_APP_PASSWORD") or ENV.get("NODARIS_WP_APP_PASSWORD", "")
UNSPLASH = os.environ.get("UNSPLASH_ACCESS_KEY") or ENV.get("UNSPLASH_ACCESS_KEY", "")

H = {"Authorization": "Basic " + base64.b64encode(f"{USER}:{PW}".encode()).decode(),
     "Content-Type": "application/json"}
PUB = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120"}

# Focus keyword y meta description por post. La keyword sale del slug (es lo que
# la entrada realmente persigue) y la descripción del excerpt cuando ya era buena.
# `unsplash` es la consulta de portada para los que no tienen imagen.
POSTS = {
    145: {"kw": "página web a código",
          "unsplash": "custom web development code editor"},
    148: {"kw": "velocidad de carga web"},
    150: {"kw": "automatización de procesos"},
    157: {"kw": "precios de páginas web en ecuador"},
    162: {"kw": "página web a la medida"},
    180: {"kw": "benchmark de salud técnica seo",
          "unsplash": "open data dashboard charts"},
    225: {"kw": "google search console para qué sirve"},
    231: {"kw": "qué es la automatización de procesos"},
    237: {"kw": "cómo crear una página web gratis"},
    240: {"kw": "para qué sirve google search console"},
    257: {"kw": "velocidad de carga de una página web"},
    259: {"kw": "cómo crear una página web",
          "unsplash": "person building website laptop"},
    260: {"kw": "cómo crear una página web para negocio",
          "unsplash": "small business owner computer shop"},
    261: {"kw": "posicionamiento web o seo",
          "unsplash": "search engine results ranking"},
    262: {"kw": "diseño de páginas web en html",
          "unsplash": "html markup code screen"},
    263: {"kw": "posicionamiento seo y sem",
          "unsplash": "digital advertising campaign analytics"},
    264: {"kw": "desarrollo web full stack",
          "unsplash": "software engineer dual monitors"},
    265: {"kw": "posicionamiento seo qué es",
          "unsplash": "seo strategy planning desk"},
    270: {"kw": "crear página web para negocio en 2026"},
    288: {"kw": "google search console tools"},
}


def slugify(texto, limite=60):
    plano = unicodedata.normalize("NFKD", texto or "").encode("ascii", "ignore").decode()
    plano = re.sub(r"[^a-zA-Z0-9]+", "-", plano).strip("-").lower()
    return plano[:limite].strip("-") or "blog"


def obtener_posts():
    out, page = {}, 1
    while True:
        r = requests.get(f"{BASE}/wp-json/wp/v2/posts", headers=H, timeout=30,
                         params={"per_page": 50, "page": page, "context": "edit", "status": "publish"})
        r.raise_for_status()
        lote = r.json()
        if not lote:
            break
        for p in lote:
            out[p["id"]] = p
        if len(lote) < 50:
            break
        page += 1
    return out


def titulo_vivo(link):
    try:
        r = requests.get(link, headers=PUB, params={"nocache": int(time.time())}, timeout=25)
        s = BeautifulSoup(r.text, "html.parser")
        t = s.find("title")
        return t.text.strip() if t else ""
    except Exception:
        return ""


def purgar(post_id, slug):
    """Re-guardar el slug dispara el purge-on-update de LiteSpeed."""
    try:
        requests.post(f"{BASE}/wp-json/wp/v2/posts/{post_id}", headers=H,
                      json={"slug": slug}, timeout=30)
    except Exception as e:
        print(f"    aviso: no se pudo purgar {post_id}: {e}")


# ── 1. METAS DE RANK MATH ──────────────────────────────────────────────────── #

def recortar_titulo(texto, limite=60):
    """Deja el título en ≤60 sin partir la marca por la mitad.

    Cortar a secas producía cosas como "... | Nodarishu": si no cabe con el
    sufijo de marca, se quita el sufijo entero y solo entonces se recorta.
    """
    texto = (texto or "").strip()
    if len(texto) <= limite:
        return texto
    if " | " in texto:
        sin_marca = texto.rsplit(" | ", 1)[0].strip()
        if len(sin_marca) <= limite:
            return sin_marca
        texto = sin_marca
    corte = texto[:limite]
    return corte[:corte.rfind(" ")].rstrip(" ,;:—-") if " " in corte else corte


def arreglar_metas(posts, dry):
    print("\n=== METAS DE RANK MATH ===")
    hechos = 0
    for pid, cfg in sorted(POSTS.items()):
        p = posts.get(pid)
        if not p:
            print(f"  [{pid}] no encontrado, se salta")
            continue
        excerpt = BeautifulSoup(p.get("excerpt", {}).get("rendered", ""), "html.parser").get_text(" ", strip=True)
        vivo = titulo_vivo(p["link"])
        # El título en vivo ya viene ≤60 gracias al agente SEO; solo se recorta si no.
        rm_title = recortar_titulo(vivo or p["title"]["rendered"])
        meta = {
            "rank_math_title": rm_title,
            "rank_math_description": (excerpt or "")[:160],
            "rank_math_focus_keyword": cfg["kw"],
        }
        print(f"  [{pid}] kw='{cfg['kw']}' | title({len(rm_title)})='{rm_title}'")
        if dry:
            continue
        r = requests.post(f"{BASE}/wp-json/rankmath/v1/updateMeta", headers=H, timeout=30,
                          json={"objectID": pid, "objectType": "post", "meta": meta})
        if r.status_code == 200:
            hechos += 1
            purgar(pid, p["slug"])
        else:
            print(f"        ERROR {r.status_code}: {r.text[:150]}")
        time.sleep(0.4)
    print(f"  → {hechos}/{len(POSTS)} actualizados")


# ── 2. IMÁGENES DE PORTADA ─────────────────────────────────────────────────── #

def ids_usados():
    usados = set()
    try:
        r = requests.get(f"{BASE}/wp-json/wp/v2/media", headers=H, timeout=30,
                         params={"per_page": 100, "search": "blog-", "_fields": "source_url"})
        for m in r.json():
            nombre = (m.get("source_url") or "").split("/")[-1]
            match = re.match(r"^blog-.*-([A-Za-z0-9_-]{8,})\.jpe?g$", nombre)
            if match:
                usados.add(match.group(1))
    except Exception as e:
        print(f"  aviso: no se pudieron leer los medios existentes: {e}")
    return usados


def buscar_foto(query, evitar):
    r = requests.get("https://api.unsplash.com/search/photos",
                     params={"query": query, "per_page": 12, "orientation": "landscape",
                             "content_filter": "high"},
                     headers={"Authorization": f"Client-ID {UNSPLASH}"}, timeout=20)
    r.raise_for_status()
    for foto in r.json().get("results", []):
        if foto["id"] not in evitar:
            try:
                requests.get(foto["links"]["download_location"],
                             headers={"Authorization": f"Client-ID {UNSPLASH}"}, timeout=10)
            except Exception:
                pass
            return foto
    return None


def arreglar_imagenes(posts, dry):
    print("\n=== IMÁGENES DE PORTADA ===")
    faltan = [pid for pid, p in posts.items() if not p.get("featured_media")]
    print(f"  Sin portada: {sorted(faltan)}")
    if not UNSPLASH and not dry:
        print("  ❌ Falta UNSPLASH_ACCESS_KEY")
        return
    evitar = ids_usados()
    print(f"  Fotos ya usadas en el blog: {len(evitar)}")
    hechos = 0
    for pid in sorted(faltan):
        p = posts[pid]
        cfg = POSTS.get(pid, {})
        query = cfg.get("unsplash") or cfg.get("kw") or p["title"]["rendered"]
        titulo = BeautifulSoup(p["title"]["rendered"], "html.parser").get_text()
        print(f"  [{pid}] '{titulo[:55]}' ← query: {query}")
        if dry:
            continue
        try:
            foto = buscar_foto(query, evitar)
        except Exception as e:
            print(f"        ERROR buscando: {e}")
            continue
        if not foto:
            print("        sin foto nueva disponible")
            continue
        evitar.add(foto["id"])
        try:
            binario = requests.get(foto["urls"]["regular"], timeout=45)
            binario.raise_for_status()
            nombre = f"blog-{slugify(p['slug'])}-{foto['id']}.jpg"
            alt = f"{titulo}"[:125]
            subida = requests.post(
                f"{BASE}/wp-json/wp/v2/media",
                headers={"Authorization": H["Authorization"],
                         "Content-Disposition": f'attachment; filename="{nombre}"',
                         "Content-Type": "image/jpeg"},
                data=binario.content, timeout=90)
            subida.raise_for_status()
            media_id = subida.json()["id"]
            requests.post(f"{BASE}/wp-json/wp/v2/media/{media_id}", headers=H,
                          json={"alt_text": alt, "title": alt}, timeout=20)
            r = requests.post(f"{BASE}/wp-json/wp/v2/posts/{pid}", headers=H,
                              json={"featured_media": media_id}, timeout=30)
            r.raise_for_status()
            confirmado = r.json().get("featured_media")
            print(f"        ✅ media {media_id} ({nombre}) asignada={confirmado == media_id}")
            hechos += 1
        except Exception as e:
            print(f"        ERROR subiendo: {e}")
        time.sleep(0.6)
    print(f"  → {hechos}/{len(faltan)} portadas asignadas")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--metas", action="store_true")
    ap.add_argument("--imagenes", action="store_true")
    a = ap.parse_args()
    if not (a.metas or a.imagenes):
        a.metas = a.imagenes = True

    posts = obtener_posts()
    print(f"Posts publicados: {len(posts)}")
    if a.metas:
        arreglar_metas(posts, a.dry_run)
    if a.imagenes:
        arreglar_imagenes(posts, a.dry_run)


if __name__ == "__main__":
    main()
