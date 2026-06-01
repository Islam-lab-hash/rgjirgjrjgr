"""SQLite storage helpers."""
from typing import Optional

import aiosqlite

from config import DB_PATH


DEFAULT_CATEGORIES = [
    "Халаты",
    "Пеньюары",
    "Сорочки",
    "Комплекты",
    "Наборы трусиков",
    "Свадебное белье",
    "Корсетные изделия",
    "Чулки и колготки",
    "Купальники",
    "Аксессуары",
    "Акции",
]

DEFAULT_SETTINGS = {
    "pay_card": "0000 0000 0000 0000",
    "pay_holder": "ИВАНОВА А. А.",
    "pay_bank": "Сбербанк",
    "start_text": "Натуральный шелк Premium Turkey",
    "shop_name": "LINGERIE BOUTIQUE",
    "shop_addresses": "📍 Grozny Mall, г. Грозный",
    "shop_schedule": "Ежедневно 10:00-22:00",
    "delivery_info": "🚚 Доставка по всей России",
    "payment_info": "💳 Оплата при получении",
    "exchange_info": "🔁 Обмен в течение 14 дней",
    "instagram_url": "https://instagram.com/",
    "operator_username": "@manager",
    "menu_catalog": "Каталог",
    "menu_selector": "Подбор",
    "menu_cart": "Корзина",
    "menu_info": "Информация",
    "image_start": "",
    "image_catalog": "",
    "image_selector": "",
    "image_cart": "",
    "image_info": "",
}

PRODUCT_FIELDS = {
    "category_id",
    "name",
    "price",
    "sizes",
    "colors",
    "material",
    "country",
    "description",
    "photo_file_id",
    "in_stock",
}


async def init_db():
    """Create tables and seed default categories/settings."""
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.executescript(
            """
            PRAGMA foreign_keys = ON;

            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                position INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                price REAL NOT NULL DEFAULT 0,
                sizes TEXT DEFAULT '',
                colors TEXT DEFAULT '',
                material TEXT DEFAULT '',
                country TEXT DEFAULT '',
                description TEXT DEFAULT '',
                photo_file_id TEXT DEFAULT '',
                in_stock INTEGER DEFAULT 1,
                FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS carts (
                user_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                qty INTEGER DEFAULT 1,
                PRIMARY KEY (user_id, product_id)
            );

            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT,
                phone TEXT,
                city TEXT,
                delivery TEXT,
                comment TEXT,
                items TEXT,
                total REAL,
                status TEXT DEFAULT 'new',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            );

            CREATE TABLE IF NOT EXISTS admins (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                added_by INTEGER,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        )

        cur = await conn.execute("SELECT COUNT(*) FROM categories")
        if (await cur.fetchone())[0] == 0:
            for i, name in enumerate(DEFAULT_CATEGORIES):
                await conn.execute(
                    "INSERT INTO categories (name, position) VALUES (?, ?)",
                    (name, i),
                )

        for key, value in DEFAULT_SETTINGS.items():
            await conn.execute(
                "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
                (key, value),
            )

        await conn.commit()


# Users
async def upsert_user(user_id: int, username: Optional[str], first_name: Optional[str]):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            """
            INSERT INTO users (user_id, username, first_name)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET username=?, first_name=?
            """,
            (user_id, username, first_name, username, first_name),
        )
        await conn.commit()


async def list_users():
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        cur = await conn.execute("SELECT user_id, username, first_name FROM users")
        return await cur.fetchall()


# Categories
async def list_categories():
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        cur = await conn.execute("SELECT id, name, position FROM categories ORDER BY position, id")
        return await cur.fetchall()


async def get_category(cat_id: int):
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        cur = await conn.execute("SELECT id, name, position FROM categories WHERE id=?", (cat_id,))
        return await cur.fetchone()


async def add_category(name: str):
    async with aiosqlite.connect(DB_PATH) as conn:
        cur = await conn.execute("SELECT COALESCE(MAX(position), -1) FROM categories")
        pos = (await cur.fetchone())[0] + 1
        await conn.execute("INSERT INTO categories (name, position) VALUES (?, ?)", (name.strip(), pos))
        await conn.commit()


async def update_category(cat_id: int, name: str):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute("UPDATE categories SET name=? WHERE id=?", (name.strip(), cat_id))
        await conn.commit()


async def delete_category(cat_id: int):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute("DELETE FROM categories WHERE id=?", (cat_id,))
        await conn.commit()


# Products
async def list_products(cat_id: int | None = None, include_hidden: bool = True):
    query = """
        SELECT id, category_id, name, price, sizes, colors, material, country,
               description, photo_file_id, in_stock
        FROM products
    """
    params: tuple = ()
    where = []
    if cat_id is not None:
        where.append("category_id=?")
        params = (cat_id,)
    if not include_hidden:
        where.append("in_stock=1")
    if where:
        query += " WHERE " + " AND ".join(where)
    query += " ORDER BY id DESC"

    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        cur = await conn.execute(query, params)
        return await cur.fetchall()


async def get_product(prod_id: int):
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        cur = await conn.execute(
            """
            SELECT id, category_id, name, price, sizes, colors, material, country,
                   description, photo_file_id, in_stock
            FROM products WHERE id=?
            """,
            (prod_id,),
        )
        return await cur.fetchone()


async def add_product(data: dict):
    async with aiosqlite.connect(DB_PATH) as conn:
        cur = await conn.execute(
            """
            INSERT INTO products (
                category_id, name, price, sizes, colors, material, country,
                description, photo_file_id, in_stock
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["category_id"],
                data["name"].strip(),
                float(data.get("price", 0) or 0),
                data.get("sizes", ""),
                data.get("colors", ""),
                data.get("material", ""),
                data.get("country", ""),
                data.get("description", ""),
                data.get("photo_file_id", ""),
                int(data.get("in_stock", 1)),
            ),
        )
        await conn.commit()
        return cur.lastrowid


