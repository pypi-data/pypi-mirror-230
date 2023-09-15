import urllib
import urllib.parse
from waddle import ParamBunch

from .base import BaseConnector


class Db2iNative(BaseConnector):
    engine = 'db2+ibm_db_dbi'
    jdbc_class = 'com.ibm.as400.access.AS400JDBCDriver'
    ping_query = 'select current date from sysibm.sysdummy1'

    @classmethod
    def connect(cls, conf: ParamBunch, **kwargs):
        """
        use the appropriate underlying library to connect to the database
        """
        import ibm_db_dbi as db2
        return db2.connect(conn_options=kwargs)

    @classmethod
    def sql_alchemy_connection_string(
            cls, conf: ParamBunch, *args, host=None, **kwargs):
        """
        the sql alchemy connection string used to connect to the database
        """
        return f'{cls.engine}://*LOCAL'

    @classmethod
    def jdbc_connection_string(cls, conf: ParamBunch, *args, **kwargs):
        """
        the jdbc connection string used to connect to the database
        """
        return f'jdbc:as400://{conf.host}'
