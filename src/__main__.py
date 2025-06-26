import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from src.handlers import menu, registration, request, admin
from src.config import config
from src.database.db import db
from src.files.middleware import LastActivityMiddleware


bot = Bot(token=config.TOKEN)
dp = Dispatcher(storage=MemoryStorage())

dp.message.middleware(LastActivityMiddleware())
dp.callback_query.middleware(LastActivityMiddleware())

dp.include_router(admin.router)
dp.include_router(registration.router)
dp.include_router(menu.router)
dp.include_router(request.router)


@dp.startup()
async def on_startup():
    await db.connect()


@dp.shutdown()
async def on_shutdown():
    await db.close()


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
