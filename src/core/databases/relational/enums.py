from enum import StrEnum


class DatabaseDriver(StrEnum):
    psycopg = "psycopg"


class DatabaseType(StrEnum):
    postgresql = "postgresql"
