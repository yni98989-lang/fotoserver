from flask import Flask, send_file
from telegram.ext import Updater, MessageHandler, Filters

app = Flask(__name__)
last_photo = None

def photo_handler(update, context):
    global last_photo
    file = update.message.photo[-1].get_file()
    file.download("last.jpg")
    last_photo = "last.jpg"

@app.route("/photo")
def get_photo():
    if last_photo:
        return send_file(last_photo, mimetype="image/jpeg")
    return "No photo yet", 404

if __name__ == "__main__":
    updater = Updater("YOUR_BOT_TOKEN")
    updater.dispatcher.add_handler(MessageHandler(Filters.photo, photo_handler))
    updater.start_polling()
    app.run(host="0.0.0.0", port=5000)
