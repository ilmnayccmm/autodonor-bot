import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

from config import *
from db import init_db, add_request, get_all_requests

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Ініціалізація бази при запуску
init_db()


# ---------- СТАНИ (FSM) ----------

class RequestState(StatesGroup):
    choosing_service = State()
    waiting_phone = State()


# ---------- КЛАВІАТУРИ ----------

def main_menu():
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔧 Послуги"), KeyboardButton(text="📝 Запис / Заявка")],
            [KeyboardButton(text="🕒 Графік роботи"), KeyboardButton(text="📍 Контакти")],
            [KeyboardButton(text="🚚 Евакуатор")]
        ],
        resize_keyboard=True
    )
    return kb


def services_menu():
    buttons = [[KeyboardButton(text=s)] for s in SERVICES]
    buttons.append([KeyboardButton(text="⬅ Назад")])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


# ---------- ОБРОБНИКИ ----------

@dp.message(Command("start", "menu"))
@dp.message(F.text == "⬅ Назад")
async def start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        f"Вітаємо у {STO_NAME} 👋\n\nОберіть дію з меню 👇",
        reply_markup=main_menu()
    )


@dp.message(Command("services"))
@dp.message(F.text == "🔧 Послуги")
@dp.message(F.text == "📝 Запис / Заявка")
async def show_services(message: types.Message, state: FSMContext):
    await state.set_state(RequestState.choosing_service)
    await message.answer("🔧 Оберіть послугу з переліку:", reply_markup=services_menu())


@dp.message(RequestState.choosing_service)
async def choose_service(message: types.Message, state: FSMContext):
    if message.text not in SERVICES:
        await message.answer("❌ Будь ласка, оберіть послугу за допомогою кнопок.")
        return

    await state.update_data(service=message.text)
    await state.set_state(RequestState.waiting_phone)
    await message.answer(
        f"✅ Ви обрали: <b>{message.text}</b>\n\n📞 Введіть номер телефону:",
        parse_mode="HTML"
    )


@dp.message(RequestState.waiting_phone)
async def save_request_handler(message: types.Message, state: FSMContext):
    phone = message.text.strip()

    if len(phone) < 9:
        await message.answer("❌ Введіть коректний номер телефону")
        return

    data = await state.get_data()
    service = data.get("service")

    # Збереження в БД
    add_request(
        user_id=message.from_user.id,
        username=message.from_user.username,
        service=service,
        phone=phone
    )

    # Сповіщення адміна
    try:
        if ADMIN_ID:
            admin_msg = (
                f"🚀 <b>Нова заявка!</b>\n\n"
                f"🛠 Послуга: {service}\n"
                f"📞 Телефон: {phone}\n"
                f"👤 Клієнт: @{message.from_user.username or 'без ніку'}"
            )
            await bot.send_message(chat_id=ADMIN_ID, text=admin_msg, parse_mode="HTML")
    except Exception as e:
        print(f"Помилка сповіщення: {e}")

    await message.answer("✅ Заявку прийнято! Скоро ми з вами зв'яжемось.", reply_markup=main_menu())
    await state.clear()


# ---------- ІНФО-БЛОКИ ----------

@dp.message(F.text == "🕒 Графік роботи")
async def schedule(message: types.Message):
    await message.answer(f"🕒 Графік роботи:\n{SCHEDULE}")


@dp.message(F.text == "📍 Контакти")
async def contacts(message: types.Message):
    await message.answer(f"📍 Адреса: {ADDRESS}\n📞 Тел: {PHONE}\n👨‍💼 Адмін: {ADMIN_TG}")


@dp.message(F.text == "🚚 Евакуатор")
async def evacuator(message: types.Message):
    await message.answer("🚚 Послуги евакуатора цілодобово.\n📞 Телефонуйте: 098 199 1246")


# ---------- АДМІН-ПАНЕЛЬ ----------

@dp.message(Command("admin"))
async def admin_panel(message: types.Message):
    if str(message.from_user.id) != str(ADMIN_ID):
        return  # Ігноруємо не-адмінів

    requests = get_all_requests()
    if not requests:
        await message.answer("Список заявок порожній.")
        return

    res = "📋 <b>Останні 10 заявок:</b>\n\n"
    for r in requests:
        res += f"📅 {r[0]}\n🛠 {r[1]}\n📞 {r[2]}\n👤 @{r[3] or '---'}\n\n"

    await message.answer(res, parse_mode="HTML")


# ---------- ЗАПУСК ----------

async def main():
    await bot.set_my_commands([
        types.BotCommand(command="menu", description="Головне меню"),
        types.BotCommand(command="admin", description="Заявки (для адміна)")
    ])
    print("🚀 Бот Автодонор запущений!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())