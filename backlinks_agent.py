"""
backlinks_agent.py — Prospector de backlinks SEO off-page (calidad > cantidad)
=============================================================================

Agente independiente para descubrir, CALIFICAR y RECOMENDAR oportunidades de
backlinks de alta calidad para tres sitios, y AUDITAR el perfil de enlaces
existente para detectar toxicidad — sin generar spam que penalice rankings.

Sitios objetivo:
  - raditech    → raditech.mx           (B2B teleradiología / imagen médica)
  - grupoptm    → grupoptm.com / PTM Novo (telemedicina de péptidos)
  - pys         → peptidosysuplementos.mx (ecommerce péptidos/suplementos, YMYL)

PRINCIPIO RECTOR: calidad sobre cantidad. El agente NO envía correos, NO publica
en ningún lado y NO sube archivos disavow. Solo investiga, califica, recomienda y
GENERA BORRADORES que tú apruebas manualmente. Es seguro por diseño: no tiene
ninguna herramienta capaz de ejecutar acciones de link-building automáticas.

Uso:
    python backlinks_agent.py

Variables de entorno requeridas:
    ANTHROPIC_API_KEY   — para Claude (tool use + web search)
Opcionales:
    BACKLINKS_MODEL     — modelo Claude (default claude-sonnet-4-6;
                          usa claude-opus-4-8 para estrategia más profunda)
"""

import os
import re
import sys
import csv
import json
import io
from datetime import datetime
from urllib.parse import urlparse

import requests
import anthropic
from dotenv import load_dotenv

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

load_dotenv()

# ─── Directorio de datos persistentes ────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "backlinks_data")
os.makedirs(DATA_DIR, exist_ok=True)

# ─── Perfiles de los tres sitios ─────────────────────────────────────────────
# geo_weight_es: cuánto pesa la relevancia idioma/geo español-México para el sitio
SITES = {
    "raditech": {
        "domain": "raditech.mx",
        "name": "Raditech",
        "tipo": "B2B — teleradiología, sistemas PACS-RIS, monitores grado médico",
        "audiencia": "hospitales, clínicas, radiólogos, directores médicos, compras hospitalarias (México y LATAM)",
        "idioma_geo": "Español (México/LATAM). Inglés aceptable para directorios médicos internacionales serios.",
    },
    "grupoptm": {
        "domain": "grupoptm.com",
        "name": "PTM Novo (Grupo PTM)",
        "tipo": "Telemedicina de péptidos / salud hormonal (YMYL médico)",
        "audiencia": "pacientes que buscan telemedicina de péptidos y salud hormonal en México",
        "idioma_geo": "Español (México). Citaciones locales y directorios médicos en español.",
    },
    "pys": {
        "domain": "peptidosysuplementos.mx",
        "name": "Péptidos y Suplementos (PYS)",
        "tipo": "Ecommerce de péptidos y suplementos (YMYL, nicho sensible/restringido)",
        "audiencia": "consumidores de fitness, biohacking, longevidad y rendimiento en México",
        "idioma_geo": "Español (México). Medios de fitness/biohacking en español.",
    },
}

# ─── Reglas de marca prohibidas (memoria del usuario) ────────────────────────
FORBIDDEN_PATTERNS = [
    (re.compile(r"farmacia", re.IGNORECASE), '"farmacia" (usa "Tienda en línea")'),
    (re.compile(r"refrigeraci[oó]n adecuada para garantizar", re.IGNORECASE),
     'frase de refrigeración en transporte'),
]


def check_forbidden(text):
    """Devuelve lista de reglas de marca violadas en un texto (para revisar borradores de outreach)."""
    hits = []
    for pat, label in FORBIDDEN_PATTERNS:
        if pat.search(text or ""):
            hits.append(label)
    return hits


# ══════════════════════════════════════════════════════════════════════════════
#  HERRAMIENTAS (client tools que ejecuta este script)
# ══════════════════════════════════════════════════════════════════════════════

def fetch_url(url):
    """Descarga y analiza una página candidata: title, meta, headings, señales de spam básicas."""
    if not BS4_AVAILABLE:
        return {"error": "beautifulsoup4 no instalado — ejecuta: pip install beautifulsoup4"}
    try:
        r = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0 (compatible; BacklinkProspector/1.0)"})
        status = r.status_code
        soup = BeautifulSoup(r.text, "html.parser")

        title = soup.title.string.strip() if soup.title and soup.title.string else ""
        meta_desc = ""
        mt = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", attrs={"property": "og:description"})
        if mt:
            meta_desc = (mt.get("content") or "").strip()

        h1s = [h.get_text(strip=True) for h in soup.find_all("h1")][:5]
        h2s = [h.get_text(strip=True) for h in soup.find_all("h2")][:10]

        # Señales de spam / calidad sobre enlaces salientes
        links = soup.find_all("a", href=True)
        ext_domains = set()
        spam_anchor_hits = 0
        SPAM_TERMS = re.compile(
            r"\b(casino|poker|bet|viagra|cialis|porn|sex|loan|payday|crypto pump|escort|replica|seo backlinks|buy links)\b",
            re.IGNORECASE,
        )
        host = urlparse(url).netloc.lower()
        for a in links:
            href = a["href"]
            d = urlparse(href).netloc.lower()
            if d and host and d not in host and host not in d:
                ext_domains.add(d)
            if SPAM_TERMS.search(a.get_text() or "") or SPAM_TERMS.search(href):
                spam_anchor_hits += 1

        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        text = soup.get_text(separator=" ", strip=True)
        word_count = len(text.split())

        return {
            "url": url,
            "status_code": status,
            "title": title,
            "meta_description": meta_desc,
            "h1": h1s,
            "h2s": h2s,
            "word_count": word_count,
            "content_preview": text[:600],
            "outbound_external_domains": len(ext_domains),
            "spam_anchor_hits": spam_anchor_hits,
            "quality_hint": (
                "ALTA sospecha de spam" if spam_anchor_hits >= 3 or len(ext_domains) > 120
                else "Sin señales obvias de spam"
            ),
        }
    except requests.RequestException as e:
        return {"error": str(e), "url": url}


# ── Scoring determinista de prospectos ───────────────────────────────────────
# Dimensiones máximas (la suma positiva da 90; -spam puede restar hasta 40).
DIM_MAX = {
    "topical_relevance": 30,   # ¿qué tan relacionado está el sitio con el nicho objetivo?
    "authority_quality": 25,   # dominio establecido, tráfico real, indexado, editorial real
    "editorial_standard": 15,  # contenido de calidad, no granja de enlaces, audiencia real
    "link_context": 10,        # enlace editorial contextual vs footer/sidebar/directorio masivo
    "geo_language_fit": 10,    # ajuste idioma/geo (español/México según el sitio)
}
# Flags que descalifican de inmediato (verdict = REJECT sin importar el puntaje)
HARD_REJECT_FLAGS = {
    "sells_links", "pbn", "deindexed", "malware", "cloaking",
    "irrelevant_niche", "link_farm", "adult_gambling_pharma_spam", "scraped_content",
}
SOFT_PENALTY_PER_FLAG = 10
SOFT_PENALTY_CAP = 40


def score_prospect(target_site, prospect_domain,
                   topical_relevance, authority_quality, editorial_standard,
                   link_context, geo_language_fit, spam_flags=None,
                   evidence="", contact_path="", suggested_tactic=""):
    """
    Calcula un puntaje 0-100 y un veredicto (PURSUE / REVIEW / REJECT) a partir de
    sub-puntajes que el agente asigna tras investigar. Determinista y auditable:
    el mismo input siempre da el mismo veredicto.
    """
    if target_site not in SITES:
        return {"error": f"target_site inválido: {target_site}. Usa: {list(SITES)}"}

    spam_flags = spam_flags or []
    # Clamp de cada dimensión a su máximo
    dims = {
        "topical_relevance": max(0, min(int(topical_relevance), DIM_MAX["topical_relevance"])),
        "authority_quality": max(0, min(int(authority_quality), DIM_MAX["authority_quality"])),
        "editorial_standard": max(0, min(int(editorial_standard), DIM_MAX["editorial_standard"])),
        "link_context": max(0, min(int(link_context), DIM_MAX["link_context"])),
        "geo_language_fit": max(0, min(int(geo_language_fit), DIM_MAX["geo_language_fit"])),
    }
    positive = sum(dims.values())

    hard = sorted(set(spam_flags) & HARD_REJECT_FLAGS)
    soft = [f for f in spam_flags if f not in HARD_REJECT_FLAGS]
    penalty = min(len(soft) * SOFT_PENALTY_PER_FLAG, SOFT_PENALTY_CAP)

    score = max(0, min(100, positive - penalty))

    if hard:
        verdict = "REJECT"
        reason = f"Descalificado por flag(s) crítico(s): {', '.join(hard)}"
    elif score >= 70:
        verdict = "PURSUE"
        reason = "Oportunidad de calidad — perseguir con outreach personalizado."
    elif score >= 45:
        verdict = "REVIEW"
        reason = "Dudoso — requiere revisión humana antes de invertir esfuerzo."
    else:
        verdict = "REJECT"
        reason = "Puntaje bajo — no vale el riesgo/esfuerzo."

    return {
        "target_site": target_site,
        "prospect_domain": prospect_domain,
        "score": score,
        "verdict": verdict,
        "reason": reason,
        "breakdown": dims,
        "soft_penalty": penalty,
        "hard_reject_flags": hard,
        "soft_flags": soft,
        "evidence": evidence,
        "contact_path": contact_path,
        "suggested_tactic": suggested_tactic,
    }


