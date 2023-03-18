import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass
class DatabaseConfig:
    host: str = "localhost"
    port: str = "5432"
    user: str = "postgres"
    password: str = "postgres"
    database: str = "project"
    driver: str = "postgresql+asyncpg"


@dataclass
class TgBot:
    token: str
    id: int
    workers_qty: int
    database: DatabaseConfig = None


@dataclass
class Config:
    tg_bot: TgBot


def setup_config() -> Config:
    return Config(
        tg_bot=TgBot(
            token=os.getenv("BOT_TOKEN"),
            id=int(os.getenv("BOT_ID")),
            workers_qty=int(os.getenv("WORKERS")),
            database=DatabaseConfig(
                host=str(os.getenv("PG_HOST")),
                port=str(os.getenv("PG_PORT")),
                user=str(os.getenv("PG_USER")),
                password=str(os.getenv("PG_PASSWORD")),
                database=str(os.getenv("PG_DATABASE")),
                driver=str(os.getenv("PG_DRIVER")),
            ),
        )
    )


def setup_config_tests() -> Config:
    return Config(
        tg_bot=TgBot(
            token=os.getenv("BOT_TOKEN_TESTS"),
            id=int(os.getenv("BOT_ID_TESTS")),
            workers_qty=int(os.getenv("WORKERS")),
            database=DatabaseConfig(
                host=str(os.getenv("PG_HOST_TESTS")),
                port=str(os.getenv("PG_PORT_TESTS")),
                user=str(os.getenv("PG_USER_TESTS")),
                password=str(os.getenv("PG_PASSWORD_TESTS")),
                database=str(os.getenv("PG_DATABASE_TESTS")),
                driver=str(os.getenv("PG_DRIVER_TESTS")),
            ),
        )
    )
