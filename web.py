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
            params={"per_page": per_page, "status": "publish", "_fields": "id,name,short_description,slug"},
            timeout=15
        )
        products = r.json()
        slim = []
        for p in products:
            slim.append({
                "id": p.get("id"),
                "name": p.get("name"),
                "short_description": p.get("short_description", "")[:150],
                "slug": p.get("slug")
            })
        return slim
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
        return {"success": True, "id": product_id}
    except Exception as e:
        return {"error": str(e)}

HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Agente SEO - Peptidos y Suplementos</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; background: #f0f2f5; min-height: 100vh; padding: 24px; }
  .container { max-width: 860px; margin: 0 auto; }
  h2 { color: #1a1a2e; margin-bottom: 16px; font-size: 22px; }
  .toolbar { display: flex; gap: 8px; margin-bottom: 12px; flex-wrap: wrap; }
  .btn-tool { padding: 8px 16px; background: white; color: #1a56db; border: 1px solid #c5d5f5; border-radius: 8px; cursor: pointer; font-size: 13px; transition: all 0.2s; }
  .btn-tool:hover { background: #e8f0fe; }
  #chat { background: white; border: 1px solid #e0e0e0; min-height: 420px; max-height: 520px; overflow-y: auto; padding: 20px; border-radius: 12px; margin-bottom: 12px; }
  .user { color: #1a56db; margin: 12px 0 4px 0; font-size: 14px; }
  .agent { color: #057a55; margin: 4px 0 12px 0; font-size: 14px; white-space: pre-wrap; line-height: 1.6; }
  .loading { color: #888; font-style: italic; }
  .error-msg { color: #dc2626; }
  .row { display: flex; gap: 8px; }
  #msg { flex: 1; padding: 12px 16px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px; outline: none; }
  #msg:focus { border-color: #1a56db; }
  #send-btn { padding: 12px 24px; background: #1a56db; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 500; }
  #send-btn:hover { background: #1040b0; }
  #send-btn:disabled { background: #93c5fd; cursor: not-allowed; }
</style>
</head>
<body>
<div class="container">
  <h2>🤖 Agente SEO — peptidosysuplementos.mx</h2>
  <div class="toolbar">
    <button class="btn-tool" onclick="quickSend('Muéstrame los 10 productos más recientes con sus títulos actuales')">📋 Ver productos</button>
    <button class="btn-tool" onclick="quickSend('Analiza los títulos de mis productos y dime cuáles necesitan optimización SEO urgente')">🔍 Analizar SEO</button>
    <button class="btn-tool" onclick="quickSend('Propón títulos optimizados para SEO para los primeros 5 productos')">✏️ Optimizar títulos</button>
  </div>
  <div id="chat"></div>
  <div class="row">
    <input id="msg" placeholder="Escribe una instrucción SEO..." onkeydown="if(event.key==='Enter' && !event.shiftKey) send()">
    <button id="send-btn" onclick="send()">Enviar</button>
  </div>
</div>
<script>
  let history = [];
  let waiting = false;

  function quickSend(text) {
    if (waiting) return;
    document.getElementById('msg').value = text;
    send();
  }

  async function send() {
    if (waiting) return;
    const msg = document.getElementById('msg').value.trim();
    if (!msg) return;

    waiting = true;
    document.getElementById('send-btn').disabled = true;
    document.getElementById('msg').value = '';

    const chat = document.getElementById('chat');
    history.push({role: 'user', content: msg});

    const userEl = document.createElement('p');
    userEl.className = 'user';
    userEl.innerHTML = '<b>Tú:</b> ' + escapeHtml(msg);
    chat.appendChild(userEl);

    const loadingEl = document.createElement('p');
    loadingEl.className = 'agent loading';
    loadingEl.id = 'loading-msg';
    loadingEl.textContent = '⏳ Consultando...';
    chat.appendChild(loadingEl);
    chat.scrollTop = chat.scrollHeight;

    try {
      const res = await fetch('/chat', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({messages: history})
      });

      const data = await res.json();
      document.getElementById('loading-msg').remove();

      if (data.reply) {
        history.push({role: 'assistant', content: data.reply});
        const agentEl = document.createElement('p');
        agentEl.className = 'agent';
        agentEl.innerHTML = '<b>Agente:</b> ' + escapeHtml(data.reply);
        chat.appendChild(agentEl);
      } else {
        throw new Error('Respuesta vacía');
      }
    } catch(e) {
      const existing = document.getElementById('loading-msg');
      if (existing) existing.remove();
      const errEl = document.createElement('p');
      errEl.className = 'agent error-msg';
      errEl.textContent = 'Error: ' + e.message;
      chat.appendChild(errEl);
    }

    waiting = false;
    document.getElementById('send-btn').disabled = false;
    chat.scrollTop = chat.scrollHeight;
  }

 function escapeHtml(text) {
    const div = document.createElement('div');
    div.appendChild(document.createTextNode(text));
    return div.innerHTML.split('\n').join('<br>');
  }
</script>
</body>
</html>
"""

SYSTEM = """Eres un agente SEO especializado en la tienda peptidosysuplementos.mx (WooCommerce).

Tienes acceso a dos herramientas:
1. get_products: obtiene productos de la tienda
2. update_product: actualiza título o descripción de un producto

Reglas para títulos SEO:
- Palabra clave principal al inicio
- Máximo 60 caracteres
- Sin caracteres especiales innecesarios
- Mencionar beneficio principal

Reglas para meta descripciones:
- Entre 140-160 caracteres
- Incluir llamada a la acción
- Mencionar beneficio y palabra clave

Siempre pide confirmación antes de aplicar cambios con update_product.
Responde en español. Sé conciso y profesional."""

TOOLS = [
    {
        "name": "get_products",
        "description": "Obtiene productos de la tienda WooCommerce con id, nombre, descripción corta y slug",
        "input_schema": {
            "type": "object",
            "properties": {
                "per_page": {
                    "type": "integer",
                    "description": "Número de productos (máximo 10)",
                    "default": 5
                }
            }
        }
    },
    {
        "name": "update_product",
        "description": "Actualiza título o descripción de un producto en WooCommerce",
        "input_schema": {
            "type": "object",
            "properties": {
                "product_id": {"type": "integer", "description": "ID del producto"},
                "name": {"type": "string", "description": "Nuevo título"},
                "short_description": {"type": "string", "description": "Nueva descripción corta"}
            },
            "required": ["product_id"]
        }
    }
]

def run_tool(name, inputs):
    if name == "get_products":
        return get_products(inputs.get("per_page", 5))
    elif name == "update_product":
        data = {}
        if "name" in inputs:
            data["name"] = inputs["name"]
        if "short_description" in inputs:
            data["short_description"] = inputs["short_description"]
        return update_product(inputs["product_id"], data)
    return {"error": "herramienta desconocida"}

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        messages = data.get('messages', [])

        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=2048,
            system=SYSTEM,
            tools=TOOLS,
            messages=messages
        )

        while response.stop_reason == "tool_use":
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
            for b in response.content:
                if b.type == "tool_use":
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
                max_tokens=2048,
                system=SYSTEM,
                tools=TOOLS,
                messages=messages
            )

        reply = ""
        for block in response.content:
            if hasattr(block, "text"):
                reply += block.text

        return jsonify({'reply': reply})

    except Exception as e:
        return jsonify({'reply': f'Error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))