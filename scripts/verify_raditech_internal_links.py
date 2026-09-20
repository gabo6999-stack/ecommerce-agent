#!/usr/bin/env python
"""Verificación pública anónima de la limpieza de enlaces internos de Raditech."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json
import re
import time

import requests

PAGES = [
    "https://raditech.mx/",
    "https://raditech.mx/sistema-pacs-ris/",
    "https://raditech.mx/monitores-medicos-radiologia/",
    "https://raditech.mx/portal-x-card/",
    "https://raditech.mx/inteligencia-artificial-radiologia-diagnostica-mexico-2026/",
    "https://raditech.mx/digitalizacion-costos-gestion-hospitalaria/",
    "https://raditech.mx/nuestros-productos/",
    "https://raditech.mx/pacs-teleradiologia/",
    "https://raditech.mx/teleradiologia-solucion-estrategica-hospitales-clinicas-mexico/",
    "https://raditech.mx/faq/",
    "https://raditech.mx/radiologia-a-distancia-hospitales-mexico/",
    "https://raditech.mx/servicio-teleradiologia/",
]
EXPECTED_MARKERS = {
    "https://raditech.mx/faq/": ">solución PACS-RIS de Raditech</a>",
    "https://raditech.mx/radiologia-a-distancia-hospitales-mexico/": ">sistema PACS</a> (Picture Archiving and Communication System) robusto",
}
OLD = [
    "https://raditech.mx/pacs-ris/",
    "https://raditech.mx/teleradiologia/",
    "https://raditech.mx/teleradiologia-de-alta-especialidad/",
    "https://raditech.mx/sistema-de-informacion-hospitalaria-his/",
    "https://raditech.mx/monitores-grado-medico/",
    "https://raditech.mx/pacs-vira-ris/",
    "https://raditech.mx/resonancia-magnetica-cardiovascular/",
    "https://raditech.mx/tomografia-cardiaca-y-angiotomografia-coronaria/",
    "https://raditech.mx/x-card/",
    'href="/pacs-ris/"',
    'href="/teleradiologia-de-alta-especialidad/"',
    'href="/sistema-de-informacion-hospitalaria-his/"',
    'href="/monitores-grado-medico/"',
    'href="/pacs-vira-ris/"',
    'href="/resonancia-magnetica-cardiovascular/"',
    'href="/tomografia-cardiaca-y-angiotomografia-coronaria/"',
    'href="/x-card/"',
]
DESTINATIONS = [
    "https://raditech.mx/sistema-pacs-ris/",
    "https://raditech.mx/servicio-teleradiologia/",
    "https://raditech.mx/teleradiologia-alta-especialidad/",
    "https://raditech.mx/monitores-medicos-radiologia/",
]
OUT = Path(r"C:\Users\gabom\Proyectos\ecommerce-agent\docs\data\raditech-verificacion-interlinks-2026-08-05.json")
HEADERS = {"User-Agent": "Mozilla/5.0 Hermes anonymous Raditech verifier"}

checks = []
for page in PAGES:
    for mode in ["normal", "cache_bust"]:
        url = page if mode == "normal" else page + ("&" if "?" in page else "?") + f"hermes_verify={int(time.time() * 1000)}"
        response = requests.get(url, headers=HEADERS, timeout=45)
        html = response.text
        title = re.search(r"(?is)<title[^>]*>(.*?)</title>", html)
        h1 = re.findall(r"(?is)<h1\b[^>]*>(.*?)</h1>", html)
        old_counts = {old: html.count(old) for old in OLD}
        destination_counts = {dest: html.count(dest) for dest in DESTINATIONS}
        marker = EXPECTED_MARKERS.get(page)
        marker_present = marker in html if marker else True
        passed = (
            response.status_code == 200
            and bool(title)
            and bool(h1)
            and sum(old_counts.values()) == 0
            and marker_present
        )
        checks.append({
            "page": page,
            "mode": mode,
            "status_code": response.status_code,
            "cache": response.headers.get("x-litespeed-cache"),
            "title_present": bool(title),
            "h1_count": len(h1),
            "expected_marker": marker,
            "marker_present": marker_present,
            "old_counts": old_counts,
            "destination_counts": destination_counts,
            "pass": passed,
        })

for destination in DESTINATIONS:
    response = requests.get(destination, headers=HEADERS, timeout=45, allow_redirects=False)
    checks.append({
        "page": destination,
        "mode": "destination_direct",
        "status_code": response.status_code,
        "pass": response.status_code == 200,
    })

result = {
    "status": "PASS" if all(item["pass"] for item in checks) else "FAIL",
    "method": "anonymous public HTML, normal and cache-busted",
    "measured_at_utc": datetime.now(timezone.utc).isoformat(),
    "checks_passed": sum(1 for item in checks if item["pass"]),
    "checks_total": len(checks),
    "checks": checks,
}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({k: result[k] for k in ["status", "checks_passed", "checks_total"]} | {"output": str(OUT)}, ensure_ascii=False, indent=2))
if result["status"] != "PASS":
    raise SystemExit(1)