async def update_product(prod_id: int, **fields):
    valid_fields = {k: v for k, v in fields.items() if k in PRODUCT_FIELDS}
    if not valid_fields:
        return

    sets = []
    vals = []
    for key, value in valid_fields.items():
        sets.append(f"{key}=?")
        vals.append(value)
    vals.append(prod_id)

    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(f"UPDATE products SET {', '.join(sets)} WHERE id=?", vals)
        await conn.commit()


async def delete_product(prod_id: int):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute("DELETE FROM products WHERE id=?", (prod_id,))
        await conn.commit()


async def delete_all_products():
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute("DELETE FROM carts")
        await conn.execute("DELETE FROM products")
        await conn.commit()


# Cart
async def get_cart(user_id: int):
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        cur = await conn.execute(
            """
            SELECT p.id, p.name, p.price, p.photo_file_id, c.qty
            FROM carts c
            JOIN products p ON c.product_id = p.id
            WHERE c.user_id=?
            """,
            (user_id,),
        )
        return await cur.fetchall()


async def add_to_cart(user_id: int, prod_id: int, qty: int = 1):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            """
            INSERT INTO carts (user_id, product_id, qty) VALUES (?, ?, ?)
            ON CONFLICT(user_id, product_id) DO UPDATE SET qty=qty+?
            """,
            (user_id, prod_id, qty, qty),
        )
        await conn.commit()


async def remove_from_cart(user_id: int, prod_id: int):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute("DELETE FROM carts WHERE user_id=? AND product_id=?", (user_id, prod_id))
        await conn.commit()


async def clear_cart(user_id: int):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute("DELETE FROM carts WHERE user_id=?", (user_id,))
        await conn.commit()


# Orders
async def create_order(data: dict):
    async with aiosqlite.connect(DB_PATH) as conn:
        cur = await conn.execute(
            """
            INSERT INTO orders (user_id, name, phone, city, delivery, comment, items, total, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'new')
            """,
            (
                data["user_id"],
                data.get("name"),
                data.get("phone"),
                data.get("city"),
                data.get("delivery"),
                data.get("comment", ""),
                data["items"],
                data["total"],
            ),
        )
        await conn.commit()
        return cur.lastrowid


async def get_order(order_id: int):
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        cur = await conn.execute("SELECT * FROM orders WHERE id=?", (order_id,))
        return await cur.fetchone()


async def list_orders(status: str | None = None):
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        if status:
            cur = await conn.execute("SELECT * FROM orders WHERE status=? ORDER BY id DESC", (status,))
        else:
            cur = await conn.execute("SELECT * FROM orders ORDER BY id DESC")
        return await cur.fetchall()


async def update_order_status(order_id: int, status: str):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute("UPDATE orders SET status=? WHERE id=?", (status, order_id))
        await conn.commit()


# Settings
async def get_text(key: str, default: str = ""):
    async with aiosqlite.connect(DB_PATH) as conn:
        cur = await conn.execute("SELECT value FROM settings WHERE key=?", (key,))
        row = await cur.fetchone()
        return row[0] if row else default


async def set_text(key: str, value: str):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
        await conn.commit()


async def get_payment_info():
    return {
        "card": await get_text("pay_card"),
        "holder": await get_text("pay_holder"),
        "bank": await get_text("pay_bank"),
    }


get_setting = get_text
set_setting = set_text


# Admins
async def is_db_admin(user_id: int):
    async with aiosqlite.connect(DB_PATH) as conn:
        cur = await conn.execute("SELECT 1 FROM admins WHERE user_id=?", (user_id,))
        return await cur.fetchone() is not None


async def add_admin(user_id: int, username: str | None = None, added_by: int | None = None):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            "INSERT OR REPLACE INTO admins (user_id, username, added_by) VALUES (?, ?, ?)",
            (user_id, username, added_by),
        )
        await conn.commit()


async def remove_admin(user_id: int):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute("DELETE FROM admins WHERE user_id=?", (user_id,))
        await conn.commit()


async def list_admins():
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        cur = await conn.execute("SELECT user_id, username FROM admins")
        return await cur.fetchall()


# Stats
async def get_stats():
    async with aiosqlite.connect(DB_PATH) as conn:
        stats = {}
        for table in ["users", "products", "categories", "orders"]:
            cur = await conn.execute(f"SELECT COUNT(*) FROM {table}")
            stats[table] = (await cur.fetchone())[0]
        return stats
