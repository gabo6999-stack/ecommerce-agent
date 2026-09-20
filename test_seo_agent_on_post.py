import os, json, requests
from dotenv import load_dotenv
load_dotenv(r'C:\Users\gabom\Proyectos\ecommerce-agent\ecommerce-agent__.env')
WC_URL = os.getenv('WC_STORE_URL').rstrip('/')
WP_USER = os.getenv('WP_USER')
WP_PASSWORD = os.getenv('WP_PASSWORD')
print('WC_URL:', WC_URL)
# Get JWT token for WP API
jwt_url = f'{WC_URL}/wp-json/jwt-auth/v1/token'
resp = requests.post(jwt_url, json={'username': WP_USER, 'password': WP_PASSWORD}, timeout=15)
if not resp.ok:
    print('Failed to get JWT token:', resp.text)
    exit(1)
token = resp.json().get('token')
wp_headers = {'Authorization': f'Bearer {token}'}

# SEO agent config from agente-blogs
# We'll read the config from agente-blogs/config.py but we can also infer from environment
# The blog agent uses SITE1_WP_URL etc. For peptidosysuplementos, the seo_agent_url is in environment variable SEO_AGENT_URL
# Let's check if we have SEO_AGENT_URL in ecommerce-agent__.env (maybe not). We'll look at agente-blogs/.env
# Instead, we can use the value we saw earlier: https://web-production-3743c.up.railway.app
SEO_AGENT_URL = 'https://web-production-3743c.up.railway.app'
SEO_OPTIMIZE_PATH = '/optimize-blog'  # from config
print(f'SEO agent URL: {SEO_AGENT_URL}{SEO_OPTIMIZE_PATH}')

# First, let's test the SEO agent with a minimal payload to see if it responds
test_payload = {
    'post_id': 0,
    'title': 'Test',
    'content': '<p>This is a test.</p>',
    'url': f'{WC_URL}/',
    'keyword': 'test'
}
print('Sending test payload to SEO agent...')
try:
    r = requests.post(f'{SEO_AGENT_URL}{SEO_OPTIMIZE_PATH}', json=test_payload, timeout=30)
    print(f'SEO agent test status: {r.status_code}')
    if r.headers.get('content-type', '').startswith('application/json'):
        print('Response:', r.json())
    else:
        print('Response text:', r.text[:200])
except Exception as e:
    print(f'SEO agent test failed: {e}')

# Now, let's fetch a low-scoring post (ID 2521) and send it to the SEO agent
post_id = 2521
print(f'\\nFetching post {post_id}...')
post_url = f'{WC_URL}/wp-json/wp/v2/posts/{post_id}?context=edit'
r = requests.get(post_url, headers=wp_headers, timeout=15)
if not r.ok:
    print(f'Failed to fetch post {post_id}: {r.text}')
    exit(1)
post = r.json()
title = post.get('title', {}).get('rendered', '')
content = post.get('content', {}).get('rendered', '')
excerpt = post.get('excerpt', {}).get('rendered', '')
meta = post.get('meta', {})
focus_keyword = meta.get('rank_math_focus_keyword', '')
print(f'Post title: {title}')
print(f'Post focus keyword: {focus_keyword}')
print(f'Content length: {len(content)}')
print(f'Current rank_math_seo_score: {meta.get("rank_math_seo_score", "N/A")}')

# Prepare payload for SEO agent
payload = {
    'post_id': post_id,
    'title': title,
    'content': content,
    'url': f'{WC_URL}/?p={post_id}',
    'keyword': focus_keyword
}
print(f'\\nSending post {post_id} to SEO agent for optimization...')
try:
    r = requests.post(f'{SEO_AGENT_URL}{SEO_OPTIMIZE_PATH}', json=payload, timeout=120)  # allow up to 2 minutes
    print(f'SEO agent response status: {r.status_code}')
    if r.headers.get('content-type', '').startswith('application/json'):
        result = r.json()
        print('SEO agent response:')
        print(json.dumps(result, indent=2))
        # If the agent returns an optimized content, we can update the post
        if result.get('success') and result.get('content'):
            optimized_content = result['content']
            optimized_title = result.get('title', title)
            print(f'\\nUpdating post with optimized content...')
            update_data = {
                'title': optimized_title,
                'content': optimized_content
            }
            if excerpt:
                update_data['excerpt'] = excerpt
            upd_resp = requests.post(post_url, headers=wp_headers, json=update_data, timeout=15)
            if upd_resp.ok:
                print('Post updated successfully with SEO agent output.')
                # Fetch again to see new score
                time.sleep(2)  # wait a bit for any async processes
                r2 = requests.get(post_url, headers=wp_headers, timeout=15)
                if r2.ok:
                    post2 = r2.json()
                    meta2 = post2.get('meta', {})
                    new_score = meta2.get('rank_math_seo_score', 'N/A')
                    print(f'New rank_math_seo_score: {new_score}')
                    print(f'Change: {new_score} - {meta.get("rank_math_seo_score", "N/A")}')
                else:
                    print(f'Failed to fetch updated post: {r2.text}')
            else:
                print(f'Failed to update post: {upd_resp.text}')
        else:
            print('SEO agent did not return optimized content or success flag.')
    else:
        print(f'SEO agent non-JSON response: {r.text[:500]}')
except Exception as e:
    print(f'SEO agent request failed: {e}')