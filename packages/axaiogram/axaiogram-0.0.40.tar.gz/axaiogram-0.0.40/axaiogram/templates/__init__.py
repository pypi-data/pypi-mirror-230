from typing import Union

from .collection import (MessagesCollection, MessagesGroup, TemplateFactory,
                         TemplateGroup, TemplatesCollection, TemplatesHolder)

TItem = Union[dict, str]

__all__ = [
    "TemplateGroup",
    "MessagesCollection",
    "TemplateFactory",
    "TemplatesHolder",
    "MessagesGroup",
    "TemplatesCollection",
    "TItem",
]
