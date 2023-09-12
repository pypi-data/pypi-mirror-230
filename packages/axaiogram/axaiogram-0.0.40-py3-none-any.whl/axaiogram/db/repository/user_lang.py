from typing import Any, Coroutine, List, Union

from axsqlalchemy.repository import BaseRepository

from ..models import AbstractUserLanguageModel
from ..schemas import UserLang as UserLangSchemas


class UserLangReposity(BaseRepository):
    DBModel = AbstractUserLanguageModel
    IModel = UserLangSchemas
    OModel = UserLangSchemas

    async def add(self, obj: IModel) -> Any:
        return await super().add(obj)

    async def get(self, id: int) -> Any:
        return await super().get(id)
