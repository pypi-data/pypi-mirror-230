from sqlalchemy.dialects.oracle.base import OracleDialect
from sqlalchemy.dialects.oracle.cx_oracle import _OracleBINARY_DOUBLE
from sqlalchemy.dialects.oracle.cx_oracle import _OracleBINARY_FLOAT
from sqlalchemy.dialects.oracle.cx_oracle import _OracleInteger
from waddle import ParamBunch

from .base import BaseConnector
from sqlalchemy.dialects.oracle import cx_oracle
from sqlalchemy.dialects import registry
from . import oracle_db_wrapper



class OracleDbDialect(cx_oracle.OracleDialect_cx_oracle):
    def __init__(
            self,
            auto_convert_lobs=True,
            coerce_to_unicode=True,
            coerce_to_decimal=True,
            arraysize=50,
            encoding_errors=None,
            threaded=None,
            **kwargs):
        import oracledb
        OracleDialect.__init__(self, **kwargs)
        self.arraysize = arraysize
        self.encoding_errors = encoding_errors
        if threaded is not None:
            self._cx_oracle_threaded = threaded
        self.auto_convert_lobs = auto_convert_lobs
        self.coerce_to_unicode = coerce_to_unicode
        self.coerce_to_decimal = coerce_to_decimal
        self.dbapi = self.__class__.dbapi()
        if self._use_nchar_for_unicode:
            self.colspecs = self.colspecs.copy()
            self.colspecs[sqltypes.Unicode] = _OracleUnicodeStringNCHAR
            self.colspecs[sqltypes.UnicodeText] = _OracleUnicodeTextNCLOB

        cx_Oracle = self.dbapi

        self._include_setinputsizes = {
            oracledb.DATETIME,
            oracledb.NCLOB,
            oracledb.CLOB,
            oracledb.LOB,
            oracledb.NCHAR,
            oracledb.FIXED_NCHAR,
            oracledb.BLOB,
            oracledb.FIXED_CHAR,
            oracledb.TIMESTAMP,
            _OracleInteger,
            _OracleBINARY_FLOAT,
            _OracleBINARY_DOUBLE,
        }

        self._paramval = lambda value: value.getvalue()

        # https://github.com/oracle/python-cx_Oracle/issues/176#issuecomment-386821291
        # https://github.com/oracle/python-cx_Oracle/issues/224
        self._values_are_lists = False
        self._returningval = self._paramval

        self._is_cx_oracle_6 = True

    @classmethod
    def dbapi(cls):
        import oracledb
        return oracledb

    def do_execute(self, cursor, statement, parameters, context=None):
        if isinstance(statement, bytes):
            statement = statement.decode('utf-8')
        super().do_execute(cursor, statement, parameters, context)


registry.register('oracledb', __name__, 'OracleDbDialect')


class OracleDb(BaseConnector):
    default_port = 1521
    engine = 'oracledb'
    jdbc_class = 'oracle.jdbc.driver.OracleDriver'

    @classmethod
    def connect(cls, conf: ParamBunch, *args,
                user=None, password=None, host=None, port=None,
                schema=None, sid=None, service_name=None,
                dsn=None, **kwargs):
        """
        use the appropriate underlying library to connect to the database
        """
        from oracledb import makedsn, connect as oci_connect  # pylint: disable=E0611
        user = user or conf.get('user')
        password = password or conf.get('password')
        host = host or conf.get('host')
        port = port or conf.get('port') or cls.default_port
        service_name = service_name or conf.get('service_name')
        sid = sid or conf.get('sid')
        dsn = dsn or conf.get('dsn')
        if not dsn:
            if service_name and not sid:
                dsn = makedsn(host, port, service_name=service_name)
            else:
                dsn = makedsn(host, port, sid)
        connection = oci_connect(user=user, password=password, dsn=dsn, **kwargs)
        schema = schema or conf.get('schema')
        if schema:
            with connection.cursor() as cursor:
                cursor.execute(
                    f'alter session set current_schema={schema}'
                    "  nls_date_format='yyyy-mm-dd hh24:mi:ss'"
                    "  nls_timestamp_format='yyyy-mm-dd hh24:mi:ss'"
                )
        else:
            with connection.cursor() as cursor:
                cursor.execute(
                    'alter session set'
                    "  nls_date_format='yyyy-mm-dd hh24:mi:ss'"
                    "  nls_timestamp_format='yyyy-mm-dd hh24:mi:ss'"
                )
        return connection

    @classmethod
    def sql_alchemy_connection_string(
            cls, conf: ParamBunch, *args,
            host=None, port=None, sid=None, service_name=None,
            dsn=None, **kwargs):
        """
        the sql alchemy connection string used to connect to the database
        """
        from cx_Oracle import makedsn
        host = host or conf.get('host')
        port = port or conf.get('port') or cls.default_port
        service_name = conf.get('service_name')
        sid = sid or conf.get('sid')
        dsn = dsn or conf.get('dsn')
        if not dsn:
            if service_name and not dsn:
                dsn = makedsn(host, port, service_name=service_name)
            else:
                dsn = makedsn(host, port, sid)
        return super().sql_alchemy_connection_string(
            conf, suffix=dsn, **kwargs)

    @classmethod
    def jdbc_connection_string(cls, conf: ParamBunch, *args,
                               host=None, port=None, sid=None,
                               service_name=None, dsn=None, **kwargs):
        """
        the jdbc connection string used to connect to the database
        """
        from cx_Oracle import makedsn
        host = host or conf.get('host')
        port = port or conf.get('port') or cls.default_port
        service_name = conf.get('service_name')
        sid = sid or conf.get('sid')
        dsn = dsn or conf.get('dsn')
        if service_name and not dsn:
            dsn = makedsn(conf.host, port, service_name=service_name)
        if dsn:
            return f'jdbc:oracle:thin:@{dsn}'
        return f'jdbc:oracle:thin:@{host}:{port}/{sid}'
