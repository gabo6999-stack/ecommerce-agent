# -*- coding: utf-8 -*-
"""
seo_health.py — Escáner de salud SEO genérico y comparable entre sitios.

Basado en el escáner por categorías de seo_audit_nodarishub.py, pero parametrizado
por URL para que corra igual en cualquier sitio (PYS, nodarishub, raditech,
arcademotorsmx). Devuelve datos estructurados (no imprime) para empujarlos a NEXUS.

Categorías: Técnico · On-Page · Velocidad · Headers → score global 0–100.
Como la rúbrica es idéntica para todos los sitios, los scores son comparables
de un vistazo (verde/ámbar/rojo significan lo mismo en cada tarjeta del dashboard).
"""
import re
import time
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (SEO-Health-Bot; +nexus)"}
TIMEOUT = 20


def _get(url, **kw):
    try:
        return requests.get(url, headers=HEADERS, timeout=TIMEOUT, **kw)
    except Exception:
        return None


def audit_site(name, url):
    """Audita un sitio y devuelve un dict estructurado con score, categorías y hallazgos.

    Nunca lanza excepción: si el sitio no responde, devuelve score 0 y error poblado.
    """
    base = url.rstrip("/")
    scanned_at = datetime.now(timezone.utc).isoformat()
    scores = {}      # cat -> {"ok": int, "total": int}
    findings = []    # [{"cat","item","ok","detail"}]

    def check(cat, item, ok, weight=1, detail=""):
        ok = bool(ok)
        scores.setdefault(cat, {"ok": 0, "total": 0})
        scores[cat]["total"] += weight
        if ok:
            scores[cat]["ok"] += weight
        findings.append({"cat": cat, "item": item, "ok": ok, "detail": str(detail)[:200]})

    # ─── 1. TÉCNICO ───────────────────────────────────────────────────────────
    robots = _get(f"{base}/robots.txt")
    check("Técnico", "robots.txt accesible", robots is not None and robots.status_code == 200)
    if robots is not None and robots.ok:
        check("Técnico", "robots.txt referencia sitemap", "Sitemap" in robots.text)
        check("Técnico", "robots.txt bloquea /wp-admin/", "Disallow: /wp-admin/" in robots.text)
    sitemap = _get(f"{base}/sitemap_index.xml") or _get(f"{base}/sitemap.xml")
    check("Técnico", "sitemap presente", sitemap is not None and sitemap.ok)

    http_host = base.replace("https://", "http://")
    http_r = _get(http_host, allow_redirects=True)
    check("Técnico", "HTTP → HTTPS redirect", http_r is not None and http_r.url.startswith("https://"))

    domain = base.replace("https://", "").replace("http://", "")
    if not domain.startswith("www."):
        www_r = _get(f"https://www.{domain}", allow_redirects=True)
        check("Técnico", "www resuelve/redirige", www_r is not None and www_r.status_code < 400)

    t0 = time.time()
    home = _get(base)
    load_ms = int((time.time() - t0) * 1000)

    if home is None or not home.ok:
        # Sitio caído: registrar el fallo y devolver score bajo sin reventar.
        check("Técnico", "Homepage responde 200", False,
              detail=f"status {home.status_code}" if home is not None else "sin respuesta")
        return _finalize(name, url, scanned_at, scores, findings,
                         error="homepage no respondió 200")

    check("Técnico", "Homepage responde 200", True)
    check("Técnico", f"Homepage carga <3s ({load_ms}ms)", load_ms < 3000, detail=f"{load_ms}ms")

    soup = BeautifulSoup(home.text, "html.parser")
    raw = home.text

    canon = soup.find("link", rel="canonical")
    check("Técnico", "Canonical en homepage", bool(canon),
          detail=canon["href"] if canon and canon.get("href") else "ausente")
    html_tag = soup.find("html")
    check("Técnico", "HTML lang declarado", bool(soup.find("html", attrs={"lang": True})),
          detail=html_tag.get("lang", "") if html_tag else "")
    check("Técnico", "Viewport meta (responsive)", bool(soup.find("meta", attrs={"name": "viewport"})))
    check("Técnico", "Favicon presente",
          bool(soup.find("link", rel=lambda v: v and "icon" in v)))

    # ─── 2. ON-PAGE (homepage) ────────────────────────────────────────────────
    title = soup.find("title")
    title_txt = title.text.strip() if title else ""
    check("On-Page", "Title tag presente", bool(title_txt))
    check("On-Page", f"Title ≤60c ({len(title_txt)}c)", 15 <= len(title_txt) <= 60, detail=title_txt)

    md = soup.find("meta", attrs={"name": "description"})
    desc = md["content"].strip() if md and md.get("content") else ""
    check("On-Page", "Meta description presente", bool(desc))
    check("On-Page", f"Meta desc 120–160c ({len(desc)}c)", 120 <= len(desc) <= 160, detail=desc)

    h1s = soup.find_all("h1")
    check("On-Page", f"Exactamente 1 H1 ({len(h1s)})", len(h1s) == 1,
          detail=h1s[0].text.strip()[:70] if h1s else "ninguno")
    h2s = soup.find_all("h2")
    check("On-Page", f"Jerarquía H2 presente ({len(h2s)})", len(h2s) >= 2, detail=f"{len(h2s)} H2")

    check("On-Page", "OG Title", bool(re.search(r'property=["\']og:title["\']', raw)))
    check("On-Page", "OG Description", bool(re.search(r'property=["\']og:description["\']', raw)))
    check("On-Page", "OG Image", bool(re.search(r'property=["\']og:image["\']', raw)))
    check("On-Page", "Twitter Card", bool(re.search(r'name=["\']twitter:card["\']', raw)))

    schema_tags = soup.find_all("script", type="application/ld+json")
    types = re.findall(r'"@type"\s*:\s*"([^"]+)"', raw)
    check("On-Page", f"Schema JSON-LD ({len(schema_tags)} bloques)", len(schema_tags) > 0,
          detail=f"tipos: {sorted(set(types))}")

    imgs = soup.find_all("img")
    no_alt = [i for i in imgs if not (i.get("alt") or "").strip()]
    check("On-Page", f"Imágenes con alt ({len(no_alt)} sin alt de {len(imgs)})", len(no_alt) == 0,
          detail=f"{len(no_alt)} sin alt de {len(imgs)}")
    lazy = [i for i in imgs if i.get("loading") == "lazy"]
    check("On-Page", f"Lazy-loading imágenes ({len(lazy)}/{len(imgs)})",
          len(imgs) == 0 or len(lazy) >= len(imgs) * 0.5, detail=f"{len(lazy)}/{len(imgs)} lazy")

    text = soup.get_text(" ", strip=True)
    wc = len(text.split())
    check("On-Page", f"Contenido suficiente ({wc} palabras)", wc >= 300, detail=f"{wc} palabras")

    # ─── 3. VELOCIDAD / PESO ──────────────────────────────────────────────────
    size_kb = len(home.content) // 1024
    check("Velocidad", f"HTML <100KB ({size_kb}KB)", size_kb < 100, detail=f"{size_kb}KB")
    n_css = len(re.findall(r'<link[^>]+rel=["\']stylesheet["\']', raw))
    n_js = len(re.findall(r'<script[^>]+src=', raw))
    check("Velocidad", f"CSS externos ≤8 ({n_css})", n_css <= 8, detail=f"{n_css} hojas CSS")
    check("Velocidad", f"JS externos ≤12 ({n_js})", n_js <= 12, detail=f"{n_js} scripts")
    enc = home.headers.get("Content-Encoding", "")
    check("Velocidad", "Compresión gzip/br", "gzip" in enc or "br" in enc, detail=enc or "ninguna")
    check("Velocidad", "Cache-Control presente", bool(home.headers.get("Cache-Control")),
          detail=home.headers.get("Cache-Control", "ausente"))

    # ─── 4. HEADERS / SEGURIDAD ───────────────────────────────────────────────
    h = home.headers
    check("Headers", "HSTS (Strict-Transport-Security)", bool(h.get("Strict-Transport-Security")))
    check("Headers", "X-Content-Type-Options: nosniff",
          h.get("X-Content-Type-Options", "").lower() == "nosniff")
    check("Headers", "Servidor identifica", bool(h.get("Server")), detail=h.get("Server", ""))

    return _finalize(name, url, scanned_at, scores, findings, error=None)


def _finalize(name, url, scanned_at, scores, findings, error):
    """Calcula porcentajes por categoría y el score global."""
    categories = {}
    tok = tpt = 0
    for cat, d in scores.items():
        pct = int(d["ok"] / d["total"] * 100) if d["total"] else 0
        categories[cat] = {"pct": pct, "ok": d["ok"], "total": d["total"]}
        tok += d["ok"]
        tpt += d["total"]
    score = int(tok / tpt * 100) if tpt else 0
    failures = [f for f in findings if not f["ok"]]
    return {
        "name": name,
        "url": url,
        "score": score,
        "categories": categories,
        "findings": findings,
        "failures": failures,
        "scanned_at": scanned_at,
        "error": error,
    }


if __name__ == "__main__":
    import sys
    import json as _json
    sys.stdout.reconfigure(encoding="utf-8")
    target = sys.argv[1] if len(sys.argv) > 1 else "https://nodarishub.com"
    res = audit_site(target.replace("https://", "").replace("http://", ""), target)
    print(_json.dumps(
        {k: v for k, v in res.items() if k != "findings"}, ensure_ascii=False, indent=2))
    print(f"\nSCORE {res['name']}: {res['score']}/100  ({len(res['failures'])} fallos)")
