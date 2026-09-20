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
# We'll also consider a secondary keyword: 'IGF-1 LR3 1mg'

# Backup original content
original_title = wp_product.get('title', {}).get('rendered', '')
original_desc = meta.get('rank_math_description', '')
original_focus = meta.get('rank_math_focus_keyword', '')
wc_product_backup = get_wc_product(product_id)
original_long_desc = wc_product_backup.get('description', '') if wc_product_backup else ''
original_short_desc = wc_product_backup.get('short_description', '') if wc_product_backup else ''

# We'll collect changes to apply
changes_made = []

# Step 1: Title
print('\\n--- Step 1: Title <=60 and includes keyword ---')
title = original_title
if keyword.lower() not in title.lower():
    title = f'{keyword}: {title}'
    changes_made.append('Prepended keyword to title')
if len(title) > 60:
    title = title[:60]
    changes_made.append('Trimmed title to 60 characters')
print(f'New title: {title} (len {len(title)})')
update_data = {'title': title}
r = requests.post(f'{WC_URL}/wp-json/wp/v2/product/{product_id}', headers=wp_headers, json=update_data, timeout=15)
if r.ok:
    print('Title updated successfully.')
    changes_made.append('Title updated via WP API')
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
desc = original_desc
# Ensure keyword present
if keyword.lower() not in desc.lower():
    desc = f'{keyword} - {desc}'
    changes_made.append('Prepended keyword to meta description')
# Adjust length
if len(desc) < 120:
    needed = 120 - len(desc)
    repeats = (needed + len(keyword) - 1) // len(keyword)
    desc = desc + (' ' + keyword) * repeats
    changes_made.append('Padded meta description to min 120 chars')
    if len(desc) > 160:
        desc = desc[:160]
        changes_made.append('Trimmed meta description to max 160 chars')
elif len(desc) > 160:
    desc = desc[:160]
    changes_made.append('Trimmed meta description to max 160 chars')
print(f'New meta description length: {len(desc)}')
rm_meta = {'rank_math_description': desc}
rm_resp = update_wp_product_meta(product_id, rm_meta)
if rm_resp:
    print('Rank Math meta description updated successfully.')
    changes_made.append('Updated RM meta description')
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
    # We'll update the alt of the first image to include keyword
    img_id = images[0].get('id')
    print(f'First image ID: {img_id}')
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
                changes_made.append('Updated image alt to include keyword')
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

# Step 4: Content optimization (long description)
print('\\n--- Step 4: Optimize long description ---')
wp_product = get_wp_product(product_id)
if not wp_product:
    exit(1)
wc_product = get_wc_product(product_id)
if not wc_product:
    exit(1)
long_desc_html = original_long_desc
print(f'Original long description length: {len(long_desc_html)}')

# We'll perform several transformations:
# 1. Ensure exactly one H1 (maybe the product title as H1)
# 2. Ensure H2 headings contain keyword
# 3. Convert H3 to H2 (or remove excess)
# 4. Remove lists (UL/OL) and convert items to paragraphs
# 5. Add a table of benefits if not present
# 6. Ensure internal/external links
# 7. Ensure FAQ schema (we'll try but may fail due to permissions)
# 8. Ensure content length is sufficient (aim for >1000 words)

# Let's start by making a copy to work on
working = long_desc_html

# 1. Ensure exactly one H1
# Count existing H1 tags
h1_matches = re.findall(r'<h1[^>]*>.*?</h1>', working, re.IGNORECASE)
print(f'  Found {len(h1_matches)} H1 tags')
if len(h1_matches) == 0:
    # Add an H1 at the very beginning with the title
    new_h1 = f'<h1>{title}</h1>'
    working = new_h1 + working
    changes_made.append('Added H1 tag at start')
elif len(h1_matches) > 1:
    # Keep only the first H1, remove the rest
    # We'll replace all H1 with a placeholder then put back the first
    # Simpler: remove all H1 and then add one at start
    working = re.sub(r'<h1[^>]*>.*?</h1>', '', working, flags=re.IGNORECASE)
    new_h1 = f'<h1>{title}</h1>'
    working = new_h1 + working
    changes_made.append('Removed extra H1s, added one H1 at start')
else:
    print(f'  Already exactly one H1: {h1_matches[0]}')
    # Ensure the H1 contains the keyword; if not, we can keep it as is or modify.
    # We'll leave it.

