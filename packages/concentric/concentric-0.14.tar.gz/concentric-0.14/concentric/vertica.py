import ssl
from ssl import SSLContext, PROTOCOL_TLS, CERT_OPTIONAL, CERT_NONE
from waddle import ParamBunch

from .base import BaseConnector


class Vertica(BaseConnector):
    default_port = 5433
    engine = 'vertica+vertica_python'
    jdbc_class = 'com.vertica.jdbc.Driver'
    default_connection_timeout = 30
    default_autocommit = True
    default_ssl = 0

    @classmethod
    def connect(cls, conf: ParamBunch, *args,
                user=None, password=None, host=None, port=None, name=None,
                search_path=None, **kwargs):
        """
        use the appropriate underlying library to connect to the database
        """
        import vertica_python as vertica
        user = user or conf.user
        password = password or conf.password
        host = host or conf.host
        name = name or conf.name
        port = port or conf.port or cls.default_port
        connect_timeout = cls.value('connect_timeout', kwargs, conf)
        autocommit = cls.as_bool('autocommit', kwargs, conf)
        ssl_context = cls.value('ssl', kwargs, conf)
        connection = vertica.connect(
            host=host,
            port=port,
            database=name,
            user=user,
            password=password,
            connection_timeout=connect_timeout,
            autocommit=autocommit,
            ssl=ssl_context)
        search_path = search_path or conf.get('search_path')
        if search_path:
            with connection.cursor() as cursor:
                cursor.execute(f'set search_path = {", ".join(search_path)}')
        return connection

    @classmethod
    def sql_alchemy_connection_string(cls, conf: ParamBunch, *args, **kwargs):
        """
        provides the connection string to connect to sql alchemy
        """
        cls.ensure('connect_timeout', kwargs, conf)
        cls.ensure('autocommit', kwargs, conf)
        cls.ensure('port', kwargs, conf)
        cls.ensure('ssl', kwargs, conf)
        st = super().sql_alchemy_connection_string(conf, *args, **kwargs)
        return st

    @classmethod
    def jdbc_connection_string(cls, conf: ParamBunch, *args, **kwargs):
        """
        the jdbc connection string used to connect to the database
        """
        port = conf.get('port', cls.default_port)
        return f'jdbc:vertica://@{conf.host}:{port}/{conf.name}'
