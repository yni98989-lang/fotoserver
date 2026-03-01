import os
import asyncio
import io
from flask import Flask, send_file
from PIL import Image  # <-- Добавили импорт
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import threading

app = Flask(__name__)
PHOTO_PATH = "last_photo.jpg"

# 1. Обработка фото (оставляем как есть, бот просто сохраняет оригинал)
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        # Берем самое качественное фото из массива
        file = await update.message.photo[-1].get_file()
        await file.download_to_drive(PHOTO_PATH)
        print("--- ФОТО ОБНОВЛЕНО И СОХРАНЕНО ---")

# 2. ИСПРАВЛЕННЫЙ Маршрут для ESP32
@app.route('/photo')
def get_photo():
    if os.path.exists(PHOTO_PATH):
        try:
            # Открываем сохраненный оригинал
            with Image.open(PHOTO_PATH) as img:
                img = img.convert("RGB") # На случай если прислали что-то кроме JPG
                
                # Уменьшаем до размеров экрана ESP32 (320x240)
                # Если у тебя экран 480x320, поменяй цифры ниже
                img.thumbnail((320, 240), Image.Resampling.LANCZOS)
                
                # Сохраняем в память (буфер) как простой Baseline JPEG
                img_io = io.BytesIO()
                img.save(img_io, 'JPEG', quality=50, progressive=False)
                img_io.seek(0)
                
                print(f"Отправка сжатого фото: {img.size[0]}x{img.size[1]}")
                return send_file(img_io, mimetype='image/jpeg')
        except Exception as e:
            print(f"Ошибка при обработке фото: {e}")
            return "Error processing image", 500
            
    return "No photo yet", 404

# Функция для запуска Flask в фоне
def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, use_reloader=False)

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    token = os.getenv("BOT_TOKEN")
    if not token:
        print("ОШИБКА: BOT_TOKEN не найден в переменных окружения!")
    else:
        application = ApplicationBuilder().token(token).build()
        application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
        
        print("Сервер Flask запущен на порту 8080...")
        print("Бот запущен и ждет фото...")
        
        application.run_polling(close_loop=False)
