from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import async_sessionmaker


class DBSessionMiddleware(BaseMiddleware):
    def __init__(self, session_factory: async_sessionmaker):
        self.session_factory = session_factory

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        async with self.session_factory() as session:
            data["db_session"] = session
            try:
                result = await handler(event, data)
                # Не используем commit, ручное управление сессиями
                return result

            except Exception as error:  # При необходимости можно оставить только ошибки, связанные со вставкой
                await session.rollback()
                raise error
