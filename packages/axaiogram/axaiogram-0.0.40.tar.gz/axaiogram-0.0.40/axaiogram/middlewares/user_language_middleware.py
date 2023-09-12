from typing import Any, Awaitable, Callable, Dict, Union

from aiogram import types
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import TelegramObject
from axsqlalchemy.uow import TRepoCollector, UOWFactory

from axaiogram.db.repository.collection import RepoCollector
from axaiogram.handlers.frozen_handler import FrozenHandler

from ..handlers.user import UserLanguageSetupHandlers


class UserLanguageMiddleware(BaseMiddleware):
    def __init__(
        self, uowf: UOWFactory[TRepoCollector], handler: UserLanguageSetupHandlers
    ) -> None:
        self.handler = handler
        self.uowf = uowf
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: Union[TelegramObject, types.Message],
        data: Dict[str, Any],
    ) -> Any:
        user_data: types.User = data["event_from_user"]
        user_id = user_data.id

        async with self.uowf() as uow:
            user_lang_data = await uow.repo.user_lang.get(user_id)

        if not user_lang_data:
            state = data["state"]

            await FrozenHandler(handler, event, data).freeze(state)

            return await self.handler._require(user_id)

        data["lang_code"] = user_lang_data.lang_code

        return await handler(event, data)
