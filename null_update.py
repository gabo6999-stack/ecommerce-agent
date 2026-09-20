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
score_before = meta.get('rank_math_seo_score', 0)
print(f'Current Rank Math SEO score: {score_before}')
# Try a null update: just update the title to be the same (or update content to be the same)
# We'll update the content to be exactly the same as fetched (to trigger a possible recalculation)
title = post.get('title', {}).get('rendered', '')
content = post.get('content', {}).get('rendered', '')
excerpt = post.get('excerpt', {}).get('rendered', '')
print(f'Title length: {len(title)}')
print(f'Content length: {len(content)}')
# Update post with same content
update_data = {
    'title': title,
    'content': content
}
if excerpt:
    update_data['excerpt'] = excerpt
upd_resp = update_post(post_id, update_data)
if upd_resp:
    print('Post update successful')
else:
    print('Post update failed')
# Fetch again to see if score changed
print('Fetching updated post...')
post2 = get_post(post_id)
if post2:
    meta2 = post2.get('meta', {})
    score_after = meta2.get('rank_math_seo_score', 0)
    print(f'Updated Rank Math SEO score: {score_after}')
    print(f'Change: {score_after} - {score_before} = {score_after - score_before}')
else:
    print('Failed to fetch updated post')