import os
import asyncio
from flask import Flask, send_file
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from threading import Thread

app = Flask(__name__)
PHOTO_PATH = "last_photo.jpg"

# 1. Обработка фото (новый синтаксис v20+)
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        photo_file = await update.message.photo[-1].get_file()
        await photo_file.download_to_drive(PHOTO_PATH)
        print("Фото обновлено!")

# 2. Flask маршрут
@app.route('/photo')
def get_photo():
    if os.path.exists(PHOTO_PATH):
        return send_file(PHOTO_PATH, mimetype='image/jpeg')
    return "No photo yet", 404

# Функция для запуска Telegram бота
def run_bot():
    token = os.getenv("BOT_TOKEN")
    # Создаем приложение бота
    application = ApplicationBuilder().token(token).build()
    
    # Добавляем обработчик фото
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    print("Бот запущен...")
    application.run_polling()

if __name__ == "__main__":
    # Запускаем бота в отдельном потоке
    bot_thread = Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()

    # Запускаем Flask
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
