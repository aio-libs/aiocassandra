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


class AiocassandraTestCase(unittest.TestCase):

    def setUp(self):
        asyncio.set_event_loop(None)
        self.loop = asyncio.new_event_loop()
        self.cluster = Cluster()
        self.session = self.cluster.connect()

        aiosession(self.session, loop=self.loop)

    @run_loop
    @asyncio.coroutine
    def test_execute_future_prepare(self):
        cql = self.session.prepare('SELECT now() as now FROM system.local;')

        ret = yield from self.session.execute_future(cql)

        self.assertEqual(len(ret), 1)

        self.assertIsInstance(ret[0].now, uuid.UUID)

    @run_loop
    @asyncio.coroutine
    def test_execute_future(self):
        cql = 'SELECT now() as now FROM system.local;'

        ret = yield from self.session.execute_future(cql)

        self.assertEqual(len(ret), 1)

        self.assertIsInstance(ret[0].now, uuid.UUID)

    def test_malformed_session(self):
        with self.assertRaises(AssertionError):
            aiosession(None)

    def test_patched_twice(self):
        with self.assertRaises(RuntimeError):
            aiosession(self.session, loop=self.loop)

    def test_main_thread_loop_missing(self):
        cluster = Cluster()
        session = cluster.connect()

        with self.assertRaises(RuntimeError):
            aiosession(session)

        cluster.shutdown()

    def test_main_thread_loop(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        cluster = Cluster()
        session = cluster.connect()

        aiosession(session)

        self.assertIs(loop, session._loop)

        cluster.shutdown()
        loop.call_soon(loop.stop)
        loop.run_forever()
        loop.close()

    def test_explicit_loop(self):
        self.assertIs(self.loop, self.session._loop)

    def test_session_patched(self):
        self.assertIsNotNone(getattr(self.session, 'execute_future', None))

    def tearDown(self):
        self.cluster.shutdown()
        self.loop.call_soon(self.loop.stop)
        self.loop.run_forever()
        self.loop.close()


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(AiocassandraTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
