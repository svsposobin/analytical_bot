from src.core.databases.relational.enums import DatabaseDriver, DatabaseType
from src.core.databases.relational.schemas import DatabaseSchema


class RelationalDatabase:
    def __init__(self, db: DatabaseSchema, driver: DatabaseDriver, database: DatabaseType) -> None:
        self.DSN: str = f"{database.value}+{driver.value}://{db.USER}:{db.PASSWORD}@{db.HOST}:{db.PORT}/{db.DATABASE}"
