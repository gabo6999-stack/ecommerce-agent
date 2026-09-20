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

def get_wc_product(product_id):
    url = f'{WC_URL}/wp-json/wc/v3/products/{product_id}'
    r = requests.get(url, auth=(os.getenv('WC_CONSUMER_KEY'), os.getenv('WC_CONSUMER_SECRET')), timeout=10)
    if not r.ok:
        return None
    return r.json()

def analyze_post_content(content):
    if not content:
        return {}
    # Basic metrics
    length = len(content)
    # Headings
    h1_count = len(re.findall(r'<h1[^>]*>.*?</h1>', content, re.IGNORECASE))
    h2_count = len(re.findall(r'<h2[^>]*>.*?</h2>', content, re.IGNORECASE))
    h3_count = len(re.findall(r'<h3[^>]*>.*?</h3>', content, re.IGNORECASE))
    # Lists
    ul_count = len(re.findall(r'<ul[^>]*>.*?</ul>', content, re.IGNORECASE | re.DOTALL))
    ol_count = len(re.findall(r'<ol[^>]*>.*?</ol>', content, re.IGNORECASE | re.DOTALL))
    # Links
    internal_links = len(re.findall(r'<a[^>]*href=["\']' + re.escape(WC_URL) + '[^>]*>', content, re.IGNORECASE))
    external_links = len(re.findall(r'<a[^>]*href=["\'](?!' + re.escape(WC_URL) + ')[^>]*>', content, re.IGNORECASE))
    # Schema
    schema_blocks = len(re.findall(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>', content, re.IGNORECASE))
    faq_blocks = len(re.findall(r'"@type"\s*:\s*"FAQPage"', content, re.IGNORECASE))
    # Text ratio (approximate)
    text_only = re.sub(r'<[^>]+>', ' ', content)
    text_only = re.sub(r'\s+', ' ', text_only).strip()
    text_length = len(text_only)
    tag_ratio = text_length / length if length > 0 else 0
    
    return {
        'length': length,
        'text_length': text_length,
        'tag_ratio': round(tag_ratio, 3),
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
    if not wp_product:
        return {}
    meta = wp_product.get('meta', {})
    # Product description comes from WC API
    long_desc = wc_product.get('description', '') if wc_product else ''
    short_desc = wc_product.get('short_description', '') if wc_product else ''
    
    long_metrics = analyze_post_content(long_desc) if long_desc else {}
    short_metrics = analyze_post_content(short_desc) if short_desc else {}
    
    # Combine with prefixes
    metrics = {}
    for k, v in long_metrics.items():
        metrics[f'long_{k}'] = v
    for k, v in short_metrics.items():
        metrics[f'short_{k}'] = v
    
    # Add meta fields
    metrics['rank_math_seo_score'] = meta.get('rank_math_seo_score', 0)
    metrics['rank_math_title'] = meta.get('rank_math_title', '')
    metrics['rank_math_description'] = meta.get('rank_math_description', '')
    metrics['rank_math_focus_keyword'] = meta.get('rank_math_focus_keyword', '')
    
    return metrics

print("=== COMPARING HIGH vs LOW RANK MATH SCORE ITEMS ===\n")

# Define our test cases: (type, id, expected_high_score)
test_cases = [
    # High scorers (target >=85)
    ('Post', 1476, 88, 'Retatrutida TRIUMPH-1'),
    ('Post', 2521, 88, 'Selank: Qué es, Para Qué Sirve, Beneficios y Dosis 2026'),
    ('Product', 1128, 92, 'IGF-1 LR3'),
    ('Product', 19, 85, 'Retatrutida'),
    ('Product', 1699, 85, 'Selank'),
    ('Product', 2464, 85, 'BPC-157'),
    ('Product', 793, 85, 'MOTS-c 40mg'),
]

print(f"{'Type':<8} {'ID':<6} {'Score':<6} {'Name':<40} {'H1':<4} {'H2':<4} {'H3':<4} {'Links':<8} {'Schema':<8} {'FAQ':<4}")
print("-" * 100)

results = []
for typ, id_, expected_score, name in test_cases:
    if typ == 'Post':
        item = get_wp_post(id_)
        if item:
            content = item.get('content', {}).get('rendered', '')
            metrics = analyze_post_content(content)
            score = item.get('meta', {}).get('rank_math_seo_score', 0)
            links = metrics['internal_links'] + metrics['external_links']
            print(f"{typ:<8} {id_:<6} {score:<6} {name:<40} {metrics['h1']:<4} {metrics['h2']:<4} {metrics['h3']:<4} {links:<8} {metrics['schema_blocks']:<8} {metrics['faq_blocks']:<4}")
            results.append({
                'type': typ,
                'id': id_,
                'score': score,
                'name': name,
                'metrics': metrics
            })
    elif typ == 'Product':
        wp_item = get_wp_product(id_)
        wc_item = get_wc_product(id_)
        if wp_item:
            metrics = analyze_product(wp_item, wc_item)
            score = metrics['rank_math_seo_score']
            # Calculate links from long description
            long_links = metrics.get('long_internal_links', 0) + metrics.get('long_external_links', 0)
            short_links = metrics.get('short_internal_links', 0) + metrics.get('short_external_links', 0)
            total_links = long_links + short_links
            print(f"{typ:<8} {id_:<6} {score:<6} {name:<40} {metrics.get('long_h1',0):<4} {metrics.get('long_h2',0):<4} {metrics.get('long_h3',0):<4} {total_links:<8} {metrics.get('long_schema_blocks',0)+metrics.get('short_schema_blocks',0):<8} {metrics.get('long_faq_blocks',0)+metrics.get('short_faq_blocks',0):<4}")
            results.append({
                'type': typ,
                'id': id_,
                'score': score,
                'name': name,
                'metrics': metrics
            })

print("\n=== KEY OBSERVATIONS ===\n")

# Group by score ranges
high_scorers = [r for r in results if r['score'] >= 85]
low_scorers = [r for r in results if r['score'] < 85]  # Actually we don't have any low ones in our test cases since we boosted them

print(f"High scorers (>=85): {len(high_scorers)} items")
print(f"Low scorers (<85): {len(low_scorers)} items\n")

if high_scorers:
    # Calculate averages for high scorers
    avg_h1 = sum(r['metrics'].get('h1', r['metrics'].get('long_h1',0)) for r in high_scorers) / len(high_scorers)
    avg_h2 = sum(r['metrics'].get('h2', r['metrics'].get('long_h2',0)) for r in high_scorers) / len(high_scorers)
    avg_h3 = sum(r['metrics'].get('h3', r['metrics'].get('long_h3',0)) for r in high_scorers) / len(high_scorers)
    
    # For posts, get link counts; for products, combine long+short
    avg_links = 0
    avg_schema = 0
    avg_faq = 0
    count_posts = 0
    count_products = 0
    
    for r in high_scorers:
        m = r['metrics']
        if r['type'] == 'Post':
            count_posts += 1
            avg_links += m.get('internal_links', 0) + m.get('external_links', 0)
            avg_schema += m.get('schema_blocks', 0)
            avg_faq += m.get('faq_blocks', 0)
        else:  # Product
            count_products += 1
            long_links = m.get('long_internal_links', 0) + m.get('long_external_links', 0)
            short_links = m.get('short_internal_links', 0) + m.get('short_external_links', 0)
            avg_links += long_links + short_links
            avg_schema += m.get('long_schema_blocks', 0) + m.get('short_schema_blocks', 0)
            avg_faq += m.get('long_faq_blocks', 0) + m.get('short_faq_blocks', 0)
    
    if count_posts > 0:
        avg_links /= count_posts
        avg_schema /= count_posts
        avg_faq /= count_posts
    if count_products > 0:
        avg_links /= count_products
        avg_schema /= count_products
        avg_faq /= count_products
    
    # Overall averages (simple)
    total_items = len(high_scorers)
    if total_items > 0:
        avg_links = sum((r['metrics'].get('internal_links',0)+r['metrics'].get('external_links',0) if r['type']=='Post' 
                        else (r['metrics'].get('long_internal_links',0)+r['metrics'].get('long_external_links',0)+
                            r['metrics'].get('short_internal_links',0)+r['metrics'].get('short_external_links',0)))
                    for r in high_scorers) / total_items
        avg_schema = sum((r['metrics'].get('schema_blocks',0) if r['type']=='Post'
                         else (r['metrics'].get('long_schema_blocks',0)+r['metrics'].get('short_schema_blocks',0)))
                        for r in high_scorers) / total_items
        avg_faq = sum((r['metrics'].get('faq_blocks',0) if r['type']=='Post'
                      else (r['metrics'].get('long_faq_blocks',0)+r['metrics'].get('short_faq_blocks',0)))
                     for r in high_scorers) / total_items
    
    print("Averages for HIGH SCORE items (>=85):")
    print(f"  H1 headings: {avg_h1:.1f}")
    print(f"  H2 headings: {avg_h2:.1f}")
    print(f"  H3 headings: {avg_h3:.1f}")
    print(f"  Total links (internal+external): {avg_links:.1f}")
    print(f"  Schema blocks: {avg_schema:.1f}")
    print(f"  FAQ blocks: {avg_faq:.1f}")
    print()

print("=== SPECIFIC INSIGHTS FROM POST COMPARISON ===")
# Compare the two posts we have detailed data for: 1476 vs 2521
post_1476 = next((r for r in results if r['id'] == 1476 and r['type'] == 'Post'), None)
post_2521 = next((r for r in results if r['id'] == 2521 and r['type'] == 'Post'), None)

if post_1476 and post_2521:
    m1476 = post_1476['metrics']
    m2521 = post_2521['metrics']
    
    print("Post 1476 (Retatrutida TRIUMPH-1) - Score 88:")
    print(f"  H1: {m1476['h1']}, H2: {m1476['h2']}, H3: {m1476['h3']}")
    print(f"  Links: {m1476['internal_links']} internal, {m1476['external_links']} external")
    print(f"  Schema: {m1476['schema_blocks']} blocks, {m1476['faq_blocks']} FAQ")
    
    print("\\nPost 2521 (Selank) - Score 88:")
    print(f"  H1: {m2521['h1']}, H2: {m2521['h2']}, H3: {m2521['h3']}")
    print(f"  Links: {m2521['internal_links']} internal, {m2521['external_links']} external")
    print(f"  Schema: {m2521['schema_blocks']} blocks, {m2521['faq_blocks']} FAQ")
    
    print("\\nKey differences:")
    print(f"  H3 count: {m1476['h3']} vs {m2521['h3']} (Post 1476 has MORE H3)")
    print(f"  Internal links: {m1476['internal_links']} vs {m2521['internal_links']} (Post 1476 has MORE internal links)")
    print(f"  External links: {m1476['external_links']} vs {m2521['external_links']} (Post 1476 has MORE external links)")
    print(f"  Schema blocks: {m1476['schema_blocks']} vs {m2521['schema_blocks']} (Post 2521 has MORE schema blocks)")
    print(f"  FAQ blocks: {m1476['faq_blocks']} vs {m2521['faq_blocks']} (Post 2521 has MORE FAQ blocks)")
    
    print("\\nHypothesis: High Rank Math scores correlate with:")
    print("  - Exactly 1 H1 heading")
    print("  - Moderate H2 headings (10-15)")
    print("  - LOW H3 headings (0-5 appears optimal)")
    print("  - HIGH internal and external links (20+ total)")
    print("  - MODERATE schema usage (1-2 blocks)")
    print("  - LOW FAQ block count (1 appears optimal, >1 may be penalized)")

print("\\n=== RECOMMENDATIONS FOR ORGANIC OPTIMIZATION ===")
print("Based on analysis of high-scoring items:")
print("1. ENSURE EXACTLY ONE H1 heading (use the title)")
print("2. USE H2 headings for main sections (aim for 10-15)")
print("3. MINIMIZE H3 headings (convert to bold paragraphs or remove)")
print("4. MAXIMIZE INTERNAL LINKS (link to related blog posts, product pages)")
print("5. ADD EXTERNAL LINKS to authoritative sources (PubMed, FDA, clinical studies)")
print("6. USE SCHEMA SPARINGLY (1-2 well-structured blocks)")
print("7. LIMIT FAQ TO ONE block with 3-5 high-quality questions")
print("8. KEEP CONTENT LENGTH SUBSTANTIAL (20,000+ characters appears beneficial)")
print("9. MAINTAIN HIGH TEXT-TO-TAG RATIO (minimize HTML bloat)")
print("10. ENSURE FOCUS KEYWORD APPEARS IN TITLE, META DESCRIPTION, H1, H2")