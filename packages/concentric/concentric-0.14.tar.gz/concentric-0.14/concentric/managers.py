import atexit
import threading
import logging
from contextlib import contextmanager

from waddle import ParamBunch
from .db2i import Db2i
from .db2i_native import Db2iNative
from .hp3000 import Hp3000
from .hp3000_odbc import Hp3000Odbc
from .mssql import SqlServer
from .mysql import Mysql
from .netsuite import Netsuite
from .oracle import Oracle
from .oracle_db import OracleDb
from .postgres import Postgres
from .redshift import Redshift
from .snowflake import Snowflake
from .vertica import Vertica
from .progress_openedge import ProgressOpenedge


gtl = threading.local()
log = logging.getLogger(__name__)


class Config:
    def __init__(self):
        self.conf = ParamBunch()
        initialized = False

    def get_connector(self, alias):
        conf = self.conf[alias]
        if conf.engine == 'oracle':
            return conf, Oracle
        if conf.engine == 'oracledb':
            return conf, OracleDb
        if conf.engine == 'db2i':
            return conf, Db2i
        if conf.engine == 'db2i_native':
            return conf, Db2iNative
        if conf.engine == 'hp3000':
            return conf, Hp3000
        if conf.engine == 'hp3000_odbc':
            return conf, Hp3000Odbc
        if conf.engine == 'mssql':
            return conf, SqlServer
        if conf.engine == 'mysql':
            return conf, Mysql
        if conf.engine == 'netsuite':
            return conf, Netsuite
        if conf.engine == 'postgres':
            return conf, Postgres
        if conf.engine == 'redshift':
            return conf, Redshift
        if conf.engine == 'snowflake':
            return conf, Snowflake
        if conf.engine == 'vertica':
            return conf, Vertica
        if conf.engine == 'progress_openedge':
            return conf, ProgressOpenedge
        return None, None

    def add_config(self, *filenames):
        for filename in filenames:
            self.conf.from_file(filename, True)
        initialized = True


config = Config()


def setup_concentric(*filenames):
    """
    sets up concentric by initializing the config with the filenames passed in
    """
    global config
    config.add_config(*filenames)


class ConnectionManager:
    thread_local_key = 'concentric_connection_manager'

    @classmethod
    def connect(cls, alias, ping=False):
        conf, connector = config.get_connector(alias)
        return connector.connect(conf)


class CachingConnectionManager(ConnectionManager):
    thread_local_key = 'concentric_caching_connection_manager'
    thread_local_cache_key = 'concentric_connection_cache'

    @classmethod
    def test_connection(cls, alias, conn):
        _, engine = config.get_connector(alias)
        ping_query = getattr(engine, 'ping_query', None)
        if ping_query:
            try:
                with conn.cursor() as cursor:
                    cursor.execute(ping_query)
                    cursor.fetchall()
            except:
                conn = None
        return conn

    @classmethod
    def connect(cls, alias, use_cache=True, pre_ping=True):
        global gtl
        cache = getattr(gtl, cls.thread_local_cache_key, None) or {}
        if use_cache:
            conn = cache.get(alias)
            if pre_ping and conn:
                if not hasattr(conn, 'ping'):
                    conn = cls.test_connection(alias, conn)
                else:
                    try:
                        conn.ping()
                    except:
                        conn = None
            if conn:
                return conn
        conn = super().connect(alias)
        if use_cache:
            cache[alias] = conn
            setattr(gtl, cls.thread_local_cache_key, cache)
        return conn

    @classmethod
    def cleanup(cls):
        global gtl
        cache = getattr(gtl, cls.thread_local_cache_key, None) or {}
        keys = []
        for alias, conn in cache.items():
            try:
                keys.append(alias)
                conn.close()
            except:
                pass
        for alias in keys:
            cache.pop(alias, None)


@contextmanager
def transactional(session_cls, initial):
    """
    Provide a transactional scope around a series of operations.
    """
    session = session_cls()
    try:
        for x in initial:
            session.execute(x)
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@contextmanager
def read_only(session_cls, initial, **params):
    """
    Provide a closing scope around a series of operations.
    used for query operations
    """
    session = session_cls(**params)
    try:
        for x in initial:
            session.execute(x)
        yield session
    finally:
        session.close()


class Alchemist:
    """

    Provides thread safe named access to sqlalchemy sessions

    first declare your connection::

        ConnectionMgr.connection("default", "sqlite:///simple.db")

    then connect::

        with ConnectionMgr.session("default") as session:
            session.execute(sql.insert(role, {"name": "user"}))
            session.commit()

    """

    connections = {}
    connections_lock = threading.Lock()

    @classmethod
    def connection(cls, using, force=False, initial=None, **kwargs):
        """
        creates a cached engine and session_cls for db_url
        kwargs are passed on the create_engine
        """
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        with cls.connections_lock:
            conn = cls.connections.get(using)
            if conn and not force:
                return conn
            conf, connector = config.get_connector(using)
            url = connector.sql_alchemy_connection_string(conf)
            initial = initial or conf.get('initial') or []
            kwargs.setdefault('pool_pre_ping', True)
            engine = create_engine(url, **kwargs)
            session_cls = sessionmaker(bind=engine)
            conn = engine, session_cls, initial
            cls.connections[using] = conn
        return conn

    @classmethod
    def transactional(cls, using, force=False):
        """
        returns a sql alchemy session for the provided
        database connection that should be defined in waddle
        use the ``force`` flag to force this function to return
        a new connection instead of using the cached connection.
        The semantics of a transactional session are such that at the beginning
        of the context, we will begin a transaction, and once the context
        exits, we will either commit or rollback the transaction.
        """
        conn = cls.connection(using, force=force)
        return transactional(conn[1], conn[2])

    @classmethod
    def read_only(cls, name='default', force=False, **params):
        """
        returns a sql alchemy session for the provided
        database connection that should be defined in waddle
        use the ``force`` flag to force this function to return
        a new connection instead of using the cached connection.
        The semantics of a read only session are that no transactional
        management will occur in the session context.
        """
        conn = cls.connection(name, force=force, **params)
        return read_only(conn[1], conn[2])


def cleanup_cached_connections():
    m = CachingConnectionManager
    m.cleanup()


atexit.register(cleanup_cached_connections)
