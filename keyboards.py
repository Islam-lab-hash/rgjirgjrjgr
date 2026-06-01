"""Bot keyboards."""
from aiogram.types import InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


# User
async def main_menu():
    from database import get_text

    builder = InlineKeyboardBuilder()
    builder.button(text=f"📋 {await get_text('menu_catalog', 'Каталог')}", callback_data="catalog")
    builder.button(text=f"🔎 {await get_text('menu_selector', 'Подбор')}", callback_data="selector")
    builder.button(text=f"🛒 {await get_text('menu_cart', 'Корзина')}", callback_data="cart")
    builder.button(text=f"ℹ️ {await get_text('menu_info', 'Информация')}", callback_data="info")
    builder.adjust(2, 2)
    return builder.as_markup()


def categories_kb(categories):
    builder = InlineKeyboardBuilder()
    for category in categories:
        builder.button(text=category["name"], callback_data=f"cat:{category['id']}")
    builder.button(text="← В меню", callback_data="main")
    builder.adjust(2)
    return builder.as_markup()


def products_kb(products, cat_id):
    builder = InlineKeyboardBuilder()
    for product in products:
        builder.button(
            text=f"{product['name']} - {int(product['price'])}₽",
            callback_data=f"prod:{product['id']}",
        )
    builder.button(text="← Назад", callback_data="catalog")
    builder.adjust(1)
    return builder.as_markup()


def product_kb(prod_id, cat_id):
    builder = InlineKeyboardBuilder()
    builder.button(text="🛒 В корзину", callback_data=f"add:{prod_id}")
    builder.button(text="← Назад", callback_data=f"cat:{cat_id}")
    builder.adjust(1)
    return builder.as_markup()


def cart_kb(items):
    builder = InlineKeyboardBuilder()
    for item in items:
        builder.button(text=f"✕ {item['name']}", callback_data=f"rm:{item['id']}")
    if items:
        builder.button(text="✅ Оформить заказ", callback_data="checkout")
        builder.button(text="🗑 Очистить", callback_data="clear_cart")
    builder.button(text="← В меню", callback_data="main")
    builder.adjust(1)
    return builder.as_markup()


def info_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="📍 Адреса", callback_data="info:addr")
    builder.button(text="🚚 Доставка", callback_data="info:delivery")
    builder.button(text="💳 Оплата", callback_data="info:pay")
    builder.button(text="🔁 Обмен", callback_data="info:return")
    builder.button(text="📷 Instagram", callback_data="info:inst")
    builder.button(text="← В меню", callback_data="main")
    builder.adjust(2, 2, 1, 1)
    return builder.as_markup()


def selector_kb(operator_username: str = ""):
    builder = InlineKeyboardBuilder()
    if operator_username:
        username = operator_username.strip().lstrip("@")
        if username:
            builder.button(text="💬 Написать оператору", url=f"https://t.me/{username}")
    builder.button(text="← В меню", callback_data="main")
    builder.adjust(1)
    return builder.as_markup()


def back_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="← В меню", callback_data="main")
    return builder.as_markup()


def phone_kb():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Отправить номер", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


# Admin
def admin_menu():
    builder = InlineKeyboardBuilder()
    builder.button(text="📦 Товары", callback_data="adm:prods")
    builder.button(text="🗂 Категории", callback_data="adm:cats")
    builder.button(text="🛒 Заказы", callback_data="adm:orders")
    builder.button(text="📝 Тексты", callback_data="adm:texts")
    builder.button(text="🖼 Картинки", callback_data="adm:images")
    builder.button(text="💳 Реквизиты", callback_data="adm:pay")
    builder.button(text="🔧 Меню", callback_data="adm:menuedit")
    builder.button(text="👥 Админы", callback_data="adm:admins")
    builder.button(text="📊 Статистика", callback_data="adm:stats")
    builder.button(text="📣 Рассылка", callback_data="adm:broadcast")
    builder.button(text="← Закрыть", callback_data="main")
    builder.adjust(2, 2, 2, 2, 2, 1)
    return builder.as_markup()


TEXT_FIELDS = [
    ("start_text", "✨ Текст /start"),
    ("shop_name", "🏷 Название"),
    ("shop_addresses", "📍 Адреса"),
    ("shop_schedule", "🕐 График"),
    ("delivery_info", "🚚 Доставка"),
    ("payment_info", "💳 Оплата"),
    ("exchange_info", "🔁 Обмен"),
    ("instagram_url", "📷 Instagram"),
    ("operator_username", "💬 Оператор"),
]

PAY_FIELDS = [
    ("pay_card", "Номер карты"),
    ("pay_holder", "Получатель"),
    ("pay_bank", "Банк"),
]

IMAGE_FIELDS = [
    ("start", "Старт"),
    ("catalog", "Каталог"),
    ("selector", "Подбор"),
    ("cart", "Корзина"),
    ("info", "Информация"),
]

PRODUCT_EDIT_FIELDS = [
    ("name", "Название"),
    ("price", "Цена"),
    ("sizes", "Размеры"),
    ("colors", "Цвета"),
    ("material", "Материал"),
    ("country", "Страна"),
    ("description", "Описание"),
]


def admin_texts_kb():
    builder = InlineKeyboardBuilder()
    for key, label in TEXT_FIELDS:
        builder.button(text=label, callback_data=f"adm:edtxt:{key}")
    builder.button(text="← Назад", callback_data="adm:main")
    builder.adjust(1)
    return builder.as_markup()


def admin_pay_kb():
    builder = InlineKeyboardBuilder()
    for key, label in PAY_FIELDS:
        builder.button(text=label, callback_data=f"adm:edtxt:{key}")
    builder.button(text="← Назад", callback_data="adm:main")
    builder.adjust(1)
    return builder.as_markup()