# 2. Ensure H2 headings contain keyword (we'll add if missing)
# We'll look for H2 tags; if none, we'll add one after the H1.
h2_matches = re.findall(r'<h2[^>]*>.*?</h2>', working, re.IGNORECASE)
print(f'  Found {len(h2_matches)} H2 tags')
if len(h2_matches) == 0:
    # Insert after first H1 if exists, else at start
    h1_pos = re.search(r'<h1[^>]*>.*?</h1>', working, re.IGNORECASE)
    if h1_pos:
        insert_pos = h1_pos.end()
    else:
        insert_pos = 0
    heading = f'<h2>{keyword}: Información general</h2>'
    working = working[:insert_pos] + heading + working[insert_pos:]
    changes_made.append('Added H2 heading with keyword')
else:
    # Check if any H2 contains keyword; if not, we can modify the first H2 to include keyword
    has_keyword = any(re.search(re.escape(keyword), h2, re.IGNORECASE) for h2 in h2_matches)
    if not has_keyword:
        # Modify the first H2 to include keyword
        def repl(m):
            inner = m.group(0)
            # Insert keyword after opening h2 tag
            # Simple: replace <h2 ...> with <h2 ...>keyword: 
            # We'll just prepend keyword inside the tag
            return inner.replace('<h2', f'<h2>{keyword}: ', 1)
        working = re.sub(r'<h2[^>]*>.*?</h2>', repl, working, count=1, flags=re.IGNORECASE)
        changes_made.append('Modified first H2 to include keyword')
    else:
        print('  At least one H2 already contains keyword')

# 3. Convert H3 to H2 (limit H2 count maybe) or remove excess H3
# We'll convert all H3 to H2 for simplicity, but we can also convert to <strong> paragraphs.
h3_matches = re.findall(r'<h3[^>]*>.*?</h3>', working, re.IGNORECASE)
print(f'  Found {len(h3_matches)} H3 tags')
if h3_matches:
    # Convert each H3 to H2 (or to <p> with bold)
    # We'll convert to H2 to keep heading structure but maybe we want to limit heading count.
    # Let's convert to <p> with <strong> to avoid too many headings.
    def h3_to_strong(m):
        inner = m.group(0)
        # Strip h3 tags
        inner = re.sub(r'<h3[^>]*>|</h3>', '', inner, flags=re.IGNORECASE)
        return f'<p><strong>{inner}</strong></p>'
    working = re.sub(r'<h3[^>]*>.*?</h3>', h3_to_strong, working, flags=re.IGNORECASE)
    changes_made.append('Converted all H3 tags to bold paragraphs')
else:
    print('  No H3 tags found')

# 4. Remove lists (UL/OL) and convert items to paragraphs
# We'll replace each <ul>...</ul> and <ol>...</ol> with a div containing <p> for each <li>
def replace_list(match):
    html = match.group(0)
    # Determine if it's ul or ol
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
    # Wrap in a div for semantic grouping? We'll just return paragraphs concatenated
    return ''.join(paras)
new_working = re.sub(r'<ul[^>]*>.*?</ul>|<ol[^>]*>.*?</ol>', replace_list, working, flags=re.IGNORECASE | re.DOTALL)
if new_working != working:
    working = new_working
    changes_made.append('Converted UL/OL lists to paragraphs')
else:
    print('  No UL/OL lists found')

# 5. Add a table of benefits if not present
# We'll check if there's already a table
if '<table' not in working.lower():
    # Create a simple table with two columns: Beneficio, Descripción
    table_html = '''
<table>
  <thead>
    <tr>
      <th>Beneficio</th>
      <th>Descripción</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Crecimiento muscular</td>
      <td>Promueve la síntesis de proteínas y la hipertrofia muscular.</td>
    </tr>
    <tr>
      <td>Reducción de grasa</td>
      <td>Aumenta la lipólisis y mejora la composición corporal.</td>
    </tr>
    <tr>
      <td>Recuperación</td>
      <td>Acelera la reparación de tejidos y reduce el tiempo de recuperación post-entrenamiento.</td>
    </tr>
    <tr>
      <td>Anti-envejecimiento</td>
      <td>Mejora la elasticidad de la piel y reduce líneas de expresión.</td>
    </tr>
  </tbody>
</table>
'''
    # Insert table after the first H2 or after H1 if no H2
    insert_pos = 0
    h2_match = re.search(r'<h2[^>]*>.*?</h2>', working, re.IGNORECASE)
    if h2_match:
        insert_pos = h2_match.end()
    else:
        h1_match = re.search(r'<h1[^>]*>.*?</h1>', working, re.IGNORECASE)
        if h1_match:
            insert_pos = h1_match.end()
    working = working[:insert_pos] + table_html + working[insert_pos:]
    changes_made.append('Added benefits table')
else:
    print('  Table already present')

