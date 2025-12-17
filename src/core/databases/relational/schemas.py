from typing import Optional

from pydantic import BaseModel


class DatabaseSchema(BaseModel):
    HOST: str
    PORT: str
    USER: str
    PASSWORD: Optional[str]
    DATABASE: str


class PoolSettings(BaseModel):
    pool_size: int = 5
    max_overflow: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 300
    echo: bool = False
