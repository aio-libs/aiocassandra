import asyncio
import uuid

import pytest
from aiocassandra import aiosession
from cassandra.cluster import Cluster
from cassandra.protocol import SyntaxException


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
async def test_execute_error(cassandra):
    cql = 'SELECT 1;'

    fut = cassandra.execute_future(cql)

    assert asyncio.isfuture(fut)

    with pytest.raises(SyntaxException):
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
