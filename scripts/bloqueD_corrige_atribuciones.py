#!/usr/bin/env python3
"""BLOQUE D — corrige las 10 afirmaciones con PMID válido pero paper no relacionado.

Lógica a/b/c aplicada sobre la AFIRMACIÓN, no sobre el enlace. Todo PMID nuevo
verificado contra eutils en los cuatro campos (autor, revista, año, título) antes
de escribirse aquí, y las cifras contra el abstract o el texto completo.

    py -3 scripts/bloqueD_corrige_atribuciones.py            # dry-run + diffs
    py -3 scripts/bloqueD_corrige_atribuciones.py --apply
"""
from __future__ import annotations

import difflib
import html as H
import json
import pathlib
import re
import sys
import time

import requests

REPO = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://peptidosysuplementos.mx"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"}
APPLY = "--apply" in sys.argv
HOY = time.strftime("%Y-%m-%d")
SALIDA = REPO / "docs" / "data" / "blog-interlinks"
DIFFS = SALIDA / "diffs-bloqueD"
BACKUPS = REPO / "backups"
EXT = ' target="_blank" rel="noopener noreferrer"'


def P(pmid):
    return f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"


# PMIDs propuestos, con los cuatro campos como los devolvió eutils. El script
# los revalida antes de escribir nada.
ESPERADO = {
    "34267654": ("Seiwerth", "Front Pharmacol", "2021",
                 "Stable Gastric Pentadecapeptide BPC 157 and Wound Healing"),
    "16352683": ("Teichman", "J Clin Endocrinol Metab", "2006",
                 "Prolonged stimulation of growth hormone"),
    "11311852": ("Huff", "Int J Biochem Cell Biol", "2001",
                 "beta-Thymosins, small acidic peptides"),
    "29986520": ("Pickart", "Int J Mol Sci", "2018",
                 "Regenerative and Protective Actions of the GHK-Cu Peptide"),
    "20536453": ("Philp", "Ann N Y Acad Sci", "2010",
                 "Animal studies with thymosin beta"),
    "14501183": ("Anisimov", "Biogerontology", "2003",
                 "Effect of Epitalon on biomarkers of aging"),
    "37366315": ("Jastreboff", "N Engl J Med", "2023",
                 "Triple-Hormone-Receptor Agonist Retatrutide for Obesity"),
    "41996180": ("Batsis", "Ann Intern Med", "2026",
                 "Effect of Incretin-Based and Nonpharmacologic Weight Loss on Body Composition"),
    "39015186": ("Pantanetti", "Front Endocrinol", "2024",
                 "Changes in body weight and composition"),
    # Fuentes de la sección reescrita del #6, una por afirmación:
    "41877354": ("Eisa", "Diabetes Obes Metab", "2026",
                 "Lean Mass Changes With Incretin Therapy Versus Lifestyle Intervention"),
    "41622038": ("Zemski Berry", "J Clin Endocrinol Metab", "2026",
                 "Weight loss reduces intermuscular adipose tissue and liver fat"),
    "41577337": ("Prokopidis", "Br J Pharmacol", "2026",
                 "Glucagon-like peptide-1 receptor agonists and muscle strength changes in older adults"),
}

