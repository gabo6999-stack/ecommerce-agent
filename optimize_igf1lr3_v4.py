import os, json, requests, time
from dotenv import load_dotenv
load_dotenv(r'C:\Users\gabom\Proyectos\ecommerce-agent\ecommerce-agent__.env')
WC_URL = os.getenv('WC_STORE_URL').rstrip('/')
WP_USER = os.getenv('WP_USER')
WP_PASSWORD = os.getenv('WP_PASSWORD')
CONSUMER_KEY = os.getenv('WC_CONSUMER_KEY')
CONSUMER_SECRET = os.getenv('WC_CONSUMER_SECRET')
print('WC_URL:', WC_URL)
# Get JWT token for WP API
jwt_url = f'{WC_URL}/wp-json/jwt-auth/v1/token'
resp = requests.post(jwt_url, json={'username': WP_USER, 'password': WP_PASSWORD}, timeout=15)
if not resp.ok:
    print('Failed to get JWT token:', resp.text)
    exit(1)
token = resp.json().get('token')
wp_headers = {'Authorization': f'Bearer {token}'}
# WooCommerce Basic Auth
wc_auth = (CONSUMER_KEY, CONSUMER_SECRET)

def get_wp_product(post_id):
    url = f'{WC_URL}/wp-json/wp/v2/product/{post_id}?context=edit'
    r = requests.get(url, headers=wp_headers, timeout=15)
    if not r.ok:
        print(f'Error fetching WP product {post_id}:', r.text)
        return None
    return r.json()
def update_wp_product(post_id, data):
    url = f'{WC_URL}/wp-json/wp/v2/product/{post_id}'
    r = requests.post(url, headers=wp_headers, json=data, timeout=15)
    if not r.ok:
        print(f'Error updating WP product {post_id}:', r.text)
        return None
    return r.json()
def get_wc_product(product_id):
    url = f'{WC_URL}/wp-json/wc/v3/products/{product_id}'
    r = requests.get(url, auth=wc_auth, timeout=15)
    if not r.ok:
        print(f'Error fetching WC product {product_id}:', r.text)
        return None
    return r.json()
def update_wc_product(product_id, data):
    url = f'{WC_URL}/wp-json/wc/v3/products/{product_id}'
    r = requests.put(url, auth=wc_auth, json=data, timeout=15)
    if not r.ok:
        print(f'Error updating WC product {product_id}:', r.text)
        return None
    return r.json()

product_id = 1128  # IGF-1 LR3
print(f'Fetching product {product_id}...')
wp_product = get_wp_product(product_id)
if not wp_product:
    exit(1)
wc_product = get_wc_product(product_id)
if not wc_product:
    exit(1)

meta = wp_product.get('meta', {})
score_before = meta.get('rank_math_seo_score', 0)
print(f'Initial Rank Math SEO score: {score_before}')
print(f'Title: {wp_product.get("title",{}).get("rendered","")}')
print(f'Meta description: {meta.get("rank_math_description","")[:100]}')
print(f'Focus keyword: {meta.get("rank_math_focus_keyword","")}')

keyword = 'IGF-1 LR3'
# We'll also consider a secondary keyword: 'IGF-1 LR3 1mg'

# Step 1: Update title via WP API (post title)
print('\\n--- Step 1: Update post title ---')
title = wp_product.get('title', {}).get('rendered', '')
if keyword.lower() not in title.lower():
    title = f'{keyword}: {title}'
if len(title) > 60:
    title = title[:60]
print(f'New title: {title} (len {len(title)})')
update_data = {'title': title}
resp = update_wp_product(product_id, update_data)
if resp:
    print('Title updated successfully.')
    time.sleep(1)
else:
    print('Title update failed.')

# Step 2: Update content (long description and short description) via WC API
print('\\n--- Step 2: Update long and short description ---')
wc_product = get_wc_product(product_id)
if not wc_product:
    exit(1)
long_desc = wc_product.get('description', '')
short_desc = wc_product.get('short_description', '')
print(f'Original long description length: {len(long_desc)}')
print(f'Original short description length: {len(short_desc)}')

# We'll prepare new long description: ensure H1, convert H3, lists, add table, links, etc.
# For simplicity, we'll just keep the existing long description but ensure it has an H1 with keyword and a table.
# We'll do a minimal set: add H1 if missing, add a benefits table, add internal/external links.
import re
working = long_desc
# Ensure H1
if not re.search(r'<h1[^>]*>', working, re.IGNORECASE):
    working = f'<h1>{title}</h1>' + working
    print('Added H1')
# Ensure at least one H2 with keyword
if not re.search(r'<h2[^>]*>.*?' + re.escape(keyword) + r'.*?</h2>', working, re.IGNORECASE):
    # Insert after H1
    h1_match = re.search(r'<h1[^>]*>.*?</h1>', working, re.IGNORECASE)
    if h1_match:
        insert_pos = h1_match.end()
    else:
        insert_pos = 0
    working = working[:insert_pos] + f'<h2>{keyword}: Información detallada</h2>' + working[insert_pos:]
    print('Added H2 with keyword')
