import sys, os, time, re
sys.stdout.reconfigure(encoding='utf-8')
import requests
from bs4 import BeautifulSoup

BASE = "https://nodarishub.com"
HEADERS = {"User-Agent": "Mozilla/5.0 (SEO-Audit-Bot)"}

def get(url, **kw):
    try:
        return requests.get(url, headers=HEADERS, timeout=20, **kw)
    except Exception:
        return None

scores, findings = {}, []
def check(cat, item, ok, weight=1, detail=""):
    scores.setdefault(cat, {"ok": 0, "total": 0})
    scores[cat]["total"] += weight
    if ok: scores[cat]["ok"] += weight
    findings.append(f"  {'✅' if ok else '❌'} [{cat}] {item}" + (f" — {detail}" if detail else ""))

# 1. TÉCNICO
print("\n━━━ 1. TÉCNICO ━━━")
robots = get(f"{BASE}/robots.txt")
check("Técnico", "robots.txt accesible", robots and robots.status_code == 200)
if robots and robots.ok:
    check("Técnico", "robots.txt referencia sitemap", "Sitemap" in robots.text)
    check("Técnico", "robots.txt bloquea /wp-admin/", "Disallow: /wp-admin/" in robots.text)
sitemap = get(f"{BASE}/sitemap_index.xml")
check("Técnico", "sitemap_index.xml presente", sitemap and sitemap.ok)
http_r = get("http://nodarishub.com", allow_redirects=True)
check("Técnico", "HTTP → HTTPS redirect", http_r and http_r.url.startswith("https://"))
www_r = get("https://www.nodarishub.com", allow_redirects=True)
check("Técnico", "www redirige a canónico", www_r is not None and www_r.status_code < 400)
t0 = time.time(); home = get(BASE); load_ms = int((time.time()-t0)*1000)
check("Técnico", f"Homepage carga <3s ({load_ms}ms)", load_ms < 3000, detail=f"{load_ms}ms")
if home and home.ok:
    soup = BeautifulSoup(home.text, "html.parser")
    canon = soup.find("link", rel="canonical")
    check("Técnico", "Canonical en homepage", bool(canon), detail=canon["href"] if canon else "ausente")
    check("Técnico", "HTML lang declarado", bool(soup.find("html", attrs={"lang": True})),
          detail=soup.find("html").get("lang","") if soup.find("html") else "")
    check("Técnico", "Viewport meta (responsive)", bool(soup.find("meta", attrs={"name":"viewport"})))
    check("Técnico", "Favicon presente",
          bool(soup.find("link", rel=lambda v: v and "icon" in v)))

# 2. ON-PAGE homepage
print("\n━━━ 2. ON-PAGE ━━━")
if home and home.ok:
    soup = BeautifulSoup(home.text, "html.parser")
    title = soup.find("title"); title_txt = title.text.strip() if title else ""
    check("On-Page", "Title tag presente", bool(title_txt))
    check("On-Page", f"Title ≤60c ({len(title_txt)}c)", 15 <= len(title_txt) <= 60, detail=title_txt)
    md = soup.find("meta", attrs={"name": "description"})
    desc = md["content"].strip() if md and md.get("content") else ""
    check("On-Page", "Meta description presente", bool(desc))
    check("On-Page", f"Meta desc 120-160c ({len(desc)}c)", 120 <= len(desc) <= 160, detail=desc)
    h1s = soup.find_all("h1")
    check("On-Page", f"Exactamente 1 H1 ({len(h1s)})", len(h1s) == 1,
          detail=h1s[0].text.strip()[:70] if h1s else "ninguno")
    h2s = soup.find_all("h2")
    check("On-Page", f"Jerarquía H2 presente ({len(h2s)})", len(h2s) >= 2, detail=f"{len(h2s)} H2")
    raw = home.text
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
    check("On-Page", f"Imágenes con alt ({len(no_alt)}/{len(imgs)} sin alt)", len(no_alt) == 0,
          detail=f"{len(no_alt)} sin alt de {len(imgs)}")
    lazy = [i for i in imgs if i.get("loading") == "lazy"]
    check("On-Page", f"Lazy-loading imágenes ({len(lazy)}/{len(imgs)})", len(imgs)==0 or len(lazy) >= len(imgs)*0.5,
          detail=f"{len(lazy)}/{len(imgs)} lazy")
    # word count (contenido)
    text = soup.get_text(" ", strip=True)
    wc = len(text.split())
    check("On-Page", f"Contenido suficiente ({wc} palabras)", wc >= 300, detail=f"{wc} palabras")

# 3. VELOCIDAD / peso
print("\n━━━ 3. VELOCIDAD / PESO ━━━")
if home:
    size_kb = len(home.content)//1024
    check("Velocidad", f"HTML <100KB ({size_kb}KB)", size_kb < 100, detail=f"{size_kb}KB")
    raw = home.text
    n_css = len(re.findall(r'<link[^>]+rel=["\']stylesheet["\']', raw))
    n_js = len(re.findall(r'<script[^>]+src=', raw))
    check("Velocidad", f"CSS externos ≤8 ({n_css})", n_css <= 8, detail=f"{n_css} hojas CSS")
    check("Velocidad", f"JS externos ≤12 ({n_js})", n_js <= 12, detail=f"{n_js} scripts")
    check("Velocidad", "Compresión gzip/br", 'gzip' in home.headers.get('Content-Encoding','') or 'br' in home.headers.get('Content-Encoding',''),
          detail=home.headers.get('Content-Encoding','ninguna'))
    check("Velocidad", "Cache-Control presente", bool(home.headers.get('Cache-Control')),
          detail=home.headers.get('Cache-Control','ausente'))

# 4. SEGURIDAD / HEADERS
print("\n━━━ 4. HEADERS / SEGURIDAD ━━━")
if home:
    h = home.headers
    check("Headers", "HSTS (Strict-Transport-Security)", bool(h.get('Strict-Transport-Security')))
    check("Headers", "X-Content-Type-Options", h.get('X-Content-Type-Options','').lower()=='nosniff')
    check("Headers", "Servidor identifica", bool(h.get('Server')), detail=h.get('Server',''))

# RESULTADO
print("\n" + "═"*70)
print("  RESULTADOS POR CATEGORÍA")
print("═"*70)
tok = tpt = 0
for cat, d in scores.items():
    pct = int(d["ok"]/d["total"]*100) if d["total"] else 0
    bar = "█"*(pct//10) + "░"*(10-pct//10)
    print(f"  {cat:<12} {bar} {pct:>3}%  ({d['ok']}/{d['total']})")
    tok += d["ok"]; tpt += d["total"]
gs = int(tok/tpt*100) if tpt else 0
print("\n" + "═"*70)
print(f"  SCORE GLOBAL NODARISHUB:  {gs}/100")
print("═"*70)
print("\n━━━ HALLAZGOS ━━━")
for f in findings: print(f)
print("\n━━━ PRIORIDADES (fallos) ━━━")
for f in findings:
    if "❌" in f: print(f)
