import os, json, requests, re, time, statistics
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

def get_wp_page(page_id):
    url = f'{WC_URL}/wp-json/wp/v2/pages/{page_id}?context=edit'
    r = requests.get(url, headers=wp_headers, timeout=15)
    if not r.ok:
        return None
    return r.json()

def analyze_content(content):
    if not content:
        return {}
    length = len(content)
    h1_count = len(re.findall(r'<h1[^>]*>.*?</h1>', content, re.IGNORECASE))
    h2_count = len(re.findall(r'<h2[^>]*>.*?</h2>', content, re.IGNORECASE))
    h3_count = len(re.findall(r'<h3[^>]*>.*?</h3>', content, re.IGNORECASE))
    ul_count = len(re.findall(r'<ul[^>]*>.*?</ul>', content, re.IGNORECASE | re.DOTALL))
    ol_count = len(re.findall(r'<ol[^>]*>.*;</ol>', content, re.IGNORECASE | re.DOTALL))
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

print('Fetching all pages for organic analysis...')
# Get all pages
page = 1
all_pages = []
while True:
    url = f'{WC_URL}/wp-json/wp/v2/pages?per_page=100&page={page}'
    r = requests.get(url, headers=wp_headers, timeout=15)
    if not r.ok:
        print(f'Error fetching page list page {page}:', r.text)
        break
    data = r.json()
    if not data:
        break
    all_pages.extend(data)
    if len(data) < 100:
        break
    page += 1

print(f'Found {len(all_pages)} pages')
print('Analyzing content...')
page_data = []
for p in all_pages:
    pid = p['id']
    title = p.get('title', {}).get('rendered', '').strip()
    page_obj = get_wp_page(pid)
    if not page_obj:
        print(f'  Skipping page ID {pid} (could not fetch)')
        continue
    content = page_obj.get('content', {}).get('rendered', '')
    meta = page_obj.get('meta', {})
    score = meta.get('rank_math_seo_score', 0)
    metrics = analyze_content(content)
    page_data.append({
        'id': pid,
        'title': title,
        'score': score,
        'metrics': metrics
    })
    # progress
    if len(page_data) % 5 == 0:
        print(f'  Processed {len(page_data)} pages...')

print(f'\\nAnalyzed {len(page_data)} pages successfully.')

