from flask import Flask, request, jsonify
import anthropic, os, requests
from requests.auth import HTTPBasicAuth

app = Flask(__name__)
client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

WC_URL = os.environ.get("WOOCOMMERCE_URL", "")
WC_KEY = os.environ.get("WOOCOMMERCE_KEY", "")
WC_SECRET = os.environ.get("WOOCOMMERCE_SECRET", "")

def get_products(per_page=10):
    try:
        r = requests.get(
            f"{WC_URL}/wp-json/wc/v3/products",
            auth=HTTPBasicAuth(WC_KEY, WC_SECRET),
            params={"per_page": per_page, "status": "publish", "_fields": "id,name,short_description,slug"},
            timeout=15
        )
        return [{"id": p.get("id"), "name": p.get("name"), "short_description": p.get("short_description","")[:150], "slug": p.get("slug")} for p in r.json()]
    except Exception as e:
        return {"error": str(e)}

def update_product(product_id, data):
    try:
        r = requests.put(
            f"{WC_URL}/wp-json/wc/v3/products/{product_id}",
            auth=HTTPBasicAuth(WC_KEY, WC_SECRET),
            json=data,
            timeout=15
        )
        result = r.json()
        if "id" in result:
            return {"success": True, "id": product_id, "name": result.get("name")}
        return {"error": str(result)}
    except Exception as e:
        return {"error": str(e)}

def get_categories(per_page=20):
    try:
        r = requests.get(
            f"{WC_URL}/wp-json/wc/v3/products/categories",
            auth=HTTPBasicAuth(WC_KEY, WC_SECRET),
            params={"per_page": per_page, "_fields": "id,name,description,slug,count"},
            timeout=15
        )
        return [{"id": c.get("id"), "name": c.get("name"), "description": c.get("description","")[:150], "slug": c.get("slug"), "count": c.get("count")} for c in r.json()]
    except Exception as e:
        return {"error": str(e)}

def update_category(category_id, data):
    try:
        r = requests.put(
            f"{WC_URL}/wp-json/wc/v3/products/categories/{category_id}",
            auth=HTTPBasicAuth(WC_KEY, WC_SECRET),
            json=data,
            timeout=15
        )
        result = r.json()
        if "id" in result:
            return {"success": True, "id": category_id, "name": result.get("name")}
        return {"error": str(result)}
    except Exception as e:
        return {"error": str(e)}

SYSTEM = """Eres un agente SEO especializado para peptidosysuplementos.mx.

Puedes optimizar TITULOS, DESCRIPCIONES CORTAS de productos, y CATEGORIAS.

REGLAS PARA TITULOS DE PRODUCTOS:
- Maximo 60 caracteres
- Palabra clave principal al inicio
- Sin caracteres especiales innecesarios

REGLAS PARA DESCRIPCIONES CORTAS:
- Entre 130-160 caracteres
- Texto plano sin markdown ni asteriscos
- Incluir palabra clave, beneficio y llamada a accion

REGLAS PARA CATEGORIAS:
- Nombre claro con keyword principal
- Descripcion entre 130-160 caracteres
- Incluir palabras clave relevantes del nicho

Siempre usa las herramientas para obtener datos reales antes de proponer cambios.
Pide confirmacion antes de aplicar cualquier cambio.
Responde siempre en espanol."""

TOOLS = [
    {
        "name": "get_products",
        "description": "Obtiene productos de WooCommerce",
        "input_schema": {
            "type": "object",
            "properties": {
                "per_page": {"type": "integer", "default": 10}
            }
        }
    },
    {
        "name": "update_product",
        "description": "Actualiza titulo y/o descripcion corta de un producto",
        "input_schema": {
            "type": "object",
            "required": ["product_id"],
            "properties": {
                "product_id": {"type": "integer"},
                "name": {"type": "string", "description": "Nuevo titulo (max 60 chars)"},
                "short_description": {"type": "string", "description": "Nueva descripcion corta (130-160 chars, texto plano)"}
            }
        }
    },
    {
        "name": "get_categories",
        "description": "Obtiene categorias de productos de WooCommerce",
        "input_schema": {
            "type": "object",
            "properties": {
                "per_page": {"type": "integer", "default": 20}
            }
        }
    },
    {
        "name": "update_category",
        "description": "Actualiza nombre y/o descripcion de una categoria",
        "input_schema": {
            "type": "object",
            "required": ["category_id"],
            "properties": {
                "category_id": {"type": "integer"},
                "name": {"type": "string", "description": "Nuevo nombre de la categoria"},
                "description": {"type": "string", "description": "Nueva descripcion (130-160 chars, texto plano)"}
            }
        }
    }
]

def run_tool(name, inputs):
    if name == "get_products":
        return get_products(inputs.get("per_page", 10))
    elif name == "update_product":
        data = {k: inputs[k] for k in ["name", "short_description"] if k in inputs}
        return update_product(inputs["product_id"], data)
    elif name == "get_categories":
        return get_categories(inputs.get("per_page", 20))
    elif name == "update_category":
        data = {k: inputs[k] for k in ["name", "description"] if k in inputs}
        return update_category(inputs["category_id"], data)
    return {"error": "herramienta desconocida"}

@app.route("/")
def index():
    return open("templates/index.html").read()

@app.route("/chat", methods=["POST"])
def chat():
    try:
        messages = request.json.get("messages", [])
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=8192,
            system=SYSTEM,
            tools=TOOLS,
            messages=messages
        )
        while response.stop_reason == "tool_use":
            ac = []
            for b in response.content:
                if b.type == "tool_use":
                    ac.append({"type": "tool_use", "id": b.id, "name": b.name, "input": b.input})
                elif hasattr(b, "text"):
                    ac.append({"type": "text", "text": b.text})
            tr = []
            for b in response.content:
                if b.type == "tool_use":
                    tr.append({"type": "tool_result", "tool_use_id": b.id, "content": str(run_tool(b.name, b.input))})
            messages = messages + [
                {"role": "assistant", "content": ac},
                {"role": "user", "content": tr}
            ]
            response = client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=2048,
                system=SYSTEM,
                tools=TOOLS,
                messages=messages
            )
        reply = "".join(b.text for b in response.content if hasattr(b, "text"))
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"reply": f"Error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))