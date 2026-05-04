# alembic/env.py

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import sys
import os
from pathlib import Path

# Добавляем корень проекта в sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.base import Base
from app.core.config import settings  # Используем готовый синглтон

# Важно: импортируем все модели, чтобы Alembic их видел
from app.models import *  # noqa: F403, F401

# Конфиг Alembic
config = context.config

# Настройка логирования
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Метаданные для автогенерации
target_metadata = Base.metadata

def get_sync_url():
    """
    Получаем синхронный URL как строку.
    Pydantic PostgresDsn может возвращать объект, поэтому явно конвертируем.
    """
    url = settings.SYNC_DATABASE_URL
    # Явное преобразование в строку
    return str(url)

def run_migrations_offline() -> None:
    """
    Запуск миграций в офлайн-режиме.
    """
    url = get_sync_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """
    Запуск миграций в онлайн-режиме.
    """
    configuration = config.get_section(config.config_ini_section)
    
    # Важно: переопределяем URL в конфигурации как СТРОКУ
    configuration["sqlalchemy.url"] = get_sync_url()
    
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata,
            compare_type=True,  
            compare_server_default=True, 
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()