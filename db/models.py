import asyncio
from datetime import datetime
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import Mapped, DeclarativeBase, mapped_column

path = Path(__file__).parent.parent / 'storage' / 'database.db'
engine = create_async_engine(url=f"sqlite+aiosqlite:///{path}")
session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    ...


class User(Base):
    __tablename__ = 'users'

    chat_id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str | None]
    remaining_time: Mapped[datetime | None]


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def main():
    await init_db()


# asyncio.run(main())
