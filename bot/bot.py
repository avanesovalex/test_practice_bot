import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from handler import menu, registration
from config import TOKEN

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

dp.include_router(registration.router)
dp.include_router(menu.router)


async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')