import os, json, requests
from dotenv import load_dotenv
load_dotenv(r'C:\Users\gabom\Proyectos\ecommerce-agent\ecommerce-agent__.env')
WC_URL = os.getenv('WC_STORE_URL').rstrip('/')
WP_USER = os.getenv('WP_USER')
WP_PASSWORD = os.getenv('WP_PASSWORD')
# JWT token
jwt_url = f'{WC_URL}/wp-json/jwt-auth/v1/token'
resp = requests.post(jwt_url, json={'username': WP_USER, 'password': WP_PASSWORD}, timeout=15)
if not resp.ok:
    print('Failed to get JWT token:', resp.text)
    exit(1)
token = resp.json().get('token')
headers = {'Authorization': f'Bearer {token}'}
# Get all products (limit 100)
url = f'{WC_URL}/wp-json/wc/v3/products'
# Use Basic Auth for WC API
from requests.auth import HTTPBasicAuth
CK = os.getenv('WC_CONSUMER_KEY')
CS = os.getenv('WC_CONSUMER_SECRET')
auth = (CK, CS)
params = {'per_page': 100}
resp = requests.get(url, auth=auth, params=params, timeout=15)
if not resp.ok:
    print('Error fetching products:', resp.text)
    exit(1)
products = resp.json()
print(f'Found {len(products)} products')
scores = []
for p in products:
    pid = p['id']
    # Get WP product to get meta
    wp_url = f'{WC_URL}/wp-json/wp/v2/product/{pid}?context=edit'
    r = requests.get(wp_url, headers=headers, timeout=15)
    if r.ok:
        meta = r.json().get('meta', {})
        score = meta.get('rank_math_seo_score', None)
        if score is not None:
            scores.append((pid, p['name'], score))
    else:
        # fallback: maybe product not accessible as WP product? skip
        pass
# Sort by score ascending
scores.sort(key=lambda x: x[2])
print('\\nLowest scores:')
for pid, name, score in scores[:10]:
    print(f'ID {pid}: {name} -> {score}')
print('\\nHighest scores:')
for pid, name, score in scores[-10:]:
    print(f'ID {pid}: {name} -> {score}')