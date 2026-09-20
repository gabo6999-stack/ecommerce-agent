import os, json, requests, re
from dotenv import load_dotenv
load_dotenv(r'C:\Users\gabom\Proyectos\ecommerce-agent\ecommerce-agent__.env')
WC_URL = os.getenv('WC_STORE_URL').rstrip('/')
WP_USER = os.getenv('WP_USER')
WP_PASSWORD = os.getenv('WP_PASSWORD')
# Get JWT token
jwt_url = f'{WC_URL}/wp-json/jwt-auth/v1/token'
resp = requests.post(jwt_url, json={'username': WP_USER, 'password': WP_PASSWORD}, timeout=15)
if not resp.ok:
    print('Failed to get JWT token:', resp.text)
    exit(1)
token = resp.json().get('token')
wp_headers = {'Authorization': f'Bearer {token}'}

def get_wp_page(page_id):
    url = f'{WC_URL}/wp-json/wp/v2/pages/{page_id}?context=edit'
    r = requests.get(url, headers=wp_headers, timeout=15)
    if not r.ok:
        print(f'Error fetching page {page_id}:', r.text)
        return None
    return r.json()

def get_page_meta(page_id):
    url = f'{WC_URL}/wp-json/wp/v2/pages/{page_id}?context=edit'
    r = requests.get(url, headers=wp_headers, timeout=15)
    if not r.ok:
        return None
    return r.json().get('meta', {})

