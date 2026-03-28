import os
import requests
from flask import Flask, request
from telegram import Bot, Update

TOKEN = os.getenv("TOKEN")

bot = Bot(token=TOKEN)
app = Flask(__name__)

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, bot)

    try:
        if update.message:
            chat_id = update.message.chat_id
            text = update.message.text

            bot.send_message(chat_id, "⏳ جاري البحث...")

            # API تحميل
            url = f"https://api.vreden.my.id/api/spotify-download?query={text}"
            res = requests.get(url).json()

            if "result" not in res:
                bot.send_message(chat_id, "❌ لم يتم العثور على الأغنية")
                return "ok"

            download_url = res["result"]["download"]

            audio = requests.get(download_url)

            with open("song.mp3", "wb") as f:
                f.write(audio.content)

            bot.send_audio(chat_id, audio=open("song.mp3", "rb"))

            os.remove("song.mp3")

    except Exception as e:
        print(e)

    return "ok"

@app.route("/")
def home():
    return "Bot is running"

if __name__ == "__main__":
    bot.set_webhook(f"https://free-music-bot.onrender.com/{TOKEN}")
    app.run(host="0.0.0.0", port=10000)