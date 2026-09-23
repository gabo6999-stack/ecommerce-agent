# -*- coding: utf-8 -*-
import json, os, re, csv
from collections import defaultdict
D = os.path.dirname(os.path.abspath(__file__))
L = lambda n: json.load(open(os.path.join(D, n), encoding="utf-8"))
BASE="https://peptidosysuplementos.mx"
cq,cp,pq,pp,qp = L("gsc_cur_query.json"),L("gsc_cur_page.json"),L("gsc_prev_query.json"),L("gsc_prev_page.json"),L("gsc_cur_query_page.json")
sm=L("sitemap_urls.json"); smset=set(u["url"] for u in sm); smtype={u["url"]:u["sitemap"] for u in sm}
def W(name,rows,cols):
    with open(os.path.join(D,name),"w",newline="",encoding="utf-8-sig") as f:
        w=csv.DictWriter(f,fieldnames=cols); w.writeheader()
        for r in rows: w.writerow({c:r.get(c,"") for c in cols})

# ── 3. CONSULTAS ──────────────────────────────────────────────────────────
print("="*100); print("3. TOP 30 CONSULTAS POR IMPRESIONES (90d: 2026-06-22 -> 2026-09-19)")
MARCA=re.compile(r"peptidos?\s*y\s*suplementos|peptidosysuplementos|\bpys\b|peptidos y suple",re.I)
TRANS=re.compile(r"compr|precio|cuanto cuesta|venta|donde|tienda|barat|envio|cuesta|costo|\bmx\b|mexico|pedido",re.I)
INFO=re.compile(r"\bque es\b|\bpara que\b|como |dosis|efectos|beneficio|sirve|funciona|vs |diferencia|protocolo|reconstitu|calcul",re.I)
def cls(q):
    if MARCA.search(q): return "marca"
    return "generico"
def intent(q):
    if TRANS.search(q): return "transaccional"
    if INFO.search(q): return "informacional"
    return "navegacional/otro"
top=sorted(cq,key=lambda r:-r["impressions"])[:30]
print("%-3s %-42s %7s %6s %7s %7s %-11s %-16s" % ("#","consulta","impr","clics","CTR%","pos","tipo","intencion"))
rows=[]
for n,r in enumerate(top,1):
    q=r["keys"][0]
    print("%-3d %-42s %7d %6d %6.2f%% %7.1f %-11s %-16s" % (n,q[:42],r["impressions"],r["clicks"],100*r["ctr"],r["position"],cls(q),intent(q)))
for r in cq:
    q=r["keys"][0]
    rows.append({"consulta":q,"impresiones":r["impressions"],"clics":r["clicks"],"ctr_pct":round(100*r["ctr"],2),"posicion":round(r["position"],1),"tipo":cls(q),"intencion":intent(q)})
W("consultas_90d.csv",sorted(rows,key=lambda x:-x["impresiones"]),["consulta","impresiones","clics","ctr_pct","posicion","tipo","intencion"])

agg=defaultdict(lambda:[0,0])
for r in cq:
    k=(cls(r["keys"][0]),intent(r["keys"][0])); agg[k][0]+=r["impressions"]; agg[k][1]+=r["clicks"]
T=sum(v[0] for v in agg.values())
print("\nREPARTO MARCA vs GENERICO x INTENCION")
print("%-10s %-18s %8s %7s %7s" % ("tipo","intencion","impr","% impr","clics"))
for k,v in sorted(agg.items(),key=lambda x:-x[1][0]):
    print("%-10s %-18s %8d %6.1f%% %7d" % (k[0],k[1],v[0],100*v[0]/T,v[1]))
mk=sum(v[0] for k,v in agg.items() if k[0]=="marca"); mc=sum(v[1] for k,v in agg.items() if k[0]=="marca")
print("-> MARCA: %d impr (%.1f%%), %d clics | GENERICO: %d impr (%.1f%%), %d clics" % (mk,100*mk/T,mc,T-mk,100*(T-mk)/T,sum(v[1] for v in agg.values())-mc))

print("\nCONSULTAS EN LA BANDA GANABLE (posicion 8-20, ordenadas por impresiones)")
band=[r for r in cq if 8<=r["position"]<=20]
band.sort(key=lambda r:-r["impressions"])
print("%-3s %-44s %7s %6s %7s %7s %-15s" % ("#","consulta","impr","clics","CTR%","pos","intencion"))
brows=[]
for n,r in enumerate(band[:25],1):
    q=r["keys"][0]
    print("%-3d %-44s %7d %6d %6.2f%% %7.1f %-15s" % (n,q[:44],r["impressions"],r["clicks"],100*r["ctr"],r["position"],intent(q)))
    brows.append({"consulta":q,"impresiones":r["impressions"],"clics":r["clicks"],"ctr_pct":round(100*r["ctr"],2),"posicion":round(r["position"],1),"intencion":intent(q)})
