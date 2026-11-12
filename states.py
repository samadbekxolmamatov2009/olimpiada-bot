from aiogram.fsm.state import State, StatesGroup


class Registration(StatesGroup):
    full_name = State()
    district = State()
    school = State()
    grade = State()
    parent_phone = State()


class AdminRegistration(StatesGroup):
    full_name = State()
    district = State()
    school = State()
    grade = State()
    parent_phone = State()
