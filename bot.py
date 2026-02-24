import os
import requests
from flask import Flask, request

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def translate(text, target_lang):
    url = "https://api.mymemory.translated.net/get"
    params = {"q": text, "langpair": f"auto|{target_lang}"}
    r = requests.get(url, params=params).json()
    return r["responseData"]["translatedText"]

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json(silent=True)
    print("Raw data:", data, flush=True)

    if not data:
        return "no data"

    # -------------------------
    # 1) اگر پیام معمولی بود
    # -------------------------
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text")

        if not text:
            return "ok"

        # دکمه‌های شیشه‌ای
        keyboard = {
            "inline_keyboard": [
                [
                    {"text": "🇮🇷 ترجمه به فارسی", "callback_data": f"fa|{text}"},
                    {"text": "🇬🇧 ترجمه به انگلیسی", "callback_data": f"en|{text}"}
                ],
                [
                    {"text": "🇹🇷 ترکی", "callback_data": f"tr|{text}"},
                    {"text": "🇸🇦 عربی", "callback_data": f"ar|{text}"}
                ]
            ]
        }

        send_url = f"{BASE_URL}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": "ترجمه به کدوم زبان؟",
            "reply_markup": keyboard
        }

        requests.post(send_url, json=payload)
        return "ok"

    # -------------------------
    # 2) اگر دکمه شیشه‌ای کلیک شد
    # -------------------------
    if "callback_query" in data:
        query = data["callback_query"]
        chat_id = query["message"]["chat"]["id"]
        callback_data = query["data"]

        lang, text = callback_data.split("|", 1)

        translated = translate(text, lang)

        send_url = f"{BASE_URL}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": translated
        }

        requests.post(send_url, json=payload)
        return "ok"

    return "ok"

@app.route("/home")
def home():
    return "Bot is running"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
