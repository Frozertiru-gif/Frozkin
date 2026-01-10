import asyncio
import os
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from redis import Redis

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
WEBAPP_PUBLIC_URL = os.getenv("WEBAPP_PUBLIC_URL", "")
API_PUBLIC_URL = os.getenv("API_PUBLIC_URL", "")
TG_BOT_API_BASE_URL = os.getenv("TG_BOT_API_BASE_URL")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

bot = Bot(token=BOT_TOKEN, base_url=TG_BOT_API_BASE_URL)
dp = Dispatcher()
redis = Redis.from_url(REDIS_URL, decode_responses=True)


async def set_active_message(chat_id: int, message_id: int):
    key = f"active_message:{chat_id}"
    previous = redis.get(key)
    if previous:
        try:
            await bot.edit_message_reply_markup(chat_id=chat_id, message_id=int(previous), reply_markup=None)
        except Exception:
            pass
    redis.set(key, message_id)


def is_debounced(chat_id: int, action: str, ttl: int = 1) -> bool:
    key = f"debounce:{chat_id}:{action}"
    return not redis.set(key, "1", nx=True, ex=ttl)


@dp.message(CommandStart())
async def start(message: types.Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Каталог", web_app=WebAppInfo(url=WEBAPP_PUBLIC_URL))],
            [InlineKeyboardButton(text="Помощь", callback_data="help")],
            [InlineKeyboardButton(text="Статус", callback_data="status")],
        ]
    )
    sent = await message.answer("Добро пожаловать!", reply_markup=keyboard)
    await set_active_message(message.chat.id, sent.message_id)


@dp.callback_query(lambda c: c.data == "help")
async def help_callback(query: types.CallbackQuery):
    if is_debounced(query.message.chat.id, "help"):
        return
    await query.answer()
    sent = await bot.send_message(query.message.chat.id, "Используйте кнопку Каталог для просмотра.")
    await set_active_message(query.message.chat.id, sent.message_id)


@dp.callback_query(lambda c: c.data == "status")
async def status_callback(query: types.CallbackQuery):
    if is_debounced(query.message.chat.id, "status"):
        return
    await query.answer()
    sent = await bot.send_message(query.message.chat.id, "Бот работает. API: " + API_PUBLIC_URL)
    await set_active_message(query.message.chat.id, sent.message_id)


async def deliver_video(request: web.Request):
    payload = await request.json()
    chat_id = int(payload["chat_id"])
    file_id = payload["file_id"]
    caption = payload.get("caption")
    lock_key = f"deliver_lock:{chat_id}"
    if not redis.set(lock_key, "1", nx=True, ex=10):
        return web.json_response({"status": "busy"}, status=429)
    cooldown_key = f"cooldown:{chat_id}"
    if not redis.set(cooldown_key, "1", nx=True, ex=20):
        redis.delete(lock_key)
        return web.json_response({"status": "cooldown"}, status=429)
    try:
        await bot.send_video(chat_id=chat_id, video=file_id, caption=caption)
        return web.json_response({"status": "sent"})
    finally:
        redis.delete(lock_key)


async def run_http_server():
    app = web.Application()
    app.router.add_post("/deliver", deliver_video)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8085)
    await site.start()


async def main():
    await run_http_server()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
