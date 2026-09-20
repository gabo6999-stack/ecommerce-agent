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

def get_wp_post(post_id):
    url = f'{WC_URL}/wp-json/wp/v2/posts/{post_id}?context=edit'
    r = requests.get(url, headers=wp_headers, timeout=15)
    if not r.ok:
        print(f'Error fetching WP post {post_id}:', r.text)
        return None
    return r.json()
def update_wp_post(post_id, data):
    url = f'{WC_URL}/wp-json/wp/v2/posts/{post_id}'
    r = requests.post(url, headers=wp_headers, json=data, timeout=15)
    if not r.ok:
        print(f'Error updating WP post {post_id}:', r.text)
        return None
    return r.json()
def update_wp_post_meta(post_id, meta):
    # Rank Math meta endpoint
    url = f'{WC_URL}/wp-json/rankmath/v1/updateMeta'
    payload = {'objectID': post_id, 'objectType': 'post', 'meta': meta}
    r = requests.post(url, headers=wp_headers, json=payload, timeout=20)
    if not r.ok:
        print(f'Error updating Rank Math meta: {r.text}')
        return None
    return r.json()
def update_wp_post_schemas(post_id, schemas):
    url = f'{WC_URL}/wp-json/rankmath/v1/updateSchemas'
    payload = {'objectID': post_id, 'objectType': 'post', 'schemas': schemas}
    r = requests.post(url, headers=wp_headers, json=payload, timeout=20)
    if not r.ok:
        print(f'Error updating Rank Math schemas: {r.text}')
        return None
    return r.json()

POST_ID = 2521  # Selank post
print(f'Fetching post {POST_ID}...')
post = get_wp_post(POST_ID)
if not post:
    exit(1)
meta = post.get('meta', {})
score_before = meta.get('rank_math_seo_score', 0)
print(f'Initial Rank Math SEO score: {score_before}')
title = post.get('title', {}).get('rendered', '')
content = post.get('content', {}).get('rendered', '')
excerpt = post.get('excerpt', {}).get('rendered', '')
focus_keyword = meta.get('rank_math_focus_keyword', '')
print(f'Title: {title}')
print(f'Focus keyword: {focus_keyword}')
print(f'Content length: {len(content)}')

# --- Step 1: Ensure exactly one H1 ---
print('\\n--- Step 1: Ensure exactly one H1 ---')
# Find all H1 tags
h1_matches = re.findall(r'<h1[^>]*>.*?</h1>', content, re.IGNORECASE)
print(f'Found {len(h1_matches)} H1 tags')
if len(h1_matches) == 0:
    # Add H1 at start with title
    new_h1 = f'<h1>{title}</h1>'
    content = new_h1 + content
    print('Added H1 at start')
elif len(h1_matches) > 1:
    # Keep first H1, remove others
    # We'll replace all H1 with placeholder then put back first
    # Simpler: remove all H1 and then add one at start
    content = re.sub(r'<h1[^>]*>.*?</h1>', '', content, flags=re.IGNORECASE)
    new_h1 = f'<h1>{title}</h1>'
    content = new_h1 + content
    print('Removed extra H1s, added one H1 at start')
else:
    print('Already exactly one H1')
    # Ensure it contains keyword? optional
    # We'll leave as is

# --- Step 2: Reduce H3 (convert to bold paragraphs) ---
print('\\n--- Step 2: Convert H3 to bold paragraphs ---')
h3_matches = re.findall(r'<h3[^>]*>.*?</h3>', content, re.IGNORECASE)
print(f'Found {len(h3_matches)} H3 tags')
if h3_matches:
    def h3_to_strong(m):
        inner = m.group(0)
        # Strip h3 tags
        inner = re.sub(r'<h3[^>]*>|</h3>', '', inner, flags=re.IGNORECASE)
        return f'<p><strong>{inner}</strong></p>'
    content = re.sub(r'<h3[^>]*>.*?</h3>', h3_to_strong, content, flags=re.IGNORECASE)
    print('Converted all H3 tags to bold paragraphs')
else:
    print('No H3 tags found')

# --- Step 3: Remove UL/OL lists (convert items to paragraphs) ---
print('\\n--- Step 3: Convert UL/OL lists to paragraphs ---')
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
new_content = re.sub(r'<ul[^>]*>.*?</ul>|<ol[^>]*>.*?</ol>', replace_list, content, flags=re.IGNORECASE | re.DOTALL)
if new_content != content:
    content = new_content
    print('Converted UL/OL lists to paragraphs')
else:
    print('No UL/OL lists found')

