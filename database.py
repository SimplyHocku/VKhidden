import asyncio

from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select

DB = "sqlite+aiosqlite:///key.db"
engine = create_async_engine(DB)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()


class Keys(Base):
    __tablename__ = "key"
    key_id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(nullable=False)

    def __repr__(self):
        return f"key = {self.key}"


async def create_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def _get_keys():
    async with async_session() as session:
        async with session.begin():
            keys = await session.execute(select(Keys))
            pretty_key = await _get_pretty_keys(keys.all())
            return pretty_key


async def create_key(key_value):
    async with async_session() as session:
        async with session.begin():
            session.add(Keys(key=key_value))


async def _get_pretty_keys(keys):
    for_return_keys = {str(index): key[0].key for index, key in enumerate(keys)}
    return for_return_keys


# asyncio.run(create_database())
# asyncio.run(create_key(key_value="acxvgdas231asdasdasd21"))
