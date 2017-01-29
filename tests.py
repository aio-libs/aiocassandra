import sys
import unittest

if sys.version_info >= (3, 3):
    from tests_asyncio import AiosessionTestCase
else:
    from tests_trollius import AiosessionTestCase


class AiocassandraTestCase(AiosessionTestCase):
    def test_main_thread_loop_missing(self):
        pass

    def test_main_thread_loop(self):
        pass

    def test_explicit_loop(self):
        pass

    def tearDown(self):
        self.cluster.shutdown()
        self.loop.call_soon(self.loop.stop)
        self.loop.close()


if __name__ == '__main__':
    unittest.main()
