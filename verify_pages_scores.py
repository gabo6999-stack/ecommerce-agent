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

def get_page_meta(page_id):
    url = f'{WC_URL}/wp-json/wp/v2/pages/{page_id}?context=edit'
    r = requests.get(url, headers=wp_headers, timeout=15)
    if not r.ok:
        return None
    return r.json().get('meta', {})

print('Fetching all pages to verify final scores...')
# Get all pages
page = 1
all_pages = []
while True:
    url = f'{WC_URL}/wp-json/wp/v2/pages?per_page=100&page={page}'
    r = requests.get(url, headers=wp_headers, timeout=15)
    if not r.ok:
        break
    data = r.json()
    if not data:
        break
    all_pages.extend(data)
    if len(data) < 100:
        break
    page += 1

print(f'Found {len(all_pages)} pages')
low_score_pages = []
for p in all_pages:
    pid = p['id']
    title = p.get('title', {}).get('rendered', '').strip()
    meta = get_page_meta(pid)
    if meta is None:
        print(f'  Page ID {pid}: FAIL to fetch meta')
        low_score_pages.append((pid, title, 'FETCH_FAILED'))
        continue
    score = meta.get('rank_math_seo_score', 0)
    if score < 85:
        low_score_pages.append((pid, title, score))
        print(f'  Page ID {pid}: "{title[:50]}..." -> SCORE: {score} (LOW)')
    #else:
    #    print(f'  Page ID {pid}: "{title[:50]}..." -> SCORE: {score} (OK)')

print(f'\\n=== VERIFICATION RESULTS ===')
print(f'Total pages: {len(all_pages)}')
print(f'Pages with score < 85: {len(low_score_pages)}')

if low_score_pages:
    print('\\nPages still below 85:')
    for pid, title, score in low_score_pages:
        print(f'  ID {pid}: "{title[:40]}..." -> {score}')
else:
    print('\\n✅ ALL PAGES HAVE SCORE >= 85')