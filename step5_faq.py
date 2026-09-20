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
post_id = 2521
print(f'Fetching post {post_id}...')
post = get_post(post_id)
if not post:
    exit(1)
content = post.get('content', {}).get('rendered', '')
title = post.get('title', {}).get('rendered', '')
excerpt = post.get('excerpt', {}).get('rendered', '')
keyword = 'selank'
# Step 5: Add FAQ schema JSON-LD
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
# Check if schema already present (simple check)
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
        # Verify
        updated = get_post(post_id)
        if updated:
            updated_content = updated.get('content', {}).get('rendered', '')
            if 'application/ld+json' in updated_content and '"@type": "FAQPage"' in updated_content:
                print('Verified: FAQ schema present in content.')
            else:
                print('Warning: FAQ schema not found in updated content.')
        else:
            print('Failed to verify update.')
    else:
        print('Post update failed.')