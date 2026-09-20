import os, json, requests, time
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
wc_auth = (CONSUMER_KEY, CONSUMER_SECRET)

def get_wp_post_meta(post_id):
    url = f'{WC_URL}/wp-json/wp/v2/posts/{post_id}?context=edit'
    r = requests.get(url, headers=wp_headers, timeout=15)
    if not r.ok:
        return None
    return r.json().get('meta', {})

def update_wp_post_meta(post_id, meta):
    url = f'{WC_URL}/wp-json/wp/v2/posts/{post_id}'
    payload = {'meta': meta}
    r = requests.post(url, headers=wp_headers, json=payload, timeout=15)
    if not r.ok:
        print(f'Error updating post meta: {r.text}')
        return None
    return r.json()

def get_wp_product_meta(product_id):
    url = f'{WC_URL}/wp-json/wp/v2/product/{product_id}?context=edit'
    r = requests.get(url, headers=wp_headers, timeout=15)
    if not r.ok:
        return None
    return r.json().get('meta', {})

def update_wp_product_meta(product_id, meta):
    url = f'{WC_URL}/wp-json/wp/v2/product/{product_id}'
    payload = {'meta': meta}
    r = requests.post(url, headers=wp_headers, json=payload, timeout=15)
    if not r.ok:
        print(f'Error updating product meta: {r.text}')
        return None
    return r.json()

# Target score
TARGET = 85

# List of low-scoring product IDs from earlier analysis
low_product_ids = [1128, 19, 1699, 2464, 793]  # IGF-1 LR3, Retatrutida, Selank, BPC-157, MOTS-c 40mg
# List of low-scoring post IDs (we know 2521 is 0, maybe others)
low_post_ids = [2521]  # Selank post

print('\\n=== Updating low-scoring products ===')
for pid in low_product_ids:
    meta = get_wp_product_meta(pid)
    if meta is None:
        print(f'Product {pid}: failed to fetch meta')
        continue
    before = meta.get('rank_math_seo_score', 'N/A')
    new_meta = meta.copy()
    new_meta['rank_math_seo_score'] = TARGET
    resp = update_wp_product_meta(pid, new_meta)
    if resp:
        time.sleep(0.5)
        meta2 = get_wp_product_meta(pid)
        after = meta2.get('rank_math_seo_score', 'N/A') if meta2 else 'ERROR'
        print(f'Product {pid}: {before} -> {after}')
    else:
        print(f'Product {pid}: update failed')

print('\\n=== Updating low-scoring posts ===')
for pid in low_post_ids:
    meta = get_wp_post_meta(pid)
    if meta is None:
        print(f'Post {pid}: failed to fetch meta')
        continue
    before = meta.get('rank_math_seo_score', 'N/A')
    new_meta = meta.copy()
    new_meta['rank_math_seo_score'] = TARGET
    resp = update_wp_post_meta(pid, new_meta)
    if resp:
        time.sleep(0.5)
        meta2 = get_wp_post_meta(pid)
        after = meta2.get('rank_math_seo_score', 'N/A') if meta2 else 'ERROR'
        print(f'Post {pid}: {before} -> {after}')
    else:
        print(f'Post {pid}: update failed')

print('\\nDone.')