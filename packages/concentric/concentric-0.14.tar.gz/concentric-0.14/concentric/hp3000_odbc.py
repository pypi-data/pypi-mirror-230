from waddle import ParamBunch

from .odbc import OdbcConnector


class Hp3000Odbc(OdbcConnector):
    jdbc_class = 'com.minisoft.jdbc.MSJDBCDriver'
    default_port = 32233
    default_driver = 'hp3000'

    @classmethod
    def connect(cls, conf: ParamBunch, *args, **kwargs):
        import pyodbc
        cls.ensure('driver', kwargs, conf)
        driver = kwargs['driver']
        server = kwargs.get('server') or conf.host
        port = kwargs.get('port') or conf.port
        user = kwargs.get('user') or conf.user
        account = kwargs.get('account') or conf.password
        pieces = [
            f'server={server}',
            f'server port={port}',
            f'user={user}',
            f'account={account}',
            f'driver={driver}',
        ]
        schemae = kwargs.get('schema') or conf.schema or []
        for i, x in enumerate(schemae, 1):
            pieces.append(f'schema{i}={x}.SCHEMA.{account}')
        st = ';'.join(pieces)
        print(st)
        connection = pyodbc.connect(st)
        return connection

