from abc import ABC, abstractclassmethod
from typing import Any, List, Type, Union

from pydantic import BaseModel

from .template_parser import TemplateParser


class TemplateGroup(ABC, BaseModel):
    base_path: str

    @property
    def template_parser(self) -> Type[TemplateParser]:
        raise NotImplementedError

    @abstractclassmethod
    def load(cls, langs: List[str]) -> "TemplateGroup":

        raise NotImplementedError

    def __getattribute__(self, __name: str) -> Union[TemplateParser, Any]:
        obj = super().__getattribute__(__name)

        if __name in self.__class__.__fields__.keys():
            return self.template_parser(base_formats=obj)

        return obj
