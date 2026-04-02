import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes

BOT_TOKEN = "8761374023:AAENmLmjXyqh0P2gir-59g3lWtJmNthVKXc"
API = "https://teraboxyx.netlify.app/.netlify/functions/terabox?url="

# START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔗 Send Terabox Link")

# HANDLE LINK
async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text

    res = requests.get(API + url).json()

    if not res["success"]:
        await update.message.reply_text("❌ Failed to fetch")
        return

    data = res["data"][0]

    # SAVE DATA
    context.user_data["streams"] = data["fastStreamUrls"]
    context.user_data["downloads"] = {
        "normal": data["downloadLink"],
        "fast": data["fastDownloadLink"],
        "direct": data["directDownloadLink"]
    }

    caption = f"""
🎬 {data['fileName']}
📦 Size: {data['sizeFormatted']}
⏱ Duration: {data['duration']}
📺 Quality: {data['quality']}
"""

    keyboard = [
        [InlineKeyboardButton("⬇️ Download", callback_data="download")],
        [InlineKeyboardButton("▶️ Watch", callback_data="watch")]
    ]

    await update.message.reply_photo(
        photo=data["thumbnail"],
        caption=caption,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# WATCH
async def watch_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    streams = context.user_data.get("streams", {})

    buttons = []
    for quality, link in streams.items():
        buttons.append([InlineKeyboardButton(f"🎬 {quality}", url=link)])

    buttons.append([InlineKeyboardButton("🔙 Back", callback_data="back")])

    await query.message.edit_reply_markup(
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# DOWNLOAD
async def download_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    d = context.user_data.get("downloads", {})

    buttons = [
        [InlineKeyboardButton("📥 Normal", url=d.get("normal"))],
        [InlineKeyboardButton("⚡ Fast", url=d.get("fast"))],
        [InlineKeyboardButton("🚀 Direct", url=d.get("direct"))],
        [InlineKeyboardButton("🔙 Back", callback_data="back")]
    ]

    await query.message.edit_reply_markup(
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# BACK
async def back_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("⬇️ Download", callback_data="download")],
        [InlineKeyboardButton("▶️ Watch", callback_data="watch")]
    ]

    await query.message.edit_reply_markup(
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# MAIN
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
app.add_handler(CallbackQueryHandler(watch_callback, pattern="watch"))
app.add_handler(CallbackQueryHandler(download_callback, pattern="download"))
app.add_handler(CallbackQueryHandler(back_callback, pattern="back"))

print("🚀 Bot Running...")
app.run_polling()
