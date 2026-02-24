import os
import requests
from flask import Flask, request
import google.generativeai as genai

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_KEY")

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# پیکربندی API Key به روش جدید
genai.configure(api_key=GEMINI_KEY)

def ai_chat(user_text):
    try:
        # تغییر مهم: استفاده از "gemini-pro" به جای "gemini-1.5-flash"
        model = genai.GenerativeModel("gemini-pro") 
        response = model.generate_content(user_text)
        return response.text
    except Exception as e:
        print("AI Error:", e)
        return "❌ خطا در ارتباط با هوش مصنوعی"

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json(silent=True)
    print("Raw data:", data, flush=True)

    if not data:
        return "no data"

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text")

        if not text:
            return "ok"

        reply = ai_chat(text)

        requests.post(f"{BASE_URL}/sendMessage", json={
            "chat_id": chat_id,
            "text": reply
        })

    return "ok"

@app.route("/home")
def home():
    return "Bot is running"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
