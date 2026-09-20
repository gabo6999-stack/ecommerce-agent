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
title = post.get('title', {}).get('rendered', '')
print(f'Current title: {title}')
print(f'Length: {len(title)}')
keyword = 'selank'
# Step 1: Ensure title <=60 and includes keyword (case-insensitive)
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
    # Build new title: ensure keyword present, keep under 60
    # Simple approach: if keyword missing, prepend it; then trim to 60
    new_title = title
    if keyword.lower() not in new_title.lower():
        new_title = f'{keyword.capitalize()}: {new_title}'
    # Trim to 60
    if len(new_title) > 60:
        new_title = new_title[:60]
    print(f'New title: {new_title} (length {len(new_title)})')
    update_data = {'title': new_title}
    upd_resp = update_post(post_id, update_data)
    if upd_resp:
        print('Title updated successfully.')
        # Verify
        updated = get_post(post_id)
        if updated:
            updated_title = updated.get('title', {}).get('rendered', '')
            print(f'Verified title: {updated_title} (len {len(updated_title)})')
        else:
            print('Failed to verify update.')
    else:
        print('Title update failed.')