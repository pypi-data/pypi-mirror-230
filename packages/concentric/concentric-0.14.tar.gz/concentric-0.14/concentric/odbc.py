from waddle import ParamBunch

from .base import BaseConnector


class OdbcConnector(BaseConnector):
    connect_keys = (
        'readonly',
        'autocommit',
        'encoding',
        'ansi',
        'timeout',
    )

    @classmethod
    def connect(cls, conf: ParamBunch, *args, **kwargs):
        """
        use the appropriate underlying library to connect to the database
        """
        from pyodbc import connect
        pieces = []
        params = {}
        for key, value in kwargs.items():
            if key not in cls.connect_keys:
                pieces.append(f'{key}={value}')
            else:
                params[key] = value
        st = ';'.join(pieces)
        connection = connect(st, **params)
        return connection
