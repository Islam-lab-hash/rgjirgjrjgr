"""Admin panel handlers."""
from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

import database as db
import keyboards as kb
from config import ADMIN_IDS
from states import AdminAddProduct, AdminEditCategory, AdminEditImage, AdminEditProduct, AdminEditText

router = Router()


async def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS or await db.is_db_admin(user_id)


def _skip_value(text: str | None) -> bool:
    return (text or "").strip().lower() in {"-", "нет", "пропустить", "skip"}


def _clean_optional(text: str | None) -> str:
    return "" if _skip_value(text) else (text or "").strip()


def _parse_price(text: str | None):
    try:
        return float((text or "").replace(",", ".").replace(" ", ""))
    except ValueError:
        return None


async def _require_admin(call: CallbackQuery) -> bool:
    if not await is_admin(call.from_user.id):
        await call.answer("⛔ Нет доступа", show_alert=True)
        return False
    return True


def _product_text(product) -> str:
    status = "показывается" if product["in_stock"] else "скрыт"
    lines = [
        f"<b>{product['name']}</b>",
        f"ID: <code>{product['id']}</code>",
        f"Цена: {int(product['price'])}₽",
        f"Статус: {status}",
        f"Размеры: {product['sizes'] or 'не указаны'}",
        f"Цвета: {product['colors'] or 'не указаны'}",
        f"Материал: {product['material'] or 'не указан'}",
        f"Страна: {product['country'] or 'не указана'}",
        "",
        product["description"] or "Описание не указано",
    ]
    return "\n".join(lines)


@router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext):
    if not await is_admin(message.from_user.id):
        await message.answer("⛔ Нет доступа")
        return
    await state.clear()
    await message.answer("<b>Админ-панель</b>", reply_markup=kb.admin_menu())


@router.callback_query(F.data == "adm:main")
async def adm_main(call: CallbackQuery, state: FSMContext):
    if not await _require_admin(call):
        return
    await state.clear()
    await call.message.edit_text("<b>Админ-панель</b>", reply_markup=kb.admin_menu())
    await call.answer()


# Products
@router.callback_query(F.data == "adm:prods")
async def adm_prods(call: CallbackQuery):
    if not await _require_admin(call):
        return
    categories = await db.list_categories()
    await call.message.edit_text(
        "📦 <b>Товары</b>\nВыберите категорию или добавьте новый товар.",
        reply_markup=kb.admin_products_root_kb(categories),
    )
    await call.answer()


@router.callback_query(F.data == "adm:newprod")
async def adm_new_product_pick_category(call: CallbackQuery):
    if not await _require_admin(call):
        return
    categories = await db.list_categories()
    await call.message.edit_text("Куда добавить товар?", reply_markup=kb.admin_pick_cat_kb(categories))
    await call.answer()


@router.callback_query(F.data.startswith("adm:prodcat:"))
async def adm_product_category(call: CallbackQuery):
    if not await _require_admin(call):
        return
    cat_id = int(call.data.split(":")[2])
    category = await db.get_category(cat_id)
    products = await db.list_products(cat_id)
    if not category:
        await call.answer("Категория не найдена", show_alert=True)
        return
    text = f"📦 <b>{category['name']}</b>\nТоваров: {len(products)}"
    await call.message.edit_text(text, reply_markup=kb.admin_products_kb(products, cat_id))
    await call.answer()


@router.callback_query(F.data.startswith("adm:newprodcat:"))
async def adm_add_product_start(call: CallbackQuery, state: FSMContext):
    if not await _require_admin(call):
        return
    cat_id = int(call.data.split(":")[2])
    category = await db.get_category(cat_id)
    if not category:
        await call.answer("Категория не найдена", show_alert=True)
        return
    await state.clear()
    await state.set_state(AdminAddProduct.name)
    await state.update_data(category_id=cat_id)
    await call.message.answer(f"Новый товар в категории <b>{category['name']}</b>.\nВведите название:")
    await call.answer()


@router.message(AdminAddProduct.name)
async def adm_add_product_name(message: Message, state: FSMContext):
    if not await is_admin(message.from_user.id):
        return
    name = (message.text or "").strip()
    if not name:
        await message.answer("Название не должно быть пустым. Введите название:")
        return
    await state.update_data(name=name)
    await state.set_state(AdminAddProduct.price)
    await message.answer("Введите цену числом:")


