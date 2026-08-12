"""
Últimos dos huecos del blog de nodarishub (2026-08-12): tags y huérfanos.

- Ocho entradas no tenían ninguna etiqueta. Las tarjetas del listado muestran los
  tags, así que sin ellos la tarjeta sale coja, y además se pierden las páginas
  de archivo por tema.
- Cuatro entradas no reciben ningún enlace interno. Una página huérfana se
  rastrea peor y no hereda autoridad de ninguna otra.

Los enlaces se insertan con reemplazos exactos sobre frases que ya existen, para
que queden dentro del texto y no como un bloque pegado al final.

Uso:
    python auditorias/nodarishub/tags_y_huerfanos.py --dry-run
    python auditorias/nodarishub/tags_y_huerfanos.py --apply
"""
import sys, os, time, base64, argparse
sys.stdout.reconfigure(encoding="utf-8")
import requests

BASE = "https://nodarishub.com"
AQUI = os.path.dirname(os.path.abspath(__file__))


def _env():
    d = {}
    for l in open(os.path.join(AQUI, "..", "..", "ecommerce-agent__.env"), encoding="utf-8"):
        if "=" in l and not l.startswith("#"):
            k, v = l.split("=", 1)
            d[k.strip()] = v.strip()
    return d


E = _env()
H = {"Authorization": "Basic " + base64.b64encode(
        f"{E.get('NODARIS_WP_USER','')}:{E.get('NODARIS_WP_APP_PASSWORD','')}".encode()).decode(),
     "Content-Type": "application/json"}

TAGS = {
    145: ["diseño web a código", "plantillas web", "diseño web PyME", "desarrollo web"],
    157: ["precios diseño web", "diseño web Ecuador", "presupuesto web", "PyMEs Ecuador"],
    180: ["salud técnica SEO", "WordPress", "benchmark", "datos abiertos"],
    261: ["posicionamiento web", "SEO para PyMEs", "SEM", "marketing digital"],
    262: ["diseño web a código", "HTML", "desarrollo web", "SEO técnico"],
    263: ["SEO para PyMEs", "SEM", "Google Ads", "marketing digital"],
    264: ["desarrollo web full stack", "software a la medida", "automatización de procesos"],
    265: ["posicionamiento web", "SEO para PyMEs", "SEO local", "marketing digital"],
}

# (post que enlaza, texto exacto a reemplazar, texto con el enlace)
ENLACES = [
    (262,
     "lo comparamos a fondo en <a href=\"https://nodarishub.com/pagina-web-a-codigo-vs-plantilla-cual-le-conviene-a-tu-negocio/\">página web a código vs. plantilla</a>.",
     "lo comparamos a fondo en <a href=\"https://nodarishub.com/pagina-web-a-codigo-vs-plantilla-cual-le-conviene-a-tu-negocio/\">página web a código vs. plantilla</a>, "
     "y si lo que necesitas es el paso a paso completo, en <a href=\"https://nodarishub.com/como-crear-una-pagina-web-para-negocio-2/\">cómo crear una página web para negocio</a>."),
    (145,
     "<h2 class=\"wp-block-heading\">Conclusión</h2>",
     "<p class=\"wp-block-paragraph\">Si ya te decidiste por el desarrollo a la medida y quieres entender qué hay debajo, lo explicamos en "
     "<a href=\"https://nodarishub.com/diseno-de-paginas-web-html/\">diseño de páginas web en HTML</a>.</p>\n\n"
     "<h2 class=\"wp-block-heading\">Conclusión</h2>"),
    (231,
     "<h2>Preguntas Frecuentes sobre Automatización de Procesos para PyMEs</h2>",
     "<p>Cuando la automatización deja de ser una herramienta suelta y pasa a ser un sistema propio, conviene saber qué implica: lo vemos en "
     "<a href=\"https://nodarishub.com/desarrollo-web-full-stack/\">desarrollo web full stack</a>.</p>\n\n"
     "<h2>Preguntas Frecuentes sobre Automatización de Procesos para PyMEs</h2>"),
    (263,
     "<h2>Preguntas frecuentes</h2>",
     "<p>Y si todavía te queda la duda de fondo sobre qué es y cómo funciona el lado orgánico, empieza por "
     "<a href=\"https://nodarishub.com/posicionamiento-seo-que-es/\">posicionamiento SEO, qué es</a>.</p>\n\n<h2>Preguntas frecuentes</h2>"),
]


def id_de_tag(nombre):
    r = requests.get(f"{BASE}/wp-json/wp/v2/tags", headers=H,
                     params={"search": nombre, "per_page": 20}, timeout=20)
    for t in r.json():
        if t["name"].lower() == nombre.lower():
            return t["id"]
    c = requests.post(f"{BASE}/wp-json/wp/v2/tags", headers=H, json={"name": nombre}, timeout=20)
    return c.json().get("id") if c.status_code in (200, 201) else None


def poner_tags(dry):
    print("=== TAGS ===")
    for pid, nombres in TAGS.items():
        print(f"  [{pid}] {nombres}")
        if dry:
            continue
        ids = [i for i in (id_de_tag(n) for n in nombres) if i]
        r = requests.post(f"{BASE}/wp-json/wp/v2/posts/{pid}", headers=H,
                          json={"tags": ids}, timeout=30)
        print(f"        {'✅' if r.status_code == 200 else '❌ ' + r.text[:100]} ({len(ids)} tags)")
        time.sleep(0.4)


def poner_enlaces(dry):
    print("\n=== ENLACES A HUÉRFANAS ===")
    for pid, viejo, nuevo in ENLACES:
        p = requests.get(f"{BASE}/wp-json/wp/v2/posts/{pid}", headers=H,
                         params={"context": "edit"}, timeout=30).json()
        raw = p["content"]["raw"]
        n = raw.count(viejo)
        if n != 1:
            print(f"  [{pid}] ⛔ el ancla aparece {n} veces, se salta (se esperaba 1)")
            continue
        print(f"  [{pid}] inserta enlace")
        if dry:
            continue
        r = requests.post(f"{BASE}/wp-json/wp/v2/posts/{pid}", headers=H,
                          json={"content": raw.replace(viejo, nuevo, 1)}, timeout=60)
        print(f"        {'✅' if r.status_code == 200 else '❌ ' + r.text[:100]}")
        time.sleep(0.5)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    poner_tags(not a.apply)
    poner_enlaces(not a.apply)
