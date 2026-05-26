from flask import Flask, request, jsonify, render_template_string
import anthropic, os

app = Flask(__name__)
client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

HTML = """
<!DOCTYPE html>
<html>
<head><title>Agente SEO - Peptidos y Suplementos</title>
<style>
  body { font-family: sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; }
  #chat { border: 1px solid #ddd; height: 400px; overflow-y: auto; padding: 16px; border-radius: 8px; margin-bottom: 12px; }
  .user { color: #1a56db; margin: 8px 0; }
  .agent { color: #057a55; margin: 8px 0; }
  input { width: 80%; padding: 10px; border: 1px solid #ddd; border-radius: 6px; }
  button { padding: 10px 20px; background: #1a56db; color: white; border: none; border-radius: 6px; cursor: pointer; }
</style>
</head>
<body>
<h2>🤖 Agente SEO</h2>
<div id="chat"></div>
<input id="msg" placeholder="Escribe una instrucción SEO..." onkeydown="if(event.key==='Enter') send()">
<button onclick="send()">Enviar</button>
<script>
  let history = [];
  async function send() {
    const msg = document.getElementById('msg').value;
    if (!msg) return;
    document.getElementById('msg').value = '';
    history.push({role:'user', content: msg});
    document.getElementById('chat').innerHTML += '<p class="user"><b>Tú:</b> ' + msg + '</p>';
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

SYSTEM = """Eres un agente SEO especializado en la tienda peptidosysuplementos.mx.
Tu función es optimizar productos, títulos, meta descripciones y contenido para mejorar el posicionamiento en Google.
Responde siempre en español. Sé conciso y profesional."""

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    messages = data.get('messages', [])
    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1000,
        system=SYSTEM,
        messages=messages
    )
    return jsonify({'reply': response.content[0].text})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))