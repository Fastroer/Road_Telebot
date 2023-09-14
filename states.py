from aiogram.fsm.state import State, StatesGroup


class RegistrationStates(StatesGroup):
    waiting_for_contact = State()
    waiting_for_city = State()
    waiting_for_make = State()
    waiting_for_model = State()
    waiting_for_year = State()
    waiting_for_color = State()
    waiting_for_license_plate = State()


class UsersSearchStates(StatesGroup):
    waiting_for_license_plate = State()
    waiting_for_users_info = State()
    waiting_for_user = State()
    waiting_for_message_to_user = State()