# ── Persistencia de prospectos ───────────────────────────────────────────────
def _prospects_path(site):
    return os.path.join(DATA_DIR, f"prospects_{site}.json")


def _load_prospects(site):
    p = _prospects_path(site)
    if os.path.isfile(p):
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def _save_prospects(site, items):
    with open(_prospects_path(site), "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)


VALID_STATUS = ["new", "qualified", "contacted", "negotiating", "won", "rejected", "lost"]


def save_prospect(target_site, prospect_domain, score=None, verdict=None,
                  status=None, contact_path=None, suggested_tactic=None,
                  notes=None, evidence=None):
    """
    Guarda/actualiza un prospecto (deduplica por dominio). Semántica de MERGE: en una
    actualización, los campos NO provistos conservan su valor previo (no se pisan con defaults).
    """
    if target_site not in SITES:
        return {"error": f"target_site inválido: {target_site}"}
    if status is not None and status not in VALID_STATUS:
        return {"error": f"status inválido: {status}. Usa: {VALID_STATUS}"}

    dom = (prospect_domain or "").lower().strip().replace("https://", "").replace("http://", "").rstrip("/")
    items = _load_prospects(target_site)
    now = datetime.now().strftime("%Y-%m-%d")
    existing = next((x for x in items if x.get("prospect_domain") == dom), None)
    base = dict(existing) if existing else {
        "prospect_domain": dom, "score": None, "verdict": None, "status": "qualified",
        "contact_path": "", "suggested_tactic": "", "notes": "", "evidence": "", "created": now,
    }
    provided = {"score": score, "verdict": verdict, "status": status, "contact_path": contact_path,
                "suggested_tactic": suggested_tactic, "notes": notes, "evidence": evidence}
    for k, v in provided.items():
        if v is not None:
            base[k] = v
    base["prospect_domain"] = dom
    base["updated"] = now
    if existing:
        items = [base if x.get("prospect_domain") == dom else x for x in items]
        action = "updated"
    else:
        items.append(base)
        action = "created"
    _save_prospects(target_site, items)
    return {"action": action, "prospect": base, "total_prospects": len(items)}


def list_prospects(target_site, status=None):
    """Lista prospectos guardados de un sitio, opcionalmente filtrando por status."""
    if target_site not in SITES:
        return {"error": f"target_site inválido: {target_site}"}
    items = _load_prospects(target_site)
    if status:
        items = [x for x in items if x.get("status") == status]
    items = sorted(items, key=lambda x: (x.get("score") or 0), reverse=True)
    by_status = {}
    for x in _load_prospects(target_site):
        by_status[x.get("status", "?")] = by_status.get(x.get("status", "?"), 0) + 1
    return {"target_site": target_site, "count": len(items), "by_status": by_status, "prospects": items}


# ── Planificador de activos linkables (link earning, no link chasing) ─────────
# Un "activo linkable" es un recurso que GANA enlaces solo (datos originales, guías
# profundas, herramientas, estudios). Se puntúa para evitar disfrazar blogs genéricos
# de activos: si no atrae enlaces por sí mismo, no es un activo linkable.
ASSET_DIM_MAX = {
    "link_attractiveness": 30,   # ¿qué tan natural es que otros lo citen/enlacen?
    "uniqueness": 25,            # ¿datos/ángulo originales o solo refrito de lo existente?
    "pr_hook": 20,              # ¿hay gancho noticiable que a un periodista le importe?
    "evergreen_value": 10,      # ¿valor duradero vs interés de un solo día?
    "production_feasibility": 15,  # ¿es realista producirlo? (mayor = más fácil)
}
VALID_ASSET_STATUS = ["idea", "briefed", "in_production", "published", "promoting", "earned", "shelved"]


def score_asset_idea(target_site, title, link_attractiveness, uniqueness, pr_hook,
                     evergreen_value, production_feasibility, asset_type="",
                     rationale="", link_targets=None):
    """
    Puntúa 0-100 una idea de activo linkable y da veredicto (BUILD/CONSIDER/SKIP).
    Determinista: el mismo input da el mismo veredicto. Sirve para filtrar ideas que
    en realidad no ganarían enlaces (link_attractiveness/uniqueness bajos = solo es 'contenido').
    """
    if target_site not in SITES:
        return {"error": f"target_site inválido: {target_site}. Usa: {list(SITES)}"}
    dims = {
        "link_attractiveness": max(0, min(int(link_attractiveness), ASSET_DIM_MAX["link_attractiveness"])),
        "uniqueness": max(0, min(int(uniqueness), ASSET_DIM_MAX["uniqueness"])),
        "pr_hook": max(0, min(int(pr_hook), ASSET_DIM_MAX["pr_hook"])),
        "evergreen_value": max(0, min(int(evergreen_value), ASSET_DIM_MAX["evergreen_value"])),
        "production_feasibility": max(0, min(int(production_feasibility), ASSET_DIM_MAX["production_feasibility"])),
    }
    score = sum(dims.values())
    # Guardia: si nadie lo enlazaría de forma natural, no es un activo linkable aunque el total suba.
    if dims["link_attractiveness"] < 12 or dims["uniqueness"] < 8:
        verdict = "SKIP"
        reason = "No gana enlaces por sí mismo (poca atracción/originalidad): es contenido normal, no un activo linkable."
    elif score >= 70:
        verdict = "BUILD"
        reason = "Activo linkable de alto potencial — vale la pena producirlo y hacer digital PR."
    elif score >= 45:
        verdict = "CONSIDER"
        reason = "Potencial medio — afínalo (más datos originales o mejor gancho de PR) antes de invertir."
    else:
        verdict = "SKIP"
        reason = "Bajo potencial de ganar enlaces — no priorizar."
    return {
        "target_site": target_site,
        "title": title,
        "asset_type": asset_type,
        "score": score,
        "verdict": verdict,
        "reason": reason,
        "breakdown": dims,
        "rationale": rationale,
        "link_targets": link_targets or [],
    }


def _assets_path(site):
    return os.path.join(DATA_DIR, f"assets_{site}.json")


def _load_assets(site):
    p = _assets_path(site)
    if os.path.isfile(p):
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_asset_idea(target_site, title, asset_type=None, score=None, verdict=None,
                    status=None, pr_hook=None, link_targets=None, brief=None,
                    links_earned=None, notes=None):
    """
    Guarda/actualiza una idea de activo linkable (deduplica por título). Semántica de MERGE:
    en una actualización, los campos NO provistos conservan su valor previo (no se pisan con defaults).
    """
    if target_site not in SITES:
        return {"error": f"target_site inválido: {target_site}"}
    if status is not None and status not in VALID_ASSET_STATUS:
        return {"error": f"status inválido: {status}. Usa: {VALID_ASSET_STATUS}"}
    items = _load_assets(target_site)
    now = datetime.now().strftime("%Y-%m-%d")
    key = (title or "").strip().lower()
    existing = next((x for x in items if (x.get("title") or "").strip().lower() == key), None)
    base = dict(existing) if existing else {
        "title": title, "asset_type": "", "score": None, "verdict": None,
        "status": "idea", "pr_hook": "", "link_targets": [], "brief": "",
        "links_earned": 0, "notes": "", "created": now,
    }
    provided = {"asset_type": asset_type, "score": score, "verdict": verdict, "status": status,
                "pr_hook": pr_hook, "link_targets": link_targets, "brief": brief,
                "links_earned": links_earned, "notes": notes}
    for k, v in provided.items():
        if v is not None:
            base[k] = v
    base["title"] = title
    base["updated"] = now
    if existing:
        items = [base if (x.get("title") or "").strip().lower() == key else x for x in items]
        action = "updated"
    else:
        items.append(base)
        action = "created"
    with open(_assets_path(target_site), "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    return {"action": action, "asset": base, "total_assets": len(items)}


def list_asset_ideas(target_site, status=None):
    """Lista el plan de activos linkables de un sitio (resumen por status)."""
    if target_site not in SITES:
        return {"error": f"target_site inválido: {target_site}"}
    items = _load_assets(target_site)
    by_status = {}
    for x in items:
        by_status[x.get("status", "?")] = by_status.get(x.get("status", "?"), 0) + 1
    if status:
        items = [x for x in items if x.get("status") == status]
    items = sorted(items, key=lambda x: (x.get("score") or 0), reverse=True)
    return {"target_site": target_site, "count": len(items), "by_status": by_status, "assets": items}


# ── Auditoría de backlinks existentes (defensa anti-penalización) ─────────────
TOXIC_TLD = re.compile(r"\.(xyz|top|loan|click|gq|cf|tk|ml|ga|work|bid|stream|download|review)$", re.IGNORECASE)
TOXIC_TOKENS = re.compile(
    r"(casino|porn|sex|viagra|cialis|payday|loan|escort|replica|gambling|bet365|seo-?backlink|buy-?link|link-?farm|guest-?post-?service)",
    re.IGNORECASE,
)


def _parse_backlink_csv(csv_text):
    """Parser flexible: detecta columnas de dominio/url origen, anchor y destino."""
    reader = csv.DictReader(io.StringIO(csv_text))
    rows = []
    for raw in reader:
        low = {(k or "").strip().lower(): (v or "").strip() for k, v in raw.items()}
        source = (low.get("source url") or low.get("source_url") or low.get("url from") or
                  low.get("referring page url") or low.get("from") or low.get("source") or
                  low.get("url") or low.get("domain") or low.get("referring domain") or "")
        anchor = (low.get("anchor") or low.get("anchor text") or low.get("anchor_text") or "")
        target = (low.get("target url") or low.get("target_url") or low.get("url to") or
                  low.get("to") or low.get("target") or low.get("destination") or "")
        if source:
            rows.append({"source": source, "anchor": anchor, "target": target})
    return rows


def _norm_domain(s):
    """Normaliza una url/dominio a su host base (sin esquema, puerto ni www.)."""
    s = (s or "").strip().lower()
    if not s:
        return ""
    if "//" not in s:
        s = "http://" + s
    net = urlparse(s).netloc.split(":")[0]
    if net.startswith("www."):
        net = net[4:]
    return net


def audit_backlinks(target_site, csv_text):
    """
    Audita un CSV de backlinks (exportado de GSC/Ahrefs/Ubersuggest/etc.) y marca
    enlaces tóxicos por patrón. NO sube nada; solo reporta y prepara el insumo para disavow.
    """
    if target_site not in SITES:
        return {"error": f"target_site inválido: {target_site}"}
    rows = _parse_backlink_csv(csv_text)
    if not rows:
        return {"error": "No se detectaron filas/columnas válidas en el CSV. Columnas esperadas: source/url, anchor, target."}

    # Distribución de anchors para detectar sobre-optimización (exact-match a escala)
    anchor_counts = {}
    for r in rows:
        a = r["anchor"].lower().strip()
        if a:
            anchor_counts[a] = anchor_counts.get(a, 0) + 1
    total_anchored = sum(anchor_counts.values()) or 1
    over_optimized = {a: c for a, c in anchor_counts.items()
                      if c / total_anchored > 0.15 and len(a.split()) >= 2 and c >= 5}

    flagged = []
    domains_seen = {}
    for r in rows:
        dom = urlparse(r["source"] if "//" in r["source"] else "http://" + r["source"]).netloc.lower() or r["source"].lower()
        domains_seen[dom] = domains_seen.get(dom, 0) + 1
        reasons = []
        if TOXIC_TLD.search(dom):
            reasons.append("TLD de alto spam")
        if TOXIC_TOKENS.search(dom) or TOXIC_TOKENS.search(r["anchor"]):
            reasons.append("token de spam en dominio/anchor")
        if r["anchor"].lower() in over_optimized:
            reasons.append("anchor exact-match sobre-optimizado a escala")
        if reasons:
            flagged.append({"source": r["source"], "domain": dom, "anchor": r["anchor"],
                            "target": r["target"], "reasons": reasons})

    # Dominios con cantidad anómala de enlaces (posible sitewide footer / PBN)
    sitewide = {d: c for d, c in domains_seen.items() if c >= 20}

    return {
        "target_site": target_site,
        "total_backlinks": len(rows),
        "unique_domains": len(domains_seen),
        "flagged_count": len(flagged),
        "flagged": flagged[:200],
        "over_optimized_anchors": over_optimized,
        "possible_sitewide_or_pbn": sitewide,
        "note": (
            "REVISIÓN HUMANA OBLIGATORIA. Esto marca SOSPECHAS por patrón, no certezas. "
            "Google recomienda NO usar disavow salvo penalización manual o spam masivo evidente. "
            "Verifica manualmente cada dominio (fetch_url) antes de considerar disavow."
        ),
    }


def generate_disavow_draft(target_site, domains):
    """
    Genera un BORRADOR de archivo disavow.txt para los dominios confirmados como tóxicos.
    NUNCA lo sube a Google. Lo escribe a disco para revisión y carga manual del usuario.
    """
    if target_site not in SITES:
        return {"error": f"target_site inválido: {target_site}"}
    if not domains:
        return {"error": "Lista de dominios vacía. Provee solo dominios YA confirmados como tóxicos."}

    clean = []
    for d in domains:
        d = (d or "").lower().strip().replace("https://", "").replace("http://", "").rstrip("/")
        d = d.split("/")[0]
        if d and d not in clean:
            clean.append(d)

    stamp = datetime.now().strftime("%Y-%m-%d")
    header = [
        f"# Disavow BORRADOR — {SITES[target_site]['domain']} — {stamp}",
        "# REVISA CADA LÍNEA ANTES DE SUBIR A Google Search Console > Disavow links.",
        "# Subir disavow incorrecto DAÑA rankings. Solo usar ante spam masivo o penalización manual.",
        "",
    ]
    body = [f"domain:{d}" for d in clean]
    content = "\n".join(header + body) + "\n"
    path = os.path.join(DATA_DIR, f"disavow_{target_site}_{stamp}.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return {
        "target_site": target_site,
        "domains_count": len(clean),
        "file": path,
        "preview": content[:800],
        "warning": "BORRADOR. No subido. Revisa manualmente y sube tú mismo solo si estás seguro.",
    }


def link_intersect(target_site, competitor_csvs, own_csv="",
                   min_competitors=1, exclude_spam=True, limit=50):
    """
    Prospección por INTERSECCIÓN: encuentra dominios que enlazan a los competidores
    pero NO a tu sitio. Es la prospección de mayor precisión y cero riesgo — solo
    descubre candidatos; luego cada uno pasa por fetch_url → score_prospect.

    competitor_csvs: lista de CSVs de backlinks de competidores (Ahrefs free, Ubersuggest,
                     Semrush, Moz o el reporte de Enlaces de GSC). Cada elemento puede ser un
                     string (el CSV) o un objeto {name, csv}.
    own_csv:         (opcional) CSV de TUS propios backlinks, para excluir quien ya te enlaza.
    min_competitors: solo devolver dominios que enlazan a >= N competidores (2 = más fuerte).
    """
    if target_site not in SITES:
        return {"error": f"target_site inválido: {target_site}. Usa: {list(SITES)}"}

    if isinstance(competitor_csvs, str):
        competitor_csvs = [competitor_csvs]
    if not competitor_csvs:
        return {"error": "Provee al menos un CSV de backlinks de competidor en competitor_csvs."}

    comps = []
    for i, c in enumerate(competitor_csvs):
        if isinstance(c, dict):
            name = c.get("name") or c.get("competitor") or f"competidor_{i + 1}"
            text = c.get("csv") or c.get("csv_text") or ""
        else:
            name = f"competidor_{i + 1}"
            text = c or ""
        if text.strip():
            comps.append({"name": name, "csv": text})
    if not comps:
        return {"error": "Ningún CSV de competidor con contenido válido."}

    # Dominios que YA te enlazan (a excluir) + tu propio dominio + dominios de competidores
    own_domains = set()
    if own_csv and own_csv.strip():
        for r in _parse_backlink_csv(own_csv):
            d = _norm_domain(r["source"])
            if d:
                own_domains.add(d)
    site_domain = _norm_domain(SITES[target_site]["domain"])
    exclude = set(own_domains) | {site_domain}
    for c in comps:
        cd = _norm_domain(c["name"])
        if cd:
            exclude.add(cd)

    gap = {}
    parse_errors = []
    for comp in comps:
        rows = _parse_backlink_csv(comp["csv"])
        if not rows:
            parse_errors.append(comp["name"])
            continue
        for r in rows:
            d = _norm_domain(r["source"])
            if not d or d in exclude:
                continue
            e = gap.setdefault(d, {
                "domain": d, "competitors": set(),
                "sample_source": r["source"], "sample_anchor": r["anchor"],
                "sample_target": r["target"],
            })
            e["competitors"].add(comp["name"])

    results = []
    for d, e in gap.items():
        cc = len(e["competitors"])
        if cc < min_competitors:
            continue
        spam = []
        if TOXIC_TLD.search(d):
            spam.append("TLD de alto spam")
        if TOXIC_TOKENS.search(d) or TOXIC_TOKENS.search(e["sample_anchor"]):
            spam.append("token de spam")
        if exclude_spam and spam:
            continue
        results.append({
            "domain": d,
            "links_to_competitors": sorted(e["competitors"]),
            "competitor_count": cc,
            "sample_source_url": e["sample_source"],
            "sample_anchor": e["sample_anchor"],
            "sample_target": e["sample_target"],
            "spam_flag": spam,
        })

    # Ordenar por fuerza de intersección (más competidores = prospecto más fuerte)
    results.sort(key=lambda x: x["competitor_count"], reverse=True)
    total_gap = len(results)

    return {
        "target_site": target_site,
        "competitors_analyzed": [c["name"] for c in comps],
        "csv_parse_failures": parse_errors,
        "own_domains_excluded": len(own_domains),
        "gap_domains_found": total_gap,
        "returned": min(total_gap, int(limit)),
        "prospects": results[:int(limit)],
        "next_step": (
            "Para cada dominio prometedor: fetch_url → score_prospect → save_prospect. "
            "Prioriza competitor_count alto (enlaza a varios competidores y no a ti = el mejor prospecto). "
            "Sube min_competitors a 2 para quedarte solo con los más fuertes."
        ),
    }


# ── Monitor anti-SEO-negativo (snapshots + diff de velocidad/toxicidad) ───────
# Como GSC no expone backlinks por API, el monitor compara snapshots de tus exports
# de backlinks en el tiempo. Detecta picos de velocidad, oleadas de dominios tóxicos
# nuevos y anchors spam que aparecen de golpe — señales típicas de SEO negativo.
SNAP_DIR = os.path.join(DATA_DIR, "snapshots")


def _median(xs):
    xs = sorted(xs)
    n = len(xs)
    if n == 0:
        return 0
    m = n // 2
    return xs[m] if n % 2 else (xs[m - 1] + xs[m]) / 2


def _toxic_in_rows(rows):
    """Devuelve (dominios tóxicos, anchors spam) detectados por patrón en filas de backlinks."""
    anchor_counts = {}
    for r in rows:
        a = r["anchor"].lower().strip()
        if a:
            anchor_counts[a] = anchor_counts.get(a, 0) + 1
    total = sum(anchor_counts.values()) or 1
    over = {a for a, c in anchor_counts.items()
            if c / total > 0.15 and len(a.split()) >= 2 and c >= 5}
    toxic_domains, spam_anchors = set(), set()
    for r in rows:
        d = _norm_domain(r["source"])
        if not d:
            continue
        if TOXIC_TLD.search(d) or TOXIC_TOKENS.search(d) or TOXIC_TOKENS.search(r["anchor"]):
            toxic_domains.add(d)
        a = r["anchor"].strip().lower()
        if a and (TOXIC_TOKENS.search(a) or a in over):
            spam_anchors.add(a)
    return toxic_domains, spam_anchors


def _site_snap_dir(site):
    d = os.path.join(SNAP_DIR, site)
    os.makedirs(d, exist_ok=True)
    return d


def _load_latest_snapshot(site):
    d = _site_snap_dir(site)
    files = sorted(f for f in os.listdir(d) if f.startswith("snap_") and f.endswith(".json"))
    if not files:
        return None
    with open(os.path.join(d, files[-1]), encoding="utf-8") as f:
        return json.load(f)


def _monitor_history_path(site):
    return os.path.join(DATA_DIR, f"monitor_history_{site}.json")


def _load_monitor_history(site):
    p = _monitor_history_path(site)
    if os.path.isfile(p):
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    return []


def _append_monitor_history(site, entry):
    h = _load_monitor_history(site)
    h.append(entry)
    with open(_monitor_history_path(site), "w", encoding="utf-8") as f:
        json.dump(h, f, ensure_ascii=False, indent=2)


def _append_monitor_alerts(site, report):
    p = os.path.join(DATA_DIR, f"monitor_alerts_{site}.json")
    a = []
    if os.path.isfile(p):
        with open(p, encoding="utf-8") as f:
            a = json.load(f)
    a.append(report)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(a, f, ensure_ascii=False, indent=2)


def monitor_backlinks(target_site, csv_text, spike_abs=25, spike_mult=3.0, save_snapshot=True):
    """
    Ingiere un export de backlinks como SNAPSHOT y lo compara con el anterior para detectar
    señales de SEO negativo: picos de velocidad de enlaces, dominios tóxicos nuevos y anchors
    spam que aparecen de golpe. NO sube nada. La primera corrida solo fija la línea base.
    """
    if target_site not in SITES:
        return {"error": f"target_site inválido: {target_site}. Usa: {list(SITES)}"}
    rows = _parse_backlink_csv(csv_text)
    if not rows:
        return {"error": "No se detectaron filas/columnas válidas en el CSV."}

    domains = {_norm_domain(r["source"]) for r in rows}
    domains.discard("")
    toxic, spam_anchors = _toxic_in_rows(rows)
    now = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    today = now[:10]
    prev = _load_latest_snapshot(target_site)

    report = {
        "target_site": target_site,
        "date": today,
        "total_referring_domains": len(domains),
        "total_backlinks": len(rows),
        "toxic_domains_now": len(toxic),
        "new_domains": None,
    }
    alerts = []

    if prev is None:
        report["status"] = "baseline"
        report["note"] = ("Primer snapshot guardado como LÍNEA BASE. Corre el monitor de nuevo con un "
                          "export posterior para detectar cambios.")
    else:
        prev_domains = set(prev.get("domains", []))
        prev_toxic = set(prev.get("toxic_domains", []))
        prev_anchors = set(prev.get("spam_anchors", []))
        new_domains = sorted(domains - prev_domains)
        lost_domains = sorted(prev_domains - domains)
        new_toxic = sorted((set(new_domains) & toxic) | (toxic - prev_toxic))
        new_spam_anchors = sorted(spam_anchors - prev_anchors)

        hist = _load_monitor_history(target_site)
        prior_new = [h["new_domains"] for h in hist if h.get("new_domains") is not None]
        baseline = _median(prior_new) if prior_new else 0
        threshold = max(spike_abs, spike_mult * baseline)

        report.update({
            "status": "ok",
            "since": prev.get("date"),
            "new_domains": len(new_domains),
            "lost_domains": len(lost_domains),
            "new_toxic_domains": new_toxic,
            "new_spam_anchors": new_spam_anchors,
            "new_domains_sample": new_domains[:50],
            "velocity_threshold": round(threshold, 1),
        })

        if len(new_domains) > threshold:
            alerts.append({"severity": "high", "type": "velocity_spike",
                           "detail": f"{len(new_domains)} dominios de referencia NUEVOS (umbral {threshold:.0f}). Posible ataque de link velocity."})
        if new_toxic:
            alerts.append({"severity": "high", "type": "toxic_influx",
                           "detail": f"{len(new_toxic)} dominios TÓXICOS nuevos detectados."})
        if new_spam_anchors:
            alerts.append({"severity": "medium", "type": "spam_anchor_influx",
                           "detail": f"{len(new_spam_anchors)} anchors spam/exact-match nuevos (patrón típico de SEO negativo)."})
        if len(lost_domains) > threshold:
            alerts.append({"severity": "medium", "type": "link_loss",
                           "detail": f"{len(lost_domains)} dominios PERDIDOS desde {prev.get('date')}."})

        report["status"] = "alert" if alerts else "ok"
        report["alerts"] = alerts
        report["recommended_action"] = (
            ("ANTE ESTAS ALERTAS: si NO tienes una acción manual en Search Console y tu historial es limpio, "
             "NO hagas disavow — SpamBrain neutraliza solo los enlaces de SEO negativo. Vigila Search Console "
             "> Acciones manuales y el rendimiento. SOLO si aparece una acción manual por enlaces no naturales: "
             "revisa los dominios tóxicos nuevos con fetch_url y, para los confirmados que no puedas remover, "
             "usa generate_disavow_draft.")
            if alerts else
            "Sin anomalías relevantes. Mantén el monitoreo periódico (semanal o quincenal)."
        )

    if save_snapshot:
        snap = {"date": today, "timestamp": now, "domains": sorted(domains),
                "toxic_domains": sorted(toxic), "spam_anchors": sorted(spam_anchors),
                "total_backlinks": len(rows), "total_domains": len(domains)}
        with open(os.path.join(_site_snap_dir(target_site), f"snap_{now}.json"), "w", encoding="utf-8") as f:
            json.dump(snap, f, ensure_ascii=False)
        _append_monitor_history(target_site, {"date": today, "total_domains": len(domains),
                                              "total_backlinks": len(rows), "toxic_count": len(toxic),
                                              "new_domains": report.get("new_domains")})
        if alerts:
            _append_monitor_alerts(target_site, report)

    return report


def get_site_profile(target_site=None):
    """Devuelve el perfil de un sitio (o de todos) para guiar la estrategia."""
    if target_site:
        if target_site not in SITES:
            return {"error": f"target_site inválido: {target_site}. Usa: {list(SITES)}"}
        return SITES[target_site]
    return SITES


# ─── Dispatcher de client tools ──────────────────────────────────────────────
TOOL_FNS = {
    "fetch_url": lambda **k: fetch_url(k["url"]),
    "score_prospect": lambda **k: score_prospect(**k),
    "save_prospect": lambda **k: save_prospect(**k),
    "list_prospects": lambda **k: list_prospects(**k),
    "score_asset_idea": lambda **k: score_asset_idea(**k),
    "save_asset_idea": lambda **k: save_asset_idea(**k),
    "list_asset_ideas": lambda **k: list_asset_ideas(**k),
    "audit_backlinks": lambda **k: audit_backlinks(**k),
    "monitor_backlinks": lambda **k: monitor_backlinks(**k),
    "link_intersect": lambda **k: link_intersect(**k),
    "generate_disavow_draft": lambda **k: generate_disavow_draft(**k),
    "get_site_profile": lambda **k: get_site_profile(k.get("target_site")),
}


def execute_tool(name, inputs):
    fn = TOOL_FNS.get(name)
    if not fn:
        return {"error": f"Unknown client tool: {name}"}
    try:
        return fn(**inputs)
    except TypeError as e:
        return {"error": f"Argumentos inválidos para {name}: {e}"}
    except Exception as e:
        return {"error": str(e)}


# ══════════════════════════════════════════════════════════════════════════════
#  CLAUDE — modelo, web search server tool, client tool schemas
# ══════════════════════════════════════════════════════════════════════════════
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
MODEL = os.getenv("BACKLINKS_MODEL", "claude-sonnet-4-6")

# Herramienta de búsqueda web del lado servidor (Anthropic la ejecuta).
WEB_SEARCH_TOOL = {
    "type": "web_search_20250305",
    "name": "web_search",
    "max_uses": 8,
    "user_location": {"type": "approximate", "country": "MX", "timezone": "America/Mexico_City"},
}

CLIENT_TOOLS = [
    {
        "name": "get_site_profile",
        "description": "Devuelve el perfil de uno de los tres sitios (raditech, grupoptm, pys) o de todos. Úsalo al inicio para alinear la estrategia al nicho correcto.",
        "input_schema": {
            "type": "object",
            "properties": {"target_site": {"type": "string", "enum": list(SITES.keys()), "description": "raditech | grupoptm | pys. Omitir para ver todos."}},
        },
    },
    {
        "name": "fetch_url",
        "description": "Descarga y analiza una página candidata: title, meta, headings, conteo de palabras, dominios externos salientes y señales básicas de spam. Úsalo para CALIFICAR un prospecto antes de puntuarlo.",
        "input_schema": {
            "type": "object",
            "properties": {"url": {"type": "string", "description": "URL completa de la página a analizar"}},
            "required": ["url"],
        },
    },
    {
        "name": "score_prospect",
        "description": (
            "Calcula un puntaje determinista 0-100 y veredicto (PURSUE/REVIEW/REJECT) de un prospecto de backlink. "
            "Asigna cada sub-puntaje SOLO tras investigar (web_search + fetch_url). "
            "Máximos: topical_relevance 30, authority_quality 25, editorial_standard 15, link_context 10, geo_language_fit 10. "
            "spam_flags con cualquiera de [sells_links, pbn, deindexed, malware, cloaking, irrelevant_niche, link_farm, adult_gambling_pharma_spam, scraped_content] fuerza REJECT."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "target_site": {"type": "string", "enum": list(SITES.keys())},
                "prospect_domain": {"type": "string"},
                "topical_relevance": {"type": "integer", "description": "0-30: relación temática con el nicho del sitio objetivo"},
                "authority_quality": {"type": "integer", "description": "0-25: autoridad/tráfico/indexación/dominio establecido"},
                "editorial_standard": {"type": "integer", "description": "0-15: calidad editorial, audiencia real, no granja de enlaces"},
                "link_context": {"type": "integer", "description": "0-10: enlace editorial contextual vs footer/directorio masivo"},
                "geo_language_fit": {"type": "integer", "description": "0-10: ajuste idioma/geo (español/México según el sitio)"},
                "spam_flags": {"type": "array", "items": {"type": "string"}, "description": "flags de riesgo detectados (ver descripción)"},
                "evidence": {"type": "string", "description": "evidencia breve que justifica los sub-puntajes"},
                "contact_path": {"type": "string", "description": "cómo contactar (email, formulario, LinkedIn, guidelines de colaboración)"},
                "suggested_tactic": {"type": "string", "description": "táctica de outreach recomendada (digital PR, recurso linkable, colaboración, etc.)"},
            },
            "required": ["target_site", "prospect_domain", "topical_relevance", "authority_quality", "editorial_standard", "link_context", "geo_language_fit"],
        },
    },
    {
        "name": "save_prospect",
        "description": "Guarda/actualiza un prospecto calificado en el tracker del sitio (deduplica por dominio). Úsalo solo para prospectos con veredicto PURSUE o REVIEW que valga la pena rastrear.",
        "input_schema": {
            "type": "object",
            "properties": {
                "target_site": {"type": "string", "enum": list(SITES.keys())},
                "prospect_domain": {"type": "string"},
                "score": {"type": "integer"},
                "verdict": {"type": "string"},
                "status": {"type": "string", "enum": VALID_STATUS, "description": "estado del pipeline de outreach"},
                "contact_path": {"type": "string"},
                "suggested_tactic": {"type": "string"},
                "notes": {"type": "string"},
                "evidence": {"type": "string"},
            },
            "required": ["target_site", "prospect_domain"],
        },
    },
    {
        "name": "list_prospects",
        "description": "Lista los prospectos ya guardados de un sitio (con resumen por status). Úsalo para evitar re-prospectar lo mismo y para reportar el pipeline.",
        "input_schema": {
            "type": "object",
            "properties": {
                "target_site": {"type": "string", "enum": list(SITES.keys())},
                "status": {"type": "string", "enum": VALID_STATUS},
            },
            "required": ["target_site"],
        },
    },
    {
        "name": "score_asset_idea",
        "description": (
            "Puntúa 0-100 una idea de ACTIVO LINKABLE (recurso que gana enlaces solo: datos/estudios originales, "
            "guías profundas, herramientas/calculadoras) y da veredicto BUILD/CONSIDER/SKIP. Úsalo para filtrar ideas "
            "que en realidad no ganarían enlaces. Máximos: link_attractiveness 30, uniqueness 25, pr_hook 20, "
            "evergreen_value 10, production_feasibility 15. Si link_attractiveness<12 o uniqueness<8 → SKIP (es solo contenido)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "target_site": {"type": "string", "enum": list(SITES.keys())},
                "title": {"type": "string", "description": "título de la idea de activo"},
                "asset_type": {"type": "string", "description": "estudio de datos | guía | herramienta/calculadora | comparativa | glosario | encuesta | infografía"},
                "link_attractiveness": {"type": "integer", "description": "0-30: qué tan natural es que otros lo citen/enlacen"},
                "uniqueness": {"type": "integer", "description": "0-25: datos/ángulo originales vs refrito"},
                "pr_hook": {"type": "integer", "description": "0-20: gancho noticiable para periodistas"},
                "evergreen_value": {"type": "integer", "description": "0-10: valor duradero"},
                "production_feasibility": {"type": "integer", "description": "0-15: realismo de producirlo (mayor = más fácil)"},
                "rationale": {"type": "string", "description": "por qué ganaría enlaces"},
                "link_targets": {"type": "array", "items": {"type": "string"}, "description": "quiénes lo enlazarían (tipos de sitios/medios)"},
            },
            "required": ["target_site", "title", "link_attractiveness", "uniqueness", "pr_hook", "evergreen_value", "production_feasibility"],
        },
    },
    {
        "name": "save_asset_idea",
        "description": "Guarda/actualiza una idea de activo linkable en el plan del sitio (deduplica por título). Úsalo para ideas BUILD/CONSIDER que valga la pena rastrear de idea → publicado → enlaces ganados.",
        "input_schema": {
            "type": "object",
            "properties": {
                "target_site": {"type": "string", "enum": list(SITES.keys())},
                "title": {"type": "string"},
                "asset_type": {"type": "string"},
                "score": {"type": "integer"},
                "verdict": {"type": "string"},
                "status": {"type": "string", "enum": VALID_ASSET_STATUS, "description": "etapa de producción/promoción"},
                "pr_hook": {"type": "string"},
                "link_targets": {"type": "array", "items": {"type": "string"}},
                "brief": {"type": "string", "description": "esquema/outline del activo y ángulo de PR"},
                "links_earned": {"type": "integer", "description": "enlaces reales ganados hasta ahora"},
                "notes": {"type": "string"},
            },
            "required": ["target_site", "title"],
        },
    },
    {
        "name": "list_asset_ideas",
        "description": "Lista el plan de activos linkables de un sitio (resumen por status). Úsalo para no duplicar ideas y reportar el pipeline de contenido.",
        "input_schema": {
            "type": "object",
            "properties": {
                "target_site": {"type": "string", "enum": list(SITES.keys())},
                "status": {"type": "string", "enum": VALID_ASSET_STATUS},
            },
            "required": ["target_site"],
        },
    },
    {
        "name": "audit_backlinks",
        "description": "Audita un CSV de backlinks existentes (exportado de GSC/Ahrefs/Ubersuggest) y marca enlaces tóxicos por patrón (TLD spam, tokens spam, anchors exact-match sobre-optimizados, posible sitewide/PBN). NO sube nada. Pega el contenido del CSV en csv_text.",
        "input_schema": {
            "type": "object",
            "properties": {
                "target_site": {"type": "string", "enum": list(SITES.keys())},
                "csv_text": {"type": "string", "description": "contenido completo del CSV de backlinks"},
            },
            "required": ["target_site", "csv_text"],
        },
    },
    {
        "name": "monitor_backlinks",
        "description": (
            "Monitor anti-SEO-negativo. Ingiere un export de backlinks como SNAPSHOT y lo compara con el anterior "
            "para detectar señales de ataque: picos de velocidad de enlaces, dominios tóxicos nuevos y anchors spam "
            "que aparecen de golpe. La primera corrida fija la línea base. NO sube nada. Corre periódicamente "
            "(semanal/quincenal) con un export fresco. También disponible headless: 'python backlinks_agent.py monitor <site> <csv>'."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "target_site": {"type": "string", "enum": list(SITES.keys())},
                "csv_text": {"type": "string", "description": "contenido del CSV de backlinks actuales"},
                "spike_abs": {"type": "integer", "description": "umbral absoluto de dominios nuevos para alertar (default 25)", "default": 25},
                "spike_mult": {"type": "number", "description": "múltiplo sobre la mediana histórica para alertar (default 3.0)", "default": 3.0},
            },
            "required": ["target_site", "csv_text"],
        },
    },
    {
        "name": "link_intersect",
        "description": (
            "PROSPECCIÓN POR INTERSECCIÓN (link gap): encuentra dominios que enlazan a tus COMPETIDORES "
            "pero NO a tu sitio. Es la prospección de mayor precisión y cero riesgo. El usuario pega el CSV "
            "de backlinks de 1-3 competidores (export gratis de Ahrefs Free Backlink Checker, Ubersuggest, "
            "Semrush, Moz o el reporte de Enlaces de GSC). Devuelve dominios candidatos ordenados por cuántos "
            "competidores enlazan (más = prospecto más fuerte). Luego cada dominio pasa por fetch_url → score_prospect."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "target_site": {"type": "string", "enum": list(SITES.keys())},
                "competitor_csvs": {
                    "type": "array",
                    "description": "1-3 competidores; cada uno con su CSV de backlinks.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "nombre/dominio del competidor (ej. 'competidorA.com')"},
                            "csv": {"type": "string", "description": "contenido del CSV de backlinks del competidor"},
                        },
                        "required": ["csv"],
                    },
                },
                "own_csv": {"type": "string", "description": "(opcional) CSV de TUS propios backlinks, para excluir quien ya te enlaza"},
                "min_competitors": {"type": "integer", "description": "solo dominios que enlazan a >= N competidores (default 1; usa 2 para los más fuertes)", "default": 1},
                "exclude_spam": {"type": "boolean", "description": "filtrar dominios con señales obvias de spam (default true)", "default": True},
                "limit": {"type": "integer", "description": "máximo de prospectos a devolver", "default": 50},
            },
            "required": ["target_site", "competitor_csvs"],
        },
    },
    {
        "name": "generate_disavow_draft",
        "description": "Genera un BORRADOR de disavow.txt SOLO con dominios YA confirmados como tóxicos tras revisión. Lo escribe a disco para que el usuario lo revise y suba manualmente. NUNCA lo sube a Google.",
        "input_schema": {
            "type": "object",
            "properties": {
                "target_site": {"type": "string", "enum": list(SITES.keys())},
                "domains": {"type": "array", "items": {"type": "string"}, "description": "dominios confirmados tóxicos (solo dominio, sin http)"},
            },
            "required": ["target_site", "domains"],
        },
    },
]

