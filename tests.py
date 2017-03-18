#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os  # noqa # isort:skip
import sys  # noqa # isort:skip

os.environ['PYTHONASYNCIODEBUG'] = '1'  # noqa # isort:skip

from aiocassandra import aiosession  # noqa # isort:skip
from cassandra.cluster import Cluster   # noqa # isort:skip


if sys.version_info >= (3, 3):
    import asyncio
    from tests_asyncio import AiosessionTestCase
else:
    import trollius as asyncio
    from tests_trollius import AiosessionTestCase

try:
    import unittest2 as unittest
except ImportError:
    import unittest


class AiocassandraTestCase(AiosessionTestCase):
    def test_malformed_session(self):
        with self.assertRaises(AssertionError):
            aiosession(None)

    def test_patched_twice(self):
        with self.assertRaises(RuntimeError):
            aiosession(self.session, loop=self.loop)

    def test_main_thread_loop_missing(self):
        with self.assertRaises(RuntimeError):
            try:
                cluster = Cluster()

                session = cluster.connect()

                aiosession(session)
            finally:
                cluster.shutdown()

    def test_main_thread_loop(self):
        try:
            loop = asyncio.new_event_loop()
            loop.set_debug(True)
            asyncio.set_event_loop(loop)

            cluster = Cluster()
            session = cluster.connect()

            aiosession(session)

            self.assertIs(loop, session._loop)
        finally:
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
