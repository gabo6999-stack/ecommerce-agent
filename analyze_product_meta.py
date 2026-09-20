import os, json, requests
from dotenv import load_dotenv
load_dotenv(r'C:\Users\gabom\Proyectos\ecommerce-agent\ecommerce-agent__.env')
WC_URL = os.getenv('WC_STORE_URL').rstrip('/')
WP_USER = os.getenv('WP_USER')
WP_PASSWORD = os.getenv('WP_PASSWORD')
CONSUMER_KEY = os.getenv('WC_CONSUMER_KEY')
CONSUMER_SECRET = os.getenv('WC_CONSUMER_SECRET')
print('Fetching product meta for analysis...')
# Get JWT token
jwt_url = f'{WC_URL}/wp-json/jwt-auth/v1/token'
resp = requests.post(jwt_url, json={'username': WP_USER, 'password': WP_PASSWORD}, timeout=15)
if not resp.ok:
    print('Failed to get JWT token:', resp.text)
    exit(1)
token = resp.json().get('token')
wp_headers = {'Authorization': f'Bearer {token}'}
wc_auth = (CONSUMER_KEY, CONSUMER_SECRET)

def get_wp_product_meta(product_id):
    url = f'{WC_URL}/wp-json/wp/v2/product/{product_id}?context=edit'
    r = requests.get(url, headers=wp_headers, timeout=15)
    if not r.ok:
        return None
    return r.json().get('meta', {})

def get_wc_product(product_id):
    url = f'{WC_URL}/wp-json/wc/v3/products/{product_id}'
    r = requests.get(url, auth=wc_auth, timeout=15)
    if not r.ok:
        return None
    return r.json()

# List of product IDs we want to check: low and high scores
# From earlier check_product_scores.py output:
low_ids = [1128, 19, 1699, 2464, 793]  # IGF-1 LR3, Retatrutida, Selank, BPC-157, MOTS-c 40mg
high_ids = [2240, 795, 790, 1151, 1158]  # Cagrilintida, BPC-157+TB-500, MOTS-c, Omega-3, DIM

print('\\n=== Low-scoring products ===')
for pid in low_ids:
    meta = get_wp_product_meta(pid)
    wc = get_wc_product(pid)
    if not meta or not wc:
        print(f'ID {pid}: failed to fetch')
        continue
    name = wc.get('name', '')
    score = meta.get('rank_math_seo_score', 'N/A')
    title = meta.get('rank_math_title', '')
    desc = meta.get('rank_math_description', '')
    focus = meta.get('rank_math_focus_keyword', '')
    print(f'ID {pid}: {name}')
    print(f'  Score: {score}')
    print(f'  Title: {title[:80]}')
    print(f'  Desc len: {len(desc)}')
    print(f'  Focus: {focus}')
    # Also get content length
    content_len = len(wc.get('description', ''))
    print(f'  Content length: {content_len}')
    # Image count
    images = wc.get('images', [])
    print(f'  Images: {len(images)}')
    print()

print('\\n=== High-scoring products ===')
for pid in high_ids:
    meta = get_wp_product_meta(pid)
    wc = get_wc_product(pid)
    if not meta or not wc:
        print(f'ID {pid}: failed to fetch')
        continue
    name = wc.get('name', '')
    score = meta.get('rank_math_seo_score', 'N/A')
    title = meta.get('rank_math_title', '')
    desc = meta.get('rank_math_description', '')
    focus = meta.get('rank_math_focus_keyword', '')
    print(f'ID {pid}: {name}')
    print(f'  Score: {score}')
    print(f'  Title: {title[:80]}')
    print(f'  Desc len: {len(desc)}')
    print(f'  Focus: {focus}')
    content_len = len(wc.get('description', ''))
    print(f'  Content length: {content_len}')
    images = wc.get('images', [])
    print(f'  Images: {len(images)}')
    print()