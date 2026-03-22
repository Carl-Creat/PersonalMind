# PersonalMind Web UI (Flask version)
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.llm import PROVIDERS, get_llm
from agent.memory import get_memory

try:
    from flask import Flask, request, jsonify, Response
    HAS_FLASK = True
except ImportError:
    HAS_FLASK = False


def generate_html():
    provider_options = ""
    for key, p in PROVIDERS.items():
        provider_options += '<option value="%s">%s</option>\n' % (key, p["name"])
    
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>PersonalMind</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Segoe UI', Arial, sans-serif; background: #f0f2f5; color: #333; }
.header { background: linear-gradient(135deg, #667eea 0%%, #764ba2 100%%); color: white; padding: 20px 30px; }
.header h1 { font-size: 24px; font-weight: 600; }
.header p { font-size: 14px; opacity: 0.8; margin-top: 4px; }
.container { max-width: 1200px; margin: 20px auto; display: flex; gap: 20px; padding: 0 20px; }
.chat-panel { flex: 1; background: white; border-radius: 12px; box-shadow: 0 2px 12px rgba(0,0,0,0.08); display: flex; flex-direction: column; height: calc(100vh - 120px); }
.side-panel { width: 280px; background: white; border-radius: 12px; box-shadow: 0 2px 12px rgba(0,0,0,0.08); padding: 20px; height: fit-content; position: sticky; top: 20px; }
.chat-messages { flex: 1; overflow-y: auto; padding: 20px; }
.msg { margin-bottom: 16px; display: flex; }
.msg.user { justify-content: flex-end; }
.msg.user .bubble { background: #667eea; color: white; border-radius: 16px 16px 4px 16px; }
.msg.ai .bubble { background: #f0f2f5; color: #333; border-radius: 16px 16px 16px 4px; }
.bubble { max-width: 70%%; padding: 12px 16px; font-size: 14px; line-height: 1.6; white-space: pre-wrap; }
.input-area { padding: 16px; border-top: 1px solid #eee; display: flex; gap: 10px; }
.input-area input { flex: 1; padding: 12px 16px; border: 2px solid #eee; border-radius: 24px; font-size: 14px; outline: none; transition: border-color 0.2s; }
.input-area input:focus { border-color: #667eea; }
.btn { padding: 10px 24px; border: none; border-radius: 20px; cursor: pointer; font-size: 14px; font-weight: 600; transition: all 0.2s; }
.btn-primary { background: #667eea; color: white; }
.btn-primary:hover { background: #5a6fd6; }
.btn-secondary { background: #f0f2f5; color: #333; margin-left: 8px; }
.btn-secondary:hover { background: #e0e2e5; }
.side-panel h3 { font-size: 16px; margin-bottom: 12px; color: #333; }
.side-panel label { display: block; font-size: 12px; color: #888; margin-bottom: 4px; margin-top: 12px; }
.side-panel select, .side-panel input { width: 100%%; padding: 8px 12px; border: 1px solid #ddd; border-radius: 8px; font-size: 13px; outline: none; }
.side-panel select:focus, .side-panel input:focus { border-color: #667eea; }
.status { margin-top: 12px; padding: 10px; background: #f8f9fa; border-radius: 8px; font-size: 12px; color: #666; }
.cmds { margin-top: 16px; padding-top: 16px; border-top: 1px solid #eee; }
.cmds p { font-size: 12px; color: #888; line-height: 1.8; }
.typing { display: none; padding: 12px 20px; color: #888; font-size: 13px; }
.typing.show { display: block; }
</style>
</head>
<body>
<div class="header">
    <h1>PersonalMind</h1>
    <p>Your Personal AI Brain - 11 Providers Supported</p>
</div>
<div class="container">
    <div class="chat-panel">
        <div class="chat-messages" id="messages">
            <div class="msg ai"><div class="bubble">Hello! I'm PersonalMind. Select your AI provider on the right, enter your API key, and start chatting!</div></div>
        </div>
        <div class="typing" id="typing">AI is thinking...</div>
        <div class="input-area">
            <input type="text" id="msgInput" placeholder="Type your message..." onkeydown="if(event.key==='Enter')send()">
            <button class="btn btn-primary" onclick="send()">Send</button>
            <button class="btn btn-secondary" onclick="clearChat()">Clear</button>
        </div>
    </div>
    <div class="side-panel">
        <h3>Settings</h3>
        <label>AI Provider</label>
        <select id="provider" onchange="onProviderChange()">
            %s
        </select>
        <label>Model</label>
        <select id="model"></select>
        <label>API Key</label>
        <input type="password" id="apiKey" placeholder="Enter API key...">
        <div class="status" id="status">Set API key to start</div>
        <div class="cmds">
            <h3 style="font-size:14px;">Commands</h3>
            <p>/help - Show help<br>/search &lt;kw&gt; - Web search<br>/remember &lt;text&gt; - Remember<br>/forget &lt;kw&gt; - Forget<br>/memory - View memories<br>/stats - Statistics</p>
        </div>
    </div>
</div>
<script>
const MODELS = %s;
let providerEl = document.getElementById('provider');
let modelEl = document.getElementById('model');

function onProviderChange() {
    let p = providerEl.value;
    modelEl.innerHTML = '';
    if (MODELS[p]) {
        MODELS[p].forEach(m => {
            let opt = document.createElement('option');
            opt.value = m; opt.textContent = m;
            modelEl.appendChild(opt);
        });
    }
    updateStatus();
}

function updateStatus() {
    let key = document.getElementById('apiKey').value;
    let p = providerEl.value;
    let m = modelEl.value;
    document.getElementById('status').textContent = 
        (key ? 'Ready' : 'API Key NOT SET') + ' | ' + p + ' | ' + m;
}

document.getElementById('apiKey').addEventListener('input', updateStatus);
onProviderChange();

function send() {
    let input = document.getElementById('msgInput');
    let msg = input.value.trim();
    if (!msg) return;
    input.value = '';
    
    let key = document.getElementById('apiKey').value;
    let p = providerEl.value;
    let m = modelEl.value;
    
    let box = document.getElementById('messages');
    box.innerHTML += '<div class="msg user"><div class="bubble">' + escHtml(msg) + '</div></div>';
    box.scrollTop = box.scrollHeight;
    
    document.getElementById('typing').classList.add('show');
    
    fetch('/api/chat', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({message: msg, provider: p, model: m, api_key: key})
    })
    .then(r => r.json())
    .then(data => {
        document.getElementById('typing').classList.remove('show');
        box.innerHTML += '<div class="msg ai"><div class="bubble">' + escHtml(data.reply) + '</div></div>';
        box.scrollTop = box.scrollHeight;
    })
    .catch(e => {
        document.getElementById('typing').classList.remove('show');
        box.innerHTML += '<div class="msg ai"><div class="bubble" style="color:red;">Error: ' + escHtml(e.message) + '</div></div>';
        box.scrollTop = box.scrollHeight;
    });
}

function clearChat() {
    fetch('/api/clear', {method:'POST'});
    document.getElementById('messages').innerHTML = '<div class="msg ai"><div class="bubble">Chat cleared. How can I help you?</div></div>';
}

function escHtml(t) {
    let d = document.createElement('div');
    d.textContent = t;
    return d.innerHTML;
}
</script>
</body>
</html>""" % (
    provider_options,
    json.dumps({k: v.get("models", []) for k, v in PROVIDERS.items()})
)


def create_app():
    if not HAS_FLASK:
        return None
    
    app = Flask(__name__)
    llm = get_llm()
    memory = get_memory()
    
    @app.route("/")
    def index():
        return Response(generate_html(), mimetype="text/html")
    
    @app.route("/api/chat", methods=["POST"])
    def chat():
        data = request.json
        message = data.get("message", "")
        provider = data.get("provider")
        model = data.get("model")
        api_key = data.get("api_key")
        
        # Update settings
        if provider:
            llm.switch_provider(provider, api_key=api_key, model=model)
        
        if not llm.api_key:
            return jsonify({"reply": "Please set your API key in the side panel."})
        
        # Handle commands
        if message.startswith("/"):
            from agent.core import get_agent
            agent = get_agent()
            reply = agent._handle_command(message)
            return jsonify({"reply": reply})
        
        # Auto-remember
        from agent.core import get_agent
        agent = get_agent()
        agent._auto_remember(message)
        
        # Get context and chat
        context = memory.get_context_for_llm(message)
        reply = llm.chat(message, context)
        
        return jsonify({"reply": reply})
    
    @app.route("/api/clear", methods=["POST"])
    def clear():
        llm.clear_history()
        return jsonify({"ok": True})
    
    @app.route("/api/memory", methods=["GET"])
    def get_memories():
        stats = memory.get_memory_stats()
        all_mem = memory.get_all_memories()
        return jsonify({"stats": stats, "memories": all_mem})
    
    @app.route("/api/providers", methods=["GET"])
    def get_providers():
        return jsonify({k: {"name": v["name"], "models": v["models"], "website": v.get("website", "")} for k, v in PROVIDERS.items()})
    
    return app


def launch_ui(share=False, port=7860):
    app = create_app()
    if app is None:
        print("Error: Flask not installed.")
        print("Install with: py -3 -m pip install --user flask")
        print("Or try CLI mode: python main.py --cli")
        return
    print("Starting PersonalMind Web UI...")
    print("Open: http://localhost:%d" % port)
    print("Press Ctrl+C to stop")
    app.run(host="0.0.0.0", port=port, debug=False)
