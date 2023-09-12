from typing import Any, Awaitable, Callable, Dict, Union

from aiogram import types
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import TelegramObject

from db.schemas import User as UserSchema

from ..templates import TemplateFactory


class TemplateMiddleWare(BaseMiddleware):
    def __init__(self, temp_factory: TemplateFactory, default_lang = 'en') -> None:
        self.temp_factory = temp_factory
        self.default_lang = default_lang
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user: Union[UserSchema, None] = data.get("user")

        if user is None:
            raise NotImplementedError("TemplateMiddleware needs user data!")

        lang_code = user.lang_code or self.default_lang
        chat_id = None

        if type(event) is types.Message:
            chat_id = event.chat.id
        elif type(event) is types.CallbackQuery and event.message:
            chat_id = event.message.chat.id

        data["temp"] = self.temp_factory.get_template(lang_code, chat_id)

        return await handler(event, data)
