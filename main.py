import os
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, CallbackQueryHandler, filters

# 🔑 احصل على التوكن من Environment Variables في Render
TOKEN = os.getenv("TOKEN")

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# لتخزين اسم الأغنية مؤقتًا لكل مستخدم
user_queries = {}

# /start
async def start(update: Update, context):
    await update.message.reply_text("🎧 أرسل اسم الأغنية التي تريد تحميلها:")

# استقبال نص المستخدم (اسم الأغنية)
async def search(update: Update, context):
    query = update.message.text
    user_queries[update.message.chat_id] = query

    keyboard = [
        [InlineKeyboardButton("🎵 جودة 128kbps", callback_data="128")],
        [InlineKeyboardButton("🔥 جودة عالية 320kbps", callback_data="320")]
    ]

    await update.message.reply_text(
        f"اختر الجودة للأغنية:\n🎧 {query}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# التعامل مع الأزرار (اختيار الجودة)
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

        await query.message.reply_audio(
            audio=open(file_path, 'rb'),
            title=entry.get('title'),
            performer=entry.get('uploader')
        )

        # حذف الملف بعد الإرسال لتوفير المساحة
        os.remove(file_path)

    except Exception as e:
        await query.message.reply_text(f"❌ حدث خطأ: {e}")

# إعداد التطبيق
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT, search))
app.add_handler(CallbackQueryHandler(download))

print("🚀 VIP BOT RUNNING...")
app.run_polling()