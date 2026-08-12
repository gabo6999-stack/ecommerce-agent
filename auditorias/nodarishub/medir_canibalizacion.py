"""
¿Cuál de cada grupo canibalizado conviene conservar?

Antes de mandar 301s hay que saber qué URL rankea de verdad: la más larga no es
necesariamente la que Google eligió. Se consulta ranked_keywords (EC y MX) y se
cruza con longitud, enlaces entrantes y antigüedad.

Uso: python auditorias/nodarishub/medir_canibalizacion.py
"""
import sys, os, json
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from dataforseo_client import DataForSEOClient

GRUPOS = {
    "cómo crear una página web": [259, 260, 270],
    "velocidad de carga web": [148, 257],
    "automatización de procesos": [150, 231],
    "google search console": [225, 240, 288],
}
# 145 (a código vs plantilla) y 237 (gratis) quedan fuera a propósito: el
# detector los agrupó por solapamiento de palabras, pero su intención es otra
# (comparativa y "gratis"), así que no compiten por la misma consulta.

AUDIT = os.path.join(os.path.dirname(__file__), "blog-auditoria-2026-08-12-post.json")


def main():
    posts = {p["id"]: p for p in json.load(open(AUDIT, encoding="utf-8"))}

    cli = DataForSEOClient()
    rankeadas = {}
    for pais, loc in [("EC", "nodaris_ec"), ("MX", "nodaris_ec")]:
        try:
            filas = cli.ranked_keywords(loc, limit=500, max_position=100)
        except Exception as e:
            print(f"[{pais}] no se pudo consultar: {e}")
            continue
        for f in filas:
            url = (((f.get("ranked_serp_element") or {}).get("serp_item") or {}).get("url") or "")
            kw = ((f.get("keyword_data") or {}).get("keyword") or "")
            pos = (((f.get("ranked_serp_element") or {}).get("serp_item") or {}).get("rank_absolute"))
            vol = (((f.get("keyword_data") or {}).get("keyword_info") or {}).get("search_volume"))
            if url:
                rankeadas.setdefault(url.rstrip("/"), []).append(
                    {"pais": pais, "kw": kw, "pos": pos, "vol": vol})
        break  # el market nodaris_ec ya trae su location; una llamada basta

    print(f"URLs del dominio con alguna posición: {len(rankeadas)}\n")

    for tema, ids in GRUPOS.items():
        print("=" * 100)
        print(f"GRUPO: {tema}")
        for pid in ids:
            p = posts.get(pid)
            if not p:
                continue
            clave = p["url"].rstrip("/")
            hits = sorted(rankeadas.get(clave, []), key=lambda h: h["pos"] or 999)[:4]
            print(f"  [{pid}] {p['palabras']:>5}p  entrantes={p['rm_incoming']:>2}  "
                  f"{p['fecha'][:10]}  {p['url'].replace('https://nodarishub.com','')}")
            print(f"        {p['titulo'][:88]}")
            if hits:
                for h in hits:
                    print(f"        ↳ RANKEA pos {h['pos']} vol {h['vol']} — {h['kw']}")
            else:
                print("        ↳ sin posiciones detectadas")
        print()


if __name__ == "__main__":
    main()
