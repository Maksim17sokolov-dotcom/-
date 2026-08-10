from flask import Flask, request
import json
import os
from datetime import datetime

app = Flask(__name__)
os.makedirs("logs", exist_ok=True)

@app.route('/grab', methods=['POST'])
def grab():
    data = request.json
    if not data:
        return "No data", 400
    filename = f"logs/{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"[+] Получены данные: {filename}")
    return "OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)