import asyncio
import csv

from aiogram.types import (InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup)
from aiogram.utils.keyboard import InlineKeyboardBuilder

main_kb = [
    [KeyboardButton(text="Зарегистрироваться 🖥"),
     KeyboardButton(text="Найти водителя по номеру авто 🚗")],
    [KeyboardButton(text="Удалиться 📤"),
     KeyboardButton(text="Мои сообщения ✉")]
]

main = ReplyKeyboardMarkup(keyboard=main_kb,
                           resize_keyboard=True,
                           input_field_placeholder='Выберите пункт ниже')

share_profile = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text='Поделиться профилем ✅', request_contact=True, request_location=True)]],
    resize_keyboard=True,
    input_field_placeholder='Поделитесь профилем ✅')

car_brands = ["Audi", "BMW", "Chevrolet", "Chrysler", "Dodge", "Fiat", "Ford", "Honda", "Hyundai", "Infiniti", "Jaguar",
              "Jeep", "Kia", "Lamborghini", "Land Rover", "Lexus", "Lincoln", "Mazda", "Mini",
              "Mitsubishi", "Nissan", "Opel", "Peugeot", "Porsche", "Renault", "Seat", "Skoda", "Smart", "Subaru",
              "Suzuki", "Toyota", "Volkswagen", "Volvo"]

years = [str(year) for year in range(1968, 2024)]

car_colors = ["Черный", "Белый", "Серый", "Серебристый", "Синий", "Красный", "Зеленый", "Желтый", "Коричневый",
              "Оранжевый", "Бежевый", "Другое"]


async def get_car_brands_keyboard():
    machines_keyboard = InlineKeyboardBuilder()

    for i in range(0, len(car_brands), 3):
        machines_keyboard.row(*[InlineKeyboardButton(text=brand, callback_data=brand) for brand in car_brands[i:i + 3]])

    return machines_keyboard


async def get_models_by_brand_async(brand):
    loop = asyncio.get_event_loop()

    with open("E:\\Road_Telebot\\csv.csv", "r") as f:
        reader = csv.reader(f, delimiter=";")
        rows = await loop.run_in_executor(None, list, reader)

        for row in rows:
            if row[0] == brand:
                yield row[1]


async def get_car_models_keyboard(car_models):
    models_keyboard = InlineKeyboardBuilder()

    for i in range(0, len(car_models), 3):
        models_keyboard.row(*[InlineKeyboardButton(text=model, callback_data=model) for model in car_models[i:i + 3]])

    return models_keyboard


async def get_car_years_keyboard():
    years_keyboard = InlineKeyboardBuilder()
    for i in range(0, len(years), 4):
        years_keyboard.row(*[InlineKeyboardButton(text=str(year), callback_data=str(year)) for year in years[i:i + 4]])

    return years_keyboard


async def get_car_colors_keyboard():
    colors_keyboard = InlineKeyboardBuilder()
    for i in range(0, len(car_colors), 3):
        colors_keyboard.row(*[InlineKeyboardButton(text=color, callback_data=color) for color in car_colors[i:i + 3]])

    return colors_keyboard


async def get_users_list_keyboard(users_list):
    users_keyboard = InlineKeyboardBuilder()
    for user_data in range(0, len(users_list), 2):
        users_keyboard.row(
            InlineKeyboardButton(text=users_list[user_data], callback_data=f'user {users_list[user_data + 1]} {users_list[user_data]}'))

    return users_keyboard


async def get_or_not_message_keyboard():
    message_keyboard = InlineKeyboardBuilder()

    message_keyboard.row(*[InlineKeyboardButton(text='Да', callback_data='send a message')])
    message_keyboard.row(*[InlineKeyboardButton(text='Нет', callback_data='dont send message')])

    return message_keyboard
