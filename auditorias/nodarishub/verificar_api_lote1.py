from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import requests
from requests.auth import HTTPBasicAuth


def load_env(path: Path) -> dict[str, str]:
    out = {}
    for raw in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        line = raw.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            out[key.strip()] = value.strip().strip('"').strip("'")
    return out


def sha(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--env", type=Path, required=True)
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    env = load_env(args.env)
    user = os.getenv("NODARIS_WP_USER") or env.get("NODARIS_WP_USER")
    password = os.getenv("NODARIS_WP_APP_PASSWORD") or env.get("NODARIS_WP_APP_PASSWORD")
    if not user or not password:
        raise RuntimeError("Faltan credenciales Nodaris en el entorno local")

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    session = requests.Session()
    session.auth = HTTPBasicAuth(user, password)
    session.headers.update({"User-Agent": "NodarisSEOReadback/1.0"})
    records = []
    failures = []
    for page in manifest["pages"]:
        page_id = int(page["id"])
        response = session.get(
            f"https://nodarishub.com/wp-json/wp/v2/pages/{page_id}",
            params={"context": "edit"}, timeout=90,
        )
        if response.status_code != 200:
            failures.append(f"{page_id}: API HTTP {response.status_code}")
            continue
        obj = response.json()
        raw = (obj.get("content") or {}).get("raw", "")
        title = (obj.get("title") or {}).get("raw", "")
        expected_hash = page["after_sha256"]
        expected_title = page["title_unchanged"]
        hash_ok = sha(raw) == expected_hash
        title_ok = title == expected_title
        if not hash_ok:
            failures.append(f"{page_id}: hash de content.raw no coincide")
        if not title_ok:
            failures.append(f"{page_id}: título WordPress cambió")
        records.append({
            "id": page_id,
            "url": obj.get("link"),
            "status": obj.get("status"),
            "modified_gmt": obj.get("modified_gmt"),
            "content_raw_sha256": sha(raw),
            "expected_sha256": expected_hash,
            "content_match": hash_ok,
            "title": title,
            "expected_title": expected_title,
            "title_match": title_ok,
            "elementor": (obj.get("meta") or {}).get("_elementor_edit_mode") == "builder",
        })

    report = {
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "verdict": "API_READBACK_PASS" if not failures else "BLOCKED",
        "checks": len(records) * 2,
        "failures": failures,
        "pages": records,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
