"""Legacy product seeding is disabled.

Products are now managed from the Telegram admin panel:
/admin -> Товары -> Добавить товар.
"""
import asyncio

import database as db


async def main():
    await db.init_db()
    products = await db.list_products()
    categories = await db.list_categories()
    print("Автозаполнение отключено, чтобы не вернуть старые товары.")
    print(f"Категорий: {len(categories)}")
    print(f"Товаров: {len(products)}")
    print("Добавляйте товары через /admin -> Товары.")


if __name__ == "__main__":
    asyncio.run(main())