@router.message(AdminAddProduct.price)
async def adm_add_product_price(message: Message, state: FSMContext):
    if not await is_admin(message.from_user.id):
        return
    price = _parse_price(message.text)
    if price is None:
        await message.answer("Не понял цену. Введите число, например 4500:")
        return
    await state.update_data(price=price)
    await state.set_state(AdminAddProduct.sizes)
    await message.answer("Введите размеры или '-' чтобы оставить пустым:")


@router.message(AdminAddProduct.sizes)
async def adm_add_product_sizes(message: Message, state: FSMContext):
    if not await is_admin(message.from_user.id):
        return
    await state.update_data(sizes=_clean_optional(message.text))
    await state.set_state(AdminAddProduct.colors)
    await message.answer("Введите цвета или '-' чтобы оставить пустым:")


@router.message(AdminAddProduct.colors)
async def adm_add_product_colors(message: Message, state: FSMContext):
    if not await is_admin(message.from_user.id):
        return
    await state.update_data(colors=_clean_optional(message.text))
    await state.set_state(AdminAddProduct.material)
    await message.answer("Введите материал или '-' чтобы оставить пустым:")


@router.message(AdminAddProduct.material)
async def adm_add_product_material(message: Message, state: FSMContext):
    if not await is_admin(message.from_user.id):
        return
    await state.update_data(material=_clean_optional(message.text))
    await state.set_state(AdminAddProduct.country)
    await message.answer("Введите страну или '-' чтобы оставить пустым:")


@router.message(AdminAddProduct.country)
async def adm_add_product_country(message: Message, state: FSMContext):
    if not await is_admin(message.from_user.id):
        return
    await state.update_data(country=_clean_optional(message.text))
    await state.set_state(AdminAddProduct.description)
    await message.answer("Введите описание или '-' чтобы оставить пустым:")


@router.message(AdminAddProduct.description)
async def adm_add_product_description(message: Message, state: FSMContext):
    if not await is_admin(message.from_user.id):
        return
    await state.update_data(description=_clean_optional(message.text))
    await state.set_state(AdminAddProduct.photo)
    await message.answer("Отправьте фото товара или напишите '-' без фото:")


@router.message(AdminAddProduct.photo)
async def adm_add_product_photo(message: Message, state: FSMContext):
    if not await is_admin(message.from_user.id):
        return

    if message.photo:
        photo_file_id = message.photo[-1].file_id
    elif _skip_value(message.text):
        photo_file_id = ""
    else:
        await message.answer("Отправьте фото или '-' без фото:")
        return

    data = await state.get_data()
    data["photo_file_id"] = photo_file_id
    prod_id = await db.add_product(data)
    await state.clear()
    product = await db.get_product(prod_id)
    await message.answer("✅ Товар добавлен", reply_markup=kb.admin_product_kb(product))


@router.callback_query(F.data.startswith("adm:prod:"))
async def adm_product_detail(call: CallbackQuery):
    if not await _require_admin(call):
        return
    prod_id = int(call.data.split(":")[2])
    product = await db.get_product(prod_id)
    if not product:
        await call.answer("Товар не найден", show_alert=True)
        return
    await call.message.edit_text(_product_text(product), reply_markup=kb.admin_product_kb(product))
    await call.answer()


@router.callback_query(F.data.startswith("adm:editprod:"))
async def adm_edit_product_field(call: CallbackQuery, state: FSMContext):
    if not await _require_admin(call):
        return
    _, _, prod_id, field = call.data.split(":", 3)
    product = await db.get_product(int(prod_id))
    if not product:
        await call.answer("Товар не найден", show_alert=True)
        return
    await state.set_state(AdminEditProduct.value)
    await state.update_data(prod_id=int(prod_id), field=field)
    current = product[field]
    hint = "\nДля необязательных полей можно отправить '-' и очистить значение."
    await call.message.answer(f"Текущее значение:\n<code>{current}</code>\n\nВведите новое значение:{hint}")
    await call.answer()


