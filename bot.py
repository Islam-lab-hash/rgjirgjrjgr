"""Bot entry point."""
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

import database as db
import handlers_admin
import handlers_user
from config import BOT_TOKEN

logging.basicConfig(level=logging.INFO)


async def main():
    await db.init_db()

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(handlers_admin.router)
    dp.include_router(handlers_user.router)

    print("✅ Бот запущен")

    try:
        await dp.start_polling(bot, allowed_updates=[])
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
