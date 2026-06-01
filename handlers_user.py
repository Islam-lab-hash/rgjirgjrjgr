"""User-facing bot handlers."""
import os

from aiogram import Bot, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile, Message, ReplyKeyboardRemove

import database as db
import keyboards as kb
from config import ADMIN_IDS
from states import OrderForm

router = Router()
ASSETS = os.path.join(os.path.dirname(__file__), "assets")


def _local_asset(name: str) -> str:
    return os.path.join(ASSETS, name)


async def _image_source(key: str):
    configured = await db.get_text(f"image_{key}", "")
    if configured:
        return FSInputFile(configured) if os.path.exists(configured) else configured

    path = _local_asset(f"{key}.png")
    if os.path.exists(path):
        return FSInputFile(path)

    return None


def _product_photo_source(value: str):
    if not value:
        return None
    if os.path.exists(value):
        return FSInputFile(value)

    local_path = os.path.join(os.path.dirname(__file__), value)
    return FSInputFile(local_path) if os.path.exists(local_path) else value


async def _replace_callback_message(call: CallbackQuery, text: str, reply_markup=None, image_key: str | None = None):
    photo = await _image_source(image_key) if image_key else None

    if photo:
        try:
            await call.message.delete()
        except Exception:
            pass
        await call.message.answer_photo(photo=photo, caption=text, reply_markup=reply_markup)
        await call.answer()
        return

    try:
        await call.message.edit_text(text, reply_markup=reply_markup)
    except Exception:
        await call.message.answer(text, reply_markup=reply_markup)
    await call.answer()


# /start
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await db.upsert_user(message.from_user.id, message.from_user.username, message.from_user.first_name)

    text = await db.get_text("start_text", "Натуральный шелк Premium Turkey")
    photo = await _image_source("start")
    markup = await kb.main_menu()

    if photo:
        await message.answer_photo(photo=photo, caption=f"<b>{text}</b>", reply_markup=markup)
    else:
        await message.answer(f"<b>{text}</b>", reply_markup=markup)


@router.message(Command("myid"))
async def cmd_myid(message: Message):
    await message.answer(f"🆔 Ваш ID: <code>{message.from_user.id}</code>")


@router.callback_query(F.data == "main")
async def to_main(call: CallbackQuery, state: FSMContext):
    await state.clear()
    text = await db.get_text("start_text", "Натуральный шелк Premium Turkey")
    await _replace_callback_message(call, f"<b>{text}</b>", await kb.main_menu(), "start")


# Catalog
@router.callback_query(F.data == "catalog")
async def show_catalog(call: CallbackQuery):
    categories = await db.list_categories()
    if not categories:
        await call.answer("Каталог пуст", show_alert=True)
        return

    text = "📋 <b>Каталог</b>\nВыберите категорию:"
    await _replace_callback_message(call, text, kb.categories_kb(categories), "catalog")


@router.callback_query(F.data.startswith("cat:"))
async def show_category(call: CallbackQuery):
    cat_id = int(call.data.split(":")[1])
    products = await db.list_products(cat_id, include_hidden=False)
    category = await db.get_category(cat_id)
    if not category:
        await call.answer("Категория не найдена", show_alert=True)
        return

    if not products:
        text = f"<b>{category['name']}</b>\n\nВ этой категории пока нет товаров."
        await _replace_callback_message(call, text, kb.categories_kb(await db.list_categories()))
        return

    text = f"<b>{category['name']}</b>\nВыберите товар:"
    await _replace_callback_message(call, text, kb.products_kb(products, cat_id))


@router.callback_query(F.data.startswith("prod:"))
async def show_product(call: CallbackQuery, bot: Bot):
    prod_id = int(call.data.split(":")[1])
    product = await db.get_product(prod_id)
    if not product or not product["in_stock"]:
        await call.answer("Товар не найден", show_alert=True)
        return

    text = f"<b>{product['name']}</b>\n💰 {int(product['price'])}₽"
    if product["sizes"]:
        text += f"\n📏 Размеры: {product['sizes']}"
    if product["colors"]:
        text += f"\n🎨 Цвета: {product['colors']}"
    if product["material"]:
        text += f"\n🧵 Материал: {product['material']}"
    if product["country"]:
        text += f"\n🌍 Страна: {product['country']}"
    if product["description"]:
        text += f"\n\n{product['description']}"

    try:
        await call.message.delete()
    except Exception:
        pass

    photo = _product_photo_source(product["photo_file_id"])
    markup = kb.product_kb(product["id"], product["category_id"])
    if photo:
        await bot.send_photo(call.from_user.id, photo=photo, caption=text, reply_markup=markup)
    else:
        await bot.send_message(call.from_user.id, text, reply_markup=markup)
    await call.answer()


