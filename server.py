import os
import asyncio
import io
import threading
from flask import Flask, send_file
from PIL import Image
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

app = Flask(__name__)
PHOTO_PATH = "last_photo.jpg"

# 1. Обработка фото из Telegram
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        file = await update.message.photo[-1].get_file()
        await file.download_to_drive(PHOTO_PATH)
        print("--- ФОТО ОБНОВЛЕНО ---")

# 2. Маршрут для ESP32 (с ресайзом и сжатием)
@app.route('/photo')
def get_photo():
    if os.path.exists(PHOTO_PATH):
        try:
            with Image.open(PHOTO_PATH) as img:
                img = img.convert("RGB")
                
                # ЖЕСТКИЙ РЕСАЙЗ: делаем ровно под экран 320x240
                # Это гарантирует, что ESP32 хватит памяти
                img = img.resize((320, 240), Image.Resampling.LANCZOS)
                
                img_io = io.BytesIO()
                # quality=40 и optimize=True делают файл очень легким (около 10-15 Кб)
                # progressive=False ОБЯЗАТЕЛЬНО для ESP32
                img.save(img_io, 'JPEG', quality=40, optimize=True, progressive=False)
                img_io.seek(0)
                
                size = img_io.getbuffer().nbytes
                print(f"Отправка сжатого фото: {size} байт")
                return send_file(img_io, mimetype='image/jpeg')
        except Exception as e:
            print(f"Ошибка: {e}")
            return "Error", 500
    return "No photo", 404

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, use_reloader=False)

if __name__ == "__main__":
    # Запуск Flask
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # Запуск Бота
    token = os.getenv("BOT_TOKEN")
    if not token:
        print("ОШИБКА: BOT_TOKEN не найден!")
    else:
        application = ApplicationBuilder().token(token).build()
        application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
        print("Сервер и Бот запущены...")
        application.run_polling(close_loop=False)
