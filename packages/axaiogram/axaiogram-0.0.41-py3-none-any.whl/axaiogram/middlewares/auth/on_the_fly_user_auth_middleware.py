from typing import Any, Awaitable, Callable, Dict, Union

from aiogram import types
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import TelegramObject
from axsqlalchemy.uow import UOWFactory
from db.repository.collection import RepoCollector


class OnTheFlyUserAuthMiddleware(BaseMiddleware):
    def __init__(self, uowf: UOWFactory[RepoCollector]) -> None:
        self.uowf = uowf
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: Union[TelegramObject, types.Message],
        data: Dict[str, Any],
    ) -> Any:
        if hasattr(event, "from_user"):
            user_data: types.User = getattr(event, "from_user")

            if user_data:
                chat_id = user_data.id
                async with self.uowf() as uow:
                    user = await uow.repo.user.get(chat_id)

                    if not user:
                        user = await uow.repo.user.add(
                            uow.repo.user.IModel(
                                id=user_data.id,
                                username=user_data.username,
                                firstname=user_data.first_name,
                                secondname=user_data.last_name,
                                lang_code=data.get("lang_code"),
                            )
                        )

                data["user"] = user

        return await handler(event, data)