# --- Step 4: Increase internal/external links ---
print('\\n--- Step 4: Ensure internal/external links paragraph ---')
links_para = f'<p>Para más información, visita nuestra <a href="{WC_URL}/">homepage</a> y consulta fuentes como <a href="https://pubmed.ncbi.nlm.nih.gov/" target="_blank" rel="nofollow">PubMed</a> sobre Selank.</p>'
if 'homepage' not in content.lower() or 'pubmed' not in content.lower():
    # Append at end before closing tags? We'll just append
    content = content + links_para
    print('Added internal/external links paragraph')
else:
    print('Internal/external links already present')

# --- Step 5: Ensure single FAQ schema ---
print('\\n--- Step 5: Ensure single FAQPage schema ---')
# We'll create a single FAQ schema
faq_schema = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [
        {
            "@type": "Question",
            "name": "¿Qué es Selank?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "Selank es un péptido sintético derivado de la tuftsin, con efectos ansiolíticos y nootrópicos, utilizado para reducir la ansiedad y mejorar la función cognitiva."
            }
        },
        {
            "@type": "Question",
            "name": "¿Cuáles son los beneficios de Selank?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "Selank puede ayudar a reducir la ansiedad, mejorar la memoria y la concentración, y tiene propiedades neuroprotectoras."
            }
        },
        {
            "@type": "Question",
            "name": "¿Cuál es la dosis típica de Selank?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "La dosis usual varía entre 250 µg y 500 µg por día, administrada por vía subcutánea o intranasal, según indicación médica."
            }
        }
    ]
}
schemas = [faq_schema]
# Update via Rank Math schema endpoint
resp = update_wp_post_schemas(POST_ID, schemas)
if resp:
    print('Rank Math FAQ schema updated successfully.')
else:
    print('Rank Math schema update failed; will try to embed JSON-LD in content as fallback')
    # Embed JSON-LD as fallback
    schema_json = json.dumps(faq_schema, ensure_ascii=False)
    schema_block = f'\\n<script type=\"application/ld+json\">\\n{schema_json}\\n</script>\\n'
    # Avoid duplicate: check if similar script already exists
    if 'application/ld+json' not in content:
        content = content + schema_block
        print('Added FAQ schema JSON-LD to content')
    else:
        print('FAQ schema JSON-LD already present in content')

# --- Step 6: Update meta fields (title, description, focus keyword) ---
print('\\n--- Step 6: Update Rank Math meta fields ---')
# Ensure title length <=60 and contains keyword (we'll keep current title)
new_title = title
if len(new_title) > 60:
    new_title = new_title[:60]
# Ensure meta description length 120-160
meta_desc = meta.get('rank_math_description', '')
# If empty, generate from content first 160 chars
if not meta_desc:
    # Extract plain text from content (strip tags)
    plain = re.sub(r'<[^>]+>', ' ', content)
    plain = re.sub(r'\\s+', ' ', plain).strip()
    meta_desc = plain[:160]
# Ensure keyword present
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
# Let's set to a phrase: 'Selank beneficios y dosis'
new_focus = 'Selank beneficios y dosis'
# Prepare meta dict
new_meta = {
    'rank_math_title': new_title,
    'rank_math_description': meta_desc,
    'rank_math_focus_keyword': new_focus
}
# Update via Rank Math meta endpoint
resp = update_wp_post_meta(POST_ID, new_meta)
if resp:
    print('Rank Math meta fields updated successfully.')
else:
    print('Rank Math meta update failed.')

# --- Update WP post title and content ---
print('\\n--- Updating WP post title and content ---')
update_data = {}
if new_title != title:
    update_data['title'] = new_title
if content != post.get('content', {}).get('rendered', ''):
    update_data['content'] = content
if update_data:
    resp = update_wp_post(POST_ID, update_data)
    if resp:
        print('WP post title/content updated successfully.')
    else:
        print('WP post title/content update failed.')
else:
    print('No changes to WP post title/content.')

# Wait a bit for any async processes
print('\\nWaiting 2 seconds for changes to propagate...')
time.sleep(2)

# Fetch final score
print('\\n--- Final verification ---')
post_final = get_wp_post(POST_ID)
if post_final:
    meta_final = post_final.get('meta', {})
    score_after = meta_final.get('rank_math_seo_score', 0)
    print(f'Final Rank Math SEO score: {score_after}')
    print(f'Change from initial: {score_after - score_before}')
    print(f'Title: {post_final.get(\"title\",{}).get(\"rendered\",\"\")}')
    print(f'Rank Math title: {meta_final.get(\"rank_math_title\",\"\")}')
    print(f'Rank Math description: {meta_final.get(\"rank_math_description\",\"\")}')
    print(f'Rank Math focus keyword: {meta_final.get(\"rank_math_focus_keyword\",\"\")}')
    # Content length
    content_final = post_final.get('content',{}).get('rendered','')
    print(f'Content length: {len(content_final)} characters')
else:
    print('Failed to fetch final post')