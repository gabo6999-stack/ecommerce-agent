import os, json, requests
from dotenv import load_dotenv
load_dotenv('ecommerce-agent__.env')
WC_URL = os.getenv('WC_STORE_URL').rstrip('/')
WP_USER = os.getenv('WP_USER')
WP_PASSWORD = os.getenv('WP_PASSWORD')
print('WC_URL:', WC_URL)
jwt_url = f'{WC_URL}/wp-json/jwt-auth/v1/token'
resp = requests.post(jwt_url, json={'username': WP_USER, 'password': WP_PASSWORD}, timeout=15)
if not resp.ok:
    print('Failed to get JWT token:', resp.text)
    exit(1)
token = resp.json().get('token')
headers = {'Authorization': f'Bearer {token}'}
def get_post(post_id):
    url = f'{WC_URL}/wp-json/wp/v2/posts/{post_id}?context=edit'
    r = requests.get(url, headers=headers, timeout=15)
    if not r.ok:
        print(f'Error fetching post {post_id}:', r.text)
        return None
    return r.json()
def update_post(post_id, data):
    url = f'{WC_URL}/wp-json/wp/v2/posts/{post_id}'
    r = requests.post(url, headers=headers, json=data, timeout=15)
    if not r.ok:
        print(f'Error updating post {post_id}:', r.text)
        return None
    return r.json()
# Get reference post 1476
print('Fetching reference post 1476...')
ref = get_post(1476)
if not ref:
    exit(1)
ref_meta = ref.get('meta', {})
elem_data = ref_meta.get('_elementor_data')
elem_type = ref_meta.get('_elementor_template_type')
print(f'Reference _elementor_template_type: {elem_type}')
print(f'Reference _elementor_data length: {len(elem_data) if elem_data else 0}')
# Get target post 2521
print('Fetching target post 2521...')
target = get_post(2521)
if not target:
    exit(1)
target_meta = target.get('meta', {})
score_before = target_meta.get('rank_math_seo_score', 0)
print(f'Target Rank Math SEO score before: {score_before}')
# Prepare updates
updates = {}
if elem_data is not None:
    updates['_elementor_data'] = elem_data
if elem_type is not None:
    updates['_elementor_template_type'] = elem_type
# Also ensure RankMath meta is set (optional)
rm_meta = {
    'rank_math_title': target.get('title', {}).get('rendered', ''),
    'rank_math_description': target_meta.get('rank_math_description', ''),
    'rank_math_focus_keyword': target_meta.get('rank_math_focus_keyword', 'selank')
}
# Update Elementor meta via post meta (using WP REST API meta field)
if updates:
    print('Updating Elementor meta...')
    # First get the current post to have the latest meta
    current = get_post(2521)
    if current:
        current_meta = current.get('meta', {})
        current_meta.update(updates)
        data = {'meta': current_meta}
        upd_resp = update_post(2521, data)
        if upd_resp:
            print('Elementor meta update successful')
        else:
            print('Elementor meta update failed')
    else:
        print('Failed to fetch current post for update')
else:
    print('No Elementor data to update')
# Touch the post (update content to same content) to possibly trigger recalculation
print('Touching post content...')
content = target.get('content', {}).get('rendered', '')
title = target.get('title', {}).get('rendered', '')
excerpt = target.get('excerpt', {}).get('rendered', '')
touch_data = {
    'title': title,
    'content': content
}
if excerpt:
    touch_data['excerpt'] = excerpt
touch_resp = update_post(2521, touch_data)
if touch_resp:
    print('Post touch successful')
else:
    print('Post touch failed')
# Fetch updated post to get new score
print('Fetching updated post...')
updated = get_post(2521)
if updated:
    updated_meta = updated.get('meta', {})
    score_after = updated_meta.get('rank_math_seo_score', 0)
    print(f'Target Rank Math SEO score after: {score_after}')
    print(f'Change: {score_after} - {score_before} = {score_after - score_before}')
    # Also show Elementor meta
    print('Updated Elementor meta:')
    for k in ['_elementor_data', '_elementor_template_type']:
        if k in updated_meta:
            val = updated_meta[k]
            if isinstance(val, str) and len(val) > 100:
                print(f'  {k}: length {len(val)}')
            else:
                print(f'  {k}: {val}')
else:
    print('Failed to fetch updated post')