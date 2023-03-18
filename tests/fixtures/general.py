import asyncio

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker

from bot.general import TgBot
from config.config import Config, setup_config_tests


# this code is taken from here (https://github.com/pytest-dev/pytest-asyncio/issues/371#issuecomment-1161462430)
# as a solution of 'Event loop is closed' issue
@pytest.yield_fixture
def event_loop():
    """Create an instance of the default event loop for each test case."""
    policy = asyncio.WindowsSelectorEventLoopPolicy()
    res = policy.new_event_loop()
    asyncio.set_event_loop(res)
    res._close = res.close
    res.close = lambda: None

    yield res

    res._close()


@pytest.fixture
async def tg_bot() -> TgBot:
    config_tests: Config = setup_config_tests()
    tg_bot = TgBot(config=config_tests)
    await tg_bot.database.connect()
    yield tg_bot
    await tg_bot.database.disconnect()


@pytest.fixture
def db_session(tg_bot) -> async_sessionmaker:
    return tg_bot.database.session


@pytest.fixture(autouse=True, scope="function")
async def clear_db(tg_bot) -> None:
    yield

    async with tg_bot.database.session.begin() as session:
        for table in tg_bot.database.db.metadata.tables:
            await session.execute(text(f"TRUNCATE {table} CASCADE"))
