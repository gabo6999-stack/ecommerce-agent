"""
build_propertyledger_cache.py
=============================
Toma el volcado crudo de DataForSEO (propertyledger_keyword_cache.json) y produce
el CACHE curado que consumen (a) el Blog Agent para publicar las próximas semanas
y (b) la optimización on-page de páginas/landings/blogs existentes.

Salida:
  agente-blogs-raditech/content_cache/propertyledger.json   (lo lee el agente)
  agente-blogs-raditech/content_cache/propertyledger_plan.md (para humanos)

La curación (qué temas, a qué página va cada keyword) es juicio editorial;
los volúmenes/KD se leen de los datos reales medidos, no se inventan.
"""

from __future__ import annotations

import json
import os
import re

RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "propertyledger_keyword_cache.json")
OUT_DIR = r"C:\Users\gabom\Proyectos\agente-blogs-raditech\content_cache"
OUT_JSON = os.path.join(OUT_DIR, "propertyledger.json")
OUT_MD = os.path.join(OUT_DIR, "propertyledger_plan.md")

STOP = {"for", "of", "a", "the", "and", "in", "to", "is", "what", "are", "my", "your", "with", "on"}


def norm(kw: str) -> str:
    toks = [t for t in re.sub(r"[^a-z0-9 ]", "", kw.lower()).split() if t not in STOP]
    toks = [t[:-1] if t.endswith("s") and len(t) > 3 else t for t in toks]
    return " ".join(sorted(toks))


def load_universe() -> dict[str, dict]:
    raw = json.load(open(RAW, encoding="utf-8"))
    by_kw = {r["keyword"]: r for r in raw["keyword_universe"]}
    return by_kw, raw


def lookup(by_kw: dict, keyword: str) -> dict:
    """Busca una keyword exacta; si no, la mejor variante del mismo cluster."""
    if keyword in by_kw:
        r = by_kw[keyword]
        return {"keyword": keyword, "volume": r["volume"], "kd": r["difficulty"], "intent": r.get("intent")}
    target = norm(keyword)
    best = None
    for k, r in by_kw.items():
        if norm(k) == target:
            if best is None or (r["volume"] or 0) > (best["volume"] or 0):
                best = {"keyword": k, "volume": r["volume"], "kd": r["difficulty"], "intent": r.get("intent")}
    return best or {"keyword": keyword, "volume": None, "kd": None, "intent": None}


def clustered_bank(by_kw: dict, intent: str, min_vol: int = 40) -> list[dict]:
    cl: dict[str, dict] = {}
    for r in by_kw.values():
        if r.get("intent") != intent or (r["volume"] or 0) < min_vol:
            continue
        k = norm(r["keyword"])
        cur = cl.get(k)
        if cur is None:
            cl[k] = {"keyword": r["keyword"], "volume": r["volume"] or 0, "kd": r["difficulty"], "variants": 1}
        else:
            cur["variants"] += 1
            if (r["volume"] or 0) > cur["volume"]:
                cur["volume"] = r["volume"] or 0
                cur["keyword"] = r["keyword"]
            if r["difficulty"] is not None and (cur["kd"] is None or r["difficulty"] < cur["kd"]):
                cur["kd"] = r["difficulty"]
    return sorted(cl.values(), key=lambda x: x["volume"], reverse=True)


# --------------------------------------------------------------------------- #
# CURACIÓN EDITORIAL
# --------------------------------------------------------------------------- #
# Blog queue: temas informacionales achievable, DIFERENCIADOS de lo ya publicado
# (trust accounting reconciliation, PM financial statements, month-end closing,
# owner statements, in-house vs outsourced). Orden = prioridad de publicación.
# primary_kw se resuelve contra los datos medidos.
BLOG_QUEUE = [
    ("What is trust accounting in property management? A plain-English guide with examples",
     "what is trust accounting", "trust-accounting-explainer"),
    ("HOA accounting basics: a guide for board members and treasurers",
     "hoa accounting", "hoa-accounting-basics"),
    ("Property management bookkeeping vs. accounting: what's the difference (and what you need)",
     "property management bookkeeping", "bookkeeping-vs-accounting"),
    ("Real estate trust accounting: the rules every property manager must follow",
     "real estate trust accounting", "real-estate-trust-accounting-rules"),
    ("HOA reserve fund accounting: how to track, fund and report reserves correctly",
     "reserve fund accounting for hoa", "hoa-reserve-fund-accounting"),
    ("Trust accounting rules for property managers: a state-by-state overview (Florida focus)",
     "trust accounting rules", "trust-accounting-rules-by-state"),
    ("Commingling of funds: the trust accounting mistake that gets property managers in trouble",
     "trust accounting law", "commingling-of-funds"),
    ("Security deposit accounting for property managers: compliance and best practices",
     "real estate trust accounting", "security-deposit-accounting"),
    ("How to do trust accounting in QuickBooks for property management",
     "quickbooks trust accounting", "quickbooks-trust-accounting"),
    ("Setting up a property management chart of accounts the right way",
     "property management bookkeeping", "property-management-chart-of-accounts"),
    ("Free trust accounting template + sample owner statement (and how to use them)",
     "trust accounting template excel", "trust-accounting-template"),
    ("5 signs your property management company needs professional accounting help",
     "what is outsourced accounting", "signs-you-need-accounting-help"),
    ("What is outsourced accounting and how does it work for property managers?",
     "what is outsourced accounting", "what-is-outsourced-accounting"),
    ("HOA & condo financial statements: what boards should review every month",
     "hoa accounting", "hoa-condo-financial-statements"),
    ("1099 filing for property managers: vendor payments and owner distributions explained",
     "bookkeeping for property management", "1099-filing-property-managers"),
]

