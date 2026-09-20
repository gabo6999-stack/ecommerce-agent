import os, json, requests
from dotenv import load_dotenv
load_dotenv(r'C:\Users\gabom\Proyectos\ecommerce-agent\ecommerce-agent__.env')
WC_URL = os.getenv('WC_STORE_URL').rstrip('/')
WP_USER = os.getenv('WP_USER')
WP_PASSWORD = os.getenv('WP_PASSWORD')
# Get JWT token
jwt_url = f'{WC_URL}/wp-json/jwt-auth/v1/token'
resp = requests.post(jwt_url, json={'username': WP_USER, 'password': WP_PASSWORD}, timeout=10)
if not resp.ok:
    print('Failed to get JWT token:', resp.text)
    exit(1)
token = resp.json().get('token')
wp_headers = {'Authorization': f'Bearer {token}'}

def get_page_meta(page_id):
    url = f'{WC_URL}/wp-json/wp/v2/pages/{page_id}?context=edit'
    r = requests.get(url, headers=wp_headers, timeout=10)
    if not r.ok:
        return None
    return r.json().get('meta', {})

# Pages we want to check
page_ids = [3, 10, 150, 2418, 2327, 1551, 1166, 1046, 1729, 1750, 22, 21, 20, 15, 5, 1]
print('Checking Rank Math scores for selected pages...')
for pid in page_ids:
    meta = get_page_meta(pid)
    if meta is None:
        print(f'  Page ID {pid}: FAIL to fetch meta')
        continue
    score = meta.get('rank_math_seo_score', 0)
    title = meta.get('rank_math_title', '') or '(no title)'
    print(f'  Page ID {pid}: {title[:50]}... -> SCORE: {score}')