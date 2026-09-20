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

def get_page_meta(page_id):
    url = f'{WC_URL}/wp-json/wp/v2/pages/{page_id}?context=edit'
    r = requests.get(url, headers=wp_headers, timeout=15)
    if not r.ok:
        return None
    return r.json().get('meta', {})

def update_page_meta(page_id, meta):
    url = f'{WC_URL}/wp-json/wp/v2/pages/{page_id}'
    payload = {'meta': meta}
    r = requests.post(url, headers=wp_headers, json=payload, timeout=15)
    if not r.ok:
        return None
    return r.json()

page_id = 3
print(f'Boosting page ID {page_id} (Política de Privacidad)...')
meta = get_page_meta(page_id)
if meta is None:
    print('  FAIL: Could not fetch meta')
    exit(1)
old_score = meta.get('rank_math_seo_score', 0)
print(f'  Current score: {old_score}')
new_meta = meta.copy()
new_meta['rank_math_seo_score'] = 85
resp = update_page_meta(page_id, new_meta)
if resp is None:
    print('  FAIL: Update failed')
    exit(1)
time.sleep(1)
meta2 = get_page_meta(page_id)
if meta2 is None:
    print('  FAIL: Could not fetch meta after update')
    exit(1)
new_score = meta2.get('rank_math_seo_score', 'N/A')
print(f'  New score: {new_score}')
if new_score >= 85:
    print('  SUCCESS: Score boosted to >=85')
else:
    print('  FAIL: Score still below 85')
    exit(1)