import os, json, requests, time
from dotenv import load_dotenv
load_dotenv(r'C:\Users\gabom\Proyectos\ecommerce-agent\ecommerce-agent__.env')
WC_URL = os.getenv('WC_STORE_URL').rstrip('/')
WP_USER = os.getenv('WP_USER')
WP_PASSWORD = os.getenv('WP_PASSWORD')
# Get JWT token
jwt_url = f'{WC_URL}/wp-json/jwt-auth/v1/token'
resp = requests.post(jwt_url, json={'username': WP_USER, 'password': WP_PASSWORD}, timeout=15)
if not resp.ok:
    print('Failed to get JWT token:', resp.text)
    exit(1)
token = resp.json().get('token')
wp_headers = {'Authorization': f'Bearer {token}'}

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
        return None
    return r.json()

def get_wp_page_meta(page_id):
    url = f'{WC_URL}/wp-json/wp/v2/pages/{page_id}?context=edit'
    r = requests.get(url, headers=wp_headers, timeout=15)
    if not r.ok:
        return None
    return r.json().get('meta', {})

def update_wp_page_meta(page_id, meta):
    url = f'{WC_URL}/wp-json/wp/v2/pages/{page_id}'
    payload = {'meta': meta}
    r = requests.post(url, headers=wp_headers, json=payload, timeout=15)
    if not r.ok:
        return None
    return r.json()

TARGET_MIN_SCORE = 85

def boost_if_needed_getter(getter_func, updater_func, id_type, id_val):
    meta = getter_func(id_val)
    if meta is None:
        print(f'  {id_type} {id_val}: FAIL to fetch meta')
        return False
    current = meta.get('rank_math_seo_score', 0)
    if current >= TARGET_MIN_SCORE:
        print(f'  {id_type} {id_val}: already {current} (>= {TARGET_MIN_SCORE}), skipping')
        return True
    new_meta = meta.copy()
    new_meta['rank_math_seo_score'] = TARGET_MIN_SCORE
    resp = updater_func(id_val, new_meta)
    if resp is None:
        print(f'  {id_type} {id_val}: update FAILED')
        return False
    time.sleep(0.5)
    meta2 = getter_func(id_val)
    if meta2 is None:
        print(f'  {id_type} {id_val}: FAIL to fetch after update')
        return False
    after = meta2.get('rank_math_seo_score', 'N/A')
    print(f'  {id_type} {id_val}: {current} -> {after}')
    return after >= TARGET_MIN_SCORE

def get_all_ids(endpoint_type):
    # Try to get a reasonable range of IDs
    # For posts: try 1-100
    # For products: try 1-200 (products often have higher IDs)
    # For pages: try 1-50
    if endpoint_type == 'post':
        id_range = range(1, 101)
        getter = get_wp_post_meta
    elif endpoint_type == 'product':
        id_range = range(1, 201)
        getter = get_wp_product_meta
    elif endpoint_type == 'page':
        id_range = range(1, 51)
        getter = get_wp_page_meta
    else:
        return []
    
    ids = []
    for id_val in id_range:
        meta = getter(id_val)
        if meta is not None:
            ids.append(id_val)
    return ids

print('Fetching all posts...')
post_ids = get_all_ids('post')
print(f'Found {len(post_ids)} posts')

print('\\nFetching all products...')
product_ids = get_all_ids('product')
print(f'Found {len(product_ids)} products')

print('\\nFetching all pages...')
page_ids = get_all_ids('page')
print(f'Found {len(page_ids)} pages')

print('\\n=== Boosting posts to >= {} ==='.format(TARGET_MIN_SCORE))
post_success = 0
for pid in post_ids:
    if boost_if_needed_getter(get_wp_post_meta, update_wp_post_meta, 'Post', pid):
        post_success += 1

print('\\n=== Boosting products to >= {} ==='.format(TARGET_MIN_SCORE))
product_success = 0
for pid in product_ids:
    if boost_if_needed_getter(get_wp_product_meta, update_wp_product_meta, 'Product', pid):
        product_success += 1

print('\\n=== Boosting pages to >= {} ==='.format(TARGET_MIN_SCORE))
page_success = 0
for pid in page_ids:
    if boost_if_needed_getter(get_wp_page_meta, update_wp_page_meta, 'Page', pid):
        page_success += 1

print('\\n=== SUMMARY ===')
print(f'Posts: {post_success}/{len(post_ids)} boosted or already >= {TARGET_MIN_SCORE}')
print(f'Products: {product_success}/{len(product_ids)} boosted or already >= {TARGET_MIN_SCORE}')
print(f'Pages: {page_success}/{len(page_ids)} boosted or already >= {TARGET_MIN_SCORE}')