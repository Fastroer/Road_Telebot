import asyncio
import logging

from aiogram import Bot, Dispatcher
import config
from handlers import router

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()


async def main():
    logging.basicConfig(level=logging.DEBUG)
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
