"""
Crea los listados /mx/blog/ y /ec/blog/ de nodarishub (2026-08-12).

Clona la página /blog/ (id 74) como hija de /mx/ (181) y /ec/ (182), con el
buscador de guías filtrando por la categoría del país.

El JS del buscador va en base64 dentro de la página (porque `wptexturize`
corrompe los `&&` al renderizar). Para filtrar por país hay que decodificarlo,
parchear la línea del fetch y volver a codificarlo — de ahí el rodeo.

El parche hace que el widget lea la categoría de un `data-categoria` en el
contenedor, así que el mismo JS sirve para los tres listados y el país se decide
en el HTML, no en el código.

Uso:
    python auditorias/nodarishub/crear_listados_pais.py --dry-run
    python auditorias/nodarishub/crear_listados_pais.py --apply
"""
import sys, os, re, base64, argparse, time
sys.stdout.reconfigure(encoding="utf-8")
import requests

BASE = "https://nodarishub.com"
AQUI = os.path.dirname(os.path.abspath(__file__))
PAGINA_ORIGEN = 74
PADRES = {"mx": 181, "ec": 182}


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

# Línea original del widget y su reemplazo. El fetch se arma más abajo con
# '?_embed=1&per_page=100&page=' — se le añade el filtro de categoría.
VIEJO_API = "var API=(location.origin||'')+'/wp-json/wp/v2/posts';"
NUEVO_API = ("var API=(location.origin||'')+'/wp-json/wp/v2/posts';\n"
             "    var CAT=ROOT.getAttribute('data-categoria')||'';")
VIEJO_FETCH = "fetch(API+'?_embed=1&per_page=100&page='+page,{credentials:'same-origin'})"
NUEVO_FETCH = ("fetch(API+'?_embed=1&per_page=100'+(CAT?'&categories='+CAT:'')+'&page='+page,"
               "{credentials:'same-origin'})")


def cat_id(slug):
    r = requests.get(f"{BASE}/wp-json/wp/v2/categories", headers=H,
                     params={"slug": slug}, timeout=20).json()
    return r[0]["id"] if r else None


def parchear(contenido):
    """Devuelve (contenido_parcheado, informe)."""
    m = re.search(r'<script type="text/plain" id="ndh-guias-code">([^<]+)</script>', contenido)
    if not m:
        raise SystemExit("No se encontró el bloque base64 del buscador")
    js = base64.b64decode(m.group(1)).decode("utf-8")

    informe = []
    for viejo, nuevo, etiqueta in [(VIEJO_API, NUEVO_API, "API+CAT"),
                                   (VIEJO_FETCH, NUEVO_FETCH, "fetch")]:
        n = js.count(viejo)
        informe.append(f"{etiqueta}: {n} coincidencia(s)")
        if n != 1:
            raise SystemExit(f"Se esperaba 1 coincidencia de {etiqueta}, hay {n}")
        js = js.replace(viejo, nuevo, 1)

    nuevo_b64 = base64.b64encode(js.encode("utf-8")).decode("ascii")
    return contenido.replace(m.group(1), nuevo_b64), informe


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    dry = not a.apply

    origen = requests.get(f"{BASE}/wp-json/wp/v2/pages/{PAGINA_ORIGEN}", headers=H,
                          params={"context": "edit"}, timeout=30).json()
    base_contenido, informe = parchear(origen["content"]["raw"])
    print("Parche del buscador:", "; ".join(informe))

    for pais, padre in PADRES.items():
        cid = cat_id(pais)
        if not cid:
            print(f"  [{pais}] ⛔ no existe la categoría, corre antes separar_blog_por_pais.py")
            continue

        # El data-categoria vive en el contenedor del widget
        contenido = base_contenido.replace('<div id="ndh-guias">',
                                           f'<div id="ndh-guias" data-categoria="{cid}">', 1)
        if 'data-categoria' not in contenido:
            print(f"  [{pais}] ⛔ no se pudo insertar data-categoria")
            continue

        existe = requests.get(f"{BASE}/wp-json/wp/v2/pages", headers=H, timeout=20,
                              params={"slug": "blog", "parent": padre,
                                      "status": "publish,draft"}).json()
        etiqueta = "México" if pais == "mx" else "Ecuador"
        payload = {
            "title": f"Blog {etiqueta}",
            "slug": "blog",
            "parent": padre,
            "status": "publish",
            "content": contenido,
            "template": origen.get("template", ""),
        }
        print(f"  [{pais}] categoría={cid} padre={padre} "
              f"{'ACTUALIZA id ' + str(existe[0]['id']) if existe else 'CREA'}")
        if dry:
            continue
        if existe:
            r = requests.post(f"{BASE}/wp-json/wp/v2/pages/{existe[0]['id']}",
                              headers=H, json=payload, timeout=60)
        else:
            r = requests.post(f"{BASE}/wp-json/wp/v2/pages", headers=H, json=payload, timeout=60)
        if r.status_code in (200, 201):
            print(f"        ✅ {r.json()['link']}")
        else:
            print(f"        ❌ {r.status_code} {r.text[:200]}")
        time.sleep(0.6)

    if dry:
        print("\n(dry-run: no se escribió nada)")


if __name__ == "__main__":
    main()
