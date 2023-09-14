
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


Package ``apache-airflow-providers-huawei``

Release: ``1.0.3``


Huawei Cloud integration (including `Huawei Cloud <https://www.huaweicloud.com/intl/en-us/>`__).


Provider package
----------------

This is a provider package for ``huawei`` provider. All classes for this provider package
are in ``airflow.providers.huawei`` python package.

You can find package information and changelog for the provider
in the `documentation <https://airflow.apache.org/docs/apache-airflow-providers-huawei/1.0.3/>`_.


Installation
------------

You can install this package on top of an existing Airflow 2 installation (see ``Requirements`` below
for the minimum Airflow version supported) via
``pip install apache-airflow-providers-huawei``

The package supports the following python versions: 3.7,3.8,3.9,3.10

Requirements
------------

======================  ==================
PIP package             Version required
======================  ==================
``apache-airflow``      ``>=2.5.0``
``psycopg2``            ``>=2.9.4``
``huaweicloudsdkcore``  ``>=3.1.21``
``esdk-obs-python``     ``>=3.22.2``
``huaweicloudsdkdws``   ``>=3.1.21``
``huaweicloudsdksmn``   ``>=3.1.19``
``huaweicloudsdkdli``   ``==3.1.19``
``huaweicloudsdkcdm``   ``>=3.1.19``
``huaweicloudsdkdlf``   ``>=3.1.19``
``huaweicloudsdkiam``   ``>=3.1.19``
======================  ==================

Cross provider package dependencies
-----------------------------------

Those are dependencies that might be needed in order to use all the features of the package.
You need to install the specified provider packages in order to use them.

You can install such cross-provider dependencies when installing from PyPI. For example:

.. code-block:: bash

    pip install apache-airflow-providers-huawei[common.sql]


============================================================================================================  ==============
Dependent package                                                                                             Extra
============================================================================================================  ==============
`apache-airflow-providers-common-sql <https://airflow.apache.org/docs/apache-airflow-providers-common-sql>`_  ``common.sql``
============================================================================================================  ==============

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


.. NOTE TO CONTRIBUTORS:
   Please, only add notes to the Changelog just below the "Changelog" header when there are some breaking changes
   and you want to add an explanation to the users on how they are supposed to deal with them.
   The changelog is updated and maintained semi-automatically by release manager.

Changelog
---------

1.0.3
.....

Bug Fixes
~~~~~~~~~

* ``Fix the DLISparkCreateBatchJobOperator parameter (!17)``

1.0.2
.....

Bug Fixes
~~~~~~~~~

* ``Fix the Connections extra param obs-bucket (!15)``

1.0.1
.....

Bug Fixes
~~~~~~~~~

* ``Fix mistakenly added install_requires for provider (!12)``

1.0.0
.....

Initial version of the provider.
