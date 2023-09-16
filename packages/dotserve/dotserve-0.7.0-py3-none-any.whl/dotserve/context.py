import asyncio
from contextvars import ContextVar
from typing import TYPE_CHECKING

from dotserve.session import Session
from lazify import LazyProxy

if TYPE_CHECKING:
    from dotserve.emitter import DotserveEmitter


class DotserveContextException(Exception):
    def __init__(self, msg="Dotserve context not found", *args, **kwargs):
        super().__init__(msg, *args, **kwargs)


class DotserveContext:
    loop: asyncio.AbstractEventLoop
    emitter: "DotserveEmitter"
    session: Session

    def __init__(self, session: Session):
        from dotserve.emitter import DotserveEmitter

        self.loop = asyncio.get_running_loop()
        self.session = session
        self.emitter = DotserveEmitter(session)


context_var: ContextVar[DotserveContext] = ContextVar("dotserve")


def init_context(session_or_sid) -> DotserveContext:
    if not isinstance(session_or_sid, Session):
        session_or_sid = Session.require(session_or_sid)

    context = DotserveContext(session_or_sid)
    context_var.set(context)
    return context


def get_context() -> DotserveContext:
    try:
        return context_var.get()
    except LookupError:
        raise DotserveContextException()


context: DotserveContext = LazyProxy(get_context, enable_cache=False)