# Compute statistics
if page_data:
    lengths = [p['metrics']['length'] for p in page_data]
    h1s = [p['metrics']['h1'] for p in page_data]
    h2s = [p['metrics']['h2'] for p in page_data]
    h3s = [p['metrics']['h3'] for p in page_data]
    internals = [p['metrics']['internal_links'] for p in page_data]
    externals = [p['metrics']['external_links'] for p in page_data]
    schemas = [p['metrics']['schema_blocks'] for p in page_data]
    faqs = [p['metrics']['faq_blocks'] for p in page_data]
    
    print('\\n=== SUMMARY STATISTICS FOR ALL PAGES ===')
    print(f'Content length: avg {statistics.mean(lengths):.0f}, min {min(lengths)}, max {max(lengths)}')
    print(f'H1 count: avg {statistics.mean(h1s):.2f}, min {min(h1s)}, max {max(h1s)}')
    print(f'H2 count: avg {statistics.mean(h2s):.2f}, min {min(h2s)}, max {max(h2s)}')
    print(f'H3 count: avg {statistics.mean(h3s):.2f}, min {min(h3s)}, max {max(h3s)}')
    print(f'Internal links: avg {statistics.mean(internals):.2f}, min {min(internals)}, max {max(internals)}')
    print(f'External links: avg {statistics.mean(externals):.2f}, min {min(externals)}, max {max(externals)}')
    print(f'Schema blocks: avg {statistics.mean(schemas):.2f}, min {min(schemas)}, max {max(schemas)}')
    print(f'FAQ blocks: avg {statistics.mean(faqs):.2f}, min {min(faqs)}, max {max(faqs)}')
    
    # Count pages meeting optimal criteria from our earlier analysis
    optimal_h1 = sum(1 for p in page_data if p['metrics']['h1'] == 1)
    optimal_h2 = sum(1 for p in page_data if 10 <= p['metrics']['h2'] <= 15)
    optimal_h3 = sum(1 for p in page_data if p['metrics']['h3'] <= 5)
    optimal_links = sum(1 for p in page_data if (p['metrics']['internal_links'] + p['metrics']['external_links']) >= 20)
    optimal_schema = sum(1 for p in page_data if 1 <= p['metrics']['schema_blocks'] <= 2)
    optimal_faq = sum(1 for p in page_data if p['metrics']['faq_blocks'] == 1)
    optimal_length = sum(1 for p in page_data if p['metrics']['length'] >= 20000)
    
    print(f'\\n=== PAGES MEETING OPTIMAL CRITERIA ===')
    print(f'Exactly 1 H1: {optimal_h1}/{len(page_data)} ({optimal_h1/len(page_data)*100:.1f}%)')
    print(f'H2 in 10-15 range: {optimal_h2}/{len(page_data)} ({optimal_h2/len(page_data)*100:.1f}%)')
    print(f'H3 ≤5: {optimal_h3}/{len(page_data)} ({optimal_h3/len(page_data)*100:.1f}%)')
    print(f'Total links ≥20: {optimal_links}/{len(page_data)} ({optimal_links/len(page_data)*100:.1f}%)')
    print(f'Schema blocks 1-2: {optimal_schema}/{len(page_data)} ({optimal_schema/len(page_data)*100:.1f}%)')
    print(f'Exactly 1 FAQ: {optimal_faq}/{len(page_data)} ({optimal_faq/len(page_data)*100:.1f}%)')
    print(f'Length ≥20,000 chars: {optimal_length}/{len(page_data)} ({optimal_length/len(page_data)*100:.1f}%)')
    
    # Identify pages that are far from optimal in multiple areas
    print(f'\\n=== PAGES WITH MULTIPLE GAPS (>=3 criteria not met) ===')
    gaps_list = []
    for p in page_data:
        gaps = 0
        if p['metrics']['h1'] != 1:
            gaps += 1
        if not (10 <= p['metrics']['h2'] <= 15):
            gaps += 1
        if p['metrics']['h3'] > 5:
            gaps += 1
        if (p['metrics']['internal_links'] + p['metrics']['external_links']) < 20:
            gaps += 1
        if not (1 <= p['metrics']['schema_blocks'] <= 2):
            gaps += 1
        if p['metrics']['faq_blocks'] != 1:
            gaps += 1
        if p['metrics']['length'] < 20000:
            gaps += 1
        if gaps >= 3:
            gaps_list.append((p['id'], p['title'], p['score'], gaps))
    
    if gaps_list:
        gaps_list.sort(key=lambda x: x[3], reverse=True)
        for pid, title, score, gap_count in gaps_list[:10]:  # top 10 worst
            print(f'  ID {pid}: "{title[:40]}..." (score {score}) - {gap_count}/7 criteria not met')
    else:
        print('  No pages with 3 or more gaps found.')
    
    # Show top scoring pages for reference
    print(f'\\n=== TOP 5 PAGES BY RANK MATH SCORE ===')
    top_by_score = sorted(page_data, key=lambda x: x['score'], reverse=True)[:5]
    for p in top_by_score:
        print(f'  ID {p["id"]}: "{p["title"][:40]}..." - score {p["score"]}')
    
    print(f'\\n=== RECOMMENDATIONS FOR BATCH ORGANIC OPTIMIZATION ===')
    print('Based on aggregate deficiencies, prioritize:')
    deficiencies = []
    if optimal_h1 < len(page_data) * 0.8:  # if less than 80% have optimal H1
        deficiencies.append('Ensure exactly 1 H1 per page (most common issue)')
    if optimal_h2 < len(page_data) * 0.5:
        deficiencies.append('Adjust H2 count to 10-15 range')
    if optimal_h3 < len(page_data) * 0.7:
        deficiencies.append('Reduce H3 count to ≤5 (convert to bold text)')
    if optimal_links < len(page_data) * 0.3:
        deficiencies.append('Dramatically increase internal and external links (aim ≥20 total)')
    if optimal_schema < len(page_data) * 0.5:
        deficiencies.append('Add schema structured data (1-2 blocks per page)')
    if optimal_faq < len(page_data) * 0.4:
        deficiencies.append('Add exactly 1 FAQ block with 3-5 quality questions')
    if optimal_length < len(page_data) * 0.3:
        deficiencies.append('Increase content length to ≥20,000 characters where appropriate')
    
    if deficiencies:
        for i, d in enumerate(deficiencies, 1):
            print(f'{i}. {d}')
    else:
        print('  Most pages already meet organic criteria - focus on fine-tuning.')
    
    print('\\n--- SAMPLE PAGE-TO-PAGE ACTIONS ---')
    print('For a quick win, consider updating these pages first (high traffic or important):')
    # Suggest pages that are important but have gaps
    important_keywords = ['politica', 'privacidad', 'devolucion', 'terminos', 'blog', 'productos', 'catalogo']
    important_pages = [p for p in page_data if any(kw in p['title'].lower() for kw in important_keywords)]
    if important_pages:
        important_pages.sort(key=lambda x: x['score'])  # lowest score first
        for p in important_pages[:5]:
            print(f'  ID {p["id"]}: "{p["title"]}" (score {p["score"]})')
    else:
        print('  No important pages identified by keyword.')

else:
    print('No page data collected.')

print('\\n=== NEXT STEPS ===')
print('1. Review the above recommendations')
print('2. Select a few high-priority pages to apply organic optimizations manually (via WordPress editor)')
print('3. After applying changes, wait for Rank Math to re-evaluate (may take some time or require manual refresh)')
print('4. Measure the impact on Rank Math scores organically')
print('5. If successful, replicate the pattern across other pages')
print('6. Consider creating content templates or guidelines based on the optimal patterns identified')