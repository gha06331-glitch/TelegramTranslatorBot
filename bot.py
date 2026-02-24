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

        result = r.json()

        # حالت ۱: مدل هنوز لود نشده
        if isinstance(result, dict) and "error" in result:
            return "⏳ مدل در حال بارگذاری است، چند ثانیه بعد دوباره پیام بده."

        # حالت ۲: خروجی به صورت لیست
        if isinstance(result, list) and "generated_text" in result[0]:
            return result[0]["generated_text"]

        # حالت ۳: خروجی به صورت دیکشنری
        if isinstance(result, dict) and "generated_text" in result:
            return result["generated_text"]

        return "❌ پاسخ نامعتبر از مدل دریافت شد."

    except Exception as e:
        print("AI Error:", e)
        return "❌ خطا در ارتباط با هوش مصنوعی"
