from dataclasses import dataclass
from enum import Enum
from typing import Union

from aiogram import Bot, types
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


class TemplateTextType:
    TEXT = "text"
    CAPTION = "caption"


class MessageTemplateTypeEnum:
    MESSAGE = "text"
    AUDIO = "audio"
    DOCUMENT = "document"
    PHOTO = "photo"
    STICKER = "sticker"
    VIDEO = "video"
    VIDEO_NOTE = "video_note"
    VOICE = "voice"
    CONTACT = "contact"


class TemplateKeyboardTypeEnum:
    INLINE = "inline"
    REPLY = "reply"


@dataclass
class TemplateMessage:
    type_: str
    id: str | None = None
    parse_mode: str | None = None

    text: Union[str, None] = None
    text_type: str = TemplateTextType.TEXT

    content_data: Union[dict, None] = None
    keyboard: Union[
        InlineKeyboardBuilder,
        ReplyKeyboardBuilder,
        types.ReplyKeyboardRemove,
        None,
    ] = None

    def to_message_data(self, **kwargs) -> dict:
        data = {
            self.text_type: self.text,
            "parse_mode": self.parse_mode,
            **(self.content_data or {}),
            **kwargs,
        }
        if type(self.keyboard) is not types.ReplyKeyboardRemove:
            data["reply_markup"] = self.keyboard.as_markup()
        else:
            data["reply_markup"] = self.keyboard

        return data
