from typing import Any, Coroutine, List, Union

from axsqlalchemy.repository import BaseRepository

from ..models import AbstractUserModel
from ..schemas import User as UserSchemas


class UserReposity(BaseRepository):
    DBModel = AbstractUserModel
    IModel = UserSchemas
    OModel = UserSchemas

    async def add(self, obj: IModel) -> Union[IModel, None]:
        res = await super().add(obj)

        if res:
            return self.OModel.from_orm(res)

    async def get(self, id: int) -> AbstractUserModel:
        return await super().get(*[id])
