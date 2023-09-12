from typing import Callable, Union

from aiogram import types
from aiogram.fsm.context import FSMContext


class FrozenHandler:
    _state_key = "frozen_handler"

    def __init__(
        self, handler: Callable, event: types.TelegramObject, data: dict
    ) -> None:
        self.handler = handler
        self.event = event
        self.data = data

    async def freeze(self, state: FSMContext) -> None:
        data = await state.get_data()

        await state.set_data(
            {
                self._state_key: self,
                **data,
            }
        )

    async def delete(self, state: FSMContext) -> None:
        data = await state.get_data()

        await state.set_data(
            {
                self._state_key: None,
                **data,
            }
        )

    @classmethod
    async def get(cls, state: FSMContext) -> Union["FrozenHandler", None]:
        data = await state.get_data()

        return data.get(cls._state_key)
