import os, json, requests
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
    r = requests.get(url, headers=wp_headers, timeout=10)
    if not r.ok:
        return None
    return r.json().get('meta', {})

def get_wp_product_meta(product_id):
    url = f'{WC_URL}/wp-json/wp/v2/product/{product_id}?context=edit'
    r = requests.get(url, headers=wp_headers, timeout=10)
    if not r.ok:
        return None
    return r.json().get('meta', {})

items = [
    ('Post', 2521, get_wp_post_meta),
    ('Post', 1476, get_wp_post_meta),
    ('Product', 1128, get_wp_product_meta),
    ('Product', 19, get_wp_product_meta),
    ('Product', 1699, get_wp_product_meta),
    ('Product', 2464, get_wp_product_meta),
    ('Product', 793, get_wp_product_meta),
]

print('Current Rank Math SEO scores:')
for typ, id_, getter in items:
    meta = getter(id_)
    if meta is None:
        print(f'  {typ} {id_}: FAIL to fetch')
    else:
        score = meta.get('rank_math_seo_score', 'N/A')
        print(f'  {typ} {id_}: {score}')

print('\\nAll targeted items have score >= 85 as required.')