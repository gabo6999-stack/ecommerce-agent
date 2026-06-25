import os
import json
import requests
import anthropic
from datetime import datetime
from dotenv import load_dotenv

try:
    from fpdf import FPDF
    FPDF_AVAILABLE = True
except ImportError:
    FPDF_AVAILABLE = False

load_dotenv()

# ── WooCommerce ─────────────────────────────────────────────────────────────
WC_URL    = os.getenv("WC_STORE_URL", "").rstrip("/")
WC_AUTH   = (os.getenv("WC_CONSUMER_KEY", ""), os.getenv("WC_CONSUMER_SECRET", ""))
WC_BASE   = f"{WC_URL}/wp-json/wc/v3"

def wc_get(endpoint, params=None):
    try:
        r = requests.get(f"{WC_BASE}/{endpoint}", auth=WC_AUTH, params=params or {}, timeout=30)
        r.raise_for_status()
        return r.json()
    except requests.RequestException as e:
        return {"error": str(e)}

# ── Tool implementations ─────────────────────────────────────────────────────

def get_products(search=None, category=None, status="publish", limit=20,
                 orderby="popularity", order="desc"):
    params = {"per_page": min(int(limit), 100), "status": status,
              "orderby": orderby, "order": order}
    if search:
        params["search"] = search
    if category:
        params["category"] = category
    data = wc_get("products", params)
    if isinstance(data, list):
        return [
            {
                "id": p["id"],
                "name": p["name"],
                "price": p["price"],
                "regular_price": p["regular_price"],
                "sale_price": p["sale_price"],
                "stock_status": p["stock_status"],
                "stock_quantity": p.get("stock_quantity"),
                "categories": [c["name"] for c in p["categories"]],
                "total_sales": p["total_sales"],
                "average_rating": p["average_rating"],
                "short_description": p.get("short_description", "")[:200],
            }
            for p in data
        ]
    return data


def get_product_details(product_id):
    p = wc_get(f"products/{product_id}")
    if "error" in (p if isinstance(p, dict) else {}):
        return p
    return {
        "id": p["id"],
        "name": p["name"],
        "description": p.get("description", "")[:600],
        "short_description": p.get("short_description", ""),
        "price": p["price"],
        "regular_price": p["regular_price"],
        "sale_price": p["sale_price"],
        "stock_status": p["stock_status"],
        "stock_quantity": p.get("stock_quantity"),
        "categories": [c["name"] for c in p["categories"]],
        "tags": [t["name"] for t in p.get("tags", [])],
        "total_sales": p["total_sales"],
        "average_rating": p["average_rating"],
        "rating_count": p["rating_count"],
        "attributes": p.get("attributes", []),
    }


def get_categories(limit=50):
    params = {"per_page": min(int(limit), 100), "orderby": "count",
              "order": "desc", "hide_empty": True}
    data = wc_get("products/categories", params)
    if isinstance(data, list):
        return [{"id": c["id"], "name": c["name"], "count": c["count"]} for c in data]
    return data


def get_orders(status=None, customer_email=None, limit=20, after=None, before=None):
    params = {"per_page": min(int(limit), 100)}
    if status:
        params["status"] = status
    if customer_email:
        params["customer"] = customer_email
    if after:
        params["after"] = after
    if before:
        params["before"] = before
    data = wc_get("orders", params)
    if isinstance(data, list):
        return [
            {
                "id": o["id"],
                "status": o["status"],
                "date_created": o["date_created"],
                "total": o["total"],
                "currency": o["currency"],
                "customer_email": o["billing"].get("email"),
                "customer_name": (
                    f"{o['billing'].get('first_name','')} "
                    f"{o['billing'].get('last_name','')}".strip()
                ),
                "items": [
                    {"name": i["name"], "quantity": i["quantity"], "total": i["total"]}
                    for i in o["line_items"]
                ],
            }
            for o in data
        ]
    return data


