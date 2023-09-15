from waddle import ParamBunch

from .base import BaseConnector


class Redshift(BaseConnector):
    default_port = 5439
    engine = 'redshift+redshift_connector'

    @classmethod
    def connect(cls, conf: ParamBunch, *args,
                user=None, password=None, host=None,
                port=None, name=None, **kwargs):
        import redshift_connector
        user = user or conf.user
        password = password or conf.password
        host = host or conf.host
        name = name or conf.name
        port = port or conf.port or cls.default_port
        return redshift_connector.connect(
            database=name, user=user, password=password,
            host=host, port=port, )

    @classmethod
    def sql_alchemy_connection_string(cls, conf: ParamBunch, *args,
                                      sslmode='require', **kwargs):
        return super().sql_alchemy_connection_string(
            conf, *args, sslmode=sslmode, **kwargs)