from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests
from requests.auth import HTTPBasicAuth

TARGETS = {
    "https://nodarishub.com/ec/",
    "https://nodarishub.com/mx/",
    "https://nodarishub.com/ec/diseno-web/",
    "https://nodarishub.com/mx/diseno-web/",
    "https://nodarishub.com/ec/seo/",
    "https://nodarishub.com/mx/seo/",
}


def load_env(path: Path) -> dict[str, str]:
    out = {}
    for raw in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        line = raw.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            out[key.strip()] = value.strip().strip('"').strip("'")
    return out


def normalize_url(value: str) -> str:
    return value.rstrip("/") + "/"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    env = load_env(args.env)
    user = os.getenv("NODARIS_WP_USER") or env.get("NODARIS_WP_USER")
    password = os.getenv("NODARIS_WP_APP_PASSWORD") or env.get("NODARIS_WP_APP_PASSWORD")
    if not user or not password:
        raise RuntimeError("Faltan NODARIS_WP_USER/NODARIS_WP_APP_PASSWORD")

    session = requests.Session()
    session.auth = HTTPBasicAuth(user, password)
    session.headers.update({"User-Agent": "NodarisSEOBackup/1.0"})
    response = session.get("https://nodarishub.com/wp-json/wp/v2/pages", params={"context": "edit", "per_page": 100, "page": 1}, timeout=120)
    response.raise_for_status()
    pages = response.json()
    by_link = {normalize_url(p.get("link") or ""): p for p in pages}
    selected = []
    for target in sorted(TARGETS):
        obj = by_link.get(normalize_url(target))
        if not obj:
            raise RuntimeError(f"No se encontró el objeto WordPress para {target}")
        # La REST incluye un campo top-level `password`. Nunca se guarda en el
        # respaldo local, aunque esté vacío, para evitar filtrar secretos o
        # generar falsos positivos en escáneres posteriores.
        obj = dict(obj)
        obj.pop("password", None)
        selected.append(obj)
        path = args.out / f"page-{obj['id']}-{obj['slug'] or 'home'}.json"
        raw = json.dumps(obj, ensure_ascii=False, indent=2)
        path.write_text(raw, encoding="utf-8")
    manifest = {
        "captured_at_utc": datetime.now(timezone.utc).isoformat(),
        "endpoint": "GET /wp-json/wp/v2/pages?context=edit&per_page=100",
        "read_only": True,
        "objects": [
            {
                "id": obj["id"],
                "slug": obj["slug"],
                "link": obj["link"],
                "status": obj["status"],
                "modified_gmt": obj["modified_gmt"],
                "content_raw_sha256": hashlib.sha256((obj.get("content") or {}).get("raw", "").encode("utf-8")).hexdigest(),
                "uses_elementor": (obj.get("meta") or {}).get("_elementor_edit_mode") == "builder",
            }
            for obj in selected
        ],
    }
    manifest_path = args.out / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"manifest": str(manifest_path), "objects": manifest["objects"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
