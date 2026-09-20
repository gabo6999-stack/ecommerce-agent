import os, json, requests, re
from dotenv import load_dotenv
load_dotenv(r'C:\Users\gabom\Proyectos\ecommerce-agent\ecommerce-agent__.env')
WC_URL = os.getenv('WC_STORE_URL').rstrip('/')
WP_USER = os.getenv('WP_USER')
WP_PASSWORD = os.getenv('WP_PASSWORD')
CONSUMER_KEY = os.getenv('WC_CONSUMER_KEY')
CONSUMER_SECRET = os.getenv('WC_CONSUMER_SECRET')
print('WC_URL:', WC_URL)
# Get JWT token for WP API
jwt_url = f'{WC_URL}/wp-json/jwt-auth/v1/token'
resp = requests.post(jwt_url, json={'username': WP_USER, 'password': WP_PASSWORD}, timeout=15)
if not resp.ok:
    print('Failed to get JWT token:', resp.text)
    exit(1)
token = resp.json().get('token')
wp_headers = {'Authorization': f'Bearer {token}'}
# WooCommerce Basic Auth
wc_auth = (CONSUMER_KEY, CONSUMER_SECRET)

def get_wp_post(post_id):
    url = f'{WC_URL}/wp-json/wp/v2/posts/{post_id}?context=edit'
    r = requests.get(url, headers=wp_headers, timeout=15)
    if not r.ok:
        print(f'Error fetching WP post {post_id}:', r.text)
        return None
    return r.json()
def get_wp_product(product_id):
    url = f'{WC_URL}/wp-json/wp/v2/product/{product_id}?context=edit'
    r = requests.get(url, headers=wp_headers, timeout=15)
    if not r.ok:
        print(f'Error fetching WP product {product_id}:', r.text)
        return None
    return r.json()
def get_wc_product(product_id):
    url = f'{WC_URL}/wp-json/wc/v3/products/{product_id}'
    r = requests.get(url, auth=wc_auth, timeout=15)
    if not r.ok:
        print(f'Error fetching WC product {product_id}:', r.text)
        return None
    return r.json()

# Known high and low scoring items from earlier analysis
# Posts
high_post_ids = [1476]  # Retatrutida TRIUMPH-1: Resultados Clinicos Reales 2026 (score 88)
low_post_ids = [2521]   # Selank: Qué es, Para Qué Sirve, Beneficios y Dosis 2026 (was 0, now 88 after boost)

# Products
high_product_ids = [2240, 795, 790, 1151, 1158]  # Cagrilintida, BPC-157+TB-500, MOTS-c, Omega-3, DIM
low_product_ids = [1128, 19, 1699, 2464, 793]    # IGF-1 LR3, Retatrutida, Selank, BPC-157, MOTS-c 40mg

def analyze_content(content, name="content"):
    if not content:
        return {}
    # Basic metrics
    length = len(content)
    # Count headings
    h1_count = len(re.findall(r'<h1[^>]*>.*?</h1>', content, re.IGNORECASE))
    h2_count = len(re.findall(r'<h2[^>]*>.*?</h2>', content, re.IGNORECASE))
    h3_count = len(re.findall(r'<h3[^>]*>.*?</h3>', content, re.IGNORECASE))
    # Count lists
    ul_count = len(re.findall(r'<ul[^>]*>.*?</ul>', content, re.IGNORECASE | re.DOTALL))
    ol_count = len(re.findall(r'<ol[^>]*>.*?</ol>', content, re.IGNORECASE | re.DOTALL))
    # Count links
    internal_links = len(re.findall(r'<a[^>]*href=["\']' + re.escape(WC_URL) + '[^>]*>', content, re.IGNORECASE))
    external_links = len(re.findall(r'<a[^>]*href=["\'](?!' + re.escape(WC_URL) + ')[^>]*>', content, re.IGNORECASE))
    # Count schema blocks
    schema_blocks = len(re.findall(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>', content, re.IGNORECASE))
    # Count FAQ schema specifically
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

print('=== POST ANALYSIS ===')
for pid in high_post_ids + low_post_ids:
    post = get_wp_post(pid)
    if not post:
        print(f'Post {pid}: failed to fetch')
        continue
    meta = post.get('meta', {})
    score = meta.get('rank_math_seo_score', 'N/A')
    title = post.get('title', {}).get('rendered', '')
    content = post.get('content', {}).get('rendered', '')
    focus = meta.get('rank_math_focus_keyword', '')
    print(f'\\nPost {pid}: {title}')
    print(f'  Score: {score}')
    print(f'  Focus keyword: {focus}')
    metrics = analyze_content(content, f'post {pid}')
    for k, v in metrics.items():
        print(f'  {k}: {v}')

print('\\n\\n=== PRODUCT ANALYSIS ===')
for pid in high_product_ids + low_product_ids:
    wp_product = get_wp_product(pid)
    wc_product = get_wc_product(pid)
    if not wp_product or not wc_product:
        print(f'Product {pid}: failed to fetch')
        continue
    meta = wp_product.get('meta', {})
    score = meta.get('rank_math_seo_score', 'N/A')
    title = wp_product.get('title', {}).get('rendered', '')
    name = wc_product.get('name', '')
    long_desc = wc_product.get('description', '')
    short_desc = wc_product.get('short_description', '')
    focus = meta.get('rank_math_focus_keyword', '')
    print(f'\\nProduct {pid}: {name} (WP title: {title})')
    print(f'  Score: {score}')
    print(f'  Focus keyword: {focus}')
    print(f'  Short desc length: {len(short_desc)}')
    # Analyze long description
    metrics = analyze_content(long_desc, f'product {pid} long desc')
    for k, v in metrics.items():
        print(f'  long_desc_{k}: {v}')
    # Analyze short description
    if short_desc:
        metrics_short = analyze_content(short_desc, f'product {pid} short desc')
        for k, v in metrics_short.items():
            print(f'  short_desc_{k}: {v}')