from dataclasses import dataclass
from os import getenv
from typing import Optional

from dotenv import load_dotenv, find_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, AsyncEngine, create_async_engine

from src.core.databases.relational.connection import RelationalDatabase
from src.core.databases.relational.enums import DatabaseDriver, DatabaseType
from src.core.databases.relational.schemas import DatabaseSchema, PoolSettings
from src.core.llms.schemas import YandexGPTAuth

load_dotenv(find_dotenv(".env"))


@dataclass(frozen=True)
class Config:
    telegram_bot_token: str
    yandex_gpt_auth: YandexGPTAuth
    main_database: RelationalDatabase

    def create_session_factory(
            self,
            pool_settings: Optional[PoolSettings] = None
    ) -> async_sessionmaker[AsyncSession]:
        db: RelationalDatabase = getattr(self, "main_database")

        if pool_settings is None:
            pool_settings = PoolSettings(
                pool_size=getenv("DATABASE_MAX_POOL_SIZE"),  # type: ignore
                max_overflow=getenv("DATABASE_MAX_OVERFLOW"),  # type: ignore
                pool_timeout=getenv("DATABASE_POOL_TIMEOUT"),  # type: ignore
                pool_recycle=getenv("DATABASE_POOL_RECYCLE")  # type: ignore
            )

        engine: AsyncEngine = create_async_engine(url=db.DSN, **pool_settings.model_dump())
        return async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False
        )


service_config: Config = Config(
    main_database=RelationalDatabase(
        db=DatabaseSchema(
            HOST=getenv("PSQL_HOST"),  # type: ignore
            PORT=getenv("PSQL_PORT"),  # type: ignore
            USER=getenv("PSQL_USER"),  # type: ignore
            PASSWORD=getenv("PSQL_PASSWORD"),  # type: ignore
            DATABASE=getenv("PSQL_DATABASE")  # type: ignore
        ),
        driver=DatabaseDriver.psycopg,
        database=DatabaseType.postgresql
    ),

    telegram_bot_token=getenv("TELEGRAM_BOT_TOKEN"),  # type: ignore

    yandex_gpt_auth=YandexGPTAuth(
        api_key=getenv("YANDEX_GPT_API_KEY"),  # type: ignore
        folder_id=getenv("YANDEX_GPT_FOLDER_ID")  # type: ignore
    )
)
