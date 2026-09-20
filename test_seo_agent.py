import sys
import os
sys.path.insert(0, r'C:\Users\gabom\Proyectos\agente-blogs')
from config import SITES
import requests
import json

site_key = 'peptidosysuplementos'
site_cfg = SITES[site_key]
seo_agent_url = site_cfg.get('seo_agent_url')
print(f'SEO agent URL: {seo_agent_url}')
if not seo_agent_url:
    print('SEO agent URL not configured')
    sys.exit(1)

# Test with a simple GET to see if it's alive
try:
    resp = requests.get(seo_agent_url, timeout=10)
    print(f'GET {seo_agent_url} -> status {resp.status_code}')
except Exception as e:
    print(f'GET failed: {e}')

# Now test the optimize endpoint
seo_optimize_path = site_cfg.get('seo_optimize_path', '/optimize-blog')
url = f'{seo_agent_url}{seo_optimize_path}'
print(f'Optimize endpoint: {url}')

# We need a post ID, title, content, etc. Let's fetch a real post from WP to test.
# We'll use the ecommerce-agent env for WP credentials.
dotenv_path = r'C:\Users\gabom\Proyectos\ecommerce-agent\ecommerce-agent__.env'
from dotenv import load_dotenv
load_dotenv(dotenv_path)
WC_URL = os.getenv('WC_STORE_URL').rstrip('/')
WP_USER = os.getenv('WP_USER')
WP_PASSWORD = os.getenv('WP_PASSWORD')
print(f'WP URL: {WC_URL}')

# Get JWT token
jwt_url = f'{WC_URL}/wp-json/jwt-auth/v1/token'
resp = requests.post(jwt_url, json={'username': WP_USER, 'password': WP_PASSWORD}, timeout=15)
if not resp.ok:
    print(f'Failed to get JWT token: {resp.text}')
    sys.exit(1)
token = resp.json().get('token')
headers = {'Authorization': f'Bearer {token}'}

# Fetch post 2521
post_id = 2521
post_url = f'{WC_URL}/wp-json/wp/v2/posts/{post_id}?context=edit'
resp = requests.get(post_url, headers=headers, timeout=15)
if not resp.ok:
    print(f'Failed to fetch post {post_id}: {resp.text}')
    sys.exit(1)
post = resp.json()
title = post.get('title', {}).get('rendered', '')
content = post.get('content', {}).get('rendered', '')
excerpt = post.get('excerpt', {}).get('rendered', '')
focus_keyword = post.get('meta', {}).get('rank_math_focus_keyword', '')
print(f'Fetched post {post_id}: title="{title}", keyword="{focus_keyword}"')

# Prepare payload for SEO agent
payload = {
    'post_id': post_id,
    'title': title,
    'content': content,
    'url': f'{WC_URL}/?p={post_id}',
    'keyword': focus_keyword
}
print(f'Payload keys: {list(payload.keys())}')
print(f'Content length: {len(content)}')

# Send to SEO agent
try:
    print(f'Sending to {url} ...')
    resp = requests.post(url, json=payload, timeout=120)  # allow up to 2 minutes
    print(f'Response status: {resp.status_code}')
    print(f'Response headers: {resp.headers}')
    if resp.headers.get('content-type', '').startswith('application/json'):
        result = resp.json()
        print(f'JSON response: {json.dumps(result, indent=2)}')
    else:
        print(f'Response text (first 500 chars): {resp.text[:500]}')
except Exception as e:
    print(f'Request failed: {e}')