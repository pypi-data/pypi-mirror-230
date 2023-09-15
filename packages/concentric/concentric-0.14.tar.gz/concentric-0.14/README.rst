concentric
==========

a connection manager for python for connecting to various databases.

supported databases:

* oracle
* netsuite
* mssql
* mysql
* vertica
* redshift
* postgres
* db2 i-series

overview
--------

concentric is based off of `waddle <https://pypi.org/project/waddle/>`_ for secrets
management, which means it is strongly coupled to aws kms for its key management.


quick start
-----------

#. create a waddle configuration file

  .. code-block::

         oracle:
           host: localhost
           user: scott
           password: tiger
           sid: xe

#. waddle in the password for security

  .. code-block::

         waddle add-secret -f /path/to/config.yml oracle.password

#. use it

  .. code-block::

         from concentric.managers import setup_concentric
         from concentric.managers import CachingConnectionManager as ccm

         setup_concentric('/path/to/waddle_config.yml', '/path/to/another_config.yml')
         conn = ccm.connect('oracle')
         with conn.cursor() as cursor:
             cursor.execute('select sysdate as dt from dual')
             results = cursor.fetchall()


contributing
------------

Sample configuration files:

#. `db2 <./concentric/example_config/db2.yml>`_
#. `hp3000 <./concentric/example_config/hp3000.yml>`_
#. `mysql <./concentric/example_config/mysql.yml>`_
#. `netsuite <./concentric/example_config/netsuite.yml>`_
#. `oracle <./concentric/example_config/oracle_sid.yml>`_
#. `postgres <./concentric/example_config/postgres.yml>`_
#. `redshift <./concentric/example_config/redshift.yml>`_
#. `snowflake <./concentric/example_config/snowflake.yml>`_
#. `sql server <./concentric/example_config/sql_server.yml>`_
#. `vertica <./concentric/example_config/vertica.yml>`_
