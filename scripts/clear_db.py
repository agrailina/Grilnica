"""
Очистка базы данных
Запуск: python scripts/clear_db.py
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
from app.core.config import settings


async def clear_db():
    """Полная очистка базы данных"""
    
    print("🗑️  Подключение к БД...")
    print(f"   URL: {settings.DATABASE_URL}")
    
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        print("\n⚠️  ВНИМАНИЕ! Будут удалены ВСЕ данные!")
        print("   Таблицы: products, categories, users, cart_items, order_items, orders")
        
        confirm = input("\n   Введите 'YES' для подтверждения: ")
        
        if confirm != "YES":
            print("   ❌ Операция отменена")
            return
        
        try:
            # Отключаем проверку внешних ключей
            await session.execute(text("SET session_replication_role = 'replica'"))
            
            # Список таблиц для очистки (в правильном порядке)
            tables = [
                "order_items",
                "cart_items", 
                "orders",
                "products",
                "categories",
                "users",
            ]
            
            print("\n📋 Очистка таблиц...")
            
            for table in tables:
                result = await session.execute(text(f"DELETE FROM {table}"))
                count = result.rowcount
                print(f"   ✅ {table}: удалено {count} записей")
            
            # Включаем проверку внешних ключей обратно
            await session.execute(text("SET session_replication_role = 'origin'"))
            
            await session.commit()
            
            print("\n" + "=" * 50)
            print("✅ База данных полностью очищена!")
            print("=" * 50)
            
        except Exception as e:
            await session.rollback()
            print(f"\n❌ Ошибка: {e}")
        finally:
            # Восстанавливаем проверку внешних ключей в любом случае
            await session.execute(text("SET session_replication_role = 'origin'"))
            await session.commit()
    
    await engine.dispose()


async def clear_products_only():
    """Очистка только товаров и категорий"""
    
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        try:
            await session.execute(text("SET session_replication_role = 'replica'"))
            
            # Удаляем связанные данные
            await session.execute(text("DELETE FROM order_items"))
            await session.execute(text("DELETE FROM cart_items"))
            
            # Удаляем товары и категории
            products_result = await session.execute(text("DELETE FROM products"))
            categories_result = await session.execute(text("DELETE FROM categories"))
            
            await session.execute(text("SET session_replication_role = 'origin'"))
            await session.commit()
            
            print(f"✅ Удалено товаров: {products_result.rowcount}")
            print(f"✅ Удалено категорий: {categories_result.rowcount}")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Ошибка: {e}")
        finally:
            await session.execute(text("SET session_replication_role = 'origin'"))
            await session.commit()
    
    await engine.dispose()


async def clear_by_table(table_name: str):
    """Очистка конкретной таблицы"""
    
    allowed_tables = ["products", "categories", "users", "cart_items", "order_items", "orders"]
    
    if table_name not in allowed_tables:
        print(f"❌ Таблица '{table_name}' не найдена. Доступные: {', '.join(allowed_tables)}")
        return
    
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        try:
            result = await session.execute(text(f"DELETE FROM {table_name}"))
            await session.commit()
            print(f"✅ Таблица '{table_name}': удалено {result.rowcount} записей")
        except Exception as e:
            await session.rollback()
            print(f"❌ Ошибка: {e}")
    
    await engine.dispose()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Очистка базы данных")
    parser.add_argument(
        "--mode",
        choices=["all", "products", "table"],
        default="all",
        help="Режим очистки: all (всё), products (товары+категории), table (конкретная таблица)"
    )
    parser.add_argument(
        "--table",
        type=str,
        help="Название таблицы для очистки (только с --mode table)"
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Пропустить подтверждение"
    )
    
    args = parser.parse_args()
    
    if args.mode == "all":
        if args.yes:
            # Модифицируем функцию для пропуска подтверждения
            import io
            original_stdin = sys.stdin
            sys.stdin = io.StringIO("YES\n")
            asyncio.run(clear_db())
            sys.stdin = original_stdin
        else:
            asyncio.run(clear_db())
    
    elif args.mode == "products":
        print("🗑️  Очистка товаров и категорий...")
        asyncio.run(clear_products_only())
    
    elif args.mode == "table":
        if not args.table:
            print("❌ Укажите --table <название_таблицы>")
        else:
            asyncio.run(clear_by_table(args.table))