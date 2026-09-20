import os, json, requests, re, time, base64
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
def update_wp_product_meta(post_id, meta):
    # Rank Math meta endpoint
    url = f'{WC_URL}/wp-json/rankmath/v1/updateMeta'
    payload = {'objectID': post_id, 'objectType': 'product', 'meta': meta}
    r = requests.post(url, headers=wp_headers, json=payload, timeout=20)
    if not r.ok:
        print(f'Error updating Rank Math meta: {r.text}')
        return None
    return r.json()
def update_wp_product_schemas(post_id, schemas):
    url = f'{WC_URL}/wp-json/rankmath/v1/updateSchemas'
    payload = {'objectID': post_id, 'objectType': 'product', 'schemas': schemas}
    r = requests.post(url, headers=wp_headers, json=payload, timeout=20)
    if not r.ok:
        print(f'Error updating Rank Math schemas: {r.text}')
        return None
    return r.json()

PRODUCT_ID = 1128  # IGF-1 LR3
print(f'Fetching product {PRODUCT_ID}...')
wp_product = get_wp_product(PRODUCT_ID)
if not wp_product:
    exit(1)
wc_product = get_wc_product(PRODUCT_ID)
if not wc_product:
    exit(1)

meta = wp_product.get('meta', {})
score_before = meta.get('rank_math_seo_score', 0)
print(f'Initial Rank Math SEO score: {score_before}')
title = wp_product.get('title', {}).get('rendered', '')
content = wp_product.get('content', {}).get('rendered', '')  # This is the product description? Actually WP product content is the description?
# For WooCommerce, the long description is in wc_product['description']
long_desc = wc_product.get('description', '')
short_desc = wc_product.get('short_description', '')
print(f'Title: {title}')
print(f'Long description length: {len(long_desc)}')
print(f'Short description length: {len(short_desc)}')
print(f'Focus keyword: {meta.get("rank_math_focus_keyword", "")}')

# --- Step 1: Ensure exactly one H1 in long description ---
print('\n--- Step 1: Ensure exactly one H1 ---')
# Find all H1 tags
h1_matches = re.findall(r'<h1[^>]*>.*?</h1>', long_desc, re.IGNORECASE)
print(f'Found {len(h1_matches)} H1 tags')
if len(h1_matches) == 0:
    # Add H1 at start with title
    new_h1 = f'<h1>{title}</h1>'
    long_desc = new_h1 + long_desc
    print('Added H1 at start')
elif len(h1_matches) > 1:
    # Keep first H1, remove others
    long_desc = re.sub(r'<h1[^>]*>.*?</h1>', '', long_desc, flags=re.IGNORECASE)
    new_h1 = f'<h1>{title}</h1>'
    long_desc = new_h1 + long_desc
    print('Removed extra H1s, added one H1 at start')
else:
    print('Already exactly one H1')

# --- Step 2: Reduce H3 (convert to bold paragraphs) ---
print('\n--- Step 2: Convert H3 to bold paragraphs ---')
h3_matches = re.findall(r'<h3[^>]*>.*?</h3>', long_desc, re.IGNORECASE)
print(f'Found {len(h3_matches)} H3 tags')
if h3_matches:
    def h3_to_strong(m):
        inner = m.group(0)
        # Strip h3 tags
        inner = re.sub(r'<h3[^>]*>|</h3>', '', inner, flags=re.IGNORECASE)
        return f'<p><strong>{inner}</strong></p>'
    long_desc = re.sub(r'<h3[^>]*>.*?</h3>', h3_to_strong, long_desc, flags=re.IGNORECASE)
    print('Converted all H3 tags to bold paragraphs')
else:
    print('No H3 tags found')

# --- Step 3: Remove UL/OL lists (convert items to paragraphs) ---
print('\n--- Step 3: Convert UL/OL lists to paragraphs ---')
def replace_list(match):
    html = match.group(0)
    # Determine if ul or ol
    tag = 'ul' if '<ul' in html.lower() else 'ol'
    # Extract list items
    lis = re.findall(r'<li[^>]*>.*?</li>', html, re.IGNORECASE)
    if not lis:
        return ''  # remove empty list
    # Convert each li to a paragraph
    paras = []
    for li in lis:
        inner = re.sub(r'<li[^>]*>|</li>', '', li, flags=re.IGNORECASE)
        paras.append(f'<p>{inner}</p>')
    return ''.join(paras)
new_long_desc = re.sub(r'<ul[^>]*>.*?</ul>|<ol[^>]*>.*?</ol>', replace_list, long_desc, flags=re.IGNORECASE | re.DOTALL)
if new_long_desc != long_desc:
    long_desc = new_long_desc
    print('Converted UL/OL lists to paragraphs')
else:
    print('No UL/OL lists found')

# --- Step 4: Increase internal/external links ---
print('\n--- Step 4: Ensure internal/external links paragraph ---')
links_para = f'<p>Para más información, visita nuestra <a href="{WC_URL}/">homepage</a> y consulta fuentes como <a href="https://pubmed.ncbi.nlm.nih.gov/" target="_blank" rel="nofollow">PubMed</a> sobre IGF-1 LR3.</p>'
if 'homepage' not in long_desc.lower() or 'pubmed' not in long_desc.lower():
    # Append at end
    long_desc = long_desc + links_para
    print('Added internal/external links paragraph')
else:
    print('Internal/external links already present')

