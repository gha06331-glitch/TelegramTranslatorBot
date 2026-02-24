import os
import requests
from flask import Flask, request

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# -------------------------
# تشخیص زبان
# -------------------------
def detect_language(text):
    url = "https://libretranslate.de/detect"
    try:
        response = requests.post(url, data={"q": text})
        if response.text.strip() == "":
            return "auto"
        data = response.json()
        return data[0]["language"]
    except:
        return "auto"

# -------------------------
# ترجمه
# -------------------------
def translate(text, source_lang, target_lang):
    url = "https://libretranslate.de/translate"
    payload = {
        "q": text,
        "source": source_lang,
        "target": target_lang,
        "format": "text"
    }
    try:
        response = requests.post(url, data=payload)
        if response.text.strip() == "":
            return "❌ سرویس ترجمه پاسخ نداد"
        data = response.json()
        return data.get("translatedText", "❌ ترجمه انجام نشد")
    except:
        return "❌ خطا در ترجمه"

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json(silent=True)
    print("Raw data:", data, flush=True)

    if not data:
        return "no data"

    # -------------------------
    # پیام معمولی
    # -------------------------
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text")

        if not text:
            return "ok"

        # اگر متن خیلی کوتاه بود
        if len(text.strip()) < 2:
            send_url = f"{BASE_URL}/sendMessage"
            requests.post(send_url, json={
                "chat_id": chat_id,
                "text": "❗ لطفاً متن طولانی‌تری بفرست"
            })
            return "ok"

        # تشخیص زبان
        detected_lang = detect_language(text)
        print("Detected:", detected_lang, flush=True)

        # دکمه‌های شیشه‌ای
        keyboard = {
            "inline_keyboard": [
                [
                    {"text": "🇮🇷 فارسی", "callback_data": f"fa|{detected_lang}|{text}"},
                    {"text": "🇬🇧 انگلیسی", "callback_data": f"en|{detected_lang}|{text}"}
                ],
                [
                    {"text": "🇹🇷 ترکی", "callback_data": f"tr|{detected_lang}|{text}"},
                    {"text": "🇸🇦 عربی", "callback_data": f"ar|{detected_lang}|{text}"}
                ]
            ]
        }

        send_url = f"{BASE_URL}/sendMessage"
        requests.post(send_url, json={
            "chat_id": chat_id,
            "text": "ترجمه به کدوم زبان؟",
            "reply_markup": keyboard
        })
        return "ok"

    # -------------------------
    # کلیک روی دکمه شیشه‌ای
    # -------------------------
    if "callback_query" in data:
        query = data["callback_query"]
        chat_id = query["message"]["chat"]["id"]
        callback_data = query["data"]

        target_lang, source_lang, text = callback_data.split("|", 2)

        translated = translate(text, source_lang, target_lang)

        send_url = f"{BASE_URL}/sendMessage"
        requests.post(send_url, json={
            "chat_id": chat_id,
            "text": translated
        })
        return "ok"

    return "ok"

@app.route("/home")
def home():
    return "Bot is running"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
