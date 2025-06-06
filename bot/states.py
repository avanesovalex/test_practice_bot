from aiogram.fsm.state import StatesGroup, State

class Registration(StatesGroup):
    wait_for_name = State()
    wait_for_birthdate = State()
    wait_for_phone = State()

class Menu(StatesGroup):
    in_menu = State()
    