from flask import Flask, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

# Папка для логов
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

@app.route('/')
def index():
    return "✅ Server is running! Send POST to /grab"

@app.route('/grab', methods=['POST'])
def grab():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data"}), 400

        # Сохраняем в файл
        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(LOG_DIR, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"[+] Получены данные: {filename}")
        print(f"[+] IP: {request.remote_addr}")
        print(f"[+] Data: {data}")

        return jsonify({"status": "OK", "file": filename}), 200

    except Exception as e:
        print(f"[-] Ошибка: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
