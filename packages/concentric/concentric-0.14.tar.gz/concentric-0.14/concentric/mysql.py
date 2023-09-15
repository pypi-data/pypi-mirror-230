from waddle import ParamBunch

from .base import BaseConnector


class Mysql(BaseConnector):
    """
    n.b., I don't like the fact that mysql uses `ssl_mode` while
    postgres uses `sslmode`, but thems the breaks (underlying libraries
    are written that way).
    """
    default_port = 3306
    jdbc_class = 'com.mysql.cj.jdbc.Driver'
    engine = 'mysql+mysqldb'
    default_local_infile = 1
    default_sslmode = 'REQUIRED'

    @classmethod
    def connect(cls, conf: ParamBunch, *args,
                user=None, password=None, host=None,
                port=None, name=None, **kwargs):
        import MySQLdb
        user = user or conf.get('user')
        password = password or conf.get('password')
        host = host or conf.get('host')
        port = port or conf.get('port') or cls.default_port
        name = name or conf.get('name')
        autocommit = cls.as_bool('autocommit', kwargs, conf)
        local_infile = cls.value('local_infile', kwargs, conf)
        connect_timeout = cls.value('connect_timeout', kwargs, conf)
        sslmode = cls.value('sslmode', kwargs, conf)
        charset = cls.value('charset', kwargs, conf)
        return MySQLdb.connect(
            host=host,
            user=user,
            password=password,
            database=name,
            port=port,
            autocommit=autocommit,
            connect_timeout=connect_timeout,
            ssl_mode=sslmode,
            local_infile=local_infile,
            charset=charset,
            **kwargs,
        )

    @classmethod
    def sql_alchemy_connection_string(
            cls, conf: ParamBunch, *args,
            **kwargs):
        autocommit = cls.as_bool('autocommit', kwargs, conf)
        local_infile = cls.as_bool('local_infile', kwargs, conf)
        connect_timeout = cls.value('connect_timeout', kwargs, conf)
        sslmode = cls.value('sslmode', kwargs, conf)
        return super().sql_alchemy_connection_string(
            conf, *args,
            connect_timeout=connect_timeout,
            ssl_mode=sslmode,
            local_infile=local_infile,
            autocommit=autocommit)
    