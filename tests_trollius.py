# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid
from functools import wraps

from cassandra.cluster import Cluster

import trollius
from aiocassandra import aiosession
from trollius import From

try:
    import unittest2 as unittest
except ImportError:
    import unittest


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
        aiosession(self.session, loop=self.loop)

    @run_loop
    @trollius.coroutine
    def test_execute_future_prepare(self):
        cql = self.session.prepare('SELECT now() as now FROM system.local;')

        ret = yield From(self.session.execute_future(cql))

        self.assertEqual(len(ret), 1)

        self.assertIsInstance(ret[0].now, uuid.UUID)

    @run_loop
    @trollius.coroutine
    def test_execute_future(self):
        cql = 'SELECT now() as now FROM system.local;'

        ret = yield From(self.session.execute_future(cql))

        self.assertEqual(len(ret), 1)

        self.assertIsInstance(ret[0].now, uuid.UUID)
