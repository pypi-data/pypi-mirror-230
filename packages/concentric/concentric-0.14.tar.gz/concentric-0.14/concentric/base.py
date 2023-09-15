import urllib
import urllib.parse

from waddle import ParamBunch


class BaseConnector:
    """
    connector classes create connections and connection strings
    in the correct format
    """
    engine = None
    default_port = None
    jdbc_class = None
    default_connect_timeout = 10
    default_application_name = 'concentric'
    default_sslmode = 'require'
    default_autocommit = False

    @classmethod
    def as_bool(cls, key, kwargs, conf: ParamBunch):
        value = kwargs.pop(key, None)
        if value is None:
            value = conf.get(key)
        if value is None:
            value = getattr(cls, f'default_{key}', None)
        return value

    @classmethod
    def value(cls, key, kwargs, conf: ParamBunch):
        value = kwargs.pop(key, None)
        value = value or conf.get(key)
        value = value or getattr(cls, f'default_{key}', None)
        return value

    @classmethod
    def ensure(cls, key, kwargs, conf: ParamBunch):
        kwargs.setdefault(
            key,
            conf.get(key, getattr(cls, f'default_{key}', None)))

    @classmethod
    def connect(cls, conf: ParamBunch, *args, **kwargs):
        """
        use the appropriate underlying library to connect to the database
        """
        pass

    @classmethod
    def sql_alchemy_connection_string(cls, conf: ParamBunch, *args,
                                      user=None, password=None,
                                      host=None, name=None,
                                      port=None, suffix=None, **kwargs):
        """
        the sql alchemy connection string used to connect to the database
        """
        user = user or conf.get('user')
        password = password or conf.get('password')
        password = urllib.parse.quote(password)
        host = host or conf.get('host')
        name = name or conf.get('name')
        port = port or conf.get('port') or cls.default_port
        suffix = suffix or f'{host}:{port}/{name}'
        url = f'{cls.engine}://{user}:{password}@{suffix}'
        if kwargs:
            params = urllib.parse.urlencode(kwargs)
            url = f'{url}?{params}'
        return url

    @classmethod
    def jdbc_connection_string(cls, conf: ParamBunch, *args, **kwargs):
        """
        the jdbc connection string used to connect to the database
        """
        pass
