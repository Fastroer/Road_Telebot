from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram import F, Router
import keyboards as kb
import re

from db.base_db import is_user_registered, register_user, register_user_car, \
    delete_user, update_user_car, get_user_id, driver_search, add_message, your_messages
from states import RegistrationStates, UsersSearchStates

router = Router()


async def process_callback(callback: CallbackQuery, message_text):
    await callback.answer()
    await callback.message.answer(message_text, reply_markup=None)
    await callback.message.delete()


async def validate_car_number(car_number):
    patterns = {
        "Беларуси": r'^\d{4}[A-Z]{2}-\d$',
        "России": r'^X\d{3}[A-Z]{2}\d{2,3}$',
        "Украины": r'^[A-Z]{2}\d{4}[A-Z]{2}$',
        "Казахстана": r'^[Xx]?\d{2,6}[XYZxyz]{0,3}$',
        "Казахстана ": r"^\d{3}[XYxy]{2}\d{2}$",
        "Казахстана  ": r"^\d{3}[XYZxyz]{3}\d{2}$",
    }

    for country, pattern in patterns.items():
        if re.match(pattern, car_number):
            return country
    return None


@router.message(F.text == '/start')
async def start(message: Message):
    user_name = message.from_user.first_name
    await message.answer(f"Привет, {user_name}! Я Бот Невовка, который поможет тебе общаться с другими водителями,"
                         f" а также просматривать про них информацию", reply_markup=kb.main)


@router.message(F.text == 'Удалиться 📤')
async def registration(message: Message):
    is_registered = await is_user_registered(message.from_user.id)

    if is_registered is None:
        await message.answer('Вам необходимо зарегистрироваться')
        return

    user_id = await get_user_id(telegram_id=message.from_user.id)
    await delete_user(user_id)
    await message.answer('Ваши данные успешно стерты из базы данных')


@router.message(F.text == 'Зарегистрироваться 🖥')
async def registration(message: Message, state: FSMContext):
    is_registered = await is_user_registered(message.from_user.id)

    if is_registered is not None:
        await message.answer('Вы уже зарегистрированы')
        return
    await state.set_state(RegistrationStates.waiting_for_contact)

    await message.answer('Для начала, нажмите Поделиться профилем, '
                         'так мы получим необходимые данные', reply_markup=kb.share_profile)


@router.message(RegistrationStates.waiting_for_contact)
async def get_contact(message: Message, state: FSMContext):
    contact = message.contact
    await message.answer(f"Спасибо, {contact.first_name}.\n"
                         f"Ваш номер {contact.phone_number} был получен.\n"
                         f"Теперь введите на русском город проживания",
                         reply_markup=ReplyKeyboardRemove())

    await state.set_state(RegistrationStates.waiting_for_city)

    @router.message(RegistrationStates.waiting_for_city)
    async def get_message(message: Message, state: FSMContext):
        await message.answer(f'Вы выбрали город {message.text}')
        await message.delete()

        await register_user(first_name=message.from_user.first_name, last_name=message.from_user.last_name,
                            phone_number=contact.phone_number, city=message.text,
                            telegram_id=message.from_user.id)

        await message.answer("Вы успешно зарегистрировались как пользователь, "
                             "теперь давайте зарегистрируем ваше авто")
        await state.set_state(RegistrationStates.waiting_for_make)
        keyboard = await kb.get_car_brands_keyboard()
        await message.answer("Выберите марку автомобиля:", reply_markup=keyboard.as_markup())


@router.callback_query(RegistrationStates.waiting_for_make)
async def get_machine_mark(callback: CallbackQuery, state: FSMContext):
    await process_callback(callback, f'Вы выбрали марку {callback.data}')

    user_id = await get_user_id(telegram_id=callback.from_user.id)
    await register_user_car(make=callback.data, user_id=user_id)

    models = [model async for model in kb.get_models_by_brand_async(callback.data)]

    await state.set_state(RegistrationStates.waiting_for_model)

    keyboard = await kb.get_car_models_keyboard(models)
    await callback.message.answer("Выберите модель автомобиля:", reply_markup=keyboard.as_markup())


@router.callback_query(RegistrationStates.waiting_for_model)
async def get_machine_model(callback: CallbackQuery, state: FSMContext):
    await process_callback(callback, f'Вы выбрали модель {callback.data}')

    user_id = await get_user_id(telegram_id=callback.from_user.id)
    await update_user_car(data=['model', callback.data], user_id=user_id)

    await state.set_state(RegistrationStates.waiting_for_year)

    keyboard = await kb.get_car_years_keyboard()
    await callback.message.answer(f"Выберите год выпуска автомобиля:", reply_markup=keyboard.as_markup())


@router.callback_query(RegistrationStates.waiting_for_year)
async def get_machine_year(callback: CallbackQuery, state: FSMContext):
    await process_callback(callback, f'Вы выбрали год выпуска {callback.data}')

    user_id = await get_user_id(telegram_id=callback.from_user.id)
    await update_user_car(data=['year', callback.data], user_id=user_id)

    await state.set_state(RegistrationStates.waiting_for_color)

    keyboard = await kb.get_car_colors_keyboard()
    await callback.message.answer(f"Выберите цвет автомобиля:", reply_markup=keyboard.as_markup())


