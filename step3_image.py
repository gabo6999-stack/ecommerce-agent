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
# Step 3: Add an image with alt text containing keyword
# We'll use an external image URL that is likely to work
image_url = 'https://via.placeholder.com/800x600.png?text=Selank+Peptide'
alt_text = f'{keyword.capitalize()} molecule'
img_tag = f'<p><img src="{image_url}" alt="{alt_text}" style="max-width:100%;height:auto;"></p>'
# Prepend image tag to content
new_content = img_tag + content
print(f'Image tag to be added: {img_tag}')
print(f'Original content length: {len(content)}')
print(f'New content length: {len(new_content)}')
# Update post
update_data = {
    'title': title,
    'content': new_content
}
if excerpt:
    update_data['excerpt'] = excerpt
upd_resp = update_post(post_id, update_data)
if upd_resp:
    print('Post updated with image successfully.')
    # Verify
    updated = get_post(post_id)
    if updated:
        updated_content = updated.get('content', {}).get('rendered', '')
        if image_url in updated_content and alt_text in updated_content:
            print('Verified: image tag present in content.')
        else:
            print('Warning: image tag not found in updated content.')
    else:
        print('Failed to verify update.')
else:
    print('Post update failed.')