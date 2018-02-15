import asyncio
import logging
import uuid

import pytest
from cassandra.cluster import Cluster
from cassandra.protocol import SyntaxException

from aiocassandra import aiosession


@pytest.mark.asyncio
async def test_execute_future_prepare(cassandra):
    cql = cassandra.prepare('SELECT now() as now FROM system.local;')

    fut = cassandra.execute_future(cql)

    assert asyncio.isfuture(fut)

    ret = await fut

    assert len(ret) == 1

    assert isinstance(ret[0].now, uuid.UUID)


@pytest.mark.asyncio
async def test_execute_future(cassandra):
    cql = 'SELECT now() as now FROM system.local;'

    fut = cassandra.execute_future(cql)

    assert asyncio.isfuture(fut)

    ret = await fut

    assert len(ret) == 1

    assert isinstance(ret[0].now, uuid.UUID)


@pytest.mark.asyncio
async def test_execute_future_error(cassandra):
    cql = 'SELECT 1;'

    fut = cassandra.execute_future(cql)

    assert asyncio.isfuture(fut)

    with pytest.raises(SyntaxException):
        await fut


@pytest.mark.asyncio
async def test_execute_future_cancel(cassandra, caplog, loop):
    cql = 'SELECT now() as now FROM system.local;'

    old_fut_factory = cassandra._asyncio_fut_factory

    def new_patch_factory():
        fut = old_fut_factory()
        fut.cancel()
        return fut

    cassandra._asyncio_fut_factory = new_patch_factory

    fut = cassandra.execute_future(cql)

    assert asyncio.isfuture(fut)

    with caplog.at_level(logging.ERROR):
        await asyncio.sleep(0.1, loop=loop)
        assert len(caplog.records) == 0

    with pytest.raises(asyncio.CancelledError):
        await fut


@pytest.mark.asyncio
async def test_execute_future_cancel_error(cassandra, caplog, loop):
    cql = 'SELECT 1;'

    old_fut_factory = cassandra._asyncio_fut_factory

    def new_patch_factory():
        fut = old_fut_factory()
        fut.cancel()
        return fut

    cassandra._asyncio_fut_factory = new_patch_factory

    fut = cassandra.execute_future(cql)

    assert asyncio.isfuture(fut)

    with caplog.at_level(logging.ERROR):
        await asyncio.sleep(0.1, loop=loop)
        assert len(caplog.records) == 0

    with pytest.raises(asyncio.CancelledError):
        await fut


def test_malformed_session():
    with pytest.raises(AssertionError):
        aiosession(None)


def test_patched_twice(cassandra, session, loop):
    with pytest.raises(RuntimeError):
        aiosession(session, loop=loop)


def test_main_thread_loop_missing(session):
    with pytest.raises(RuntimeError):
        aiosession(session)


def test_main_thread_loop(loop, session):
    asyncio.set_event_loop(loop)
    cluster = Cluster()
    session = cluster.connect()

    aiosession(session)

    assert loop is session._loop


def test_explicit_loop(cassandra, loop):
    assert loop is cassandra._loop


def test_session_patched(cassandra):
    assert getattr(cassandra, 'execute_future', None) is not None