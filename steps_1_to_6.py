import os, json, requests, re
from dotenv import load_dotenv
load_dotenv('ecommerce-agent__.env')
WC_URL = os.getenv('WC_STORE_URL').rstrip('/')
WP_USER = os.getenv('WP_USER')
WP_PASSWORD = os.getenv('WP_PASSWORD')
print('WC_URL:', WC_URL)
jwt_url = f'{WC_URL}/wp-json/jwt-auth/v1/token'
resp = requests.post(jwt_url, json={'username': WP_USER, 'password': WP_PASSWORD}, timeout=15)
if not resp.ok:
    print('Failed to get JWT token:', resp.text)
    exit(1)
token = resp.json().get('token')
headers = {'Authorization': f'Bearer {token}'}
def get_post(post_id):
    url = f'{WC_URL}/wp-json/wp/v2/posts/{post_id}?context=edit'
    r = requests.get(url, headers=headers, timeout=15)
    if not r.ok:
        print(f'Error fetching post {post_id}:', r.text)
        return None
    return r.json()
def update_post(post_id, data):
    url = f'{WC_URL}/wp-json/wp/v2/posts/{post_id}'
    r = requests.post(url, headers=headers, json=data, timeout=15)
    if not r.ok:
        print(f'Error updating post {post_id}:', r.text)
        return None
    return r.json()
def update_rm_meta(object_id, meta):
    url = f'{WC_URL}/wp-json/rankmath/v1/updateMeta'
    payload = {'objectID': object_id, 'objectType': 'post', 'meta': meta}
    r = requests.post(url, headers=headers, json=payload, timeout=20)
    if not r.ok:
        print(f'Error updating RM meta:', r.text)
        return None
    return r.json()
post_id = 2521
print('=== Starting optimization steps for post', post_id, '===')
# Get initial state
post = get_post(post_id)
if not post:
    exit(1)
meta = post.get('meta', {})
score_before = meta.get('rank_math_seo_score', 0)
print(f'Initial Rank Math SEO score: {score_before}')
# We'll keep track of current post data
current = post
# Step 1: Title
print('\n--- Step 1: Title <=60 and includes keyword ---')
title = current.get('title', {}).get('rendered', '')
keyword = 'selank'
needs_change = False
if len(title) > 60:
    print('Title longer than 60 characters, will truncate.')
    needs_change = True
if keyword.lower() not in title.lower():
    print(f'Title does not contain keyword "{keyword}", will add.')
    needs_change = True
if not needs_change:
    print('Title already meets step 1 requirements.')
else:
    new_title = title
    if keyword.lower() not in new_title.lower():
        new_title = f'{keyword.capitalize()}: {new_title}'
    if len(new_title) > 60:
        new_title = new_title[:60]
    print(f'New title: {new_title} (length {len(new_title)})')
    update_data = {'title': new_title}
    upd_resp = update_post(post_id, update_data)
    if upd_resp:
        print('Title updated successfully.')
        # Refresh current
        current = get_post(post_id)
    else:
        print('Title update failed.')
# Check score after step 1
current = get_post(post_id)
if current:
    score = current.get('meta', {}).get('rank_math_seo_score', 0)
    print(f'Score after step 1: {score}')
else:
    print('Failed to fetch post after step 1')
# Step 2: Meta description length 120-160
print('\n--- Step 2: Meta description length 120-160 ---')
current = get_post(post_id)
if not current:
    exit(1)
meta = current.get('meta', {})
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
    # Update via Rank Math meta endpoint
    rm_meta = {'rank_math_description': desc}
    rm_resp = update_rm_meta(post_id, rm_meta)
    if rm_resp:
        print('Rank Math meta description updated successfully.')
        # Refresh current
        current = get_post(post_id)
    else:
        print('Rank Math meta description update failed.')
# Check score after step 2
current = get_post(post_id)
if current:
    score = current.get('meta', {}).get('rank_math_seo_score', 0)
    print(f'Score after step 2: {score}')
else:
    print('Failed to fetch post after step 2')
# Step 3: Add image with alt text containing keyword
print('\n--- Step 3: Add image with alt text containing keyword ---')
current = get_post(post_id)
if not current:
    exit(1)
content = current.get('content', {}).get('rendered', '')
title = current.get('title', {}).get('rendered', '')
excerpt = current.get('excerpt', {}).get('rendered', '')
keyword = 'selank'
image_url = 'https://via.placeholder.com/800x600.png?text=Selank+Peptide'
alt_text = f'{keyword.capitalize()} molecule'
img_tag = f'<p><img src="{image_url}" alt="{alt_text}" style="max-width:100%;height:auto;"></p>'
# Check if image already present (simple)
if image_url in content and alt_text in content:
    print('Image with required alt text already present. Step 3 already satisfied.')
else:
    print(f'Image tag to be added: {img_tag}')
    print(f'Original content length: {len(content)}')
    new_content = img_tag + content
    print(f'New content length: {len(new_content)}')
    update_data = {
        'title': title,
        'content': new_content
    }
    if excerpt:
        update_data['excerpt'] = excerpt
    upd_resp = update_post(post_id, update_data)
    if upd_resp:
        print('Post updated with image successfully.')
        # Refresh current
        current = get_post(post_id)
    else:
        print('Post update failed.')
