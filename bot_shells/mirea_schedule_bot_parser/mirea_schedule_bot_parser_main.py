import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from dotenv import load_dotenv


from bot_shells.mirea_schedule_bot_parser.mirea_schedule_bot_parser_keyboards import start_kb

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
                         "Пожалуйста, выбери необходимое действие",
                         reply_markup=start_kb)
# -----------------------------------------------------------------------------
# "Расписание на сегодня"
# -----------------------------------------------------------------------------
@dp.message(lambda message: message.text == "Расписание на сегодня")
async def handle_today_schedule(message: types.Message):
    await message.answer("Вы отправили команду!")
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
