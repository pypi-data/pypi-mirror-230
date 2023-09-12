from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union
from aiogram import Bot, Router
from axabc.db import AbstractUOWFactory, AbstractUOW


TUOWFactory = TypeVar('TUOWFactory', bound=AbstractUOWFactory)


class BaseHandlersGroup(ABC):
    __router: Union[None, Router] = None
    uow: Optional[AbstractUOW] = None

    def __init__(self, bot: Bot, uowf: Optional[TUOWFactory] = None) -> None:
        self.bot = bot
        self.uowf = uowf
        self.router = proxy_router.get_group_observed_router(self)
        self.register_handlers(self.router)
    
    @abstractmethod
    def register_handlers(self, router: Router) -> Router:
        raise NotImplementedError

    @classmethod
    @property
    def router_collector(cls) -> Router:
        if not cls.__router:
            cls.__router = Router(name=cls.__name__)
        return cls.__router


def with_uow(f):
    @wraps(f)
    async def wrapper(self: BaseHandlersGroup, *args, **kwargs):
        if self.uowf is None:
            raise NotImplementedError('uowf is not found')

        async with self.uowf() as uow:  # type: ignore
            self.uow = uow
            return await f(self, *args, **kwargs)
    
    return wrapper 


OBSERVERS_NAME = [
    "message",
    "edited_message",
    "channel_post",
    "edited_channel_post",
    "inline_query",
    "chosen_inline_result",
    "callback_query",
    "shipping_query",
    "pre_checkout_query",
    "poll",
    "poll_answer",
    "my_chat_member",
    "chat_member",
    "chat_join_request",
    "error",
]

@dataclass
class FrozenHandler:
    observer_name: str

    args: Union[List[Any], tuple[Any]]
    kwargs: Dict[str, Any]
    fn: Any


class ProxyRouter(Router):
    _observers_name = OBSERVERS_NAME

    def __init__(self, *, name: str | None = None) -> None:
        self._cls_registrations: Dict[str, Dict[str, FrozenHandler]] = {}
        super().__init__(name=name)

    def proxy_observer(self, __name: str) -> Callable[[Any], Any]:
        def inner_wrapper(*args: Any, **kwargs: Dict[Any, Any]):
            def wrapper(fn: Callable[[Any], Any]) -> Any:
                clsname, methodname, *extra = fn.__qualname__.split('.')
                if not extra:
                    if clsname not in self._cls_registrations:
                        self._cls_registrations[clsname] = {}

                    self._cls_registrations[clsname][methodname] = FrozenHandler(
                        observer_name=__name,
                        args=args,
                        kwargs=kwargs,
                        fn=fn,
                    )

                return fn

            return wrapper

        return inner_wrapper

    def get_group_observed_router(self, group: BaseHandlersGroup) -> Router:
        cls = group.__class__
        clsname = cls.__name__
        router = Router(name=clsname)

        if clsname not in self._cls_registrations:
            return router

        for methodname, fh in self._cls_registrations[clsname].items():
            getattr(router, fh.observer_name)(*fh.args, **fh.kwargs)(getattr(group, methodname))

        return router


    def __getattribute__(self, __name: str) -> Any:
        if not __name.startswith('_') and __name in self._observers_name:
            return self.proxy_observer(__name)
        return super().__getattribute__(__name)


proxy_router = ProxyRouter()
