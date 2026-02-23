import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("توکن ربات پیدا نشد! BOT_TOKEN را در تنظیمات Render اضافه کن.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! متن انگلیسی رو بفرست تا ترجمه کنم به فارسی.")

def translate_text(text):
    url = "https://api.mymemory.translated.net/get"
    params = {"q": text, "langpair": "en|fa"}
    response = requests.get(url, params=params).json()
    return response["responseData"]["translatedText"]

async def translate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    translated = translate_text(text)
    await update.message.reply_text(translated)

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, translate))

print("Bot is running...")
app.run_polling()
