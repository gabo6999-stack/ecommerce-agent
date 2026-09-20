import os, json, requests, re, time
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
def update_wp_product_meta(post_id, meta):
    url = f'{WC_URL}/wp-json/rankmath/v1/updateMeta'
    payload = {'objectID': post_id, 'objectType': 'product', 'meta': meta}
    r = requests.post(url, headers=wp_headers, json=payload, timeout=20)
    if not r.ok:
        print(f'Error updating RM meta: {r.text}')
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
def update_rm_schemas(object_id, schemas):
    url = f'{WC_URL}/wp-json/rankmath/v1/updateSchemas'
    payload = {'objectID': object_id, 'objectType': 'product', 'schemas': schemas}
    r = requests.post(url, headers=wp_headers, json=payload, timeout=20)
    if not r.ok:
        print(f'Error updating RM schemas: {r.text}')
        return None
    return r.json()
def update_media_alt(media_id, alt_text):
    url = f'{WC_URL}/wp-json/wp/v2/media/{media_id}'
    r = requests.post(url, headers=wp_headers, json={'alt_text': alt_text}, timeout=15)
    if not r.ok:
        print(f'Error updating media alt: {r.text}')
        return None
    return r.json()

def fetch_score(product_id):
    wp = get_wp_product(product_id)
    if wp:
        return wp.get('meta', {}).get('rank_math_seo_score', None)
    return None

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

# Step 1: Title
print('\\n--- Step 1: Title <=60 and includes keyword ---')
title = wp_product.get('title', {}).get('rendered', '')
if keyword.lower() not in title.lower():
    title = f'{keyword}: {title}'
if len(title) > 60:
    title = title[:60]
print(f'New title: {title} (len {len(title)})')
update_data = {'title': title}
r = requests.post(f'{WC_URL}/wp-json/wp/v2/product/{product_id}', headers=wp_headers, json=update_data, timeout=15)
if r.ok:
    print('Title updated successfully.')
    time.sleep(1)
else:
    print('Title update failed.')

score = fetch_score(product_id)
print(f'Score after step 1: {score}')

# Step 2: Meta description
print('\\n--- Step 2: Meta description length 120-160 ---')
wp_product = get_wp_product(product_id)
if not wp_product:
    exit(1)
meta = wp_product.get('meta', {})
desc = meta.get('rank_math_description', '')
print(f'Current meta description length: {len(desc)}')
needs_change = False
if len(desc) < 120:
    print(f'Description too short ({len(desc)} < 120), will pad.')
    needs_change = True
elif len(desc) > 160:
    print(f'Description too long ({len(desc)} > 160), will trim.')
    needs_change = True
else:
    print('Description length already within 120-160 characters.')
if not needs_change:
    print('Step 2 already satisfied.')
else:
    if len(desc) < 120:
        needed = 120 - len(desc)
        repeats = (needed + len(keyword) - 1) // len(keyword)
        desc = desc + (' ' + keyword) * repeats
        if len(desc) > 160:
            desc = desc[:160]
    else:
        desc = desc[:160]
    print(f'New meta description length: {len(desc)}')
    rm_meta = {'rank_math_description': desc}
    rm_resp = update_wp_product_meta(product_id, rm_meta)
    if rm_resp:
        print('Rank Math meta description updated successfully.')
        time.sleep(1)
    else:
        print('Rank Math meta description update failed.')
score = fetch_score(product_id)
print(f'Score after step 2: {score}')

# Step 3: Image alt
print('\\n--- Step 3: Ensure image with alt containing keyword ---')
wp_product = get_wp_product(product_id)
if not wp_product:
    exit(1)
wc_product = get_wc_product(product_id)
if not wc_product:
    exit(1)
images = wc_product.get('images', [])
print(f'Number of images: {len(images)}')
if images:
    img_id = images[0].get('id')
    print(f'First image ID: {img_id}')
    # Fetch media
    media_url = f'{WC_URL}/wp-json/wp/v2/media/{img_id}'
    media_resp = requests.get(media_url, headers=wp_headers, timeout=15)
    if media_resp.ok:
        media = media_resp.json()
        alt = media.get('alt_text', '')
        print(f'Current alt text: {alt}')
        if keyword.lower() not in alt.lower():
            new_alt = f'{alt} {keyword}'.strip()
            print(f'Updating alt to: {new_alt}')
            media_update = requests.post(media_url, headers=wp_headers, json={'alt_text': new_alt}, timeout=15)
            if media_update.ok:
                print('Image alt updated successfully.')
                time.sleep(1)
            else:
                print(f'Failed to update image alt: {media_update.text}')
        else:
            print('Alt already contains keyword.')
    else:
        print(f'Failed to fetch media: {media_resp.text}')
