#!/usr/bin/env python3
"""
Скрипт для создания всех таблиц в базе данных
"""

import asyncio
import sys
import os

# Добавляем корневую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from infrastructure.repositiry.base_repository import engine
from infrastructure.repositiry.db_models import Base

async def create_tables():
    """Создание всех таблиц"""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("Все таблицы успешно созданы!")
    except Exception as e:
        print(f"Ошибка при создании таблиц: {e}")

if __name__ == "__main__":
    asyncio.run(create_tables())
