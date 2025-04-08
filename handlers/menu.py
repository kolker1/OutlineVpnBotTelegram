from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart, Filter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardMarkup, \
    KeyboardButton

from db.query import add_user, get_user
from main import bot
from utils.create_url import Payment
from utils.vpn import MyClassOutlineVpn

router = Router()


class MainState(StatesGroup):
    support = State()


class Registration(Filter):
    async def __call__(self, message: Message) -> bool:
        if not await get_user(message.chat.id):
            await message.answer('⚠️ Для регистрации нажмите */start*!', parse_mode=ParseMode.MARKDOWN)
            return False
        return True


class CheckPrivateChatMessage(Filter):
    async def __call__(self, message: Message) -> bool:
        if message.chat.type != "private" and message.text == '/start':
            await message.answer('⚠️ Бот доступен только для использования в личном чате!')
            return False
        return True


class CheckPrivateChatCallbackQuery(Filter):
    async def __call__(self, callback: CallbackQuery) -> bool:
        if callback.message.chat.type != "private":
            await callback.message.answer('⚠️ Бот доступен только для использования в личном чате!', show_alert=True)
            return False
        return True


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await add_user(message.chat.id, message.chat.username)

    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔑 Получить ключ", callback_data="get_key")],
            [InlineKeyboardButton(text="📖 Инструкция", callback_data="instruction"),
             InlineKeyboardButton(text="🛠️ Тех. Поддержка", callback_data="support")],
            [InlineKeyboardButton(text="💰 Пожертвование", callback_data="donation")]
        ]
    )

    text = (
        '👋 Рад вас видеть!\n\n'
        '🚀 Именно в этом телеграмм боте вы можете получить бесплатный ключ для OutlineVpn.\n'
        '🖥️ OutlineVpn можно использовать как на компьютере, так и на телефоне.\n'
        '🌍 OutlineVpn надежный и имеет очень быстрые сервера с помощью которых вы можете выходить спокойно в интернет на заблокированные сайты в вашей стране.\n\n'
        '⬇️ Для получения ключа нажмите на кнопку ниже — *Получить ключ* ⬇️'
    )

    try:
        await message.edit_text(text, reply_markup=markup, parse_mode=ParseMode.MARKDOWN)
    except TelegramBadRequest:
        if message.caption and message.caption.startswith('🌐 Инструкция по подключению к VPN:'):
            await message.delete()
        await message.answer(text, reply_markup=markup, parse_mode=ParseMode.MARKDOWN)


@router.callback_query(F.data.in_({"get_key", "instruction", "support", "back_menu", "donation"}))
async def click(callback: CallbackQuery, state: FSMContext) -> None:
    if callback.data == "back_menu":
        return await cmd_start(callback.message)

    if callback.data == 'get_key':
        markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="📖 Инструкция", callback_data="instruction")],
                [InlineKeyboardButton(text="⏪ Назад", callback_data="back_menu")]
            ]
        )

        loading_message = await callback.message.edit_text('⏳ Пожалуйста, подождите немного...')

        async with MyClassOutlineVpn() as sess:
            if key := await sess.one_key_info(callback.message.chat.id):
                access_url = key[1]
            else:
                access_url = await sess.create_new_key(callback.message.chat.id)

            await loading_message.edit_text(
                text=f'🔑 Вот ваш ключ с помощью которого вы можете подключить себе VPN:\n\n'
                     f'`{access_url}#🚀@outline_master_bot — ваш лучший и самый быстрый VPN!`.\n\n'
                     f'📖 Если вы не знаете как сделать это, то кликните на инструкцию.',
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=markup
            )

    if callback.data == "instruction":
        markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text='📱 Android',
                                      url='https://play.google.com/store/apps/details?id=org.outline.android.client&hl=ru'),
                 InlineKeyboardButton(text='📱 IOS', url='https://apps.apple.com/ru/app/outline-app/id1356177741'),
                 InlineKeyboardButton(text='🖥 ПК', url='https://outline-vpn.com/')],
                [InlineKeyboardButton(text='⏪ Назад', callback_data='back_menu')]])
        await callback.message.delete()

        await bot.send_video(
            caption='''
🌐 Инструкция по подключению к VPN:

1. Во-первых, скачайте приложение `Outline`, доступное для всех устройств: iPhone, Android, Mac, Windows, Linux.

2. Во-вторых, нажмите на плюсик в правом верхнем углу и вставьте ключ. 🔑

3. Затем нажмите кнопку `Подключиться`, и всё готово! 🚀
        ''',
            reply_markup=markup,
            parse_mode=ParseMode.MARKDOWN,
            chat_id=callback.message.chat.id,
            video='BAACAgIAAxkDAAIB1mf1cxOJwP_O9_pGb_E9pITEgpNJAAKoawACLeGxSxAK_cgr0DGuNgQ'
        )

    if callback.data == "support":
        markup = ReplyKeyboardMarkup(
            resize_keyboard=True,
            keyboard=[[KeyboardButton(text="🚫 Отмена")]],
            one_time_keyboard=True
        )
        await callback.message.delete()
        await callback.message.answer("❓ Напишите вопрос:", reply_markup=markup)
        await state.set_state(MainState.support)

    if callback.data == 'donation':
        markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="50 ₽", url=Payment(sum=50).create_url)],
                [InlineKeyboardButton(text="100 ₽", url=Payment(sum=100).create_url)],
                [InlineKeyboardButton(text="250 ₽", url=Payment(sum=250).create_url)],
                [InlineKeyboardButton(text="500 ₽", url=Payment(sum=500).create_url)],
                [InlineKeyboardButton(text="⏪ Назад", callback_data="back_menu")]
            ]
        )
        await callback.message.edit_text("💰 Выберите сумму поддержки:", reply_markup=markup)

    return None


router_all_messages = Router()


@router_all_messages.message()
async def all_message(message: Message) -> None:
    await message.answer('⚠️ Чтобы получить VPN нажмите /start!')
