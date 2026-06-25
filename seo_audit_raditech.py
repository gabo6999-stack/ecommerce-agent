import sys, os, json, time, re
sys.stdout.reconfigure(encoding='utf-8')
import requests
from bs4 import BeautifulSoup

BASE = "https://raditech.mx"
HEADERS = {"User-Agent": "Mozilla/5.0 (SEO-Audit-Bot/1.0)"}

def get(url, **kw):
    try:
        r = requests.get(url, headers=HEADERS, timeout=15, **kw)
        return r
    except Exception as e:
        return None

scores = {}
findings = []

def check(category, item, ok, weight=1, detail=""):
    scores.setdefault(category, {"ok": 0, "total": 0})
    scores[category]["total"] += weight
    if ok:
        scores[category]["ok"] += weight
    status = "✅" if ok else "❌"
    findings.append(f"  {status} [{category}] {item}" + (f" — {detail}" if detail else ""))

# ══════════════════════════════════════════════════════════════════════════════
# 1. TÉCNICO
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
    print(f"    robots.txt preview:\n{rb[:400]}")

sitemap = get(f"{BASE}/sitemap_index.xml")
sitemap_alt = get(f"{BASE}/sitemap.xml") if not (sitemap and sitemap.ok) else None
sitemap_ok = (sitemap and sitemap.ok) or (sitemap_alt and sitemap_alt.ok)
check("Técnico", "Sitemap XML presente", sitemap_ok)
if sitemap_ok:
    sm_text = sitemap.text if (sitemap and sitemap.ok) else sitemap_alt.text
    sub_sitemaps = re.findall(r'<loc>(.*?)</loc>', sm_text)
    check("Técnico", f"Sub-sitemaps/URLs en sitemap ({len(sub_sitemaps)})", len(sub_sitemaps) > 0,
          detail=f"{len(sub_sitemaps)} entradas")
    print(f"    Sitemap URLs: {sub_sitemaps[:6]}")

# HTTPS
http_r = get(f"http://raditech.mx", allow_redirects=True)
check("Técnico", "HTTP → HTTPS redirect", http_r and http_r.url.startswith("https://"))

# Velocidad homepage
t0 = time.time()
home = get(BASE)
load_ms = int((time.time() - t0) * 1000)
check("Técnico", f"Homepage carga <3s ({load_ms}ms)", load_ms < 3000, detail=f"{load_ms}ms")

if home and home.ok:
    soup = BeautifulSoup(home.text, "html.parser")
    canon = soup.find("link", rel="canonical")
    check("Técnico", "Canonical en homepage", bool(canon),
          detail=canon["href"] if canon else "ausente")

    # Check www vs non-www consistency
    check("Técnico", "Sin www (canonical limpio)", "www" not in (canon["href"] if canon else ""),
          detail=canon["href"] if canon else "")

# ══════════════════════════════════════════════════════════════════════════════
# 2. ON-PAGE — Homepage
# ══════════════════════════════════════════════════════════════════════════════
print("\n━━━ 2. ON-PAGE — Homepage ━━━")
if home and home.ok:
    soup = BeautifulSoup(home.text, "html.parser")
    raw = home.text

    title = soup.find("title")
    title_txt = title.text.strip() if title else ""
    check("On-Page", "Title tag presente", bool(title_txt))
    check("On-Page", f"Title ≤60c ({len(title_txt)}c)", len(title_txt) <= 60,
          detail=f'"{title_txt}"')

    meta_desc = soup.find("meta", attrs={"name": "description"})
    desc_txt = meta_desc["content"].strip() if meta_desc and meta_desc.get("content") else ""
    check("On-Page", "Meta description presente", bool(desc_txt))
    check("On-Page", f"Meta desc 140-160c ({len(desc_txt)}c)", 140 <= len(desc_txt) <= 160,
          detail=f'"{desc_txt[:80]}..."')

    h1s = soup.find_all("h1")
    check("On-Page", f"Exactamente 1 H1 ({len(h1s)} encontrados)", len(h1s) == 1,
          detail=h1s[0].text.strip()[:60] if h1s else "ninguno")

    og_title = bool(re.search(r'property=["\']og:title["\']', raw))
    og_desc  = bool(re.search(r'property=["\']og:description["\']', raw))
    og_img_m = re.search(r'property=["\']og:image["\'][^>]*content=["\']([^"\']+)["\']|content=["\']([^"\']+)["\'][^>]*property=["\']og:image["\']', raw)
    check("On-Page", "OG Title presente", og_title)
    check("On-Page", "OG Description presente", og_desc)
    check("On-Page", "OG Image presente", bool(og_img_m),
          detail=(og_img_m.group(1) or og_img_m.group(2))[:60] if og_img_m else "ausente")

    schema_tags = soup.find_all("script", type="application/ld+json")
    check("On-Page", f"Schema JSON-LD en homepage ({len(schema_tags)})", len(schema_tags) > 0,
          detail=f"{len(schema_tags)} bloques")
    for i, s in enumerate(schema_tags):
        try:
            d = json.loads(s.string or "{}"); print(f"    Schema {i+1}: @type={d.get('@type','?')}")
        except: pass

    imgs_no_alt = [i for i in soup.find_all("img") if not i.get("alt","").strip()]
    check("On-Page", f"Imágenes sin alt ({len(imgs_no_alt)})", len(imgs_no_alt) == 0,
          detail=f"{len(imgs_no_alt)} sin alt" + (f": {[i.get('src','')[:50] for i in imgs_no_alt[:3]]}" if imgs_no_alt else ""))

    # Focus keyword check
    kw_targets = ["pacs", "teleradiologia", "radiologia", "ris", "imagen medica"]
    h1_text = " ".join([h.text.lower() for h in h1s])
    kw_found = [kw for kw in kw_targets if kw in h1_text or kw in title_txt.lower()]
    check("On-Page", f"Keyword principal en H1/Title", bool(kw_found),
          detail=f"encontradas: {kw_found}" if kw_found else "ninguna de las keywords clave")