# Qué fuente sostiene cada afirmación de la sección reescrita (#6). Cada cifra
# se leyó del abstract antes de escribirla; ninguna sale de memoria del modelo.
FUENTES_SECCION_6 = [
    ("1. La masa magra sí disminuye de forma significativa",
     "PMID 41877354 · Eisa & Barood, Diabetes Obes Metab 2026 · metaanálisis de 20 ECA "
     "y 15,782 participantes: semaglutida 35.2% del peso perdido como masa magra "
     "(IC95% 31.5-38.9)"),
    ("2. Parte de esa caída no es músculo contráctil; la grasa intermuscular baja más "
     "y eso es favorable",
     "PMID 41622038 · Zemski Berry et al., J Clin Endocrinol Metab 2026 · ECA de 12 "
     "semanas con RM: IMAT -12.7% (P<.0001) frente a masa muscular esquelética -4.2% "
     "(P=.17, no significativa); sensibilidad a la insulina +42%; textual: «DXA "
     "overestimated muscle loss compared with MRI»"),
    ("3. La pérdida de músculo real ocurre y es relevante en mayores o con sarcopenia",
     "PMID 41577337 · Prokopidis, Br J Pharmacol 2026 · a corto-medio plazo la fuerza "
     "de prensión se preserva pese a la caída de masa magra, pero en adultos mayores "
     "con diabetes tipo 2 los estudios longitudinales reportan pérdida de fuerza y "
     "sarcopenia acelerada con semaglutida prolongada"),
    ("4. Mitigación: entrenamiento de resistencia y aporte proteico",
     "PMID 41877354 · Eisa & Barood 2026 · estilo de vida + entrenamiento de "
     "resistencia: 17.5% (IC95% 14.2-20.8) del peso perdido como masa magra, frente al "
     "35.2% de semaglutida sola; conclusión textual sobre integrar entrenamiento de "
     "fuerza, aporte proteico y seguimiento de composición corporal"),
]

