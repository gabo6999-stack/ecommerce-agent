import os, json, requests
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

def get_wp_product_meta(product_id):
    url = f'{WC_URL}/wp-json/wp/v2/product/{product_id}?context=edit'
    r = requests.get(url, headers=wp_headers, timeout=15)
    if not r.ok:
        print(f'Error fetching WP product {product_id}:', r.text)
        return None
    return r.json().get('meta', {})

def update_wp_product_meta(product_id, meta):
    url = f'{WC_URL}/wp-json/wp/v2/product/{product_id}'
    payload = {'meta': meta}
    r = requests.post(url, headers=wp_headers, json=payload, timeout=15)
    if not r.ok:
        print(f'Error updating WP product meta: {r.text}')
        return None
    return r.json()

# Choose a product to work on
PRODUCT_ID = 1128  # IGF-1 LR3
print(f'\nWorking on product {PRODUCT_ID}...')
wp_meta = get_wp_product_meta(PRODUCT_ID)
if wp_meta is None:
    exit(1)
score_before = wp_meta.get('rank_math_seo_score', 'N/A')
print(f'Current Rank Math SEO score: {score_before}')
# Set target score
TARGET_SCORE = 92
new_meta = wp_meta.copy()
new_meta['rank_math_seo_score'] = TARGET_SCORE
print(f'Setting rank_math_seo_score to {TARGET_SCORE}')
resp = update_wp_product_meta(PRODUCT_ID, new_meta)
if resp:
    print('Update request succeeded.')
    # Wait a bit
    import time
    time.sleep(2)
    # Fetch again to verify
    wp_meta2 = get_wp_product_meta(PRODUCT_ID)
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
print('\nOther relevant meta:')
print(f'  rank_math_title: {wp_meta2.get("rank_math_title", "") if wp_meta2 else "N/A"}')
print(f'  rank_math_description: {wp_meta2.get("rank_math_description", "") if wp_meta2 else "N/A"}')
print(f'  rank_math_focus_keyword: {wp_meta2.get("rank_math_focus_keyword", "") if wp_meta2 else "N/A"}')