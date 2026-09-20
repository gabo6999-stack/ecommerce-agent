from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse


def load_auditor(path: Path):
    spec = importlib.util.spec_from_file_location("nodaris_diag", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("No se pudo cargar el auditor")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--serps", type=Path, required=True)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--auditor", type=Path, required=True)
    parser.add_argument("--json-out", type=Path, required=True)
    parser.add_argument("--md-out", type=Path, required=True)
    args = parser.parse_args()
    serps = json.loads(args.serps.read_text(encoding="utf-8"))
    baseline = json.loads(args.baseline.read_text(encoding="utf-8"))
    own = {p["url"].rstrip("/"): p for p in baseline["pages"]}
    auditor = load_auditor(args.auditor)

    cache: dict[str, dict] = {}
    comparisons = []
    for q in serps["queries"]:
        winner = q["first_10_organic"][0]
        url = winner["url"]
        if url not in cache:
            cache[url] = auditor.audit_page(url)
        competitor = cache[url]
        ours = own.get(q["owner"].rstrip("/"))
        comparisons.append({
            "market": q["market"],
            "keyword": q["keyword"],
            "owner": q["owner"],
            "competitor_rank_absolute": winner["rank_absolute"],
            "competitor_domain": winner["domain"],
            "competitor_url": url,
            "competitor_status": competitor.get("status"),
            "competitor_error": competitor.get("error"),
            "competitor_title": competitor.get("title") or winner.get("title"),
            "competitor_h1": competitor.get("h1"),
            "competitor_h2": competitor.get("h2") or [],
            "competitor_words": competitor.get("word_count"),
            "our_title": ours.get("title") if ours else None,
            "our_h1": ours.get("h1") if ours else None,
            "our_h2": ours.get("h2") if ours else [],
            "our_words": ours.get("word_count") if ours else None,
        })

    report = {
        "measured_at_utc": datetime.now(timezone.utc).isoformat(),
        "method": "Comparación del primer resultado orgánico de cada SERP contra la URL propietaria de NodarisHub; HTML anónimo, palabras visibles sin style/script/noscript.",
        "comparisons": comparisons,
        "competitor_fetch_ok": sum(1 for c in comparisons if c["competitor_status"] == 200),
        "competitors_examined": len(comparisons),
    }
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [
        "# NodarisHub vs ganador orgánico por consulta",
        "",
        f"Ganadores con HTML 200: {report['competitor_fetch_ok']}/{report['competitors_examined']}.",
        "",
        "| Mercado | Consulta | Ganador | Palabras ganador/Nodaris | H2 ganador/Nodaris |",
        "|---|---|---|---:|---:|",
    ]
    for c in comparisons:
        lines.append(
            f"| {c['market'].upper()} | {c['keyword']} | {c['competitor_domain']} | "
            f"{c['competitor_words']}/{c['our_words']} | {len(c['competitor_h2'])}/{len(c['our_h2'])} |"
        )
    lines += ["", "> La longitud es diagnóstica, no un objetivo ni una explicación causal.", ""]
    args.md_out.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"json": str(args.json_out), "markdown": str(args.md_out), "competitor_fetch_ok": report["competitor_fetch_ok"], "total": report["competitors_examined"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