@router.message(AdminEditProduct.value)
async def adm_save_product_field(message: Message, state: FSMContext):
    if not await is_admin(message.from_user.id):
        return
    data = await state.get_data()
    prod_id = data["prod_id"]
    field = data["field"]

    if field == "price":
        value = _parse_price(message.text)
        if value is None:
            await message.answer("Не понял цену. Введите число:")
            return
    elif field == "name":
        value = (message.text or "").strip()
        if not value:
            await message.answer("Название не должно быть пустым. Введите название:")
            return
    else:
        value = _clean_optional(message.text)

    await db.update_product(prod_id, **{field: value})
    await state.clear()
    product = await db.get_product(prod_id)
    await message.answer("✅ Сохранено", reply_markup=kb.admin_product_kb(product))


@router.callback_query(F.data.startswith("adm:editprodphoto:"))
async def adm_edit_product_photo_start(call: CallbackQuery, state: FSMContext):
    if not await _require_admin(call):
        return
    prod_id = int(call.data.split(":")[2])
    await state.set_state(AdminEditProduct.photo)
    await state.update_data(prod_id=prod_id)
    await call.message.answer("Отправьте новое фото или '-' чтобы удалить фото товара:")
    await call.answer()


@router.message(AdminEditProduct.photo)
async def adm_save_product_photo(message: Message, state: FSMContext):
    if not await is_admin(message.from_user.id):
        return
    data = await state.get_data()
    prod_id = data["prod_id"]
    if message.photo:
        value = message.photo[-1].file_id
    elif _skip_value(message.text):
        value = ""
    else:
        await message.answer("Отправьте фото или '-' чтобы удалить фото:")
        return
    await db.update_product(prod_id, photo_file_id=value)
    await state.clear()
    product = await db.get_product(prod_id)
    await message.answer("✅ Фото обновлено", reply_markup=kb.admin_product_kb(product))


@router.callback_query(F.data.startswith("adm:editprodcat:"))
async def adm_edit_product_category_start(call: CallbackQuery):
    if not await _require_admin(call):
        return
    prod_id = int(call.data.split(":")[2])
    categories = await db.list_categories()
    await call.message.edit_text(
        "Выберите новую категорию:",
        reply_markup=kb.admin_pick_cat_kb(categories, prefix=f"adm:setprodcat:{prod_id}"),
    )
    await call.answer()


@router.callback_query(F.data.startswith("adm:setprodcat:"))
async def adm_save_product_category(call: CallbackQuery):
    if not await _require_admin(call):
        return
    _, _, prod_id, cat_id = call.data.split(":")
    await db.update_product(int(prod_id), category_id=int(cat_id))
    product = await db.get_product(int(prod_id))
    await call.message.edit_text("✅ Категория изменена\n\n" + _product_text(product), reply_markup=kb.admin_product_kb(product))
    await call.answer()


@router.callback_query(F.data.startswith("adm:toggleprod:"))
async def adm_toggle_product(call: CallbackQuery):
    if not await _require_admin(call):
        return
    prod_id = int(call.data.split(":")[2])
    product = await db.get_product(prod_id)
    if not product:
        await call.answer("Товар не найден", show_alert=True)
        return
    await db.update_product(prod_id, in_stock=0 if product["in_stock"] else 1)
    product = await db.get_product(prod_id)
    await call.message.edit_text(_product_text(product), reply_markup=kb.admin_product_kb(product))
    await call.answer("✅ Статус изменен")


@router.callback_query(F.data.startswith("adm:delprodask:"))
async def adm_delete_product_ask(call: CallbackQuery):
    if not await _require_admin(call):
        return
    prod_id = int(call.data.split(":")[2])
    await call.message.edit_text("Удалить товар безвозвратно?", reply_markup=kb.admin_confirm_delete_product_kb(prod_id))
    await call.answer()


@router.callback_query(F.data.startswith("adm:delprod:"))
async def adm_delete_product(call: CallbackQuery):
    if not await _require_admin(call):
        return
    prod_id = int(call.data.split(":")[2])
    product = await db.get_product(prod_id)
    cat_id = product["category_id"] if product else None
    await db.delete_product(prod_id)
    if cat_id:
        category = await db.get_category(cat_id)
        products = await db.list_products(cat_id)
        text = f"📦 <b>{category['name']}</b>\nТоваров: {len(products)}" if category else "📦 <b>Товары</b>"
        await call.message.edit_text(text, reply_markup=kb.admin_products_kb(products, cat_id))
        await call.answer("✅ Удалено")
    else:
        await adm_prods(call)


