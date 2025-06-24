from aiogram import F
from aiogram.types import Message
from aiogram.filters import Filter

from src.database.repositories.admin import is_user_admin


class AdminFilter(Filter):
    async def __call__(self, message: Message):
        return await is_user_admin(message.from_user.id) # type: ignore