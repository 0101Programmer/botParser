from aiogram.fsm.state import StatesGroup, State

class TodaySchedule(StatesGroup):
    group_number = State()

class ParticularDateSchedule(StatesGroup):
    group_number = State()
    date = State()