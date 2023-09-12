from abc import ABC, abstractmethod
from typing import Dict, Union

from .template_message import TemplateMessage


class TemplateParser(ABC):
    def __init__(self, base_formats: Dict[str, str]) -> None:
        """
        base_formats: Dict[lang_code: "not parsed text"]
        """
        self.base_formats = base_formats

    def _format_text(self, text: str, context: dict) -> str:
        return text.format(**context)

    @abstractmethod
    def render(
        self,
        lang_code: str,
        context: Union[dict, None] = None,
        is_prerender: bool = False,
    ) -> TemplateMessage:
        raise NotImplementedError
