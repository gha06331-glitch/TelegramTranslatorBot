import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from googletrans import Translator

# گرفتن توکن از Environment Variable
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("توکن ربات پیدا نشد! حتما BOT_TOKEN در محیط تعریف شده باشد.")

translator = Translator()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! متن انگلیسی رو بفرست تا ترجمه کنم به فارسی.")

async def translate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    translated = translator.translate(text, dest='fa')
    await update.message.reply_text(translated.text)

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, translate))

print("Bot is running...")
app.run_polling()