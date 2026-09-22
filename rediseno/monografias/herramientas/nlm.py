#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cliente minimo de NCBI E-utilities + PubChem PUG REST.
Todo lo que baja se cachea en ./pubmed/ para no repetir peticiones."""
import json, os, re, sys, time, urllib.parse, urllib.request, io, hashlib, html as _html

try: sys.stdout.reconfigure(encoding='utf-8')
except Exception: pass
BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pubmed')
os.makedirs(BASE, exist_ok=True)
EUT = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'
PUG = 'https://pubchem.ncbi.nlm.nih.gov/rest/pug/'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) monografias-pys/1.0'
_last = [0.0]


def _get(url, tries=3):
    for i in range(tries):
        gap = time.time() - _last[0]
        if gap < 0.40:
            time.sleep(0.40 - gap)
        _last[0] = time.time()
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read().decode('utf-8', 'replace')
        except Exception as e:
            if i == tries - 1:
                return 'ERROR: %s' % e
            time.sleep(1.5 * (i + 1))


def cached(key, url):
    safe = re.sub(r'[^A-Za-z0-9._-]', '_', key)
    if len(safe) > 90:
        safe = safe[:60] + '_' + hashlib.md5(key.encode('utf-8')).hexdigest()[:10] + '.json'
    p = os.path.join(BASE, safe)
    if os.path.exists(p) and os.path.getsize(p) > 0:
        return open(p, encoding='utf-8').read()
    t = _get(url)
    open(p, 'w', encoding='utf-8').write(t)
    return t


def esearch(term, retmax=30):
    u = EUT + 'esearch.fcgi?db=pubmed&retmode=json&retmax=%d&term=%s' % (
        retmax, urllib.parse.quote(term))
    t = cached('esearch_%s_%d.json' % (term, retmax), u)
    try:
        d = json.loads(t)['esearchresult']
        return int(d.get('count', 0)), d.get('idlist', [])
    except Exception:
        return -1, []


def efetch(pmids):
    """Devuelve dict pmid -> {title, journal, year, authors, abstract, ptypes}"""
    pmids = [str(p) for p in pmids]
    out = {}
    for i in range(0, len(pmids), 20):
        chunk = pmids[i:i + 20]
        u = EUT + 'efetch.fcgi?db=pubmed&retmode=xml&rettype=abstract&id=' + ','.join(chunk)
        t = cached('efetch_%s.xml' % '_'.join(chunk), u)
        for art in re.split(r'(?=<PubmedArticle>)', t):
            m = re.search(r'<PMID[^>]*>(\d+)</PMID>', art)
            if not m:
                continue
            pmid = m.group(1)
            if pmid not in chunk:
                continue

            def tag(pat, s=art):
                mm = re.search(pat, s, re.S)
                return strip(mm.group(1)) if mm else ''

            title = tag(r'<ArticleTitle[^>]*>(.*?)</ArticleTitle>')
            journal = tag(r'<Title>(.*?)</Title>') or tag(r'<ISOAbbreviation>(.*?)</ISOAbbreviation>')
            year = tag(r'<PubDate>.*?<Year>(\d{4})</Year>') or tag(r'<ArticleDate[^>]*>\s*<Year>(\d{4})</Year>')
            au = []
            for a in re.finditer(r'<Author[^>]*>(.*?)</Author>', art, re.S):
                ln = re.search(r'<LastName>(.*?)</LastName>', a.group(1))
                ini = re.search(r'<Initials>(.*?)</Initials>', a.group(1))
                if ln:
                    au.append(strip(ln.group(1)) + (' ' + strip(ini.group(1)) if ini else ''))
            abst = []
            for a in re.finditer(r'<AbstractText([^>]*)>(.*?)</AbstractText>', art, re.S):
                lb = re.search(r'Label="([^"]*)"', a.group(1))
                abst.append((lb.group(1) + ': ' if lb else '') + strip(a.group(2)))
            pt = [strip(x) for x in re.findall(r'<PublicationType[^>]*>(.*?)</PublicationType>', art)]
            out[pmid] = {'pmid': pmid, 'titulo': title, 'revista': journal, 'anio': year,
                         'autores': au, 'abstract': '\n'.join(abst), 'tipos': pt}
    return out


def strip(s):
    # OJO: primero se quitan las etiquetas, luego se desescapan TODAS las
    # entidades con html.unescape. Una lista manual perdia &#xb5; (micro) y
    # convertia 10 ug/kg en 10 g/kg. Nunca volver a la lista manual.
    s = re.sub(r'<[^>]+>', ' ', s)
    s = _html.unescape(s)
    return re.sub(r'[ 	]+', ' ', s).strip()


def pubchem(name):
    """name -> {cid, formula, mw, iupac, smiles, cas, sinonimos}"""
    q = urllib.parse.quote(name)
    props = 'MolecularFormula,MolecularWeight,IUPACName,CanonicalSMILES,InChIKey'
    t = cached('pc_prop_%s.json' % name,
               PUG + 'compound/name/%s/property/%s/JSON' % (q, props))
    try:
        p = json.loads(t)['PropertyTable']['Properties'][0]
    except Exception:
        return {'error': t[:200], 'consulta': name}
    cid = p['CID']
    ts = cached('pc_syn_%s.json' % name, PUG + 'compound/cid/%d/synonyms/JSON' % cid)
    syn = []
    try:
        syn = json.loads(ts)['InformationList']['Information'][0]['Synonym']
    except Exception:
        pass
    cas = [s for s in syn if re.fullmatch(r'\d{2,7}-\d{2}-\d', s)]
    return {'consulta': name, 'cid': cid, 'formula': p.get('MolecularFormula'),
            'peso_molecular': p.get('MolecularWeight'), 'iupac': p.get('IUPACName'),
            'inchikey': p.get('InChIKey'), 'cas_candidatos': cas[:6],
            'sinonimos': [s for s in syn if not re.fullmatch(r'\d{2,7}-\d{2}-\d', s)][:30]}


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'search':
        n, ids = esearch(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 30)
        print('COUNT=%d' % n)
        print(' '.join(ids))
    elif cmd == 'fetch':
        d = efetch(sys.argv[2:])
        for pmid, a in d.items():
            print('=' * 70)
            print('PMID %s | %s | %s | %s' % (pmid, a['anio'], a['revista'], '/'.join(a['tipos'][:3])))
            print('AUT: %s' % ', '.join(a['autores'][:4]))
            print('TIT: %s' % a['titulo'])
            print('ABS: %s' % a['abstract'])
    elif cmd == 'pc':
        for n in sys.argv[2:]:
            print(json.dumps(pubchem(n), ensure_ascii=False, indent=1))