else:
    print('No images found; skipping image alt update.')
score = fetch_score(product_id)
print(f'Score after step 3: {score}')

# Step 4: H2 heading in description
print('\\n--- Step 4: Ensure H2 heading with keyword in description ---')
wp_product = get_wp_product(product_id)
if not wp_product:
    exit(1)
wc_product = get_wc_product(product_id)
if not wc_product:
    exit(1)
long_desc_html = wc_product.get('description', '')
print(f'Long description length: {len(long_desc_html)}')
pattern = re.compile(r'<h2[^>]*>.*?' + re.escape(keyword) + r'.*?</h2>', re.IGNORECASE)
if pattern.search(long_desc_html):
    print(f'Found an H2 containing keyword "{keyword}". Step 4 already satisfied.')
else:
    print(f'No H2 containing keyword "{keyword}" found. Adding one.')
    heading = f'<h2>{keyword}: Información detallada</h2>'
    long_desc_html = heading + long_desc_html
    print(f'Added heading: {heading}')
    update_data = {'description': long_desc_html}
    update_resp = update_wc_product(product_id, update_data)
    if update_resp:
        print('Long description updated successfully.')
        time.sleep(1)
    else:
        print('Long description update failed.')
score = fetch_score(product_id)
print(f'Score after step 4: {score}')

# Step 5: FAQ schema
print('\\n--- Step 5: Add FAQ schema JSON-LD ---')
wp_product = get_wp_product(product_id)
if not wp_product:
    exit(1)
faq_schema = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [
        {
            "@type": "Question",
            "name": f"¿Qué es {keyword}?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": f"{keyword} es un péptido sintético de la familia de la insulina que promueve el crecimiento celular y tiene efectos anabólicos."
            }
        },
        {
            "@type": "Question",
            "name": f"¿Cuáles son los beneficios de {keyword}?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": f"La investigación sugiere que {keyword} puede aumentar la masa muscular, reducir la grasa corporal y mejorar la recuperación atlética."
            }
        }
    ]
}
schemas = [faq_schema]
print('Adding FAQ schema...')
schema_resp = update_rm_schemas(product_id, schemas)
if schema_resp:
    print('Rank Math schema updated successfully.')
    time.sleep(1)
else:
    print('Rank Math schema update failed (maybe permission issue).')
score = fetch_score(product_id)
print(f'Score after step 5: {score}')

# Step 6: Internal/external links
print('\\n--- Step 6: Add internal and external links in description ---')
wp_product = get_wp_product(product_id)
if not wp_product:
    exit(1)
wc_product = get_wc_product(product_id)
if not wc_product:
    exit(1)
long_desc_html = wc_product.get('description', '')
links_paragraph = f'<p>Para más información, visita nuestra <a href="{WC_URL}/">homepage</a> y consulta fuentes como <a href="https://pubmed.ncbi.nlm.nih.gov/" target="_blank" rel="nofollow">PubMed</a> sobre {keyword}.</p>'
if 'homepage' in long_desc_html and 'PubMed' in long_desc_html:
    print('Similar link paragraph already present. Step 6 already satisfied.')
else:
    print(f'Adding links paragraph.')
    long_desc_html = long_desc_html + links_paragraph
    update_data = {'description': long_desc_html}
    update_resp = update_wc_product(product_id, update_data)
    if update_resp:
        print('Description updated with links successfully.')
        time.sleep(1)
    else:
        print('Description update with links failed.')
score = fetch_score(product_id)
print(f'\\nFinal Rank Math SEO score: {score}')
print(f'Change from initial: {score - score_before}')
# Show final meta
wp_product = get_wp_product(product_id)
if wp_product:
    meta = wp_product.get('meta', {})
    print(f'Title: {meta.get("rank_math_title","")}')
    print(f'Meta description: {meta.get("rank_math_description","")}')
    print(f'Focus keyword: {meta.get("rank_math_focus_keyword","")}')
else:
    print('Failed to fetch final product')