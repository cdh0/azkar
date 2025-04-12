import logging
import random
import datetime
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    JobQueue,
)
from dotenv import load_dotenv

# تحميل متغيرات البيئة من ملف .env
load_dotenv()

# إعدادات التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# قراءة التوكن من متغير البيئة
BOT_TOKEN = os.getenv('BOT_TOKEN')

# قوائم الأذكار
azkar_morning = [
    "أصبحنا وأصبح الملك لله...",
    "اللهم بك أصبحنا وبك أمسينا...",
    # أضف المزيد من الأذكار هنا
]

azkar_evening = [
    "أمسينا وأمسى الملك لله...",
    "اللهم بك أمسينا وبك أصبحنا...",
    # أضف المزيد من الأذكار هنا
]

random_azkar = [
    "سبحان الله وبحمده...",
    "لا إله إلا الله وحده لا شريك له...",
    # أضف المزيد من الأذكار هنا
]

# دالة بدء البوت
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📿 الاشتراك في أذكار الصباح", callback_data='subscribe_morning')],
        [InlineKeyboardButton("🌙 الاشتراك في أذكار المساء", callback_data='subscribe_evening')],
        [InlineKeyboardButton("🔁 الحصول على ذكر عشوائي", callback_data='random_azkar')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('مرحبًا! اختر من الخيارات التالية:', reply_markup=reply_markup)

# دالة التعامل مع الأزرار
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    choice = query.data
    chat_id = query.message.chat_id

    if choice == 'subscribe_morning':
        context.chat_data['subscribe_morning'] = True
        context.chat_data['subscribe_evening'] = False
        await query.edit_message_text(text="تم الاشتراك في أذكار الصباح. ستتلقى ذكرًا كل صباح.")
    elif choice == 'subscribe_evening':
        context.chat_data['subscribe_morning'] = False
        context.chat_data['subscribe_evening'] = True
        await query.edit_message_text(text="تم الاشتراك في أذكار المساء. ستتلقى ذكرًا كل مساء.")
    elif choice == 'random_azkar':
        azkar = random.choice(random_azkar)
        await query.edit_message_text(text=f"🔹 {azkar}")

# دوال إرسال الأذكار
async def send_morning_azkar(context: ContextTypes.DEFAULT_TYPE):
    for chat_id, data in context.application.chat_data.items():
        if data.get('subscribe_morning'):
            azkar = random.choice(azkar_morning)
            await context.bot.send_message(chat_id=chat_id, text=f"صباح الخير! 🌞\n\n🔹 {azkar}")

async def send_evening_azkar(context: ContextTypes.DEFAULT_TYPE):
    for chat_id, data in context.application.chat_data.items():
        if data.get('subscribe_evening'):
            azkar = random.choice(azkar_evening)
            await context.bot.send_message(chat_id=chat_id, text=f"مساء الخير! 🌙\n\n🔹 {azkar}")

# تشغيل البوت
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(CallbackQueryHandler(button_handler))

    # جدولة إرسال الأذكار
    job_queue = app.job_queue
    job_queue.run_daily(send_morning_azkar, time=datetime.time(hour=6, minute=0))
    job_queue.run_daily(send_evening_azkar, time=datetime.time(hour=18, minute=0))

    app.run_polling()

if name == 'main':
    main()