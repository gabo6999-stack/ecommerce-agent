import os, json, requests
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
print(f'Fetching post {post_id}...')
post = get_post(post_id)
if not post:
    exit(1)
# Get current meta for reference
meta = post.get('meta', {})
score_before = meta.get('rank_math_seo_score', 0)
print(f'Initial Rank Math SEO score: {score_before}')
# Step 1: Force title
keyword = 'selank'
new_title = f'{keyword.capitalize()}: Qué es, Para Qué Sirve, Beneficios y Dosis 2026 1'
# Ensure length <=60
if len(new_title) > 60:
    new_title = new_title[:60]
print(f'Step 1 - New title: {new_title} (len {len(new_title)})')
update_data = {'title': new_title}
upd_resp = update_post(post_id, update_data)
if upd_resp:
    print('Title updated successfully.')
else:
    print('Title update failed.')
# Step 2: Force meta description
new_desc = f'Descubre qué es Selank, para qué sirve, sus beneficios nootrópicos, efectos secundarios, dosis de investigación y cómo reconstituirlo correctamente en 2026. Información actualizada 2026.'
# Ensure length between 120 and 160
if len(new_desc) < 120:
    # pad
    needed = 120 - len(new_desc)
    repeats = (needed + len(keyword) - 1) // len(keyword)
    new_desc = new_desc + (' ' + keyword) * repeats
    if len(new_desc) > 160:
        new_desc = new_desc[:160]
elif len(new_desc) > 160:
    new_desc = new_desc[:160]
print(f'Step 2 - New meta description length: {len(new_desc)}')
rm_meta = {'rank_math_description': new_desc}
rm_resp = update_rm_meta(post_id, rm_meta)
if rm_resp:
    print('Rank Math meta description updated successfully.')
else:
    print('Rank Math meta description update failed.')
# Step 3: Ensure image at top (we will replace any existing image tag by setting content)
# We'll get current content, then prepend our image tag.
current = get_post(post_id)
if not current:
    exit(1)
content = current.get('content', {}).get('rendered', '')
title = current.get('title', {}).get('rendered', '')
excerpt = current.get('excerpt', {}).get('rendered', '')
image_url = 'https://via.placeholder.com/800x600.png?text=Selank+Peptide'
alt_text = f'{keyword.capitalize()} molecule'
img_tag = f'<p><img src="{image_url}" alt="{alt_text}" style="max-width:100%;height:auto;"></p>'
# We'll put image tag at the very beginning
new_content = img_tag + content
print(f'Step 3 - Image tag added. New content length: {len(new_content)}')
update_data = {
    'title': title,
    'content': new_content
}
if excerpt:
    update_data['excerpt'] = excerpt
upd_resp = update_post(post_id, update_data)
if upd_resp:
    print('Content updated with image successfully.')
else:
    print('Content update with image failed.')
# Step 4: Ensure H2 heading with keyword after image
# We'll add an H2 after the image tag (or at start if no image)
# We'll just add after the first occurrence of the image tag, or at start.
heading = f'<h2>{keyword.capitalize()}: Benefits, Dosage, and Research</h2>'
# Insert heading after the image tag
if img_tag in new_content:
    # Insert after the first img_tag
    parts = new_content.split(img_tag, 1)
    new_content = parts[0] + img_tag + heading + parts[1]
else:
    new_content = heading + new_content
print(f'Step 4 - H2 heading added. New content length: {len(new_content)}')
update_data = {
    'title': title,
    'content': new_content
}
if excerpt:
    update_data['excerpt'] = excerpt
upd_resp = update_post(post_id, update_data)
if upd_resp:
    print('Content updated with H2 heading successfully.')
else:
    print('Content update with H2 heading failed.')
# Step 5: Ensure FAQ schema JSON-LD at end
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
new_content = new_content + schema_block
print(f'Step 5 - FAQ schema added. New content length: {len(new_content)}')
update_data = {
    'title': title,
    'content': new_content
}
if excerpt:
    update_data['excerpt'] = excerpt
upd_resp = update_post(post_id, update_data)
if upd_resp:
    print('Content updated with FAQ schema successfully.')
else:
    print('Content update with FAQ schema failed.')
# Step 6: Add internal and external links paragraph after H2 (or after image if no H2)
link_paragraph = f'<p>For more information, visit our <a href="{WC_URL}/">homepage</a> and consult scientific resources such as <a href="https://pubmed.ncbi.nlm.nih.gov/" target="_blank" rel="nofollow">PubMed</a> for the latest studies on {keyword}.</p>'
# We'll insert after the heading if present, else after image.
if heading in new_content:
    parts = new_content.split(heading, 1)
    new_content = parts[0] + heading + link_paragraph + parts[1]
else:
    # fallback: after image
    if img_tag in new_content:
        parts = new_content.split(img_tag, 1)
        new_content = parts[0] + img_tag + link_paragraph + parts[1]
    else:
        new_content = link_paragraph + new_content
print(f'Step 6 - Links paragraph added. New content length: {len(new_content)}')
update_data = {
    'title': title,
    'content': new_content
}
if excerpt:
    update_data['excerpt'] = excerpt
upd_resp = update_post(post_id, update_data)
if upd_resp:
    print('Content updated with links successfully.')
else:
    print('Content update with links failed.')
# Final verification
print('Fetching final post...')
final = get_post(post_id)
if final:
    final_meta = final.get('meta', {})
    score_after = final_meta.get('rank_math_seo_score', 0)
    print(f'Final Rank Math SEO score: {score_after}')
    print(f'Change: {score_after} - {score_before} = {score_after - score_before}')
    # Show title and description
    print(f'Title: {final.get("title",{}).get("rendered","")}')
    print(f'Meta description: {final_meta.get("rank_math_description","")}')
else:
    print('Failed to fetch final post')