def get_sales_report(period="month", date_min=None, date_max=None):
    params = {"period": period}
    if date_min:
        params["date_min"] = date_min
    if date_max:
        params["date_max"] = date_max
    return wc_get("reports/sales", params)


def get_top_sellers(period="month", limit=10):
    params = {"period": period, "per_page": min(int(limit), 100)}
    return wc_get("reports/top_sellers", params)


def compare_mexico_prices(query, limit=5):
    try:
        r = requests.get(
            "https://api.mercadolibre.com/sites/MLM/search",
            params={"q": query, "limit": limit, "condition": "new"},
            timeout=15,
        )
        r.raise_for_status()
        data = r.json()
        results = [
            {
                "title": item["title"],
                "price_mxn": item["price"],
                "seller": item.get("seller", {}).get("nickname", ""),
                "sold_quantity": item.get("sold_quantity", 0),
                "url": item["permalink"],
            }
            for item in data.get("results", [])[:int(limit)]
        ]
        return {"query": query, "market": "MercadoLibre Mexico", "listings": results}
    except Exception as e:
        return {"error": str(e)}


# ── Tool dispatcher ──────────────────────────────────────────────────────────
TOOL_FNS = {
    "get_products":          get_products,
    "get_product_details":   get_product_details,
    "get_categories":        get_categories,
    "get_orders":            get_orders,
    "get_sales_report":      get_sales_report,
    "get_top_sellers":       get_top_sellers,
    "compare_mexico_prices": compare_mexico_prices,
}

def execute_tool(name, inputs):
    fn = TOOL_FNS.get(name)
    if not fn:
        return {"error": f"Unknown tool: {name}"}
    try:
        return fn(**inputs)
    except Exception as e:
        return {"error": str(e)}


# ── Claude setup ─────────────────────────────────────────────────────────────
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
MODEL  = "claude-opus-4-7"

SYSTEM = [
    {
        "type": "text",
        "text": (
            "You are an expert e-commerce assistant for Péptidos y Suplementos "
            "(peptidosysuplementos.mx), a Mexican online store specializing in peptides, "
            "supplements, and health products.\n\n"
            "Your capabilities:\n"
            "- **Product Recommendations**: Suggest products based on customer goals "
            "(muscle gain, weight loss, recovery, anti-aging, cognitive performance, etc.)\n"
            "- **Customer Support**: Look up orders by email, answer questions about "
            "products, shipping, and returns\n"
            "- **Marketing & Campaigns**: Generate compelling ad copy and social media "
            "content; advise on the best posting times for Mexican audiences on Instagram, "
            "Facebook, and TikTok\n"
            "- **Analytics & Insights**: Analyze sales trends, identify top/bottom "
            "performing products, surface actionable patterns\n"
            "- **Mexico Market Price Comparison**: Compare store prices against "
            "MercadoLibre Mexico to assess competitiveness\n\n"
            "Guidelines:\n"
            "- Always respond in the same language the user writes in (Spanish or English)\n"
            "- Be specific and data-driven — pull real store data before making recommendations\n"
            "- When recommending products, explain WHY they match the customer's needs\n"
            "- For marketing advice, consider Mexican market context: pay days fall on the "
            "1st and 15th of each month, peak fitness motivation is Jan–Mar and Aug–Sep\n"
            "- All prices are in MXN unless noted otherwise\n"
            f"- Today's date is {datetime.now().strftime('%Y-%m-%d')}"
        ),
        "cache_control": {"type": "ephemeral"},
    }
]

