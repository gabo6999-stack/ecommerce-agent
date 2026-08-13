"""
Arregla el lote de entradas programadas por Rafa (266, 267, 268) — 2026-08-13.

Rafa programa entradas desde el editor, fuera del Agente de Blogs, así que NO
pasan por sus compuertas: salen cortas, sin portada y sin categoría de país. Sin
país, el mu-plugin no puede construir la URL y la entrada se queda colgando en
la raíz en vez de /mx/blog/ o /ec/blog/ (le pasó a la 266 al publicarse hoy).

Este script les pone país y portada. La expansión la hace
`expandir_posts_flacos.py`, que ya tiene las compuertas de integridad.

País: van a Ecuador. Es la misma regla de reparto que quedó en el agente
(publicar donde haya MENOS artículos: EC 4 vs MX 10) y Rafa escribe desde Quito.
Cambiarlo después es cambiarles la categoría, nada más.

Uso:
    python auditorias/nodarishub/arreglar_lote_programado.py --dry-run
    python auditorias/nodarishub/arreglar_lote_programado.py --apply
"""
import sys, os, re, time, base64, argparse, unicodedata
sys.stdout.reconfigure(encoding="utf-8")
import requests

BASE = "https://nodarishub.com"
AQUI = os.path.dirname(os.path.abspath(__file__))
PAIS = "ec"
NOMBRE_PAIS = "Ecuador"

# id -> consulta de portada en Unsplash
LOTE = {
    266: "python programming code screen",
    267: "digital marketing team meeting",
    268: "business process automation workflow",
}


def _env():
    d = {}
    for l in open(os.path.join(AQUI, "..", "..", "ecommerce-agent__.env"), encoding="utf-8"):
        if "=" in l and not l.startswith("#"):
            k, v = l.split("=", 1)
            d[k.strip()] = v.strip()
    for l in open(os.path.join(AQUI, "..", "..", "..", "agente-blogs", "agente-blogs__.env"), encoding="utf-8"):
        if l.startswith("UNSPLASH_ACCESS_KEY="):
            d["UNSPLASH_ACCESS_KEY"] = l.split("=", 1)[1].strip()
    return d


E = _env()
H = {"Authorization": "Basic " + base64.b64encode(
        f"{E.get('NODARIS_WP_USER','')}:{E.get('NODARIS_WP_APP_PASSWORD','')}".encode()).decode(),
     "Content-Type": "application/json"}
UNSPLASH = E.get("UNSPLASH_ACCESS_KEY", "")


def slugify(t, limite=60):
    p = unicodedata.normalize("NFKD", t or "").encode("ascii", "ignore").decode()
    p = re.sub(r"[^a-zA-Z0-9]+", "-", p).strip("-").lower()
    return p[:limite].strip("-") or "blog"


def ids_usados():
    usados = set()
    r = requests.get(f"{BASE}/wp-json/wp/v2/media", headers=H, timeout=30,
                     params={"per_page": 100, "search": "blog-", "_fields": "source_url"})
    for m in r.json():
        n = (m.get("source_url") or "").split("/")[-1]
        mt = re.match(r"^blog-.+-([A-Za-z0-9_-]{11})\.jpe?g$", n)
        if mt:
            usados.add(mt.group(1))
    return usados


def cat_id(slug):
    r = requests.get(f"{BASE}/wp-json/wp/v2/categories", headers=H,
                     params={"slug": slug}, timeout=20).json()
    return r[0]["id"] if r else None


def buscar_foto(query, evitar):
    r = requests.get("https://api.unsplash.com/search/photos", timeout=20,
                     params={"query": query, "per_page": 12, "orientation": "landscape",
                             "content_filter": "high"},
                     headers={"Authorization": f"Client-ID {UNSPLASH}"})
    r.raise_for_status()
    for f in r.json().get("results", []):
        if f["id"] not in evitar:
            try:
                requests.get(f["links"]["download_location"],
                             headers={"Authorization": f"Client-ID {UNSPLASH}"}, timeout=10)
            except Exception:
                pass
            return f
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    dry = not a.apply

    cid = cat_id(PAIS)
    print(f"Categoría '{PAIS}' = {cid} ({NOMBRE_PAIS})")
    evitar = ids_usados()
    print(f"Portadas ya usadas: {len(evitar)}\n")

    for pid, query in LOTE.items():
        p = requests.get(f"{BASE}/wp-json/wp/v2/posts/{pid}", headers=H,
                         params={"context": "edit"}, timeout=30).json()
        titulo = re.sub("<[^>]+>", "", p["title"]["rendered"])
        print(f"[{pid}] {p['status']:<8} {titulo[:52]}")
        print(f"       cats={p['categories']} portada={p.get('featured_media')}")

        cambios = {}
        if cid and cid not in p["categories"]:
            cambios["categories"] = sorted(set(p["categories"] + [cid]))

        if dry:
            print(f"       → asignaría país {PAIS} y portada (query: {query})\n")
            continue

        # Portada
        if not p.get("featured_media"):
            try:
                foto = buscar_foto(query, evitar)
                if foto:
                    evitar.add(foto["id"])
                    b = requests.get(foto["urls"]["regular"], timeout=45)
                    b.raise_for_status()
                    nombre = f"blog-{slugify(p['slug'])}-{foto['id']}.jpg"
                    up = requests.post(f"{BASE}/wp-json/wp/v2/media", timeout=90,
                                       headers={"Authorization": H["Authorization"],
                                                "Content-Disposition": f'attachment; filename="{nombre}"',
                                                "Content-Type": "image/jpeg"},
                                       data=b.content)
                    up.raise_for_status()
                    mid = up.json()["id"]
                    requests.post(f"{BASE}/wp-json/wp/v2/media/{mid}", headers=H, timeout=20,
                                  json={"alt_text": titulo[:125], "title": titulo[:125]})
                    cambios["featured_media"] = mid
                    print(f"       portada nueva: {nombre} (media {mid})")
                else:
                    print("       ⚠️ sin foto nueva disponible")
            except Exception as e:
                print(f"       ERROR portada: {e}")

        if not cambios:
            print("       nada que cambiar\n")
            continue

        r = requests.post(f"{BASE}/wp-json/wp/v2/posts/{pid}", headers=H,
                          json=cambios, timeout=45)
        if r.status_code == 200:
            d = r.json()
            print(f"       ✅ cats={d['categories']} portada={d.get('featured_media')}")
            print(f"       {d['link']}\n")
        else:
            print(f"       ❌ {r.status_code} {r.text[:150]}\n")
        time.sleep(0.5)

    if dry:
        print("(dry-run: no se escribió nada)")


if __name__ == "__main__":
    main()
