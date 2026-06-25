import sys, os, json, time, re
sys.stdout.reconfigure(encoding='utf-8')
import requests
from requests.auth import HTTPBasicAuth
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

BASE = "https://peptidosysuplementos.mx"
WC_KEY = os.getenv("WC_CONSUMER_KEY", "")
WC_SEC = os.getenv("WC_CONSUMER_SECRET", "")
AUTH = HTTPBasicAuth(WC_KEY, WC_SEC)
HEADERS = {"User-Agent": "Mozilla/5.0 (SEO-Audit-Bot)"}

def get(url, **kw):
    try:
        r = requests.get(url, headers=HEADERS, timeout=15, **kw)
        return r
    except Exception as e:
        return None

def wc(endpoint, params=None):
    url = f"{BASE}/wp-json/wc/v3/{endpoint}"
    r = requests.get(url, auth=AUTH, params=params or {}, timeout=15)
    return r.json() if r.ok else []

# ── Score tracker ──────────────────────────────────────────────────────────────
scores = {}
findings = []

def check(category, item, ok, weight=1, detail=""):
    scores.setdefault(category, {"ok": 0, "total": 0, "weight": 0})
    scores[category]["total"] += weight
    scores[category]["weight"] += weight
    if ok:
        scores[category]["ok"] += weight
    status = "✅" if ok else "❌"
    findings.append(f"  {status} [{category}] {item}" + (f" — {detail}" if detail else ""))

# ══════════════════════════════════════════════════════════════════════════════
# 1. TÉCNICO — robots, sitemap, canonicals, HTTPS
# ══════════════════════════════════════════════════════════════════════════════
print("\n━━━ 1. TÉCNICO ━━━")

robots = get(f"{BASE}/robots.txt")
check("Técnico", "robots.txt accesible", robots and robots.status_code == 200)
if robots and robots.ok:
    rb = robots.text
    has_sitemap = "Sitemap" in rb
    blocks_admin = "Disallow: /wp-admin/" in rb
    check("Técnico", "robots.txt referencia sitemap", has_sitemap)
    check("Técnico", "robots.txt bloquea /wp-admin/", blocks_admin)
    print(f"    robots.txt: sitemap={has_sitemap}, bloquea-admin={blocks_admin}")

sitemap = get(f"{BASE}/sitemap_index.xml")
check("Técnico", "sitemap_index.xml presente", sitemap and sitemap.ok)
if sitemap and sitemap.ok:
    sub_sitemaps = re.findall(r'<loc>(.*?)</loc>', sitemap.text)
    check("Técnico", f"Sub-sitemaps encontrados ({len(sub_sitemaps)})", len(sub_sitemaps) > 0,
          detail=f"{len(sub_sitemaps)} subs")
    print(f"    Sitemaps: {sub_sitemaps[:5]}")

# HTTPS redirect
http_r = get(f"http://peptidosysuplementos.mx", allow_redirects=True)
check("Técnico", "HTTP → HTTPS redirect", http_r and http_r.url.startswith("https://"))

# Homepage load
t0 = time.time()
home = get(BASE)
load_ms = int((time.time() - t0) * 1000)
check("Técnico", f"Homepage carga <3s ({load_ms}ms)", load_ms < 3000, detail=f"{load_ms}ms")

# Canonical en homepage
if home and home.ok:
    soup = BeautifulSoup(home.text, "html.parser")
    canon = soup.find("link", rel="canonical")
    check("Técnico", "Canonical en homepage", bool(canon), detail=canon["href"] if canon else "ausente")

# ══════════════════════════════════════════════════════════════════════════════
# 2. ON-PAGE — homepage
# ══════════════════════════════════════════════════════════════════════════════
print("\n━━━ 2. ON-PAGE — Homepage ━━━")
if home and home.ok:
    soup = BeautifulSoup(home.text, "html.parser")
    title = soup.find("title")
    title_txt = title.text.strip() if title else ""
    check("On-Page", "Title tag presente", bool(title_txt))
    check("On-Page", f"Title ≤60c ({len(title_txt)}c)", len(title_txt) <= 60, detail=title_txt[:70])

    meta_desc = soup.find("meta", attrs={"name": "description"})
    desc_txt = meta_desc["content"].strip() if meta_desc and meta_desc.get("content") else ""
    check("On-Page", "Meta description presente", bool(desc_txt))
    check("On-Page", f"Meta desc 140-160c ({len(desc_txt)}c)", 140 <= len(desc_txt) <= 160, detail=desc_txt[:80])

    h1s = soup.find_all("h1")
    check("On-Page", f"Exactamente 1 H1 (encontrados: {len(h1s)})", len(h1s) == 1,
          detail=h1s[0].text.strip()[:60] if h1s else "ninguno")

    # BeautifulSoup no indexa 'property' como atributo estándar; usar regex directo
    raw = home.text
    og_title = bool(re.search(r'property=["\']og:title["\']', raw))
    og_desc = bool(re.search(r'property=["\']og:description["\']', raw))
    og_img_match = re.search(r'property=["\']og:image["\'][^>]*content=["\']([^"\']+)["\']|content=["\']([^"\']+)["\'][^>]*property=["\']og:image["\']', raw)
    og_img = bool(og_img_match)
    check("On-Page", "OG Title presente", og_title)
    check("On-Page", "OG Description presente", og_desc)
    check("On-Page", "OG Image presente", og_img, detail=og_img_match.group(1) or og_img_match.group(2) if og_img_match else "ausente")

    schema_tags = soup.find_all("script", type="application/ld+json")
    check("On-Page", f"Schema JSON-LD en homepage ({len(schema_tags)})", len(schema_tags) > 0)

    imgs_no_alt = [i for i in soup.find_all("img") if not i.get("alt")]
    check("On-Page", f"Imágenes sin alt ({len(imgs_no_alt)})", len(imgs_no_alt) == 0,
          detail=f"{len(imgs_no_alt)} sin alt")

