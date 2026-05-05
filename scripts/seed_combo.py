"""
Заполнение базы данных товарами Комбо (с slug)
"""
import asyncio
import sys
from pathlib import Path
import re

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
from app.core.config import settings
from app.services.category_service import CategoryService
from app.services.product_service import ProductService
from app.schemas.category import CategoryCreate
from app.schemas.product import ProductCreate
from decimal import Decimal


def slugify(name: str) -> str:
    """Создание slug из названия"""
    # Транслитерация
    translit = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
        'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
        'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
        'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
        ' ': '-', '_': '-'
    }
    
    name = name.lower()
    result = ''
    for char in name:
        result += translit.get(char, char)
    
    # Оставляем только буквы, цифры и дефисы
    result = re.sub(r'[^a-z0-9-]', '', result)
    # Убираем повторяющиеся дефисы
    result = re.sub(r'-+', '-', result)
    # Убираем дефисы в начале и конце
    result = result.strip('-')
    
    return result


async def seed_combo():
    """Заполняем категорию Комбо и товары"""
    
    print("🔌 Подключение к БД...")
    print(f"   URL: {settings.DATABASE_URL}")
    
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
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
                "description": "Вкусно, сытно и с душой. От нас, как от мамы, голодным не уйдёшь! Наваристый супчик, сытная роллини и сочный вок - идеально для обеда или ужина.",
                "price": Decimal("499.00"),
                "image": "/src/combo/elem_2.png",
            },
            {
                "name": "На компанию",
                "description": "Это когда вкусно всем! Две ароматные итальянские пиццы 30 см — «Пепперони» и «4 мяса», крылышки чикен фри 4 шт., чигетсы 6 шт., сочные мясные шарики классические 10 шт., сырные шарики классические — 4 шт. и с беконом — 4 шт., картошка фри — 100 г, а ещё два соуса: гриль и песто по-русски. Отличный выбор для компании из 4 человек!",
                "price": Decimal("1999.00"),
                "image": "/src/combo/elem_3.png",
            },
            {
                "name": "На Вкусе",
                "description": "Фирменный хот-дог, золотистая хрустящая картошечка и морс на выбор — брусничный или облепиховый. Любимое сочетание для отличного перекуса!",
                "price": Decimal("549.00"),
                "image": "/src/combo/elem_4.png",
            },
            {
                "name": "На Двоих",
                "description": "Для любителей паназиатской кухни! Два сочных хот-боула с митболами и хрустящая картошечка. Идеальный выбор для сытного перекуса на двоих!",
                "price": Decimal("749.00"),
                "image": "/src/combo/elem_5.png",
            },
            {
                "name": "Бизнес-ланч",
                "description": "Грильница заряжает вкусом! Теперь у нас бизнес-ланч каждый день! С 12:00 до 15:00 забегай, хватай свою вкусную энергию и продолжай день сытым и в хорошем настроении!",
                "price": Decimal("299.00"),
                "image": "/src/combo/elem_6.png",
            },
            {
                "name": "ШаурмОБЕД",
                "description": "Это обед, который заряжает - сочная шаурма по-Французски L и кола Добрый 0.5л. Обед с Грильницей — быстро, сытно и по-настоящему вкусно!",
                "price": Decimal("399.00"),
                "image": "/src/combo/elem_7.png",
            },
            {
                "name": "Сытненько",
                "description": "Горячая роллини на выбор: пепперони, сырная или с пикантными колбасками, и морс на твой вкус — брусничный или облепиховый. Идеально, чтобы поесть с удовольствием!",
                "price": Decimal("310.00"),
                "image": "/src/combo/elem_8.png",
            },
            {
                "name": "Сладкая радость",
                "description": "Согревайся со вкусом! Нежные творожные шарики со сгущёнкой и авторский зимний напиток на выбор. Грильница — когда хочется себя порадовать!",
                "price": Decimal("319.00"),
                "image": "/src/combo/elem_9.png",
            },
            {
                "name": "3 пиццы",
                "description": "Три итальянские пиццы (30 см) - Пепперони, Карбонара и Парочка. Комбо подобрано идеально, поэтому добавить или убрать что-либо не получится",
                "price": Decimal("1529.00"),
                "image": "/src/combo/elem_10.png",
            },
            {
                "name": "5 пицц",
                "description": "Пять итальянских пицц (30 см) - Пепперони, 4 Мяса, Молодежная, Жульен, Карбонара. Комбо подобрано идеально, поэтому добавить или убрать что-либо не получится",
                "price": Decimal("2699.00"),
                "image": "/src/combo/elem_11.png",
            },
            {
                "name": "7 пицц",
                "description": "Семь итальянских пицц (30 см) - Пепперони, 4 Мяса, Молодежная, Жульен, Карбонара, Добрейшая, Парочка. Комбо подобрано идеально, поэтому добавить или убрать что-либо не получится",
                "price": Decimal("3699.00"),
                "image": "/src/combo/elem_12.png",
            },
        ]
        
        print(f"\n📦 Создаем {len(combo_products)} товаров Комбо...")
        success = 0
        
        for product_data in combo_products:
            # Генерируем slug
            product_data["slug"] = slugify(product_data["name"])
            
            try:
                product = await prod_service.create_product(ProductCreate(
                    category_id=combo_category.id,
                    is_available=True,
                    is_active=True,
                    **product_data
                ))
                print(f"   ✅ {product.name} → /menu/combo/{product.slug}")
                success += 1
            except Exception as e:
                print(f"   ❌ {product_data['name']}: {e}")
        
        print(f"\n{'='*50}")
        print(f"✅ Успешно создано: {success}/{len(combo_products)}")
        print(f"📁 Категория: Комбо")
        print(f"{'='*50}")
    
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_combo())