# Optimización on-page de lo que YA existe. focus_kw recomendado resuelto vs datos.
PAGE_OPT = [
    {"url": "https://propertyledger.us/", "type": "page", "current_focus": "accounting for property management",
     "recommended_focus": "accounting for property management", "secondary": ["outsourced accounting firm", "property management bookkeeping"],
     "note": "Mantener focus (KD0). Enriquecer con el ángulo 'outsourced accounting firm' (KD1-7, 720-2900 vol) que hoy no se captura. Interlink a los 2 servicios + nuevos blogs."},
    {"url": "https://propertyledger.us/monthly-accounting/", "type": "page", "current_focus": "property management accounting service",
     "recommended_focus": "property management accounting service", "secondary": ["property management bookkeeping", "monthly financial statements property management"],
     "note": "Diferenciar de /property-management-accounting/: esta es el SERVICIO recurrente mensual (close, statements, AP/AR). Añadir 'bookkeeping' como secundaria (KD0, 320)."},
    {"url": "https://propertyledger.us/property-management-accounting/", "type": "page", "current_focus": "accounting for property management companies",
     "recommended_focus": "property management trust accounting", "secondary": ["real estate trust accounting", "owner statements", "commingling"],
     "note": "RIESGO DE CANIBALIZACIÓN con home. Reposicionar esta página al ángulo TRUST/owner-funds/compliance (que ya enfatiza) para separarla del home. Focus -> trust accounting PM."},
    {"url": "https://propertyledger.us/contact/", "type": "page", "current_focus": "free accounting consultation",
     "recommended_focus": "free accounting consultation", "secondary": ["property management accounting consultation"],
     "note": "OK. Meta description con CTA + teléfono. Interlink desde todos los blogs (ya lo hace el prompt)."},
    {"url": "NUEVA: https://propertyledger.us/hoa-condo-accounting/", "type": "page-new", "current_focus": None,
     "recommended_focus": "hoa accounting services", "secondary": ["hoa accounting", "condo association accounting", "hoa accounting software"],
     "note": "GAP COMERCIAL claro: 'hoa accounting services' (KD0, 320) + 'hoa accounting' (KD0, 480) sin página dedicada. Alta relevancia + KD0. Recomendado crear landing HOA/Condo."},
    # Blogs existentes: el focus keyword ya está bien; la optimización es interlink
    # a los nuevos blogs del mismo cluster + verificar meta.
    {"url": "https://propertyledger.us/property-management-trust-accounting/", "type": "post", "current_focus": "property management trust accounting",
     "recommended_focus": "property management trust accounting", "secondary": ["real estate trust accounting"],
     "note": "Interlink al nuevo explainer 'what is trust accounting' y a 'trust accounting rules by state'. Pilar del cluster trust."},
    {"url": "https://propertyledger.us/owner-statements-explained/", "type": "post", "current_focus": "owner statements",
     "recommended_focus": "owner statements", "secondary": ["owner distributions"],
     "note": "Interlink al template/sample owner statement (blog #11) y a HOA/condo financial statements."},
    {"url": "https://propertyledger.us/property-management-financial-statements/", "type": "post", "current_focus": "property management financial statements",
     "recommended_focus": "property management financial statements", "secondary": ["hoa condo financial statements"],
     "note": "Interlink al nuevo 'HOA & condo financial statements'. Ya bien optimizado (84/100)."},
    {"url": "https://propertyledger.us/month-end-closing-checklist/", "type": "post", "current_focus": "month-end closing checklist",
     "recommended_focus": "month-end closing checklist", "secondary": ["property management chart of accounts"],
     "note": "Interlink al 'chart of accounts' (blog #10). Ya bien optimizado (85/100)."},
    {"url": "https://propertyledger.us/in-house-bookkeeper-vs-outsourced-accounting-property-management/", "type": "post", "current_focus": "outsourced property management accounting",
     "recommended_focus": "outsourced property management accounting", "secondary": ["what is outsourced accounting", "outsourced accounting firm"],
     "note": "Post #109 (ya optimizado a mano). Interlink a '5 signs you need help' y 'what is outsourced accounting'."},
]


