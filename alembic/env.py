import os
from logging.config import fileConfig
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context
from dotenv import load_dotenv
from app.db.database import Base
import asyncio

# Загружаем переменные окружения из файла .env
load_dotenv()

# Получаем строку подключения из переменных окружения
DATABASE_URL = os.getenv("DATABASE_URL")

# Этот объект предоставляет доступ к значениям из конфигурационного файла Alembic
config = context.config

# Интерпретируем конфигурацию для логирования
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Метаинформация для схемы базы данных
target_metadata = Base.metadata

async def run_migrations_online() -> None:
    """Запуск миграций в онлайн-режиме с асинхронным движком."""
    # Создаем асинхронный движок
    connectable = create_async_engine(DATABASE_URL, echo=True)

    # Подключаемся через асинхронный контекст
    async with connectable.connect() as connection:
        # Конфигурируем контекст для работы с асинхронным соединением
        await connection.run_sync(
            lambda conn: context.configure(
                connection=conn, target_metadata=target_metadata
            )
        )

        # Запускаем миграции в асинхронном контексте
        async with connection.begin():
            await context.run_migrations()

async def run_migrations_offline() -> None:
    """Запуск миграций в оффлайн-режиме с асинхронным движком."""
    # Получаем строку подключения и конфигурируем контекст
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    # Запускаем миграции
    with context.begin_transaction():
        context.run_migrations()

# Выбираем, в каком режиме запускать миграции
if context.is_offline_mode():
    # Ожидаем выполнения в оффлайн-режиме
    asyncio.run(run_migrations_offline())
else:
    # Ожидаем выполнения в онлайн-режиме
    asyncio.run(run_migrations_online())
