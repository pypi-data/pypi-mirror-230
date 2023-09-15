from waddle import ParamBunch

from .base import BaseConnector


class Oracle(BaseConnector):
    default_port = 1521
    engine = 'oracle+cx_oracle'
    jdbc_class = 'oracle.jdbc.driver.OracleDriver'

    @classmethod
    def connect(cls, conf: ParamBunch, *args,
                user=None, password=None, host=None, port=None,
                schema=None, sid=None, service_name=None,
                dsn=None, **kwargs):
        """
        use the appropriate underlying library to connect to the database
        """
        from cx_Oracle import makedsn, connect as oci_connect  # pylint: disable=E0611
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
        connection = oci_connect(user, password, dsn, **kwargs)
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