@router.callback_query(F.data == "adm:clearprods:ask")
async def adm_clear_products_ask(call: CallbackQuery):
    if not await _require_admin(call):
        return
    await call.message.edit_text(
        "Удалить все товары и очистить корзины? Категории останутся.",
        reply_markup=kb.admin_confirm_clear_products_kb(),
    )
    await call.answer()


@router.callback_query(F.data == "adm:clearprods:yes")
async def adm_clear_products(call: CallbackQuery):
    if not await _require_admin(call):
        return
    await db.delete_all_products()
    categories = await db.list_categories()
    await call.message.edit_text(
        "📦 <b>Товары</b>\nВсе товары удалены. Категории сохранены.",
        reply_markup=kb.admin_products_root_kb(categories),
    )
    await call.answer("✅ Все товары удалены")


# Categories
@router.callback_query(F.data == "adm:cats")
async def adm_categories(call: CallbackQuery):
    if not await _require_admin(call):
        return
    categories = await db.list_categories()
    await call.message.edit_text("🗂 <b>Категории</b>", reply_markup=kb.admin_categories_kb(categories))
    await call.answer()


@router.callback_query(F.data.startswith("adm:cat:"))
async def adm_category_detail(call: CallbackQuery):
    if not await _require_admin(call):
        return
    cat_id = int(call.data.split(":")[2])
    category = await db.get_category(cat_id)
    products = await db.list_products(cat_id)
    if not category:
        await call.answer("Категория не найдена", show_alert=True)
        return
    text = f"<b>{category['name']}</b>\nТоваров: {len(products)}"
    await call.message.edit_text(text, reply_markup=kb.admin_category_kb(cat_id))
    await call.answer()


@router.callback_query(F.data == "adm:addcat")
async def adm_add_category_start(call: CallbackQuery, state: FSMContext):
    if not await _require_admin(call):
        return
    await state.set_state(AdminEditCategory.name)
    await state.update_data(action="add")
    await call.message.answer("Введите название новой категории:")
    await call.answer()


@router.callback_query(F.data.startswith("adm:editcat:"))
async def adm_edit_category_start(call: CallbackQuery, state: FSMContext):
    if not await _require_admin(call):
        return
    cat_id = int(call.data.split(":")[2])
    category = await db.get_category(cat_id)
    if not category:
        await call.answer("Категория не найдена", show_alert=True)
        return
    await state.set_state(AdminEditCategory.name)
    await state.update_data(action="edit", cat_id=cat_id)
    await call.message.answer(f"Текущее название: <b>{category['name']}</b>\nВведите новое:")
    await call.answer()


@router.message(AdminEditCategory.name)
async def adm_save_category(message: Message, state: FSMContext):
    if not await is_admin(message.from_user.id):
        return
    name = (message.text or "").strip()
    if not name:
        await message.answer("Название не должно быть пустым. Введите название:")
        return
    data = await state.get_data()
    try:
        if data["action"] == "add":
            await db.add_category(name)
            await message.answer("✅ Категория добавлена", reply_markup=kb.simple_admin_back_kb())
        else:
            await db.update_category(data["cat_id"], name)
            await message.answer("✅ Категория переименована", reply_markup=kb.simple_admin_back_kb())
    except Exception as exc:
        await message.answer(f"Не удалось сохранить категорию: {exc}")
    await state.clear()


@router.callback_query(F.data.startswith("adm:delcat:"))
async def adm_delete_category(call: CallbackQuery):
    if not await _require_admin(call):
        return
    cat_id = int(call.data.split(":")[2])
    await db.delete_category(cat_id)
    categories = await db.list_categories()
    await call.message.edit_text("🗂 <b>Категории</b>", reply_markup=kb.admin_categories_kb(categories))
    await call.answer("✅ Категория удалена")


# Orders
@router.callback_query(F.data == "adm:orders")
async def adm_orders(call: CallbackQuery):
    if not await _require_admin(call):
        return
    orders = await db.list_orders()
    text = "🛒 <b>Заказы</b>" if orders else "🛒 <b>Заказов пока нет</b>"
    await call.message.edit_text(text, reply_markup=kb.admin_orders_kb(orders))
    await call.answer()