# ══════════════════════════════════════════════════════════════════════════════
# 3. PÁGINAS INTERNAS
# ══════════════════════════════════════════════════════════════════════════════
print("\n━━━ 3. PÁGINAS INTERNAS ━━━")
key_pages = [
    ("PACS", f"{BASE}/pacs/"),
    ("Teleradiología", f"{BASE}/teleradiologia/"),
    ("RIS", f"{BASE}/ris/"),
    ("Servicios", f"{BASE}/servicios/"),
    ("Contacto", f"{BASE}/contacto/"),
    ("Blog", f"{BASE}/blog/"),
    ("Nosotros", f"{BASE}/nosotros/"),
    ("Pricing/Precios", f"{BASE}/precios/"),
]
found_pages = []
for name, url in key_pages:
    r = get(url)
    ok = r and r.status_code == 200
    check("Páginas", f"{name} accesible", ok,
          detail=f"HTTP {r.status_code if r else 'timeout'}" if not ok else url)
    if ok:
        found_pages.append((name, url, r))
        sp = BeautifulSoup(r.text, "html.parser")
        t = sp.find("title")
        m = sp.find("meta", attrs={"name": "description"})
        tl = len(t.text.strip()) if t else 0
        dl = len(m["content"].strip()) if m and m.get("content") else 0
        check("Páginas", f"{name} — title ≤60c ({tl}c)", tl > 0 and tl <= 60,
              detail=t.text.strip()[:65] if t else "sin title")
        check("Páginas", f"{name} — meta desc 140-160c ({dl}c)", 140 <= dl <= 160)

# ══════════════════════════════════════════════════════════════════════════════
# 4. BLOG / CONTENIDO
# ══════════════════════════════════════════════════════════════════════════════
print("\n━━━ 4. BLOG / CONTENIDO ━━━")
posts_r = get(f"{BASE}/wp-json/wp/v2/posts?per_page=20&status=publish")
posts = posts_r.json() if posts_r and posts_r.ok else []
if posts:
    print(f"    Posts publicados: {len(posts)}")
    check("Blog", f"Posts de blog ({len(posts)})", len(posts) >= 3,
          detail=f"{len(posts)} posts encontrados")
    no_excerpt = [p for p in posts if not p.get("excerpt",{}).get("rendered","").strip()]
    check("Blog", f"Excerpt/meta en todos ({len(no_excerpt)} sin)", len(no_excerpt) == 0)

    schema_ok = h1_ok = 0
    for post in posts[:5]:
        link = post.get("link","")
        if not link: continue
        pr = get(link)
        if not pr or not pr.ok: continue
        sp = BeautifulSoup(pr.text, "html.parser")
        if sp.find("script", type="application/ld+json"): schema_ok += 1
        if sp.find_all("h1"): h1_ok += 1
        print(f"    Post: {post['title']['rendered'][:50]} — schema={'sí' if sp.find('script',type='application/ld+json') else 'no'}")
    check("Blog", f"Schema en posts ({schema_ok}/5)", schema_ok >= 3)
    check("Blog", f"H1 en posts ({h1_ok}/5)", h1_ok >= 4)
