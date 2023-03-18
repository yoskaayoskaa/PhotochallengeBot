from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import Delete, Insert, Select, Update

from config.config import DatabaseConfig
from database.sqlalchemy_base import db


class Database:
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.db: Optional[declarative_base] = None
        self.engine: Optional[AsyncEngine] = None
        self.session: Optional[async_sessionmaker, AsyncSession] = None
        self.database_url = self.generate_pg_database_url()

    async def connect(self, *_: list, **__: dict) -> None:
        self.db = db
        self.engine = create_async_engine(self.database_url, future=True)
        self.session = async_sessionmaker(bind=self.engine, expire_on_commit=False)

    async def disconnect(self, *_: list, **__: dict) -> None:
        self.session = None

        if self.engine:
            await self.engine.dispose()
            self.engine = None

    async def execute_statement(self, statement: Select | Insert | Update | Delete) -> None:
        async with self.session() as session:
            await session.execute(statement)
            await session.commit()
        await self.engine.dispose()

    async def execute_statement_scalars(self, statement: Select | Insert | Update | Delete) -> List:
        async with self.session() as session:
            scalars = await session.scalars(statement)
            await session.commit()
        await self.engine.dispose()
        return scalars.all()

    def generate_pg_database_url(self) -> str:
        return "{driver}://{user}:{password}@{host}/{db_name}".format(
            driver=self.config.driver,
            user=self.config.user,
            password=self.config.password,
            host=self.config.host,
            db_name=self.config.database,
        )
