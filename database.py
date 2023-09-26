import asyncio

from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select, update

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


class Guest(Base):
    __tablename__ = "guest"
    guest_id: Mapped[int] = mapped_column(primary_key=True)
    guest_host: Mapped[str] = mapped_column(nullable=False)
    guest_alias: Mapped[str] = mapped_column(nullable=False)
    is_allowed: Mapped[bool] = mapped_column(default=False)

    def __repr__(self):
        return f"{Guest.__name__}({self.guest_host}//{self.guest_alias}//{self.is_allowed})"


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


async def _save_vk_token(key_value):
    async with async_session() as session:
        async with session.begin():
            session.add(Keys(key=key_value))


async def _get_pretty_keys(keys):
    for_return_keys = {str(index): key[0].key for index, key in enumerate(keys)}
    return for_return_keys


async def _add_host_guest(host, alias):
    async with async_session() as session:
        async with session.begin():
            session.add(Guest(guest_host=host, guest_alias=alias))
            return 200


async def _get_host_guest_allow(host, alias):
    async with async_session() as session:
        async with session.begin():
            allowed = await session.execute(
                select(Guest.is_allowed).where(Guest.guest_host == host, Guest.guest_alias == alias))
            return allowed.scalar()


async def _set_guest_permission(host, alias, permission):
    async with async_session() as session:
        async with session.begin():
            await session.execute(
                update(Guest).where(Guest.guest_host == host, Guest.guest_alias == alias).values(is_allowed=permission))


async def _get_guest_exist(host, alias):
    async with async_session() as session:
        async with session.begin():
            guest = await session.execute(select(Guest).where(Guest.guest_host == host, Guest.guest_alias == alias))
            return guest.scalar()

async def _get_all_guests_with_perm():
    async with async_session() as session:
        async with session.begin():
            guests = await session.execute(select(Guest))
            return guests.scalars().all()
            # print(guests.scalars()[0][0].is_allowed)
            # print(guests.all())

# asyncio.run(_add_host_guest("127.0.0.1", "Binary"))
# asyncio.run(create_database())
# asyncio.run(_set_guest_permission("127.0.0.1", "Hocku", True))
# asyncio.run(_get_all_guests_with_perm())