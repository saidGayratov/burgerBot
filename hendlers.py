from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, \
    InlineKeyboardButton
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import ADMINS
from database import save_orders

router = Router()

class Order(StatesGroup):
    choosing_burger = State()
    entering_phone = State()


def get_main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Burger buyurtma qilish")],
            [KeyboardButton(text="Biz haqimizda"), KeyboardButton(text="Aloqa")]
        ],
        resize_keyboard=True
    )


def get_burger_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Cheeseburger - 25,000 so'm", callback_data="burger_cheese")],
            [InlineKeyboardButton(text="Double Burger - 35,000 so'm", callback_data="burger_double")],
            [InlineKeyboardButton(text="Hot Burger - 35,000 so'm", callback_data="burger_hot")]
        ]
    )


@router.message(CommandStart())
async def cmd_start(message: Message):
    text = "Assalomu aleykum! Guliston Burger Uz yetkazib berish xizmatiga xush kelibsiz."
    await message.answer(text, reply_markup=get_main_menu())


@router.message(F.text == "Burger buyurtma qilish")
async def start_order(message: Message, state: FSMContext):
    await message.answer("Marhamat, menyudan o'zingizga yoqgan burgerni tanlang", reply_markup=get_burger_menu())
    await state.set_state(Order.choosing_burger)


@router.callback_query(Order.choosing_burger, F.data.startswith("burger_"))
async def process_burger(callback: CallbackQuery, state: FSMContext):
    burger_name = callback.data.split("_")[1].capitalize()
    await state.update_data(burger=burger_name)
    await callback.message.answer("Raqamingizni yuboring (masalan: +998912345678 yoki tugmani bosing):",
                                  reply_markup=ReplyKeyboardMarkup(
                                      keyboard=[
                                          [KeyboardButton(text="Telefon raqamni yuborish", request_contact=True)]],
                                      resize_keyboard=True,
                                      one_time_keyboard=True
                                  ))
    await state.set_state(Order.entering_phone)
    await callback.answer()


@router.message(Order.entering_phone, F.contact | F.text)
async def process_phone(message: Message, state: FSMContext):
    phone = message.contact.phone_number if message.contact else message.text
    data = await state.get_data()
    burger = data.get("burger")

    try:
        save_orders(message.from_user.id, message.from_user.full_name, phone, burger)
    except Exception as e:
        print(f"Database saving error: {e}")

    await message.answer(
        f"Buyurmangiz qabul qilindi!\nBurger: {burger}\nTez orada operatorimiz siz bilan bog'lanishadi.",
        reply_markup=get_main_menu()
    )

    for admin_id in ADMINS:
        try:
            admin_text = f"Yangi buyurtma!\n\nMijoz: {message.from_user.full_name}\nTelefon: {phone}\nBuyurtma: {burger}"
            await message.bot.send_message(admin_id, admin_text)
        except Exception:
            pass

    await state.clear()


@router.message(F.text == "Biz haqimizda")
async def about_us(message: Message):
    await message.answer("Guliston Burger Uz - Guliston shahridagi eng mazali va sharofatli burgerlar maskani!")


@router.message(F.text == "Aloqa")
async def contact_us(message: Message):
    await message.answer("Murojaat uchun: +998 93 353-33-13\nManzil: Guliston shahar, Mahalla gilam magazin yonida.")