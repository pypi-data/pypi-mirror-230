import os
from json import loads, dumps
from contextlib import asynccontextmanager
from dataclasses import dataclass

from asyncpg.pool import Pool
from asyncpg import create_pool, connect, Connection

from .database_errors import DatabaseError


async def get(user: str = None, password: str = None, database: str = None, host: str = None,
              port: int = None, connection_timeout: int = None) -> Connection:
    """Retrieve a database connection.
    :param user: Database user.
    :param password: Database password.
    :param database: Database name.
    :param host: Database host.
    :param port: Database port number.
    :param connection_timeout: Connection timeout.
    :return: (asyncpg) Connection.
    """

    datasource = _construct_datasource(user, password, database, host, port, connection_timeout)

    connection: Connection = await connect(user=datasource.user, password=datasource.password,
                                           database=datasource.database, host=datasource.host,
                                           port=datasource.port, timeout=datasource.connection_timeout)

    await __init(connection)
    return connection


async def get_pool(user: str = None, password: str = None, database: str = None, host: str = None,
                   port: int = None, connection_timeout: int = None,
                   pool_min_size: int = None, pool_max_size: int = None,
                   pool_max_inactive_connection_lifetime: int = None) -> Pool:
    """Retrieve a database connection pool.
    :param user: Database user.
    :param password: Database password.
    :param database: Database name.
    :param host: Database host.
    :param port: Database port number.
    :param connection_timeout: Connection timeout.
    :param pool_min_size: Number of connection the pool will be initialized with.
    :param pool_max_size: Max number of connections.
    :param pool_max_inactive_connection_lifetime: Number of seconds after which inactive connections will be closed.
    :return: (asyncpg) Pool.
    """

    datasource = _construct_datasource(user, password, database, host, port, connection_timeout,
                                       pool_min_size, pool_max_size, pool_max_inactive_connection_lifetime)

    return await create_pool(user=datasource.user, password=datasource.password,
                             database=datasource.database, host=datasource.host,
                             port=datasource.port, timeout=datasource.connection_timeout,
                             min_size=datasource.pool_min_size, max_size=datasource.pool_max_size,
                             max_inactive_connection_lifetime=datasource.pool_max_inactive_connection_lifetime,
                             init=__init)


@asynccontextmanager
async def create_transaction(pool: Pool = None, connection: Connection = None):
    """Create a database transaction conditionally. If connection is provided then this
    connection is returned immediately without creating any transaction, if not then a
    transaction is established using a connection acquired from provided connection pool.
    :param pool: (asyncpg) Connection pool.
    :param connection: (asyncpg) Connection.
    :raise DatabaseError: If nor connection neither connection pool are specified.
    :return: Transactional connection.
    """

    if connection:
        yield connection
    elif pool:
        async with pool.acquire() as _connection, _connection.transaction():
            yield _connection
    else:
        raise DatabaseError("nor connection neither connection pool are specified")


@asynccontextmanager
async def create_connection(pool: Pool = None, connection: Connection = None):
    """Create a database connection conditionally. If connection is provided then this
    connection is returned immediately, if not then a connection is acquired from provided
    connection pool.
    :param pool: (asyncpg) Connection pool.
    :param connection: (asyncpg) Connection.
    :raise DatabaseError: If nor connection neither connection pool are specified.
    :return: Connection.
    """

    if connection:
        yield connection
    elif pool:
        async with pool.acquire() as _connection:
            yield _connection
    else:
        raise DatabaseError("nor connection neither connection pool are specified")


async def __init(conn: Connection):
    await conn.set_type_codec("uuid", encoder=str, decoder=str, schema="pg_catalog")
    await conn.set_type_codec("numeric", encoder=str, decoder=float, schema="pg_catalog")
    await conn.set_type_codec("jsonb", encoder=dumps, decoder=loads, schema="pg_catalog")


@dataclass()
class Datasource:
    user: str
    password: str
    database: str
    host: str
    port: int
    connection_timeout: int
    pool_min_size: int
    pool_max_size: int
    pool_max_inactive_connection_lifetime: int


def _construct_datasource(user: str = None, password: str = None, database: str = None, host: str = None,
                          port: int = None, connection_timeout: int = None, pool_min_size: int = None,
                          pool_max_size: int = None, pool_max_inactive_connection_lifetime: int = None) -> Datasource:
    datasource = loads(os.environ["Datasource"]) if "Datasource" in os.environ else None

    if not user:
        user = datasource["user"]
    if not password:
        password = datasource["password"]
    if not database:
        database = datasource["database"]
    if not host:
        host = datasource["host"]
    if not port:
        port = datasource["port"]
    if not connection_timeout:
        connection_timeout = datasource["connection_timeout"]
    if not pool_min_size:
        pool_min_size = datasource["pool_min_size"]
    if not pool_max_size:
        pool_max_size = datasource["pool_max_size"]
    if not pool_max_inactive_connection_lifetime:
        pool_max_inactive_connection_lifetime = datasource["pool_max_inactive_connection_lifetime"]

    return Datasource(user, password, database, host, port, int(connection_timeout / 1000),
                      pool_min_size, pool_max_size, int(pool_max_inactive_connection_lifetime / 1000))
