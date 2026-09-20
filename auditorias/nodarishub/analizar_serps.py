from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

PUBLIC_DOMAINS = {
    "gob.mx", "agenciadigital.edomex.gob.mx", "atd.qroo.gob.mx", "datos.gob.mx",
    "adip.cdmx.gob.mx", "tic.unam.mx",
}
SOCIAL_DOMAINS = {"instagram.com", "mx.linkedin.com"}
DIY_DOMAINS = {"webador.mx", "pagina.mx", "es.wix.com", "canva.com"}
DIRECTORY_DOMAINS = {"sortlist.com", "mx.indeed.com", "marketing4ecommerce.mx", "puromarketing.com", "ecomsystem.amvo.org.mx"}
EDITORIAL_PATTERNS = re.compile(r"\b(top\s*\d*|mejores?|cómo|como|gu[ií]a|ranking|tendencias|desaf[ií]os|beneficios|qu[eé] es|cu[aá]nto cuesta|empresas de|la clave para)\b", re.I)
EDITORIAL_PATH = re.compile(r"/(?:blog|contenido|rankings?|articulos?)(?:/|$)|/20\d\d/\d\d/\d\d/", re.I)


def classify(query: str, row: dict) -> str:
    domain = row["domain"]
    title = row.get("title") or ""
    url = row.get("url") or ""
    if domain in PUBLIC_DOMAINS or domain.endswith(".gob.mx") or domain.endswith(".edu.mx"):
        return "publico_academico"
    # En esta consulta concreta Facebook y X son perfiles del organismo público,
    # no resultados sociales genéricos.
    if query == "agencia digital mexico" and domain in {"facebook.com", "x.com"}:
        return "publico_academico"
    if domain == "es.wikipedia.org":
        return "directorio_editorial"
    if domain in SOCIAL_DOMAINS:
        return "otro"
    if domain == "reddit.com":
        return "directorio_editorial"
    if EDITORIAL_PATH.search(url) or domain in DIRECTORY_DOMAINS or EDITORIAL_PATTERNS.search(title):
        return "directorio_editorial"
    if domain in DIY_DOMAINS:
        return "plataforma_diy"
    if "software" in query:
        return "proveedor_software"
    return "agencia_servicio_directo"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--json-out", type=Path, required=True)
    parser.add_argument("--md-out", type=Path, required=True)
    args = parser.parse_args()
    data = json.loads(args.input.read_text(encoding="utf-8"))

    market_counts: dict[str, Counter] = defaultdict(Counter)
    query_reports = []
    domain_market: dict[str, Counter] = defaultdict(Counter)
    domain_market_queries: dict[str, Counter] = defaultdict(Counter)
    total_rows = 0
    owner_visible = 0
    for q in data["queries"]:
        counts = Counter()
        classified = []
        domains_in_query: set[str] = set()
        for row in q["first_10_organic"]:
            category = classify(q["keyword"], row)
            counts[category] += 1
            market_counts[q["market"]][category] += 1
            domain_market[q["market"]][row["domain"]] += 1
            domains_in_query.add(row["domain"])
            classified.append({**row, "category": category})
            total_rows += 1
        for domain in domains_in_query:
            domain_market_queries[q["market"]][domain] += 1
        if q["owner_exact_match_positions"]:
            owner_visible += 1
        query_reports.append({
            "market": q["market"],
            "keyword": q["keyword"],
            "owner": q["owner"],
            "owner_visible_depth30": bool(q["owner_exact_match_positions"]),
            "nodaris_visible_depth30": bool(q["nodaris_positions_returned_depth"]),
            "organic_in_absolute_top10": q["organic_in_absolute_top10"],
            "counts_first_10_organic": dict(counts),
            "results": classified,
        })

    result = {
        "source": str(args.input),
        "method": {
            "queries": len(query_reports),
            "first_10_organic_examined": total_rows,
            "classification": "Reglas deterministas por dominio, tipo de página y title; revisar manualmente antes de decisiones irreversibles.",
        },
        "owner_visible_depth30_queries": owner_visible,
        "market_counts": {m: dict(c) for m, c in market_counts.items()},
        "top_domains_by_market": {m: domain_market[m].most_common() for m in domain_market},
        "query_overlap_by_market": {m: domain_market_queries[m].most_common() for m in domain_market_queries},
        "queries": query_reports,
    }
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    labels = {
        "agencia_servicio_directo": "Agencia/servicio directo",
        "proveedor_software": "Proveedor de software",
        "plataforma_diy": "Plataforma DIY",
        "directorio_editorial": "Directorio/editorial",
        "publico_academico": "Público/académico",
        "otro": "Otro/social",
    }
    lines = [
        "# Composición SERP NodarisHub EC/MX",
        "",
        f"Fuente: DataForSEO live. Consultas: {len(query_reports)}/12. Resultados clasificados: {total_rows}/{len(query_reports)*10}.",
        f"NodarisHub visible en la profundidad devuelta (~30 orgánicos): {owner_visible}/{len(query_reports)} consultas.",
        "",
        "## Composición por mercado",
        "",
        "| Mercado | Categoría | Resultados |",
        "|---|---|---:|",
    ]
    for market in ("ec", "mx"):
        denominator = sum(market_counts[market].values())
        for category, count in market_counts[market].most_common():
            lines.append(f"| {market.upper()} | {labels[category]} | {count}/{denominator} ({count/denominator:.1%}) |")
    lines += ["", "## Composición por consulta", ""]
    for q in query_reports:
        lines.append(f"### {q['market'].upper()} — {q['keyword']}")
        lines.append("")
        lines.append(f"- Orgánicos dentro de rank_absolute ≤10: {q['organic_in_absolute_top10']}/10 posibles.")
        lines.append(f"- NodarisHub visible en profundidad devuelta: {'sí' if q['nodaris_visible_depth30'] else 'no'}.")
        lines.append("- Primeros 10 orgánicos: " + "; ".join(f"{labels[k]} {v}/10" for k, v in sorted(q["counts_first_10_organic"].items())))
        lines.append("")
        lines.append("| Pos. orgánica/absoluta | Dominio | Tipo | Título |")
        lines.append("|---:|---|---|---|")
        for row in q["results"]:
            title = (row.get("title") or "").replace("|", "\\|")
            lines.append(f"| {row.get('rank_group')}/{row.get('rank_absolute')} | {row['domain']} | {labels[row['category']]} | {title} |")
        lines.append("")
    lines += [
        "## Dominios con solapamiento",
        "",
    ]
    for market in ("ec", "mx"):
        lines.append(f"### {market.upper()}")
        lines.append("")
        for domain, query_appearances in domain_market_queries[market].most_common():
            result_count = domain_market[market][domain]
            lines.append(f"- {domain}: aparece en {query_appearances}/6 SERPs y ocupa {result_count}/60 resultados.")
        lines.append("")
    lines += [
        "> Clasificación automática ad hoc. Es evidencia de composición, no una afirmación causal sobre rankings ni una autorización de publicación.",
        "",
    ]
    args.md_out.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"json": str(args.json_out), "markdown": str(args.md_out), "market_counts": result["market_counts"], "owner_visible": owner_visible}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
