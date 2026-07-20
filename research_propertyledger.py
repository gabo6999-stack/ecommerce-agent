"""
research_propertyledger.py
==========================
Investigación DataForSEO one-shot para propertyledger.us (mercado US, inglés).
Replica la metodología usada con arcade/nodaris_ec:

  1. Baseline: dónde rankea YA propertyledger.us (top-20).
  2. Competidores REALES: mide ranked_keywords de varios candidatos y los
     ordena por footprint (nº de keywords top-20 + suma de volumen).
  3. Universo de keywords: keyword_suggestions por cada semilla, TODAS las
     intenciones (para optimizar páginas comerciales + escribir blogs
     informacionales). Etiqueta intención real con search_intent.
  4. Content gap: keywords donde el competidor top rankea y nosotros no.

Vuelca todo a un JSON (el "cache") que luego alimenta el calendario de blogs
y la optimización on-page de páginas/landings/blogs existentes.

Uso:
    python research_propertyledger.py
"""

from __future__ import annotations

import json
import logging
import os
import sys

from dotenv import load_dotenv

load_dotenv("ecommerce-agent__.env", override=True)

from dataforseo_client import DataForSEOClient, get_market  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger("research")

SLUG = "propertyledger"

# Semillas verificadas contra el contenido real del sitio (home + 2 servicios +
# 4 blogs). Cubren servicio (comercial) e informacional.
SEEDS = [
    "property management accounting",
    "property management bookkeeping",
    "trust accounting",
    "hoa accounting",
    "condo association accounting",
    "owner statements",
    "property management financial statements",
    "outsourced accounting",
]

# Candidatos a competidor a MEDIR (no asumidos). Mezcla de:
#  - servicios de bookkeeping/accounting para property managers (directos)
#  - blogs de software PM que dominan las SERPs informacionales del nicho
CANDIDATE_COMPETITORS = [
    "doorloop.com",
    "buildium.com",
    "appfolio.com",
    "apmhelp.com",
    "hemlane.com",
    "rentecdirect.com",
    "stessa.com",
    "baselane.com",
    "propertymatics.com",
]

OUT_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "propertyledger_keyword_cache.json",
)


def footprint(client: DataForSEOClient, domain: str) -> dict:
    """Nº de keywords top-20 + suma de volumen como proxy de fuerza orgánica."""
    rows = client.ranked_keywords(SLUG, target=domain, limit=1000, max_position=20)
    total_vol = sum(r["volume"] or 0 for r in rows)
    return {
        "domain": domain,
        "ranked_kw_top20": len(rows),
        "sum_volume_top20": total_vol,
        "capped": len(rows) >= 1000,
        "sample": sorted(rows, key=lambda r: r["volume"] or 0, reverse=True)[:15],
    }


def main() -> None:
    cli = DataForSEOClient()
    m = get_market(SLUG)
    print(f"\n== {m.name} | location {m.location_code} | {m.target} | lang {m.language_code} ==\n")

    cache: dict = {
        "generated_for": m.target,
        "location_code": m.location_code,
        "language_code": m.language_code,
        "seeds": SEEDS,
    }

    # 1. Baseline propio ------------------------------------------------------
    log.info("Baseline: ranked_keywords de %s", m.target)
    own = cli.ranked_keywords(SLUG, limit=1000, max_position=100)
    cache["own_ranked"] = own
    print(f"[baseline] {m.target} rankea (top-100) en {len(own)} keywords\n")

    # 2. Competidores reales --------------------------------------------------
    comps = []
    for d in CANDIDATE_COMPETITORS:
        try:
            fp = footprint(cli, d)
            comps.append(fp)
            print(f"[competitor] {d:<24} {fp['ranked_kw_top20']:>5} kw top20 | "
                  f"vol {fp['sum_volume_top20']:>9,}{' (capped)' if fp['capped'] else ''}")
        except Exception as e:  # noqa: BLE001
            print(f"[competitor] {d:<24} ERROR: {e}")
    comps.sort(key=lambda c: (c["ranked_kw_top20"], c["sum_volume_top20"]), reverse=True)
    cache["competitors_measured"] = comps

    # 3. Universo de keywords (todas las intenciones) -------------------------
    universe: dict[str, dict] = {}
    for seed in SEEDS:
        try:
            for k in cli.keyword_suggestions(SLUG, seed, limit=300):
                if k["keyword"] and k["keyword"] not in universe:
                    universe[k["keyword"]] = k
        except Exception as e:  # noqa: BLE001
            print(f"[suggestions] '{seed}' ERROR: {e}")
    rows = list(universe.values())
    print(f"\n[universe] {len(rows)} keywords únicas de {len(SEEDS)} semillas")

    # Etiquetar intención real (search_intent) para las de mayor volumen ------
    top_for_intent = sorted(rows, key=lambda r: r["volume"] or 0, reverse=True)[:900]
    try:
        intents = cli.search_intent(SLUG, [r["keyword"] for r in top_for_intent])
        for r in rows:
            lab = intents.get(r["keyword"])
            if lab:
                r["intent"] = lab
        print(f"[intent] etiquetadas {len(intents)} keywords")
    except Exception as e:  # noqa: BLE001
        print(f"[intent] ERROR: {e}")
    rows.sort(key=lambda r: r["volume"] or 0, reverse=True)
    cache["keyword_universe"] = rows

    # 4. Content gap vs el competidor más fuerte medido ----------------------
    if comps:
        rival = comps[0]["domain"]
        try:
            gap = cli.content_gap(SLUG, competitor=rival, limit=1000, max_difficulty=45)
            cache["content_gap"] = {"vs": rival, "opportunities": gap}
            print(f"\n[gap] vs {rival}: {len(gap)} oportunidades (KD<=45)")
        except Exception as e:  # noqa: BLE001
            print(f"[gap] ERROR: {e}")

    cache["total_cost_usd"] = round(cli.total_cost, 5)

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

    print(f"\n== Cache escrito en {OUT_PATH} ==")
    print(f"== Costo total de la corrida: ${cli.total_cost:.5f} USD ==")


if __name__ == "__main__":
    sys.exit(main())
