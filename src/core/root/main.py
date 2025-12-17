from sys import path as sys_path
from os import getcwd as os_getcwd

sys_path.append(os_getcwd())

from asyncio import run as run_async

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.base import BaseStorage
from aiogram.fsm.storage.memory import MemoryStorage
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from src.core.root.config import service_config
from src.core.root.middlewares import DBSessionMiddleware
from src.handlers.sso import SSO_ROUTER
from src.handlers.videos import VIDEOS_ROUTER


async def run(
        telegram_token: str,
        db_sessions_factory: async_sessionmaker[AsyncSession],
        storage: BaseStorage | MemoryStorage
):
    bot: Bot = Bot(token=telegram_token)
    dispatcher: Dispatcher = Dispatcher(storage=storage)

    # Middlewares:
    dispatcher.update.outer_middleware(
        DBSessionMiddleware(session_factory=db_sessions_factory)
    )

    # Routes:
    dispatcher.include_router(SSO_ROUTER)
    dispatcher.include_router(VIDEOS_ROUTER)

    try:
        await dispatcher.start_polling(bot)

    finally:
        await bot.session.close()
        await dispatcher.storage.close()


if __name__ == "__main__":
    run_async(
        run(
            telegram_token=service_config.telegram_bot_token,
            db_sessions_factory=service_config.create_session_factory(),
            storage=MemoryStorage()
        )
    )
