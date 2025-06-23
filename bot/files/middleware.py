from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from typing import Callable, Dict, Any, Awaitable

from database.repositories.user import update_last_activity


class LastActivityMiddleware(BaseMiddleware):
    async def __call__( # type: ignore
            self,
            handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
            event: Message | CallbackQuery,
            data: Dict[str, Any],
    ) -> Any:
        user_id = event.from_user.id # type: ignore

        await update_last_activity(user_id)

        return await handler(event, data)