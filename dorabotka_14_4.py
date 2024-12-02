from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
from crud_functions import *

api = '7898781198:AAFPcK1g6Er5calmo2EpyvdhYllVPe_3G7w'
bot = Bot(token = api)
dp = Dispatcher(bot, storage = MemoryStorage())
get_all_products()

class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()

# class State:
#     def __init__(self, value=None):
#         self.value = value

class RegistrationState(StatesGroup):
    username = State()
    email = State()
    age = State()
    balance = State(1000)
registration_state = RegistrationState()

@dp.message_handler(text=['Регистрация'])
async def sing_up(message):
    await message.answer("Введите имя пользователя (только латинский алфавит):")
    await RegistrationState.username.set()


@dp.message_handler(state=registration_state.username)
async def set_username(message: types.Message, state: FSMContext):
    username = message.text
    if is_included(username):
        await message.answer("Пользователь существует, введите другое имя:")
    else:
        await state.update_data(username=username)
        await message.answer("Введите свой email:")
        await RegistrationState.email.set()

@dp.message_handler(state=registration_state.email)
async def set_email(message: types.Message, state: FSMContext):
    email = message.text
    await state.update_data(email=email)
    await message.answer("Введите свой возраст:")
    await RegistrationState.age.set()


@dp.message_handler(state=registration_state.age)
async def set_age(message: types.Message, state: FSMContext):
    age = message.text
    await state.update_data(age=age)
    user_data = await state.get_data()
    username = user_data.get('username')
    email = user_data.get('email')
    add_user(username=username, email=email, age=age)
    await message.answer("Регистрация завершена! Ваши данные сохранены.")
    await state.finish()


kb = ReplyKeyboardMarkup(resize_keyboard=True)
button1 = KeyboardButton(text = 'Рассчитать')
button2 = KeyboardButton(text = 'Информация')
button3 = KeyboardButton(text = 'Купить')
button4 = KeyboardButton(text = 'Регистрация')
kb.add(button1, button2, button3, button4)

productsss = InlineKeyboardMarkup(resize_keyboard=True)
button_product1 = InlineKeyboardButton('Product1', callback_data="product_buying")
button_product2 = InlineKeyboardButton('Product2', callback_data="product_buying")
button_product3 = InlineKeyboardButton('Product3', callback_data="product_buying")
button_product4 = InlineKeyboardButton('Product4', callback_data="product_buying")
productsss.add(button_product1, button_product2, button_product3, button_product4)

@dp.message_handler(text=['Купить'])
async def get_buying_list(message):
    products = get_all_products()
    for product in products:
        id, title, description, price = product
        await message.answer(f'Название: {title} | Описание: {description} | Цена: {price}')
        if id == 1:
            image_path = "vanil.jpg"
        elif id == 2:
            image_path = "баблгам.jpg"
        elif id == 3:
            image_path = "клубника.jpg"
        elif id == 4:
            image_path = "fruct_led.jpg"
        if image_path:
            with open(image_path, "rb") as photo:
                await message.answer_photo(photo)
    await message.answer('Выберите продукт для покупки:', reply_markup=productsss)


@dp.callback_query_handler(text = ["product_buying"])
async def send_confirm_message(call):
    await call.message.answer("Вы успешно приобрели продукт!")


dvach = InlineKeyboardMarkup(resize_keyboard=True)
button_dvach1 = InlineKeyboardButton('Рассчитать норму калорий', callback_data='calories')
button_dvach2 = InlineKeyboardButton('Формула расчёта', callback_data='formulas')
dvach.add(button_dvach1, button_dvach2)

@dp.message_handler(text = ['Рассчитать'])
async def main_menu(message):
    await message.answer('Выберите опцию:', reply_markup=dvach)



@dp.callback_query_handler(text='formulas')
async def get_formulas(call):
    await call.message.answer('10 х вес (кг) + 6,25 x рост (см) – 5 х возраст (г) + 5')

    await call.answer()

@dp.message_handler(commands = ['start'])
async def start(message):
    await message.answer('Привет! Я бот помогающий твоему здоровью.', reply_markup = kb)


@dp.callback_query_handler(text = ['calories'])
async def set_age(call):
    await call.message.answer('Введите свой возраст:')
    await UserState.age.set()
    await call.age()


@dp.message_handler(state = UserState.age)
async def set_growth(message, state):
    await state.update_data(age=message.text)
    await message.answer('Введите свой рост:')
    await UserState.growth.set()

@dp.message_handler(state = UserState.growth)
async def set_weight(message, state):
    await state.update_data(growth=message.text)
    await message.answer('Введите свой вес:')
    await UserState.weight.set()

@dp.message_handler(state = UserState.weight)
async def send_calories(message, state):
    await state.update_data(weight=message.text)
    data = await state.get_data()
    formula = (int(data['growth']) * 6.25) + (int(data['weight']) * 10) - (int(data['age']) * 5)
    await message.answer(f"Ваша норма каллорий: {formula}")

@dp.message_handler()
async def all_message(message):
    await message.answer('Введите команду /start, чтобы начать общение.')

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates = True)