# ─── SYSTEM prompt (estrategia) ───────────────────────────────────────────────
SYSTEM_STRATEGY = """Eres un PROSPECTOR DE BACKLINKS SEO (off-page) experto, extremadamente cauteloso.
Sirves a tres sitios del mismo dueño en México:

  • raditech  → raditech.mx — B2B teleradiología, sistemas PACS-RIS, monitores grado médico.
                Audiencia: hospitales, clínicas, radiólogos, directores médicos, compras hospitalarias (México/LATAM).
  • grupoptm  → grupoptm.com (marca "PTM Novo") — TELEMEDICINA de péptidos / salud hormonal (YMYL).
                IMPORTANTE: el dominio cambió de giro; ignora todo contenido viejo de radiología.
  • pys       → peptidosysuplementos.mx — ECOMMERCE de péptidos y suplementos (YMYL, nicho sensible/restringido).

═══════════════════════════════════════════════════════════════════════════════
DIRECTIVA PRIMORDIAL: CALIDAD SOBRE CANTIDAD. Tu trabajo es proteger los rankings,
NO inflar el número de enlaces. Un solo enlace relevante y editorial de un sitio
confiable vale más que 100 enlaces de directorios basura. Prefieres recomendar
CERO enlaces antes que recomendar uno riesgoso.
═══════════════════════════════════════════════════════════════════════════════

CÓMO FUNCIONA GOOGLE HOY (2025-2026) — entiende esto antes de recomendar nada:
  - Desde el "link spam update" de dic-2022, el sistema SpamBrain DETECTA y NEUTRALIZA
    los enlaces no naturales: los "apaga" para que no pasen PageRank. NO penaliza por ellos.
    Consecuencia: la mayoría de los enlaces comprados/spam hoy simplemente NO HACEN NADA
    (dinero y esfuerzo desperdiciados), no son una "sentencia de muerte".
  - El peligro REAL y grave es la ACCIÓN MANUAL ("Unnatural links to your site"), revisada
    por humanos, que sí aparece en Search Console y exige limpieza + reconsideración para
    recuperarse. Se gatilla con esquemas evidentes y a escala creados por el propio sitio.
  - Marzo-2024 añadió "site reputation abuse": contenido patrocinado/parasitario en un sitio
    reputado pero FUERA DE TEMA, hecho para pedir prestada autoridad, ahora es violación —
    aunque el sitio sea de prestigio. No recomiendes "patrocinios" en medios off-topic.
  - Cualquier enlace pagado, regalado (producto a cambio de reseña) o auto-colocado DEBE
    llevar rel="sponsored" o rel="nofollow" (y rel="ugc" en contenido de usuario). Un enlace
    así NO ayuda al ranking, pero es 100% seguro y sirve para marca, tráfico y E-E-A-T.

SEGURO POR DISEÑO — lo que NO puedes hacer (no tienes herramientas para ello):
  - No envías correos ni mensajes, no publicas en ningún sitio, no dejas comentarios.
  - No compras enlaces ni contratas servicios de link-building.
  - No subes archivos disavow a Google. Solo generas BORRADORES para revisión humana.
  Tú INVESTIGAS, CALIFICAS, RECOMIENDAS y preparas BORRADORES que el dueño aprueba.

LA MEJOR ESTRATEGIA (la más segura y de mayor ROI): NO perseguir enlaces, sino MERECERLOS.
Casi todo lo que Google penaliza es perseguir enlaces; casi nada penaliza ganarlos. Prioriza:
  1. Activos linkables: datos/estudios originales, guías profundas, herramientas/calculadoras
     que otros citen naturalmente. Es la base que Google recompensa.
  2. Digital PR: ofrecer historias/datos noticiables a periodistas para cobertura editorial.
  3. Plataformas de fuentes expertas (Featured —sucesor de HARO—, Qwoted) con comentario real.
  4. Reclamar menciones de marca sin enlace; broken-link building; colaboraciones genuinas.

FLUJO DE PROSPECCIÓN (síguelo siempre):
  1. get_site_profile para alinear el nicho correcto.
  2. web_search para descubrir prospectos reales y relevantes (en español-México cuando aplique).
     Busca tipos de fuentes legítimas; NUNCA busques "comprar backlinks" ni proveedores de enlaces.
  3. fetch_url para inspeccionar cada candidato: ¿es real? ¿tiene audiencia y editorial?
     ¿enlaces salientes spam? ¿está en el nicho? ¿está indexado?
  4. score_prospect con sub-puntajes honestos basados en evidencia.
  5. save_prospect solo para PURSUE/REVIEW que valgan la pena rastrear.
  6. Entrega recomendación con: por qué es relevante, vía de contacto, táctica de outreach y
     un BORRADOR de propuesta de valor genuina (no un correo de spam genérico).

PLANIFICADOR DE ACTIVOS LINKABLES (score_asset_idea → save_asset_idea → list_asset_ideas):
La forma MÁS segura y de mayor ROI de ganar enlaces es CREAR activos que los atraen solos, no
perseguirlos. Un "activo linkable" gana enlaces por sí mismo: datos/estudios originales, guías
profundas de referencia, herramientas/calculadoras, comparativas, glosarios, encuestas. Un blog
normal NO es un activo linkable. Proceso:
  1. web_search para detectar HUECOS: ¿qué recurso falta en el nicho?, ¿qué citan/enlazan ya los
     competidores?, ¿qué datos no existen en español?
  2. Propón ideas concretas. Puntúa cada una con score_asset_idea (sé honesto: si nadie lo enlazaría,
     dará SKIP). Solo persigue BUILD/CONSIDER.
  3. save_asset_idea con un BRIEF (esquema del recurso + ángulo de PR + a quién se le pitchea).
  4. La PRODUCCIÓN del contenido la hace el agente de blogs/SEO existente (web.py) o el dueño; tú
     planificas, priorizas y defines el gancho de PR. Recuerda atribuir/pedir enlaces a la fuente
     ORIGINAL del dato (eso es lo que se enlaza).
Arquetipos por sitio (guía, no lista cerrada):
  ▸ raditech: "Estado de la teleradiología en México 2026" (encuesta a radiólogos/hospitales);
    guía de cumplimiento normativo (NOM e interoperabilidad DICOM/HL7 para PACS-RIS); calculadora de
    ROI/costo por estudio in-house vs teleradiología; glosario técnico PACS/RIS/DICOM; comparativa de
    monitores grado médico por modalidad. (Citan: asociaciones de radiología, prensa salud/IT, hospitales.)
  ▸ grupoptm/PTM Novo: encuesta de acceso a telemedicina/salud hormonal en México (datos NO clínicos
    = PR seguro); guía "cómo funciona una consulta de telemedicina" (proceso, privacidad de datos);
    glosario de péptidos/hormonas revisado médicamente (E-E-A-T). (Citan: medios de salud, directorios.)
  ▸ pys: guía de uso/dosificación de péptidos comunes basada en evidencia con referencias científicas
    (E-E-A-T fuerte); encuesta a la comunidad fitness/biohacking MX (tendencias); calculadora de
    macros/proteína/recuperación; infografías citables con atribución. (Citan: blogs fitness, creadores.)
Aplica SIEMPRE las reglas de marca en cualquier brief (nada de "farmacia"; nada de la frase de refrigeración).

PROSPECCIÓN POR INTERSECCIÓN (link_intersect) — tu táctica de MAYOR precisión y CERO riesgo:
encuentra dominios que enlazan a los competidores pero NO a tu sitio. SUGIÉRELA PROACTIVAMENTE,
sin esperar a que el usuario la pida, cuando se cumpla cualquiera de estos casos:
  • El usuario pide conseguir/prospectar backlinks o "subir autoridad".
  • Menciona a uno o más competidores.
  • La prospección por web_search se queda corta o muy genérica.
  • Quiere maximizar resultados con el mínimo esfuerzo/riesgo.
Al sugerirla, explica en una línea qué necesitas: que pegue el CSV de backlinks de 1-3 competidores
(export GRATIS de Ahrefs Free Backlink Checker, Ubersuggest, Semrush, Moz, o el reporte de Enlaces de
GSC) y, opcional, su propio CSV para excluir quien ya lo enlaza. Luego corre cada dominio devuelto por
fetch_url → score_prospect → save_prospect. Prioriza competitor_count alto; sube min_competitors a 2
para quedarte solo con los más fuertes.

QUÉ EVITAR SIEMPRE (violaciones explícitas de la política de spam de enlaces de Google):
  - Comprar/vender enlaces que pasen ranking (dinero, productos o servicios a cambio de enlace
    o de un post con enlace). Es el ejemplo #1 que nombra Google.
  - "Niche edits"/inserciones pagadas, advertorials y rentas mensuales de enlaces sin nofollow.
  - Guest posting a escala con anchors comerciales exact-match; press releases con anchors optimizados.
  - PBNs (redes privadas de blogs), granjas de enlaces, intercambios recíprocos excesivos.
  - Spam de comentarios, foros, perfiles y firmas; widgets/badges/infografías con enlaces sembrados.
  - Directorios y bookmarks masivos de baja calidad ("envíalo a 500 directorios").
  - Enlaces sitewide en footer/sidebar/plantilla distribuidos en muchos sitios.
  - Dominios expirados comprados por su autoridad residual; contenido fino solo para alojar enlaces.
  - Automatización de creación de enlaces. Cualquier patrón a escala que se vea artificial.

ANCHOR TEXT (evita sobre-optimización — es señal #1 de patrón manipulado):
  La mayoría de los anchors deben ser de MARCA ("Raditech", "PTM Novo", "Péptidos y Suplementos"),
  URL desnuda, o genéricos naturales ("ver aquí", "este servicio", "más información").
  Los anchors exact-match comerciales deben ser una minoría pequeña y natural. NUNCA recomiendes
  repetir el mismo anchor comercial en muchos sitios.

NICHOS YMYL (los tres son sensibles; pys y grupoptm son salud — "Your Money Your Life"):
  Google exige el máximo nivel de confianza (E-E-A-T). Un perfil de enlaces manipulado o fuera
  de tema ACTIVAMENTE erosiona la confianza, no solo "se ignora". Refuerza E-E-A-T on-site:
  autores acreditados (cédula profesional), revisor médico nombrado, referencias científicas,
  transparencia del negocio.

PLAYBOOK POR SITIO:
  ▸ raditech (B2B imagen médica): asociaciones y colegios de radiología/imagenología y de
    informática médica; directorios serios de healthcare-IT y proveedores hospitalarios;
    prensa B2B de tecnología y salud en español; partnerships con clínicas/hospitales (casos de
    éxito, testimoniales); listados de expositores en congresos/expos médicas; liderazgo de
    pensamiento en LinkedIn; co-marketing con fabricantes/integradores no competidores. Inglés OK
    para directorios médicos internacionales serios. Evita directorios B2B genéricos pay-to-list.
  ▸ grupoptm / PTM Novo (telemedicina): perfiles verificados en Doctoralia MX (gratis, ~48h) por
    cada médico tratante; Google Business Profile (config. telesalud) con NAP idéntico; membresía/
    listado en Sociedad Mexicana de Telemedicina, Telesalud y Medicina Digital (soctelmed.com) y
    alineación con el marco CENETEC / Salud Digital; citaciones locales NAP-consistentes; digital PR
    con datos originales no clínicos (encuestas de acceso a telesalud en México); páginas linkables
    (cómo funciona la consulta, privacidad de datos). Crecimiento esperado: 6+ meses, velocidad estable.
  ▸ pys (ecommerce péptidos/suplementos): el nicho es restringido — los medios mainstream casi no
    enlazan y casi todo enlace "follow" que aparece suele ser pagado (riesgo). NO fuerces enlaces de
    baja calidad para compensar; eso es justo lo que te neutraliza o te mete en problemas. Apóyate en:
    blogs/medios de fitness, nutrición y biohacking en español; reseñas de creadores reales (con
    rel=sponsored si hay producto/pago); partnerships con marcas (listados de distribuidor autorizado),
    gimnasios, entrenadores y nutriólogos; citaciones locales (GBP, Sección Amarilla, Cylex MX);
    podcasts/YouTube; recursos linkables basados en evidencia. Acepta que muchos enlaces legítimos
    serán y deben ser nofollow/sponsored.

MONITOR ANTI-SEO-NEGATIVO (monitor_backlinks):
Corre periódicamente con un export fresco de backlinks. Compara contra el snapshot anterior y alerta de
picos de velocidad, dominios tóxicos nuevos y anchors spam súbitos. INTERPRETACIÓN CRÍTICA — no cundir
el pánico: un pico de enlaces basura casi siempre es SEO negativo que SpamBrain NEUTRALIZA solo. NO es
motivo de disavow. La regla: si no hay ACCIÓN MANUAL en Search Console y el historial es limpio, NO actúes
sobre los enlaces; solo documenta y vigila. Escala a disavow únicamente si llega una acción manual.
Sugiérele al usuario configurar el monitor periódico (headless) cuando hablen de proteger rankings.

AUDITORÍA DEFENSIVA (audit_backlinks → generate_disavow_draft):
  - audit_backlinks marca SOSPECHAS por patrón, no certezas. Los "toxicity scores" de terceros
    (Semrush/Ahrefs/Moz) son heurísticas que Google NO usa; no disavow solo por un puntaje rojo.
  - Antes de proponer disavow, verifica manualmente con fetch_url los dominios marcados.
  - REGLA DE DISAVOW (dos partes — solo si AMBAS son ciertas):
      (1) tienes (o esperas con evidencia fuerte) una ACCIÓN MANUAL por enlaces no naturales, Y
      (2) los enlaces son auto-construidos/comprados/manipulados por ti o un proveedor, y NO puedes
          quitarlos en la fuente.
    Para spam orgánico, comment/forum/scraper y ataques de SEO negativo en un sitio con historial
    limpio: NO hagas disavow — SpamBrain ya los neutraliza. Desautorizar enlaces buenos DAÑA rankings.
    Ante la duda, NO disavow. Primero intenta REMOVER el enlace en la fuente; disavow es último recurso.
  - generate_disavow_draft solo con dominios YA confirmados tóxicos y auto-creados. Recuérdale al
    usuario que revise línea por línea y suba el archivo él mismo en Search Console.

REGLAS DE MARCA (obligatorias en cualquier borrador de texto/outreach/descripción):
  - NUNCA uses la palabra "farmacia" (en ninguna forma). Sustituto: "Tienda en línea".
  - NUNCA uses la frase sobre refrigeración para garantizar integridad del producto en transporte.

ESTILO: responde en el idioma del usuario (español por defecto). Sé concreto y honesto; si una
oportunidad es dudosa, dilo. Reporta el puntaje y el desglose. Hoy es """ + datetime.now().strftime("%Y-%m-%d") + "."

