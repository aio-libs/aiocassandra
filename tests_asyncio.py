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

        aiosession(self.session, loop=self.loop)

    @run_loop
    @asyncio.coroutine
    def test_execute_future_prepare(self):
        cql = self.session.prepare('SELECT now() FROM system.local;')

        ret = yield from self.session.execute_future(cql)

        self.assertEqual(len(ret), 1)

        self.assertIsInstance(ret[0].system_now, uuid.UUID)

    @run_loop
    @asyncio.coroutine
    def test_execute_future(self):
        cql = 'SELECT now() FROM system.local;'

        ret = yield from self.session.execute_future(cql)

        self.assertEqual(len(ret), 1)

        self.assertIsInstance(ret[0].system_now, uuid.UUID)
