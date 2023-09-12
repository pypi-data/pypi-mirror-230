from dataclasses import dataclass
from typing import Any, List, Type, TypeVar, Union

from aiogram import Bot

from axaiogram.static import MessagesGroup

from .template_group import TemplateGroup
from .template_parser import TemplateParser


@dataclass
class MessagesCollection:
    _groups = {}
    _lang_code: str = "en"

    def __getattribute__(self, __name: str) -> Any:
        try:
            return super().__getattribute__(__name)

        except AttributeError:
            if __name not in self._groups:

                cls = self.__class__.__annotations__.get(__name)

                if cls and issubclass(MessagesGroup, cls):
                    self._groups[__name] = cls.from_file(self._lang_code)
                else:
                    raise

            return self._groups[__name]


@dataclass
class TemplatesCollection:
    langs: tuple[str] = ("en",)
    _groups = None

    def __getattribute__(self, __name: str) -> Any:
        try:
            return super().__getattribute__(__name)

        except AttributeError:
            if not self._groups:
                self._groups = {}

            if __name not in self._groups:
                cls = self.__class__.__annotations__.get(__name)

                if cls is not None and issubclass(TemplateGroup, cls):
                    self._groups[__name] = cls.load(self.langs)

                else:
                    raise

            return self._groups[__name]


TTemplateCollection = TypeVar("TTemplateCollection", bound=TemplatesCollection)
TMessagesCollection = TypeVar("TMessagesCollection", bound=MessagesCollection)


class TemplatesHolder:
    def __init__(
        self,
        bot: Bot,
        tc: TemplatesCollection,
        mc: MessagesCollection,
        lang_code: str = "en",
        chat_id: Union[int, None] = None,
    ) -> None:
        self.bot = bot
        self.lang_code = lang_code

        self.collection = tc
        self.msg_collection = mc

        self.chat_id = chat_id

    async def render(
        self,
        template_parser: TemplateParser,
        context: Union[dict, None] = None,
        **kwargs,
    ):
        if context is None:
            context = {}

        res = template_parser.render(
            self.lang_code,
            context={
                "mc": self.msg_collection,
            },
        )

        method = (
            self.bot.send_message
            if res.type_ == "text"
            else self.bot.__getattribute__(f"send_{res.type_}")
        )

        if not kwargs.get("chat_id"):
            kwargs["chat_id"] = self.chat_id

        return await method(**res.to_message_data(**kwargs))


class TemplateFactory:
    def __init__(
        self,
        bot: Bot,
        tc: Type[TTemplateCollection],
        mc: Type[TMessagesCollection],
        langs: Union[List[str], None] = None,
    ) -> None:

        if not langs:
            raise NotImplementedError("langs aren't set up")

        self.bot = bot
        self.langs: List[str] = langs

        self.msg_collection_type = mc
        self.temp_collection = tc(langs=self.langs)

        self._msg_collections = {}

    def get_template(
        self, lang_code: str, chat_id: Union[int, None] = None
    ) -> TemplatesHolder:

        if lang_code not in self.langs:
            raise NotImplementedError("Lang code not found")

        if lang_code not in self._msg_collections:
            self._msg_collections[lang_code] = self.msg_collection_type(
                _lang_code=lang_code
            )

        return TemplatesHolder(
            bot=self.bot,
            tc=self.temp_collection,
            mc=self._msg_collections[lang_code],
            lang_code=lang_code,
            chat_id=chat_id,
        )
