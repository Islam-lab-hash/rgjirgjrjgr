"""Import products extracted from the ZIP archives."""
import asyncio
from pathlib import Path

import database as db

ROOT = Path(__file__).resolve().parent
PRODUCTS_DIR = ROOT / "assets" / "products"


PRODUCTS = [
    {
        "category": "Бюсты",
        "file": "Бюсты/Бюсты_01.jpg",
        "name": "Черный кружевной бюст Classic",
        "price": 2700,
        "sizes": "75B, 75C, 80B, 80C, 85B",
        "colors": "черный",
        "material": "кружево, микрофибра",
        "description": "Черный бюст с фактурным кружевом и аккуратной посадкой. Базовая модель для повседневных и вечерних образов.",
    },
    {
        "category": "Бюсты",
        "file": "Бюсты/Бюсты_02.jpg",
        "name": "Голубой кружевной бюст Sky",
        "price": 2800,
        "sizes": "75B, 75C, 80B, 80C, 85B",
        "colors": "голубой",
        "material": "кружево, микрофибра",
        "description": "Нежный голубой бюст с кружевной чашкой. Легкий оттенок и мягкая форма для деликатного женственного образа.",
    },
    {
        "category": "Бюсты",
        "file": "Бюсты/Бюсты_03.jpg",
        "name": "Белый кружевной бюст Pearl",
        "price": 2800,
        "sizes": "75B, 75C, 80B, 80C, 85B",
        "colors": "белый",
        "material": "кружево, микрофибра",
        "description": "Белый кружевной бюст в классическом исполнении. Подходит под светлую одежду и романтичные комплекты.",
    },
    {
        "category": "Бюсты",
        "file": "Бюсты/Бюсты_04.jpg",
        "name": "Бежевый гладкий бюст Nude",
        "price": 2500,
        "sizes": "75B, 75C, 80B, 80C, 85B",
        "colors": "бежевый",
        "material": "гладкая микрофибра",
        "description": "Гладкий бежевый бюст без лишнего декора. Незаметный под одеждой и удобный для ежедневной носки.",
    },
    {
        "category": "Бюсты",
        "file": "Бюсты/Бюсты_05.jpg",
        "name": "Молочный кружевной бюст Lace",
        "price": 2900,
        "sizes": "75B, 75C, 80B, 80C, 85B",
        "colors": "молочный",
        "material": "кружево, микрофибра",
        "description": "Молочный бюст с кружевной отделкой и изящными деталями по бокам. Мягкий акцент для светлых образов.",
    },
    {
        "category": "Бюсты",
        "file": "Бюсты/Бюсты_06.png",
        "name": "Набор базовых бюстов Trio",
        "price": 6900,
        "sizes": "75B, 75C, 80B, 80C, 85B",
        "colors": "красный, белый, черный",
        "material": "микрофибра",
        "description": "Набор из трех базовых бюстов в универсальных цветах. Удобный вариант для обновления бельевого гардероба.",
    },
    {
        "category": "Комплекты",
        "file": "Комплекты/Комплекты_01.jpg",
        "name": "Синий кружевной комплект Azure",
        "price": 4200,
        "sizes": "S, M, L",
        "colors": "синий",
        "material": "кружево, микрофибра",
        "description": "Комплект бюст и трусики в насыщенном синем цвете. Кружевные детали делают модель выразительной и аккуратной.",
    },
    {
        "category": "Комплекты",
        "file": "Комплекты/Комплекты_02.png",
        "name": "Красный комплект Passion",
        "price": 5500,
        "sizes": "S, M, L",
        "colors": "красный",
        "material": "кружево, эластичная сетка",
        "description": "Эффектный красный комплект с декоративными линиями и выразительной посадкой. Подойдет для особого случая.",
    },
    {
        "category": "Комплекты",
        "file": "Комплекты/Комплекты_03.png",
        "name": "Изумрудный комплект Emerald",
        "price": 6500,
        "sizes": "S, M, L",
        "colors": "изумрудный, серо-зеленый",
        "material": "кружево, атлас",
        "description": "Комплект белья с легким халатом в благородном оттенке. Готовый образ с мягким блеском и кружевными акцентами.",
    },
    {
        "category": "Пеньюары",
        "file": "Пеньюары/Пеньюар_01.jpg",
        "name": "Черный атласный пеньюар Noir",
        "price": 6000,
        "sizes": "S, M, L",
        "colors": "черный",
        "material": "атлас, кружево",
        "description": "Черный пеньюар с глубоким разрезом и тонкими бретелями. Элегантная модель для вечернего образа.",
    },
    {
        "category": "Пижамы",
        "file": "Пижамы/Пижама_01.jpg",
        "name": "Красный брючный комплект Ruby",
        "price": 5200,
        "sizes": "S, M, L, XL",
        "colors": "красный",
        "material": "шелковистая ткань",
        "description": "Красный комплект свободного кроя с рубашкой и брюками. Комфортная посадка и яркий премиальный оттенок.",
    },
    {
        "category": "Пижамы",
        "file": "Пижамы/Пижама_02.png",
        "name": "Фиолетовый комплект Viola",
        "price": 4900,
        "sizes": "S, M, L",
        "colors": "фиолетовый",
        "material": "шелковистая ткань",
        "description": "Комплект с открытыми плечами и широкими брюками. Легкая модель для дома, отдыха и красивых образов.",
    },
    {
        "category": "Пижамы",
        "file": "Пижамы/Пижама_03.png",
        "name": "Бордовый комплект Bordeaux",
        "price": 4900,
        "sizes": "S, M, L",
        "colors": "бордовый",
        "material": "шелковистая ткань",
        "description": "Бордовый комплект с мягкой линией плеч и свободными брюками. Насыщенный цвет делает образ более выразительным.",
    },
    {
        "category": "Пижамы",
        "file": "Пижамы/Пижама_04.png",
        "name": "Белый комплект топ и брюки Milk",
        "price": 4500,
        "sizes": "S, M, L",
        "colors": "белый",
        "material": "легкая ткань",
        "description": "Белый летний комплект с укороченным топом и брюками. Свежий и воздушный вариант для теплого сезона.",
    },
    {
        "category": "Пижамы",
        "file": "Пижамы/Пижама_05.png",
        "name": "Лавандовый комплект Lavender",
        "price": 4900,
        "sizes": "S, M, L",
        "colors": "лавандовый",
        "material": "шелковистая ткань",
        "description": "Лавандовый комплект с открытыми плечами. Мягкий оттенок и свободный крой для расслабленного женственного образа.",
    },
    {
        "category": "Пижамы",
        "file": "Пижамы/Пижама_06.png",
        "name": "Комплект цвета шампань Satin",
        "price": 5200,
        "sizes": "S, M, L",
        "colors": "шампань",
        "material": "атласная ткань",
        "description": "Атласный комплект цвета шампань с мягким блеском. Элегантная модель для дома и красивых вечерних фото.",
    },
    {
        "category": "Халаты",
        "file": "Халаты/Халат_01.jpg",
        "name": "Молочный длинный халат Lace",
        "price": 6500,
        "sizes": "S, M, L",
        "colors": "молочный",
        "material": "атлас, кружево",
        "description": "Длинный молочный халат с кружевными деталями и поясом. Нежный образ с легкой прозрачностью и мягким блеском.",
    },
    {
        "category": "Халаты",
        "file": "Халаты/Халат_02.jpg",
        "name": "Белый шелковистый халат Pearl",
        "price": 5200,
        "sizes": "S, M, L, XL",
        "colors": "белый",
        "material": "шелковистая ткань",
        "description": "Белый халат свободного кроя с поясом. Универсальная модель для дома, сборов невесты и подарка.",
    },
    {
        "category": "Халаты",
        "file": "Халаты/Халат_03.jpg",
        "name": "Черный шелковистый халат Noir",
        "price": 5200,
        "sizes": "S, M, L, XL",
        "colors": "черный",
        "material": "шелковистая ткань",
        "description": "Черный халат с поясом и лаконичным кроем. Базовая элегантная модель с мягким струящимся силуэтом.",
    },
    {
        "category": "Халаты",
        "file": "Халаты/Халат_04.jpg",
        "name": "Черный халат с кружевом Night",
        "price": 5600,
        "sizes": "S, M, L, XL",
        "colors": "черный",
        "material": "шелковистая ткань, кружево",
        "description": "Черный халат с кружевной отделкой на рукавах и подоле. Более нарядный вариант классической модели.",
    },
    {
        "category": "Халаты",
        "file": "Халаты/Халат_05.jpg",
        "name": "Бордовый шелковистый халат Wine",
        "price": 5600,
        "sizes": "S, M, L, XL",
        "colors": "бордовый",
        "material": "шелковистая ткань",
        "description": "Бордовый халат с поясом в глубоким оттенке вина. Выглядит дорого и хорошо подходит для подарка.",
    },
    {
        "category": "Халаты",
        "file": "Халаты/Халат_06.jpg",
        "name": "Голубой халат с кружевом Sky",
        "price": 5800,
        "sizes": "S, M, L, XL",
        "colors": "голубой",
        "material": "шелковистая ткань, кружево",
        "description": "Голубой халат с кружевными рукавами и поясом. Светлая нежная модель с воздушным настроением.",
    },
    {
        "category": "Халаты",
        "file": "Халаты/Халат_07.jpg",
        "name": "Графитовый шелковистый халат Graphite",
        "price": 5400,
        "sizes": "S, M, L, XL",
        "colors": "графитовый",
        "material": "шелковистая ткань",
        "description": "Халат графитового оттенка с поясом и спокойным силуэтом. Сдержанный цвет для повседневной элегантности.",
    },
]


async def category_id_by_name(name: str) -> int:
    categories = await db.list_categories()
    for category in categories:
        if category["name"] == name:
            return category["id"]

    await db.add_category(name)
    categories = await db.list_categories()
    for category in categories:
        if category["name"] == name:
            return category["id"]

    raise RuntimeError(f"Category was not created: {name}")


async def main():
    await db.init_db()
    await db.delete_all_products()

    added = 0
    category_cache: dict[str, int] = {}

    for product in PRODUCTS:
        category = product["category"]
        if category not in category_cache:
            category_cache[category] = await category_id_by_name(category)

        relative_photo_path = Path("assets") / "products" / product["file"]
        photo_path = ROOT / relative_photo_path
        if not photo_path.exists():
            raise FileNotFoundError(photo_path)

        await db.add_product(
            {
                "category_id": category_cache[category],
                "name": product["name"],
                "price": product["price"],
                "sizes": product["sizes"],
                "colors": product["colors"],
                "material": product["material"],
                "country": "Турция",
                "description": product["description"],
                "photo_file_id": relative_photo_path.as_posix(),
                "in_stock": 1,
            }
        )
        added += 1

    print(f"Добавлено товаров: {added}")


if __name__ == "__main__":
    asyncio.run(main())
