from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests
from requests.auth import HTTPBasicAuth

VOLUME_API = "https://api.dataforseo.com/v3/keywords_data/google_ads/search_volume/live"
DIFFICULTY_API = "https://api.dataforseo.com/v3/dataforseo_labs/google/bulk_keyword_difficulty/live"
MARKETS = {
    "ec": {
        "location_code": 2218,
        "keywords": [
            "agencia digital ecuador", "crear pagina web ecuador", "diseño de paginas web ecuador",
            "agencia de marketing digital ecuador", "agencia seo ecuador", "desarrollo de software a medida ecuador",
        ],
    },
    "mx": {
        "location_code": 2484,
        "keywords": [
            "agencia digital mexico", "crear pagina web mexico", "diseño de paginas web mexico",
            "agencia de marketing digital mexico", "agencia seo mexico", "desarrollo de software a medida mexico",
        ],
    },
}


def load_env(path: Path) -> dict[str, str]:
    out = {}
    for raw in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        line = raw.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            out[key.strip()] = value.strip().strip('"').strip("'")
    return out


def post(session: requests.Session, api: str, task: dict, label: str) -> tuple[dict, list[dict], float]:
    response = session.post(api, json=[task], timeout=180)
    response.raise_for_status()
    payload = response.json()
    if payload.get("status_code") != 20000:
        raise RuntimeError(f"{label}: API {payload.get('status_code')} {payload.get('status_message')}")
    tasks = payload.get("tasks") or []
    if len(tasks) != 1 or tasks[0].get("status_code") != 20000:
        raise RuntimeError(f"{label}: contrato/tarea inválida")
    results = tasks[0].get("result") or []
    # Keywords Data returns rows directly; Labs usually wraps rows in result[0].items.
    if results and isinstance(results[0], dict) and "items" in results[0]:
        items = results[0].get("items") or []
    else:
        items = results
    return payload, items, tasks[0].get("cost") or 0.0


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

    report = {"measured_at_utc": datetime.now(timezone.utc).isoformat(), "markets": {}, "costs": {"volume": 0.0, "difficulty": 0.0}}
    for market, cfg in MARKETS.items():
        volume_payload, volume_items, volume_cost = post(session, VOLUME_API, {
            "keywords": cfg["keywords"], "location_code": cfg["location_code"], "language_code": "es",
        }, f"volume-{market}")
        diff_payload, diff_items, diff_cost = post(session, DIFFICULTY_API, {
            "keywords": cfg["keywords"], "location_code": cfg["location_code"], "language_code": "es",
        }, f"difficulty-{market}")
        (args.out / f"metrics-{market}-volume-raw.json").write_text(json.dumps(volume_payload, ensure_ascii=False, indent=2), encoding="utf-8")
        (args.out / f"metrics-{market}-difficulty-raw.json").write_text(json.dumps(diff_payload, ensure_ascii=False, indent=2), encoding="utf-8")
        volumes = {}
        for item in volume_items:
            kw = item.get("keyword")
            if kw:
                volumes[kw] = {
                    "search_volume": item.get("search_volume"),
                    "cpc": item.get("cpc"),
                    "competition": item.get("competition"),
                    "competition_index": item.get("competition_index"),
                }
        difficulties = {item.get("keyword"): item.get("keyword_difficulty") for item in diff_items if item.get("keyword")}
        rows = []
        for keyword in cfg["keywords"]:
            rows.append({"keyword": keyword, **volumes.get(keyword, {}), "keyword_difficulty": difficulties.get(keyword)})
        if len(rows) != len(cfg["keywords"]):
            raise RuntimeError(f"{market}: cardinalidad interna inesperada")
        report["markets"][market] = {"location_code": cfg["location_code"], "requested": len(cfg["keywords"]), "volume_rows_received": len(volume_items), "difficulty_rows_received": len(diff_items), "rows": rows}
        report["costs"]["volume"] += volume_cost
        report["costs"]["difficulty"] += diff_cost
        print(f"{market}: volume {len(volume_items)}/{len(cfg['keywords'])}; difficulty {len(diff_items)}/{len(cfg['keywords'])}")
    report["costs"] = {k: round(v, 6) for k, v in report["costs"].items()}
    path = args.out / "keyword-metrics-live.json"
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"report": str(path), "costs": report["costs"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
