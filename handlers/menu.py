from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart, Filter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardMarkup, \
    KeyboardButton

from db.query import add_user, get_user
from utils.create_url import Payment
from utils.vpn import MyClassOutlineVpn

router = Router()


class MainState(StatesGroup):
    support = State()


class Reg(Filter):
    async def __call__(self, message: Message) -> bool:
        if not await get_user(message.chat.id):
            await message.answer('Для регистрации нажмите /start!')
            return False
        return True


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await add_user(message.chat.id, message.chat.username)

    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Получить ключ", callback_data="get_key")],
            [InlineKeyboardButton(text="Инструкция", callback_data="instruction"),
             InlineKeyboardButton(text="Тех. Поддержка", callback_data="support")],
            [InlineKeyboardButton(text="Пожертвование", callback_data="donation")]
        ]
    )

    try:
        await message.edit_text('Привет!', reply_markup=markup)
    except TelegramBadRequest:
        await message.answer('Привет!', reply_markup=markup)


@router.callback_query(F.data.in_({"get_key", "instruction", "support", "back_menu", "donation"}))
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

        loading_message = await callback.message.edit_text('Подождите, загрузка...')

        async with MyClassOutlineVpn() as sess:
            if key := await sess.one_key_info(callback.message.chat.id):
                access_url = key[1]
            else:
                access_url = await sess.create_new_key(callback.message.chat.id)

            await loading_message.edit_text(
                text=f'Вот ваш ключ: `{access_url}`',
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=markup
            )

    if callback.data == "instruction":
        markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Назад", callback_data="back_menu")]])
        await callback.message.edit_text("Впн бот тебе в помощь бро", reply_markup=markup)

    if callback.data == "support":
        markup = ReplyKeyboardMarkup(
            resize_keyboard=True,
            keyboard=[[KeyboardButton(text="❌ Отмена ")]],
            one_time_keyboard=True
        )
        await callback.message.delete()
        await callback.message.answer("Напиши сообщение", reply_markup=markup)
        await state.set_state(MainState.support)

    if callback.data == 'donation':
        markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="50 ₽", url=Payment(sum=50).create_url)],
                [InlineKeyboardButton(text="100 ₽", url=Payment(sum=100).create_url)],
                [InlineKeyboardButton(text="250 ₽", url=Payment(sum=250).create_url)],
                [InlineKeyboardButton(text="500 ₽", url=Payment(sum=500).create_url)],
                [InlineKeyboardButton(text="Назад", callback_data="back_menu")]
            ]
        )
        await callback.message.edit_text("Выберите сумму поддержки.", reply_markup=markup)

    return None
