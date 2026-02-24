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
    try:
        r = requests.post("https://libretranslate.de/detect", data={"q": text})
        if r.text.strip() == "":
            return "auto"
        return r.json()[0]["language"]
    except:
        return "auto"

# -------------------------
# ترجمه (با دو API)
# -------------------------
def translate(text, source_lang, target_lang):
    # API اول: LibreTranslate
    try:
        payload = {
            "q": text,
            "source": source_lang,
            "target": target_lang,
            "format": "text"
        }
        r = requests.post("https://libretranslate.de/translate", data=payload)
        if r.text.strip() != "":
            return r.json().get("translatedText", None)
    except:
        pass

    # API دوم: MyMemory (پشتیبان)
    try:
        url = "https://api.mymemory.translated.net/get"
        params = {"q": text, "langpair": f"{source_lang}|{target_lang}"}
        r = requests.get(url, params=params).json()
        return r["responseData"]["translatedText"]
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

        # تشخیص زبان
        detected = detect_language(text)
        print("Detected:", detected, flush=True)

        # دکمه‌های شیشه‌ای
        keyboard = {
            "inline_keyboard": [
                [
                    {"text": "🇮🇷 فارسی", "callback_data": f"fa|{detected}|{text}"},
                    {"text": "🇬🇧 انگلیسی", "callback_data": f"en|{detected}|{text}"}
                ],
                [
                    {"text": "🇹🇷 ترکی", "callback_data": f"tr|{detected}|{text}"},
                    {"text": "🇸🇦 عربی", "callback_data": f"ar|{detected}|{text}"}
                ]
            ]
        }

        requests.post(f"{BASE_URL}/sendMessage", json={
            "chat_id": chat_id,
            "text": "ترجمه به کدوم زبان؟",
            "reply_markup": keyboard
        })
        return "ok"

    # -------------------------
    # کلیک روی دکمه شیشه‌ای
    # -------------------------
    if "callback_query" in data:
        q = data["callback_query"]
        chat_id = q["message"]["chat"]["id"]
        target, source, text = q["data"].split("|", 2)

        translated = translate(text, source, target)

        requests.post(f"{BASE_URL}/sendMessage", json={
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
