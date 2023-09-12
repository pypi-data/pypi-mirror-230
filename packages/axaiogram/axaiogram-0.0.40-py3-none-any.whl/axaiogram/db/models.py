import sqlalchemy as sa
from axsqlalchemy.model import Base, BaseTableAt


class AbstractUserModel(BaseTableAt):
    __abstract__ = True

    id = sa.Column(sa.BigInteger, primary_key=True, index=True)
    username = sa.Column(sa.String(length=256), nullable=True)
    firstname = sa.Column(sa.String(length=456), nullable=False)
    secondname = sa.Column(sa.String(length=456), nullable=True)
    is_active = sa.Column(sa.Boolean, nullable=False, default=True)


class AbstractUserLanguageModel(BaseTableAt):
    __abstract__ = True

    id = sa.Column(sa.BigInteger, primary_key=True, index=True)
    lang_code = sa.Column(sa.String(length=256), nullable=True)


class AbstractUserWithEmailModel(AbstractUserModel):
    __abstract__ = True

    email = sa.Column(sa.String, nullable=False)


__all__ = [
    "Base",
    "AbstractUserModel",
    "AbstractUserWithEmailModel",
]
