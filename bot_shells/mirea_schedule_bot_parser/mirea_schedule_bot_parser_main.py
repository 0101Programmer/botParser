import asyncio
import logging
import os
from datetime import datetime
from pathlib import Path

from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove, FSInputFile
from dotenv import load_dotenv

from bot_shells.mirea_schedule_bot_parser.mirea_schedule_bot_parser_fsm_classes import TodaySchedule, ParticularDateSchedule
from bot_shells.mirea_schedule_bot_parser.mirea_schedule_bot_parser_keyboards import start_kb, fsm_cmd_cancel_kb
from bot_shells.mirea_schedule_bot_parser.mirea_schedule_bot_parser_tools import group_number_validator, date_validator
from parser_classes.mirea_schedule_parser import MireaScheduleParser


logging.basicConfig(level=logging.INFO)

load_dotenv()
bot_token = os.getenv('BOT_TOKEN')

# Инициализация бота с использованием DefaultBotProperties
bot = Bot(
    token=bot_token,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# -----------------------------------------------------------------------------
# Обработчик команды /start
# -----------------------------------------------------------------------------
@dp.message(Command('start'))
async def send_welcome(message: types.Message):
    await message.answer("<b>Привет!</b> Это <i>бот для парсинга расписания с сайта МИРЭА</i>.\n"
                         "Пожалуйста, выберите необходимое действие",
                         reply_markup=start_kb)
# -----------------------------------------------------------------------------
# "Расписание на сегодня"
# -----------------------------------------------------------------------------
@dp.message(lambda message: message.text == "Расписание на сегодня", StateFilter(None))
async def handle_today_schedule(message: types.Message, state: FSMContext):
    await message.answer("Введите номер своей группы в формате <i>АБВГ-01-24</i>",
                         reply_markup=ReplyKeyboardRemove())
    # Устанавливаем пользователю состояние "вводит название группы"
    await state.set_state(TodaySchedule.group_number)

# обработка введённого номера группы:

@dp.message(TodaySchedule.group_number)
async def fsm_group_choice(message: types.Message, state: FSMContext):
    if message.text == "Вернуться в главное меню":
        await state.clear()
        await message.answer(text="Действие отменено", reply_markup=start_kb)
    elif group_number_validator(message.text):
        await message.answer(text="Пожалуйста, ожидайте")
        await state.update_data(chosen_group=message.text)
        group_data = await state.get_data()
        schedule_parser = MireaScheduleParser()
        schedule_img = schedule_parser.datetime_now_schedule_page_parser(group_data['chosen_group'], f"{Path(__file__).parents[2]}/media/mirea_schedule_parser_media/")
        schedule_img_path = f"{Path(__file__).parents[2]}/media/mirea_schedule_parser_media/{schedule_img}"
        # Создание объекта FSInputFile
        photo_input_file = FSInputFile(schedule_img_path)
        # Получение текущего времени
        current_time = datetime.now()
        # Форматирование текущего времени
        formatted_current_time = current_time.strftime("%Y-%m-%d %H:%M")
        await message.answer_photo(photo_input_file, caption=f"Расписание для группы <u>{group_data['chosen_group']}</u> "
                                                             f"на <u>{formatted_current_time}</u>\n"
                                                             f"(если расписание отобразилось некорректно, пожалуйста, "
                                                             f"попробуйте сделать запрос ещё раз)",
                                   reply_markup=start_kb)
        # удаляем отправленный скриншот
        try:
            schedule_img_path = Path(schedule_img_path)
            # Удаление файла
            schedule_img_path.unlink()
            logging.info(f"Скриншот '{schedule_img_path}' удален.")
        except FileNotFoundError:
            logging.info(f"Скриншот '{schedule_img_path}' не существует.")
        except Exception as e:
            logging.info(f"Ошибка при удалении скриншота '{schedule_img_path}': {e}")
        await state.clear()
    else:
        await message.answer(text="Введён некорректный формат.\n"
                                  "Введите номер своей группы в формате <i>АБВГ-01-24</i>",
                             reply_markup=fsm_cmd_cancel_kb)

# -----------------------------------------------------------------------------
# "Расписание на конкретную дату"
# -----------------------------------------------------------------------------
@dp.message(lambda message: message.text == "Расписание на конкретную дату", StateFilter(None))
async def handle_particular_date_schedule(message: types.Message, state: FSMContext):
    await message.answer("Введите номер своей группы в формате <i>АБВГ-01-24</i>",
                         reply_markup=ReplyKeyboardRemove())
    # Устанавливаем пользователю состояние "вводит название группы"
    await state.set_state(ParticularDateSchedule.group_number)

# обработка введённого номера группы:

@dp.message(ParticularDateSchedule.group_number)
async def fsm_group_choice(message: types.Message, state: FSMContext):
    if message.text == "Вернуться в главное меню":
        await state.clear()
        await message.answer(text="Действие отменено", reply_markup=start_kb)
    elif group_number_validator(message.text):
        await message.answer(text="Введите дату, на которую хотите получить расписание в формате <i>Месяц, ГГГГ, Д</i>\n"
                                  "(например: Март, 2025, 4)")
        await state.update_data(chosen_group=message.text)
        # Устанавливаем пользователю состояние "вводит дату"
        await state.set_state(ParticularDateSchedule.date)

    else:
        await message.answer(text="Введён некорректный формат.\n"
                                  "Введите номер своей группы в формате <i>АБВГ-01-24</i>",
                             reply_markup=fsm_cmd_cancel_kb)

# обработка введённой даты:

@dp.message(ParticularDateSchedule.date)
async def fsm_date_choice(message: types.Message, state: FSMContext):
    if message.text == "Вернуться в главное меню":
        await state.clear()
        await message.answer(text="Действие отменено", reply_markup=start_kb)

    elif date_validator(message.text):
        await message.answer(text="Пожалуйста, ожидайте")
        await state.update_data(chosen_date=message.text)
        got_data = await state.get_data()
        schedule_parser = MireaScheduleParser()
        schedule_img = schedule_parser.particular_date_schedule_parser(group_number=got_data['chosen_group'],
                                                                       required_date=got_data['chosen_date'],
                                                                         path_to_mirea_schedule_parser_media=
                                                                       f"{Path(__file__).parents[2]}/media/mirea_schedule_parser_media/")

        schedule_img_path = f"{Path(__file__).parents[2]}/media/mirea_schedule_parser_media/{schedule_img}"
        # Создание объекта FSInputFile, для того, чтобы отправить изображение
        photo_input_file = FSInputFile(schedule_img_path)
        await message.answer_photo(photo_input_file,
                                   caption=f"Расписание для группы:\n<u>{got_data['chosen_group']}</u>\nна дату:\n"
                                           f"<u>{got_data['chosen_date']}</u>\n"
                                           f"(если расписание отобразилось некорректно, пожалуйста, "
                                           f"попробуйте сделать запрос ещё раз)",
                                   reply_markup=start_kb)
        try:
            schedule_img_path = Path(schedule_img_path)
            # Удаление скриншота после отправки
            schedule_img_path.unlink()
            logging.info(f"Скриншот '{schedule_img_path}' удален.")
        except FileNotFoundError:
            logging.info(f"Скриншот '{schedule_img_path}' не существует.")
        except Exception as e:
            logging.info(f"Ошибка при удалении скриншота '{schedule_img_path}': {e}")
        await state.clear()

    else:
        await message.answer(text="Введён некорректный формат.\n"
                                  "Введите дату в формате <i>Месяц, ГГГГ, Д</i>",
                             reply_markup=fsm_cmd_cancel_kb)


# -----------------------------------------------------------------------------
# Обработчик всех сообщений
# -----------------------------------------------------------------------------
@dp.message()
async def all_messages(message: types.Message):
    await message.answer("Введите команду /start, чтобы начать")
# -----------------------------------------------------------------------------
# Запуск бота
# -----------------------------------------------------------------------------
async def main():
    await dp.start_polling(bot, allowed_updates=[])

if __name__ == '__main__':
    asyncio.run(main())