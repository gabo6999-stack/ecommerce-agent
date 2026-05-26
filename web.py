from flask import Flask, request, jsonify, render_template_string
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
            params={"per_page": per_page, "status": "publish"}
        )
        return r.json()
    except Exception as e:
        return []

def update_product(product_id, data):
    try:
        r = requests.put(
            f"{WC_URL}/wp-json/wc/v3/products/{product_id}",
            auth=HTTPBasicAuth(WC_KEY, WC_SECRET),
            json=data
        )
        return r.json()
    except Exception as e:
        return {"error": str(e)}

HTML = """
<!DOCTYPE html>
<html>
<head><title>Agente SEO - Peptidos y Suplementos</title>
<style>
  body { font-family: sans-serif; max-width: 860px; margin: 40px auto; padding: 20px; background: #f9f9f9; }
  h2 { color: #1a1a2e; }
  #chat { background: white; border: 1px solid #ddd; height: 450px; overflow-y: auto; padding: 16px; border-radius: 10px; margin-bottom: 12px; }
  .user { color: #1a56db; margin: 10px 0; }
  .agent { color: #057a55; margin: 10px 0; white-space: pre-wrap; }
  .row { display: flex; gap: 8px; }
  input { flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px; }
  button { padding: 10px 20px; background: #1a56db; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 14px; }
  button:hover { background: #1040b0; }
  .toolbar { display: flex; gap: 8px; margin-bottom: 10px; flex-wrap: wrap; }
  .btn-tool { padding: 7px 14px; background: #e8f0fe; color: #1a56db; border: 1px solid #c5d5f5; border-radius: 6px; cursor: pointer; font-size: 13px; }
  .btn-tool:hover { background: #d0e2ff; }
</style>
</head>
<body>
<h2>🤖 Agente SEO — peptidosysuplementos.mx</h2>
<div class="toolbar">
  <button class="btn-tool" onclick="quickSend('Muéstrame los 10 productos más recientes de la tienda con sus títulos actuales')">📋 Ver productos</button>
  <button class="btn-tool" onclick="quickSend('Analiza los títulos y descripciones de mis productos y dime cuáles necesitan optimización SEO urgente')">🔍 Analizar SEO</button>
  <button class="btn-tool" onclick="quickSend('Propón títulos optimizados para SEO para los primeros 5 productos')">✏️ Optimizar títulos</button>
</div>
<div id="chat"></div>
<div class="row">
  <input id="msg" placeholder="Escribe una instrucción SEO..." onkeydown="if(event.key==='Enter') send()">
  <button onclick="send()">Enviar</button>
</div>
<script>
  let history = [];
  function quickSend(text) {
    document.getElementById('msg').value = text;
    send();
  }
  async function send() {
    const msg = document.getElementById('msg').value.trim();
    if (!msg) return;
    document.getElementById('msg').value = '';
    history.push({role:'user', content: msg});
    document.getElementById('chat').innerHTML += '<p class="user"><b>Tú:</b> ' + msg + '</p>';
    document.getElementById('chat').scrollTop = 9999;
    const res = await fetch('/chat', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({messages: history})});
    const data = await res.json();
    history.push({role:'assistant', content: data.reply});
    document.getElementById('chat').innerHTML += '<p class="agent"><b>Agente:</b> ' + data.reply + '</p>';
    document.getElementById('chat').scrollTop = 9999;
  }
</script>
</body>
</html>
"""

SYSTEM = """Eres un agente SEO especializado en la tienda peptidosysuplementos.mx (WooCommerce).

Tienes acceso a dos herramientas:
1. get_products: obtiene los productos de la tienda
2. update_product: actualiza título o descripción de un producto

Cuando el usuario pida ver productos, analizar SEO u optimizar, usa get_products primero para obtener datos reales.

Para optimizar títulos SEO:
- Incluir palabra clave principal al inicio
- Máximo 60 caracteres
- Sin caracteres especiales innecesarios
- Mencionar el beneficio principal

Para meta descripciones:
- Entre 140-160 caracteres
- Incluir llamada a la acción
- Mencionar beneficio y palabra clave

Cuando propongas cambios, pregunta confirmación antes de aplicarlos.
Responde siempre en español. Sé concreto y profesional."""

TOOLS = [
    {
        "name": "get_products",
        "description": "Obtiene productos de la tienda WooCommerce",
        "input_schema": {
            "type": "object",
            "properties": {
                "per_page": {
                    "type": "integer",
                    "description": "Número de productos a obtener (máximo 50)",
                    "default": 10
                }
            }
        }
    },
    {
        "name": "update_product",
        "description": "Actualiza el título o descripción de un producto en WooCommerce",
        "input_schema": {
            "type": "object",
            "properties": {
                "product_id": {"type": "integer", "description": "ID del producto"},
                "name": {"type": "string", "description": "Nuevo título del producto"},
                "description": {"type": "string", "description": "Nueva descripción"},
                "short_description": {"type": "string", "description": "Nueva descripción corta"}
            },
            "required": ["product_id"]
        }
    }
]

def run_tool(name, inputs):
    if name == "get_products":
        return get_products(inputs.get("per_page", 10))
    elif name == "update_product":
        data = {}
        if "name" in inputs:
            data["name"] = inputs["name"]
        if "description" in inputs:
            data["description"] = inputs["description"]
        if "short_description" in inputs:
            data["short_description"] = inputs["short_description"]
        return update_product(inputs["product_id"], data)
    return {"error": "herramienta desconocida"}

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    messages = data.get('messages', [])

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=4096,
        system=SYSTEM,
        tools=TOOLS,
        messages=messages
    )

    while response.stop_reason == "tool_use":
        tool_uses = [b for b in response.content if b.type == "tool_use"]
        text_blocks = [b for b in response.content if hasattr(b, "text")]

        assistant_content = []
        for b in response.content:
            if b.type == "tool_use":
                assistant_content.append({
                    "type": "tool_use",
                    "id": b.id,
                    "name": b.name,
                    "input": b.input
                })
            elif hasattr(b, "text"):
                assistant_content.append({
                    "type": "text",
                    "text": b.text
                })

        tool_results = []
        for b in tool_uses:
            result = run_tool(b.name, b.input)
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": b.id,
                "content": str(result)
            })

        messages = messages + [
            {"role": "assistant", "content": assistant_content},
            {"role": "user", "content": tool_results}
        ]

        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=4096,
            system=SYSTEM,
            tools=TOOLS,
            messages=messages
        )

    reply = ""
    for block in response.content:
        if hasattr(block, "text"):
            reply += block.text

    return jsonify({'reply': reply})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))