from flask import Flask, request, jsonify
import anthropic, os, requests, re
from requests.auth import HTTPBasicAuth

app = Flask(__name__)
client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

WC_URL = os.environ.get("WOOCOMMERCE_URL", "")
WC_KEY = os.environ.get("WOOCOMMERCE_KEY", "")
WC_SECRET = os.environ.get("WOOCOMMERCE_SECRET", "")

def markdown_to_html(text):
    # Limpiar caracteres especiales al inicio
    text = text.strip().strip('"').strip("'")
    lines = text.split("\n")
    html_lines = []
    in_ul = False
    for line in lines:
        line = line.strip()
        if not line:
            if in_ul:
                html_lines.append("</ul>")
                in_ul = False
            continue
        # H2
        if line.startswith("## "):
            if in_ul: html_lines.append("</ul>"); in_ul = False
            line = re.sub(r'[#*🔧📝✅❌🚨💡📋🔍✏️]', '', line).strip()
            html_lines.append(f"<h3>{line}</h3>")
        # H3
        elif line.startswith("### "):
            if in_ul: html_lines.append("</ul>"); in_ul = False
            line = re.sub(r'[#*🔧📝✅❌🚨💡📋🔍✏️]', '', line).strip()
            html_lines.append(f"<h4>{line}</h4>")
        # Bullets
        elif line.startswith("- ") or line.startswith("* "):
            if not in_ul:
                html_lines.append("<ul>")
                in_ul = True
            content = line[2:].strip()
            content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', content)
            html_lines.append(f"<li>{content}</li>")
        # Linea separadora
        elif line == "---":
            if in_ul: html_lines.append("</ul>"); in_ul = False
        # Parrafo normal
        else:
            if in_ul: html_lines.append("</ul>"); in_ul = False
            line = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', line)
            line = re.sub(r'[#*🔧📝✅❌🚨💡📋🔍✏️]', '', line).strip()
            if line:
                html_lines.append(f"<p>{line}</p>")
    if in_ul:
        html_lines.append("</ul>")
    return "\n".join(html_lines)

def get_products(per_page=5):
    try:
        r = requests.get(
            f"{WC_URL}/wp-json/wc/v3/products",
            auth=HTTPBasicAuth(WC_KEY, WC_SECRET),
            params={"per_page": per_page, "status": "publish", "_fields": "id,name,short_description,description,slug"},
            timeout=15
        )
        products = r.json()
        return [{"id": p.get("id"), "name": p.get("name"), "short_description": p.get("short_description","")[:100], "description": p.get("description","")[:150]} for p in products]
    except Exception as e:
        return {"error": str(e)}

def update_product(product_id, data):
    try:
        if "description" in data:
            data["description"] = markdown_to_html(data["description"])
        r = requests.put(
            f"{WC_URL}/wp-json/wc/v3/products/{product_id}",
            auth=HTTPBasicAuth(WC_KEY, WC_SECRET),
            json=data,
            timeout=15
        )
        result = r.json()
        if "id" in result:
            return {"success": True, "id": product_id, "name": result.get("name")}
        else:
            return {"error": str(result)}
    except Exception as e:
        return {"error": str(e)}

SYSTEM = "Eres un agente SEO para peptidosysuplementos.mx. Usa get_products para ver productos reales antes de sugerir cambios. Pide confirmacion antes de usar update_product. Titulos SEO: max 60 chars, keyword al inicio. Responde en espanol."

TOOLS = [
    {
        "name": "get_products",
        "description": "Obtiene productos de WooCommerce con id, nombre, descripcion corta, descripcion larga y slug",
        "input_schema": {
            "type": "object",
            "properties": {
                "per_page": {"type": "integer", "default": 5}
            }
        }
    },
    {
        "name": "update_product",
        "description": "Actualiza titulo, descripcion corta o descripcion larga de un producto en WooCommerce",
        "input_schema": {
            "type": "object",
            "required": ["product_id"],
            "properties": {
                "product_id": {"type": "integer", "description": "ID del producto"},
                "name": {"type": "string", "description": "Nuevo titulo del producto"},
                "short_description": {"type": "string", "description": "Nueva descripcion corta"},
                "description": {"type": "string", "description": "Nueva descripcion larga del producto"}
            }
        }
    }
]

def run_tool(name, inputs):
    if name == "get_products":
        return get_products(inputs.get("per_page", 5))
    elif name == "update_product":
        data = {k: inputs[k] for k in ["name", "short_description", "description"] if k in inputs}
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