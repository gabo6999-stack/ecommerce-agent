# -*- coding: utf-8 -*-
import json, os, re, csv
from collections import defaultdict
from datetime import datetime, date, timedelta
D = os.path.dirname(os.path.abspath(__file__))
L = lambda n: json.load(open(os.path.join(D, n), encoding="utf-8"))
BASE = "https://peptidosysuplementos.mx"

daily = L("gsc_daily_365.json")
cq, cp = L("gsc_cur_query.json"), L("gsc_cur_page.json")
pq, pp = L("gsc_prev_query.json"), L("gsc_prev_page.json")
qp = L("gsc_cur_query_page.json")
sm = L("sitemap_urls.json")
smset = set(u["url"] for u in sm)
smtype = {u["url"]: u["sitemap"] for u in sm}

def W(name, rows, cols):
    with open(os.path.join(D, name), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader()
        for r in rows: w.writerow({c: r.get(c, "") for c in cols})

# ── 1. SERIE DIARIA / MENSUAL ────────────────────────────────────────────
print("="*78); print("1. CRECIMIENTO — serie real de datos disponibles")
d0, d1 = daily[0]["keys"][0], daily[-1]["keys"][0]
print("Datos de GSC disponibles: %s -> %s  (%d dias)" % (d0, d1, len(daily)))
bym = defaultdict(lambda: [0,0,0.0,0])   # clicks, impr, pos*impr, dias
for r in daily:
    m = r["keys"][0][:7]
    bym[m][0]+=r["clicks"]; bym[m][1]+=r["impressions"]
    bym[m][2]+=r["position"]*r["impressions"]; bym[m][3]+=1
print("\n%-9s %6s %8s %7s %7s %6s" % ("mes","dias","impr","clics","CTR%","pos"))
mrows=[]
for m in sorted(bym):
    c,i,pw,dd = bym[m]
    pos = pw/i if i else 0
    print("%-9s %6d %8d %7d %7.2f %6.1f" % (m,dd,i,c,100*c/i if i else 0,pos))
    mrows.append({"mes":m,"dias":dd,"impresiones":i,"clics":c,"ctr_pct":round(100*c/i,2) if i else 0,"posicion":round(pos,1)})
W("mensual.csv", mrows, ["mes","dias","impresiones","clics","ctr_pct","posicion"])

# mitades iguales del periodo con datos
half = len(daily)//2
def agg(rows):
    c=sum(r["clicks"] for r in rows); i=sum(r["impressions"] for r in rows)
    p=sum(r["position"]*r["impressions"] for r in rows)/i if i else 0
    return c,i,(100*c/i if i else 0),p
A=daily[:half]; B=daily[half:]
ca,ia,ta,pa = agg(A); cb,ib,tb,pb = agg(B)
print("\nCOMPARACION LIKE-FOR-LIKE (mitades iguales de %d dias c/u):" % half)
print("  %s..%s : %5d impr %4d clics CTR %.2f%% pos %.1f" % (A[0]['keys'][0],A[-1]['keys'][0],ia,ca,ta,pa))
print("  %s..%s : %5d impr %4d clics CTR %.2f%% pos %.1f" % (B[0]['keys'][0],B[-1]['keys'][0],ib,cb,tb,pb))
def pc(n,o): return "n/a" if not o else "%+.0f%%" % (100*(n-o)/o)
print("  delta  : impr %s | clics %s | CTR %s | pos %+.1f" % (pc(ib,ia),pc(cb,ca),pc(tb,ta),pb-pa))

# ── 2. TECHO: impresiones por tramo de posicion ──────────────────────────
print("\n"+"="*78); print("2. DONDE ESTA EL TECHO")
def bucket(p):
    if p<=3: return "1-3"
    if p<=10: return "4-10"
    if p<=20: return "11-20"
    if p<=50: return "21-50"
    return "51+"
ORD=["1-3","4-10","11-20","21-50","51+"]
bq=defaultdict(lambda:[0,0]); 
for r in cq: b=bucket(r["position"]); bq[b][0]+=r["impressions"]; bq[b][1]+=r["clicks"]
TI=sum(v[0] for v in bq.values()); TC=sum(v[1] for v in bq.values())
print("\nPor CONSULTA (posicion media de la consulta) — total %d impr / %d clics" % (TI,TC))
print("%-7s %8s %7s %7s %8s" % ("tramo","impr","% impr","clics","CTR%"))
brows=[]
for b in ORD:
    i,c=bq[b]
    print("%-7s %8d %6.1f%% %7d %7.2f%%" % (b,i,100*i/TI if TI else 0,c,100*c/i if i else 0))
    brows.append({"tramo":b,"impresiones":i,"pct_impresiones":round(100*i/TI,1) if TI else 0,"clics":c,"ctr_pct":round(100*c/i,2) if i else 0})
W("tramos_posicion_query.csv", brows, ["tramo","impresiones","pct_impresiones","clics","ctr_pct"])
top10 = sum(bq[b][0] for b in ["1-3","4-10"]); 
print("-> Impresiones en pagina 1 (pos<=10): %d = %.1f%%" % (top10,100*top10/TI))
print("-> Impresiones en pos 21+           : %d = %.1f%%" % (bq['21-50'][0]+bq['51+'][0],100*(bq['21-50'][0]+bq['51+'][0])/TI))

# por tramo a nivel query+page (mas granular)
bqp=defaultdict(lambda:[0,0])
for r in qp: b=bucket(r["position"]); bqp[b][0]+=r["impressions"]; bqp[b][1]+=r["clicks"]
TI2=sum(v[0] for v in bqp.values())
print("\nPor par CONSULTA+URL — total %d impr" % TI2)
for b in ORD:
    i,c=bqp[b]; print("%-7s %8d %6.1f%% %7d clics" % (b,i,100*i/TI2 if TI2 else 0,c))

# ── tipo de pagina ───────────────────────────────────────────────────────
def ptype(u):
    p = u.replace(BASE,"") or "/"
    p = p.split("?")[0]
    if p=="/" : return "home"
    if p.startswith("/product/"): return "ficha producto"
    if p.startswith("/product-category/") or p.startswith("/categoria-producto/"): return "categoria producto"
    if p.startswith("/marca/"): return "marca"
    if p.startswith("/category/") or p.startswith("/tag/"): return "archivo blog"
    if u in smtype:
        return {"post":"blog","page":"landing/pagina","product":"ficha producto","category":"archivo blog"}[smtype[u]]
    if p.startswith("/tienda") or p.startswith("/shop"): return "tienda"
    return "otra/huerfana"
print("\nPor TIPO DE PAGINA (dimension page, 90d)")
bt=defaultdict(lambda:[0,0,0,0.0])
for r in cp:
    t=ptype(r["keys"][0]); bt[t][0]+=r["impressions"]; bt[t][1]+=r["clicks"]; bt[t][2]+=1; bt[t][3]+=r["position"]*r["impressions"]
TIP=sum(v[0] for v in bt.values())
print("%-20s %5s %8s %7s %7s %8s %6s" % ("tipo","urls","impr","% impr","clics","CTR%","pos"))
trows=[]
for t,(i,c,n,pw) in sorted(bt.items(), key=lambda x:-x[1][0]):
    print("%-20s %5d %8d %6.1f%% %7d %7.2f%% %6.1f" % (t,n,i,100*i/TIP,c,100*c/i if i else 0,pw/i if i else 0))
    trows.append({"tipo":t,"urls":n,"impresiones":i,"pct_impresiones":round(100*i/TIP,1),"clics":c,"ctr_pct":round(100*c/i,2) if i else 0,"posicion":round(pw/i,1) if i else 0})
W("tipos_pagina.csv", trows, ["tipo","urls","impresiones","pct_impresiones","clics","ctr_pct","posicion"])
