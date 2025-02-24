from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv
import os
import asyncio
import uuid  # Для генерации уникального ID

load_dotenv()

# Токен бота и ID чата администратора
TOKEN = os.getenv("TOKEN") # Замените на ваш токен
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID"))  # Замените на ваш chat_id

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Меню
menu = {
    "Starters": ["Bruschetta", "Caprese Salad", "Garlic Shrimp"],
    "Pasta & Risotto": ["Carbonara", "Seafood Risotto", "Penne Arrabbiata"],
    "Pizza": ["Margherita", "Funghi e Prosciutto", "Diavola"],
    "Main Courses": ["T-Bone Steak", "Oven-Baked Sea Bass", "Chicken Cacciatore"],
    "Desserts": ["Tiramisu", "Panna Cotta", "Chocolate Lava Cake"],
    "Drinks": ["Red & White Wine", "Aperol Spritz", "Espresso"]
}

# Описание меню
menu_description = """
🔹 1. Starters 🍽️

🥖 Bruschetta al Pomodoro – Toasted bread with fresh tomatoes, basil & olive oil
🧀 Caprese Salad – Mozzarella, tomatoes & basil with balsamic glaze
🍤 Gamberi al Aglio – Garlic butter shrimp with herbs

🔹 2. Pasta & Risotto 🍝

🍝 Spaghetti Carbonara – Traditional Roman pasta with pancetta, egg & cheese
🍤 Seafood Risotto – Creamy risotto with shrimp, mussels & calamari
🍆 Penne Arrabbiata – Spicy tomato sauce with garlic & chili

🔹 3. Pizza 🍕

🍕 Margherita – Tomato sauce, mozzarella & fresh basil
🍄 Funghi e Prosciutto – Mushrooms, prosciutto & mozzarella
🌶️ Diavola – Spicy salami, tomato sauce & mozzarella

🔹 4. Main Courses 🍖

🥩 Bistecca alla Fiorentina – Grilled T-bone steak with rosemary
🐟 Branzino al Forno – Oven-baked sea bass with lemon & herbs
🍗 Pollo alla Cacciatora – Chicken braised with tomatoes, olives & white wine

🔹 5. Desserts 🍰

🍮 Tiramisu – Coffee-soaked sponge cake with mascarpone
🍨 Panna Cotta – Italian vanilla cream pudding with berry sauce
🍫 Chocolate Lava Cake – Warm chocolate cake with molten center

🔹 6. Drinks 🍷

🍷 Red & White Wine – Selection of fine Italian wines
🍹 Aperol Spritz – Classic Italian aperitif
☕ Espresso – Authentic Italian coffee
"""

# Корзина заказов (словарь: блюдо -> количество)
orders = {}

# Время доставки (будет задано пользователем)
delivery_time = None

# Уникальный ID заказа
order_id = str(uuid.uuid4())[:8]  # Генерация короткого уникального ID

# Стартовое меню (только Menu и View Order)
start_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Menu"), KeyboardButton(text="🛒 View Order")]
    ],
    resize_keyboard=True
)

# Главное меню (категории)
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=category)] for category in menu.keys()
    ] + [
        [KeyboardButton(text="⬅ Back to Start")]
    ],
    resize_keyboard=True
)

# Обработчик команды /start
@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer("🍽 Welcome to our Italian Restaurant! What would you like to do?", reply_markup=start_menu)

# Обработчик кнопки Menu
@dp.message(lambda message: message.text == "Menu")
async def show_menu(message: types.Message):
    await message.answer(menu_description, reply_markup=main_menu)

# Обработчик выбора категории
@dp.message(lambda message: message.text in menu.keys())
async def select_category(message: types.Message):
    category = message.text
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=item)] for item in menu[category]
        ] + [
            [KeyboardButton(text="⬅ Back to Menu")]
        ],
        resize_keyboard=True
    )
    await message.answer(f"🍕 Choose a dish from {category}:", reply_markup=markup)

# Обработчик выбора блюда
@dp.message(lambda message: any(message.text in items for items in menu.values()))
async def select_item(message: types.Message):
    dish = message.text
    if dish in orders:
        orders[dish] += 1
    else:
        orders[dish] = 1

    markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=f"➕ Add more {dish}")],
            [KeyboardButton(text="⬅ Back to Menu")]
        ],
        resize_keyboard=True
    )
    await message.answer(f"✅ {dish} added to your order! Current quantity: {orders[dish]}", reply_markup=markup)

# Обработчик добавления дополнительных единиц блюда
@dp.message(lambda message: message.text.startswith("➕ Add more"))
async def add_more_dish(message: types.Message):
    dish = message.text.replace("➕ Add more ", "")
    if dish in orders:
        orders[dish] += 1
        await message.answer(f"✅ Added one more {dish}. Current quantity: {orders[dish]}")
    else:
        await message.answer("❌ Dish not found in your order.")

# Просмотр заказа
@dp.message(lambda message: message.text == "🛒 View Order")
async def view_order(message: types.Message):
    if not orders:
        await message.answer("🛒 Your order is empty.")
    else:
        order_list = "\n".join([f"{dish} x {quantity}" for dish, quantity in orders.items()])
        markup = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="✅ Confirm Order")],
                [KeyboardButton(text="⬅ Back to Start")]
            ],
            resize_keyboard=True
        )
        await message.answer(f"🛒 Your order:\n{order_list}", reply_markup=markup)

# Обработчик подтверждения заказа
@dp.message(lambda message: message.text == "✅ Confirm Order")
async def confirm_order(message: types.Message):
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="10 minutes"), KeyboardButton(text="20 minutes")],
            [KeyboardButton(text="30 minutes")]
        ],
        resize_keyboard=True
    )
    await message.answer("🕒 Choose delivery time:", reply_markup=markup)

# Обработчик выбора времени доставки
@dp.message(lambda message: message.text.endswith("minutes"))
async def select_delivery_time(message: types.Message):
    global delivery_time
    delivery_time = message.text
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Send Order")]
        ],
        resize_keyboard=True
    )
    await message.answer(f"🕒 Delivery time set to {delivery_time}. Press '✅ Send Order' to confirm.", reply_markup=markup)

# Отправка заказа администратору
@dp.message(lambda message: message.text == "✅ Send Order")
async def send_order(message: types.Message):
    global order_id  # Объявляем order_id как глобальную переменную
    if not orders:
        await message.answer("🛒 Your order is empty.")
    else:
        order_list = "\n".join([f"{dish} x {quantity}" for dish, quantity in orders.items()])
        # Формируем сообщение для администратора
        order_message = (
            f"📩 New Order ID: {order_id}\n"
            f"👤 Customer ID: {message.from_user.id}\n"
            f"🛒 Order:\n{order_list}\n"
            f"🕒 Delivery time: {delivery_time}"
        )
        # Отправляем заказ администратору
        await bot.send_message(chat_id=ADMIN_CHAT_ID, text=order_message)
        # Очистка корзины после отправки
        orders.clear()
        # Генерация нового ID для следующего заказа
        order_id = str(uuid.uuid4())[:8]
        await message.answer("✅ Your order has been sent! Thank you!", reply_markup=start_menu)

# Кнопка назад в стартовое меню
@dp.message(lambda message: message.text == "⬅ Back to Start")
async def back_to_start(message: types.Message):
    await message.answer("🍽 What would you like to do?", reply_markup=start_menu)

# Кнопка назад в меню
@dp.message(lambda message: message.text == "⬅ Back to Menu")
async def back_to_menu(message: types.Message):
    await message.answer("🍽 Choose a category:", reply_markup=main_menu)

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())