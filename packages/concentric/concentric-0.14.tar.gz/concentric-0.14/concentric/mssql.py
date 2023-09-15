import urllib
import urllib.parse
from waddle import ParamBunch

from .odbc import OdbcConnector


class SqlServer(OdbcConnector):
    # https://docs.microsoft.com/en-us/sql/connect/odbc/dsn-connection-string-attribute?view=sql-server-ver16
    default_port = 1433
    engine = 'mssql+pyodbc'
    jdbc_class = 'com.microsoft.sqlserver.jdbc.SQLServerDriver'
    default_driver = 'ODBC Driver 17 for SQL Server'
    ping_query = 'select getdate()'

    @classmethod
    def connect(cls, conf: ParamBunch, *args,
                user=None, password=None, host=None, port=None,
                name=None, driver=None, **kwargs):
        """
        use the appropriate underlying library to connect to the database
        """
        user = user or conf.get('user')
        password = password or conf.get('password')
        host = host or conf.get('host')
        port = port or conf.get('port') or cls.default_port
        name = name or conf.get('name')
        driver = driver or conf.get('driver', cls.default_driver)
        app = cls.value('application_name', kwargs, conf)
        return super().connect(
            conf, driver=driver, server=f'{host},{port}',
            database=name, uid=user, pwd=password,
            trustservercertificate='yes',
            app=app,
        )

    @classmethod
    def sql_alchemy_connection_string(
            cls, conf: ParamBunch, driver=None, *args, **kwargs):
        """
        the sql alchemy connection string used to connect to the database
        """
        driver = driver or conf.get('driver', cls.default_driver)
        app = cls.value('application_name', kwargs, conf)
        return super().sql_alchemy_connection_string(
            conf, driver=driver, trustservercertificate='yes', app=app,
            **kwargs
        )

    @classmethod
    def jdbc_connection_string(cls, conf: ParamBunch, *args, **kwargs):
        """
        the jdbc connection string used to connect to the database
        """
        port = conf.get('port', cls.default_port)
        params = dict(
            databaseName=f'{conf.name}',
            trustServerCertificate='yes',
            **kwargs,
        )
        params = urllib.parse.urlencode(params)
        return f'jdbc:sqlserver://{conf.host}:{port}?{params}'
