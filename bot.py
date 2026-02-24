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
    data = request.get_json()
    chat_id = data["message"]["chat"]["id"]
    text = data["message"]["text"]

    translated = translate(text)

    requests.get(f"{BASE_URL}/sendMessage", params={
        "chat_id": chat_id,
        "text": translated
    })

    return "ok"

@app.route("/")
def home():
    return "Bot is running"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
