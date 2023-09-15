from waddle import ParamBunch

from .base import BaseConnector


class JdbcConnector(BaseConnector):
    @classmethod
    def connect(cls, conf: ParamBunch, *args, **kwargs):
        """
        use the appropriate underlying library to connect to the database
        """
        from jaydebeapi import connect
        jars = kwargs.pop('jars', None)
        driver_args = kwargs.pop('driver_args', None)
        st = cls.jdbc_connection_string(conf, *args, **kwargs)
        connection = connect(cls.jdbc_class, st, driver_args, jars)
        return connection

