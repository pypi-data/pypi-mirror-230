import sys
from waddle import ParamBunch

from .odbc import OdbcConnector


class Netsuite(OdbcConnector):
    default_trust_store = '/opt/netsuite/odbcclient/cert/ca3.cer'
    default_schema = 'NetSuite2.com'
    default_driver = '{netsuite drivers 64bit}'
    default_port = 1708
    engine = 'pyodbc'

    @classmethod
    def connect(cls, conf: ParamBunch, *args,
                user=None, password=None, host=None, port=None,
                name=None, trust_store=None, driver=None, role_id=None,
                **kwargs):
        user = user or conf.get('user')
        password = password or conf.get('password')
        host = host or conf.get('host')
        port = port or conf.get('port') or cls.default_port
        account_id = host.split('.')[0].replace('-', '_').upper()
        default_trust_store = cls.default_trust_store
        if sys.platform == 'win32':
            default_trust_store = 'system'
        port = f'{port}'
        trust_store = trust_store or conf.trust_store
        trust_store = trust_store or default_trust_store
        name = name or conf.get('name') or cls.default_schema
        driver = driver or conf.get('default_driver') or cls.default_driver
        role_id = role_id or conf.role_id
        return super().connect(
            conf,
            driver=driver,
            host=host,
            port=port,
            truststore=trust_store,
            encrypted=1,
            allowsinglepacketlogout=1,
            sdsn=name,
            uid=user,
            pwd=password,
            customproperties=f'accountid={account_id};roleid={role_id}',
        )

