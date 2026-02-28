import os
import asyncio
from flask import Flask, send_file
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import threading

app = Flask(__name__)
PHOTO_PATH = "last_photo.jpg"

# 1. Обработка фото
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        file = await update.message.photo[-1].get_file()
        await file.download_to_drive(PHOTO_PATH)
        print("--- ФОТО ОБНОВЛЕНО ---")

# 2. Маршрут для ESP32
@app.route('/photo')
def get_photo():
    if os.path.exists(PHOTO_PATH):
        return send_file(PHOTO_PATH, mimetype='image/jpeg')
    return "No photo yet", 404

# Функция для запуска Flask в фоне
def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, use_reloader=False)

if __name__ == "__main__":
    # Запускаем Flask в отдельном потоке
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # Запускаем Telegram бота в ГЛАВНОМ потоке
    token = os.getenv("BOT_TOKEN")
    application = ApplicationBuilder().token(token).build()
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    print("Сервер Flask запущен в фоне...")
    print("Бот запущен в основном потоке и ждет фото...")
    
    # close_loop=False помогает избежать конфликтов при остановке
    application.run_polling(close_loop=False)
