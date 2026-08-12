"""
Expansión de las entradas cortas de nodarishub (2026-08-12).

Cinco entradas quedaron entre 666 y 786 palabras, muy por debajo del piso de
1.200 que ahora exige el agente. Se amplían con Claude.

El cuidado está en no romper el diseño: estas entradas no son texto plano, son
un bloque `wp:html` con un `<div class="nh-article">`, su propio `<style>` y un
JSON-LD de FAQPage al final. El script parte el contenido en tres, manda a
Claude SOLO la prosa del medio y vuelve a pegar prefijo y sufijo tal cual, así
que ni la hoja de estilos ni el schema pueden salir dañados. La FAQ visible se
conserva textual para que el JSON-LD, que la refleja, siga siendo verdad.

Uso:
    python auditorias/nodarishub/expandir_posts_flacos.py --dry-run
    python auditorias/nodarishub/expandir_posts_flacos.py --apply [--solo 265]
"""
import sys, os, re, json, time, base64, argparse
sys.stdout.reconfigure(encoding="utf-8")
import requests
import anthropic

BASE = "https://nodarishub.com"
AQUI = os.path.dirname(os.path.abspath(__file__))
RESPALDOS = os.path.join(AQUI, "backups-expansion-2026-08-12")
PISO = 1200
OBJETIVO = 1400

FLACOS = [261, 262, 263, 264, 265]
# 180 (aviso del benchmark, 155 palabras) queda fuera a propósito: es un aviso
# corto por diseño, no un artículo al que le falte cuerpo.


def _env():
    d = {}
    for linea in open(os.path.join(AQUI, "..", "..", "ecommerce-agent__.env"), encoding="utf-8"):
        if "=" in linea and not linea.startswith("#"):
            k, v = linea.split("=", 1)
            d[k.strip()] = v.strip()
    return d


E = _env()
H = {"Authorization": "Basic " + base64.b64encode(
        f"{E.get('NODARIS_WP_USER','')}:{E.get('NODARIS_WP_APP_PASSWORD','')}".encode()).decode(),
     "Content-Type": "application/json"}
PUB = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120"}
cliente = anthropic.Anthropic(api_key=E.get("ANTHROPIC_API_KEY", os.environ.get("ANTHROPIC_API_KEY", "")))


def contar_palabras(html):
    texto = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html or "", flags=re.S | re.I)
    texto = re.sub(r"<[^>]+>", " ", texto)
    return len(texto.split())


def partir(raw):
    """(prefijo con el <style>, cuerpo de prosa, sufijo con el JSON-LD)."""
    fin_style = raw.find("</style>")
    ini_script = raw.find("<script")
    if fin_style == -1 or ini_script == -1 or ini_script <= fin_style:
        return None
    corte = fin_style + len("</style>")
    return raw[:corte], raw[corte:ini_script], raw[ini_script:]


def expandir(titulo, keyword, cuerpo, palabras):
    prompt = f"""Amplía el cuerpo de este artículo del blog de Nodarishub, una agencia digital
que hace diseño web a código, SEO y software a la medida para PyMEs en México y Ecuador.

TÍTULO: {titulo}
KEYWORD PRINCIPAL: {keyword}
LONGITUD ACTUAL: {palabras} palabras — insuficiente.
OBJETIVO: mínimo {OBJETIVO} palabras reales de prosa.

CÓMO AMPLIARLO:
- Profundiza CADA sección existente con ejemplos concretos, cifras útiles, comparativas
  y checklists accionables para un dueño de PyME (no para un técnico).
- Puedes añadir 1-2 secciones <h2> nuevas si aportan algo real.
- Explica el "por qué le conviene al negocio", no solo el "qué es".

REGLAS QUE NO PUEDES ROMPER:
1. Devuelve SOLO el HTML del cuerpo, sin ```, sin <style>, sin <script>, sin <h1>,
   y sin el <div class="nh-article"> (eso lo pone el sistema).
2. CONSERVA TEXTUALMENTE la sección final de preguntas frecuentes (el <h2> de FAQ y
   todas sus preguntas y respuestas, palabra por palabra). Hay un JSON-LD que la
   refleja y dejaría de ser cierto si la cambias.
3. CONSERVA todos los enlaces <a> que ya existen, con su mismo href.
4. Si usas una tabla, envuélvela en <div class="nh-tablewrap"> y usa
   <table class="nh-compare">, que son las clases que este diseño ya trae.
5. No inventes URLs ni cites fuentes médicas o científicas.
6. Etiquetas permitidas: <p> <h2> <h3> <ul> <ol> <li> <strong> <em> <a> <table>
   <thead> <tbody> <tr> <th> <td> <div class="nh-tablewrap"> <blockquote>.

CUERPO ACTUAL:
{cuerpo}"""
    r = cliente.messages.create(model="claude-sonnet-4-6", max_tokens=16000,
                                messages=[{"role": "user", "content": prompt}])
    texto = "".join(b.text for b in r.content if hasattr(b, "text")).strip()
    if texto.startswith("```"):
        texto = texto.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    return texto


