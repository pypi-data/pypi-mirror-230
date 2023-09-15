from waddle import ParamBunch

from .base import BaseConnector


class Postgres(BaseConnector):
    # for connection parameters
    # https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-PARAMKEYWORDS
    default_port = 5432
    engine = 'postgresql'

    @classmethod
    def connect(cls, conf: ParamBunch, *args,
                user=None, password=None, host=None,
                port=None, name=None, connect_timeout=None,
                application_name=None, sslmode=None, **kwargs):
        import psycopg2
        user = user or conf.user
        password = password or conf.password
        host = host or conf.host
        name = name or conf.name
        port = port or conf.port or cls.default_port
        connect_timeout = connect_timeout or conf.get('connect_timeout')
        connect_timeout = connect_timeout or cls.default_connect_timeout
        sslmode = sslmode or conf.get('sslmode') or cls.default_sslmode
        application_name = application_name or conf.get('application_name')
        application_name = application_name or cls.default_application_name
        return psycopg2.connect(
            dbname=name, user=user, password=password,
            host=host, port=port, connect_timeout=connect_timeout,
            sslmode=sslmode, application_name=application_name)

    @classmethod
    def sql_alchemy_connection_string(
            cls, conf: ParamBunch, *args,
            connect_timeout=None,
            application_name=None, sslmode=None,  **kwargs):
        connect_timeout = connect_timeout or conf.get('connect_timeout')
        connect_timeout = connect_timeout or cls.default_connect_timeout
        sslmode = sslmode or conf.get('sslmode') or cls.default_sslmode
        application_name = application_name or conf.get('application_name')
        application_name = application_name or cls.default_application_name
        return super().sql_alchemy_connection_string(
            conf, *args,
            connect_timeout=connect_timeout,
            application_name=application_name,
            sslmode=sslmode)
