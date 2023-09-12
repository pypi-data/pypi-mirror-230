from typing import Callable, Optional, TypeVar, Iterable
from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder


TObj = TypeVar('TObj')


def objs2inline(
    objs: Iterable[TObj], 
    getter: Callable[[TObj], types.InlineKeyboardButton]
) -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    for obj in objs:
        builder.add(getter(obj))

    builder.adjust(1)

    return builder.as_markup()


def ibutton(text: str, data: Optional[str] = None, url: Optional[str] = None) -> types.InlineKeyboardButton:
    return types.InlineKeyboardButton(
        text=text,
        callback_data=data,
        url=url,
    )

