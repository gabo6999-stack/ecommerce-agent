from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import requests
from requests.auth import HTTPBasicAuth

API = "https://api.dataforseo.com/v3/dataforseo_labs/google/ranked_keywords/live"
MARKETS = {
    "ec": {"location_code": 2218, "language_code": "es"},
    "mx": {"location_code": 2484, "language_code": "es"},
}


def load_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def flatten(item: dict) -> dict:
    kd = item.get("keyword_data") or {}
    info = kd.get("keyword_info") or {}
    props = kd.get("keyword_properties") or {}
    intent = (kd.get("search_intent_info") or {}).get("main_intent")
    serp_item = (item.get("ranked_serp_element") or {}).get("serp_item") or {}
    return {
        "keyword": kd.get("keyword"),
        "volume": info.get("search_volume"),
        "cpc": info.get("cpc"),
        "difficulty": props.get("keyword_difficulty"),
        "intent": intent,
        "rank_absolute": serp_item.get("rank_absolute"),
        "rank_group": serp_item.get("rank_group"),
        "url": serp_item.get("url"),
        "path": urlparse(serp_item.get("url") or "").path,
        "title": serp_item.get("title"),
        "type": serp_item.get("type"),
    }


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
        raise RuntimeError("Faltan credenciales DataForSEO")

    session = requests.Session()
    session.auth = HTTPBasicAuth(login, password)
    session.headers.update({"Content-Type": "application/json", "User-Agent": "NodarisSEOAudit/1.0"})
    reports = {}
    total_cost = 0.0
    for market, cfg in MARKETS.items():
        task = {
            "target": "nodarishub.com",
            "location_code": cfg["location_code"],
            "language_code": cfg["language_code"],
            "include_subdomains": True,
            "filters": [["ranked_serp_element.serp_item.rank_absolute", "<=", 100]],
            "order_by": ["keyword_data.keyword_info.search_volume,desc"],
            "limit": 1000,
        }
        response = session.post(API, json=[task], timeout=180)
        response.raise_for_status()
        payload = response.json()
        if payload.get("status_code") != 20000:
            raise RuntimeError(f"API {market}: {payload.get('status_code')} {payload.get('status_message')}")
        tasks = payload.get("tasks") or []
        if len(tasks) != 1 or tasks[0].get("status_code") != 20000:
            raise RuntimeError(f"Contrato/tarea inválida en {market}: tasks={len(tasks)}")
        results = tasks[0].get("result") or []
        if len(results) != 1:
            raise RuntimeError(f"Contrato inválido en {market}: results={len(results)}")
        raw_path = args.out / f"ranked-{market}-raw.json"
        raw_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        items = results[0].get("items") or []
        rows = [flatten(i) for i in items]
        total_count = results[0].get("total_count")
        cost = tasks[0].get("cost") or 0.0
        total_cost += cost
        reports[market] = {
            "location_code": cfg["location_code"],
            "returned": len(rows),
            "total_count": total_count,
            "top10": sum(1 for r in rows if (r.get("rank_absolute") or 999) <= 10),
            "top20": sum(1 for r in rows if (r.get("rank_absolute") or 999) <= 20),
            "ec_urls": sum(1 for r in rows if (r.get("path") or "").startswith("/ec/")),
            "mx_urls": sum(1 for r in rows if (r.get("path") or "").startswith("/mx/")),
            "rows": rows,
            "api_cost_usd": cost,
        }
        print(f"{market}: {len(rows)}/{total_count} keywords devueltas; top10={reports[market]['top10']}; top20={reports[market]['top20']}")

    output = {
        "measured_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": "DataForSEO Labs ranked_keywords live",
        "method": {"target": "nodarishub.com", "max_rank_absolute": 100, "limit": 1000},
        "total_api_cost_usd": round(total_cost, 6),
        "markets": reports,
    }
    path = args.out / "ranked-live.json"
    path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"report": str(path), "total_api_cost_usd": output["total_api_cost_usd"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
