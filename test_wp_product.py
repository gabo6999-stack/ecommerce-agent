import os
from dotenv import load_dotenv
load_dotenv(r'C:\Users\gabom\Proyectos\ecommerce-agent\ecommerce-agent__.env')
WC_URL = os.getenv('WC_STORE_URL').rstrip('/')
WP_USER = os.getenv('WP_USER')
WP_PASSWORD = os.getenv('WP_PASSWORD')
print('WC_URL:', WC_URL)
print('WP_USER:', WP_USER)
print('WP_PASSWORD set:', bool(WP_PASSWORD))
# JWT
import requests
jwt_url = f'{WC_URL}/wp-json/jwt-auth/v1/token'
resp = requests.post(jwt_url, json={'username': WP_USER, 'password': WP_PASSWORD}, timeout=15)
print('JWT status:', resp.status_code)
if resp.ok:
    token = resp.json().get('token')
    print('Token obtained')
    headers = {'Authorization': f'Bearer {token}'}
    # Try to get product 2464 as WP post (product post type)
    r = requests.get(f'{WC_URL}/wp-json/wp/v2/products/2464?context=edit', headers=headers, timeout=15)
    print('WP product status:', r.status_code)
    if r.ok:
        print('Success')
        data = r.json()
        print('Title:', data.get('title', {}).get('rendered', ''))
        print('Meta keys:', list(data.get('meta', {}).keys()))
    else:
        print('Error:', r.text)
else:
    print('Failed to get token:', resp.text)