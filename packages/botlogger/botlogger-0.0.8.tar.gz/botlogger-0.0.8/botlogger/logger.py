import aiohttp
import loguru

from typing import Any
from .services import _get_user_photo_url, _get_user_profile_url


class Logger:
    bot_token: str
    url: str

    def __init__(self):
        self.logger = loguru.logger.opt(depth=1)

    async def _send_async_request(self, url, json_data) -> dict:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=json_data) as response:
                    response_json = await response.json()
                    if response_json.get('error'):
                        self.logger.error(response_json['error'])
                    return response_json
        except aiohttp.ClientConnectorError:
            self.logger.warning('Error connecting to data server')
            return dict()

    async def _send_message(self, user, profile_url, profile_photo, message_text, answer) -> None:
        json = {
            "bot_token": self.bot_token,
            "user_id": user.id,
            "user_first_name": user.first_name,
            "user_last_name": user.last_name,
            "user_full_name": user.full_name,
            "user_profile_url": profile_url,
            "user_photo_url": profile_photo,
            "text": message_text,
            "answer": answer
        }

        await self._send_async_request(f'{self.url}/api/v1/bot/{self.bot_token}/messages/', json)

    async def _send_log(self, text, importance) -> None:
        json = {
            "bot_token": self.bot_token,
            "importance": importance,
            "text": text
        }

        await self._send_async_request(f'{self.url}/api/v1/bot/{self.bot_token}/logs/', json)

    async def send_log(self, __message: str, *args: Any, **kwargs: Any) -> None:
        self.logger.info(__message, *args, **kwargs)
        await self._send_log(text=__message, importance=3)

    async def send_error(self, err: Exception, *args: Any, **kwargs: Any) -> None:
        text = f'{type(err).__name__}: {err}'
        self.logger.error(text, *args, **kwargs)
        await self._send_log(text=text, importance=1)

    async def send_message(self, data, text, answer=None, *args: Any, **kwargs: Any) -> None:
        self.logger.info(f'{data.from_user.full_name}/{data.from_user.id} - {text}', *args, **kwargs)

        photo_url = await _get_user_photo_url(data.from_user)
        profile_url = await _get_user_profile_url(data.from_user)

        await self._send_message(user=data.from_user, profile_url=profile_url,
                                 profile_photo=photo_url, message_text=text, answer=answer)

    def log_without_sending(self, __message: str, *args: Any, **kwargs: Any) -> None:
        self.logger.debug(__message, *args, **kwargs)


logger = Logger()