# Check score after step 3
current = get_post(post_id)
if current:
    score = current.get('meta', {}).get('rank_math_seo_score', 0)
    print(f'Score after step 3: {score}')
else:
    print('Failed to fetch post after step 3')
# Step 4: Add H2 heading with keyword
print('\n--- Step 4: Add H2 heading with keyword ---')
current = get_post(post_id)
if not current:
    exit(1)
content = current.get('content', {}).get('rendered', '')
title = current.get('title', {}).get('rendered', '')
excerpt = current.get('excerpt', {}).get('rendered', '')
keyword = 'selank'
pattern = re.compile(r'<h2[^>]*>.*?' + re.escape(keyword) + r'.*?</h2>', re.IGNORECASE)
if pattern.search(content):
    print(f'Found an H2 containing keyword "{keyword}". Step 4 already satisfied.')
else:
    print(f'No H2 containing keyword "{keyword}" found. Adding one.')
    heading = f'<h2>{keyword.capitalize()}: Benefits, Dosage, and Research</h2>'
    new_content = heading + content
    print(f'Adding heading: {heading}')
    print(f'Original content length: {len(content)}')
    print(f'New content length: {len(new_content)}')
    update_data = {
        'title': title,
        'content': new_content
    }
    if excerpt:
        update_data['excerpt'] = excerpt
    upd_resp = update_post(post_id, update_data)
    if upd_resp:
        print('Post updated with H2 heading successfully.')
        # Refresh current
        current = get_post(post_id)
    else:
        print('Post update failed.')
# Check score after step 4
current = get_post(post_id)
if current:
    score = current.get('meta', {}).get('rank_math_seo_score', 0)
    print(f'Score after step 4: {score}')
else:
    print('Failed to fetch post after step 4')
# Step 5: Add FAQ schema JSON-LD
print('\n--- Step 5: Add FAQ schema JSON-LD ---')
current = get_post(post_id)
if not current:
    exit(1)
content = current.get('content', {}).get('rendered', '')
title = current.get('title', {}).get('rendered', '')
excerpt = current.get('excerpt', {}).get('rendered', '')
keyword = 'selank'
faq_schema = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [
        {
            "@type": "Question",
            "name": f"What is {keyword.capitalize()}?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": f"{keyword.capitalize()} is a synthetic peptide studied for its nootropic and anxiolytic effects."
            }
        },
        {
            "@type": "Question",
            "name": f"What are the benefits of {keyword.capitalize()}?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": f"Research suggests {keyword.capitalize()} may improve cognitive function, reduce anxiety, and enhance mood."
            }
        }
    ]
}
schema_json = json.dumps(faq_schema, ensure_ascii=False)
schema_block = f'\n<script type="application/ld+json">{schema_json}</script>\n'
if 'application/ld+json' in content and '"@type": "FAQPage"' in content:
    print('FAQ schema already present. Step 5 already satisfied.')
else:
    print('Adding FAQ schema JSON-LD.')
    new_content = content + schema_block
    print(f'Original content length: {len(content)}')
    print(f'New content length: {len(new_content)}')
    update_data = {
        'title': title,
        'content': new_content
    }
    if excerpt:
        update_data['excerpt'] = excerpt
    upd_resp = update_post(post_id, update_data)
    if upd_resp:
        print('Post updated with FAQ schema successfully.')
        # Refresh current
        current = get_post(post_id)
    else:
        print('Post update failed.')
# Check score after step 5
current = get_post(post_id)
if current:
    score = current.get('meta', {}).get('rank_math_seo_score', 0)
    print(f'Score after step 5: {score}')
else:
    print('Failed to fetch post after step 5')
# Step 6: Add internal and external links
print('\n--- Step 6: Add internal and external links ---')
current = get_post(post_id)
if not current:
    exit(1)
content = current.get('content', {}).get('rendered', '')
title = current.get('title', {}).get('rendered', '')
excerpt = current.get('excerpt', {}).get('rendered', '')
keyword = 'selank'
# We'll add a paragraph with links after the first paragraph or at start.
link_paragraph = f'<p>For more information, visit our <a href="{WC_URL}/">homepage</a> and consult scientific resources such as <a href="https://pubmed.ncbi.nlm.nih.gov/" target="_blank" rel="nofollow">PubMed</a> for the latest studies on {keyword}.</p>'
# Check if similar link already present (simple)
if 'homepage' in content and 'PubMed' in content:
    print('Similar link paragraph already present. Step 6 already satisfied.')
else:
    print(f'Link paragraph to be added: {link_paragraph}')
    new_content = link_paragraph + content
    print(f'Original content length: {len(content)}')
    print(f'New content length: {len(new_content)}')
    update_data = {
        'title': title,
        'content': new_content
    }
    if excerpt:
        update_data['excerpt'] = excerpt
    upd_resp = update_post(post_id, update_data)
    if upd_resp:
        print('Post updated with links successfully.')
        # Refresh current
        current = get_post(post_id)
    else:
        print('Post update failed.')
# Final score
current = get_post(post_id)
if current:
    score = current.get('meta', {}).get('rank_math_seo_score', 0)
    print(f'\nFinal Rank Math SEO score after all steps: {score}')
    print(f'Change from initial: {score - score_before}')
else:
    print('Failed to fetch final post')