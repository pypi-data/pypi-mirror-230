from typing import Any

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