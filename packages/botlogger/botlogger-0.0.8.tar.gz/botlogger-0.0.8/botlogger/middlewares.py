from typing import Any, Callable, Dict, Awaitable

from aiogram import types

try:
    from aiogram.dispatcher.middlewares import BaseMiddleware
except ImportError:
    from aiogram import BaseMiddleware

from .logger import logger


class MessageLogger(BaseMiddleware):
    logger = logger

    async def on_pre_process_message(self, message: types.Message, data: dict) -> Any:
        await self.logger.send_message(data=message, text=message.text)

    async def on_pre_process_callback_query(self, query: types.CallbackQuery, data: dict):
        await self.logger.send_message(data=query, text=query.data)

    async def on_post_process_callback_query(self, query: types.CallbackQuery, data: dict):
        await self.logger.send_message(data=query, text=query.data, answer=query.message.text)

    async def on_post_process_message(self, message: types.Message, data: dict) -> Any:
        await self.logger.send_message(data=message, text=message.text, answer=message.reply_to_message.text)


class MessageV3(BaseMiddleware):
    logger = logger

    async def __call__(
            self,
            handler: Callable[[types.Message, Dict[str, Any]], Awaitable[Any]],
            event: types.Message,
            data: Dict[str, Any]
    ) -> Any:
        await self.logger.send_message(data=event, text=event.text)
        return await handler(event, data)


class CallbackQueryV3(BaseMiddleware):
    logger = logger

    async def __call__(
            self,
            handler: Callable[[types.CallbackQuery, Dict[str, Any]], Awaitable[Any]],
            event: types.CallbackQuery,
            data: Dict[str, Any]
    ) -> Any:
        await self.logger.send_message(data=event, text=event.data)
        return await handler(event, data)
