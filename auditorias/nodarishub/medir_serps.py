from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import requests
from requests.auth import HTTPBasicAuth

API = "https://api.dataforseo.com/v3/serp/google/organic/live/advanced"
QUERIES = [
    {"market": "ec", "location_code": 2218, "keyword": "agencia digital ecuador", "owner": "https://nodarishub.com/ec/"},
    {"market": "ec", "location_code": 2218, "keyword": "crear pagina web ecuador", "owner": "https://nodarishub.com/ec/crear-pagina-web/"},
    {"market": "ec", "location_code": 2218, "keyword": "diseño de paginas web ecuador", "owner": "https://nodarishub.com/ec/diseno-web/"},
    {"market": "ec", "location_code": 2218, "keyword": "agencia de marketing digital ecuador", "owner": "https://nodarishub.com/ec/marketing/"},
    {"market": "ec", "location_code": 2218, "keyword": "agencia seo ecuador", "owner": "https://nodarishub.com/ec/seo/"},
    {"market": "ec", "location_code": 2218, "keyword": "desarrollo de software a medida ecuador", "owner": "https://nodarishub.com/ec/software/"},
    {"market": "mx", "location_code": 2484, "keyword": "agencia digital mexico", "owner": "https://nodarishub.com/mx/"},
    {"market": "mx", "location_code": 2484, "keyword": "crear pagina web mexico", "owner": "https://nodarishub.com/mx/crear-pagina-web/"},
    {"market": "mx", "location_code": 2484, "keyword": "diseño de paginas web mexico", "owner": "https://nodarishub.com/mx/diseno-web/"},
    {"market": "mx", "location_code": 2484, "keyword": "agencia de marketing digital mexico", "owner": "https://nodarishub.com/mx/marketing/"},
    {"market": "mx", "location_code": 2484, "keyword": "agencia seo mexico", "owner": "https://nodarishub.com/mx/seo/"},
    {"market": "mx", "location_code": 2484, "keyword": "desarrollo de software a medida mexico", "owner": "https://nodarishub.com/mx/software/"},
]


def load_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip().strip('"').strip("'")
        values[key.strip()] = value
    return values


def domain_of(url: str) -> str:
    return urlparse(url).netloc.lower().removeprefix("www.")


def run_query(session: requests.Session, query: dict) -> tuple[dict, dict]:
    task = {
        "keyword": query["keyword"],
        "location_code": query["location_code"],
        "language_code": "es",
        "device": "desktop",
        "os": "windows",
        "depth": 30,
    }
    response = session.post(API, json=[task], timeout=120)
    response.raise_for_status()
    payload = response.json()
    if payload.get("status_code") != 20000:
        raise RuntimeError(f"Respuesta API inválida para {query['keyword']!r}: {payload.get('status_code')} {payload.get('status_message')}")
    tasks = payload.get("tasks") or []
    if len(tasks) != 1:
        raise RuntimeError(f"Cardinalidad inesperada: 1 tarea enviada, {len(tasks)} recibidas")
    task_result = tasks[0]
    if task_result.get("status_code") != 20000:
        raise RuntimeError(f"Tarea fallida: {task_result.get('status_code')} {task_result.get('status_message')}")
    results = task_result.get("result") or []
    if len(results) != 1:
        raise RuntimeError(f"Cardinalidad inesperada: se esperaba 1 result, llegaron {len(results)}")
    result = results[0]
    organic = [item for item in (result.get("items") or []) if item.get("type") == "organic"]
    organic.sort(key=lambda x: (x.get("rank_absolute") or 10_000, x.get("rank_group") or 10_000))
    first_ten = organic[:10]
    absolute_top_ten = [item for item in organic if (item.get("rank_absolute") or 10_000) <= 10]
    nodaris = [item for item in organic if domain_of(item.get("url") or "") == "nodarishub.com"]
    summary = {
        **query,
        "check_url": result.get("check_url"),
        "se_results_count": result.get("se_results_count"),
        "organic_returned": len(organic),
        "organic_in_absolute_top10": len(absolute_top_ten),
        "first_10_organic": [
            {
                "rank_absolute": i.get("rank_absolute"),
                "rank_group": i.get("rank_group"),
                "domain": domain_of(i.get("url") or ""),
                "url": i.get("url"),
                "title": i.get("title"),
                "description": i.get("description"),
            }
            for i in first_ten
        ],
        "organic_absolute_top10": [
            {
                "rank_absolute": i.get("rank_absolute"),
                "rank_group": i.get("rank_group"),
                "domain": domain_of(i.get("url") or ""),
                "url": i.get("url"),
                "title": i.get("title"),
            }
            for i in absolute_top_ten
        ],
        "nodaris_positions_returned_depth": [
            {"rank_absolute": i.get("rank_absolute"), "rank_group": i.get("rank_group"), "url": i.get("url")}
            for i in nodaris
        ],
        "owner_exact_match_positions": [
            {"rank_absolute": i.get("rank_absolute"), "rank_group": i.get("rank_group")}
            for i in organic if (i.get("url") or "").rstrip("/") == query["owner"].rstrip("/")
        ],
        "api_cost_usd": task_result.get("cost") or 0.0,
    }
    return payload, summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    env = load_env(args.env)
    login = os.getenv("DATAFORSEO_USERNAME") or env.get("DATAFORSEO_USERNAME")
    password = os.getenv("DATAFORSEO_PASSWORD") or env.get("DATAFORSEO_PASSWORD")
    if not login or not password:
        raise RuntimeError("Faltan DATAFORSEO_USERNAME/DATAFORSEO_PASSWORD en el entorno o archivo indicado")

    session = requests.Session()
    session.auth = HTTPBasicAuth(login, password)
    session.headers.update({"Content-Type": "application/json", "User-Agent": "NodarisSEOAudit/1.0"})

    summaries: list[dict] = []
    raw_dir = args.out / "raw-serp"
    raw_dir.mkdir(exist_ok=True)
    for index, query in enumerate(QUERIES, 1):
        payload, summary = run_query(session, query)
        raw_path = raw_dir / f"{index:02d}-{query['market']}.json"
        raw_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        summaries.append(summary)
        print(f"{index}/{len(QUERIES)} {query['market']} {query['keyword']}: {summary['organic_returned']} orgánicos; Nodaris={summary['nodaris_positions_returned_depth']}")
        time.sleep(0.25)

    report = {
        "measured_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": "DataForSEO SERP Google organic live advanced",
        "method": {
            "queries_sent": len(QUERIES),
            "usable_results": len(summaries),
            "location_codes": {"ec": 2218, "mx": 2484},
            "language_code": "es",
            "device": "desktop",
            "depth": 30,
            "note": "Se conservan por separado los orgánicos con rank_absolute<=10 y los primeros 10 resultados orgánicos."
        },
        "total_api_cost_usd": round(sum(x["api_cost_usd"] for x in summaries), 6),
        "queries": summaries,
    }
    out_path = args.out / "serps-live.json"
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"report": str(out_path), "queries": len(summaries), "total_api_cost_usd": report["total_api_cost_usd"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
