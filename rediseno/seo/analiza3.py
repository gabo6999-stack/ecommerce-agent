# -*- coding: utf-8 -*-
import json,os,csv
from collections import defaultdict
D=os.path.dirname(os.path.abspath(__file__)); L=lambda n: json.load(open(os.path.join(D,n),encoding="utf-8"))
BASE="https://peptidosysuplementos.mx"
qp,cp,daily=L("gsc_cur_query_page.json"),L("gsc_cur_page.json"),L("gsc_daily_365.json")
sm=L("sitemap_urls.json"); smset=set(u["url"] for u in sm); smtype={u["url"]:u["sitemap"] for u in sm}
est={BASE+e["url"]:e for e in L("urls_fuera_sitemap_estado.json")}
def W(n,rows,cols):
    with open(os.path.join(D,n),"w",newline="",encoding="utf-8-sig") as f:
        w=csv.DictWriter(f,fieldnames=cols); w.writeheader()
        for r in rows: w.writerow({c:r.get(c,"") for c in cols})

# cuanto pesa el 301
tot=sum(r["impressions"] for r in cp); totc=sum(r["clicks"] for r in cp)
r301=[e for e in est.values() if e["http"].startswith("3")]
i301=sum(e["impresiones"] for e in r301); c301=sum(e["clics"] for e in r301)
r404=[e for e in est.values() if e["http"]=="404"]
print("="*100)
print("PESO DE LAS URLs VIEJAS REDIRIGIDAS (301) — 90d")
print("  URLs con 301 que aun reciben impresiones : %d" % len(r301))
print("  Impresiones que van a URLs 301           : %d de %d = %.1f%%" % (i301,tot,100*i301/tot))
print("  Clics que van a URLs 301                 : %d de %d = %.1f%%" % (c301,totc,100*c301/totc))
print("  URLs 404 con impresiones                 : %d (%s)" % (len(r404),", ".join(e["url"] for e in r404)))
print("  URLs 200 fuera del sitemap               : %d" % len([e for e in est.values() if e["http"]=="200"]))

# ── 5. CANIBALIZACION ─────────────────────────────────────────────────────
print("\n"+"="*100); print("5. CANIBALIZACION — consultas servidas por 2+ URLs (>=5 impr totales)")
byq=defaultdict(list)
for r in qp: byq[r["keys"][0]].append(r)
can=[]
for q,rs in byq.items():
    if len(rs)<2: continue
    ti=sum(x["impressions"] for x in rs)
    if ti<5: continue
    can.append((q,ti,sum(x["clicks"] for x in rs),sorted(rs,key=lambda x:-x["impressions"])))
can.sort(key=lambda x:-x[1])
print("%d consultas canibalizadas, %d impresiones implicadas (%.1f%% del total)\n" % (
    len(can),sum(c[1] for c in can),100*sum(c[1] for c in can)/sum(r["impressions"] for r in qp)))
crows=[]
for q,ti,tc,rs in can[:25]:
    print("  '%s'  — %d impr, %d clics, %d URLs" % (q,ti,tc,len(rs)))
    for x in rs:
        u=x["keys"][1].replace(BASE,"")
        flag="301->"+est[x["keys"][1]]["redirect"] if x["keys"][1] in est and est[x["keys"][1]]["http"].startswith("3") else ("404" if x["keys"][1] in est and est[x["keys"][1]]["http"]=="404" else "")
        print("      %-56s %5d impr  pos %5.1f  %d clics  %s" % (u[:56],x["impressions"],x["position"],x["clicks"],flag))
for q,ti,tc,rs in can:
    for x in rs:
        u=x["keys"][1]
        crows.append({"consulta":q,"impr_total_consulta":ti,"url":u.replace(BASE,""),"impresiones":x["impressions"],
            "clics":x["clicks"],"posicion":round(x["position"],1),
            "estado":est[u]["http"] if u in est else "200(sitemap)","redirige_a":est[u]["redirect"] if u in est else ""})
