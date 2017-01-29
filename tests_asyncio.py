#!/usr/bin/env python
import asyncio
import unittest
import uuid
from functools import wraps

from aiocassandra import aiosession
from cassandra.cluster import Cluster


def run_loop(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        self = args[0]

        loop = self.loop

        coro = fn(*args, **kwargs)

        return loop.run_until_complete(coro)

    return wrapped


class AiosessionTestCase(unittest.TestCase):
    def setUp(self):
        asyncio.set_event_loop(None)
        self.loop = asyncio.new_event_loop()
        self.cluster = Cluster()
        self.session = self.cluster.connect()

    @asyncio.coroutine
    def test_session(self):
        session = aiosession(self.session)

        self.assertIsNotNone(getattr(session, 'execute_future', None))

    @asyncio.coroutine
    def test_execute_future_prepare(self):
        aiosession(self.session)

        now_cql = session.prepare('SELECT now() FROM system.local;')

        ret = yield from self.session.execute_future(now_cql)

        self.assertEqual(len(ret), 1)

        self.assertIsInstance(ret[0].system_now, uuid.UUID)

    @asyncio.coroutine
    def test_execute_future(self):
        aiosession(self.session)

        now_cql = 'SELECT now() FROM system.local;'

        ret = yield from self.session.execute_future(now_cql)

        self.assertEqual(len(ret), 1)

        self.assertIsInstance(ret[0].system_now, uuid.UUID)

    def tearDown(self):
        self.cluster.shutdown()
        self.loop.call_soon(self.loop.stop)
        self.loop.close()
