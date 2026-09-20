#!/usr/bin/env python
"""Crawl público acotado de Raditech para arquitectura PACS/RIS."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from html import unescape
from pathlib import Path
from urllib.parse import urljoin, urlparse
import json
import re
import time

import requests

BASE = "https://raditech.mx"
TARGET = BASE + "/sistema-pacs-ris/"
OUT = Path(r"C:\Users\gabom\Proyectos\ecommerce-agent\docs\data\raditech-arquitectura-pacs-ris-2026-08-05.json")
HEADERS = {"User-Agent": "Mozilla/5.0 Hermes Raditech SEO architecture audit"}


def get(url: str) -> requests.Response:
    last_error = None
    for attempt in range(4):
        try:
            response = requests.get(url, headers=HEADERS, timeout=45)
            response.raise_for_status()
            return response
        except requests.RequestException as error:
            last_error = error
            if attempt < 3:
                time.sleep(2 ** attempt)
    raise last_error


def locs(xml: str) -> list[str]:
    return [unescape(x.strip()) for x in re.findall(r"(?is)<loc>(.*?)</loc>", xml)]

index = get(BASE + "/sitemap_index.xml")
sitemaps = [u for u in locs(index.text) if "post-sitemap" in u or "page-sitemap" in u]
urls: list[str] = []
for sitemap in sitemaps:
    urls.extend(locs(get(sitemap).text))
urls = sorted(set(u.split("?")[0] for u in urls if urlparse(u).netloc.endswith("raditech.mx")))


def parse(url: str) -> dict:
    r = get(url)
    html = r.text
    title_m = re.search(r"(?is)<title[^>]*>(.*?)</title>", html)
    h1s = [re.sub(r"\s+", " ", re.sub(r"(?is)<[^>]+>", " ", x)).strip() for x in re.findall(r"(?is)<h1\b[^>]*>(.*?)</h1>", html)]
    body = re.sub(r"(?is)<(script|style|noscript)\b.*?</\1>", " ", html)
    main_m = re.search(r"(?is)<main\b[^>]*>(.*?)</main>", body)
    content_html = main_m.group(1) if main_m else body
    visible = re.sub(r"\s+", " ", unescape(re.sub(r"(?is)<[^>]+>", " ", content_html))).strip()
    links = []
    for match in re.finditer(r"(?is)<a\b[^>]*href=[\"']([^\"']+)[\"'][^>]*>(.*?)</a>", content_html):
        raw, inner = match.group(1), match.group(2)
        absolute = urljoin(url, unescape(raw)).split("#")[0].split("?")[0]
        if urlparse(absolute).netloc.endswith("raditech.mx"):
            anchor = re.sub(r"\s+", " ", unescape(re.sub(r"(?is)<[^>]+>", " ", inner))).strip()
            links.append({"url": absolute.rstrip("/") + "/", "anchor": anchor})
    target_norm = TARGET.rstrip("/") + "/"
    terms = {term: len(re.findall(rf"(?i)\b{re.escape(term)}\b", visible)) for term in ["PACS", "RIS", "DICOM", "HL7", "servidor", "radiología"]}
    return {
        "url": url,
        "status": r.status_code,
        "final_url": r.url,
        "cache": r.headers.get("x-litespeed-cache"),
        "title": re.sub(r"\s+", " ", re.sub(r"(?is)<[^>]+>", " ", title_m.group(1))).strip() if title_m else "",
        "h1": h1s,
        "visible_words": len(re.findall(r"\b[\wÁÉÍÓÚÜÑáéíóúüñ-]+\b", visible)),
        "terms": terms,
        "links_to_target": sum(1 for link in links if link["url"] == target_norm),
        "target_anchors": [link["anchor"] for link in links if link["url"] == target_norm],
        "internal_links_unique": len(set(link["url"] for link in links)),
        "internal_links": links,
    }

with ThreadPoolExecutor(max_workers=3) as pool:
    pages = list(pool.map(parse, urls))

candidates = [
    page for page in pages
    if page["url"].rstrip("/") != TARGET.rstrip("/")
    and page["links_to_target"] == 0
    and (page["terms"]["PACS"] >= 2 or page["terms"]["RIS"] >= 2)
]
inbound = [page for page in pages if page["links_to_target"] > 0]
result = {
    "method": "anonymous public sitemap crawl",
    "sitemaps_examined": len(sitemaps),
    "urls_examined": len(pages),
    "failures": 0,
    "target": TARGET,
    "current_inbound_source_pages": len(inbound),
    "inbound_sources": inbound,
    "missing_link_candidates": sorted(candidates, key=lambda p: -(p["terms"]["PACS"] + p["terms"]["RIS"])),
    "pages": pages,
}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({
    "status": "PASS",
    "sitemaps_examined": len(sitemaps),
    "urls_examined": len(pages),
    "current_inbound_source_pages": len(inbound),
    "missing_link_candidates": len(candidates),
    "top_candidates": [{"url": p["url"], "title": p["title"], "terms": p["terms"]} for p in result["missing_link_candidates"][:12]],
    "output": str(OUT),
}, ensure_ascii=False, indent=2))
