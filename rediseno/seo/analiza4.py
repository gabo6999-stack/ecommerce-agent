# -*- coding: utf-8 -*-
import json,os,re,csv
from collections import defaultdict
D=os.path.dirname(os.path.abspath(__file__)); L=lambda n: json.load(open(os.path.join(D,n),encoding="utf-8"))
BASE="https://peptidosysuplementos.mx"
cp,cq,daily,qp=L("gsc_cur_page.json"),L("gsc_cur_query.json"),L("gsc_daily_365.json"),L("gsc_cur_query_page.json")
sm=L("sitemap_urls.json"); smtype={u["url"]:u["sitemap"] for u in sm}
est={BASE+e["url"]:e for e in L("urls_fuera_sitemap_estado.json")}

# resolver cada URL a su DESTINO final y reagrupar
def final(u):
    e=est.get(u)
    if e and e["http"].startswith("3") and e["final"]: return BASE+e["final"]
    return u
def tipo(u):
    p=(u.replace(BASE,"") or "/").split("?")[0]
    if p=="/": return "home"
    if p.startswith("/product/"): return "ficha producto"
    if p.startswith("/product-category/"): return "categoria producto"
    if p.startswith("/marca/"): return "marca (404)"
    if p.startswith("/category/") or p.startswith("/blog"): return "archivo blog"
    t=smtype.get(u)
    if t=="post": return "blog (articulo)"
    if t=="page": return "landing/pagina"
    if t=="product": return "ficha producto"
    return "pagina sin sitemap"
print("="*90); print("IMPRESIONES REAGRUPADAS POR DESTINO FINAL DEL 301 (quien deberia estar rankeando)")
ag=defaultdict(lambda:[0,0,set()])
for r in cp:
    f=final(r["keys"][0]); ag[f][0]+=r["impressions"]; ag[f][1]+=r["clicks"]; ag[f][2].add(r["keys"][0])
top=sorted(ag.items(),key=lambda x:-x[1][0])[:20]
print("%-46s %7s %6s %5s  %s" % ("destino final","impr","clics","#urls","tipo"))
for u,(i,c,s) in top:
    print("%-46s %7d %6d %5d  %s" % (u.replace(BASE,"")[:46],i,c,len(s),tipo(u)))
# tipo por destino final
bt=defaultdict(lambda:[0,0,0])
for u,(i,c,s) in ag.items():
    t=tipo(u); bt[t][0]+=i; bt[t][1]+=c; bt[t][2]+=1
T=sum(v[0] for v in bt.values())
print("\nPOR TIPO (tras consolidar redirecciones) — total %d impr" % T)
print("%-22s %5s %8s %7s %7s %8s" % ("tipo","urls","impr","% impr","clics","CTR%"))
rows=[]
for t,(i,c,n) in sorted(bt.items(),key=lambda x:-x[1][0]):
    print("%-22s %5d %8d %6.1f%% %7d %7.2f%%" % (t,n,i,100*i/T,c,100*c/i if i else 0))
    rows.append({"tipo":t,"urls":n,"impresiones":i,"pct":round(100*i/T,1),"clics":c,"ctr_pct":round(100*c/i,2) if i else 0})
with open(os.path.join(D,"tipos_pagina_consolidado.csv"),"w",newline="",encoding="utf-8-sig") as f:
    w=csv.DictWriter(f,fieldnames=["tipo","urls","impresiones","pct","clics","ctr_pct"]); w.writeheader(); [w.writerow(r) for r in rows]

# ── el blog: 19 articulos ────────────────────────────────────────────────
print("\n"+"="*90); print("RENDIMIENTO DEL BLOG (los 19 articulos del sitemap, consolidando sus URLs viejas)")
blog=[(u,v) for u,v in ag.items() if smtype.get(u)=="post"]
blog.sort(key=lambda x:-x[1][0])
print("%-58s %7s %6s" % ("articulo","impr","clics"))
bi=bc=0
for u,(i,c,s) in blog:
    print("%-58s %7d %6d" % (u.replace(BASE,"")[:58],i,c)); bi+=i; bc+=c
print("-> BLOG TOTAL: %d articulos, %d impresiones (%.1f%% del sitio), %d clics en 90 dias" % (len(blog),bi,100*bi/T,bc))

# ── CTR esperado vs real ─────────────────────────────────────────────────
print("\n"+"="*90); print("CUANTO CUESTA ESTAR EN LA POSICION EN LA QUE ESTAN")
CTR={1:.28,2:.15,3:.11,4:.08,5:.06,6:.05,7:.04,8:.03,9:.028,10:.025}
pot=0
for r in cq:
    if r["position"]<=10: pot+=r["impressions"]*CTR.get(int(round(r["position"])) or 1,.025)
print("  Clics que darian HOY las impresiones que ya estan en pag.1, con CTR normal: ~%.0f (reales: %d)" % (
    pot,sum(r["clicks"] for r in cq if r["position"]<=10)))
i21=sum(r["impressions"] for r in cq if r["position"]>20)
print("  Si esas %d impresiones en pos 21+ subieran a pos 5 (CTR 6%%): ~%.0f clics/90d" % (i21,i21*.06))
print("  ESTIMACION, no medicion.")

# resumen json
S={"periodo":["2026-06-22","2026-09-19"],"clics":72,"impresiones":5597,"ctr_pct":1.29,"posicion":36.5,
   "datos_gsc_desde":daily[0]["keys"][0],
   "impr_pos_21mas_pct":85.3,"impr_pag1_pct":10.8,
   "impr_a_urls_301_pct":56.9,"clics_a_urls_301_pct":34.2,
   "consultas_canibalizadas":121,"impr_canibalizadas_pct":78.4,
   "sitemap_urls":64,"sitemap_sin_impresiones":10,"urls_impr_fuera_sitemap":55,
   "blog_articulos":len(blog),"blog_impresiones":bi,"blog_clics":bc,
   "ultimo_post":"2026-08-22","impr_marca_pct":0.1}
json.dump(S,open(os.path.join(D,"resumen.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)
print("\n-> resumen.json guardado")