TOOLS = [
    {
        "name": "get_products",
        "description": (
            "Fetch products from the WooCommerce store. "
            "Filter by keyword, category ID, or sort by popularity/price/rating."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "search":   {"type": "string",  "description": "Keyword to search products"},
                "category": {"type": "string",  "description": "Category ID (use get_categories to get IDs)"},
                "status":   {"type": "string",  "description": "publish or draft", "default": "publish"},
                "limit":    {"type": "integer", "description": "Max results (up to 100)", "default": 20},
                "orderby":  {"type": "string",  "description": "date | popularity | rating | price", "default": "popularity"},
                "order":    {"type": "string",  "description": "asc or desc", "default": "desc"},
            },
        },
    },
    {
        "name": "get_product_details",
        "description": "Get full details for a specific product: description, attributes, ratings, stock.",
        "input_schema": {
            "type": "object",
            "properties": {
                "product_id": {"type": "integer", "description": "WooCommerce product ID"},
            },
            "required": ["product_id"],
        },
    },
    {
        "name": "get_categories",
        "description": "List all product categories with product counts.",
        "input_schema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "default": 50},
            },
        },
    },
    {
        "name": "get_orders",
        "description": "Fetch store orders. Filter by status, customer email, or date range.",
        "input_schema": {
            "type": "object",
            "properties": {
                "status":           {"type": "string", "description": "pending | processing | on-hold | completed | cancelled | refunded | failed"},
                "customer_email":   {"type": "string", "description": "Look up orders for a specific customer"},
                "limit":            {"type": "integer", "default": 20},
                "after":            {"type": "string", "description": "ISO 8601 start date, e.g. 2026-01-01T00:00:00"},
                "before":           {"type": "string", "description": "ISO 8601 end date"},
            },
        },
    },
    {
        "name": "get_sales_report",
        "description": "Aggregated sales report: total revenue, order count, average order value.",
        "input_schema": {
            "type": "object",
            "properties": {
                "period":   {"type": "string", "description": "week | month | last_month | year", "default": "month"},
                "date_min": {"type": "string", "description": "Start date YYYY-MM-DD"},
                "date_max": {"type": "string", "description": "End date YYYY-MM-DD"},
            },
        },
    },
    {
        "name": "get_top_sellers",
        "description": "Best-selling products by units sold for a given period.",
        "input_schema": {
            "type": "object",
            "properties": {
                "period": {"type": "string", "description": "week | month | last_month | year", "default": "month"},
                "limit":  {"type": "integer", "default": 10},
            },
        },
    },
    {
        "name": "compare_mexico_prices",
        "description": (
            "Search MercadoLibre Mexico for a product and return current market prices "
            "so you can assess whether the store's pricing is competitive."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string",  "description": "Product name or keywords to search"},
                "limit": {"type": "integer", "description": "Number of listings to compare", "default": 5},
            },
            "required": ["query"],
        },
    },
]


# ── History persistence ───────────────────────────────────────────────────────
HISTORY_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sessions")


def _serialize_content(content):
    if isinstance(content, str):
        return content
    return [block.model_dump() if hasattr(block, "model_dump") else block for block in content]


