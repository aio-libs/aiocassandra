# -*- coding: utf-8 -*-
try:
    import asyncio
except ImportError:
    import trollius as asyncio
import sys
from functools import partial

from cassandra.cluster import Session

from types import MethodType  # isort:skip


__version__ = '1.0.0'


def _asyncio_fut_factory(loop):
    try:
        return loop.create_future
    except AttributeError:
        return partial(asyncio.Future, loop=loop)


def _asyncio_result(self, fut, result):
    self._loop.call_soon_threadsafe(fut.set_result, result)


def _asyncio_exception(self, fut, exc):
    self._loop.call_soon_threadsafe(fut.set_exception, exc)


def execute_future(self, *args, **kwargs):
    cassandra_fut = self.execute_async(*args, **kwargs)

    asyncio_fut = self._asyncio_fut_factory()

    cassandra_fut.add_callbacks(
        partial(self._asyncio_result, asyncio_fut),
        partial(self._asyncio_exception, asyncio_fut),
    )

    return asyncio_fut


def aiosession(session, loop=None):
    assert isinstance(session, Session)

    if loop is None:
        loop = asyncio.get_event_loop()

    setattr(session, '_loop', loop)
    setattr(session, '_asyncio_fut_factory', _asyncio_fut_factory(loop=loop))

    if sys.version_info >= (3, 0):
        session._asyncio_result = MethodType(_asyncio_result, session)
        session._asyncio_exception = MethodType(_asyncio_exception, session)
        session.execute_future = MethodType(execute_future, session)
    else:
        session._asyncio_result = MethodType(_asyncio_result, session, Session)
        session._asyncio_exception = MethodType(_asyncio_exception, session, Session)  # noqa
        session.execute_future = MethodType(execute_future, session, Session)

    return session