def admin_images_kb():
    builder = InlineKeyboardBuilder()
    for key, label in IMAGE_FIELDS:
        builder.button(text=label, callback_data=f"adm:edimg:{key}")
    builder.button(text="← Назад", callback_data="adm:main")
    builder.adjust(1)
    return builder.as_markup()


def admin_menu_edit_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="📋 Каталог", callback_data="adm:edmenu:catalog")
    builder.button(text="🔎 Подбор", callback_data="adm:edmenu:selector")
    builder.button(text="🛒 Корзина", callback_data="adm:edmenu:cart")
    builder.button(text="ℹ️ Информация", callback_data="adm:edmenu:info")
    builder.button(text="← Назад", callback_data="adm:main")
    builder.adjust(1)
    return builder.as_markup()


def admin_categories_kb(categories):
    builder = InlineKeyboardBuilder()
    for category in categories:
        builder.button(text=category["name"], callback_data=f"adm:cat:{category['id']}")
    builder.button(text="➕ Добавить категорию", callback_data="adm:addcat")
    builder.button(text="← Назад", callback_data="adm:main")
    builder.adjust(1)
    return builder.as_markup()


def admin_category_kb(cat_id):
    builder = InlineKeyboardBuilder()
    builder.button(text="✏️ Переименовать", callback_data=f"adm:editcat:{cat_id}")
    builder.button(text="🗑 Удалить", callback_data=f"adm:delcat:{cat_id}")
    builder.button(text="📦 Товары категории", callback_data=f"adm:prodcat:{cat_id}")
    builder.button(text="← Категории", callback_data="adm:cats")
    builder.adjust(1)
    return builder.as_markup()


def admin_products_root_kb(categories):
    builder = InlineKeyboardBuilder()
    builder.button(text="➕ Добавить товар", callback_data="adm:newprod")
    builder.button(text="🧹 Удалить все товары", callback_data="adm:clearprods:ask")
    for category in categories:
        builder.button(text=category["name"], callback_data=f"adm:prodcat:{category['id']}")
    builder.button(text="← Назад", callback_data="adm:main")
    builder.adjust(1)
    return builder.as_markup()


def admin_pick_cat_kb(categories, prefix="adm:newprodcat"):
    builder = InlineKeyboardBuilder()
    for category in categories:
        builder.button(text=category["name"], callback_data=f"{prefix}:{category['id']}")
    builder.button(text="← Отмена", callback_data="adm:prods")
    builder.adjust(2)
    return builder.as_markup()


def admin_products_kb(products, cat_id):
    builder = InlineKeyboardBuilder()
    builder.button(text="➕ Добавить товар сюда", callback_data=f"adm:newprodcat:{cat_id}")
    for product in products:
        status = "" if product["in_stock"] else " (скрыт)"
        builder.button(text=f"{product['name']}{status}", callback_data=f"adm:prod:{product['id']}")
    builder.button(text="← Товары", callback_data="adm:prods")
    builder.adjust(1)
    return builder.as_markup()


def admin_product_kb(product):
    builder = InlineKeyboardBuilder()
    for field, label in PRODUCT_EDIT_FIELDS:
        builder.button(text=f"✏️ {label}", callback_data=f"adm:editprod:{product['id']}:{field}")
    builder.button(text="🖼 Фото", callback_data=f"adm:editprodphoto:{product['id']}")
    builder.button(text="🗂 Категория", callback_data=f"adm:editprodcat:{product['id']}")
    builder.button(
        text="🙈 Скрыть" if product["in_stock"] else "👁 Показать",
        callback_data=f"adm:toggleprod:{product['id']}",
    )
    builder.button(text="🗑 Удалить", callback_data=f"adm:delprodask:{product['id']}")
    builder.button(text="← К товарам", callback_data=f"adm:prodcat:{product['category_id']}")
    builder.adjust(2, 2, 2, 1, 1, 1)
    return builder.as_markup()


def admin_confirm_delete_product_kb(prod_id):
    builder = InlineKeyboardBuilder()
    builder.button(text="Да, удалить", callback_data=f"adm:delprod:{prod_id}")
    builder.button(text="Отмена", callback_data=f"adm:prod:{prod_id}")
    builder.adjust(1)
    return builder.as_markup()


def admin_confirm_clear_products_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="Да, удалить все товары", callback_data="adm:clearprods:yes")
    builder.button(text="Отмена", callback_data="adm:prods")
    builder.adjust(1)
    return builder.as_markup()


def admin_orders_kb(orders):
    builder = InlineKeyboardBuilder()
    for order in orders:
        builder.button(text=f"#{order['id']} - {order['name'] or 'без имени'}", callback_data=f"adm:ord:{order['id']}")
    builder.button(text="← Назад", callback_data="adm:main")
    builder.adjust(1)
    return builder.as_markup()


def admin_order_kb(order_id):
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Подтвердить", callback_data=f"adm:ordok:{order_id}")
    builder.button(text="❌ Отменить", callback_data=f"adm:ordno:{order_id}")
    builder.button(text="← Назад", callback_data="adm:orders")
    builder.adjust(1)
    return builder.as_markup()


def admin_admins_kb(admins):
    builder = InlineKeyboardBuilder()
    for admin in admins:
        label = admin["username"] or admin["user_id"]
        builder.button(text=f"🗑 {label}", callback_data=f"adm:deladm:{admin['user_id']}")
    builder.button(text="➕ Добавить", callback_data="adm:addadm")
    builder.button(text="← Назад", callback_data="adm:main")
    builder.adjust(1)
    return builder.as_markup()


def simple_admin_back_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="← В админ-панель", callback_data="adm:main")
    return builder.as_markup()
