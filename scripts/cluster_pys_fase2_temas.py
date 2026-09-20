#!/usr/bin/env python3
"""Fase 2 — paso 2: limpiar el pool y agrupar por tema. SIN costo de API.

Corrige el filtro del paso 1 (el 'nad' suelto capturaba fexofeNADina /
boNADoxina) y separa el péptido de investigación (catálogo PYS) del péptido
de colágeno/cobre, que es otro mercado.
"""
from __future__ import annotations

import json
import pathlib
import re
from collections import defaultdict

REPO = pathlib.Path(__file__).resolve().parent.parent
POOL = REPO / "docs" / "data" / "cluster-pys-pool.json"
OUT = REPO / "docs" / "data" / "cluster-pys-temas.json"

d = json.load(open(POOL, encoding="utf-8"))
pool = d["pool"]

# --- ruido: otro mercado, no es el catálogo de PYS ---
EXCLUIR = re.compile(
    r"col[aá]geno|de cobre|capilar|cabello|piel|crema|serum|s[eé]rum|"
    r"shampoo|facial|arrugas|cosm[eé]tic|uñas|"
    r"fexofenadin|bonadoxin|loratadin|paracetamol|ibuprofen",
    re.IGNORECASE,
)
# --- relevante de verdad: catálogo o categoría de péptidos de investigación ---
RELEVANTE = re.compile(
    r"p[eé]ptid|bpc|tb-?500|semaglutid|tirzepatid|retatrutid|cagrilintid|"
    r"ipamorelin|sermorelin|cjc|mots-?c|igf-?1|selank|thymosin|timosin|"
    r"glutati[oó]n|\bnad\b|nad\+|bacteriost|liofiliz|\bhgh\b|ghrp|ghrh|"
    r"hexarelin|melanotan|epitalon|tesamorelin|\baod\b|\bdsip\b|kisspeptin|amilina",
    re.IGNORECASE,
)

# --- temas (orden importa: la primera que casa gana) ---
TEMAS = [
    ("GLP-1 / pérdida de peso", re.compile(
        r"semaglutid|tirzepatid|retatrutid|cagrilintid|amilina|ozempic|mounjaro|"
        r"wegovy|bajar de peso|p[eé]rdida de peso|adelgaz|obesidad|saciedad", re.I)),
    ("Reparación / recuperación", re.compile(
        r"bpc|tb-?500|reparaci[oó]n|recuperaci[oó]n|lesi[oó]n|tend[oó]n|"
        r"articula|cicatriz|desgarr", re.I)),
    ("GH / longevidad", re.compile(
        r"ipamorelin|sermorelin|cjc|ghrp|ghrh|hexarelin|tesamorelin|\bhgh\b|"
        r"hormona de crecimiento|igf-?1|epitalon|antienvejec|longevidad|"
        r"mots-?c|\bnad\b|nad\+", re.I)),
    ("Inmunidad / antioxidante", re.compile(
        r"thymosin|timosin|glutati[oó]n|inmun|antioxidant|detox", re.I)),
    ("Cognitivo", re.compile(r"selank|semax|noopept|dsip|cognitiv|ansiedad|sue[ñn]o", re.I)),
    ("Protocolo / uso / aplicación", re.compile(
        r"bacteriost|liofiliz|reconstitu|dosis|dosifica|aplicar|aplicaci[oó]n|"
        r"inyect|jeringa|conservar|refriger|almacen|protocolo|ciclo", re.I)),
    ("Seguridad / efectos", re.compile(
        r"efecto|secundario|riesgo|peligro|seguro|contraindicaci|da[ñn]in|legal", re.I)),
    ("Educacional / qué son", re.compile(
        r"qu[eé] son|que son|qu[eé] es|que es|para qu[eé] sirve|para que sirve|"
        r"c[oó]mo funciona|tipos de|beneficios", re.I)),
    ("Compra / precio", re.compile(
        r"precio|comprar|venta|donde|d[oó]nde|costo|cu[aá]nto cuesta|barato|"
        r"tienda|farmacia|similares", re.I)),
]

limpio = []
for v in pool:
    kw = v["keyword"]
    if EXCLUIR.search(kw) or not RELEVANTE.search(kw):
        continue
    if not (v.get("volume") or 0) > 0:
        continue
    limpio.append(v)

por_tema = defaultdict(list)
for v in limpio:
    kw = v["keyword"]
    for nombre, rx in TEMAS:
        if rx.search(kw):
            por_tema[nombre].append(v)
            break
    else:
        por_tema["(sin tema)"].append(v)

print(f"=== pool crudo {len(pool)} -> limpio {len(limpio)} keywords ===")
print(f"=== volumen limpio total: {sum(v['volume'] for v in limpio):,}/mes ===\n")

resumen = {}
for nombre, _ in TEMAS + [("(sin tema)", None)]:
    kws = por_tema.get(nombre) or []
    if not kws:
        continue
    kws.sort(key=lambda v: -v["volume"])
    vol = sum(v["volume"] for v in kws)
    intents = defaultdict(int)
    for v in kws:
        intents[v.get("intent") or "?"] += v["volume"]
    mix = ", ".join(f"{k} {100*n//vol}%" for k, n in
                    sorted(intents.items(), key=lambda x: -x[1])[:3])
    print(f"── {nombre}: {len(kws)} kw | {vol:,}/mes | {mix}")
    for v in kws[:8]:
        print(f"     {v['volume']:>6}  {str(v.get('intent') or '?'):<14} {v['keyword']}")
    print()
    resumen[nombre] = {"n": len(kws), "volumen": vol,
                       "keywords": [v["keyword"] for v in kws]}

json.dump({"temas": resumen, "limpio": limpio}, open(OUT, "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print(f"Guardado en {OUT}")
