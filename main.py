import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from aiogram.dispatcher.filters import Text
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import random
import asyncio
import json
import os
from dotenv import load_dotenv

load_dotenv()
API_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
scheduler = AsyncIOScheduler()

# أذكار
azkar_morning = ["ذكر صباح 1", "ذكر صباح 2"]
azkar_evening = ["ذكر مساء 1", "ذكر مساء 2"]
azkar_general = ["ذكر عام 1", "ذكر عام 2", "ذكر عام 3"]

# قائمة المشتركين
subscribers_file = "subscribers.json"
if not os.path.exists(subscribers_file):
    with open(subscribers_file, "w") as f:
        json.dump({"general": []}, f)

def load_subscribers():
    with open(subscribers_file, "r") as f:
        return json.load(f)

def save_subscribers(data):
    with open(subscribers_file, "w") as f:
        json.dump(data, f)

# القوائم
main_menu = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.add("أذكار الصباح", "أذكار المساء").add("القرآن الكريم (صوت)").add("الاشتراك في إشعارات الأذكار", "إلغاء الاشتراك")

back_button = KeyboardButton("رجوع")
back_menu = ReplyKeyboardMarkup(resize_keyboard=True).add(back_button)

@dp.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    await message.answer("مرحبًا بك في بوت الأذكار", reply_markup=main_menu)

@dp.message_handler(Text(equals="أذكار الصباح"))
async def morning_zekr(message: types.Message):
    await message.answer(random.choice(azkar_morning), reply_markup=back_menu)

@dp.message_handler(Text(equals="أذكار المساء"))
async def evening_zekr(message: types.Message):
    await message.answer(random.choice(azkar_evening), reply_markup=back_menu)

@dp.message_handler(Text(equals="الاشتراك في إشعارات الأذكار"))
async def subscribe_general(message: types.Message):
    data = load_subscribers()
    user_id = str(message.from_user.id)
    if user_id not in data["general"]:
        data["general"].append(user_id)
        save_subscribers(data)
        await message.answer("تم الاشتراك في إشعارات الأذكار العشوائية.", reply_markup=main_menu)
    else:
        await message.answer("أنت مشترك بالفعل.", reply_markup=main_menu)

@dp.message_handler(Text(equals="إلغاء الاشتراك"))
async def unsubscribe_general(message: types.Message):
    data = load_subscribers()
    user_id = str(message.from_user.id)
    if user_id in data["general"]:
        data["general"].remove(user_id)
        save_subscribers(data)
        await message.answer("تم إلغاء الاشتراك.", reply_markup=main_menu)
    else:
        await message.answer("أنت غير مشترك.", reply_markup=main_menu)

@dp.message_handler(Text(equals="رجوع"))
async def back(message: types.Message):
    await message.answer("تم الرجوع إلى القائمة الرئيسية.", reply_markup=main_menu)

@dp.message_handler(Text(equals="القرآن الكريم (صوت)"))
async def quran_menu(message: types.Message):
    quran_kb = InlineKeyboardMarkup(row_width=1)
    quran_kb.add(
        InlineKeyboardButton("سورة الفاتحة - عبد الباسط", url="https://..."),
        InlineKeyboardButton("سورة الملك - مشاري العفاسي", url="https://..."),
        InlineKeyboardButton("رجوع", callback_data="back")
    )
    await message.answer("اختر السورة والقارئ:", reply_markup=quran_kb)

@dp.callback_query_handler(lambda c: c.data == "back")
async def inline_back(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, "تم الرجوع إلى القائمة الرئيسية.", reply_markup=main_menu)

async def send_random_zekr():
    data = load_subscribers()
    for user_id in data.get("general", []):
        try:
            await bot.send_message(user_id, random.choice(azkar_general))
        except Exception as e:
            print(f"خطأ أثناء إرسال الذكر: {e}")

async def on_startup(dp):
    scheduler.add_job(send_random_zekr, "interval", hours=2)
    scheduler.start()

if __name__ == "__main__":
    from aiogram import executor
    executor.start_polling(dp, on_startup=on_startup)
