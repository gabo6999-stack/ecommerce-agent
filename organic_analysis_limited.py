import os, json, requests, re, csv
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

def get_wp_post(post_id):
    url = f'{WC_URL}/wp-json/wp/v2/posts/{post_id}?context=edit'
    r = requests.get(url, headers=wp_headers, timeout=10)
    if not r.ok:
        return None
    return r.json()

def get_wp_product(product_id):
    url = f'{WC_URL}/wp-json/wp/v2/product/{product_id}?context=edit'
    r = requests.get(url, headers=wp_headers, timeout=10)
    if not r.ok:
        return None
    return r.json()

def analyze_post(content):
    if not content:
        return {}
    length = len(content)
    h1_count = len(re.findall(r'<h1[^>]*>.*?</h1>', content, re.IGNORECASE))
    h2_count = len(re.findall(r'<h2[^>]*>.*?</h2>', content, re.IGNORECASE))
    h3_count = len(re.findall(r'<h3[^>]*>.*?</h3>', content, re.IGNORECASE))
    ul_count = len(re.findall(r'<ul[^>]*>.*?</ul>', content, re.IGNORECASE | re.DOTALL))
    ol_count = len(re.findall(r'<ol[^>]*>.*?</ol>', content, re.IGNORECASE | re.DOTALL))
    internal_links = len(re.findall(r'<a[^>]*href=["\']' + re.escape(WC_URL) + '[^>]*>', content, re.IGNORECASE))
    external_links = len(re.findall(r'<a[^>]*href=["\'](?!' + re.escape(WC_URL) + ')[^>]*>', content, re.IGNORECASE))
    schema_blocks = len(re.findall(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>', content, re.IGNORECASE))
    faq_blocks = len(re.findall(r'"@type"\s*:\s*"FAQPage"', content, re.IGNORECASE))
    return {
        'length': length,
        'h1': h1_count,
        'h2': h2_count,
        'h3': h3_count,
        'ul': ul_count,
        'ol': ol_count,
        'internal_links': internal_links,
        'external_links': external_links,
        'schema_blocks': schema_blocks,
        'faq_blocks': faq_blocks
    }

def analyze_product(wp_product, wc_product):
    if not wp_product or not wc_product:
        return {}
    meta = wp_product.get('meta', {})
    # content from WP product is not the description; we need WC product description
    long_desc = wc_product.get('description', '')
    short_desc = wc_product.get('short_description', '')
    # analyze long description
    long_metrics = analyze_post(long_desc) if long_desc else {}
    # analyze short description
    short_metrics = analyze_post(short_desc) if short_desc else {}
    # combine with prefixes
    metrics = {}
    for k, v in long_metrics.items():
        metrics[f'long_{k}'] = v
    for k, v in short_metrics.items():
        metrics[f'short_{k}'] = v
    # add meta fields
    metrics['rank_math_seo_score'] = meta.get('rank_math_seo_score', 0)
    metrics['rank_math_title_len'] = len(meta.get('rank_math_title', ''))
    metrics['rank_math_desc_len'] = len(meta.get('rank_math_description', ''))
    metrics['rank_math_focus_keyword'] = meta.get('rank_math_focus_keyword', '')
    return metrics

print('Fetching posts (1-100)...')
posts_data = []
for pid in range(1, 101):
    post = get_wp_post(pid)
    if post:
        meta = post.get('meta', {})
        score = meta.get('rank_math_seo_score', 0)
        title = post.get('title', {}).get('rendered', '')
        content = post.get('content', {}).get('rendered', '')
        metrics = analyze_post(content)
        metrics['id'] = pid
        metrics['type'] = 'post'
        metrics['title'] = title[:50]
        metrics['score'] = score
        posts_data.append(metrics)
    # progress
    if pid % 20 == 0:
        print(f'  processed {pid} posts')

print('Fetching products (1-100)...')
products_data = []
for pid in range(1, 101):
    wp_product = get_wp_product(pid)
    wc_product = None
    # we need WC API credentials for product fetch; skip if not available
    # For now, we'll just use WP product meta which may include rank_math fields
    if wp_product:
        meta = wp_product.get('meta', {})
        score = meta.get('rank_math_seo_score', 0)
        title = wp_product.get('title', {}).get('rendered', '')
        # we still need description; we'll try to get via WC API if credentials exist
        # but to keep simple, we'll skip detailed product analysis for now
        # Instead, we'll just record basic meta
        metrics = {
            'id': pid,
            'type': 'product',
            'title': title[:50],
            'score': score,
            'rank_math_seo_score': score,
            'rank_math_title_len': len(meta.get('rank_math_title', '')),
            'rank_math_desc_len': len(meta.get('rank_math_description', '')),
            'rank_math_focus_keyword': meta.get('rank_math_focus_keyword', '')
        }
        products_data.append(metrics)
    if pid % 20 == 0:
        print(f'  processed {pid} products')

# Write to CSV for inspection
if posts_data:
    fieldnames = posts_data[0].keys()
    with open('/c/Users/gabom/AppData/Local/Temp/posts_analysis.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(posts_data)
    print('\\nPosts analysis written to /c/Users/gabom/AppData/Local/Temp/posts_analysis.csv')

if products_data:
    fieldnames = products_data[0].keys()
    with open('/c/Users/gabom/AppData/Local/Temp/products_analysis.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(products_data)
    print('Products analysis written to /c/Users/gabom/AppData/Local/Temp/products_analysis.csv')

# Print summary stats
print('\\n=== POST SUMMARY ===')
if posts_data:
    scores = [p['score'] for p in posts_data]
    print(f'Posts analyzed: {len(posts_data)}')
    print(f'Score min: {min(scores)}')
    print(f'Score max: {max(scores)}')
    print(f'Score mean: {sum(scores)/len(scores):.1f}')
    # count >=85
    high = [p for p in posts_data if p['score'] >= 85]
    print(f'Posts >=85: {len(high)}')
    if high:
        print('  Examples:')
        for p in high[:5]:
            print(f'    ID {p["id"]}: {p["title"]} (score {p["score"]})')

print('\\n=== PRODUCT SUMMARY ===')
if products_data:
    scores = [p['score'] for p in products_data]
    print(f'Products analyzed: {len(products_data)}')
    print(f'Score min: {min(scores)}')
    print(f'Score max: {max(scores)}')
    print(f'Score mean: {sum(scores)/len(scores):.1f}')
    high = [p for p in products_data if p['score'] >= 85]
    print(f'Products >=85: {len(high)}')
    if high:
        print('  Examples:')
        for p in high[:5]:
            print(f'    ID {p["id"]}: {p["title"]} (score {p["score"]})')