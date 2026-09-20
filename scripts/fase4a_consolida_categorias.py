#!/usr/bin/env python3
"""FASE 4a — 301 de las 4 categorias vacias/casi-vacias del blog hacia
/category/blog/. Via la REST API del plugin "Redirection" (John Godley),
autenticado con el mismo JWT que el resto del sitio.

    py -3 scripts/fase4a_consolida_categorias.py            # dry-run
    py -3 scripts/fase4a_consolida_categorias.py --apply
"""
from __future__ import annotations

import json
import pathlib
import sys
import time

import requests

REPO = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://peptidosysuplementos.mx"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"}
APPLY = "--apply" in sys.argv
HOY = time.strftime("%Y-%m-%d")

ORIGENES = [
    "/category/metabolismo/",
    "/category/salud-metabolica/",
    "/category/longevidad-y-regeneracion-biologica/",
    "/category/crecimiento-y-reparacion/",
]
DESTINO = "/category/blog/"


def env():
    d = {}
    for line in (REPO / "ecommerce-agent__.env").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            d[k.strip()] = v.strip().strip('"').strip("'")
    return d


ENV = env()


def jwt():
    r = requests.post(f"{SITE}/wp-json/jwt-auth/v1/token",
                      json={"username": ENV["WP_USER"], "password": ENV["WP_PASSWORD"]},
                      timeout=20)
    tok = r.json().get("token")
    if not tok:
        sys.exit(f"JWT falló: {r.status_code} {r.text[:200]}")
    return {"Authorization": f"Bearer {tok}"}


def main():
    h = jwt()

    # no duplicar si ya existe un redirect para esta url
    existentes = requests.get(f"{SITE}/wp-json/redirection/v1/redirect",
                              headers=h, params={"per_page": 200}, timeout=30).json()
    urls_existentes = {it["url"] for it in existentes.get("items", [])}

    creados = []
    for origen in ORIGENES:
        if origen in urls_existentes:
            print(f"  · {origen} ya tiene un redirect — se omite")
            continue
        payload = {
            "url": origen,
            "match_type": "url",
            "action_type": "url",
            "action_code": 301,
            "action_data": {"url": DESTINO},
            "group_id": 1,
            "match_data": {"source": {"flag_query": "exact", "flag_case": True,
                                      "flag_trailing": True, "flag_regex": False}},
        }
        print(f"  {origen}  ->  {DESTINO}")
        if APPLY:
            r = requests.post(f"{SITE}/wp-json/redirection/v1/redirect",
                              headers=h, json=payload, timeout=30)
            ok = r.status_code in (200, 201)
            print(f"      POST -> HTTP {r.status_code} {'OK' if ok else r.text[:200]}")
            creados.append({"origen": origen, "destino": DESTINO, "http": r.status_code,
                            "id": r.json().get("id") if ok else None})

    if not APPLY:
        print("\n(dry-run: no se creó nada. Usa --apply)")
        return

    print("\nverificación en vivo (con cache-bust)...")
    time.sleep(3)
    resultado = []
    for origen in ORIGENES:
        url = f"{SITE}{origen}?nc={int(time.time())}"
        r = requests.get(url, headers=UA, timeout=30, allow_redirects=True)
        final = r.url.split("?")[0]
        ok = final.rstrip("/") == f"{SITE}{DESTINO}".rstrip("/")
        print(f"  {origen}  -> HTTP final {r.status_code} en {final}  {'OK' if ok else 'FALLÓ'}")
        resultado.append({"origen": origen, "destino_final": final, "http": r.status_code, "ok": ok})

    (REPO / "docs" / "data" / f"fase4a-redirects-{HOY}.json").write_text(
        json.dumps({"fecha": HOY, "creados": creados, "verificacion": resultado},
                   ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nreporte -> docs/data/fase4a-redirects-{HOY}.json")


if __name__ == "__main__":
    main()
