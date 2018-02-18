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
    from cassandra.query import SimpleStatement

    # connection is blocking call
    cluster = Cluster()
    # aiocassandra uses executor_threads to talk to cassndra driver
    # https://datastax.github.io/python-driver/api/cassandra/cluster.html?highlight=executor_threads
    session = cluster.connect()


    async def main():
        # patches and adds `execute_future`, `execute_futures` and `prepare_future`
        # to `cassandra.cluster.Session`
        aiosession(session)

        # best way is to use cassandra prepared statements
        # https://cassandra-zone.com/prepared-statements/
        # https://datastax.github.io/python-driver/api/cassandra/cluster.html#cassandra.cluster.Session.prepare
        # try to create them once on application init
        query = session.prepare('SELECT now() FROM system.local;')

        # if non-blocking prepared statements is really needed:
        query = await session.prepare_future('SELECT now() FROM system.local;')

        print(await session.execute_future(query))

        # pagination is also supported
        query = 'SELECT * FROM system.size_estimates;'
        statement = SimpleStatement(query, fetch_size=100)

        # don't miss *s* (execute_futureS)
        async with session.execute_futures(statement) as paginator:
            async for row in paginator:
                print(row)


    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    cluster.shutdown()
    loop.close()

Python 3.5+ is required

Thanks
------

The library was donated by `Ocean S.A. <https://ocean.io/>`_

Thanks to the company for contribution.
