def ai_chat(user_text):
    try:
        url = "https://api-inference.huggingface.co/models/google/gemma-2-2b-it"
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
