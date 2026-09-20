#!/usr/bin/env python
"""Descubre módulos disponibles de Google Site Kit sin exponer credenciales."""
from __future__ import annotations

from pathlib import Path
import json

import requests

ENV = Path(r"C:\Users\gabom\Proyectos\ecommerce-agent\ecommerce-agent__.env")
OUT = Path(r"C:\Users\gabom\Proyectos\ecommerce-agent\docs\data\raditech-sitekit-discovery-2026-08-05.json")
BASE = "https://raditech.mx/wp-json"


def load_env(path: Path) -> dict[str, str]:
    values = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


env = load_env(ENV)
username = env.get("RADITECH_WP_USER")
password = env.get("RADITECH_WP_PASSWORD")
if not username or not password:
    raise SystemExit("Faltan RADITECH_WP_USER/RADITECH_WP_PASSWORD")

token_response = requests.post(
    BASE + "/jwt-auth/v1/token",
    json={"username": username, "password": password},
    timeout=45,
)
token_response.raise_for_status()
token = token_response.json().get("token")
if not token:
    raise SystemExit("JWT no devuelto")
headers = {"Authorization": f"Bearer {token}", "User-Agent": "Hermes Raditech Site Kit audit"}

response = requests.get(BASE + "/google-site-kit/v1/core/modules/data/list", headers=headers, timeout=45)
response.raise_for_status()
modules = response.json()
# Se conservan únicamente estados y nombres; nunca tokens ni credenciales.
safe = []
for module in modules:
    safe.append({
        key: module.get(key)
        for key in ["slug", "name", "description", "active", "connected", "setupComplete", "recoverable", "shareable"]
        if key in module
    })
result = {"status": "PASS", "modules": safe}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(result | {"output": str(OUT)}, ensure_ascii=False, indent=2))