print("TOTAL banda 8-20: %d consultas, %d impresiones (%.1f%% del total), %d clics" % (
    len(band),sum(r["impressions"] for r in band),100*sum(r["impressions"] for r in band)/T,sum(r["clicks"] for r in band)))
W("consultas_banda_8_20.csv",brows,["consulta","impresiones","clics","ctr_pct","posicion","intencion"])

# ── 4. PAGINAS ────────────────────────────────────────────────────────────
print("\n"+"="*100); print("4. TOP 30 PAGINAS POR IMPRESIONES (90d)")
prevp={r["keys"][0]:r for r in pp}
tp=sorted(cp,key=lambda r:-r["impressions"])[:30]
print("%-3s %-52s %7s %6s %7s %7s %-9s %s" % ("#","url","impr","clics","CTR%","pos","sitemap","prev_impr"))
for n,r in enumerate(tp,1):
    u=r["keys"][0]; p=u.replace(BASE,"")
    pv=prevp.get(u)
    print("%-3d %-52s %7d %6d %6.2f%% %7.1f %-9s %s" % (n,p[:52],r["impressions"],r["clicks"],100*r["ctr"],r["position"],
        "SI" if u in smset else "NO",("%d (pos %.0f)"%(pv["impressions"],pv["position"])) if pv else "-"))
prows=[]
for r in cp:
    u=r["keys"][0]; pv=prevp.get(u)
    prows.append({"url":u.replace(BASE,""),"impresiones":r["impressions"],"clics":r["clicks"],"ctr_pct":round(100*r["ctr"],2),
        "posicion":round(r["position"],1),"en_sitemap":"SI" if u in smset else "NO",
        "impr_periodo_anterior":pv["impressions"] if pv else 0,"pos_periodo_anterior":round(pv["position"],1) if pv else ""})
W("paginas_90d.csv",sorted(prows,key=lambda x:-x["impresiones"]),
  ["url","impresiones","clics","ctr_pct","posicion","en_sitemap","impr_periodo_anterior","pos_periodo_anterior"])

print("\nURLs QUE RECIBEN IMPRESIONES Y **NO** ESTAN EN EL SITEMAP (huerfanas/redirigidas/borradas)")
orf=[r for r in cp if r["keys"][0] not in smset]
orf.sort(key=lambda r:-r["impressions"])
print("%-3s %-56s %7s %6s %7s" % ("#","url","impr","clics","pos"))
orows=[]
for n,r in enumerate(orf[:30],1):
    print("%-3d %-56s %7d %6d %7.1f" % (n,r["keys"][0].replace(BASE,"")[:56],r["impressions"],r["clicks"],r["position"]))
    orows.append({"url":r["keys"][0].replace(BASE,""),"impresiones":r["impressions"],"clics":r["clicks"],"posicion":round(r["position"],1)})
TT=sum(r["impressions"] for r in cp)
print("TOTAL huerfanas: %d URLs, %d impr = %.1f%% de todas las impresiones, %d clics" % (
    len(orf),sum(r["impressions"] for r in orf),100*sum(r["impressions"] for r in orf)/TT,sum(r["clicks"] for r in orf)))
W("urls_fuera_de_sitemap.csv",orows,["url","impresiones","clics","posicion"])

print("\nGANADORAS / PERDEDORAS (impresiones actual vs anterior; el periodo anterior solo tiene 54 dias con datos)")
comp=[]
for r in cp:
    u=r["keys"][0]; pv=prevp.get(u)
    comp.append({"url":u.replace(BASE,""),"impr":r["impressions"],"impr_prev":pv["impressions"] if pv else 0,
                 "pos":r["position"],"pos_prev":pv["position"] if pv else None,"clics":r["clicks"],"clics_prev":pv["clicks"] if pv else 0})
hund=[c for c in comp if c["pos_prev"] is not None and c["pos"]-c["pos_prev"]>=8]
hund.sort(key=lambda c:-(c["pos"]-c["pos_prev"]))
print("\n  HUNDIDAS (perdieron >=8 posiciones):")
print("  %-50s %7s %7s %8s %8s" % ("url","pos_ant","pos_act","impr_ant","impr_act"))
for c in hund[:15]: print("  %-50s %7.1f %7.1f %8d %8d" % (c["url"][:50],c["pos_prev"],c["pos"],c["impr_prev"],c["impr"]))
sub=[c for c in comp if c["pos_prev"] is not None and c["pos_prev"]-c["pos"]>=5]
sub.sort(key=lambda c:-(c["pos_prev"]-c["pos"]))
print("\n  MEJORARON (>=5 posiciones):")
for c in sub[:10]: print("  %-50s %7.1f %7.1f %8d %8d" % (c["url"][:50],c["pos_prev"],c["pos"],c["impr_prev"],c["impr"]))
W("paginas_ganadoras_perdedoras.csv",sorted(comp,key=lambda c:-c["impr"]),["url","impr","impr_prev","pos","pos_prev","clics","clics_prev"])
