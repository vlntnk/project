from typing import Generator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

import settings

# Подклоючение к базе данных
engine = create_async_engine(settings.REAL_DATABASE_URL, future=True, echo=True)

# Создание ассинхронной сессии
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_db() -> Generator:
    try:
        session: AsyncSession = async_session()
        yield session
    finally:
        await session.close()

# async def get_db() -> AsyncSession:
#     async with async_session() as session:
#         yield session