# Convert H3 to bold paragraphs (optional)
working = re.sub(r'<h3[^>]*>.*?</h3>', lambda m: f'<p><strong>{re.sub(r\"<h3[^>]*>|</h3>\", \"\", m.group(0), flags=re.IGNORECASE)}</strong></p>', working, flags=re.IGNORECASE)
# Convert lists to paragraphs
working = re.sub(r'<ul[^>]*>.*?</ul>|<ol[^>]*>.*?</ol>', lambda m: ''.join([f'<p>{re.sub(r\"<li[^>]*>|</li>\", \"\", li, flags=re.IGNORECASE)}</p>' for li in re.findall(r'<li[^>]*>.*?</li>', m.group(0), flags=re.IGNORECASE)]), working, flags=re.IGNORECASE | re.DOTALL)
# Add a simple benefits table if not present
if '<table' not in working.lower():
    table = '''
<table>
  <thead><tr><th>Beneficio</th><th>Descripción</th></tr></thead>
  <tbody>
    <tr><td>Crecimiento muscular</td><td>Promueve la síntesis de proteínas y la hipertrofia muscular.</td></tr>
    <tr><td>Reducción de grasa</td><td>Aumenta la lipólisis y mejora la composición corporal.</td></tr>
    <tr><td>Recuperación</td><td>Acelera la reparación de tejidos y reduce el tiempo de recuperación post-entrenamiento.</td></tr>
    <tr><td>Anti-envejecimiento</td><td>Mejora la elasticidad de la piel y reduce líneas de expresión.</td></tr>
  </tbody>
</table>
'''
    # Insert after first H2 or after H1
    insert_pos = 0
    h2_match = re.search(r'<h2[^>]*>.*?</h2>', working, re.IGNORECASE)
    if h2_match:
        insert_pos = h2_match.end()
    else:
        h1_match = re.search(r'<h1[^>]*>.*?</h1>', working, re.IGNORECASE)
        if h1_match:
            insert_pos = h1_match.end()
    working = working[:insert_pos] + table + working[insert_pos:]
    print('Added benefits table')
# Add internal/external links paragraph
links_para = f'<p>Para más información, visita nuestra <a href="{WC_URL}/">homepage</a> y consulta fuentes como <a href="https://pubmed.ncbi.nlm.nih.gov/" target="_blank" rel="nofollow">PubMed</a> sobre {keyword}.</p>'
if 'homepage' not in working.lower() or 'pubmed' not in working.lower():
    working = working + links_para
    print('Added links paragraph')
else:
    print('Links already present')
new_long_desc = working
new_short_desc = f'IGF-1 LR3 1mg liofilizado, pureza ≥99% HPLC con certificado de análisis por lote. Consulta precio y disponibilidad en México. Envío a toda la República.'
# Truncate short description to ~200 chars
if len(new_short_desc) > 200:
    new_short_desc = new_short_desc[:200] + '...'
print(f'New long description length: {len(new_long_desc)}')
print(f'New short description length: {len(new_short_desc)}')
# Update via WC API
update_wc_data = {
    'description': new_long_desc,
    'short_description': new_short_desc
}
resp = update_wc_product(product_id, update_wc_data)
if resp:
    print('Long and short description updated successfully.')
    time.sleep(1)
else:
    print('Long/short description update failed.')

# Step 3: Update Rank Math meta fields via WP API (post meta)
print('\\n--- Step 3: Update Rank Math meta fields via WP API ---')
# Fetch current post to get existing meta (we need to preserve other meta)
wp_product = get_wp_product(product_id)
if not wp_product:
    exit(1)
current_meta = wp_product.get('meta', {})
print(f'Current meta keys: {list(current_meta.keys())}')
# Prepare new meta values
new_meta = current_meta.copy()
new_meta['rank_math_title'] = title  # use the same title we set
new_meta['rank_math_description'] = new_short_desc  # or we could use a longer description; but meta description usually short
new_meta['rank_math_focus_keyword'] = keyword  # we'll use the main keyword
# Update the post with meta field
# The WP API expects meta as an array of objects? Let's try sending as an object under 'meta'
update_data = {'meta': new_meta}
resp = update_wp_product(product_id, update_data)
if resp:
    print('Rank Math meta fields updated successfully via WP API.')
    time.sleep(1)
else:
    print('Rank Math meta fields update failed.')
    # Try alternative: send meta as array of objects
    meta_array = [{'key': k, 'value': v} for k, v in new_meta.items()]
    update_data = {'meta': meta_array}
    resp = update_wp_product(product_id, update_data)
    if resp:
        print('Rank Math meta fields updated successfully via WP API (array format).')
        time.sleep(1)
    else:
        print('Rank Math meta fields update also failed in array format.')

# Step 4: Verify changes
print('\\n--- Step 4: Verify changes ---')
time.sleep(2)
wp_product = get_wp_product(product_id)
if wp_product:
    final_meta = wp_product.get('meta', {})
    score_after = final_meta.get('rank_math_seo_score', 0)
    print(f'Final Rank Math SEO score: {score_after}')
    print(f'Change from initial: {score_after - score_before}')
    print(f'Title: {wp_product.get("title",{}).get("rendered","")}')
    print(f'Rank Math title: {final_meta.get("rank_math_title","")}')
    print(f'Rank Math description: {final_meta.get("rank_math_description","")}')
    print(f'Rank Math focus keyword: {final_meta.get("rank_math_focus_keyword","")}')
    # Also get content length
    wc_product = get_wc_product(product_id)
    if wc_product:
        print(f'Long description length: {len(wc_product.get("description",""))}')
        print(f'Short description length: {len(wc_product.get("short_description",""))}')
else:
    print('Failed to fetch final product')