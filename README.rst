aiocassandra
============

:info: Simple threaded cassandra wrapper for asyncio

.. image:: https://travis-ci.org/aio-libs/aiocassandra.svg?branch=master
    :target: https://travis-ci.org/aio-libs/aiocassandra

.. image:: https://img.shields.io/pypi/v/aiocassandra.svg
    :target: https://pypi.python.org/pypi/aiocassandra

.. image:: https://codecov.io/gh/aio-libs/aiocassandra/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/aio-libs/aiocassandra

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
        return (yield from session.execute_future(cql))

    loop = asyncio.get_event_loop()

    try:
        response = loop.run_until_complete(main(loop=loop))
        print(response)
    finally:
        cluster.shutdown()
        loop.close()

Python 3.4+ is required

Thanks
------

The library was donated by `Ocean S.A. <https://ocean.io/>`_

Thanks to the company for contribution.