else:
    print("    No se encontraron posts vía WP REST API")
    check("Blog", "Posts de blog accesibles vía API", False, detail="API no disponible o sin posts")

# ══════════════════════════════════════════════════════════════════════════════
# 5. VELOCIDAD
# ══════════════════════════════════════════════════════════════════════════════
print("\n━━━ 5. VELOCIDAD ━━━")
speed_pages = [BASE] + [url for _, url, _ in found_pages[:2]]
for url in speed_pages:
    t0 = time.time()
    r = get(url)
    ms = int((time.time()-t0)*1000)
    size_kb = len(r.content)//1024 if r else 0
    check("Velocidad", f"Carga <2s: {url.replace(BASE,'') or '/'} ({ms}ms)",
          ms < 2000, detail=f"{ms}ms, {size_kb}KB")

# ══════════════════════════════════════════════════════════════════════════════
# 6. LINKS INTERNOS
# ══════════════════════════════════════════════════════════════════════════════
print("\n━━━ 6. LINKS INTERNOS ━━━")
broken = []
if home and home.ok:
    sp = BeautifulSoup(home.text, "html.parser")
    internal = set()
    for a in sp.find_all("a", href=True):
        href = a["href"]
        if BASE in href and href != BASE and href != BASE+"/":
            internal.add(href.split("?")[0].rstrip("/"))
    print(f"    Links internos en homepage: {len(internal)}")
    for link in list(internal)[:15]:
        lr = get(link, allow_redirects=True)
        if not lr or lr.status_code >= 400:
            broken.append(f"{link} → {lr.status_code if lr else 'timeout'}")
    check("Links", f"Links rotos en homepage ({len(broken)})", len(broken) == 0,
          detail=str(broken) if broken else "")

# ══════════════════════════════════════════════════════════════════════════════
# 7. SEO TÉCNICO AVANZADO
# ══════════════════════════════════════════════════════════════════════════════
print("\n━━━ 7. SEO AVANZADO ━━━")
if home and home.ok:
    raw = home.text
    # Structured data types
    schemas = re.findall(r'"@type"\s*:\s*"([^"]+)"', raw)
    check("SEO Avanzado", f"Organization/LocalBusiness schema",
          any(t in schemas for t in ["Organization","LocalBusiness","MedicalOrganization","Corporation"]),
          detail=f"tipos encontrados: {list(set(schemas))}" if schemas else "ninguno")

    # hreflang
    has_hreflang = bool(re.search(r'hreflang', raw))
    check("SEO Avanzado", "hreflang (multilang)", has_hreflang, weight=0,
          detail="presente" if has_hreflang else "ausente (ok si sitio es solo español)")

    # Viewport meta
    check("SEO Avanzado", "Meta viewport (mobile)", bool(re.search(r'name=["\']viewport["\']', raw)))

    # Favicon
    fav = get(f"{BASE}/favicon.ico")
    check("SEO Avanzado", "Favicon presente", fav and fav.status_code == 200)

    # SSL cert / HSTS
    check("SEO Avanzado", "Sitio en HTTPS", home.url.startswith("https://"))

# ══════════════════════════════════════════════════════════════════════════════
# RESULTADO FINAL
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "═"*70)
print("  RESULTADOS POR CATEGORÍA — RADITECH.MX")
print("═"*70)
total_ok = total_pts = 0
for cat, data in scores.items():
    pct = int(data["ok"] / data["total"] * 100) if data["total"] else 0
    bar = "█" * (pct//10) + "░" * (10 - pct//10)
    print(f"  {cat:<15} {bar} {pct:>3}%  ({data['ok']}/{data['total']} checks)")
    total_ok += data["ok"]
    total_pts += data["total"]

global_score = int(total_ok / total_pts * 100) if total_pts else 0
print("\n" + "═"*70)
print(f"  SCORE GLOBAL RADITECH:  {global_score}/100")
print("═"*70)

print("\n━━━ HALLAZGOS DETALLADOS ━━━")
for f in findings:
    print(f)

print("\n━━━ ISSUES A CORREGIR (por prioridad) ━━━")
fails = [f for f in findings if f.strip().startswith("❌")]
for f in fails:
    print(f)
print(f"\nTotal issues: {len(fails)}")
