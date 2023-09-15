import logging

from waddle import ParamBunch

from .odbc import OdbcConnector


log = logging.getLogger(__name__)


class ProgressOpenedge(OdbcConnector):
    default_driver = 'progress_openedge'
    default_port = 8000
    engine = 'progress_openedge'

    @classmethod
    def connect(cls, conf: ParamBunch, *args, name=None,
                host=None, user=None, password=None,
                port=None, **kwargs):
        cls.ensure('driver', kwargs, conf)
        port = port or conf.port or cls.default_port
        user = user or conf.user
        host = host or conf.host
        password = password or conf.password
        kwargs['portnumber'] = port
        kwargs['databasename'] = name or conf.name
        kwargs['uid'] = user
        kwargs['pwd'] = password
        kwargs['hostname'] = host
        return super().connect(conf, **kwargs)
