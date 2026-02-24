import os
import requests
from flask import Flask, request

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# -------------------------
# تشخیص زبان (پایدار و بدون auto)
# -------------------------
def detect_language(text):
    # 1) تلاش با LibreTranslate
    try:
        r = requests.post("https://libretranslate.de/detect", data={"q": text})
        if r.text.strip() != "":
            lang = r.json()[0]["language"]
            if lang != "auto":
                return lang
    except:
        pass

    # 2) تشخیص دستی برای متن‌های کوتاه
    # فارسی
    if any("ا" <= ch <= "ی" for ch in text):
        return "fa"

    # عربی
    if any("ء" <= ch <= "ي" for ch in text):
        return "ar"

    # انگلیسی
    if any("a" <= ch.lower() <= "z" for ch in text):
        return "en"

    # ترکی
    if any(ch in "çğıöşü" for ch in text.lower()):
        return "tr"

    # 3) پیش‌فرض
    return "en"

# -------------------------
# ترجمه (با دو API برای پایداری)
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
            data = r.json()
            if "translatedText" in data:
                return data["translatedText"]
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
