"""
Auditoría SEO PROFUNDA — raditech.mx (2026-06-24)
Usa el inventario REAL del sitemap (sin slugs genéricos = sin falsos positivos).
Chequea: técnico, on-page de TODAS las páginas+posts, redirects 301, schema, imágenes,
velocidad, links rotos, favicon. Salida con score por categoría + JSON.
"""
import sys, re, time, json
sys.stdout.reconfigure(encoding='utf-8')
import requests
from bs4 import BeautifulSoup

BASE = "https://raditech.mx"
UA = {"User-Agent": "Mozilla/5.0 (SEO-Deep-Audit/2.0)"}

def get(url, **kw):
    try: return requests.get(url, headers=UA, timeout=20, **kw)
    except Exception: return None

scores, findings = {}, []
def check(cat, item, ok, weight=1, detail=""):
    scores.setdefault(cat, {"ok":0,"total":0})
    scores[cat]["total"] += weight
    if ok: scores[cat]["ok"] += weight
    findings.append(f"  {'✅' if ok else '❌'} [{cat}] {item}" + (f" — {detail}" if detail else ""))

def page_seo(url):
    r = get(url)
    if not r or not r.ok: return None
    s = BeautifulSoup(r.text, "html.parser"); raw = r.text
    t = s.find("title"); t = t.text.strip() if t else ""
    m = s.find("meta", attrs={"name":"description"})
    d = m["content"].strip() if m and m.get("content") else ""
    h1 = s.find_all("h1")
    canon = s.find("link", rel="canonical")
    return {
        "status": r.status_code, "title": t, "tlen": len(t), "desc": d, "dlen": len(d),
        "h1": len(h1), "canon": canon["href"] if canon else "",
        "schema": len(s.find_all("script", type="application/ld+json")),
        "og_img": bool(re.search(r'property=["\']og:image["\']', raw)),
        "imgs_no_alt": len([i for i in s.find_all("img") if not i.get("alt","").strip()]),
        "bytes": len(r.content),
    }

# ── 1. TÉCNICO ───────────────────────────────────────────────────────────────
print("━━━ 1. TÉCNICO ━━━")
robots = get(f"{BASE}/robots.txt")
check("Técnico","robots.txt accesible", robots and robots.ok)
if robots and robots.ok:
    check("Técnico","robots.txt referencia sitemap","sitemap" in robots.text.lower())
    check("Técnico","robots.txt bloquea /wp-admin/","Disallow: /wp-admin/" in robots.text)
sm = get(f"{BASE}/sitemap_index.xml")
check("Técnico","sitemap_index.xml presente", sm and sm.ok)
sub = re.findall(r'<loc>(.*?)</loc>', sm.text) if sm and sm.ok else []
check("Técnico", f"Sub-sitemaps ({len(sub)})", len(sub)>0, detail=str([u.split('/')[-1] for u in sub]))
http_r = get("http://raditech.mx", allow_redirects=True)
check("Técnico","HTTP→HTTPS redirect", http_r and http_r.url.startswith("https://"))
fav = get(f"{BASE}/favicon.ico")
check("Técnico","favicon.ico sirve (200)", fav and fav.status_code==200,
      detail=f"{fav.status_code if fav else '?'} {fav.headers.get('content-type','') if fav else ''}")
home = get(BASE)
if home and home.ok:
    s = BeautifulSoup(home.text,"html.parser")
    canon = s.find("link", rel="canonical")
    check("Técnico","Canonical homepage sin www", bool(canon) and "www" not in canon["href"],
          detail=canon["href"] if canon else "ausente")
    check("Técnico","Meta viewport (mobile)", bool(s.find("meta", attrs={"name":"viewport"})))

# ── 2. INVENTARIO REAL (sitemap) ─────────────────────────────────────────────
print("━━━ 2. INVENTARIO desde sitemap ━━━")
page_urls, post_urls = [], []
for sub_url in sub:
    r = get(sub_url)
    if not r or not r.ok: continue
    urls = re.findall(r'<loc>(.*?)</loc>', r.text)
    if "post-sitemap" in sub_url: post_urls += urls
    elif "page-sitemap" in sub_url: page_urls += urls
    else: page_urls += urls
print(f"    Páginas: {len(page_urls)} | Posts: {len(post_urls)}")

# ── 3. ON-PAGE TODAS LAS PÁGINAS ─────────────────────────────────────────────
print("━━━ 3. ON-PAGE PÁGINAS ━━━")
short_titles, long_titles, no_desc, bad_desc, multi_h1, no_h1 = [],[],[],[],[],[]
for u in page_urls:
    p = page_seo(u)
    if not p:
        check("Páginas", f"{u.replace(BASE,'')} accesible", False); continue
    slug = u.replace(BASE,'') or "/"
    if p["tlen"]==0: short_titles.append(slug)
    elif p["tlen"]>60: long_titles.append(f"{slug}({p['tlen']})")
    if p["dlen"]==0: no_desc.append(slug)
    elif not (120<=p["dlen"]<=160): bad_desc.append(f"{slug}({p['dlen']})")
    if p["h1"]==0: no_h1.append(slug)
    elif p["h1"]>1: multi_h1.append(f"{slug}({p['h1']})")
