#!/usr/bin/env python
import unittest
import uuid
from functools import wraps

import trollius
from aiocassandra import aiosession
from cassandra.cluster import Cluster
from trollius import From


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
        trollius.set_event_loop(None)
        self.loop = trollius.new_event_loop()
        self.cluster = Cluster()
        self.session = self.cluster.connect()

    @trollius.coroutine
    def test_session(self):
        session = aiosession(self.session)

        self.assertIsNotNone(getattr(session, 'execute_future', None))

    @trollius.coroutine
    def test_execute_future_prepare(self):
        session = aiosession(self.session)

        now_cql = session.prepare('SELECT now() FROM system.local;')

        ret = yield From(session.execute_future(now_cql))

        self.assertEqual(len(ret), 1)

        self.assertIsInstance(ret[0].system_now, uuid.UUID)

    @trollius.coroutine
    def test_execute_future(self):
        session = aiosession(self.session)

        now_cql = 'SELECT now() FROM system.local;'

        ret = yield From(session.execute_future(now_cql))

        self.assertEqual(len(ret), 1)

        self.assertIsInstance(ret[0].system_now, uuid.UUID)
