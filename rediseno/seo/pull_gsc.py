# -*- coding: utf-8 -*-
"""Extractor GSC completo para PYS. Corre con: railway run python pull_gsc.py
NO imprime credenciales."""
import os, json, sys, time
from datetime import datetime, timedelta, date
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

OUT = os.path.dirname(os.path.abspath(__file__))

CID = os.environ.get("GOOGLE_CLIENT_ID", "")
CS  = os.environ.get("GOOGLE_CLIENT_SECRET", "")
RT  = os.environ.get("GOOGLE_REFRESH_TOKEN", "")
SITE_ENV = os.environ.get("GSC_SITE_URL", "sc-domain:peptidosysuplementos.mx")
print("env: client_id=%s client_secret=%s refresh_token=%s site=%s" % (
    bool(CID), bool(CS), bool(RT), SITE_ENV))

creds = Credentials(token=None, refresh_token=RT, client_id=CID, client_secret=CS,
                    token_uri="https://oauth2.googleapis.com/token",
                    scopes=["https://www.googleapis.com/auth/webmasters.readonly"])
svc = build("searchconsole", "v1", credentials=creds, cache_discovery=False)

sites = svc.sites().list().execute()
print("SITIOS DISPONIBLES:")
for s in sites.get("siteEntry", []):
    print("  ", s.get("siteUrl"), "->", s.get("permissionLevel"))
json.dump(sites, open(os.path.join(OUT, "gsc_sites.json"), "w"), indent=1)

# elegir la propiedad de PREFIJO si existe
avail = [s["siteUrl"] for s in sites.get("siteEntry", [])]
SITE = None
for pref in ["https://peptidosysuplementos.mx/", "sc-domain:peptidosysuplementos.mx",
             "https://www.peptidosysuplementos.mx/"]:
    if pref in avail:
        SITE = pref; break
if SITE is None:
    SITE = SITE_ENV
print("USANDO PROPIEDAD:", SITE)

def q(start, end, dims, limit=25000, dtype=None, filters=None):
    rows, startRow = [], 0
    while True:
        body = {"startDate": start, "endDate": end, "dimensions": dims,
                "rowLimit": min(limit, 25000), "startRow": startRow}
        if dtype: body["type"] = dtype
        if filters: body["dimensionFilterGroups"] = filters
        r = svc.searchanalytics().query(siteUrl=SITE, body=body).execute()
        got = r.get("rows", [])
        rows.extend(got)
        if len(got) < 25000 or len(rows) >= limit: break
        startRow += 25000
        time.sleep(0.4)
    return rows

def save(name, obj):
    p = os.path.join(OUT, name)
    json.dump(obj, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("  guardado %s (%d filas)" % (name, len(obj) if isinstance(obj, list) else -1))

today = date.today()
# GSC tiene ~2-3 dias de retraso
end_cur   = today - timedelta(days=3)
start_cur = end_cur - timedelta(days=89)          # 90 dias
end_prev  = start_cur - timedelta(days=1)
start_prev= end_prev - timedelta(days=89)         # 90 dias anteriores
F = "%Y-%m-%d"
meta = {"site": SITE, "generated": datetime.now().isoformat(),
        "cur": [start_cur.strftime(F), end_cur.strftime(F)],
        "prev": [start_prev.strftime(F), end_prev.strftime(F)]}
print("RANGOS:", meta["cur"], "vs", meta["prev"])
save("gsc_meta.json", meta)

jobs = [
 ("gsc_daily_365.json", (( today - timedelta(days=400)).strftime(F), end_cur.strftime(F), ["date"])),
 ("gsc_cur_query.json", (start_cur.strftime(F), end_cur.strftime(F), ["query"])),
 ("gsc_cur_page.json",  (start_cur.strftime(F), end_cur.strftime(F), ["page"])),
 ("gsc_cur_query_page.json", (start_cur.strftime(F), end_cur.strftime(F), ["query","page"])),
 ("gsc_cur_country_device.json", (start_cur.strftime(F), end_cur.strftime(F), ["country","device"])),
 ("gsc_prev_query.json", (start_prev.strftime(F), end_prev.strftime(F), ["query"])),
 ("gsc_prev_page.json",  (start_prev.strftime(F), end_prev.strftime(F), ["page"])),
 ("gsc_cur_page_date.json", (start_cur.strftime(F), end_cur.strftime(F), ["page","date"])),
]
for name, (s, e, d) in jobs:
    try:
        save(name, q(s, e, d))
    except Exception as ex:
        print("  ERROR %s: %s" % (name, str(ex)[:300]))

# totales por periodo (sin dimensiones)
tot = {}
for label, (s, e) in [("cur", (start_cur.strftime(F), end_cur.strftime(F))),
                      ("prev", (start_prev.strftime(F), end_prev.strftime(F)))]:
    try:
        r = svc.searchanalytics().query(siteUrl=SITE, body={
            "startDate": s, "endDate": e, "dimensions": []}).execute()
        tot[label] = {"range": [s, e], "rows": r.get("rows", [])}
    except Exception as ex:
        tot[label] = {"error": str(ex)[:300]}
save("gsc_totals.json", tot)
print("LISTO")
