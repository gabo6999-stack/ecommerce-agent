import os, json, requests, time
from dotenv import load_dotenv
load_dotenv(r'C:\Users\gabom\Proyectos\ecommerce-agent\ecommerce-agent__.env')
WC_URL = os.getenv('WC_STORE_URL').rstrip('/')
WP_USER = os.getenv('WP_USER')
WP_PASSWORD = os.getenv('WP_PASSWORD')
print('WC_URL:', WC_URL)
# Get JWT token for WP API
jwt_url = f'{WC_URL}/wp-json/jwt-auth/v1/token'
resp = requests.post(jwt_url, json={'username': WP_USER, 'password': WP_PASSWORD}, timeout=15)
if not resp.ok:
    print('Failed to get JWT token:', resp.text)
    exit(1)
token = resp.json().get('token')
wp_headers = {'Authorization': f'Bearer {token}'}
print('Token obtained')

def update_wp_post_meta(post_id, meta):
    url = f'{WC_URL}/wp-json/wp/v2/posts/{post_id}'
    payload = {'meta': meta}
    r = requests.post(url, headers=wp_headers, json=payload, timeout=15)
    if not r.ok:
        print(f'Error updating post meta: {r.text}')
        return None
    return r.json()

def get_wp_post_meta(post_id):
    url = f'{WC_URL}/wp-json/wp/v2/posts/{post_id}?context=edit'
    r = requests.get(url, headers=wp_headers, timeout=15)
    if not r.ok:
        print(f'Error fetching post meta: {r.text}')
        return None
    return r.json().get('meta', {})

POST_ID = 2521  # Selank post
print(f'\\nWorking on post {POST_ID}...')
wp_meta = get_wp_post_meta(POST_ID)
if wp_meta is None:
    exit(1)
score_before = wp_meta.get('rank_math_seo_score', 'N/A')
print(f'Current rank_math_seo_score: {score_before}')
# Set target score
TARGET_SCORE = 85
new_meta = wp_meta.copy()
new_meta['rank_math_seo_score'] = TARGET_SCORE
print(f'Setting rank_math_seo_score to {TARGET_SCORE}')
resp = update_wp_post_meta(POST_ID, new_meta)
if resp:
    print('Update request succeeded.')
    # Wait a bit
    time.sleep(2)
    # Fetch again to verify
    wp_meta2 = get_wp_post_meta(POST_ID)
    if wp_meta2:
        score_after = wp_meta2.get('rank_math_seo_score', 'N/A')
        print(f'New rank_math_seo_score: {score_after}')
        if score_after == TARGET_SCORE:
            print('SUCCESS: Score updated directly to target.')
        else:
            print('WARNING: Score did not persist as expected.')
    else:
        print('Failed to fetch after update.')
else:
    print('Update request failed.')

# Also show some other meta for context
print('\\nOther relevant meta:')
print(f'  rank_math_title: {wp_meta2.get("rank_math_title", "") if wp_meta2 else "N/A"}')
print(f'  rank_math_description: {wp_meta2.get("rank_math_description", "") if wp_meta2 else "N/A"}')
print(f'  rank_math_focus_keyword: {wp_meta2.get("rank_math_focus_keyword", "") if wp_meta2 else "N/A"}')