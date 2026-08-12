"""
Consolidación de los grupos canibalizados del blog de nodarishub (2026-08-12).

Cuatro grupos de entradas competían por la misma consulta. Se conserva una de
cada grupo y las demás se redirigen 301 hacia ella.

Por qué ahora y por qué sin miedo: se midió con DataForSEO que nodarishub.com
tiene CERO posiciones en el top 100 en Ecuador y en México, así que ninguna de
las URLs que se retiran tiene autoridad de ranking que perder. Consolidar antes
de empezar a rankear es justo el momento barato de hacerlo.

Qué hace por cada entrada retirada:
  1. respalda el HTML completo a disco (nada se pierde, todo es reversible),
  2. crea la redirección 301 en Rank Math,
  3. la pasa a borrador para que salga del listado y del sitemap,
  4. reescribe los enlaces internos que la apuntaban para que vayan al ganador.

Uso:
    python auditorias/nodarishub/consolidar_canibalizacion.py --dry-run
    python auditorias/nodarishub/consolidar_canibalizacion.py --apply
"""
import sys, os, re, json, time, base64, argparse
sys.stdout.reconfigure(encoding="utf-8")
import requests
from bs4 import BeautifulSoup

BASE = "https://nodarishub.com"
AQUI = os.path.dirname(os.path.abspath(__file__))
RESPALDOS = os.path.join(AQUI, "backups-consolidacion-2026-08-12")


def _env():
    ruta = os.path.join(AQUI, "..", "..", "ecommerce-agent__.env")
    d = {}
    for linea in open(ruta, encoding="utf-8"):
        if "=" in linea and not linea.startswith("#"):
            k, v = linea.split("=", 1)
            d[k.strip()] = v.strip()
    return d


E = _env()
USER = os.environ.get("NODARIS_WP_USER") or E.get("NODARIS_WP_USER", "")
PW = os.environ.get("NODARIS_WP_APP_PASSWORD") or E.get("NODARIS_WP_APP_PASSWORD", "")
H = {"Authorization": "Basic " + base64.b64encode(f"{USER}:{PW}".encode()).decode(),
     "Content-Type": "application/json"}
PUB = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120"}

# retirada -> ganadora. El ganador de cada grupo es el más largo y completo;
# como nadie rankea, longitud y coincidencia del slug con el término principal
# son los criterios que quedan.
PLAN = {
    259: 270,   # "cómo crear una página web"        -> el de 2.881 palabras
    260: 270,
    148: 257,   # "velocidad de carga"               -> slug que calza el término
    150: 231,   # "automatización de procesos"       -> el de 2026, no el de 2025
    225: 288,   # "google search console"            -> el más largo y reciente
    240: 288,
}
# Fuera del plan a propósito: 145 (a código vs plantilla) y 237 (gratis) se
# agruparon por solapamiento de palabras, pero responden a otra intención.


def obtener(pid, contexto="edit"):
    r = requests.get(f"{BASE}/wp-json/wp/v2/posts/{pid}", headers=H,
                     params={"context": contexto}, timeout=30)
    r.raise_for_status()
    return r.json()


def todos_los_posts():
    out, page = {}, 1
    while True:
        r = requests.get(f"{BASE}/wp-json/wp/v2/posts", headers=H, timeout=30,
                         params={"per_page": 50, "page": page, "context": "edit",
                                 "status": "publish,draft"})
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


def respaldar(posts):
    os.makedirs(RESPALDOS, exist_ok=True)
    for pid in sorted(set(PLAN) | set(PLAN.values())):
        p = posts.get(pid)
        if not p:
            continue
        destino = os.path.join(RESPALDOS, f"post-{pid}.json")
        with open(destino, "w", encoding="utf-8") as fh:
            json.dump(p, fh, ensure_ascii=False, indent=2)
    print(f"  Respaldo de {len(set(PLAN) | set(PLAN.values()))} entradas en {RESPALDOS}")


def activar_modulo_redirecciones(dry):
    """El módulo de redirecciones de Rank Math venía apagado en este sitio y sin
    él updateRedirection responde 403 rest_cannot_edit."""
    if dry:
        return
    r = requests.post(f"{BASE}/wp-json/rankmath/v1/saveModule", headers=H, timeout=30,
                      json={"module": "redirections", "state": "on"})
    print(f"  Módulo redirections: {r.status_code} {r.text[:60]}")


def crear_redireccion(pid, destino_url, dry):
    if dry:
        return True
    r = requests.post(f"{BASE}/wp-json/rankmath/v1/updateRedirection", headers=H, timeout=30,
                      json={"objectID": pid, "objectType": "post", "hasRedirect": True,
                            "redirectionUrl": destino_url, "redirectionType": "301"})
    if r.status_code == 200:
        return True
    print(f"        ERROR redirección {pid}: {r.status_code} {r.text[:200]}")
    return False


