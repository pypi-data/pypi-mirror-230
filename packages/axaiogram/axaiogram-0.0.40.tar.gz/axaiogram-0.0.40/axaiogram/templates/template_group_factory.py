import inspect
from typing import Type, TypeVar

from templates.renderers.md.template_group import MarkdownTemplateGroup
from templates.template_group import TemplateGroup

TTemplateGroup = TypeVar("TTemplateGroup", bound=TemplateGroup)


class TemplateGroupFactory:
    def get_template_group(self, cls: Type[TTemplateGroup]) -> TemplateGroup:
        if cls.base_path.endswith(".md") and inspect.isclass(cls):

            class ImplementedTemplateGroup(cls, MarkdownTemplateGroup):
                ...

            return ImplementedTemplateGroup

        raise NotImplementedError
