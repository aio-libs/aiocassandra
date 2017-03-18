aiocassandra
============

:info: Simple threaded cassandra wrapper for asyncio

.. image:: https://img.shields.io/travis/wikibusiness/aiocassandra.svg
    :target: https://travis-ci.org/wikibusiness/aiocassandra

.. image:: https://img.shields.io/pypi/v/aiocassandra.svg
    :target: https://pypi.python.org/pypi/aiocassandra

Installation
------------

.. code-block:: shell

    pip install aiocassandra

Usage
-----

.. code-block:: python

    import asyncio

    from aiocassandra import aiosession
    from cassandra.cluster import Cluster

    cluster = Cluster()
    session = cluster.connect()

    # best way is to use cassandra prepared statements
    cql = session.prepare('SELECT now() FROM system.local;')

    @asyncio.coroutine
    def main(*, loop):
        # patches and adds `execute_future` to `cassandra.cluster.Session`
        aiosession(session, loop=loop)
        return (yield session.execute_future(cql))

    loop = asyncio.get_event_loop()

    try:
        response = loop.run_until_complete(main(loop=loop))
        print(response)
    finally:
        cluster.shutdown()
        loop.close()

Python 2.7(trollius), 3.3+ and PyPy(trollius) are supported
