# STDLIB
from typing import Annotated, AsyncGenerator

# THIRDPARTY
from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# FIRSTPARTY
from app.logger import logger

engine = create_async_engine(url="sqlite+aiosqlite:///db.sqlite3")
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Функция для создания экземпляра асинхронной сессии базы данных.

    Yields:
        AsyncSession: Асинхронная сессия SQLAlchemy.
    """
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except:
            await session.rollback()
            raise
        finally:
            await session.close()


DbSession = Annotated[AsyncSession, Depends(get_session)]


async def check_db_connection():
    async with async_session() as session:
        try:
            await session.execute(text("SELECT 1"))
            logger.info("Database connection successful")
        except Exception as e:
            logger.error(f"Unsuccessful connection to database: {e}", exc_info=True)
            raise e


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True)
