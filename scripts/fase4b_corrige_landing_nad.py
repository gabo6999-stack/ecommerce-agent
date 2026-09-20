#!/usr/bin/env python3
"""FASE 4b -- correcciones a la landing NAD+ (page_id 2418) pedidas en
revision: contenido (H1 duplicado, fusion de secciones, bloque "Revisado
por"), imagen social, y schema (FAQPage + Person/reviewedBy tipo ficha).
La pagina se queda en DRAFT -- no cambia el status.

    py -3 scripts/fase4b_corrige_landing_nad.py            # dry-run
    py -3 scripts/fase4b_corrige_landing_nad.py --apply
"""
from __future__ import annotations

import json
import pathlib
import re
import sys
import time
import uuid

import requests

REPO = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://peptidosysuplementos.mx"
PAGE_ID = 2418
APPLY = "--apply" in sys.argv
HOY = time.strftime("%Y-%m-%d")
CONTENT_FILE = REPO / "docs" / "contenido" / "landing-nad-que-es-para-que-sirve.html"

IMG_ID = 2274
IMG_URL = "https://peptidosysuplementos.mx/wp-content/uploads/2026/07/NAD-500mg-v4.png"


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


def extrae_faq(html):
    """[(pregunta, respuesta_texto_plano), ...] de los <h3>/<p> del bloque FAQ."""
    pares = []
    for m in re.finditer(r"<h3>(.*?)</h3>\s*<p>(.*?)</p>", html, re.S):
        preg = re.sub(r"<[^>]+>", "", m.group(1)).strip()
        resp = re.sub(r"<[^>]+>", "", m.group(2)).strip()
        resp = re.sub(r"\s+", " ", resp)
        pares.append((preg, resp))
    return pares


def main():
    html = CONTENT_FILE.read_text(encoding="utf-8")
    faq = extrae_faq(html)
    print(f"contenido: {len(html)} caracteres")
    print(f"FAQ detectada: {len(faq)} pares pregunta/respuesta")
    for p, r in faq:
        print(f"   - {p}")

    medical_schema = {
        "@context": "https://schema.org",
        "@type": "MedicalWebPage",
        "name": "NAD+: qué es y para qué sirve",
        "url": f"{SITE}/nad-que-es-y-para-que-sirve/",
        "lastReviewed": HOY,
        "reviewedBy": {
            "@type": "Person",
            "name": "Antonio Gavito Hernández",
            "honorificPrefix": "Dr.",
            "jobTitle": "Médico cirujano",
            "identifier": {
                "@type": "PropertyValue",
                "propertyID": "Cédula profesional (México)",
                "value": "4606965",
            },
            "description": "Práctica enfocada en medicina de longevidad y terapias con péptidos",
        },
        "medicalAudience": {"@type": "Patient"},
        "isAccessibleForFree": True,
        "inLanguage": "es-MX",
    }

    faq_schema = {
        "@type": "FAQPage",
        "metadata": {
            "title": "FAQ",
            "type": "template",
            "shortcode": f"s-{uuid.uuid4().hex[:13]}",
            "isPrimary": 0,
            "reviewLocation": "custom",
        },
        "mainEntity": [
            {"@type": "Question", "name": p,
             "acceptedAnswer": {"@type": "Answer", "text": r}}
            for p, r in faq
        ],
    }

    # Rank Math/updateSchemas NO persiste para este tipo de contenido (probado:
    # dispatch real vía el editor + guardar tampoco lo hizo persistir -- FAQ
    # es PRO-only en el Schema Generator y MedicalWebPage ni siquiera es un
    # tipo del generador). Mecanismo que SÍ funciona, verificado en vivo:
    # <script type="application/ld+json"> embebido directo en el contenido
    # de la página SÍ sobrevive (a diferencia de wc/v3 en productos) y SÍ
    # renderiza. Mismo patrón que el inyector PHP de las fichas, solo que
    # aquí va en el body en vez de wp_head.
    faq_jsonld = {"@context": "https://schema.org", **faq_schema}
    del faq_jsonld["metadata"]
    html_con_schema = (
        html
        + f'\n<script type="application/ld+json">{json.dumps(faq_jsonld, ensure_ascii=False)}</script>'
        + f'\n<script type="application/ld+json">{json.dumps(medical_schema, ensure_ascii=False)}</script>\n'
    )

    print("\n--- schema Person/reviewedBy (MedicalWebPage) ---")
    print(json.dumps(medical_schema, ensure_ascii=False, indent=1))
    print(f"\n--- schema FAQPage: {len(faq_schema['mainEntity'])} preguntas ---")

    if not APPLY:
        print("\n(dry-run: no se escribe nada. Usa --apply)")
        return

    h = jwt()

    # 1) contenido corregido (H1 único, secciones fusionadas, revisado-por,
    #    + los 2 <script> de schema embebidos al final)
    r1 = requests.post(f"{SITE}/wp-json/wp/v2/pages/{PAGE_ID}", headers=h, timeout=30,
                       json={"content": html_con_schema, "featured_media": IMG_ID})
    p1 = r1.json()
    print(f"\ncontenido + featured_media + schema embebido: HTTP {r1.status_code}  status={p1.get('status')}")

    # 2) imagen social (og:image / twitter:image) explícita, sobreescribe el fallback
    r2 = requests.post(f"{SITE}/wp-json/rankmath/v1/updateMeta", headers=h, timeout=20, json={
        "objectID": PAGE_ID, "objectType": "post",
        "meta": {"rank_math_facebook_image": IMG_URL, "rank_math_twitter_image": IMG_URL},
    })
    print(f"imagen social: HTTP {r2.status_code} {r2.text[:150]}")

    reporte = {"fecha": HOY, "page_id": PAGE_ID, "featured_media": IMG_ID,
              "og_image": IMG_URL, "faq_preguntas": len(faq),
              "schema_embebido_en_contenido": True}
    (REPO / "docs" / "data" / f"fase4b-landing-nad-fixes-{HOY}.json").write_text(
        json.dumps(reporte, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nreporte -> docs/data/fase4b-landing-nad-fixes-{HOY}.json")
    print("\nLA PÁGINA SIGUE EN DRAFT. No se cambió el status.")


if __name__ == "__main__":
    main()