SYSTEM = [
    {
        "type": "text",
        "text": SYSTEM_STRATEGY,
        "cache_control": {"type": "ephemeral"},
    }
]


# ══════════════════════════════════════════════════════════════════════════════
#  Loop agéntico (maneja web_search server-side + client tools + pause_turn)
# ══════════════════════════════════════════════════════════════════════════════
def _print_assistant_text(content):
    for block in content:
        if getattr(block, "type", None) == "text" and getattr(block, "text", ""):
            print(f"\nAgente: {block.text}\n")
        if getattr(block, "type", None) == "server_tool_use" and getattr(block, "name", "") == "web_search":
            q = ""
            try:
                q = block.input.get("query", "")
            except Exception:
                pass
            print(f"  [→ web_search: {q}]", flush=True)


def run_turn(messages):
    """Procesa un turno completo del usuario, iterando tools hasta end_turn."""
    while True:
        response = client.messages.create(
            model=MODEL,
            max_tokens=4096,
            system=SYSTEM,
            tools=[WEB_SEARCH_TOOL] + CLIENT_TOOLS,
            messages=messages,
        )
        messages.append({"role": "assistant", "content": response.content})
        _print_assistant_text(response.content)

        sr = response.stop_reason

        if sr == "pause_turn":
            # Búsqueda web de larga duración: reenviar para que el servidor continúe.
            continue

        if sr == "tool_use":
            tool_results = []
            for block in response.content:
                if getattr(block, "type", None) == "tool_use" and block.name in TOOL_FNS:
                    print(f"  [→ {block.name}]", flush=True)
                    result = execute_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(result, ensure_ascii=False, default=str),
                    })
            if tool_results:
                messages.append({"role": "user", "content": tool_results})
                continue
            # tool_use sin client tools nuestros (p.ej. solo server tool ya resuelto) → terminar
            break

        if sr not in ("end_turn", "tool_use"):
            print(f"  [stop_reason: {sr}]")
        break
    return messages