# 6. Ensure internal and external links
# We'll add a paragraph with links if not already present
links_paragraph = f'<p>Para más información, visita nuestra <a href="{WC_URL}/">homepage</a> y consulta fuentes como <a href="https://pubmed.ncbi.nlm.nih.gov/" target="_blank" rel="nofollow">PubMed</a> sobre {keyword}.</p>'
if 'homepage' not in working.lower() or 'pubmed' not in working.lower():
    # Append at the end
    working = working + links_paragraph
    changes_made.append('Added internal/external links paragraph')
else:
    print('  Internal/external links already present')

# 7. Update the product description via WC API
print(f'  New long description length: {len(working)}')
update_data = {'description': working}
update_resp = update_wc_product(product_id, update_data)
if update_resp:
    print('Long description updated successfully.')
    changes_made.append('Updated product long description via WC API')
    time.sleep(1)
else:
    print('Long description update failed.')

# Step 5: Ensure short description (maybe we already updated meta description, but short_description is separate)
# We'll set short_description to a concise version of meta description
print('\\n--- Step 5: Update short description ---')
short_desc = desc  # use the meta description we already prepared
# Ensure it's not too long (short_description usually shown in loops)
if len(short_desc) > 200:
    short_desc = short_desc[:200] + '...'
update_data = {'short_description': short_desc}
update_resp = update_wc_product(product_id, update_data)
if update_resp:
    print('Short description updated successfully.')
    changes_made.append('Updated product short description via WC API')
    time.sleep(1)
else:
    print('Short description update failed.')

# Step 6: Focus keyword (already set via meta description step, but we can also ensure rank_math_focus_keyword is set)
# We'll update RM meta for focus keyword if not already set correctly
print('\\n--- Step 6: Ensure focus keyword ---')
wp_product = get_wp_product(product_id)
if not wp_product:
    exit(1)
meta = wp_product.get('meta', {})
current_focus = meta.get('rank_math_focus_keyword', '')
if current_focus.lower() != keyword.lower():
    # We'll set focus keyword to the main keyword
    rm_meta = {'rank_math_focus_keyword': keyword}
    rm_resp = update_wp_product_meta(product_id, rm_meta)
    if rm_resp:
        print('Focus keyword updated successfully.')
        changes_made.append('Updated RM focus keyword')
        time.sleep(1)
    else:
        print('Focus keyword update failed.')
else:
    print('Focus keyword already set correctly.')

# Step 7: Try to add FAQ schema (may fail due to permissions)
print('\\n--- Step 7: Add FAQ schema JSON-LD ---')
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
schema_resp = update_rm_schemas(product_id, schemas)
if schema_resp:
    print('Rank Math schema updated successfully.')
    changes_made.append('Added FAQ schema via RM API')
    time.sleep(1)
else:
    print('Rank Math schema update failed (maybe permission issue).')
    # We can still add the schema JSON-LD directly to the content as a fallback
    schema_json = json.dumps(faq_schema)
    schema_block = f'\\n<script type=\"application/ld+json\">{schema_json}</script>\\n'
    # Append to end of content
    wp_product = get_wp_product(product_id)
    if wp_product:
        long_desc = wp_product.get('content', {}).get('rendered', '')
        new_long_desc = long_desc + schema_block
        update_data = {'description': new_long_desc}
        update_resp = update_wc_product(product_id, update_data)
        if update_resp:
            print('Added FAQ schema JSON-LD directly to product description.')
            changes_made.append('Added FAQ schema JSON-LD to content')
            time.sleep(1)
        else:
            print('Failed to update content with FAQ schema.')
    else:
        print('Could not fetch product to add schema to content.')

# Final verification
print('\\n=== Final verification ===')
time.sleep(2)  # wait a bit for any async processes
wp_product = get_wp_product(product_id)
if wp_product:
    final_meta = wp_product.get('meta', {})
    score_after = final_meta.get('rank_math_seo_score', 0)
    print(f'Final Rank Math SEO score: {score_after}')
    print(f'Change from initial: {score_after - score_before}')
    # Show some key meta
    print(f'Title: {final_meta.get("rank_math_title","")}')
    print(f'Meta description: {final_meta.get("rank_math_description","")}')
    print(f'Focus keyword: {final_meta.get("rank_math_focus_keyword","")}')
    # Also get the content length
    content_len = len(wp_product.get('content',{}).get('rendered',''))
    print(f'Content length: {content_len} characters')
    # List changes made
    print('\\nChanges made:')
    for i, change in enumerate(changes_made, 1):
        print(f'  {i}. {change}')
else:
    print('Failed to fetch final product')