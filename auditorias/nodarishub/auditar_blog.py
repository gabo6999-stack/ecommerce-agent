"""
Auditoría exhaustiva del blog de nodarishub.

Mide por post: longitud, imagen destacada, imágenes en cuerpo, metas de Rank Math
(persistidas de verdad, no las que WordPress deriva por fallback), enlaces
internos/externos, jerarquía de encabezados y señal de país MX/EC.

El score de Rank Math se lee de `rankmath/v1/links/posts`, que expone el
`rank_math_seo_score` guardado en postmeta. Un 0 ahí no significa "malo":
significa que nadie corrió el análisis (solo lo calcula el editor de Gutenberg),
que es justo lo que pasa con todo post publicado por REST.

Uso:  python auditorias/nodarishub/auditar_blog.py [--json salida.json]
"""
import sys, os, re, json, time, base64, argparse
sys.stdout.reconfigure(encoding="utf-8")
import requests
from bs4 import BeautifulSoup

BASE = "https://nodarishub.com"
USER = os.environ.get("NODARIS_WP_USER", "")
PW = os.environ.get("NODARIS_WP_APP_PASSWORD", "")

if not USER or not PW:
    envfile = os.path.join(os.path.dirname(__file__), "..", "..", "ecommerce-agent__.env")
    if os.path.exists(envfile):
        for line in open(envfile, encoding="utf-8"):
            if line.startswith("NODARIS_WP_USER="):
                USER = line.split("=", 1)[1].strip()
            elif line.startswith("NODARIS_WP_APP_PASSWORD="):
                PW = line.split("=", 1)[1].strip()

AUTH = base64.b64encode(f"{USER}:{PW}".encode()).decode()
H = {"Authorization": f"Basic {AUTH}", "User-Agent": "Mozilla/5.0 (Nodaris-Blog-Audit)"}
PUB = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"}

SERVICIOS = ["/diseno-web/", "/seo/", "/software/", "/marketing/", "/crear-pagina-web/"]
PISO_PALABRAS = 1200          # piso de publicación del agente (post_length 1400 - 200)
MIN_ENLACES_INTERNOS = 3


def fetch_posts():
    posts, page = [], 1
    while True:
        r = requests.get(f"{BASE}/wp-json/wp/v2/posts", headers=H, timeout=30,
                         params={"per_page": 50, "page": page, "context": "edit",
                                 "status": "publish", "_embed": "1"})
        r.raise_for_status()
        batch = r.json()
        if not batch:
            break
        posts += batch
        if len(batch) < 50:
            break
        page += 1
    return posts


def fetch_rm_scores():
    """seo_score + conteo de enlaces que Rank Math tiene guardados en postmeta."""
    out, page = {}, 1
    while True:
        r = requests.get(f"{BASE}/wp-json/rankmath/v1/links/posts", headers=H, timeout=30,
                         params={"page": page, "per_page": 100})
        if r.status_code != 200:
            break
        batch = (r.json() or {}).get("posts", [])
        if not batch:
            break
        for x in batch:
            out[int(x["post_id"])] = {
                "seo_score": int(x.get("seo_score") or 0),
                "incoming_links": int(x.get("incoming_link_count") or 0),
                "is_orphan": bool(x.get("is_orphan")),
            }
        if len(batch) < 100:
            break
        page += 1
    return out