def integridad(html):
    """Recuento de etiquetas de apertura/cierre para detectar marcado roto."""
    problemas = []
    for tag in ["div", "p", "h2", "h3", "ul", "ol", "li", "table", "tr", "td", "th", "a"]:
        ab = len(re.findall(rf"<{tag}[\s>]", html, re.I))
        ce = len(re.findall(rf"</{tag}>", html, re.I))
        if ab != ce:
            problemas.append(f"{tag}: {ab} abren / {ce} cierran")
    return problemas


def faq_intacta(antes, despues):
    """Las preguntas de la FAQ del JSON-LD deben seguir apareciendo en el cuerpo."""
    preguntas = re.findall(r'"name":"(.*?)","acceptedAnswer"', antes)
    faltan = []
    for q in preguntas:
        limpio = q.replace("\\", "")
        # Comparar por un fragmento estable, evitando líos de escapes
        aguja = limpio[:45]
        if aguja and aguja not in despues:
            faltan.append(limpio[:60])
    return faltan


CUERPOS = os.path.join(AQUI, "cuerpos-expandidos")


def volcar_cuerpos():
    """Escribe a disco el cuerpo actual de cada entrada flaca, para redactarlo aparte."""
    os.makedirs(CUERPOS, exist_ok=True)
    for pid in FLACOS:
        p = requests.get(f"{BASE}/wp-json/wp/v2/posts/{pid}", headers=H,
                         params={"context": "edit"}, timeout=30).json()
        partes = partir(p["content"]["raw"])
        if not partes:
            print(f"[{pid}] estructura inesperada")
            continue
        destino = os.path.join(CUERPOS, f"{pid}-actual.html")
        with open(destino, "w", encoding="utf-8") as fh:
            fh.write(partes[1])
        print(f"[{pid}] {contar_palabras(partes[1])} palabras -> {destino}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--solo", type=int, default=0)
    ap.add_argument("--volcar", action="store_true",
                    help="exporta los cuerpos actuales para redactarlos a mano")
    ap.add_argument("--desde-archivo", action="store_true",
                    help="toma el cuerpo nuevo de cuerpos-expandidos/<id>-nuevo.html "
                         "en vez de llamar a la API")
    a = ap.parse_args()
    if a.volcar:
        volcar_cuerpos()
        return
    dry = not a.apply
    objetivo = [a.solo] if a.solo else FLACOS

    os.makedirs(RESPALDOS, exist_ok=True)
    resumen = []

    for pid in objetivo:
        p = requests.get(f"{BASE}/wp-json/wp/v2/posts/{pid}", headers=H,
                         params={"context": "edit"}, timeout=30).json()
        raw = p["content"]["raw"]
        titulo = re.sub(r"<[^>]+>", "", p["title"]["rendered"])
        partes = partir(raw)
        if not partes:
            print(f"[{pid}] estructura inesperada, se salta")
            continue
        prefijo, cuerpo, sufijo = partes
        antes = contar_palabras(raw)
        print(f"\n[{pid}] {titulo[:62]}")
        print(f"      antes: {antes} palabras  (prefijo {len(prefijo)}c / cuerpo {len(cuerpo)}c / sufijo {len(sufijo)}c)")

        if dry:
            resumen.append((pid, antes, None))
            continue

        with open(os.path.join(RESPALDOS, f"post-{pid}.json"), "w", encoding="utf-8") as fh:
            json.dump(p, fh, ensure_ascii=False, indent=2)

        if a.desde_archivo:
            ruta = os.path.join(CUERPOS, f"{pid}-nuevo.html")
            if not os.path.exists(ruta):
                print(f"      falta {ruta}, se salta")
                continue
            nuevo_cuerpo = open(ruta, encoding="utf-8").read().strip()
        else:
            nuevo_cuerpo = expandir(titulo, titulo, cuerpo, antes)
        nuevo_raw = prefijo + "\n\n" + nuevo_cuerpo + "\n\n" + sufijo
        despues = contar_palabras(nuevo_raw)

        # Compuertas antes de escribir
        fallos = []
        if despues < PISO:
            fallos.append(f"sigue flaco ({despues} < {PISO})")
        rotas = integridad(nuevo_cuerpo)
        if rotas:
            fallos.append("marcado desbalanceado: " + "; ".join(rotas))
        perdidas = faq_intacta(sufijo, nuevo_cuerpo)
        if perdidas:
            fallos.append(f"FAQ alterada ({len(perdidas)}): {perdidas[:2]}")
        if "<script" in nuevo_cuerpo or "<style" in nuevo_cuerpo:
            fallos.append("el cuerpo trae <script>/<style>")

        if fallos:
            print(f"      ⛔ NO se escribe: {' | '.join(fallos)}")
            resumen.append((pid, antes, None))
            continue

        r = requests.post(f"{BASE}/wp-json/wp/v2/posts/{pid}", headers=H,
                          json={"content": nuevo_raw}, timeout=90)
        if r.status_code != 200:
            print(f"      ERROR al guardar: {r.status_code} {r.text[:150]}")
            resumen.append((pid, antes, None))
            continue
        print(f"      ✅ {antes} → {despues} palabras")
        resumen.append((pid, antes, despues))
        time.sleep(1)

    print("\n" + "=" * 70)
    for pid, antes, despues in resumen:
        print(f"  {pid}: {antes} → {despues if despues else '(sin cambio)'}")


if __name__ == "__main__":
    main()
