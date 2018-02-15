import asyncio
from collections import deque
from functools import partial
from types import MethodType

from async_generator import async_generator, yield_
from cassandra.cluster import Session

__version__ = '2.0.0a0'


@async_generator
async def _paginator(cassandra_fut, *, loop):
    _deque = deque()
    _exc = None
    _drain = asyncio.Event(loop=loop)
    _finished = asyncio.Event(loop=loop)

    def _handle_page(rows):
        for row in rows:
            _deque.append(row)

        loop.call_soon_threadsafe(_drain.set)

        if cassandra_fut.has_more_pages:
            cassandra_fut.start_fetching_next_page()
            return

        loop.call_soon_threadsafe(_finished.set)

    def _handle_err(exc):
        nonlocal _exc

        _exc = exc

        loop.call_soon_threadsafe(_drain.set)

        loop.call_soon_threadsafe(_finished.set)

    cassandra_fut.add_callbacks(
        callback=_handle_page,
        errback=_handle_err
    )

    while _deque or not _finished.is_set():
        if _exc is not None:
            raise _exc

        while _deque:
            await yield_(_deque.popleft())

        await asyncio.wait(
            (
                _drain.wait(),
                _finished.wait(),
            ),
            return_when=asyncio.FIRST_COMPLETED,
            loop=loop
        )


def _asyncio_fut_factory(loop):
    try:
        return loop.create_future
    except AttributeError:  # pragma: no cover
        return partial(asyncio.Future, loop=loop)


def _asyncio_result(self, fut, result):
    if fut.cancelled():
        return

    self._loop.call_soon_threadsafe(fut.set_result, result)


def _asyncio_exception(self, fut, exc):
    if fut.cancelled():
        return

    self._loop.call_soon_threadsafe(fut.set_exception, exc)


def execute_future(self, *args, **kwargs):
    cassandra_fut = self.execute_async(*args, **kwargs)

    asyncio_fut = self._asyncio_fut_factory()

    cassandra_fut.add_callbacks(
        callback=partial(self._asyncio_result, asyncio_fut),
        errback=partial(self._asyncio_exception, asyncio_fut)
    )

    return asyncio_fut


def execute_futures(self, *args, **kwargs):
    cassandra_fut = self.execute_async(*args, **kwargs)
    return _paginator(cassandra_fut, loop=self._loop)


def prepare_future(self, *args, **kwargs):
    statement = partial(self.prepare, *args, **kwargs)
    return self._loop.run_in_executor(None, statement)


def aiosession(session, loop=None):
    assert isinstance(session, Session), 'provide cassandra.cluster.Session'

    if hasattr(session, '_asyncio_fut_factory'):
        raise RuntimeError('session is already patched by aiosession')

    if loop is None:
        loop = asyncio.get_event_loop()

    session._loop = loop
    session._asyncio_fut_factory = _asyncio_fut_factory(loop=loop)

    session._asyncio_result = MethodType(_asyncio_result, session)
    session._asyncio_exception = MethodType(_asyncio_exception, session)
    session.execute_future = MethodType(execute_future, session)
    session.execute_futures = MethodType(execute_futures, session)
    session.prepare_future = MethodType(prepare_future, session)

    return session
