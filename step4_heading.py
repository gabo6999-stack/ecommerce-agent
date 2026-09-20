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
# Step 4: Add an H2 heading with the keyword
# Check if there's already an H2 containing the keyword (case-insensitive)
import re
# Simple check for <h2>...selank...</h2>
pattern = re.compile(r'<h2[^>]*>.*?' + re.escape(keyword) + r'.*?</h2>', re.IGNORECASE)
if pattern.search(content):
    print(f'Found an H2 containing keyword "{keyword}". Step 4 already satisfied.')
else:
    print(f'No H2 containing keyword "{keyword}" found. Adding one.')
    # We'll add an H2 heading after any existing image tag at the start, or at the beginning.
    heading = f'<h2>{keyword.capitalize()}: Benefits, Dosage, and Research</h2>'
    # Find where to insert: after the first image tag if present, else at start.
    # We'll just prepend for simplicity.
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
        # Verify
        updated = get_post(post_id)
        if updated:
            updated_content = updated.get('content', {}).get('rendered', '')
            if pattern.search(updated_content):
                print('Verified: H2 with keyword present in content.')
            else:
                print('Warning: H2 with keyword not found in updated content.')
        else:
            print('Failed to verify update.')
    else:
        print('Post update failed.')