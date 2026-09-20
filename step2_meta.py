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
meta = post.get('meta', {})
desc = meta.get('rank_math_description', '')
print(f'Current meta description: {desc}')
print(f'Length: {len(desc)}')
keyword = 'selank'
# Step 2: Ensure length between 120 and 160 characters
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
    # Adjust description
    if len(desc) < 120:
        # Pad by repeating the keyword until reaching at least 120, then trim to 160
        needed = 120 - len(desc)
        repeats = (needed + len(keyword) - 1) // len(keyword)  # ceiling division
        desc = desc + (' ' + keyword) * repeats
        # Now trim to 160 if exceeded
        if len(desc) > 160:
            desc = desc[:160]
    else:  # len(desc) > 160
        desc = desc[:160]
    print(f'New meta description: {desc}')
    print(f'Length: {len(desc)}')
    # Update via Rank Math meta endpoint
    url = f'{WC_URL}/wp-json/rankmath/v1/updateMeta'
    payload = {
        'objectID': post_id,
        'objectType': 'post',
        'meta': {
            'rank_math_description': desc
        }
    }
    r = requests.post(url, headers=headers, json=payload, timeout=20)
    if not r.ok:
        print(f'Error updating RM meta: {r.text}')
    else:
        print('Rank Math meta description updated successfully.')
        # Verify by fetching again
        updated = get_post(post_id)
        if updated:
            updated_meta = updated.get('meta', {})
            updated_desc = updated_meta.get('rank_math_description', '')
            print(f'Verified meta description: {updated_desc}')
            print(f'Length: {len(updated_desc)}')
        else:
            print('Failed to verify update.')