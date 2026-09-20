import os, json, requests, re
from dotenv import load_dotenv
load_dotenv(r'C:\Users\gabom\Proyectos\ecommerce-agent\ecommerce-agent__.env')
WC_URL = os.getenv('WC_STORE_URL').rstrip('/')
WP_USER = os.getenv('WP_USER')
WP_PASSWORD = os.getenv('WP_PASSWORD')
# Get JWT token
jwt_url = f'{WC_URL}/wp-json/jwt-auth/v1/token'
resp = requests.post(jwt_url, json={'username': WP_USER, 'password': WP_PASSWORD}, timeout=10)
if not resp.ok:
    print('Failed to get JWT token:', resp.text)
    exit(1)
token = resp.json().get('token')
wp_headers = {'Authorization': f'Bearer {token}'}

def get_wp_page(page_id):
    url = f'{WC_URL}/wp-json/wp/v2/pages/{page_id}?context=edit'
    r = requests.get(url, headers=wp_headers, timeout=8)
    if not r.ok:
        return None
    return r.json()

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

# Let's just analyze a few key pages first
key_pages = [
    (3, 'Política de Privacidad'),
    (10, 'Política de Devolución'), 
    (150, 'Blog'),
    (2418, 'NAD+ artículo'),
    (2327, 'Artículo blog'),
    (1551, 'Catálogo de productos'),
    (1166, 'Suplementos deportivos'),
    (1046, 'Precio Retatrutida'),
    (1729, 'Tirzepatida en Mexico'),
    (1750, 'Semaglutida en Mexico'),
]

print('Analyzing key pages for organic optimization opportunities...')
results = []
for pid, name in key_pages:
    print(f'  Analyzing ID {pid}: {name}...')
    page = get_wp_page(pid)
    if not page:
        print(f'    FAIL: Could not fetch page')
        continue
    content = page.get('content', {}).get('rendered', '')
    meta = page.get('meta', {})
    score = meta.get('rank_math_seo_score', 0)
    metrics = analyze_content(content)
    results.append({
        'id': pid,
        'name': name,
        'score': score,
        'metrics': metrics
    })
    print(f'    Score: {score}')
    print(f'    H1/H2/H3: {metrics["h1"]}/{metrics["h2"]}/{metrics["h3"]}')
    print(f'    Links: {metrics["internal_links"]} internal, {metrics["external_links"]} external')
    print(f'    Schema/FAQ: {metrics["schema_blocks"]} schema, {metrics["faq_blocks"]} FAQ')
    print(f'    Length: {metrics["length"]} chars')
    print()

print('=== SUMMARY OF KEY PAGES ===')
print('ID  Name                                      Score  H1  H2  H3  Links  Schema  FAQ  Length')
print('-' * 85)
for r in results:
    m = r['metrics']
    links = m['internal_links'] + m['external_links']
    print(f'{r["id"]:2}  {r["name"]:<40} {r["score"]:>5}  {m["h1"]:>2}  {m["h2"]:>2}  {m["h3"]:>2}  {links:>5}  {m["schema_blocks"]:>6}  {m["faq_blocks"]:>3}  {m["length"]:>6}')

print()
print('=== ANALYSIS VS OPTIMAL PATTERNS ===')
print('Optimal patterns from high-performing content:')
print('  - H1: exactly 1')
print('  - H2: 10-15')  
print('  - H3: 0-5')
print('  - Links (internal+external): ≥20')
print('  - Schema blocks: 1-2')
print('  - FAQ blocks: exactly 1')
print('  - Length: ≥20,000 characters (beneficial)')
print()

print('Pages needing attention:')
for r in results:
    m = r['metrics']
    issues = []
    if m['h1'] != 1:
        issues.append(f'H1={m["h1"]} (need 1)')
    if not (10 <= m['h2'] <= 15):
        issues.append(f'H2={m["h2"]} (need 10-15)')
    if m['h3'] > 5:
        issues.append(f'H3={m["h3"]} (need ≤5)')
    links = m['internal_links'] + m['external_links']
    if links < 20:
        issues.append(f'Links={links} (need ≥20)')
    if not (1 <= m['schema_blocks'] <= 2):
        issues.append(f'Schema={m["schema_blocks"]} (need 1-2)')
    if m['faq_blocks'] != 1:
        issues.append(f'FAQ={m["faq_blocks"]} (need 1)')
    if m['length'] < 20000:
        issues.append(f'Length={m["length"]} (need ≥20k)')
    
    if issues:
        print(f'  ID {r["id"]}: {r["name"]} - {", ".join(issues)}')
    else:
        print(f'  ID {r["id"]}: {r["name"]} - ✓ Meets all organic criteria')