@router.callback_query(F.data.startswith("adm:ord:"))
async def adm_order_detail(call: CallbackQuery):
    if not await _require_admin(call):
        return
    order_id = int(call.data.split(":")[2])
    order = await db.get_order(order_id)
    if not order:
        await call.answer("Заказ не найден", show_alert=True)
        return

    text = (
        f"<b>Заказ #{order['id']}</b>\n\n"
        f"👤 {order['name']}\n"
        f"📞 {order['phone']}\n"
        f"💰 {int(order['total'])}₽\n"
        f"Статус: {order['status']}\n\n"
        f"{order['items']}"
    )
    if order["comment"]:
        text += f"\n\n💬 {order['comment']}"

    await call.message.edit_text(text, reply_markup=kb.admin_order_kb(order_id))
    await call.answer()


@router.callback_query(F.data.startswith("adm:ordok:"))
async def adm_order_ok(call: CallbackQuery, bot: Bot):
    if not await _require_admin(call):
        return
    order_id = int(call.data.split(":")[2])
    await db.update_order_status(order_id, "done")
    order = await db.get_order(order_id)
    try:
        await bot.send_message(order["user_id"], f"✅ Заказ #{order_id} подтвержден!")
    except Exception:
        pass
    orders = await db.list_orders()
    text = "🛒 <b>Заказы</b>" if orders else "🛒 <b>Заказов пока нет</b>"
    await call.message.edit_text(text, reply_markup=kb.admin_orders_kb(orders))
    await call.answer("✅ Подтверждено")


@router.callback_query(F.data.startswith("adm:ordno:"))
async def adm_order_no(call: CallbackQuery, bot: Bot):
    if not await _require_admin(call):
        return
    order_id = int(call.data.split(":")[2])
    await db.update_order_status(order_id, "cancelled")
    order = await db.get_order(order_id)
    try:
        await bot.send_message(order["user_id"], f"❌ Заказ #{order_id} отменен.")
    except Exception:
        pass
    orders = await db.list_orders()
    text = "🛒 <b>Заказы</b>" if orders else "🛒 <b>Заказов пока нет</b>"
    await call.message.edit_text(text, reply_markup=kb.admin_orders_kb(orders))
    await call.answer("❌ Отменено")


# Texts and images
@router.callback_query(F.data == "adm:texts")
async def adm_texts(call: CallbackQuery):
    if not await _require_admin(call):
        return
    await call.message.edit_text("📝 <b>Тексты</b>", reply_markup=kb.admin_texts_kb())
    await call.answer()


@router.callback_query(F.data.startswith("adm:edtxt:"))
async def adm_edit_text_start(call: CallbackQuery, state: FSMContext):
    if not await _require_admin(call):
        return
    key = call.data.split(":")[2]
    current = await db.get_text(key)
    await state.set_state(AdminEditText.value)
    await state.update_data(action="set_text", key=key)
    await call.message.answer(f"Текущее значение:\n<code>{current}</code>\n\nВведите новое:")
    await call.answer()


@router.callback_query(F.data == "adm:menuedit")
async def adm_menu_edit(call: CallbackQuery):
    if not await _require_admin(call):
        return
    await call.message.edit_text("🔧 <b>Редактирование меню</b>", reply_markup=kb.admin_menu_edit_kb())
    await call.answer()


@router.callback_query(F.data.startswith("adm:edmenu:"))
async def adm_edit_menu_start(call: CallbackQuery, state: FSMContext):
    if not await _require_admin(call):
        return
    key = call.data.split(":")[2]
    db_key = f"menu_{key}"
    current = await db.get_text(db_key)
    await state.set_state(AdminEditText.value)
    await state.update_data(action="set_text", key=db_key)
    await call.message.answer(f"Текущее название: <b>{current}</b>\n\nВведите новое название:")
    await call.answer()


@router.callback_query(F.data == "adm:images")
async def adm_images(call: CallbackQuery):
    if not await _require_admin(call):
        return
    await call.message.edit_text("🖼 <b>Картинки разделов</b>", reply_markup=kb.admin_images_kb())
    await call.answer()


@router.callback_query(F.data.startswith("adm:edimg:"))
async def adm_edit_image_start(call: CallbackQuery, state: FSMContext):
    if not await _require_admin(call):
        return
    key = call.data.split(":")[2]
    await state.set_state(AdminEditImage.photo)
    await state.update_data(key=f"image_{key}")
    await call.message.answer("Отправьте новую картинку или '-' чтобы вернуть стандартную картинку из папки assets:")
    await call.answer()


