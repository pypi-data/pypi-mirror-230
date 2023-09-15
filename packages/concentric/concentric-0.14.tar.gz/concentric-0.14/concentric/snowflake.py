from waddle import ParamBunch

from .base import BaseConnector


class Snowflake(BaseConnector):
    engine = 'snowflake'

    @classmethod
    def connect(cls, conf: ParamBunch, *args, user=None, password=None,
                name=None, **kwargs):
        from snowflake.connector import connect
        name = name or conf.name
        return connect(
            user=user or conf.user,
            password=password or conf.password,
            account=name or conf.name)

    @classmethod
    def sql_alchemy_connection_string(
            cls, conf: ParamBunch, *args,
            user=None, password=None, name=None,
            database=None, schema=None, warehouse=None, **kwargs):
        name = name or conf.name
        pieces = []
        database = database or conf.database
        schema = schema or conf.schema
        warehouse = warehouse or conf.warehouse
        if database:
            pieces.append(database)
            if schema:
                pieces.append(schema)
        junk = '/'.join(pieces)
        suffix = f'{name}/{junk}'
        return super().sql_alchemy_connection_string(
            conf, suffix=suffix, warehouse=warehouse, **kwargs)
