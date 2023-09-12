
.. Licensed to the Apache Software Foundation (ASF) under one
   or more contributor license agreements.  See the NOTICE file
   distributed with this work for additional information
   regarding copyright ownership.  The ASF licenses this file
   to you under the Apache License, Version 2.0 (the
   "License"); you may not use this file except in compliance
   with the License.  You may obtain a copy of the License at

..   http://www.apache.org/licenses/LICENSE-2.0

.. Unless required by applicable law or agreed to in writing,
   software distributed under the License is distributed on an
   "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
   KIND, either express or implied.  See the License for the
   specific language governing permissions and limitations
   under the License.

 .. Licensed to the Apache Software Foundation (ASF) under one
    or more contributor license agreements.  See the NOTICE file
    distributed with this work for additional information
    regarding copyright ownership.  The ASF licenses this file
    to you under the Apache License, Version 2.0 (the
    "License"); you may not use this file except in compliance
    with the License.  You may obtain a copy of the License at

 ..   http://www.apache.org/licenses/LICENSE-2.0

 .. Unless required by applicable law or agreed to in writing,
    software distributed under the License is distributed on an
    "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
    KIND, either express or implied.  See the License for the
    specific language governing permissions and limitations
    under the License.


Package ``apache-airflow-providers-apache-hive``

Release: ``6.1.6``


`Apache Hive <https://hive.apache.org/>`__


Provider package
----------------

This is a provider package for ``apache.hive`` provider. All classes for this provider package
are in ``airflow.providers.apache.hive`` python package.

You can find package information and changelog for the provider
in the `documentation <https://airflow.apache.org/docs/apache-airflow-providers-apache-hive/6.1.6/>`_.


Installation
------------

You can install this package on top of an existing Airflow 2 installation (see ``Requirements`` below
for the minimum Airflow version supported) via
``pip install apache-airflow-providers-apache-hive``

The package supports the following python versions: 3.8,3.9,3.10,3.11

Requirements
------------

=======================================  ==================
PIP package                              Version required
=======================================  ==================
``apache-airflow``                       ``>=2.4.0``
``apache-airflow-providers-common-sql``  ``>=1.3.1``
``hmsclient``                            ``>=0.1.0``
``pandas``                               ``>=0.17.1``
``pyhive[hive_pure_sasl]``               ``>=0.7.0``
``thrift``                               ``>=0.9.2``
=======================================  ==================

Cross provider package dependencies
-----------------------------------

Those are dependencies that might be needed in order to use all the features of the package.
You need to install the specified provider packages in order to use them.

You can install such cross-provider dependencies when installing from PyPI. For example:

.. code-block:: bash

    pip install apache-airflow-providers-apache-hive[amazon]


======================================================================================================================  ===================
Dependent package                                                                                                       Extra
======================================================================================================================  ===================
`apache-airflow-providers-amazon <https://airflow.apache.org/docs/apache-airflow-providers-amazon>`_                    ``amazon``
`apache-airflow-providers-common-sql <https://airflow.apache.org/docs/apache-airflow-providers-common-sql>`_            ``common.sql``
`apache-airflow-providers-microsoft-mssql <https://airflow.apache.org/docs/apache-airflow-providers-microsoft-mssql>`_  ``microsoft.mssql``
`apache-airflow-providers-mysql <https://airflow.apache.org/docs/apache-airflow-providers-mysql>`_                      ``mysql``
`apache-airflow-providers-presto <https://airflow.apache.org/docs/apache-airflow-providers-presto>`_                    ``presto``
`apache-airflow-providers-samba <https://airflow.apache.org/docs/apache-airflow-providers-samba>`_                      ``samba``
`apache-airflow-providers-vertica <https://airflow.apache.org/docs/apache-airflow-providers-vertica>`_                  ``vertica``
======================================================================================================================  ===================

The changelog for the provider package can be found in the
`changelog <https://airflow.apache.org/docs/apache-airflow-providers-apache-hive/6.1.6/changelog.html>`_.