# lohinlove.py
# --- Веб-часть для Render ---
import os
from flask import Flask
from threading import Thread
import time as _time

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive and running!"

def run_web_server():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_web_server)
    t.daemon = True
    t.start()

# --- Основной код бота ---
import logging
import random
from datetime import time
from telegram.ext import Application, CommandHandler

BOT_TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

# Сообщения
MORNING_MESSAGES = [
    "Доброе утро, моя любимая ☀️ Пусть сегодня всё будет прекрасно!",
    "Просыпайся, моя красавица ❤️ День ждёт тебя!",
    "Солнышко встало, и вместе с ним проснулась самая милая девочка на свете ☀️",
    "Доброе утро, принцесса 👑 Пусть твой день будет лёгким и добрым!",
    "Пусть сегодня тебе улыбнётся весь мир 🌸 Ты этого заслуживаешь!",
    "Утро начинается с мысли о тебе ❤️",
    "Желаю тебе сладкого утра, как ты 🍯",
    "Пусть утро принесёт тебе уют, тепло и вдохновение 🌅",
    "Ты — мой лучший повод улыбаться по утрам 💕",
    "Доброе утро, ангел мой 😇 Пусть день будет чудесным!"
]

DAY_MESSAGES = [
    "Надеюсь, у тебя всё хорошо 💖 Я просто хотел напомнить, какая ты классная!",
    "Ты делаешь этот мир лучше просто тем, что в нём есть 🌍",
    "Пусть всё, за что ты сегодня возьмёшься, получится идеально ✨",
    "Ты невероятная 💫 Даже если день сложный — я верю в тебя!",
    "Если вдруг устала — помни, что ты заслуживаешь отдыха и любви 🌸",
    "Я бы сейчас всё отдал, чтобы просто обнять тебя 🤍",
    "Ты заслуживаешь только самого лучшего 💐",
    "Не забывай улыбаться 😌 твоя улыбка делает чудеса!",
    "Ты мой источник вдохновения 💞",
    "Надеюсь, твой день проходит чудесно 🌤️"
]

EVENING_MESSAGES = [
    "Спокойной ночи, моя родная 🌙 Пусть тебе снятся самые добрые сны ❤️",
    "День закончился, теперь отдыхай, красавица 🌌",
    "Я горжусь тобой, ты сегодня справилась со всем 💪",
    "Пусть ночь обнимет тебя теплом и покоем 💤",
    "Ты заслужила отдых, моя звёздочка ⭐",
    "Сладких снов, любимая 💋 Я рядом — мысленно и сердцем.",
    "Ты самая лучшая, и пусть даже сны тебе это напомнят 🌙",
    "Пусть твои сны будут добрыми и светлыми, как ты 🌸",
    "Ночь — для того, чтобы восстанавливаться. Спи спокойно ❤️",
    "Обнимаю тебя сквозь экран, спи сладко 😴"
]

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

async def send_message_job(context):
    job_context = context.job.data
    message_type = job_context["type"]
    master_list = job_context["list"]
    bot_data = context.bot_data
    chat_id = bot_data.get("chat_id") or CHAT_ID
    if not chat_id:
        logger.info("chat_id не найден — сообщение не отправлено.")
        return
    message_list_key = f"{message_type}_messages"
    if not bot_data.get(message_list_key):
        bot_data[message_list_key] = master_list.copy()
        random.shuffle(bot_data[message_list_key])
    if not bot_data[message_list_key]:
        bot_data[message_list_key] = master_list.copy()
        random.shuffle(bot_data[message_list_key])
    message = bot_data[message_list_key].pop()
    await context.bot.send_message(chat_id=chat_id, text=message)
    logger.info(f"Отправлено '{message_type}' сообщение в чат {chat_id}")

async def start(update, context):
    chat_id = update.effective_chat.id
    user_name = update.effective_user.first_name or "друг"
    context.bot_data["chat_id"] = chat_id
    await update.message.reply_text(f"Привет, {user_name}! ❤️\nЯ буду присылать тебе приятные сообщения каждый день 🥰")

    current_jobs = context.job_queue.get_jobs_by_name(str(chat_id))
    if not current_jobs:
        # UTC+3 время
        context.job_queue.run_daily(send_message_job, time=time(hour=7, minute=30),  # утро 07:30
                                    data={"type": "morning", "list": MORNING_MESSAGES},
                                    name=str(chat_id))
        context.job_queue.run_daily(send_message_job, time=time(hour=14, minute=0),   # день 14:00
                                    data={"type": "day", "list": DAY_MESSAGES},
                                    name=str(chat_id))
        context.job_queue.run_daily(send_message_job, time=time(hour=23, minute=30),  # вечер 23:30
                                    data={"type": "evening", "list": EVENING_MESSAGES},
                                    name=str(chat_id))
        logger.info(f"Добавлены ежедневные задания для чата {chat_id}")
    if "day_messages" not in context.bot_data:
        context.bot_data["day_messages"] = DAY_MESSAGES.copy()
        random.shuffle(context.bot_data["day_messages"])
    first_message = context.bot_data["day_messages"].pop()
    await context.bot.send_message(chat_id=chat_id, text=first_message)

async def test_send(update, context):
    chat_id = update.effective_chat.id
    context.bot_data["chat_id"] = chat_id
    for ttype, lst in [("morning", MORNING_MESSAGES), ("day", DAY_MESSAGES), ("evening", EVENING_MESSAGES)]:
        msg = random.choice(lst)
        await context.bot.send_message(chat_id=chat_id, text=f"[TEST {ttype}] " + msg)
    await update.message.reply_text("Тестовые сообщения отправлены!")

def main():
    if not BOT_TOKEN:
        print("Ошибка: BOT_TOKEN не найден. Убедись, что он добавлен в Render → Environment.")
        return

    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("test", test_send))
    keep_alive()
    _time.sleep(1)
    print("Бот успешно запущен...")
    application.run_polling()

if __name__ == "__main__":
    main()
