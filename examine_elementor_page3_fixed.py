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
        print(f'Type of parsed data: {type(data)}')
        if isinstance(data, list):
            print(f'It is a list with {len(data)} item(s)')
            # The first item is the root container
            root = data[0] if len(data) > 0 else {}
            print(f'Root element keys: {list(root.keys())}')
            if 'elements' in root:
                print(f'Root has {len(root["elements"])} child element(s)')
                # Examine first child (likely the HTML widget)
                for i, elem in enumerate(root['elements']):
                    print(f'  Child {i}:')
                    print(f'    ID: {elem.get("id")}')
                    print(f'    elType: {elem.get("elType")}')
                    print(f'    widgetType: {elem.get("widgetType", "N/A")}')
                    # Settings
                    settings = elem.get('settings', {})
                    if isinstance(settings, dict) and settings:
                        print(f'    Settings keys: {list(settings.keys())}')
                        # Look for html content
                        if 'html' in settings:
                            html_content = settings['html']
                            print(f'    HTML content length: {len(html_content)} chars')
                            # Show first 200 chars
                            print(f'    HTML preview: {html_content[:200]}')
                    else:
                        print(f'    Settings: {settings}')
                    # Nested elements
                    if 'elements' in elem:
                        print(f'    Has {len(elem["elements"])} nested elements')
                        for j, sub in enumerate(elem['elements'][:2]):  # show first 2
                            print(f'      Nested {j}: ID={sub.get("id")}, elType={sub.get("elType")}, widgetType={sub.get("widgetType","N/A")}')
            else:
                print('Root has no "elements"')
        else:
            print(f'Data is {type(data)}: {data}')
    except json.JSONDecodeError as e:
        print(f'Failed to parse as JSON: {e}')
        print('Data might be serialized PHP or other format')
else:
    print('No _elementor_data to parse')