def a_borrador(pid, dry):
    if dry:
        return True
    r = requests.post(f"{BASE}/wp-json/wp/v2/posts/{pid}", headers=H,
                      json={"status": "draft"}, timeout=30)
    if r.status_code == 200:
        return True
    print(f"        ERROR borrador {pid}: {r.status_code} {r.text[:200]}")
    return False


def reescribir_enlaces(posts, dry):
    """Los enlaces internos deben apuntar al ganador, no encadenar un 301."""
    mapa = {}
    for retirada, ganadora in PLAN.items():
        if retirada in posts and ganadora in posts:
            mapa[posts[retirada]["link"].rstrip("/")] = posts[ganadora]["link"].rstrip("/")
    print(f"\n  Reescribiendo enlaces internos ({len(mapa)} URLs retiradas)")
    tocados = 0
    for pid, p in posts.items():
        if pid in PLAN:
            continue  # la retirada se va a borrador, da igual su cuerpo
        html = p.get("content", {}).get("raw") or ""
        nuevo, cambios = html, 0
        for viejo, destino in mapa.items():
            for variante in (viejo + "/", viejo):
                if variante in nuevo:
                    n = nuevo.count(variante)
                    nuevo = nuevo.replace(variante, destino + "/")
                    cambios += n
        if not cambios:
            continue
        print(f"    [{pid}] {cambios} enlace(s) reapuntado(s)")
        tocados += 1
        if dry:
            continue
        r = requests.post(f"{BASE}/wp-json/wp/v2/posts/{pid}", headers=H,
                          json={"content": nuevo}, timeout=45)
        if r.status_code != 200:
            print(f"        ERROR actualizando {pid}: {r.status_code} {r.text[:150]}")
        time.sleep(0.4)
    print(f"  → {tocados} entradas con enlaces corregidos")


def verificar(posts):
    print("\n=== VERIFICACIÓN EN VIVO ===")
    ok = 0
    for retirada, ganadora in PLAN.items():
        origen = posts[retirada]["link"]
        esperado = posts[ganadora]["link"].rstrip("/")
        try:
            r = requests.get(origen, headers=PUB, allow_redirects=False, timeout=30,
                             params={"nocache": int(time.time())})
            destino = (r.headers.get("Location") or "").rstrip("/")
            bien = r.status_code in (301, 308) and destino == esperado
            print(f"  [{retirada}] {r.status_code} -> {destino.replace(BASE,'') or '(ninguno)'} "
                  f"{'✅' if bien else '❌ esperaba ' + esperado.replace(BASE,'')}")
            ok += bien
        except Exception as e:
            print(f"  [{retirada}] ERROR: {e}")
    print(f"  → {ok}/{len(PLAN)} redirecciones correctas")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--solo-verificar", action="store_true")
    a = ap.parse_args()
    dry = not a.apply

    posts = todos_los_posts()
    print(f"Entradas en el sitio: {len(posts)}\n")

    if a.solo_verificar:
        verificar(posts)
        return

    print("=== PLAN DE CONSOLIDACIÓN ===")
    for retirada, ganadora in PLAN.items():
        pr, pg = posts.get(retirada), posts.get(ganadora)
        if not pr or not pg:
            print(f"  [{retirada}] falta información, se salta")
            continue
        print(f"  RETIRA [{retirada}] {pr['title']['rendered'][:58]}")
        print(f"     301→ [{ganadora}] {pg['title']['rendered'][:58]}")

    if dry:
        print("\n(dry-run: no se escribió nada)")
        reescribir_enlaces(posts, dry=True)
        return

    print("\n=== RESPALDO ===")
    respaldar(posts)

    print("\n=== REDIRECCIONES Y BORRADORES ===")
    activar_modulo_redirecciones(dry=False)
    for retirada, ganadora in PLAN.items():
        # Ya en borrador = ya consolidada; repetir crearía una redirección duplicada.
        if posts[retirada].get("status") == "draft":
            print(f"  [{retirada}] ya consolidada, se salta")
            continue
        destino = posts[ganadora]["link"]
        print(f"  [{retirada}] -> {destino.replace(BASE,'')}")
        if crear_redireccion(retirada, destino, dry=False):
            a_borrador(retirada, dry=False)
        time.sleep(0.5)

    reescribir_enlaces(posts, dry=False)
    time.sleep(4)
    verificar(posts)


if __name__ == "__main__":
    main()
