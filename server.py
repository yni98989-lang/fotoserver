import os
from flask import Flask, send_file
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext

app = Flask(__name__)
PHOTO_PATH = "last_photo.jpg"

def handle_photo(update: Update, context: CallbackContext):
    if update.message.photo:
        # Скачиваем фото в самом высоком качестве
        photo_file = update.message.photo[-1].get_file()
        photo_file.download(PHOTO_PATH)
        print("Фото успешно получено и сохранено!")

@app.route('/photo')
def get_photo():
    if os.path.exists(PHOTO_PATH):
        return send_file(PHOTO_PATH, mimetype='image/jpeg')
    return "No photo yet", 404

if __name__ == "__main__":
    TOKEN = os.getenv("BOT_TOKEN")
    
    # Запуск бота
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(MessageHandler(Filters.photo, handle_photo))
    updater.start_polling()

    # Запуск Flask
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
