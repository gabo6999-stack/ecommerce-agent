"""
Realinea las focus keywords de las entradas con puntaje bajo (2026-08-13).

DIAGNÓSTICO. Rank Math comprueba la keyword contra el **título SEO**, no contra
el H1, y exige la frase EXACTA. `keywordInTitle` vale 38 de los 100 puntos y
arrastra otros seis tests, así que un desajuste de una palabra hunde la nota.

Las keywords que puse el 2026-08-12 salieron de los slugs y quedaron largas y
ligeramente desalineadas ("crear página web para negocio en 2026" cuando el
título dice "crear una página web..."). Ese era el fallo, no el contenido: son
artículos de 2.800-2.900 palabras.

Se corrige por el lado más barato de cada caso:
- si el título SEO ya contiene una keyword mejor → se cambia la keyword;
- si no → se ajusta el título SEO para que la contenga, sin pasar de 60 chars.

Volúmenes medidos con DataForSEO (México, loc 2484) antes de elegir, para no
optimizar hacia frases que nadie busca.

Uso:
    python auditorias/nodarishub/realinear_keywords.py --dry-run
    python auditorias/nodarishub/realinear_keywords.py --apply
"""
import sys, os, time, base64, argparse, unicodedata
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

# id -> (keyword nueva, título SEO nuevo o None si el actual ya sirve, nota)
PLAN = {
    270: ("cómo crear una página web", None,
          "4.400/mes KD51. Ya está literal en el título actual; solo sobraba la keyword vieja."),
    231: ("automatización de procesos", None,
          "1.600/mes KD14, 5x la anterior (320) y también winnable. Ya está en el título."),
    288: ("google search console", None,
          "Está en el título; sube la nota. OJO: 22.200/mes pero KD94 y NAVEGACIONAL — "
          "la consulta la gana Google con su propio producto. No esperar ranking."),
    162: ("página web a la medida", "Página web a la medida para PyMEs | Nodarishub",
          "El título decía 'a medida' y la keyword 'a la medida'. OJO: la familia entera "
          "mide CERO volumen en México."),
    257: ("velocidad de carga de una página web", "Velocidad de carga de una página web | Nodarishub",
          "Se alinea el título. OJO: solo 40/mes; la familia es diminuta en México."),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    dry = not a.apply

    for pid, (kw, titulo, nota) in PLAN.items():
        p = requests.get(f"{BASE}/wp-json/wp/v2/posts/{pid}", headers=H,
                         params={"context": "edit", "_fields": "slug,title"}, timeout=30).json()
        meta = {"rank_math_focus_keyword": kw}
        if titulo:
            meta["rank_math_title"] = titulo
        print(f"[{pid}] kw -> '{kw}'" + (f"  ({len(titulo)}c) título -> '{titulo}'" if titulo else "  (título actual sirve)"))
        print(f"       {nota}")
        if dry:
            print()
            continue
        r = requests.post(f"{BASE}/wp-json/rankmath/v1/updateMeta", headers=H, timeout=30,
                          json={"objectID": pid, "objectType": "post", "meta": meta})
        print(f"       {'✅' if r.status_code == 200 else '❌ ' + r.text[:120]}")
        if r.status_code == 200:
            # purge-on-update de LiteSpeed
            requests.post(f"{BASE}/wp-json/wp/v2/posts/{pid}", headers=H,
                          json={"slug": p["slug"]}, timeout=30)
        print()
        time.sleep(0.4)

    if dry:
        print("(dry-run: no se escribió nada)")
    else:
        print("Hecho. Falta reabrir cada entrada en el editor para que Rank Math")
        print("recalcule y volver a persistir el puntaje.")


if __name__ == "__main__":
    main()