def main() -> None:
    by_kw, raw = load_universe()
    os.makedirs(OUT_DIR, exist_ok=True)

    banks = {
        "informational": clustered_bank(by_kw, "informational"),
        "commercial": clustered_bank(by_kw, "commercial"),
        "transactional": clustered_bank(by_kw, "transactional"),
    }

    queue = []
    for i, (topic, primary, slug) in enumerate(BLOG_QUEUE, 1):
        info = lookup(by_kw, primary)
        queue.append({
            "order": i,
            "topic": topic,
            "primary_keyword": primary,
            "measured_volume": info["volume"],
            "measured_kd": info["kd"],
            "suggested_slug": slug,
            "status": "queued",
        })

    pages = []
    for p in PAGE_OPT:
        rec = lookup(by_kw, p["recommended_focus"]) if p["recommended_focus"] else {"volume": None, "kd": None}
        pages.append({**p, "recommended_focus_volume": rec["volume"], "recommended_focus_kd": rec["kd"]})

    cache = {
        "site": "propertyledger",
        "domain": raw["generated_for"],
        "market": {"location_code": raw["location_code"], "language_code": raw["language_code"]},
        "generated": "2026-07-20",
        "source": "DataForSEO Labs (research_propertyledger.py)",
        "research_cost_usd": raw.get("total_cost_usd"),
        "competitors_measured": [
            {"domain": c["domain"], "ranked_kw_top20": c["ranked_kw_top20"], "sum_volume_top20": c["sum_volume_top20"]}
            for c in raw.get("competitors_measured", [])
        ],
        "notes": [
            "Baseline: propertyledger.us rankeaba en 0 keywords al medir (dominio nuevo).",
            "content_gap vs doorloop = ruido (doorloop es software PM full, rankea por todo el universo PM/real estate genérico, no accounting). Se usa keyword_universe de semillas de accounting como señal limpia.",
            "'trust accounting' bruto (5400) está dominado por trust accounting LEGAL (abogados/IOLTA). Property Ledger es PM/HOA -> targetear variantes real-estate/PM, no genéricas/legales.",
            "'property management accounting software' (1300) es intención de SOFTWARE (quieren AppFolio/Buildium), no servicio -> no targetear en páginas de servicio; solo abordar como comparación/educación.",
            "Competidores todos capped a 1000 kw (gigantes). Directo de servicio = apmhelp.com (282K).",
        ],
        "keyword_banks": banks,
        "blog_queue": queue,
        "page_optimization": pages,
    }

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

    # -------- Markdown legible --------
    lines = []
    lines.append(f"# Cache SEO — Property Ledger Solutions ({cache['domain']})\n")
    lines.append(f"Generado {cache['generated']} · DataForSEO Labs (US 2840, en) · costo research ${cache['research_cost_usd']}\n")
    lines.append("## Competidores medidos (ranked_keywords top-20)\n")
    lines.append("| Dominio | kw top20 | vol top20 |\n|---|--:|--:|")
    for c in cache["competitors_measured"]:
        lines.append(f"| {c['domain']} | {c['ranked_kw_top20']} | {c['sum_volume_top20']:,} |")
    lines.append("\n## Notas estratégicas\n")
    for n in cache["notes"]:
        lines.append(f"- {n}")
    lines.append("\n## Calendario de blogs (cola que consume el agente)\n")
    lines.append("Cadencia L-V 9am. ~3 semanas. El agente toma el siguiente `topic` no publicado.\n")
    lines.append("| # | Tema | Keyword principal | Vol | KD |\n|--:|---|---|--:|--:|")
    for q in queue:
        lines.append(f"| {q['order']} | {q['topic']} | {q['primary_keyword']} | {q['measured_volume']} | {q['measured_kd']} |")
    lines.append("\n## Optimización on-page (lo que ya existe)\n")
    lines.append("| URL | Tipo | Focus recomendado | Vol | KD | Nota |\n|---|---|---|--:|--:|---|")
    for p in pages:
        lines.append(f"| {p['url']} | {p['type']} | {p['recommended_focus']} | {p['recommended_focus_volume']} | {p['recommended_focus_kd']} | {p['note']} |")
    lines.append("\n## Banco de keywords comerciales (para páginas de servicio)\n")
    lines.append("| Keyword | Vol | KD | variantes |\n|---|--:|--:|--:|")
    for x in banks["commercial"][:20]:
        lines.append(f"| {x['keyword']} | {x['volume']} | {x['kd']} | {x['variants']} |")
    lines.append("\n## Banco de keywords informacionales (para blogs)\n")
    lines.append("| Keyword | Vol | KD | variantes |\n|---|--:|--:|--:|")
    for x in banks["informational"][:20]:
        lines.append(f"| {x['keyword']} | {x['volume']} | {x['kd']} | {x['variants']} |")

    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"Cache JSON -> {OUT_JSON}")
    print(f"Plan MD    -> {OUT_MD}")
    print(f"blog_queue: {len(queue)} temas | páginas a optimizar: {len(pages)}")
    print(f"banks: info {len(banks['informational'])}, commercial {len(banks['commercial'])}, transactional {len(banks['transactional'])}")


if __name__ == "__main__":
    main()