# (post, viejo, nuevo, grupo, nota)
EDICIONES = [
    # ── #1 (a) BPC-157: la afirmación es cierta y hay literatura ─────────────
    (2256,
     f'<a href="{P("33915439")}"{EXT}>Investigaciones preclínicas publicadas en PubMed han documentado su potencial en la reparación de tejidos y procesos antiinflamatorios</a>',
     f'<a href="{P("34267654")}"{EXT}>Una revisión en Frontiers in Pharmacology (Seiwerth et al., 2021)</a> documenta su potencial en la reparación de tejidos y procesos antiinflamatorios',
     "a", "recita el paper correcto y nombra fuente, revista y año"),

    # ── #2 (a) CJC-1295: el paper correcto está en la revista que el texto ya nombraba
    (2096,
     f'<a href="{P("18710725")}"{EXT}>Un estudio clínico publicado en el Journal of Clinical Endocrinology</a>',
     f'<a href="{P("16352683")}"{EXT}>Un estudio clínico publicado en el Journal of Clinical Endocrinology and Metabolism (Teichman et al., 2006)</a>',
     "a", "el paper real está justo en la revista que el texto citaba; solo estaba mal el PMID"),

    # ── #3 (b) Tβ4: hecho cierto, revista inventada ──────────────────────────
    (2070,
     f'<a href="{P("16338069")}"{EXT}>Investigaciones publicadas en el Journal of Cell Science</a> han documentado este mecanismo de acción con detalle',
     f'<a href="{P("11311852")}"{EXT}>La literatura sobre las β-timosinas (Huff et al., Int J Biochem Cell Biol, 2001)</a> documenta este mecanismo de acción con detalle',
     "b", "se elimina la revista falsa (Journal of Cell Science) y se cita la real"),

    # ── #4 (a) GHK-Cu: se recita Y se suaviza la cifra ───────────────────────
    # Pickart & Margolina 2018 NO dice "más de 4,000 genes". Dice textualmente:
    # «The number of human genes stimulated or suppressed by GHK with a change
    # greater than or equal to 50% is 31.2%» y «GHK increases gene expression in
    # 59% of the genes, while suppressing it in 41%». Se escribe eso.
    (1913,
     f'<a href="{P("25999638")}"{EXT}>estudios genómicos publicados en PubMed demuestran que el GHK-Cu modula la expresión de más de 4,000 genes implicados en la reparación tisular y la inflamación</a>',
     f'<a href="{P("29986520")}"{EXT}>el análisis genómico de Pickart y Margolina (Int J Mol Sci, 2018)</a> reporta que el GHK modifica en un 50% o más la expresión del 31.2% de los genes humanos analizados —aumentándola en el 59% de los casos y suprimiéndola en el 41%—, con efectos sobre vías de reparación tisular e inflamación',
     "a", "cifra corregida contra el TEXTO COMPLETO: el paper no enuncia '4,000 genes'"),

    # ── #5 (c) GHK y cognición: se borra ─────────────────────────────────────
    # El paper correcto (Pickart 2017) es de expresión génica, no de conducta en
    # ratones. El único trabajo en ratones es un preprint sin revisión por pares:
    # no es fuente válida en un sitio de salud.
    (1913,
     f'<p>Observaciones preliminares sugieren que GHK puede revertir parcialmente el deterioro cognitivo en ratones ancianos al dirigirse a vías antiinflamatorias y epigenéticas, abriendo posibilidades fascinantes para futuras aplicaciones terapéuticas. Estos hallazgos están respaldados por <a href="{P("24396637")}"{EXT}>investigaciones publicadas en PubMed que evalúan el impacto del GHK en la expresión génica relacionada con el envejecimiento</a>.</p>\n',
     '',
     "c", "no hay fuente revisada por pares para la afirmación cognitiva en ratones; el preprint no cuenta"),

    # ── #6 sección reescrita — RESOLUCIÓN MÉDICA: los 4 puntos exigidos ──────
    # Cada afirmación numerada corresponde 1:1 a una entrada de
    # FUENTES_SECCION_6 (impresa en el reporte para verificación cruzada).
    # Ninguna cifra sale de memoria del modelo: las tres fuentes se leyeron
    # completas antes de escribir una sola línea de este bloque.
    (1727,
     '<h2>Composición Corporal: Preservando la Masa Muscular</h2>\n'
     '<p>Un aspecto crucial para deportistas y entusiastas del fitness es el impacto de la semaglutida en la masa muscular. <cite index="9-3">La composición corporal mejoró, con la mayoría (84%) de la pérdida de peso con semaglutida 7.2 mg proveniente de masa grasa, con pruebas que mostraron preservación de la función muscular.</cite> Para profundizar en este tema, nuestra Guía Completa de Composición Corporal ofrece estrategias basadas en evidencia para optimizar tu físico.</p>\n'
     f'<p><cite index="13-6">En el grupo tratado con la nueva dosis, el 84% de la reducción de peso se debió a la pérdida de masa grasa, preservando la masa muscular.</cite> Estos datos son especialmente relevantes para atletas que buscan optimizar su composición corporal sin comprometer su rendimiento. La evidencia científica disponible en <a href="{P("34583183")}" rel="noopener noreferrer" target="_blank">PubMed sobre semaglutida y composición corporal</a> respalda estos hallazgos con datos de múltiples ensayos clínicos.</p>',
     '<h2>Composición Corporal: qué pasa realmente con la masa muscular</h2>\n'
     '<p>Un aspecto crucial para deportistas y entusiastas del fitness es el impacto de la semaglutida en la masa muscular, y conviene ser directo con lo que dice la evidencia.</p>\n'
     f'<p><strong>La masa magra sí disminuye de forma significativa.</strong> El metaanálisis más amplio disponible —<a href="{P("41877354")}"{EXT}>Eisa y Barood, Diabetes &amp; Obesity Metabolism, 2026</a>, 20 ensayos clínicos aleatorizados y 15,782 participantes— encontró que con semaglutida el <strong>35.2%</strong> del peso perdido (IC95% 31.5–38.9) correspondió a masa magra; con tirzepatida fue 25.4% y con liraglutide 26.8%.</p>\n'
     f'<p><strong>Pero no toda esa caída es músculo contráctil.</strong> La masa magra que mide un DXA incluye agua, glucógeno y también la grasa intermuscular e intergrasa que rodea al músculo — y esa parte, al perderse, es una mejora, no una pérdida. Un ensayo aleatorizado con resonancia magnética (<a href="{P("41622038")}"{EXT}>Zemski Berry et al., Journal of Clinical Endocrinology &amp; Metabolism, 2026</a>) encontró que, con la pérdida de peso, el tejido adiposo intermuscular bajó <strong>12.7%</strong> mientras que la masa muscular esquelética real apenas cambió (<strong>-4.2%, sin significancia estadística</strong>) — y advierte textualmente que el DXA sobrestima la pérdida muscular frente a la resonancia.</p>\n'
     f'<p><strong>Aun así, la pérdida de tejido muscular real también ocurre, y es clínicamente relevante</strong> — sobre todo en personas mayores o con sarcopenia. Una revisión reciente (<a href="{P("41577337")}"{EXT}>Prokopidis, British Journal of Pharmacology, 2026</a>) reporta que a corto y mediano plazo la fuerza de prensión suele preservarse pese a la caída de masa magra, pero que en adultos mayores con diabetes tipo 2 los estudios longitudinales sí documentan pérdida de fuerza y sarcopenia acelerada con el uso prolongado de semaglutida.</p>\n'
     f'<p><strong>La mitigación que sí cambia el resultado: entrenamiento de resistencia y aporte proteico adecuado.</strong> En el mismo metaanálisis de Eisa y Barood, combinar estilo de vida con entrenamiento de resistencia bajó la proporción de masa magra perdida a <strong>17.5%</strong> (IC95% 14.2–20.8) — la mitad, aproximadamente, que con semaglutida sola. No es un extra opcional: es la parte del protocolo que decide si lo que se pierde es grasa o es función.</p>',
     "c", "REESCRITURA por resolución médica: 4 puntos exigidos, cada cifra "
          "verificada contra el abstract (ver FUENTES_SECCION_6)"),

    # ── #7 (c) ejercicio 15.9% → 52.2%: sin fuente, se borra ─────────────────
    (1727,
     f'<cite index="20-6">La proporción de personas con obesidad que realiza ejercicio físico de forma regular incrementó de 15.9% a 52.2%, siendo el incremento en la realización de ejercicio físico el mejor predictor de la pérdida de peso.</cite> Esto sugiere que la semaglutida puede promover adherencia a hábitos saludables más allá de su efecto farmacológico directo. Para apoyar los niveles de energía durante este proceso, el <a href="{SITE}/product/nad-plus-500mg/">NAD+ 500mg</a> es un suplemento que favorece el metabolismo energético celular, con respaldo en <a href="{P("31186521")}" rel="noopener noreferrer" target="_blank">investigaciones publicadas en PubMed sobre NAD+ y metabolismo</a>.',
     f'Para apoyar los niveles de energía durante el proceso, el <a href="{SITE}/product/nad-plus-500mg/">NAD+ 500mg</a> es un suplemento que favorece el metabolismo energético celular.',
     "c", "la cifra 15.9%→52.2% no tiene fuente localizable; se borra junto con la cita falsa de NAD+"),

    # ── #8 (b) TB-500 ≠ Tβ4, con la redacción que ya usa bien la ficha 795 ───
    (1675,
     f'De acuerdo con una <a href="{P("20570613")}" rel="noopener noreferrer" target="_blank">revisión publicada en PubMed sobre Thymosin Beta-4 y regeneración tisular</a>, el mecanismo de acción del TB-500 involucra la regulación positiva de la actina, lo que facilita la migración y proliferación celular.',
     f'Conviene precisar una distinción que se pasa por alto a menudo: <strong>TB-500 no es timosina beta-4 completa</strong>. La timosina beta-4 (Tβ4) es una proteína de 43 aminoácidos; TB-500 corresponde únicamente al motivo de unión a actina de 7 aminoácidos derivado de ella. Casi toda la literatura disponible —incluida la <a href="{P("20536453")}"{EXT}>revisión de estudios en animales de Philp y Kleinman (Ann N Y Acad Sci, 2010)</a>— es sobre la proteína completa, y describe un mecanismo de regulación de la actina que facilita la migración y proliferación celular. Los resultados de Tβ4 no son directamente extrapolables al fragmento.',
     "b", "añade la distinción Tβ4 ≠ TB-500 con la misma redacción que la ficha 795"),

    # ── #9 (b) Epitalon: se corrige el DATO, no solo la cita ─────────────────
    # El abstract de Anisimov 2003 dice literalmente que Epitalon «did not
    # influence food consumption, body weight or MEAN LIFE SPAN of mice»;
    # +13.3% en el último 10% de supervivientes y +12.3% de vida máxima.
    (1675,
     f'El <strong>Epitalon</strong> representa uno de los casos más intrigantes: estudios en roedores han demostrado que puede extender la vida media y máxima entre un 12% y 24%. Este péptido actúa sobre los telómeros, las estructuras protectoras en los extremos de nuestros cromosomas que se acortan con cada división celular y que están directamente relacionadas con el envejecimiento celular. Una <a href="{P("12374163")}" rel="noopener noreferrer" target="_blank">investigación publicada en PubMed sobre Epitalon y la activación de la telomerasa</a> sugiere que este tetrapéptido podría inducir la actividad de la telomerasa en células somáticas humanas, abriendo una línea de investigación muy relevante.',
     f'El <strong>Epitalon</strong> representa uno de los casos más intrigantes, y también uno donde conviene leer la evidencia con cuidado. En el estudio de referencia en ratones (<a href="{P("14501183")}"{EXT}>Anisimov et al., Biogerontology, 2003</a>), el Epitalon <strong>no modificó la vida media</strong>; lo que sí aumentó fue la vida del último 10% de supervivientes (+13.3%) y la <strong>vida máxima (+12.3%)</strong>. Una distinción importante: buena parte de la literatura de longevidad que se le atribuye es en realidad sobre la <strong>epitalamina</strong>, un extracto pineal, y no sobre el Epitalon tetrapéptido (Ala-Glu-Asp-Gly); son cosas distintas y sus resultados no son intercambiables. Sobre el mecanismo, se ha descrito que este tetrapéptido induce actividad de la telomerasa en células somáticas humanas, una línea de investigación relevante pero todavía inicial.',
     "b", "corrige el dato (la fuente dice que NO influyó en la vida media) y añade Epitalon ≠ epitalamina"),

    # ── #10 (a) retatrutide fase 2 ───────────────────────────────────────────
    (1647,
     f'<a href="{P("37354911")}" rel="noopener noreferrer" target="_blank">PubMed – Efectos metabólicos del retatrutide en ensayo de fase 2</a>',
     f'<a href="{P("37366315")}"{EXT}>el ensayo de fase 2 publicado en el New England Journal of Medicine (Jastreboff et al., 2023)</a>',
     "a", "recita el ensayo de fase 2 real"),
]