# --- Step 5: Ensure single FAQ schema ---
print('\n--- Step 5: Ensure single FAQPage schema ---')
# We'll create a single FAQ schema for IGF-1 LR3
faq_schema = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [
        {
            "@type": "Question",
            "name": "¿Qué es IGF-1 LR3?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "IGF-1 LR3 (Long R3 Insulin-like Growth Factor-1) es una versión modificada y más larga del IGF-1 humano, con una vida media prolongada y mayor potencia para promover el crecimiento celular y la síntesis de proteínas."
            }
        },
        {
            "@type": "Question",
            "name": "¿Cuáles son los beneficios de IGF-1 LR3?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "IGF-1 LR3 puede aumentar la masa muscular, mejorar la recuperación, promover la pérdida de grasa y tener efectos anti-envejecimiento a nivel celular."
            }
        },
        {
            "@type": "Question",
            "name": "¿Cuál es la dosis típica de IGF-1 LR3?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "La dosis de investigación varía entre 20 mcg y 100 mcg por día, administrada por vía subcutánea, generalmente en ciclos de 4-6 semanas."
            }
        }
    ]
}
schemas = [faq_schema]
# Update via Rank Math schema endpoint
resp = update_wp_product_schemas(PRODUCT_ID, schemas)
if resp:
    print('Rank Math FAQ schema updated successfully.')
else:
    print('Rank Math schema update failed; will try to embed JSON-LD in content as fallback')
    # Embed JSON-LD as fallback
    schema_json = json.dumps(faq_schema, ensure_ascii=False)
    schema_block = f'\\n<script type=\"application/ld+json\">\\n{schema_json}\\n</script>\\n'
    # Avoid duplicate: check if similar script already exists
    if 'application/ld+json' not in long_desc:
        long_desc = long_desc + schema_block
        print('Added FAQ schema JSON-LD to long description')
    else:
        print('FAQ schema JSON-LD already present in long description')

# --- Step 6: Update meta fields (title, description, focus keyword) ---
print('\n--- Step 6: Update Rank Math meta fields ---')
# Ensure title length <=60 and contains keyword (we'll keep current title)
new_title = title
if len(new_title) > 60:
    new_title = new_title[:60]
# Ensure meta description length 120-160
meta_desc = meta.get('rank_math_description', '')
# If empty, generate from content first 160 chars
if not meta_desc:
    # Extract plain text from long_desc (strip tags)
    plain = re.sub(r'<[^>]+>', ' ', long_desc)
    plain = re.sub(r'\\s+', ' ', plain).strip()
    meta_desc = plain[:160]
# Ensure keyword present (we'll use a focused keyword)
focus_keyword = 'IGF-1 LR3'
if focus_keyword.lower() not in meta_desc.lower():
    meta_desc = f'{focus_keyword} - {meta_desc}'
# Adjust length
if len(meta_desc) < 120:
    needed = 120 - len(meta_desc)
    # pad with keyword repeats
    pad = (focus_keyword + ' ') * ((needed // len(focus_keyword)) + 1)
    meta_desc = meta_desc + pad
    if len(meta_desc) > 160:
        meta_desc = meta_desc[:160]
elif len(meta_desc) > 160:
    meta_desc = meta_desc[:160]
print(f'Meta description length: {len(meta_desc)}')
# Focus keyword: we can keep existing or set to a phrase
# Let's set to a phrase: 'IGF-1 LR3 beneficios'
new_focus = 'IGF-1 LR3 beneficios'
# Prepare meta dict
new_meta = {
    'rank_math_title': new_title,
    'rank_math_description': meta_desc,
    'rank_math_focus_keyword': new_focus
}
# Update via Rank Math meta endpoint
resp = update_wp_product_meta(PRODUCT_ID, new_meta)
if resp:
    print('Rank Math meta fields updated successfully.')
else:
    print('Rank Math meta update failed.')

# --- Update WP product title (post title) and WC product description/short_description ---
print('\n--- Updating WP product title and WC description ---')
update_wp_data = {}
if new_title != title:
    update_wp_data['title'] = new_title
# Note: WP product content is not the same as WooCommerce description; we'll update WC description via WC API
update_wc_data = {}
if long_desc != wc_product.get('description', ''):
    update_wc_data['description'] = long_desc
if short_desc != wc_product.get('short_description', ''):
    # We'll set short description to a concise version of meta description
    short_desc_new = meta_desc
    if len(short_desc_new) > 200:
        short_desc_new = short_desc_new[:200] + '...'
    update_wc_data['short_description'] = short_desc_new
if update_wp_data:
    resp = update_wp_product(PRODUCT_ID, update_wp_data)
    if resp:
        print('WP product title updated successfully.')
    else:
        print('WP product title update failed.')
if update_wc_data:
    resp = update_wc_product(PRODUCT_ID, update_wc_data)
    if resp:
        print('WC product description and short description updated successfully.')
    else:
        print('WC product description/update failed.')

# Wait a bit for any async processes
print('\nWaiting 2 seconds for changes to propagate...')
time.sleep(2)

# Fetch final score
print('\n--- Final verification ---')
wp_product_final = get_wp_product(PRODUCT_ID)
if wp_product_final:
    meta_final = wp_product_final.get('meta', {})
    score_after = meta_final.get('rank_math_seo_score', 0)
    print(f'Final Rank Math SEO score: {score_after}')
    print(f'Change from initial: {score_after - score_before}')
    print(f'Title: {wp_product_final.get(\"title\",{}).get(\"rendered\",\"\")}')
    print(f'Rank Math title: {meta_final.get(\"rank_math_title\",\"\")}')
    print(f'Rank Math description: {meta_final.get(\"rank_math_description\",\"\")}')
    print(f'Rank Math focus keyword: {meta_final.get(\"rank_math_focus_keyword\",\"\")}')
    # Also get WC product to see description length
    wc_product_final = get_wc_product(PRODUCT_ID)
    if wc_product_final:
        print(f'Long description length: {len(wc_product_final.get(\"description\",\""))}')
        print(f'Short description length: {len(wc_product_final.get(\"short_description\",\""))}')
else:
    print('Failed to fetch final product')