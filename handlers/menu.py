from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardMarkup, \
    KeyboardButton

from utils.vpn import MyClassOutlineVpn

router = Router()


class MainState(StatesGroup):
    support = State()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Получить ключ", callback_data="get_key")],
            [InlineKeyboardButton(text="Мой ключ", callback_data="my_key")],
            [InlineKeyboardButton(text="Инструкция", callback_data="instruction")],
            [InlineKeyboardButton(text="Тех. Поддержка", callback_data="support")]
        ]
    )

    try:
        await message.edit_text('Привет!', reply_markup=markup)
    except TelegramBadRequest:
        await message.answer('Привет!', reply_markup=markup)


@router.callback_query(F.data.in_({"get_key", "my_key", "instruction", "support", "back_menu"}))
async def click(callback: CallbackQuery, state: FSMContext) -> None:
    if callback.data == "back_menu":
        return await cmd_start(callback.message)

    if callback.data == 'get_key':
        markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Инструкция", callback_data="instruction")],
                [InlineKeyboardButton(text="Назад", callback_data="back_menu")]
            ]
        )

        async with MyClassOutlineVpn() as sess:
            if not await sess.one_key_info(callback.message.chat.id):
                key = await sess.create_new_key(callback.message.chat.id)
                await callback.message.edit_text(text=f'Вот ваша ссылка `{key}`', parse_mode=ParseMode.MARKDOWN)
            else:
                await callback.answer(
                    text='У вас уже есть ключ, зайдите во вкладку мой ключ для повторного просмотра',
                    show_alert=True
                )

    if callback.data == "instruction":
        await callback.message.edit_text("Впн бот тебе в помощь бро", reply_markup=markup)

    if callback.data == "my_key":
        markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Назад", callback_data="back_menu")]
            ]
        )
        async with MyClassOutlineVpn() as sess:
            key = await sess.one_key_info(callback.message.chat.id)

        if key:
            await callback.message.edit_text(
                f"Вот твой ключ: `{key[1]}`",
                reply_markup=markup,
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await callback.answer(text='Ниту', show_alert=True)

    if callback.data == "support":
        markup = ReplyKeyboardMarkup(
            resize_keyboard=True,
            keyboard=[[KeyboardButton(text="❌ Отмена ❌")]],
            one_time_keyboard=True
        )
        await callback.message.delete()
        await callback.message.answer("Напиши сообщение", reply_markup=markup)
        return await state.set_state(MainState.support)
