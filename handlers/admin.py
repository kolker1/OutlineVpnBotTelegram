from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramForbiddenError
from aiogram.filters import Command, Filter, CommandObject
from aiogram.types import Message

from db.query import get_user
from main import bot

router = Router()


class AdminFilter(Filter):
    def __init__(self):
        self.allowed_ids = 1225032041

    async def __call__(self, message: Message):
        return message.from_user.id == self.allowed_ids


@router.message(Command('write_user'), AdminFilter())
async def write_user(message: Message, command: CommandObject):
    if not command.args:
        return await message.answer("Напишите что-то.")

    try:
        chat_id = int(command.args.split()[0])
        text = command.args.split()[1:]

        if not text:
            raise ValueError

    except ValueError:
        return await message.answer("В ответе должен быть chat\\_id, а потом текст.")

    if await get_user(chat_id):
        try:
            await bot.send_message(chat_id, f"*🛠️ Ответ от Тех.Поддержки:*\n\n{' '.join(text)}",
                                   parse_mode=ParseMode.MARKDOWN)
            await message.answer(f'Ответ был отправлен пользователю - {chat_id}!')
        except TelegramForbiddenError:
            await message.answer("Бот заблокирован у пользователя.")
    else:
        await message.answer('Такого пользователя не существует.')

    return None


@router.message(Command('learn_id'), AdminFilter())
async def write_user(message: Message, command: CommandObject):
    if not command.args:
        return await message.answer("Напишите что-то.")

    if user := await get_user(username=command.args):
        await message.answer(f'ID: `{user.chat_id}`.', parse_mode=ParseMode.MARKDOWN)
    else:
        await message.answer('Такого пользователя не существует.')

    return None
