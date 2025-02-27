from dotenv import load_dotenv
import os

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
import asyncio


load_dotenv()
bot_token = os.getenv('BOT_TOKEN')

# Инициализация бота с использованием DefaultBotProperties
bot = Bot(
    token=bot_token,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# Обработчик команды /start
@dp.message(Command('start'))
async def send_welcome(message: types.Message):
    await message.answer("<b>Привет!</b> Это <i>HTML</i> текст.")

# Обработчик текстовых сообщений
@dp.message()
async def echo(message: types.Message):
    await message.answer(message.text)

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
