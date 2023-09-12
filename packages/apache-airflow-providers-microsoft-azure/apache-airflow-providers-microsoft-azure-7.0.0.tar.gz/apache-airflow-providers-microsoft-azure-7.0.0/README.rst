
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


Package ``apache-airflow-providers-microsoft-azure``

Release: ``7.0.0``


`Microsoft Azure <https://azure.microsoft.com/>`__


Provider package
----------------

This is a provider package for ``microsoft.azure`` provider. All classes for this provider package
are in ``airflow.providers.microsoft.azure`` python package.

You can find package information and changelog for the provider
in the `documentation <https://airflow.apache.org/docs/apache-airflow-providers-microsoft-azure/7.0.0/>`_.


Installation
------------

You can install this package on top of an existing Airflow 2 installation (see ``Requirements`` below
for the minimum Airflow version supported) via
``pip install apache-airflow-providers-microsoft-azure``

The package supports the following python versions: 3.8,3.9,3.10,3.11

Requirements
------------

================================  ==================
PIP package                       Version required
================================  ==================
``apache-airflow``                ``>=2.4.0``
``azure-batch``                   ``>=8.0.0``
``azure-cosmos``                  ``>=4.0.0``
``azure-mgmt-cosmosdb``
``azure-datalake-store``          ``>=0.0.45``
``azure-identity``                ``>=1.3.1``
``azure-keyvault-secrets``        ``>=4.1.0``
``azure-mgmt-datalake-store``     ``>=0.5.0``
``azure-mgmt-resource``           ``>=2.2.0``
``azure-storage-blob``            ``>=12.14.0``
``azure-mgmt-storage``            ``>=16.0.0``
``azure-storage-file-share``
``azure-servicebus``              ``>=7.6.1``
``azure-synapse-spark``
``adal``                          ``>=1.2.7``
``azure-storage-file-datalake``   ``>=12.9.1``
``azure-kusto-data``              ``>=4.1.0``
``azure-mgmt-containerregistry``  ``>=8.0.0``
``azure-mgmt-containerinstance``  ``>=7.0.0,<9.0.0``
``azure-mgmt-datafactory``        ``>=1.0.0,<2.0``
================================  ==================

Cross provider package dependencies
-----------------------------------

Those are dependencies that might be needed in order to use all the features of the package.
You need to install the specified provider packages in order to use them.

You can install such cross-provider dependencies when installing from PyPI. For example:

.. code-block:: bash

    pip install apache-airflow-providers-microsoft-azure[google]


====================================================================================================  ==========
Dependent package                                                                                     Extra
====================================================================================================  ==========
`apache-airflow-providers-google <https://airflow.apache.org/docs/apache-airflow-providers-google>`_  ``google``
`apache-airflow-providers-oracle <https://airflow.apache.org/docs/apache-airflow-providers-oracle>`_  ``oracle``
`apache-airflow-providers-sftp <https://airflow.apache.org/docs/apache-airflow-providers-sftp>`_      ``sftp``
====================================================================================================  ==========

The changelog for the provider package can be found in the
`changelog <https://airflow.apache.org/docs/apache-airflow-providers-microsoft-azure/7.0.0/changelog.html>`_.