# ══════════════════════════════════════════════════════════════════════════════
# 3. PRODUCTOS — on-page masivo via WC API
# ══════════════════════════════════════════════════════════════════════════════
print("\n━━━ 3. PRODUCTOS (WC API) ━━━")
products = wc("products", {"per_page": 100, "status": "publish"})
if isinstance(products, list):
    print(f"    Total productos publicados: {len(products)}")
    no_short = [p for p in products if not p.get("short_description","").strip()]
    no_desc = [p for p in products if not p.get("description","").strip()]
    check("Productos", f"Short description en todos ({len(no_short)} sin)", len(no_short)==0,
          detail=f"Sin short_desc: {[p['name'][:30] for p in no_short]}" if no_short else "")
    check("Productos", f"Description en todos ({len(no_desc)} sin)", len(no_desc)==0,
          detail=f"Sin desc: {[p['name'][:30] for p in no_desc]}" if no_desc else "")

    # Check rank_math meta en muestra
    no_rm_title, no_rm_desc, no_focus_kw = [], [], []
    has_schema = []
    for p in products:
        meta = {m["key"]: m["value"] for m in p.get("meta_data", [])}
        if not meta.get("rank_math_title"):
            no_rm_title.append(p["name"][:30])
        if not meta.get("rank_math_description"):
            no_rm_desc.append(p["name"][:30])
        if not meta.get("rank_math_focus_keyword"):
            no_focus_kw.append(p["name"][:30])
        desc = p.get("description","")
        if "FAQPage" in desc or "application/ld+json" in desc:
            has_schema.append(p["name"][:30])

    check("Productos", f"rank_math_title en todos ({len(no_rm_title)} sin)", len(no_rm_title)==0,
          detail=str(no_rm_title[:5]) if no_rm_title else "")
    check("Productos", f"rank_math_description en todos ({len(no_rm_desc)} sin)", len(no_rm_desc)==0,
          detail=str(no_rm_desc[:5]) if no_rm_desc else "")
    check("Productos", f"focus_keyword en todos ({len(no_focus_kw)} sin)", len(no_focus_kw)==0,
          detail=str(no_focus_kw[:5]) if no_focus_kw else "")
    check("Productos", f"FAQPage schema ({len(has_schema)}/{len(products)} productos)", len(has_schema)==len(products),
          detail=f"Con schema: {len(has_schema)}")

    # Image alt
    no_img_alt = []
    for p in products:
        imgs = p.get("images", [])
        for img in imgs:
            if not img.get("alt","").strip():
                no_img_alt.append(p["name"][:30])
                break
    check("Productos", f"Image alt en todos ({len(no_img_alt)} sin)", len(no_img_alt)==0,
          detail=str(no_img_alt[:5]) if no_img_alt else "")

# ══════════════════════════════════════════════════════════════════════════════
# 4. BLOGS — check via WP REST API (public)
# ══════════════════════════════════════════════════════════════════════════════
print("\n━━━ 4. BLOGS (WP REST API) ━━━")
posts_r = get(f"{BASE}/wp-json/wp/v2/posts?per_page=20&status=publish")
posts = posts_r.json() if posts_r and posts_r.ok else []
if posts:
    print(f"    Total posts encontrados: {len(posts)}")
    no_excerpt = [p for p in posts if not p.get("excerpt",{}).get("rendered","").strip()]
    check("Blogs", f"Excerpt/meta en todos ({len(no_excerpt)} sin)", len(no_excerpt)==0)

    # Fetch 3 posts to check schema + H1
    schema_ok, h1_ok = 0, 0
    for post in posts[:5]:
        link = post.get("link","")
        if not link: continue
        pr = get(link)
        if not pr or not pr.ok: continue
        sp = BeautifulSoup(pr.text, "html.parser")
        if sp.find("script", type="application/ld+json"):
            schema_ok += 1
        if sp.find_all("h1"):
            h1_ok += 1
    check("Blogs", f"Schema JSON-LD en posts ({schema_ok}/5 revisados)", schema_ok >= 3,
          detail=f"{schema_ok}/5")
    check("Blogs", f"H1 en posts ({h1_ok}/5 revisados)", h1_ok >= 4,
          detail=f"{h1_ok}/5")

