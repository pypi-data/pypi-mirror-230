import urllib
import urllib.parse
from waddle import ParamBunch

from .odbc import OdbcConnector


class Db2i(OdbcConnector):
    engine = 'ibmi'
    jdbc_class = 'com.ibm.as400.access.AS400JDBCDriver'
    default_driver = 'IBM i Access ODBC Driver 64-bit'
    ping_query = 'select current date from sysibm.sysdummy1'
    default_port = 448
    default_trimchar = 1
    default_ssl = 0

    @classmethod
    def connect(cls, conf: ParamBunch, *args, 
                user=None, password=None, host=None,
                driver=None, port=None, **kwargs):
        """
        use the appropriate underlying library to connect to the database
        """
        driver = driver or conf.get('driver', cls.default_driver)
        port = port or conf.get('port', 448)
        host = host or conf.get('host')
        user = user or conf.get('user')
        password = password or conf.get('password')
        cls.ensure('ssl', kwargs, conf)
        cls.ensure('trimchar', kwargs, conf)
        return super().connect(
            conf, driver=driver, system=host, port=f'{port}',
            uid=user, pwd=password, **kwargs
        )

    @classmethod
    def sql_alchemy_connection_string(
            cls, conf: ParamBunch, *args, host=None, **kwargs):
        """
        the sql alchemy connection string used to connect to the database
        """
        host = host or conf.host
        trim_char = cls.value('trimchar', kwargs, conf)
        cls.ensure('ssl', kwargs, conf)
        return super().sql_alchemy_connection_string(
            conf, suffix=f'{host}/', trim_char_fields=trim_char, **kwargs
        )

    @classmethod
    def jdbc_connection_string(cls, conf: ParamBunch, *args, **kwargs):
        """
        the jdbc connection string used to connect to the database
        """
        return f'jdbc:as400://{conf.host}'