check("Páginas", f"Títulos presentes (sin vacíos)", len(short_titles)==0, detail=str(short_titles))
check("Páginas", f"Títulos ≤60c", len(long_titles)==0, detail=str(long_titles[:6]))
check("Páginas", f"Meta desc presente en todas", len(no_desc)==0, detail=str(no_desc))
check("Páginas", f"Meta desc 120-160c", len(bad_desc)==0, detail=str(bad_desc[:8]))
check("Páginas", f"1 H1 por página (0 sin H1)", len(no_h1)==0, detail=str(no_h1))
check("Páginas", f"Sin múltiples H1", len(multi_h1)==0, detail=str(multi_h1[:6]))

# ── 4. POSTS / BLOG ──────────────────────────────────────────────────────────
print("━━━ 4. POSTS/BLOG ━━━")
p_no_desc, p_no_schema, p_no_h1 = [],[],[]
for u in post_urls:
    p = page_seo(u)
    if not p: continue
    slug = u.replace(BASE,'')
    if p["dlen"]==0: p_no_desc.append(slug)
    if p["schema"]==0: p_no_schema.append(slug)
    if p["h1"]!=1: p_no_h1.append(f"{slug}(h1={p['h1']})")
check("Blog", f"Posts ({len(post_urls)})", len(post_urls)>=3)
check("Blog", "Meta desc en todos los posts", len(p_no_desc)==0, detail=str(p_no_desc))
check("Blog", "Schema JSON-LD en todos los posts", len(p_no_schema)==0, detail=str(p_no_schema))
check("Blog", "1 H1 por post", len(p_no_h1)==0, detail=str(p_no_h1[:6]))

# ── 5. REDIRECTS 301 ─────────────────────────────────────────────────────────
print("━━━ 5. REDIRECTS 301 ━━━")
REDIRECTS = [
    ("/aviso-de-privacidad/","/politicas-de-privacidad/"),
    ("/resonancia-magnetica-cardiovascular/","/teleradiologia-resonancia-cardiovascular/"),
    ("/tomografia-cardiaca-y-angiotomografia-coronaria/","/teleradiologia-tomografia-cardiaca/"),
    ("/sistema-de-informacion-hospitalaria-his/","/sistema-his-medsi/"),
    ("/pacs-ris/","/sistema-pacs-ris/"),
    ("/monitores-grado-medico/","/monitores-medicos-radiologia/"),
    ("/x-card/","/portal-x-card/"),
    ("/teleradiologia/","/servicio-teleradiologia/"),
]
for src,dst in REDIRECTS:
    rr = get(f"{BASE}{src}", allow_redirects=False)
    ok = rr is not None and rr.status_code in (301,308)
    check("Redirects", f"{src} → 301", ok, detail=f"{rr.status_code if rr else '?'}→{rr.headers.get('Location','').replace(BASE,'')[:40] if rr else ''}")

# ── 6. SCHEMA HOMEPAGE ───────────────────────────────────────────────────────
print("━━━ 6. SCHEMA ━━━")
if home and home.ok:
    types = re.findall(r'"@type"\s*:\s*"([^"]+)"', home.text)
    check("Schema","Organization/LocalBusiness en homepage",
          any(t in types for t in ["Organization","LocalBusiness","MedicalOrganization","Corporation"]),
          detail=str(sorted(set(types))))

# ── 7. VELOCIDAD ─────────────────────────────────────────────────────────────
print("━━━ 7. VELOCIDAD ━━━")
for u in [BASE]+page_urls[:3]:
    t0=time.time(); r=get(u); ms=int((time.time()-t0)*1000)
    check("Velocidad", f"{(u.replace(BASE,'') or '/')} <2s", ms<2000, detail=f"{ms}ms, {len(r.content)//1024 if r else 0}KB")

# ── 8. LINKS INTERNOS ────────────────────────────────────────────────────────
print("━━━ 8. LINKS INTERNOS ━━━")
broken=[]
if home and home.ok:
    s=BeautifulSoup(home.text,"html.parser")
    internal={a["href"].split("?")[0].rstrip("/") for a in s.find_all("a",href=True)
              if BASE in a["href"] and a["href"].rstrip("/")!=BASE}
    for link in list(internal)[:25]:
        lr=get(link, allow_redirects=True)
        if not lr or lr.status_code>=400: broken.append(f"{link.replace(BASE,'')}→{lr.status_code if lr else 'timeout'}")
    check("Links", f"Sin links rotos en homepage ({len(internal)} revisados)", len(broken)==0, detail=str(broken))

# ── RESULTADO ────────────────────────────────────────────────────────────────
print("\n"+"═"*70); print("  RESULTADOS POR CATEGORÍA — RADITECH.MX (PROFUNDA)"); print("═"*70)
tok=tpt=0
for cat,d in scores.items():
    pct=int(d["ok"]/d["total"]*100) if d["total"] else 0
    print(f"  {cat:<12} {'█'*(pct//10)}{'░'*(10-pct//10)} {pct:>3}%  ({d['ok']}/{d['total']})")
    tok+=d["ok"]; tpt+=d["total"]
g=int(tok/tpt*100) if tpt else 0
print("\n"+"═"*70); print(f"  SCORE GLOBAL: {g}/100  ({tok}/{tpt} checks)"); print("═"*70)
print("\n━━━ ISSUES (❌) ━━━")
fails=[f for f in findings if f.strip().startswith("❌")]
for f in fails: print(f)
print(f"\nTotal issues reales: {len(fails)}")
print("\n━━━ TODOS LOS HALLAZGOS ━━━")
for f in findings: print(f)
