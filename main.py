import asyncio
import logging
from typing import Callable, Any, Awaitable

from aiogram import Bot, Dispatcher, BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from aiohttp import ClientError

from config.loading import config

bot = Bot(token=config.BOT_TOKEN.get_secret_value())
dp = Dispatcher()
logger = logging.getLogger()


class ErrorMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: dict[str, Any]
    ) -> Any:
        try:
            return await handler(event, data)
        except ClientError as e:
            logger.error(f"Connection error: {e}", exc_info=True)
            if isinstance(event, (Message, CallbackQuery)):
                try:
                    await event.answer("⚠️ Ошибка соединения с сервером. Попробуйте позже.")
                except Exception as send_error:
                    logger.error("Failed to send error message:", exc_info=send_error)
            return False

        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            if isinstance(event, Message):
                await event.answer("⚠️ Произошла непредвиденная ошибка")
            elif isinstance(event, CallbackQuery) and event.message:
                await event.message.answer("⚠️ Ошибка при обработке запроса")
            return False


def activate():
    from handlers.menu import router as menu_router, router_all_messages
    from handlers.support import router as support_router
    from handlers.admin import router as admin_router

    from handlers.menu import (
        Registration,
        CheckPrivateChatMessage,
        CheckPrivateChatCallbackQuery
    )
    dp.update.middleware(ErrorMiddleware())

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
