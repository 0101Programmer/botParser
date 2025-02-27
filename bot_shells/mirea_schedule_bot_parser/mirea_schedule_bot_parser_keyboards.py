from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# стартовая клавиатура
start_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Расписание на сегодня")],
        [KeyboardButton(text="Расписание на конкретную дату")],
        [KeyboardButton(text="Расписание на неделю")]
    ],
    resize_keyboard=True  # Клавиатура подстраивается под размер экрана
)

# остановка машины состояний
fsm_cmd_cancel_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Вернуться в главное меню")],
    ],
    resize_keyboard=True  # Клавиатура подстраивается под размер экрана
)