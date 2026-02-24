import os
import requests
from flask import Flask, request

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
HF_KEY = os.getenv("HF_KEY")

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def ai_chat(user_text):
    try:
        url = "https://api-inference.huggingface.co/models/meta-llama/Llama-3-8B-Instruct"
        headers = {
            "Authorization": f"Bearer {HF_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "inputs": user_text
        }

        r = requests.post(url, headers=headers, json=data)
        r.raise_for_status()

        return r.json()[0]["generated_text"]

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