def analizar_cuerpo(html):
    soup = BeautifulSoup(html or "", "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()
    texto = soup.get_text(" ", strip=True)
    enlaces = soup.find_all("a", href=True)
    internos = [a["href"] for a in enlaces if "nodarishub.com" in a["href"] or a["href"].startswith("/")]
    externos = [a["href"] for a in enlaces if a["href"].startswith("http") and "nodarishub.com" not in a["href"]]
    imgs = soup.find_all("img")
    return {
        "palabras": len(texto.split()),
        "h2": len(soup.find_all("h2")),
        "h3": len(soup.find_all("h3")),
        "imgs_cuerpo": len(imgs),
        "imgs_sin_alt": len([i for i in imgs if not (i.get("alt") or "").strip()]),
        "enlaces_internos": len(internos),
        "enlaces_externos": len(externos),
        "enlaza_servicio": any(any(s in u for s in SERVICIOS) for u in internos),
        "texto": texto,
    }


def analizar_vivo(url):
    try:
        r = requests.get(url, headers=PUB, timeout=25, params={"nocache": int(time.time())})
    except Exception as e:
        return {"error": str(e)}
    if not r.ok:
        return {"error": f"HTTP {r.status_code}"}
    s = BeautifulSoup(r.text, "html.parser")
    t = s.find("title")
    m = s.find("meta", attrs={"name": "description"})
    h1 = s.find_all("h1")
    tipos = re.findall(r'"@type"\s*:\s*"([^"]+)"', r.text)
    return {
        "title": t.text.strip() if t else "",
        "title_len": len(t.text.strip()) if t else 0,
        "desc": m["content"].strip() if m and m.get("content") else "",
        "desc_len": len(m["content"].strip()) if m and m.get("content") else 0,
        "h1_count": len(h1),
        "og_image": bool(s.find("meta", attrs={"property": "og:image"})),
        "schema_tipos": sorted(set(tipos)),
    }


def senal_pais(texto):
    bajo = texto.lower()
    mx = bool(re.search(r"\bméxico\b|\bmexicano|\bcdmx\b|guadalajara|monterrey|\bmxn\b", bajo))
    ec = bool(re.search(r"\becuador\b|ecuatorian|\bquito\b|guayaquil", bajo))
    return "MX+EC" if mx and ec else ("MX" if mx else ("EC" if ec else "NINGUNO"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default="")
    args = ap.parse_args()

    posts = fetch_posts()
    rm = fetch_rm_scores()
    print(f"Posts publicados: {len(posts)}\n")

    filas = []
    for p in posts:
        pid = p["id"]
        cuerpo = analizar_cuerpo(p.get("content", {}).get("raw") or p.get("content", {}).get("rendered", ""))
        vivo = analizar_vivo(p["link"])
        emb = p.get("_embedded", {})
        destacada = p.get("featured_media", 0) or 0
        fila = {
            "id": pid,
            "titulo": p["title"]["rendered"],
            "slug": p["slug"],
            "url": p["link"],
            "fecha": p.get("date", ""),
            "autor": p.get("author"),
            "palabras": cuerpo["palabras"],
            "h2": cuerpo["h2"],
            "h3": cuerpo["h3"],
            "featured_media": destacada,
            "tiene_destacada": bool(destacada),
            "imgs_cuerpo": cuerpo["imgs_cuerpo"],
            "imgs_sin_alt": cuerpo["imgs_sin_alt"],
            "enlaces_internos": cuerpo["enlaces_internos"],
            "enlaces_externos": cuerpo["enlaces_externos"],
            "enlaza_servicio": cuerpo["enlaza_servicio"],
            "pais": senal_pais(cuerpo["texto"]),
            "rm_seo_score": rm.get(pid, {}).get("seo_score", 0),
            "rm_incoming": rm.get(pid, {}).get("incoming_links", 0),
            "rm_huerfano": rm.get(pid, {}).get("is_orphan", None),
            "categorias": [c["name"] for c in emb.get("wp:term", [[]])[0]] if emb.get("wp:term") else [],
            "n_tags": len(p.get("tags", [])),
            **{f"vivo_{k}": v for k, v in vivo.items()},
        }
        problemas = []
        if not fila["tiene_destacada"]:
            problemas.append("SIN-IMAGEN-DESTACADA")
        if fila["palabras"] < PISO_PALABRAS:
            problemas.append(f"FLACO({fila['palabras']}p)")
        if fila["rm_seo_score"] == 0:
            problemas.append("RANKMATH-SIN-ANALIZAR")
        if fila["enlaces_internos"] < MIN_ENLACES_INTERNOS:
            problemas.append(f"POCOS-INTERLINKS({fila['enlaces_internos']})")
        if not fila["enlaza_servicio"]:
            problemas.append("NO-ENLAZA-SERVICIO")
        if fila["rm_huerfano"]:
            problemas.append("HUERFANO")
        if fila.get("vivo_title_len", 0) > 60:
            problemas.append(f"TITULO-LARGO({fila.get('vivo_title_len')})")
        if fila["h2"] < 3:
            problemas.append(f"POCOS-H2({fila['h2']})")
        if not fila["n_tags"]:
            problemas.append("SIN-TAGS")
        fila["problemas"] = problemas
        filas.append(fila)

    filas.sort(key=lambda f: f["fecha"])

    print(f"{'ID':>4} {'pais':<6} {'pal':>5} {'H2':>3} {'img':>3} {'int':>3} {'ext':>3} {'RM':>3} {'inc':>3}  problemas")
    print("-" * 118)
    for f in filas:
        print(f"{f['id']:>4} {f['pais']:<6} {f['palabras']:>5} {f['h2']:>3} "
              f"{'SI' if f['tiene_destacada'] else 'NO':>3} {f['enlaces_internos']:>3} "
              f"{f['enlaces_externos']:>3} {f['rm_seo_score']:>3} {f['rm_incoming']:>3}  "
              f"{', '.join(f['problemas']) if f['problemas'] else 'ok'}")
        print(f"     {f['titulo'][:100]}")

    # Resumen
    print("\n" + "=" * 118)
    sin_img = [f["id"] for f in filas if not f["tiene_destacada"]]
    flacos = [(f["id"], f["palabras"]) for f in filas if f["palabras"] < PISO_PALABRAS]
    sin_rm = [f["id"] for f in filas if f["rm_seo_score"] == 0]
    huerfanos = [f["id"] for f in filas if f["rm_huerfano"]]
    sin_tags = [f["id"] for f in filas if not f["n_tags"]]
    sin_servicio = [f["id"] for f in filas if not f["enlaza_servicio"]]
    print(f"Sin imagen destacada ({len(sin_img)}): {sin_img}")
    print(f"Flacos <{PISO_PALABRAS} palabras ({len(flacos)}): {flacos}")
    print(f"Rank Math sin analizar ({len(sin_rm)}/{len(filas)}): {sin_rm}")
    print(f"Huérfanos sin enlaces entrantes ({len(huerfanos)}): {huerfanos}")
    print(f"Sin tags ({len(sin_tags)}): {sin_tags}")
    print(f"No enlazan ninguna página de servicio ({len(sin_servicio)}): {sin_servicio}")
    print(f"Con imagen en el cuerpo: {len([f for f in filas if f['imgs_cuerpo']])}/{len(filas)}")

    # Canibalización por solapamiento de palabras del título
    print("\n--- POSIBLE CANIBALIZACIÓN (títulos con >=60% de palabras clave en común) ---")
    def clave(t):
        stop = {"de","la","el","en","para","que","tu","un","una","y","o","por","con","los","las","del","al","es","2026","2025","guia","guía","como","cómo","mi","se"}
        return {w for w in re.findall(r"\w+", t.lower()) if w not in stop and len(w) > 2}
    vistos = set()
    for i, a in enumerate(filas):
        grupo = [a]
        for b in filas[i+1:]:
            ka, kb = clave(a["titulo"]), clave(b["titulo"])
            if ka and kb and len(ka & kb) / min(len(ka), len(kb)) >= 0.6:
                grupo.append(b)
        if len(grupo) > 1 and a["id"] not in vistos:
            for g in grupo:
                vistos.add(g["id"])
            print(f"  · {[g['id'] for g in grupo]}")
            for g in grupo:
                print(f"      {g['id']}: {g['titulo']}  ({g['palabras']}p, {g['url'].replace(BASE,'')})")

    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(filas, fh, ensure_ascii=False, indent=2)
        print(f"\nJSON escrito en {args.json}")


if __name__ == "__main__":
    main()
