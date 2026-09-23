# -*- coding: utf-8 -*-
import re, json, sys, io
sys.stdout.reconfigure(encoding='utf-8')

def load(p):
    return open(p, encoding='utf-8').read()

def ldjson(h):
    out=[]
    for m in re.findall(r'<script[^>]*ld\+json[^>]*>(.*?)</script>', h, re.S):
        try: out.append(json.loads(m))
        except Exception as e: out.append({'PARSE_ERROR':str(e),'raw':m[:500]})
    return out

def graph_types(h):
    rows=[]
    for blk in ldjson(h):
        g = blk.get('@graph', [blk]) if isinstance(blk,dict) else blk
        for n in g:
            t=n.get('@type')
            rows.append((t, sorted(n.keys())))
    return rows

def headings(h):
    # strip script/style
    b = re.sub(r'<(script|style)[^>]*>.*?</\1>','',h,flags=re.S)
    out=[]
    for m in re.finditer(r'<(h[1-4])\b[^>]*>(.*?)</\1>', b, re.S|re.I):
        txt = re.sub(r'<[^>]+>','',m.group(2))
        txt = re.sub(r'\s+',' ',txt).strip()
        if txt: out.append((m.group(1).lower(), txt))
    return out

def text(h):
    b = re.sub(r'<(script|style|noscript)[^>]*>.*?</\1>','',h,flags=re.S)
    b = re.sub(r'<[^>]+>',' ',b)
    import html as H
    b = H.unescape(b)
    return re.sub(r'[ \t]+',' ',b)

def links(h):
    out=[]
    for m in re.finditer(r'<a\b([^>]*)>(.*?)</a>', h, re.S|re.I):
        attrs=m.group(1); t=re.sub(r'<[^>]+>','',m.group(2)); t=re.sub(r'\s+',' ',t).strip()
        hm=re.search(r'href="([^"]*)"',attrs)
        if hm: out.append((hm.group(1), t))
    return out