W("canibalizacion.csv",crows,["consulta","impr_total_consulta","url","impresiones","clics","posicion","estado","redirige_a"])

# ── 6. INDEXACION ─────────────────────────────────────────────────────────
print("\n"+"="*100); print("6. INDEXACION — sitemap vs realidad")
seen={r["keys"][0]:r for r in cp}
con=[u for u in sm if u["url"] in seen]; sin=[u for u in sm if u["url"] not in seen]
print("  URLs en el sitemap                         : %d" % len(sm))
print("  URLs del sitemap CON impresiones en 90d    : %d (%.0f%%)" % (len(con),100*len(con)/len(sm)))
print("  URLs del sitemap SIN ninguna impresion     : %d (%.0f%%)" % (len(sin),100*len(sin)/len(sm)))
print("  URLs con impresiones que NO estan en el sitemap: %d" % len([r for r in cp if r["keys"][0] not in smset]))
tb=defaultdict(lambda:[0,0])
for u in sm:
    tb[u["sitemap"]][0]+=1
    if u["url"] in seen: tb[u["sitemap"]][1]+=1
print("\n  %-10s %6s %10s %10s" % ("sitemap","urls","con impr","sin impr"))
for t,(n,c) in tb.items(): print("  %-10s %6d %10d %10d" % (t,n,c,n-c))
print("\n  URLs PUBLICADAS QUE NUNCA APARECEN EN GSC (0 impresiones en 90 dias):")
srows=[]
for u in sin:
    print("    [%-8s] %s" % (u["sitemap"],u["url"].replace(BASE,"")))
    srows.append({"url":u["url"].replace(BASE,""),"tipo":u["sitemap"]})
W("sitemap_sin_impresiones.csv",srows,["url","tipo"])
# con impresiones pero 0 clics
cero=[r for r in cp if r["clicks"]==0]
print("\n  URLs con impresiones pero CERO clics en 90d: %d de %d (%.0f%%), %d impresiones desperdiciadas" % (
    len(cero),len(cp),100*len(cero)/len(cp),sum(r["impressions"] for r in cero)))

# ── 7. REDISEÑO ───────────────────────────────────────────────────────────
print("\n"+"="*100); print("7. EFECTO DEL REDISENO (19-22 sep 2026)")
print("  Ultimo dia con datos en GSC: %s" % daily[-1]["keys"][0])
print("  El rediseno empezo el 2026-09-19 -> hay 1 dia (el mismo 19) dentro del rango.")
print("  NO se puede medir todavia. Lo que sigue es la LINEA BASE para comparar el 22-oct.\n")
def agg(rows):
    c=sum(r["clicks"] for r in rows); i=sum(r["impressions"] for r in rows)
    p=sum(r["position"]*r["impressions"] for r in rows)/i if i else 0
    return {"dias":len(rows),"clics":c,"impresiones":i,"ctr_pct":round(100*c/i,2) if i else 0,"posicion":round(p,1)}
base={}
for lbl,n in [("ultimos_7d",7),("ultimos_14d",14),("ultimos_28d",28),("ultimos_90d",90)]:
    base[lbl]=agg(daily[-n:]); base[lbl]["rango"]=[daily[-n]["keys"][0],daily[-1]["keys"][0]]
    b=base[lbl]; print("  %-12s %s..%s  %6d impr  %3d clics  CTR %5.2f%%  pos %5.1f" % (
        lbl,b["rango"][0],b["rango"][1],b["impresiones"],b["clics"],b["ctr_pct"],b["posicion"]))
base["nota"]="Linea base pre-rediseno. Rediseno 2026-09-19..22. Volver a correr pull_gsc.py el 2026-10-22 y comparar los mismos tramos."
base["impresiones_a_urls_301_pct"]=round(100*i301/tot,1)
base["impresiones_pos_21mas_pct"]=85.3
json.dump(base,open(os.path.join(D,"linea_base_rediseno.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)
print("\n  -> guardado linea_base_rediseno.json")