def web_respond(history, max_rounds=14, max_tokens=8192):
    """
    Versión para la interfaz web: corre el loop agéntico (web_search + client tools + pause_turn)
    y DEVUELVE el texto final, sin imprimir. `history` es una lista [{role, content}] (content puede
    ser string). Devuelve dict {"reply": str, "tools_used": [..]}.
    """
    msgs = [{"role": m["role"], "content": m["content"]} for m in history if m.get("content")]
    tools_used = []
    response = None
    rounds = 0
    while rounds < max_rounds:
        rounds += 1
        response = client.messages.create(
            model=MODEL,
            max_tokens=max_tokens,
            system=SYSTEM,
            tools=[WEB_SEARCH_TOOL] + CLIENT_TOOLS,
            messages=msgs,
        )
        msgs.append({"role": "assistant", "content": response.content})
        sr = response.stop_reason

        if sr == "pause_turn":
            continue

        if sr == "tool_use":
            tool_results = []
            for block in response.content:
                if getattr(block, "type", None) == "server_tool_use" and getattr(block, "name", "") == "web_search":
                    tools_used.append("web_search")
                if getattr(block, "type", None) == "tool_use" and block.name in TOOL_FNS:
                    tools_used.append(block.name)
                    result = execute_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(result, ensure_ascii=False, default=str),
                    })
            if tool_results:
                msgs.append({"role": "user", "content": tool_results})
                continue
            break

        break

    reply = ""
    if response is not None:
        reply = "".join(getattr(b, "text", "") for b in response.content
                         if getattr(b, "type", None) == "text").strip()
    return {"reply": reply or "(sin respuesta)", "tools_used": sorted(set(tools_used))}