GRUPO = {"a": "(a) recitar", "b": "(b) reescribir", "c": "(c) borrar/reescribir"}


def env():
    d = {}
    for line in (REPO / "ecommerce-agent__.env").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            d[k.strip()] = v.strip().strip('"').strip("'")
    return d


ENV = env()


def jwt():
    r = requests.post(f"{SITE}/wp-json/jwt-auth/v1/token",
                      json={"username": ENV["WP_USER"], "password": ENV["WP_PASSWORD"]},
                      timeout=20)
    tok = r.json().get("token")
    if not tok:
        sys.exit(f"JWT falló: {r.status_code} {r.text[:200]}")
    return {"Authorization": f"Bearer {tok}"}


def get_post(pid):
    r = requests.get(f"{SITE}/wp-json/wp/v2/posts/{pid}",
                     params={"_fields": "id,title,link,content"}, headers=UA, timeout=45)
    r.raise_for_status()
    d = r.json()
    return {"title": H.unescape(re.sub("<[^>]+>", "", d["title"]["rendered"])),
            "link": d["link"], "content": d["content"]["rendered"]}


def revalida_pmids():
    """Compuerta 1: cada PMID nuevo existe y sus cuatro campos coinciden."""
    ids = sorted(ESPERADO)
    r = requests.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi",
                     params={"db": "pubmed", "id": ",".join(ids), "retmode": "json"},
                     timeout=60)
    res = (r.json() or {}).get("result") or {}
    print("compuerta 1 — revalidación de los PMID propuestos:")
    fallos = []
    for p in ids:
        rec = res.get(p) or {}
        au = (rec.get("authors") or [{}])[0].get("name", "")
        rev, anio, tit = rec.get("source", ""), (rec.get("pubdate") or "")[:4], rec.get("title", "")
        e_au, e_rev, e_anio, e_tit = ESPERADO[p]
        ok = (e_au.lower() in au.lower() and e_rev.lower()[:12] in rev.lower()
              and e_anio == anio and e_tit.lower()[:40] in tit.lower())
        print(f"  {'OK ' if ok else '✗  '} {p}  {au} · {rev} {anio}")
        print(f"        {tit[:92]}")
        if not ok:
            fallos.append((p, au, rev, anio, tit))
    if fallos:
        sys.exit(f"ABORTADO: no coinciden los cuatro campos en {[f[0] for f in fallos]}")
    print()


