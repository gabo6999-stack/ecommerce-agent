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
            return {"success": True, "id": product_id, "name": result.get("name"), "short_description": result.get("short_description","")}
        return {"error": str(result)}
    except Exception as e:
        return {"error": str(e)}

SYSTEM = """Eres un agente SEO especializado para peptidosysuplementos.mx.

Tu funcion es optimizar TITULOS y DESCRIPCIONES CORTAS de productos WooCommerce.

REGLAS PARA TITULOS:
- Maximo 60 caracteres
- Palabra clave principal al inicio
- Sin caracteres especiales innecesarios
- Ejemplo: "Tirzepatida 60mg | Peptido GLP-1 Mexico"

REGLAS PARA DESCRIPCIONES CORTAS:
- Entre 130-160 caracteres
- Incluir palabra clave principal
- Mencionar beneficio principal
- Incluir llamada a accion
- Texto plano sin markdown ni asteriscos
- Ejemplo: "Tirzepatida 60mg peptido analogo GLP-1 para control de peso. Alta pureza, envio express Mexico. Compra segura con factura."

FLUJO DE TRABAJO:
1. Usa get_products para obtener productos reales
2. Analiza titulos y descripciones cortas actuales
3. Propone mejoras concretas
4. Pide confirmacion antes de aplicar
5. Aplica cambios con update_product uno por uno

Responde siempre en espanol. Se conciso y profesional."""

TOOLS = [
    {
        "name": "get_products",
        "description": "Obtiene productos de WooCommerce con id, nombre, descripcion corta y slug",
        "input_schema": {
            "type": "object",
            "properties": {
                "per_page": {"type": "integer", "description": "Numero de productos (max 10)", "default": 10}
            }
        }
    },
    {
        "name": "update_product",
        "description": "Actualiza el titulo y/o descripcion corta de un producto en WooCommerce",
        "input_schema": {
            "type": "object",
            "required": ["product_id"],
            "properties": {
                "product_id": {"type": "integer", "description": "ID del producto"},
                "name": {"type": "string", "description": "Nuevo titulo optimizado para SEO (max 60 chars)"},
                "short_description": {"type": "string", "description": "Nueva descripcion corta optimizada (130-160 chars, texto plano)"}
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
            max_tokens=2048,
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