from flask import Flask, request, jsonify
import anthropic, os, requests
from requests.auth import HTTPBasicAuth

app = Flask(__name__)
client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

WC_URL = os.environ.get("WOOCOMMERCE_URL", "")
WC_KEY = os.environ.get("WOOCOMMERCE_KEY", "")
WC_SECRET = os.environ.get("WOOCOMMERCE_SECRET", "")

def get_products(per_page=5):
    try:
        r = requests.get(
            f"{WC_URL}/wp-json/wc/v3/products",
            auth=HTTPBasicAuth(WC_KEY, WC_SECRET),
            params={"per_page": per_page, "status": "publish", "_fields": "id,name,short_description,slug"},
            timeout=15
        )
        products = r.json()
        return [{"id": p.get("id"), "name": p.get("name"), "short_description": p.get("short_description","")[:100]} for p in products]
    except Exception as e:
        return {"error": str(e)}

def update_product(product_id, data):
    try:
        requests.put(f"{WC_URL}/wp-json/wc/v3/products/{product_id}", auth=HTTPBasicAuth(WC_KEY, WC_SECRET), json=data, timeout=15)
        return {"success": True, "id": product_id}
    except Exception as e:
        return {"error": str(e)}

SYSTEM = "Eres un agente SEO para peptidosysuplementos.mx. Usa get_products para ver productos reales antes de sugerir cambios. Pide confirmacion antes de usar update_product. Titulos SEO: max 60 chars, keyword al inicio. Responde en espanol."

TOOLS = [
    {"name": "get_products", "description": "Obtiene productos de WooCommerce", "input_schema": {"type": "object", "properties": {"per_page": {"type": "integer", "default": 5}}}},
    {"name": "update_product", "description": "Actualiza titulo o descripcion de un producto", "input_schema": {"type": "object", "required": ["product_id"], "properties": {"product_id": {"type": "integer"}, "name": {"type": "string"}, "short_description": {"type": "string"}}}}
]

def run_tool(name, inputs):
    if name == "get_products":
        return get_products(inputs.get("per_page", 5))
    elif name == "update_product":
        data = {k: inputs[k] for k in ["name","short_description"] if k in inputs}
        return update_product(inputs["product_id"], data)
    return {"error": "desconocida"}

@app.route("/")
def index():
    return open("templates/index.html").read()

@app.route("/chat", methods=["POST"])
def chat():
    try:
        messages = request.json.get("messages", [])
        response = client.messages.create(model="claude-sonnet-4-5", max_tokens=2048, system=SYSTEM, tools=TOOLS, messages=messages)
        while response.stop_reason == "tool_use":
            ac = [{"type": "tool_use", "id": b.id, "name": b.name, "input": b.input} if b.type == "tool_use" else {"type": "text", "text": b.text} for b in response.content]
            tr = [{"type": "tool_result", "tool_use_id": b.id, "content": str(run_tool(b.name, b.input))} for b in response.content if b.type == "tool_use"]
            messages = messages + [{"role": "assistant", "content": ac}, {"role": "user", "content": tr}]
            response = client.messages.create(model="claude-sonnet-4-5", max_tokens=2048, system=SYSTEM, tools=TOOLS, messages=messages)
        reply = "".join(b.text for b in response.content if hasattr(b, "text"))
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"reply": f"Error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
