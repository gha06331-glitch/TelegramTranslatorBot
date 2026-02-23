import os
import requests
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("توکن ربات پیدا نشد! BOT_TOKEN را در Render تنظیم کن.")

def start(update, context):
    update.message.reply_text("سلام! متن انگلیسی رو بفرست تا ترجمه کنم به فارسی.")

def translate_text(text):
    url = "https://api.mymemory.translated.net/get"
    params = {"q": text, "langpair": "en|fa"}
    response = requests.get(url, params=params).json()
    return response["responseData"]["translatedText"]

def translate(update, context):
    text = update.message.text
    translated = translate_text(text)
    update.message.reply_text(translated)

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, translate))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
