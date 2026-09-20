from __future__ import annotations

import argparse
import difflib
import hashlib
import html
import json
import re
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

BASE = "https://nodarishub.com"
UA = "Mozilla/5.0 (compatible; NodarisSEOAudit/1.0; +https://nodarishub.com/)"
SKIP_TAGS = {"script", "style", "noscript", "svg", "template"}
CHROME_TAGS = {"header", "footer", "nav"}


def fetch(url: str) -> tuple[int, dict[str, str], bytes, float]:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,application/xml;q=0.9,*/*;q=0.8"})
    started = time.perf_counter()
    with urllib.request.urlopen(req, timeout=30) as response:
        body = response.read()
        elapsed = time.perf_counter() - started
        return response.status, dict(response.headers.items()), body, elapsed


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title_parts: list[str] = []
        self.h1_parts: list[str] = []
        self.h2_parts: list[list[str]] = []
        self.text_parts: list[str] = []
        self.links: list[str] = []
        self.images = 0
        self.images_missing_alt = 0
        self.canonical: str | None = None
        self.robots: str | None = None
        self.description: str | None = None
        self.html_lang: str | None = None
        self.hreflang: dict[str, str] = {}
        self.in_title = 0
        self.in_h1 = 0
        self.current_h2: list[str] | None = None
        self.skip_depth = 0
        self.chrome_depth = 0
        self.main_depth = 0
        self.saw_main = False

    def handle_starttag(self, tag: str, attrs_list: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        attrs = {k.lower(): (v or "") for k, v in attrs_list}
        if tag == "html":
            self.html_lang = attrs.get("lang") or None
        if tag in SKIP_TAGS:
            self.skip_depth += 1
        if tag in CHROME_TAGS:
            self.chrome_depth += 1
        if tag == "main":
            self.main_depth += 1
            self.saw_main = True
        if tag == "title":
            self.in_title += 1
        if tag == "h1":
            self.in_h1 += 1
        if tag == "h2":
            self.current_h2 = []
        if tag == "meta":
            name = attrs.get("name", "").lower()
            if name == "robots":
                self.robots = attrs.get("content") or None
            elif name == "description":
                self.description = attrs.get("content") or None
        if tag == "link":
            rel = set(attrs.get("rel", "").lower().split())
            href = attrs.get("href")
            if "canonical" in rel and href:
                self.canonical = href
            if "alternate" in rel and attrs.get("hreflang") and href:
                self.hreflang[attrs["hreflang"]] = href
        if tag == "a" and attrs.get("href"):
            self.links.append(attrs["href"])
        if tag == "img":
            self.images += 1
            if not attrs.get("alt", "").strip():
                self.images_missing_alt += 1

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "title" and self.in_title:
            self.in_title -= 1
        if tag == "h1" and self.in_h1:
            self.in_h1 -= 1
        if tag == "h2" and self.current_h2 is not None:
            heading = normalize(" ".join(self.current_h2))
            if heading:
                self.h2_parts.append([heading])
            self.current_h2 = None
        if tag == "main" and self.main_depth:
            self.main_depth -= 1
        if tag in CHROME_TAGS and self.chrome_depth:
            self.chrome_depth -= 1
        if tag in SKIP_TAGS and self.skip_depth:
            self.skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if self.skip_depth:
            return
        value = normalize(data)
        if not value:
            return
        if self.in_title:
            self.title_parts.append(value)
        if self.in_h1:
            self.h1_parts.append(value)
        if self.current_h2 is not None:
            self.current_h2.append(value)
        # Prefer <main>. When no <main> has appeared yet, collect body-like text
        # outside global chrome. Most WordPress templates expose <main>.
        if self.main_depth or (not self.saw_main and not self.chrome_depth):
            self.text_parts.append(value)


def normalize(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(value)).strip()


def tokens(value: str) -> list[str]:
    return re.findall(r"[\wáéíóúüñÁÉÍÓÚÜÑ]+", value.lower(), flags=re.UNICODE)


def page_key(url: str) -> tuple[str, str] | None:
    path = urlparse(url).path.strip("/")
    pieces = path.split("/") if path else []
    if not pieces or pieces[0] not in {"ec", "mx"}:
        return None
    return pieces[0], "/".join(pieces[1:]) or "__home__"


def parse_sitemap(url: str) -> list[str]:
    status, _, body, _ = fetch(url)
    if status != 200:
        raise RuntimeError(f"Sitemap {url} devolvió HTTP {status}")
    root = ET.fromstring(body)
    locs = [normalize(el.text or "") for el in root.iter() if el.tag.endswith("loc")]
    if root.tag.endswith("sitemapindex"):
        urls: list[str] = []
        for child in locs:
            urls.extend(parse_sitemap(child))
        return urls
    return locs


def audit_page(url: str) -> dict:
    try:
        status, headers, body, elapsed = fetch(url)
        parser = PageParser()
        parser.feed(body.decode("utf-8", "replace"))
        visible_text = normalize(" ".join(parser.text_parts))
        page_tokens = tokens(visible_text)
        return {
            "url": url,
            "status": status,
            "elapsed_ms": round(elapsed * 1000),
            "content_type": headers.get("Content-Type") or headers.get("content-type"),
            "html_bytes": len(body),
            "title": normalize(" ".join(parser.title_parts)),
            "description": parser.description,
            "h1": normalize(" ".join(parser.h1_parts)),
            "h2": [part[0] for part in parser.h2_parts],
            "canonical": parser.canonical,
            "robots": parser.robots,
            "html_lang": parser.html_lang,
            "hreflang": parser.hreflang,
            "word_count": len(page_tokens),
            "visible_text": visible_text,
            "visible_text_sha256": hashlib.sha256(visible_text.encode("utf-8")).hexdigest(),
            "internal_links": sum(1 for href in parser.links if href.startswith("/") or "nodarishub.com" in href),
            "images": parser.images,
            "images_missing_alt": parser.images_missing_alt,
            "error": None,
        }
    except Exception as exc:
        return {"url": url, "status": None, "error": f"{type(exc).__name__}: {exc}"}


def pair_similarity(ec: dict, mx: dict) -> dict:
    ec_tokens = tokens(ec.get("visible_text", ""))
    mx_tokens = tokens(mx.get("visible_text", ""))
    seq_ratio = difflib.SequenceMatcher(None, ec_tokens, mx_tokens, autojunk=False).ratio()
    ec_set, mx_set = set(ec_tokens), set(mx_tokens)
    jaccard = len(ec_set & mx_set) / len(ec_set | mx_set) if ec_set | mx_set else 1.0
    ec_bigrams = set(zip(ec_tokens, ec_tokens[1:]))
    mx_bigrams = set(zip(mx_tokens, mx_tokens[1:]))
    bigram_jaccard = len(ec_bigrams & mx_bigrams) / len(ec_bigrams | mx_bigrams) if ec_bigrams | mx_bigrams else 1.0
    return {
        "ec_url": ec["url"],
        "mx_url": mx["url"],
        "ec_words": len(ec_tokens),
        "mx_words": len(mx_tokens),
        "sequence_similarity_pct": round(seq_ratio * 100, 2),
        "vocabulary_jaccard_pct": round(jaccard * 100, 2),
        "bigram_jaccard_pct": round(bigram_jaccard * 100, 2),
    }


def build_findings(pages: list[dict], pairs: list[dict], pair_candidates: int) -> dict:
    scoped = [p for p in pages if page_key(p["url"])]
    ok = [p for p in scoped if p.get("status") == 200 and not p.get("error")]
    return {
        "scoped_urls": len(scoped),
        "http_200": len(ok),
        "canonical_missing_or_mismatch": sum(1 for p in ok if p.get("canonical") != p["url"]),
        "hreflang_missing_required": sum(1 for p in ok if not {"es-EC", "es-MX", "x-default"}.issubset(p.get("hreflang", {}))),
        "noindex": sum(1 for p in ok if "noindex" in (p.get("robots") or "").lower()),
        "missing_h1": sum(1 for p in ok if not p.get("h1")),
        "missing_description": sum(1 for p in ok if not p.get("description")),
        "images_missing_alt": sum(p.get("images_missing_alt", 0) for p in ok),
        "images_total": sum(p.get("images", 0) for p in ok),
        "pair_candidates": pair_candidates,
        "paired": len(pairs),
        "pairs_over_95_sequence": sum(1 for p in pairs if p["sequence_similarity_pct"] > 95),
        "pairs_over_90_sequence": sum(1 for p in pairs if p["sequence_similarity_pct"] > 90),
        "average_sequence_similarity_pct": round(sum(p["sequence_similarity_pct"] for p in pairs) / len(pairs), 2) if pairs else None,
    }


def markdown(report: dict) -> str:
    s = report["summary"]
    lines = [
        "# Línea base SEO NodarisHub EC/MX",
        "",
        f"Fecha UTC: {report['measured_at_utc']}",
        "",
        "## Alcance",
        "",
        f"- URLs EC/MX encontradas en sitemap: {s['scoped_urls']}",
        f"- URLs con HTTP 200: {s['http_200']}/{s['scoped_urls']}",
        f"- Pares EC/MX completos: {s['paired']}/{s['pair_candidates']}",
        "",
        "## Hallazgos técnicos",
        "",
        f"- Canonical ausente o distinto de la URL: {s['canonical_missing_or_mismatch']}/{s['http_200']}",
        f"- Hreflang sin es-EC, es-MX o x-default: {s['hreflang_missing_required']}/{s['http_200']}",
        f"- Noindex: {s['noindex']}/{s['http_200']}",
        f"- H1 ausente: {s['missing_h1']}/{s['http_200']}",
        f"- Meta description ausente: {s['missing_description']}/{s['http_200']}",
        f"- Imágenes sin alt: {s['images_missing_alt']}/{s['images_total']}",
        "",
        "## Similitud por par",
        "",
        "| EC | MX | Palabras EC/MX | Secuencia | Bigramas | Vocabulario |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for pair in sorted(report["pairs"], key=lambda x: x["sequence_similarity_pct"], reverse=True):
        lines.append(
            f"| {urlparse(pair['ec_url']).path} | {urlparse(pair['mx_url']).path} | "
            f"{pair['ec_words']}/{pair['mx_words']} | {pair['sequence_similarity_pct']}% | "
            f"{pair['bigram_jaccard_pct']}% | {pair['vocabulary_jaccard_pct']}% |"
        )
    lines += [
        "",
        "## Resumen de similitud",
        "",
        f"- Promedio de similitud secuencial: {s['average_sequence_similarity_pct']}%",
        f"- Pares por encima de 95%: {s['pairs_over_95_sequence']}/{s['paired']}",
        f"- Pares por encima de 90%: {s['pairs_over_90_sequence']}/{s['paired']}",
        "",
        "> La similitud es una señal diagnóstica, no una penalización demostrada. Debe contrastarse con GSC/SERP antes de atribuir impacto causal.",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    sitemap_urls = sorted(set(parse_sitemap(f"{BASE}/sitemap_index.xml")))
    scoped_urls = [u for u in sitemap_urls if page_key(u)]
    pages = [audit_page(url) for url in scoped_urls]

    by_key: dict[str, dict[str, dict]] = {}
    for page in pages:
        key = page_key(page["url"])
        if key:
            market, suffix = key
            by_key.setdefault(suffix, {})[market] = page
    pair_candidates = len(by_key)
    pairs = [pair_similarity(v["ec"], v["mx"]) for v in by_key.values() if "ec" in v and "mx" in v and not v["ec"].get("error") and not v["mx"].get("error")]

    report = {
        "measured_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": "anonymous live HTML + Rank Math sitemap",
        "sitemap_urls_total": len(sitemap_urls),
        "summary": build_findings(pages, pairs, pair_candidates),
        "pairs": pairs,
        "pages": pages,
    }
    json_path = args.out / "baseline-live.json"
    md_path = args.out / "baseline-live.md"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(markdown(report), encoding="utf-8")
    print(json.dumps({"json": str(json_path), "markdown": str(md_path), "summary": report["summary"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
