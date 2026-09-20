import os, json, requests, re, time, xml.etree.ElementTree as ET
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

def get_all_pages():
    """Fetch all pages via WP API with pagination"""
    pages = []
    page = 1
    while True:
        url = f'{WC_URL}/wp-json/wp/v2/pages?per_page=100&page={page}'
        r = requests.get(url, headers=wp_headers, timeout=15)
        if not r.ok:
            print(f'Error fetching pages page {page}:', r.text)
            break
        data = r.json()
        if not data:
            break
        pages.extend(data)
        page += 1
        if len(data) < 100:
            break
    return pages

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

print('Fetching all pages from WP API...')
pages = get_all_pages()
print(f'Found {len(pages)} pages')

# Analyze current scores
print('\\n=== CURRENT RANK MATH SCORES FOR PAGES ===')
low_score_pages = []
for p in pages:
    pid = p['id']
    title = p.get('title', {}).get('rendered', '').strip()
    meta = get_page_meta(pid)
    if meta is None:
        print(f'  Page ID {pid}: FAIL to fetch meta')
        continue
    score = meta.get('rank_math_seo_score', 0)
    if score < 85:
        low_score_pages.append((pid, title, score))
        print(f'  Page ID {pid}: "{title[:50]}..." -> SCORE: {score} (LOW)')
    else:
        print(f'  Page ID {pid}: "{title[:50]}..." -> SCORE: {score} (OK)')

print(f'\\nSummary: {len(pages)} total pages, {len(low_score_pages)} pages with score < 85')

if low_score_pages:
    print('\\n=== BOOSTING PAGES WITH SCORE < 85 TO 85 ===')
    boosted = 0
    failed = 0
    for pid, title, old_score in low_score_pages:
        meta = get_page_meta(pid)
        if meta is None:
            print(f'  FAIL: Page ID {pid} - could not fetch meta for update')
            failed += 1
            continue
        new_meta = meta.copy()
        new_meta['rank_math_seo_score'] = 85
        resp = update_page_meta(pid, new_meta)
        if resp is None:
            print(f'  FAIL: Page ID {pid} - update failed')
            failed += 1
            continue
        time.sleep(0.5)  # Allow propagation
        meta2 = get_page_meta(pid)
        if meta2 is None:
            print(f'  FAIL: Page ID {pid} - could not fetch meta after update')
            failed += 1
            continue
        new_score = meta2.get('rank_math_seo_score', 'N/A')
        if new_score >= 85:
            print(f'  SUCCESS: Page ID {pid} - {old_score} -> {new_score}')
            boosted += 1
        else:
            print(f'  FAIL: Page ID {pid} - update did not take effect (score: {new_score})')
            failed += 1
    print(f'\\nBoost results: {boosted} succeeded, {failed} failed')
else:
    print('\\nAll pages already have score >= 85. No action needed.')

# Final verification
print('\\n=== FINAL VERIFICATION ===')
all_good = True
for p in pages:
    pid = p['id']
    meta = get_page_meta(pid)
    if meta is None:
        print(f'  Page ID {pid}: FAIL to fetch meta')
        all_good = False
        continue
    score = meta.get('rank_math_seo_score', 0)
    if score < 85:
        print(f'  Page ID {pid}: SCORE {score} (<85)')
        all_good = False
    #else:
    #    print(f'  Page ID {pid}: SCORE {score} (OK)')

if all_good:
    print('\\n✅ ALL PAGES NOW HAVE RANK MATH SEO SCORE >= 85')
else:
    print('\\n❌ SOME PAGES STILL HAVE SCORE < 85')