@router.message(AdminEditImage.photo)
async def adm_save_image(message: Message, state: FSMContext):
    if not await is_admin(message.from_user.id):
        return
    data = await state.get_data()
    if message.photo:
        value = message.photo[-1].file_id
    elif _skip_value(message.text):
        value = ""
    else:
        await message.answer("Отправьте картинку или '-' для стандартной картинки:")
        return
    await db.set_text(data["key"], value)
    await state.clear()
    await message.answer("✅ Картинка сохранена", reply_markup=kb.simple_admin_back_kb())


# Payment
@router.callback_query(F.data == "adm:pay")
async def adm_pay(call: CallbackQuery):
    if not await _require_admin(call):
        return
    pay = await db.get_payment_info()
    text = (
        "💳 <b>Реквизиты</b>\n\n"
        f"Карта: {pay['card']}\n"
        f"Получатель: {pay['holder']}\n"
        f"Банк: {pay['bank']}"
    )
    await call.message.edit_text(text, reply_markup=kb.admin_pay_kb())
    await call.answer()


# Admins
@router.callback_query(F.data == "adm:admins")
async def adm_admins(call: CallbackQuery):
    if not await _require_admin(call):
        return
    admins = await db.list_admins()
    await call.message.edit_text("👥 <b>Админы</b>", reply_markup=kb.admin_admins_kb(admins))
    await call.answer()


@router.callback_query(F.data.startswith("adm:deladm:"))
async def adm_delete_admin(call: CallbackQuery):
    if not await _require_admin(call):
        return
    user_id = int(call.data.split(":")[2])
    await db.remove_admin(user_id)
    admins = await db.list_admins()
    await call.message.edit_text("👥 <b>Админы</b>", reply_markup=kb.admin_admins_kb(admins))
    await call.answer("✅ Удален")


@router.callback_query(F.data == "adm:addadm")
async def adm_add_admin_start(call: CallbackQuery, state: FSMContext):
    if not await _require_admin(call):
        return
    await state.set_state(AdminEditText.value)
    await state.update_data(action="add_admin")
    await call.message.answer("Введите Telegram ID нового админа:")
    await call.answer()


# Stats and broadcast
@router.callback_query(F.data == "adm:stats")
async def adm_stats(call: CallbackQuery):
    if not await _require_admin(call):
        return
    stats = await db.get_stats()
    text = (
        "📊 <b>Статистика</b>\n\n"
        f"👥 Пользователей: {stats['users']}\n"
        f"🛒 Заказов: {stats['orders']}\n"
        f"📦 Товаров: {stats['products']}\n"
        f"🗂 Категорий: {stats['categories']}"
    )
    await call.message.edit_text(text, reply_markup=kb.simple_admin_back_kb())
    await call.answer()


@router.callback_query(F.data == "adm:broadcast")
async def adm_broadcast_start(call: CallbackQuery, state: FSMContext):
    if not await _require_admin(call):
        return
    await state.set_state(AdminEditText.value)
    await state.update_data(action="broadcast")
    await call.message.answer("Введите текст рассылки:")
    await call.answer()


@router.message(AdminEditText.value)
async def adm_text_state_router(message: Message, state: FSMContext, bot: Bot):
    if not await is_admin(message.from_user.id):
        return
    data = await state.get_data()
    action = data.get("action")

    if action == "set_text":
        await db.set_text(data["key"], message.text or "")
        await message.answer("✅ Сохранено", reply_markup=kb.simple_admin_back_kb())

    elif action == "add_admin":
        try:
            user_id = int((message.text or "").strip())
        except ValueError:
            await message.answer("ID должен быть числом. Введите Telegram ID:")
            return
        await db.add_admin(user_id, added_by=message.from_user.id)
        await message.answer("✅ Админ добавлен", reply_markup=kb.simple_admin_back_kb())

    elif action == "broadcast":
        users = await db.list_users()
        ok = 0
        failed = 0
        for user in users:
            try:
                await bot.send_message(user["user_id"], message.text or "")
                ok += 1
            except Exception:
                failed += 1
        await message.answer(
            f"✅ Рассылка завершена\nДоставлено: {ok}\nОшибок: {failed}",
            reply_markup=kb.simple_admin_back_kb(),
        )

    else:
        await message.answer("Действие не найдено. Откройте админ-панель заново: /admin")

    await state.clear()
