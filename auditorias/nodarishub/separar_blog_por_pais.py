"""
Separación del blog de nodarishub por país (2026-08-12).

El blog era uno solo en la raíz (/slug/) mientras el resto del sitio ya vivía en
/mx/ y /ec/. Esto lo alinea: cada entrada pasa a /<pais>/blog/<slug>/.

El país de una entrada se guarda como categoría (`mx` o `ec`). El mu-plugin
`nodaris-blog-paises.php` lee esa categoría para construir el permalink, así que
la categoría es la única fuente de verdad y basta cambiarla para mover un post
de mercado.

Reparto acordado: las entradas con señal de Ecuador van a EC, el resto a MX.
No se duplica contenido entre países — son artículos distintos, no traducciones,
así que no llevan hreflang entre sí.

Uso:
    python auditorias/nodarishub/separar_blog_por_pais.py --dry-run
    python auditorias/nodarishub/separar_blog_por_pais.py --apply
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

# Ecuador: los que hablan de Ecuador o los publicó Rafa desde Quito.
EC = [157, 261, 263, 265]
# El resto va a México. 180 (aviso del benchmark) es corporativo y no de mercado,
# pero necesita un país para tener URL; va a MX con los demás.

CATEGORIAS = {"mx": "México", "ec": "Ecuador"}


def categoria(slug, nombre, dry):
    r = requests.get(f"{BASE}/wp-json/wp/v2/categories", headers=H,
                     params={"slug": slug}, timeout=20)
    hallada = r.json()
    if hallada:
        print(f"  categoría '{slug}' ya existe (id {hallada[0]['id']})")
        return hallada[0]["id"]
    if dry:
        print(f"  categoría '{slug}' se crearía")
        return None
    c = requests.post(f"{BASE}/wp-json/wp/v2/categories", headers=H,
                      json={"name": nombre, "slug": slug}, timeout=20)
    if c.status_code in (200, 201):
        print(f"  categoría '{slug}' creada (id {c.json()['id']})")
        return c.json()["id"]
    print(f"  ERROR creando '{slug}': {c.status_code} {c.text[:150]}")
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    dry = not a.apply

    print("=== CATEGORÍAS DE PAÍS ===")
    ids = {s: categoria(s, n, dry) for s, n in CATEGORIAS.items()}

    posts = requests.get(f"{BASE}/wp-json/wp/v2/posts", headers=H, timeout=30,
                         params={"per_page": 100, "status": "publish",
                                 "_fields": "id,slug,categories,title"}).json()

    print(f"\n=== ASIGNACIÓN ({len(posts)} entradas) ===")
    for p in sorted(posts, key=lambda x: x["id"]):
        pais = "ec" if p["id"] in EC else "mx"
        # Conservar las categorías que ya tiene, quitando la del otro país
        otras = [c for c in p["categories"] if c not in ids.values()]
        nuevas = sorted(set(otras + ([ids[pais]] if ids[pais] else [])))
        print(f"  [{p['id']:>3}] {pais.upper()}  {p['title']['rendered'][:56]}")
        if dry or nuevas == sorted(p["categories"]):
            continue
        r = requests.post(f"{BASE}/wp-json/wp/v2/posts/{p['id']}", headers=H,
                          json={"categories": nuevas}, timeout=30)
        if r.status_code != 200:
            print(f"        ERROR: {r.status_code} {r.text[:120]}")
        time.sleep(0.35)

    if dry:
        print("\n(dry-run: no se escribió nada)")
    else:
        print("\n✅ Categorías de país asignadas")
        print("   Las URLs no cambian hasta que se instale el mu-plugin de rutas.")


if __name__ == "__main__":
    main()
