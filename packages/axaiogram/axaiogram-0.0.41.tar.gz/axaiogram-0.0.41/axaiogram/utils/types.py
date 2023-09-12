from dataclasses import dataclass
from aiogram import types


class CallbackQuery(types.CallbackQuery):
    message: types.Message


class CallbackDataQuery(CallbackQuery):
    data: str


@dataclass
class PaginatedMessage:
    cq: CallbackDataQuery
    user_message: types.Message
    loading: types.Message
    page: int = 1

