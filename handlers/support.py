from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove, Message

from handlers.menu import cmd_start, MainState
from main import bot

router = Router()
SUPPORT_CHAT_ID = -1002481972506


@router.message(MainState.support)
async def support_func(message: Message, state: FSMContext):
    try:

        if message.text == "❌ Отмена ":
            await message.answer(
                "❌ Отменено ",
                reply_markup=ReplyKeyboardRemove()
            )
            return await cmd_start(message)

        if not message.text:
            await bot.copy_message(
                chat_id=SUPPORT_CHAT_ID,
                from_chat_id=message.chat.id,
                message_id=message.message_id,
                caption=f'{message.caption}\n\n'
                        f'ID: `{message.chat.id}`\n'
                        f'Username: `{message.chat.username}`',
                caption_entities=message.caption_entities
            )
        else:
            await bot.send_message(
                chat_id=SUPPORT_CHAT_ID,
                text=f'{message.text}\n\n'
                     f'Username: `{message.chat.username}`',
                entities=message.entities
            )

        await message.answer(
            "Ваш ответ был успешно передан технической поддержке! 📨",
            reply_markup=ReplyKeyboardRemove()
        )
        return await cmd_start(message)

    except Exception:
        await message.answer(
            "⚠️ Произошла ошибка при отправке. Пожалуйста, отправьте сообщение в тех. поддержку ещё раз!",
            reply_markup=ReplyKeyboardRemove()
        )

    finally:
        await state.clear()