# ─── Persistencia de sesión ──────────────────────────────────────────────────
SESSIONS_DIR = os.path.join(DATA_DIR, "sessions")


def _serialize(content):
    if isinstance(content, str):
        return content
    return [b.model_dump() if hasattr(b, "model_dump") else b for b in content]


def save_session(messages):
    os.makedirs(SESSIONS_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    path = os.path.join(SESSIONS_DIR, f"backlinks_{ts}.json")
    payload = [{"role": m["role"], "content": _serialize(m["content"])} for m in messages]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, default=str)
    return path


# ─── CLI ──────────────────────────────────────────────────────────────────────
def run():
    messages = []
    print("\n" + "=" * 66)
    print("  Backlink Prospector — Raditech · PTM Novo · PYS")
    print("  Calidad > cantidad · sin spam · seguro por diseño")
    print("  Comandos: 'salir' para terminar")
    print("=" * 66 + "\n")
    print("  Sugerencias:")
    print("   • 'Prospecta 10 backlinks de calidad para raditech'")
    print("   • 'Planifica activos linkables para grupoptm'")
    print("   • 'Link intersect de pys vs estos competidores' (pega sus CSVs)")
    print("   • 'Audita estos backlinks de pys' (pega tu CSV)")
    print("   • 'Monitorea los backlinks de raditech' (pega tu CSV; detecta SEO negativo)")
    print("   • 'Muéstrame el pipeline de grupoptm'")
    print("   • 'Dame una estrategia de digital PR para pys sin riesgo'\n")

    try:
        while True:
            try:
                user_input = input("Tú: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nAgente: ¡Hasta luego!")
                break
            if not user_input:
                continue
            if user_input.lower() in ("exit", "salir", "quit"):
                print("Agente: ¡Hasta luego!")
                break
            messages.append({"role": "user", "content": user_input})
            messages = run_turn(messages)
    finally:
        if messages:
            path = save_session(messages)
            print(f"  [Sesión guardada → {path}]")


def _cli_monitor(argv):
    """Subcomando headless para programar: python backlinks_agent.py monitor <site> <ruta_csv>"""
    if len(argv) < 4:
        print("Uso: python backlinks_agent.py monitor <raditech|grupoptm|pys> <ruta_csv>")
        return 2
    site, path = argv[2], argv[3]
    if site not in SITES:
        print(f"Sitio inválido: {site}. Usa: {list(SITES)}")
        return 2
    try:
        with open(path, encoding="utf-8-sig", errors="replace") as f:
            csv_text = f.read()
    except OSError as e:
        print(f"No se pudo leer {path}: {e}")
        return 2
    report = monitor_backlinks(site, csv_text)
    print(json.dumps(report, ensure_ascii=False, indent=2, default=str))
    # exit code 1 si hay alertas → útil para Task Scheduler / cron (disparar notificación)
    return 1 if report.get("alerts") else 0


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "monitor":
        sys.exit(_cli_monitor(sys.argv))
    run()
