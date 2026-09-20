import os, json, requests, re
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
    r = requests.get(url, headers=wp_headers, timeout=15)
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

# Let's check a range of posts to find more high scorers
print('Scanning posts 1000-2000 for high scorers...')
high_scoring_posts = []
for pid in range(1000, 2001, 50):  # Every 50th post to start
    post = get_wp_post(pid)
    if post:
        meta = post.get('meta', {})
        score = meta.get('rank_math_seo_score', 0)
        if score >= 80:
            high_scoring_posts.append((pid, score))
            print(f'  Found high scorer: Post {pid} = {score}')

print(f'\\nFound {len(high_scoring_posts)} high scoring posts (>=80) in sample')

# Now analyze the top few
if high_scoring_posts:
    high_scoring_posts.sort(key=lambda x: x[1], reverse=True)
    top_posts = high_scoring_posts[:5]  # Top 5
    print('\\n=== ANALYZING TOP 5 POSTS ===')
    for pid, score in top_posts:
        post = get_wp_post(pid)
        if post:
            title = post.get('title', {}).get('rendered', '')
            content = post.get('content', {}).get('rendered', '')
            meta = post.get('meta', {})
            focus = meta.get('rank_math_focus_keyword', '')
            print(f'\\nPost {pid}: {title[:60]}...')
            print(f'  Score: {score}')
            print(f'  Focus: {focus}')
            metrics = analyze_post(content)
            for k, v in metrics.items():
                print(f'  {k}: {v}')

# Also check some known posts from context
known_posts = [1000, 1476, 1500, 2000, 2521]
print('\\n\\n=== ANALYZING KNOWN POSTS ===')
for pid in known_posts:
    post = get_wp_post(pid)
    if post:
        title = post.get('title', {}).get('rendered', '')
        content = post.get('content', {}).get('rendered', '')
        meta = post.get('meta', {})
        score = meta.get('rank_math_seo_score', 'N/A')
        focus = meta.get('rank_math_focus_keyword', '')
        print(f'\\nPost {pid}: {title[:60]}...')
        print(f'  Score: {score}')
        print(f'  Focus: {focus}')
        metrics = analyze_post(content)
        for k, v in metrics.items():
            print(f'  {k}: {v}')