def analyze_content(content):
    if not content:
        return {}
    length = len(content)
    h1_count = len(re.findall(r'<h1[^>]*>.*?</h1>', content, re.IGNORECASE))
    h2_count = len(re.findall(r'<h2[^>]*>.*?</h2>', content, re.IGNORECASE))
    h3_count = len(re.findall(r'<h3[^>]*>.*?</h3>', content, re.IGNORECASE))
    ul_count = len(re.findall(r'<ul[^>]*>.*?</ul>', content, re.IGNORECASE | re.DOTALL))
    ol_count = len(re.findall(r'<ol[^>]*>.*?</ol>', content, re.IGNORECASE | re.DOTALL))
    internal_links = len(re.findall(r'<a[^>]*href=["\']' + re.escape(WC_URL) + '[^>]*>', content, re.IGNORECASE))
    external_links = len(re.findall(r'<a[^>]*href=["\'](?!' + re.escape(WC_URL) + ')[^>]*>', content, re.IGNORECASE))
    schema_blocks = len(re.findall(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>', content, re.IGNORECASE))
    faq_blocks = len(re.findall(r'"@type"\s*:\s*"FAQPage"', content, re.IGNORECASE))
    return {
        'length': length,
        'h1': h1_count,
        'h2': h2_count,
        'h3': h3_count,
        'ul': ul_count,
        'ol': ol_count,
        'internal_links': internal_links,
        'external_links': external_links,
        'schema_blocks': schema_blocks,
        'faq_blocks': faq_blocks
    }

print('=== ANALIZANDO PÁGINA: Política de Privacidad (ID 3) ===')
page = get_wp_page(3)
if not page:
    print('ERROR: No se pudo obtener la página')
    exit(1)

title = page.get('title', {}).get('rendered', '')
content = page.get('content', {}).get('rendered', '')
meta = page.get('meta', {})

print(f'Título: {title}')
print(f'URL: {page.get("link", "N/A")}')
print(f'Estado: {page.get("status", "N/A")}')
print()

print('--- METADATOS RANK MATH ACTUALES ---')
rank_math_title = meta.get('rank_math_title', '')
rank_math_description = meta.get('rank_math_description', '')
rank_math_focus_keyword = meta.get('rank_math_focus_keyword', '')
current_score = meta.get('rank_math_seo_score', 0)

print(f'rank_math_title: "{rank_math_title}" (longitud: {len(rank_math_title)})')
print(f'rank_math_description: "{rank_math_description}" (longitud: {len(rank_math_description)})')
print(f'rank_math_focus_keyword: "{rank_math_focus_keyword}"')
print(f'rank_math_seo_score: {current_score}')
print()

print('--- ANÁLISIS DE CONTENIDO ---')
metrics = analyze_content(content)
print(f'Longitud total: {metrics["length"]} caracteres')
print(f'Estructura de encabezados:')
print(f'  H1: {metrics["h1"]}')
print(f'  H2: {metrics["h2"]}')
print(f'  H3: {metrics["h3"]}')
print(f'Listas:')
print(f'  UL: {metrics["ul"]}')
print(f'  OL: {metrics["ol"]}')
print(f'Enlaces:')
print(f'  Internos: {metrics["internal_links"]}')
print(f'  Externos: {metrics["external_links"]}')
print(f'Estructura de datos:')
print(f'  Bloques de schema: {metrics["schema_blocks"]}')
print(f'  Bloques FAQ: {metrics["faq_blocks"]}')
print()

print('--- COMPARACIÓN CON PATRÓN ÓPTIMO IDENTIFICADO ---')
print('Basado en nuestro análisis de alto rendimiento:')
print()
print('✅ CORRECTO (cumple con patrón óptimo):')
if metrics['h1'] == 1:
    print('  - EXACTAMENTE 1 H1: ✓')
else:
    print(f'  - EXACTAMENTE 1 H1: ✗ (tiene {metrics["h1"]} H1)')
    
if 10 <= metrics['h2'] <= 15:
    print(f'  - H2 en rango óptimo (10-15): ✓ ({metrics["h2"]} H2)')
else:
    print(f'  - H2 en rango óptimo (10-15): ✗ ({metrics["h2"]} H2 - necesita {"más" if metrics["h2"] < 10 else "menos"} H2)')
    
if metrics['h3'] <= 5:
    print(f'  - H3 máximo recomendado (≤5): ✓ ({metrics["h3"]} H3)')
else:
    print(f'  - H3 máximo recomendado (≤5): ✗ ({metrics["h3"]} H3 - necesita reducir a 5 o menos)')
    
total_links = metrics['internal_links'] + metrics['external_links']
if total_links >= 20:
    print(f'  - Total de enlaces (interno+externo ≥20): ✓ ({total_links} enlaces)')
else:
    print(f'  - Total de enlaces (interno+externo ≥20): ✗ ({total_links} enlaces - necesita {20-total_links} más)')
    
if 1 <= metrics['schema_blocks'] <= 2:
    print(f'  - Bloques de schema óptimos (1-2): ✓ ({metrics["schema_blocks"]} bloques)')
else:
    print(f'  - Bloques de schema óptimos (1-2): ✗ ({metrics["schema_blocks"]} bloques - necesita {"más" if metrics["schema_blocks"] < 1 else "menos"} bloques)')
    
if metrics['faq_blocks'] == 1:
    print(f'  - Bloques FAQ óptimos (exactamente 1): ✓ ({metrics["faq_blocks"]} FAQ)')
else:
    print(f'  - Bloques FAQ óptimos (exactamente 1): ✗ ({metrics["faq_blocks"]} FAQ - necesita {"más" if metrics["faq_blocks"] < 1 else "menos"} FAQ)')
    
print()
print('--- PLAN DE ACCIÓN ORGÁNICO PARA MEJORAR PUNTUACIÓN ---')
print('Basado en los gaps identificados:')
print()
acciones = []
if metrics['h1'] != 1:
    acciones.append('AJUSTAR H1: Asegurar que haya exactamente 1 H1 (usualmente el título de la página)')
if not (10 <= metrics['h2'] <= 15):
    needed = 10 - metrics['h2'] if metrics['h2'] < 10 else metrics['h2'] - 15
    acciones.append(f'AJUSTAR H2: {"Agregar" if metrics["h2"] < 10 else "Reducir a"} {abs(needed)} H2 para llegar al rango 10-15')
if metrics['h3'] > 5:
    acciones.append(f'REDUCIR H3: Convertir {metrics["h3"] - 5} H3 a párrafos en negrita o eliminarlos')
if total_links < 20:
    acciones.append(f'AGREGAR ENLACES: Añadir {20 - total_links} enlaces (mezcla de internos a contenido relacionado y externos a fuentes autoritativas)')
if metrics['schema_blocks'] < 1:
    acciones.append('AGREGAR SCHEMA: Añadir 1 bloque de schema JSON-LD (por ejemplo, WebPage o FAQPage)')
elif metrics['schema_blocks'] > 2:
    acciones.append(f'REDUCIR SCHEMA: Mantener solo 2 bloques de schema más relevantes, eliminar el resto')
if metrics['faq_blocks'] != 1:
    needed = 1 - metrics['faq_blocks']
    acciones.append(f'AJUSTAR FAQ: {"Agregar" if metrics["faq_blocks"] < 1 else "Eliminar"} {abs(needed)} bloque(s) FAQ para tener exactamente 1')
if metrics['length'] < 20000:
    acciones.append(f'AMPLIAR CONTENIDO: Añadir aproximadamente {20000 - metrics["length"]} caracteres de contenido relevante y de calidad')
    
print('Acciones recomendadas:')
for i, accion in enumerate(acciones, 1):
    print(f'{i}. {accion}')
    
if not acciones:
    print('✅ La página ya cumple con todos los patrones orgánicos óptimos identificados.')
    
print()
print('--- RECOMENDACIONES DE CONTENIDO ESPECÍFICAS ---')
print('Para una Política de Privacidad, considere:')
print('1. ESTRUCTURA DE ENCABCEADOS:')
print('   - H1: "Política de Privacidad de PyS México"')
print('   - H2: Secciones como "Información que Recopilamos", "Cómo Usamos su Información",')
print('         "Compartición de Datos", "Derechos del Usuario", "Cookies y Tecnologías de Seguimiento",')
print('         "Transferencias Internacionales", "Seguridad de los Datos", "Menores de Edad",')
print('         "Cambios a esta Política", "Contacto"')
print('   - Evitar H3 innecesarios; usar negrita para sub-puntos importantes')
print()
print('2. ENLACES INTERNOS:')
print('   - Vincular a: Términos y Condiciones, Política de Cookies,')
print('                 Página de inicio, sección de productos más relevantes,')
print('                 blog artículos relacionados con privacidad de datos en salud/suplementos')
print()
print('3. ENLACES EXTERNOS (a fuentes autoritativas):')
print('   - Ley Federal de Protección de Datos Personales en Posesión de Particulares (LFPDPPP)')
print('   - Aviso de Privacidad Integral de la Secretaría de Salud')
print('   - Guía de la PROFECO sobre comercio electrónico')
print('   - Recursos de la OMS o FDA sobre privacidad en salud digital')
print()
print('4. ESQUEMA ESTRUCTURADO:')
print('   - Usar un solo bloque WebPage con propiedades específicas para sitio de salud')
print('   - O bien, un bloque FAQPage con 3-5 preguntas clave sobre privacidad')
print()
print('5. CONTENIDO:')
print('   - Asegurar cobertura completa de lo que requiere la LFPDPPP')
print('   - Incluir ejemplos específicos de cómo PyS maneja datos de salud')
print('   - Asegurar longitud sustancial (>20,000 caracteres parece beneficioso)')

print()
print('--- PRÓXIMOS PASOS PARA IMPLEMENTACIÓN ---')
print('1. Crear copia de respaldo de la página actual')
print('2. Aplicar los cambios de estructura de encabezados sugeridos')
print('3. Añadir/ajustar enlaces internos y externos según las recomendaciones')
print('4. Implementar el schema estructurado recomendado')
print('5. Expandir y mejorar el contenido según las pautas de privacidad')
print('6. Medir el impacto en la puntuación Rank Math de forma orgánica')
print('7. Si la mejora es significativa, replicar el patrón en otras páginas')