import os
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, CallbackQueryHandler, filters

TOKEN = os.getenv("TOKEN")
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

user_queries = {}

async def start(update: Update, context):
    await update.message.reply_text("🎧 مرحبًا! أرسل اسم الأغنية التي تريد تحميلها:")

async def search(update: Update, context):
    query = update.message.text
    user_queries[update.message.chat_id] = query

    keyboard = [
        [InlineKeyboardButton("🎵 جودة 128kbps", callback_data="128")],
        [InlineKeyboardButton("🔥 جودة 320kbps", callback_data="320")]
    ]

    await update.message.reply_text(
        f"اختر الجودة للأغنية:\n🎧 {query}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def download(update: Update, context):
    query = update.callback_query
    await query.answer()
    quality = query.data
    chat_id = query.message.chat_id
    song = user_queries.get(chat_id)

    await query.message.reply_text("⏳ جاري التحميل...")

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
        'noplaylist': True,
        'quiet': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': quality,
        }],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{song}", download=True)
            entry = info['entries'][0]
            file_path = ydl.prepare_filename(entry).replace(".webm", ".mp3").replace(".m4a", ".mp3")
            thumbnail = entry.get('thumbnail')

        # إرسال الصورة + معلومات الأغنية
        caption = f"🎵 {entry.get('title')}\n👤 {entry.get('uploader')}"
        if thumbnail:
            await query.message.reply_photo(photo=thumbnail, caption=caption)
        else:
            await query.message.reply_text(caption)

        # إرسال الأغنية mp3
        await query.message.reply_audio(audio=open(file_path, 'rb'), title=entry.get('title'), performer=entry.get('uploader'))

        os.remove(file_path)

        # زر البحث مرة أخرى
        keyboard = [[InlineKeyboardButton("🔄 ابحث مرة أخرى", callback_data="search_again")]]
        await query.message.reply_text("✅ يمكنك البحث عن أغنية أخرى:", reply_markup=InlineKeyboardMarkup(keyboard))

    except Exception as e:
        await query.message.reply_text(f"❌ حدث خطأ: {e}")

async def search_again(update: Update, context):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("🎧 أرسل اسم الأغنية الجديدة:")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT, search))
app.add_handler(CallbackQueryHandler(download, pattern='^(128|320)$'))
app.add_handler(CallbackQueryHandler(search_again, pattern='^search_again$'))

print("🚀 VIP 2.0 BOT RUNNING...")
app.run_polling()