# Cart
@router.callback_query(F.data.startswith("add:"))
async def add_cart(call: CallbackQuery):
    prod_id = int(call.data.split(":")[1])
    product = await db.get_product(prod_id)
    if not product or not product["in_stock"]:
        await call.answer("Товар недоступен", show_alert=True)
        return
    await db.add_to_cart(call.from_user.id, prod_id)
    await call.answer("✅ Добавлено в корзину", show_alert=True)


@router.callback_query(F.data.startswith("rm:"))
async def rm_cart(call: CallbackQuery):
    prod_id = int(call.data.split(":")[1])
    await db.remove_from_cart(call.from_user.id, prod_id)
    await show_cart(call)


@router.callback_query(F.data == "clear_cart")
async def clear_cart(call: CallbackQuery):
    await db.clear_cart(call.from_user.id)
    await show_cart(call)


@router.callback_query(F.data == "cart")
async def show_cart(call: CallbackQuery):
    items = await db.get_cart(call.from_user.id)

    if not items:
        text = "🛒 <b>Корзина пуста</b>"
    else:
        total = sum(item["price"] * item["qty"] for item in items)
        lines = ["🛒 <b>Ваша корзина</b>\n"]
        for item in items:
            lines.append(f"• {item['name']} x{item['qty']} = {int(item['price'] * item['qty'])}₽")
        lines.append(f"\n<b>Итого: {int(total)}₽</b>")
        text = "\n".join(lines)

    await _replace_callback_message(call, text, kb.cart_kb(items), "cart")


# Checkout
@router.callback_query(F.data == "checkout")
async def checkout(call: CallbackQuery, state: FSMContext):
    items = await db.get_cart(call.from_user.id)
    if not items:
        await call.answer("Корзина пуста", show_alert=True)
        return

    await state.set_state(OrderForm.name)
    await call.message.answer("Введите ваше <b>имя</b>:")
    await call.answer()


@router.message(OrderForm.name)
async def order_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(OrderForm.phone)
    await message.answer("Введите <b>телефон</b>:", reply_markup=kb.phone_kb())


@router.message(OrderForm.phone)
async def order_phone(message: Message, state: FSMContext):
    phone = message.contact.phone_number if message.contact else message.text
    await state.update_data(phone=phone)
    await state.set_state(OrderForm.comment)
    await message.answer("Комментарий к заказу (или /skip):", reply_markup=ReplyKeyboardRemove())


@router.message(OrderForm.comment, Command("skip"))
async def order_skip(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(comment="")
    await order_finish(message, state, bot)


@router.message(OrderForm.comment)
async def order_comment(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(comment=message.text)
    await order_finish(message, state, bot)


async def order_finish(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    items = await db.get_cart(message.from_user.id)
    total = sum(item["price"] * item["qty"] for item in items)
    items_text = "; ".join(f"{item['name']} x{item['qty']}" for item in items)

    order_id = await db.create_order(
        {
            "user_id": message.from_user.id,
            "name": data.get("name"),
            "phone": data.get("phone"),
            "items": items_text,
            "total": total,
            "comment": data.get("comment", ""),
        }
    )

    await db.clear_cart(message.from_user.id)
    await state.clear()

    admins = set(ADMIN_IDS)
    admins.update(admin["user_id"] for admin in await db.list_admins())
    for admin_id in admins:
        try:
            await bot.send_message(
                admin_id,
                f"🆕 <b>Заказ #{order_id}</b>\n"
                f"👤 {data.get('name')}\n"
                f"📞 {data.get('phone')}\n"
                f"💰 {int(total)}₽\n\n{items_text}",
            )
        except Exception:
            pass

    await message.answer(
        f"✅ <b>Заказ #{order_id} создан!</b>\nОжидайте подтверждения.",
        reply_markup=kb.back_kb(),
    )


# Info
@router.callback_query(F.data == "info")
async def show_info(call: CallbackQuery):
    text = "ℹ️ <b>Информация</b>"
    await _replace_callback_message(call, text, kb.info_kb(), "info")


@router.callback_query(F.data.startswith("info:"))
async def info_page(call: CallbackQuery):
    key = call.data.split(":")[1]
    texts = {
        "addr": ("shop_addresses", "📍 Адреса"),
        "delivery": ("delivery_info", "🚚 Доставка"),
        "pay": ("payment_info", "💳 Оплата"),
        "return": ("exchange_info", "🔁 Обмен"),
        "inst": ("instagram_url", "📷 Instagram"),
    }

    if key in texts:
        db_key, label = texts[key]
        value = await db.get_text(db_key)
        if key == "inst" and value.startswith("http"):
            value = f'<a href="{value}">{value}</a>'
        text = f"<b>{label}</b>\n\n{value}"
    else:
        text = "Раздел не найден"

    await _replace_callback_message(call, text, kb.back_kb())


# Selector
@router.callback_query(F.data == "selector")
async def show_selector(call: CallbackQuery):
    operator = await db.get_text("operator_username", "")
    text = "🔎 <b>Подбор товара</b>\nДля подбора напишите оператору."
    await _replace_callback_message(call, text, kb.selector_kb(operator), "selector")