def _extract_text(content):
    """Extrae texto limpio de content (str o lista de bloques)."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", ""))
        return " ".join(parts)
    return str(content)


def save_session(messages):
    os.makedirs(HISTORY_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    path = os.path.join(HISTORY_DIR, f"session_{timestamp}.json")
    payload = [{"role": m["role"], "content": _serialize_content(m["content"])} for m in messages]

    # ── JSON ────────────────────────────────────────────────────────────────
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    # ── PDF ─────────────────────────────────────────────────────────────────
    if FPDF_AVAILABLE:
        pdf_path = path.replace(".json", ".pdf")
        _export_pdf(payload, pdf_path, timestamp)
        print(f"  [PDF saved  → {pdf_path}]")
    else:
        print("  [fpdf2 no instalado — ejecuta: pip install fpdf2]")

    return path


def _export_pdf(payload, pdf_path, timestamp):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # ── Encabezado ──────────────────────────────────────────────────────────
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_fill_color(30, 30, 30)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 12, "Peptidos y Suplementos - Sesion de Agente", fill=True, ln=True, align="C")

    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 7, f"Generado: {timestamp.replace('_', ' ')}  |  {len(payload)} mensajes",
             ln=True, align="C")
    pdf.ln(6)

    # ── Mensajes ────────────────────────────────────────────────────────────
    for msg in payload:
        role = msg["role"]
        text = _extract_text(msg["content"]).strip()
        if not text:
            continue

        # Saltar mensajes de herramientas internos
        if role == "user" and isinstance(msg["content"], list):
            if all(isinstance(b, dict) and b.get("type") == "tool_result"
                   for b in msg["content"]):
                continue

        is_user = role == "user"

        # Etiqueta de rol
        pdf.set_font("Helvetica", "B", 8)
        if is_user:
            pdf.set_text_color(255, 255, 255)
            pdf.set_fill_color(37, 99, 235)     # azul
        else:
            pdf.set_text_color(255, 255, 255)
            pdf.set_fill_color(22, 163, 74)     # verde

        label = "  Tu  " if is_user else "  Agente  "
        pdf.cell(0, 6, label, fill=True, ln=True)

        # Contenido del mensaje
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(30, 30, 30)
        if is_user:
            pdf.set_fill_color(235, 244, 255)   # azul muy claro
        else:
            pdf.set_fill_color(240, 253, 244)   # verde muy claro

        # Limpiar caracteres no compatibles con latin-1
        safe_text = text.encode("latin-1", errors="replace").decode("latin-1")
        pdf.multi_cell(0, 6, safe_text, fill=True)
        pdf.ln(4)

    pdf.output(pdf_path)

def load_last_session():
    if not os.path.isdir(HISTORY_DIR):
        return []
    files = sorted(
        f for f in os.listdir(HISTORY_DIR)
        if f.startswith("session_") and f.endswith(".json")
    )
    if not files:
        return []
    path = os.path.join(HISTORY_DIR, files[-1])
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ── Main loop ────────────────────────────────────────────────────────────────
def run():
    messages = []
    print("\n" + "=" * 60)
    print("  Péptidos y Suplementos — E-commerce Agent")
    print("  Powered by Claude  |  'exit' / 'salir' to quit")
    print("=" * 60 + "\n")

    prior = load_last_session()
    if prior:
        print(f"  [Found previous session — {len(prior)} messages.]")
        try:
            resume = input("  Continue from last session? (y/n): ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            resume = "n"
        if resume == "y":
            messages = prior
            print(f"  [Loaded {len(messages)} messages.]\n")
        else:
            print("  [Starting fresh session.]\n")

    try:
        while True:
            try:
                user_input = input("You: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nAgent: ¡Hasta luego!")
                break

            if not user_input:
                continue
            if user_input.lower() in ("exit", "salir", "quit"):
                print("Agent: ¡Hasta luego!")
                break

            messages.append({"role": "user", "content": user_input})

            # agentic loop — only continue while the model is asking us to run tools.
            # Any other stop_reason (end_turn, max_tokens, stop_sequence, refusal,
            # pause_turn, …) ends the turn; otherwise we'd loop back to the API with
            # an assistant-final messages list and trigger
            # "conversation must end with a user message".
            while True:
                response = client.messages.create(
                    model=MODEL,
                    max_tokens=4096,
                    system=SYSTEM,
                    tools=TOOLS,
                    messages=messages,
                )

                messages.append({"role": "assistant", "content": response.content})

                if response.stop_reason == "tool_use":
                    tool_results = []
                    for block in response.content:
                        if block.type == "tool_use":
                            print(f"  [→ {block.name}]", flush=True)
                            result = execute_tool(block.name, block.input)
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": json.dumps(result, ensure_ascii=False),
                            })

                    if tool_results:
                        messages.append({"role": "user", "content": tool_results})
                        continue
                    # stop_reason said tool_use but no tool_use blocks were emitted —
                    # fall through and end the turn rather than send an empty user msg.

                for block in response.content:
                    if hasattr(block, "text") and block.text:
                        print(f"\nAgent: {block.text}\n")
                if response.stop_reason not in ("end_turn", "tool_use"):
                    print(f"  [stop_reason: {response.stop_reason}]")
                break
    finally:
        if messages:
            path = save_session(messages)
            print(f"  [Session saved → {path}]")


if __name__ == "__main__":
    run()
