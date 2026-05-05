"""
Заполнение базы данных товарами Комбо
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
from app.core.config import settings
from app.services.category_service import CategoryService
from app.services.product_service import ProductService
from app.schemas.category import CategoryCreate
from app.schemas.product import ProductCreate
from decimal import Decimal


async def seed_combo():
    """Заполняем категорию Комбо и товары"""
    
    print("🔌 Проверка подключения к БД...")
    print(f"   URL: {settings.DATABASE_URL}")
    
    # Проверяем подключение
    try:
        engine = create_async_engine(settings.DATABASE_URL, echo=False)
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            print("   ✅ Подключение успешно!\n")
    except Exception as e:
        print(f"   ❌ Ошибка подключения: {e}")
        print("\n   💡 Проверьте .env файл:")
        print(f"   POSTGRES_HOST=db (не localhost!)")
        return
    
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        cat_service = CategoryService(session)
        prod_service = ProductService(session)
        
        # Создаем категорию "Комбо"
        print("📁 Создаем категорию Комбо...")
        try:
            combo_category = await cat_service.create_category(CategoryCreate(
                name="Комбо",
                slug="combo",
                icon="🍱",
                order=1
            ))
            print(f"   ✅ Категория создана: {combo_category.name}")
        except Exception as e:
            if "уже существует" in str(e):
                print("   ⚠️  Категория уже существует, получаем...")
                combo_category = await cat_service.get_category_by_slug("combo")
                print(f"   ✅ ID: {combo_category.id}")
            else:
                print(f"   ❌ Ошибка: {e}")
                return
        
        # Товары Комбо
        combo_products = [
            {
                "name": "Шары залетают",
                "description": "Идеально залетают под киношку и на вечеринке! Сочные мясные шарики классические 5 шт., с сыром 5 шт., пикантные Том Ям 5 шт., нежные мини-беляшки 5 шт., а ещё сырные шарики халапеньо 4 шт. и с беконом 4 шт.",
                "price": Decimal("729.00"),
                "image": "/src/combo/elem_1.png",
            },
            {
                "name": "Покушал как у мамы",
                "description": "Вкусно, сытно и с душой. Наваристый супчик, сытная роллини и сочный воск – идеально для обеда или ужина.",
                "price": Decimal("499.00"),
                "image": "/src/combo/elem_2.png",
            },
            {
                "name": "На компанию",
                "description": "Две ароматные итальянские пиццы 30 см – «Пепперони» и «4 мяса», крылышки чикен фри 4 шт., чигеты 6 шт., сочные мясные шарики, сырные шарики, картошка фри и два соуса.",
                "price": Decimal("1999.00"),
                "image": "/src/combo/elem_3.png",
            },
            {
                "name": "На Вкусе",
                "description": "Фирменный хот-дог, золотистая хрустящая картошечка и морс на выбор – брусничный или облепиховый. Любимое сочетание для отличного перекуса!",
                "price": Decimal("549.00"),
                "image": "/src/combo/elem_4.png",
            },
            {
                "name": "Сладкая радость",
                "description": "Согревайся со вкусом! Нежные творожные шарики со сгущенкой и авторский зимний напиток на выбор.",
                "price": Decimal("319.00"),
                "image": "/src/combo/elem_5.png",
            },
            {
                "name": "3 пиццы",
                "description": "Три итальянские пиццы (30 см) – Пепперони, Карбонара и Парочка. Комбо подобрано идеально.",
                "price": Decimal("1425.00"),
                "image": "/src/combo/elem_6.png",
            },
            {
                "name": "5 пицц",
                "description": "Пять итальянских пицц (30 см) – Пепперони, 4 Масса, Молодежная, Жульен, Карбонара.",
                "price": Decimal("2595.00"),
                "image": "/src/combo/elem_7.png",
            },
            {
                "name": "7 пицц",
                "description": "Семь итальянских пицц (30 см) – Пепперони, 4 Масса, Молодежная, Жульен, Карбонара, Добрейшая, Парочка.",
                "price": Decimal("3685.00"),
                "image": "/src/combo/elem_8.png",
            },
            {
                "name": "Комбо-микс",
                "description": "Шаурма классическая, картофель фри и напиток на выбор. Сытный обед за отличную цену.",
                "price": Decimal("389.00"),
                "image": "/src/combo/elem_9.png",
            },
            {
                "name": "Двойной удар",
                "description": "Две шаурмы, две картошки фри и два соуса для тех, кто любит делиться или очень голоден.",
                "price": Decimal("649.00"),
                "image": "/src/combo/elem_10.png",
            },
            {
                "name": "Семейный",
                "description": "Пицца 30 см, 4 хот-дога, 2 картошки фри, 4 напитка. Идеально для семейного вечера.",
                "price": Decimal("1799.00"),
                "image": "/src/combo/elem_11.png",
            },
            {
                "name": "Мега-комбо",
                "description": "Самое большое комбо: пицца, шаурма, хот-дог, закуски, картошка и напитки на 4 персоны.",
                "price": Decimal("2899.00"),
                "image": "/src/combo/elem_12.png",
            },
        ]
        
        print(f"\n📦 Создаем {len(combo_products)} товаров Комбо...")
        success = 0
        
        for i, product_data in enumerate(combo_products, 1):
            try:
                product = await prod_service.create_product(ProductCreate(
                    category_id=combo_category.id,
                    is_available=True,
                    is_active=True,
                    **product_data
                ))
                print(f"   ✅ {i}. {product.name} - {product.price}₽")
                success += 1
            except Exception as e:
                print(f"   ❌ {i}. {product_data['name']}: {e}")
        
        print(f"\n{'='*50}")
        print(f"✅ Успешно создано: {success}/{len(combo_products)}")
        print(f"📁 Категория: Комбо")
        print(f"🔗 http://localhost:8000/category/combo")
        print(f"{'='*50}")
    
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_combo())