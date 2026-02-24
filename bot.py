import os
import requests
from flask import Flask, request

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def translate(text):
    url = "https://api.mymemory.translated.net/get"
    params = {"q": text, "langpair": "en|fa"}
    r = requests.get(url, params=params).json()
    return r["responseData"]["translatedText"]

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json(silent=True)
    print("Raw data:", data)

    if not data:
        return "no data"

    message = data.get("message")
    if not message:
        print("No message field")
        return "ok"

    text = message.get("text")
    chat_id = message["chat"]["id"]

    if not text:
        print("No text found")
        return "ok"

    translated = translate(text)
    print("Translated:", translated)

    send_url = f"{BASE_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": translated
    }

    r = requests.get(send_url, params=payload)
    print("Send response:", r.text)

    return "ok"

@app.route("/home")
def home():
    return "Bot is running"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