def main():
    DIFFS.mkdir(parents=True, exist_ok=True)
    BACKUPS.mkdir(exist_ok=True)
    revalida_pmids()

    print("=" * 96)
    print("Sección reescrita del #6 (post 1727) — fuente por afirmación:")
    for afirma, fuente in FUENTES_SECCION_6:
        print(f"  {afirma}")
        print(f"      -> {fuente}")
    print("=" * 96 + "\n")

    por_post = {}
    for pid, viejo, nuevo, grupo, nota in EDICIONES:
        por_post.setdefault(pid, []).append((viejo, nuevo, grupo, nota))

    reporte = []
    for pid, eds in sorted(por_post.items()):
        post = get_post(pid)
        html = post["content"]
        nuevo_html, acciones, error = html, [], False
        for viejo, nuevo, grupo, nota in eds:
            n = nuevo_html.count(viejo)
            if n != 1:
                print(f"  ✗ {pid} [{grupo}] el fragmento aparece {n} veces: {viejo[:80]!r}")
                error = True
                continue
            nuevo_html = nuevo_html.replace(viejo, nuevo)
            acciones.append({"grupo": grupo, "nota": nota,
                             "quita": re.sub(r"\s+", " ", re.sub("<[^>]+>", "", viejo)).strip(),
                             "deja": re.sub(r"\s+", " ", re.sub("<[^>]+>", "", nuevo)).strip() or "(nada)"})
        if error or nuevo_html == html:
            continue

        d = "\n".join(difflib.unified_diff(
            html.splitlines(), nuevo_html.splitlines(),
            fromfile=f"{pid}-antes", tofile=f"{pid}-despues", lineterm="", n=1))
        (DIFFS / f"{pid}.diff").write_text(d, encoding="utf-8")

        print(f"\n  {pid}  {post['title'][:54]}")
        for a in acciones:
            print(f"      {GRUPO[a['grupo']]} — {a['nota']}")
            print(f"          antes: {a['quita'][:150]}")
            print(f"          ahora: {a['deja'][:150]}")
        reporte.append({"id": pid, "title": post["title"], "link": post["link"],
                        "acciones": acciones, "diff": f"diffs-bloqueD/{pid}.diff"})

        if APPLY:
            (BACKUPS / f"blog-{pid}-antes-bloqueD-{HOY}.json").write_text(
                json.dumps({"id": pid, "title": post["title"], "content": html},
                           ensure_ascii=False, indent=1), encoding="utf-8")
            r = requests.post(f"{SITE}/wp-json/wp/v2/posts/{pid}",
                              headers=jwt(), json={"content": nuevo_html}, timeout=60)
            print(f"      WP -> HTTP {r.status_code}")
            reporte[-1]["http"] = r.status_code

    (SALIDA / "reporte-bloqueD.json").write_text(
        json.dumps({"fecha": HOY, "aplicado": APPLY, "posts": reporte},
                   ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nposts a tocar: {len(reporte)}   diffs -> {DIFFS}")
    if not APPLY:
        print("(dry-run: no se escribió nada)")


if __name__ == "__main__":
    main()
