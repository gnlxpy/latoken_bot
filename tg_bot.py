import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart
from dotenv import load_dotenv
from ai_query import ai_answer_query

load_dotenv()


TOKEN = os.getenv('TG_TOKEN')

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("Привет 👋 \nЯ отвечу на все вопросы о компании Latoken и даже проверю твои знания\nПриступим? 🤖")


@dp.message()
async def handle_message(message: Message):
    """
    Обработчик всех входящих сообщений
    """
    tg_id = message.from_user.id
    text = message.text

    answer = await ai_answer_query(text, tg_id)
    await message.answer(answer)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
