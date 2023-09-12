from abc import ABC, abstractmethod
from typing import Any, Awaitable, Callable, Dict

from aiogram import types
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup
from aiogram.types import TelegramObject
from axsqlalchemy.uow import UOWFactory
from db.repository.collection import RepoCollector

from axaiogram.handlers.frozen_handler import FrozenHandler


class BaseUserAuthHandlers(ABC):
    async def require(self, chat_id: int, state: FSMContext, data: dict):
        raise NotImplementedError


class UseHandlerUserAuthMiddleware(BaseMiddleware):
    def __init__(
        self,
        uowf: UOWFactory[RepoCollector],
        auth_handlers_group: BaseUserAuthHandlers,
        auth_states_group: StatesGroup,
    ) -> None:
        self.uowf = uowf
        self.auth_handlers = auth_handlers_group
        self.auth_states_group = auth_states_group

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: types.Message,
        data: Dict[str, Any],
    ) -> Any:
        if not hasattr(event, "from_user"):
            raise NotImplementedError(
                f"`{self.__class__.__name__}` can't handler event type of `{type(event)}`"
            )

        assert event.from_user is not None
        user_id = event.from_user.id
        data["user_id"] = user_id

        async with self.uowf() as uow:
            user = await uow.repo.user.get(user_id)

        if not user or not bool(user.is_active):
            state: FSMContext = data["state"]

            current_state = await state.get_state()
            print(
                f"state in auth states group: {current_state in self.auth_states_group.__states__}"
            )

            if current_state not in self.auth_states_group.__states__:
                await FrozenHandler(handler, event, data).freeze(state)

                return await self.auth_handlers.require(user_id, state, data)

        data["user"] = user

        return await handler(event, data)