# ══════════════════════════════════════════════════════════════════════════════
# 5. PÁGINAS CLAVE
# ══════════════════════════════════════════════════════════════════════════════
print("\n━━━ 5. PÁGINAS CLAVE ━━━")
key_pages = [
    ("Categoría péptidos", f"{BASE}/peptidos-en-mexico/"),
    ("Categoría suplementos", f"{BASE}/suplementos/"),
    ("Tienda/Productos", f"{BASE}/productos/"),
    ("BPC-157 producto", f"{BASE}/product/bpc-157-tb-500-10-10mg/"),
]
for name, url in key_pages:
    r = get(url)
    if not r or not r.ok:
        check("Páginas", f"{name} accesible", False, detail=f"HTTP {r.status_code if r else 'error'}")
        continue
    check("Páginas", f"{name} accesible", True)
    sp = BeautifulSoup(r.text, "html.parser")
    title = sp.find("title")
    meta = sp.find("meta", attrs={"name":"description"})
    tl = len(title.text.strip()) if title else 0
    dl = len(meta["content"].strip()) if meta and meta.get("content") else 0
    check("Páginas", f"{name} — title OK ({tl}c)", 30 <= tl <= 65, detail=title.text.strip()[:60] if title else "")
    check("Páginas", f"{name} — meta desc OK ({dl}c)", 120 <= dl <= 165)

# ══════════════════════════════════════════════════════════════════════════════
# 6. VELOCIDAD / CORE WEB VITALS proxy
# ══════════════════════════════════════════════════════════════════════════════
print("\n━━━ 6. VELOCIDAD ━━━")
pages_to_time = [BASE, f"{BASE}/peptidos-en-mexico/", f"{BASE}/product/semaglutida-5-mg/"]
for url in pages_to_time:
    t0 = time.time()
    r = get(url)
    ms = int((time.time()-t0)*1000)
    size_kb = len(r.content)//1024 if r else 0
    check("Velocidad", f"Carga <2s: {url.replace(BASE,'')or'/'} ({ms}ms)", ms < 2000,
          detail=f"{ms}ms, {size_kb}KB")

# ══════════════════════════════════════════════════════════════════════════════
# 7. LINKS INTERNOS rotos (muestra)
# ══════════════════════════════════════════════════════════════════════════════
print("\n━━━ 7. LINKS INTERNOS ━━━")
# Revisar links en página de categoría peptidos
cat_r = get(f"{BASE}/peptidos-en-mexico/")
broken = []
if cat_r and cat_r.ok:
    sp = BeautifulSoup(cat_r.text, "html.parser")
    internal_links = set()
    for a in sp.find_all("a", href=True):
        href = a["href"]
        if BASE in href and "/product/" in href:
            internal_links.add(href.split("?")[0])
    for link in list(internal_links)[:15]:
        lr = get(link, allow_redirects=True)
        if not lr or lr.status_code >= 400:
            broken.append(link)
    check("Links", f"Links rotos en /peptidos-en-mexico/ ({len(broken)})", len(broken)==0,
          detail=str(broken) if broken else "")

# ══════════════════════════════════════════════════════════════════════════════
# RESULTADO FINAL
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "═"*70)
print("  RESULTADOS POR CATEGORÍA")
print("═"*70)
total_ok = total_pts = 0
cat_scores = {}
for item in findings:
    pass  # already printed via check()

# Recalculate from scores dict
for cat, data in scores.items():
    pct = int(data["ok"] / data["total"] * 100) if data["total"] else 0
    cat_scores[cat] = pct
    bar = "█" * (pct//10) + "░" * (10 - pct//10)
    print(f"  {cat:<15} {bar} {pct:>3}%  ({data['ok']}/{data['total']} checks)")
    total_ok += data["ok"]
    total_pts += data["total"]

global_score = int(total_ok / total_pts * 100) if total_pts else 0
print("\n" + "═"*70)
print(f"  SCORE GLOBAL PYS:  {global_score}/100")
print("═"*70)

# Findings
print("\n━━━ HALLAZGOS DETALLADOS ━━━")
for f in findings:
    print(f)

print("\n━━━ PRIORIDADES DE MEJORA ━━━")
for f in findings:
    if f.strip().startswith("❌"):
        print(f)