@router.callback_query(RegistrationStates.waiting_for_color)
async def get_machine_color(callback: CallbackQuery, state: FSMContext):
    await process_callback(callback, f'Вы выбрали цвет машины {callback.data}')

    user_id = await get_user_id(telegram_id=callback.from_user.id)
    await update_user_car(data=['color', callback.data], user_id=user_id)

    await callback.message.answer("Введите латиницей номер автомобиля в формате:\n"
                                  "- 1234ZZ-7 (для Беларуси)\n"
                                  "- X123YZ12, X123YZ123 (для России)\n"
                                  "- YZ1234YX (для Украины)\n"
                                  "- X123YZ, X1234YZ, X1234XYZ, 1234YZ, 1234XYZ, X123456, "
                                  "123XY45, 123XYZ45, 12XY (для Казахстана):")

    await state.set_state(RegistrationStates.waiting_for_license_plate)

    @router.message(RegistrationStates.waiting_for_license_plate)
    async def get_message_car(message: Message, state: FSMContext):
        car_number = message.text

        country = await validate_car_number(car_number)

        if country is None:
            await message.answer(
                "Вы ввели недействительный номер автомобиля. "
                "Пожалуйста, введите номер снова и убедитесь, что он соответствует формату.")
        else:
            await message.delete()

            user_id = await get_user_id(telegram_id=message.from_user.id)
            await update_user_car(data=['license_plate', car_number], user_id=user_id)

            await message.answer(f"Вы ввели номер автомобиля: {car_number}.\n"
                                 f"Этот номер соответствует формату для {country}")
            await message.answer('Вы успешно прошли регистрацию автомобиля ✅', reply_markup=kb.main)
        await state.clear()


@router.message(F.text == 'Найти водителя по номеру авто 🚗')
async def driver_search_function(message: Message, state: FSMContext):
    await message.answer('Введи номер автомобиля: ')

    await state.set_state(UsersSearchStates.waiting_for_license_plate)

    @router.message(UsersSearchStates.waiting_for_license_plate)
    async def get_message_car_number(message: Message, state: FSMContext):
        car_number = message.text

        country = await validate_car_number(car_number)

        if country is None:
            await message.answer(
                "Вы ввели недействительный номер автомобиля. "
                "Пожалуйста, введите номер снова и убедитесь, что он соответствует формату.")
            await state.clear()

        else:
            await message.delete()
            await message.answer(f"Вы ввели номер автомобиля: {car_number}")
            users_list = await driver_search(car_number)
            if users_list:
                await state.set_state(UsersSearchStates.waiting_for_users_info)
                keyboard = await kb.get_users_list_keyboard(users_list)
                await message.answer(f'Вот список людей с таким номером: ', reply_markup=keyboard.as_markup())
            if not users_list:
                await message.answer('Похоже водитель с таким номер не зарегистрирован в нашем боте')

                await state.clear()

        @router.callback_query(UsersSearchStates.waiting_for_users_info)
        async def users_messages(callback: CallbackQuery, state: FSMContext):
            data = callback.data.split(' ')
            user_name = data[2] + ' ' + data[3]
            await process_callback(callback, f'Вы выбрали пользователя {user_name}')

            await state.clear()

            keyboard = await kb.get_or_not_message_keyboard()
            await callback.message.answer(f'Желаете отправить выбранному пользователю сообщение: ',
                                          reply_markup=keyboard.as_markup())

            @router.callback_query(lambda query: query.data == 'send a message')
            async def send_message_to_user(callback: CallbackQuery, state: FSMContext):
                await process_callback(callback, f'Введите сообщение для выбранного пользователя: ')
                await state.set_state(UsersSearchStates.waiting_for_message_to_user)

                @router.message(UsersSearchStates.waiting_for_message_to_user)
                async def get_message_for_user(message: Message):
                    message_text = message.text
                    receiver_user_id = int(data[1])
                    sender_user_id = await get_user_id(telegram_id=message.from_user.id)
                    await add_message(sender_user_id=sender_user_id, receiver_user_id=receiver_user_id,
                                      message_text=message_text)
                    await message.answer('Сообщение успешно отправлено')
                    await state.clear()


@router.message(F.text == 'Мои сообщения ✉')
async def my_messages(message: Message):
    is_registered = await is_user_registered(message.from_user.id)

    if is_registered is None:
        await message.answer('Вам необходимо зарегистрироваться')
        return

    your_id = await get_user_id(telegram_id=message.from_user.id)
    your_messages_data = await your_messages(your_id)
    if your_messages_data:
        await message.answer('Вот все сообщения адресованные вам: ')
        for u_message in your_messages_data:
            await message.answer(f'Отправитель: {u_message[0]}. \n'
                                 f'Текст сообщения: {u_message[1]}.')
    elif not your_messages_data:
        await message.answer('Пока вам не приходило сообщений')


@router.callback_query(lambda query: query.data == 'dont send message')
async def back(callback: CallbackQuery):
    await process_callback(callback, 'Возврат к главному меню')
