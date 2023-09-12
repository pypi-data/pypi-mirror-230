DBCC - Database Connector
=========================
.. image:: https://img.shields.io/badge/test-pass-00d200.svg
    :target: nono

.. image:: https://img.shields.io/badge/build-pass-00d200.svg
    :target: nono

.. image:: https://img.shields.io/badge/license-BSD-blue.svg?style=flat-square
    :target: https://en.wikipedia.org/wiki/BSD_License

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/ambv/black

Database connector for different DBs with same interface.

Dbcc is Simple
--------------
.. code-block:: python

    from dbcc import MongoTableEngine

    db = MongoTableEngine(URL, DB_NAME)
    collection = db["collection"]
    result = await collection.create({"any":"entry"})
    print(result["id"])

Features
--------
In process

To Do
-----
In process

License
-------
dbcc is a `Stepan Starovoitov`_ open source project,
distributed under the BSD license.

.. _`Stepan Starovoitov`: https://starovoitov.startech.live
