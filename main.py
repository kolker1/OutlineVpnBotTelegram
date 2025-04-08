import asyncio
from aiogram import Bot, Dispatcher
from config.loading import config

bot = Bot(token=config.BOT_TOKEN.get_secret_value())
dp = Dispatcher()


def activate():
    from handlers.menu import router as menu_router, router_all_messages
    from handlers.support import router as support_router
    from handlers.admin import router as admin_router

    from handlers.menu import (
        Registration,
        CheckPrivateChatMessage,
        CheckPrivateChatCallbackQuery
    )

    dp.include_router(menu_router)
    dp.include_router(support_router)
    dp.include_router(admin_router)
    dp.include_router(router_all_messages)

    dp.message.filter(CheckPrivateChatMessage())
    dp.callback_query.filter(CheckPrivateChatCallbackQuery())
    dp.update.filter(Registration())


async def main():
    activate()
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
