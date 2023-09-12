from axsqlalchemy.uow import BaseRepoCollector

from .user import UserReposity
from .user_lang import UserLangReposity


class RepoCollector(BaseRepoCollector):
    user: UserReposity
    user_lang: UserLangReposity
