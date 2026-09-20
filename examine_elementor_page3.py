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

def get_wp_page(page_id):
    url = f'{WC_URL}/wp-json/wp/v2/pages/{page_id}?context=edit'
    r = requests.get(url, headers=wp_headers, timeout=10)
    if not r.ok:
        print(f'Error fetching page {page_id}:', r.text)
        return None
    return r.json()

page = get_wp_page(3)
if page is None:
    print('Failed to fetch page')
    exit(1)

meta = page.get('meta', {})
print('=== META FIELDS FOR PAGE ID 3 ===')
for key, value in meta.items():
    if key in ['_elementor_data', '_elementor_template_type', 'rank_math_seo_score', 'rank_math_title', 'rank_math_description']:
        print(f'{key}: {value}')
    elif key.startswith('_elementor') or key.startswith('rank_math'):
        print(f'{key}: {value}')

print()
print('=== FULL _ELEMENTOR_DATA (first 1000 chars) ===')
elementor_data = meta.get('_elementor_data')
if elementor_data:
    print(elementor_data[:1000])
    if len(elementor_data) > 1000:
        print('... (truncated)')
else:
    print('_elementor_data not found or empty')

print()
print('=== ATTEMPTING TO PARSE _ELEMENTOR_DATA AS JSON ===')
if elementor_data:
    try:
        data = json.loads(elementor_data)
        print('Successfully parsed as JSON')
        print(f'Top-level keys: {list(data.keys())}')
        if 'elements' in data:
            print(f'Number of top-level elements: {len(data["elements"])}')
            # Print structure of first few elements
            for i, elem in enumerate(data['elements'][:3]):
                print(f'  Element {i}:')
                print(f'    ID: {elem.get("id")}')
                print(f'    EL_TYPE: {elem.get("el_type")}')
                print(f'    Widget type: {elem.get("widgetType") if "widgetType" in elem else "N/A"}')
                # Look for content
                if 'elements' in elem:
                    print(f'    Has {len(elem["elements"])} nested elements')
                if isinstance(elem.get('settings'), dict):
                    settings = elem['settings']
                    # Look for common content fields
                    for key in ['title', 'text', 'editor', 'content', 'heading_title']:
                        if key in settings:
                            print(f'    Settings.{key}: {settings[key][:100] if isinstance(settings[key], str) and len(settings[key]) > 100 else settings[key]}')
        else:
            print('No "elements" key found in data')
    except json.JSONDecodeError as e:
        print(f'Failed to parse as JSON: {e}')
        print('Data might be serialized PHP or other format')
else:
    print('No _elementor_data to parse')