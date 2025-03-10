from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")


engine = create_async_engine(DATABASE_URL, echo=True)
# Иногда типовая система не распознает AsyncEngine корректно,
# поэтому можно добавить комментарий для подавления ошибки типов.
AsyncSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)  # type: ignore
Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


"""

Синхронная настройка подключения к базе

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Загружаем переменные из .env
load_dotenv()

# Получаем URL базы данных из переменных окружения
DATABASE_URL = os.getenv("DATABASE_URL")

# Создаём движок SQLAlchemy
engine = create_engine(DATABASE_URL, echo=True)

# Создаём сессию
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс моделей
Base = declarative_base()

# Функция для получения сессии в FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
"""