import asyncio
from aiogram import Bot, Dispatcher
from handler.registration_handler import reg_rt
from handler.menu_handler import menu_rt

from config import TOKEN

bot = Bot(token=TOKEN)
dp = Dispatcher()

dp.include_routers(reg_rt, menu_rt)

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')