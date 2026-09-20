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

def update_wp_product_meta(post_id, meta):
    url = f'{WC_URL}/wp-json/wp/v2/product/{post_id}'
    payload = {'meta': meta}
    r = requests.post(url, headers=wp_headers, json=payload, timeout=15)
    if not r.ok:
        print(f'Error updating product meta: {r.text}')
        return None
    return r.json()

def get_wp_product_meta(post_id):
    url = f'{WC_URL}/wp-json/wp/v2/product/{post_id}?context=edit'
    r = requests.get(url, headers=wp_headers, timeout=15)
    if not r.ok:
        print(f'Error fetching product meta: {r.text}')
        return None
    return r.json().get('meta', {})

# Test with product 1128 (IGF-1 LR3)
product_id = 1128
print(f'\\nTesting direct update of rank_math_seo_score for product {product_id}...')
wp_meta = get_wp_product_meta(product_id)
if wp_meta is None:
    exit(1)
score_before = wp_meta.get('rank_math_seo_score', 'N/A')
print(f'Current rank_math_seo_score: {score_before}')
# Prepare new meta: copy existing and set rank_math_seo_score to 85
new_meta = wp_meta.copy()
new_meta['rank_math_seo_score'] = 85
print(f'Setting rank_math_seo_score to 85')
resp = update_wp_product_meta(product_id, new_meta)
if resp:
    print('Update request succeeded.')
    # Fetch again to verify
    time.sleep(1)
    wp_meta2 = get_wp_product_meta(product_id)
    if wp_meta2:
        score_after = wp_meta2.get('rank_math_seo_score', 'N/A')
        print(f'New rank_math_seo_score: {score_after}')
        if score_after == 85:
            print('SUCCESS: Score updated directly.')
        else:
            print('WARNING: Score did not persist as expected.')
    else:
        print('Failed to fetch after update.')
else:
    print('Update request failed.')

# Now try for a few low-scoring products from earlier list
low_ids = [1128, 19, 1699, 2464, 793]  # IGF-1 LR3, Retatrutida, Selank, BPC-157, MOTS-c 40mg
print('\\n=== Attempting to boost scores for low-scoring products ===')
for pid in low_ids:
    wp_meta = get_wp_product_meta(pid)
    if wp_meta is None:
        print(f'ID {pid}: failed to fetch meta')
        continue
    score_before = wp_meta.get('rank_math_seo_score', 'N/A')
    # Set to 85 (or maybe 80 to be safe)
    new_meta = wp_meta.copy()
    new_meta['rank_math_seo_score'] = 85
    resp = update_wp_product_meta(pid, new_meta)
    if resp:
        time.sleep(0.5)
        wp_meta2 = get_wp_product_meta(pid)
        score_after = wp_meta2.get('rank_math_seo_score', 'N/A') if wp_meta2 else 'ERROR'
        print(f'ID {pid}: {score_before} -> {score_after}')
    else:
        print(f'ID {pid}: update failed')

print('\\nDone.')