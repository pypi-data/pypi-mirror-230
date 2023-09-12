import math
from typing import Optional
from aiogram import types


class InlineKeyboardPaginator:
    def __init__(
        self, 
        page_size: int, 
        previous_symbol: str = '<-',
        next_symbol: str = '->',
        back_symbol: str = 'back',
        separator: str = "_page:",
    ) -> None:
        self.page_size = page_size
        self.previous_symbol = previous_symbol
        self.next_symbol = next_symbol
        self.separator = separator
        self.back_symbol = back_symbol

    def paginate(
        self, 
        keyboard: types.InlineKeyboardMarkup, 
        page: int,
        all_count: int,
        data: str = "",
        back_data: Optional[str] = None,
        back_symbol: Optional[str] = None,
    ) -> types.InlineKeyboardMarkup:
        if all_count < page:
            return keyboard

        final_page = math.ceil(all_count / self.page_size)
        pagination_row = []

        if page > 1:
            pagination_row.append(
               types.InlineKeyboardButton(
                    text=self.previous_symbol,
                    callback_data=f"{data}{self.separator}{(page - 1)}",
                )
            )
        if page < final_page:
            pagination_row.append(
               types.InlineKeyboardButton(
                    text=self.next_symbol,
                    callback_data=f"{data}{self.separator}{(page + 1)}",
                )
            )
        
        keyboard.inline_keyboard.append(pagination_row)

        if back_data is not None:
            keyboard.inline_keyboard.append(
                [
                   types.InlineKeyboardButton(
                        text=back_symbol or self.back_symbol,
                        callback_data=back_data,
                    )
                ]
            )
        
        return keyboard

