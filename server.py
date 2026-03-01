import os
import asyncio
import io
import threading
from flask import Flask, send_file, make_response
from PIL import Image
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

app = Flask(__name__)
PHOTO_PATH = "last_photo.jpg"

@app.route('/photo')
def get_photo():
    if os.path.exists(PHOTO_PATH):
        try:
            with Image.open(PHOTO_PATH) as img:
                img = img.convert("RGB")
                # Изменяем размер
                img = img.resize((320, 240), Image.Resampling.LANCZOS)
                
                img_io = io.BytesIO()
                # Сжатие
                img.save(img_io, 'JPEG', quality=40, optimize=True, progressive=False)
                img_io.seek(0)
                
                size = img_io.getbuffer().nbytes
                print(f"--- ОТПРАВКА: {size} байт ---")
                
                # Создаем ответ с отключенным кешированием
                response = make_response(send_file(img_io, mimetype='image/jpeg'))
                response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
                return response
        except Exception as e:
            print(f"Ошибка: {e}")
            return "Error", 500
    return "No photo", 404

# Остальная часть кода (handle_photo, run_flask, main) без изменений...
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        file = await update.message.photo[-1].get_file()
        await file.download_to_drive(PHOTO_PATH)
        print("--- ФОТО ОБНОВЛЕНО ---")

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, use_reloader=False)

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    token = os.getenv("BOT_TOKEN")
    if not token:
        print("ОШИБКА: BOT_TOKEN не найден!")
    else:
        application = ApplicationBuilder().token(token).build()
        application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
        print("Сервер запущен...")
        application.run_polling()
