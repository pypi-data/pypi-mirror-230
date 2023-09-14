#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
"""This module contains Huawei Cloud DLI operators."""
from __future__ import annotations

from typing import TYPE_CHECKING, Sequence

from airflow.models import BaseOperator
from airflow.providers.huawei.cloud.hooks.dli import DLIHook

if TYPE_CHECKING:
    pass


class DLICreateQueueOperator(BaseOperator):
    """
    This operator is used to create a queue. The queue will be bound to specified compute resources.

    :param project_id: Specifies the project ID.
    :param queue_name: Name of a newly created resource queue.
    :param cu_count: Minimum number of CUs that are bound to a queue.
        Currently, the value can only be 16, 64, or 256.
    :param platform: CPU architecture of compute resources.
    :param enterprise_project_id: Enterprise project ID.
        The value 0 indicates the default enterprise project.
    :param feature: Indicates the queue feature. The options are as follows:
        basic: basic type
        ai: AI-enhanced (Only the SQL x86_64 dedicated queue supports this option.)
        The default value is basic.
    :param resource_mode: Queue resource mode. The options are as follows:
        0: indicates the shared resource mode.
        1: indicates the exclusive resource mode.
    :param charging_mode: Billing mode of a queue. This value can only be set to 1,
        indicating that the billing is based on the CUH used.
    :param description: Description of a queue.
    :param queue_type: Queue type. The options are as follows:
        sql: Queues used to run SQL jobs. general: Queues used to run Flink and Spark Jar jobs.
    :param list_tags_body: Queue tags for identifying cloud resources. A tag consists of a key and tag value
    :param list_labels_body: Tag information of the queue to be created. Currently, the tag information
        includes whether the queue is cross-AZ (JSON character string). The value can only be 2, that is,
        a dual-AZ queue whose compute resources are distributed in two AZs is created.
    :param elastic_resource_pool_name: Name of a new elastic resource pool. The name can contain only
        digits, lowercase letters, and underscores (), but cannot contain only digits or start with an
        underscore
    :param region: Regions where the API is available.
    :param huaweicloud_conn_id: The Airflow connection used for SMN credentials.
    """

    template_fields: Sequence[str] = (
        "queue_name",
        "cu_count",
        "platform",
        "enterprise_project_id",
        "feature",
        "description",
        "queue_type",
        "elastic_resource_pool_name",
        "project_id",
        "list_tags_body",
        "list_labels_body",
    )
    template_fields_renderers = {"list_tags_body": "json", "list_labels_body": "json"}
    ui_color = "#44b5e2"

    def __init__(
        self,
        queue_name: str,
        cu_count: int,
        project_id: str | None = None,
        platform: str | None = None,
        enterprise_project_id: str | None = None,
        # basic or ai(Only the SQL x86_64 dedicated queue supports this option)
        feature: str | None = None,
        resource_mode: int | None = None,  # 0 Shared or 1 Exclusive
        charging_mode: int | None = None,  # Set only 1
        description: str | None = None,
        queue_type: str | None = None,  # sql or general
        list_tags_body: list | None = None,
        list_labels_body: list | None = None,
        elastic_resource_pool_name: str | None = None,
        region: str | None = None,
        huaweicloud_conn_id: str = "huaweicloud_default",
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)

        self.region = region
        self.project_id = project_id
        self.queue_name = queue_name
        self.cu_count = cu_count
        self.platform = platform
        self.enterprise_project_id = enterprise_project_id
        self.feature = feature
        self.resource_mode = resource_mode
        self.charging_mode = charging_mode
        self.description = description
        self.queue_type = queue_type
        self.list_tags_body = list_tags_body
        self.list_labels_body = list_labels_body
        self.elastic_resource_pool_name = elastic_resource_pool_name
        self.huaweicloud_conn_id = huaweicloud_conn_id

    def execute(self, context):
        dli_hook = DLIHook(
            huaweicloud_conn_id=self.huaweicloud_conn_id, region=self.region, project_id=self.project_id
        )

        return dli_hook.create_queue(
            queue_name=self.queue_name,
            cu_count=self.cu_count,
            platform=self.platform,
            enterprise_project_id=self.enterprise_project_id,
            feature=self.feature,
            resource_mode=self.resource_mode,
            charging_mode=self.charging_mode,
            description=self.description,
            queue_type=self.queue_type,
            list_tags_body=self.list_tags_body,
            list_labels_body=self.list_labels_body,
            elastic_resource_pool_name=self.elastic_resource_pool_name,
        ).to_json_object()


class DLIUpdateQueueCidrOperator(BaseOperator):
    """
    This operator is used to modify the CIDR block of the queues using the yearly/monthly packages.
    If the queue whose CIDR block is to be modified has jobs that are being submitted or running,
    or the queue has been bound to enhanced datasource connections, the CIDR block cannot be modified.

    :param project_id: Specifies the project ID.
    :param queue_name: Name of the queue to be updated.
    :param cidr_in_vpc: VPC CIDR block of the queue.
    :param region: Regions where the API is available.
    :param huaweicloud_conn_id: The Airflow connection used for SMN credentials.
    """

    template_fields: Sequence[str] = ("queue_name", "cidr_in_vpc", "project_id")
    ui_color = "#44b5e2"

    def __init__(
        self,
        queue_name: str,
        cidr_in_vpc: str,
        project_id: str | None = None,
        region: str | None = None,
        huaweicloud_conn_id: str = "huaweicloud_default",
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)

        self.region = region
        self.project_id = project_id
        self.queue_name = queue_name
        self.cidr_in_vpc = cidr_in_vpc
        self.huaweicloud_conn_id = huaweicloud_conn_id

    def execute(self, context):
        dli_hook = DLIHook(
            huaweicloud_conn_id=self.huaweicloud_conn_id, region=self.region, project_id=self.project_id
        )

        return dli_hook.update_queue_cidr(
            queue_name=self.queue_name, cidr_in_vpc=self.cidr_in_vpc
        ).to_json_object()


class DLIDeleteQueueOperator(BaseOperator):
    """
    This operator is used to delete a specified queue.

    :param project_id: Specifies the project ID.
    :param queue_name: Name of the queue to be deleted.
    :param region: Regions where the API is available.
    :param huaweicloud_conn_id: The Airflow connection used for SMN credentials.
    """

    template_fields: Sequence[str] = ("queue_name", "project_id")
    ui_color = "#44b5e2"

    def __init__(
        self,
        queue_name: str,
        project_id: str | None = None,
        region: str | None = None,
        huaweicloud_conn_id: str = "huaweicloud_default",
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)

        self.region = region
        self.project_id = project_id
        self.queue_name = queue_name
        self.huaweicloud_conn_id = huaweicloud_conn_id

    def execute(self, context):
        dli_hook = DLIHook(
            huaweicloud_conn_id=self.huaweicloud_conn_id, region=self.region, project_id=self.project_id
        )

        return dli_hook.delete_queue(queue_name=self.queue_name).to_json_object()


class DLIListQueuesOperator(BaseOperator):
    """
    This operator is used to list all queues under the project.

    :param project_id: Specifies the project ID.
    :param queue_type: Queue type. The options are as follows: sql, general and all.
        If this parameter is not specified, the default value sql is used.
    :param tags: Specifies the message content.
    :param return_billing_info: Regions where the API is available.
    :param return_permission_info: Specifies the message subject, which is used as the email subject when
        you publish email messages.
    :param region: Regions where the API is available.
    :param huaweicloud_conn_id: The Airflow connection used for SMN credentials.
    """

    template_fields: Sequence[str] = ("project_id", "queue_type", "tags")
    ui_color = "#44b5e2"

    def __init__(
        self,
        project_id: str | None = None,
        queue_type: str | None = None,
        tags: str | None = None,
        return_billing_info: bool = False,
        return_permission_info: bool = False,
        region: str | None = None,
        huaweicloud_conn_id: str = "huaweicloud_default",
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)

        self.region = region
        self.project_id = project_id
        self.queue_type = queue_type
        self.tags = tags
        self.return_billing_info = return_billing_info
        self.return_permission_info = return_permission_info
        self.huaweicloud_conn_id = huaweicloud_conn_id

    def execute(self, context):
        dli_hook = DLIHook(
            huaweicloud_conn_id=self.huaweicloud_conn_id, region=self.region, project_id=self.project_id
        )

        list = dli_hook.list_queues(
            queue_type=self.queue_type,
            tags=self.tags,
            return_billing_info=self.return_billing_info,
            return_permission_info=self.return_permission_info,
        ).to_dict()

        return list["queues"]


class DLISparkCreateBatchJobOperator(BaseOperator):
    """
    This operator is used to create a batch processing job in a queue.

    :param project_id: Specifies the project ID.
    :param file: Name of the package that is of the JAR or pyFile type and has been uploaded to the DLI
        resource management system. You can also specify an OBS path, for example,
        obs://Bucket name/Package name.
    :param class_name: Java/Spark main class of the batch processing job.
    :param queue_name: Queue name. Set this parameter to the name of the created DLI queue.
        The queue must be of the general-purpose type. This parameter is compatible with the cluster_name
        parameter. That is, if cluster_name is used to specify a queue, the queue is still valid.
        You are advised to use the queue parameter. The queue and cluster_name parameters cannot coexist.
    :param obs_bucket: OBS bucket for storing the Spark jobs. Set this parameter when you need to save jobs.
    :param catalog_name: To access metadata, set this parameter to dli.
    :param image: Custom image. The format is Organization name/Image name:Image version.
        This parameter is valid only when feature is set to custom. You can use this
        parameter with the feature parameter to specify a user-defined Spark image for job running.
    :param max_retry_times: Maximum retry times. The maximum value is 100, and the default value is 20.
    :param auto_recovery: Whether to enable the retry function. If enabled, Spark jobs will be
        automatically retried after an exception occurs. The default value is false.
    :param spark_version: Version of the Spark component
        If the in-use Spark version is 2.3.2, this parameter is not required.
        If the current Spark version is 2.3.3, this parameter is required when feature is basic or ai.
        If this parameter is not set, the default Spark version 2.3.2 is used.
    :param feature: Job feature. Type of the Spark image used by a job.
        basic: indicates that the basic Spark image provided by DLI is used.
        custom: indicates that the user-defined Spark image is used.
        ai: indicates that the AI image provided by DLI is used.
    :param num_executors: Number of Executors in a Spark application. This configuration item replaces
        the default parameter in sc_type.
    :param executor_cores: Number of CPU cores of each Executor in the Spark application.
        This configuration item replaces the default parameter in sc_type.
    :param executor_memory: Executor memory of the Spark application, for example, 2 GB and 2048 MB.
    :param driver_cores: Number of CPU cores of the Spark application driver. This configuration item
        replaces the default parameter in sc_type.
    :param driver_memory: Driver memory of the Spark application, for example, 2 GB and 2048 MB.
    :param name: Batch processing task name. The value contains a maximum of 128 characters.
    :param list_conf_body: Batch configuration item
    :param list_groups_body: JSON object list, including the package group resource. If the type of the name
        in resources is not verified, the package with the name exists in the group.
    :param list_resources_body: JSON object list, including the name and type of the JSON package that
        has been uploaded to the queue.
    :param list_modules_body: Name of the dependent system resource module.
        You can view the module name using the API related to Querying Resource Packages in a Group.
        DLI provides dependencies for executing datasource jobs. The following table lists the dependency
        modules corresponding to different services.
        CloudTable/MRS HBase: sys.datasource.hbase
        CloudTable/MRS OpenTSDB: sys.datasource.opentsdb
        RDS MySQL: sys.datasource.rds
        RDS Postgre: preset
        DWS: preset
        CSS: sys.datasource.css
    :param list_files_body: Name of the package that is of the file type and has been uploaded to the DLI
        resource management system. You can also specify an OBS path, for example, obs://Bucket name/Package.
    :param list_python_files_body: Name of the package that is of the PyFile type and has been uploaded to
        the DLI resource management system. You can also specify an OBS path, for example,
        obs://Bucket name/Package name.
    :param list_jars_body: Name of the package that is of the JAR type and has been uploaded to the DLI
        resource management system. You can also specify an OBS path, for example, obs://Bucket name/Package.
    :param sc_type: Compute resource type. Currently, resource types A, B, and C are available.
        If this parameter is not specified, the minimum configuration (type A) is used.
    :param list_args_body: Input parameters of the main class, that is, application parameters.
    :param cluster_name: Queue name. Set this parameter to the created DLI queue name.
        You are advised to use the queue parameter. The queue and cluster_name parameters cannot coexist.
    :param region: Regions where the API is available.
    :param huaweicloud_conn_id: The Airflow connection used for SMN credentials.
    """

    template_fields: Sequence[str] = (
        "file",
        "class_name",
        "project_id",
        "queue_name",
        "obs_bucket",
        "catalog_name",
        "image",
        "spark_version",
        "feature",
        "executor_memory",
        "driver_memory",
        "name",
        "sc_type",
        "cluster_name",
        "list_conf_body",
        "list_groups_body",
        "list_resources_body",
        "list_modules_body",
        "list_files_body",
        "list_python_files_body",
        "list_jars_body",
        "list_args_body",
    )
    template_fields_renderers = {
        "list_conf_body": "json",
        "list_groups_body": "json",
        "list_resources_body": "json",
        "list_modules_body": "json",
        "list_files_body": "json",
        "list_python_files_body": "json",
        "list_jars_body": "json",
        "list_args_body": "json",
    }
    ui_color = "#f0eee4"

    def __init__(
        self,
        file: str,
        class_name: str,
        project_id: str | None = None,
        queue_name: str | None = None,
        obs_bucket: str | None = None,
        catalog_name: str | None = None,
        image: str | None = None,
        max_retry_times: int | None = None,
        auto_recovery: bool | None = None,
        spark_version: str | None = None,
        feature: str | None = None,
        num_executors: int | None = None,
        executor_cores: int | None = None,
        executor_memory: str | None = None,
        driver_cores: int | None = None,
        driver_memory: str | None = None,
        name: str | None = None,
        list_conf_body: dict | None = None,
        list_groups_body: list | None = None,
        list_resources_body: list | None = None,
        list_modules_body: list | None = None,
        list_files_body: list | None = None,
        list_python_files_body: list | None = None,
        list_jars_body: list | None = None,
        sc_type: str | None = None,
        list_args_body: list | None = None,
        cluster_name: str | None = None,
        region: str | None = None,
        huaweicloud_conn_id: str = "huaweicloud_default",
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)

        self.region = region
        self.project_id = project_id
        self.queue_name = queue_name
        self.file = file
        self.class_name = class_name
        self.obs_bucket = obs_bucket
        self.catalog_name = catalog_name
        self.image = image
        self.max_retry_times = max_retry_times
        self.auto_recovery = auto_recovery
        self.spark_version = spark_version
        self.feature = feature
        self.num_executors = num_executors
        self.executor_cores = executor_cores
        self.executor_memory = executor_memory
        self.driver_cores = driver_cores
        self.driver_memory = driver_memory
        self.name = name
        self.list_conf_body = list_conf_body
        self.list_groups_body = list_groups_body
        self.list_resources_body = list_resources_body
        self.list_modules_body = list_modules_body
        self.list_files_body = list_files_body
        self.list_python_files_body = list_python_files_body
        self.list_jars_body = list_jars_body
        self.sc_type = sc_type
        self.list_args_body = list_args_body
        self.cluster_name = cluster_name
        self.huaweicloud_conn_id = huaweicloud_conn_id

    def execute(self, context):
        dli_hook = DLIHook(
            huaweicloud_conn_id=self.huaweicloud_conn_id, region=self.region, project_id=self.project_id
        )

        return dli_hook.create_batch_job(
            queue_name=self.queue_name,
            file=self.file,
            class_name=self.class_name,
            auto_recovery=self.auto_recovery,
            catalog_name=self.catalog_name,
            cluster_name=self.cluster_name,
            driver_cores=self.driver_cores,
            driver_memory=self.driver_memory,
            executor_cores=self.executor_cores,
            executor_memory=self.executor_memory,
            feature=self.feature,
            image=self.image,
            list_args_body=self.list_args_body,
            list_conf_body=self.list_conf_body,
            list_files_body=self.list_files_body,
            list_groups_body=self.list_groups_body,
            list_jars_body=self.list_jars_body,
            list_modules_body=self.list_modules_body,
            list_python_files_body=self.list_python_files_body,
            list_resources_body=self.list_resources_body,
            max_retry_times=self.max_retry_times,
            name=self.name,
            num_executors=self.num_executors,
            obs_bucket=self.obs_bucket,
            sc_type=self.sc_type,
            spark_version=self.spark_version,
        ).to_json_object()


class DLIUploadFilesOperator(BaseOperator):
    """
    This operator is used to upload a group of File packages to a project.

    :param project_id: Specifies the project ID.
    :param group: Name of a package group.
    :param paths: List of OBS object paths. The OBS object path refers to the OBS object URL.
    :param region: Regions where the API is available.
    :param huaweicloud_conn_id: The Airflow connection used for SMN credentials.
    """

    template_fields = ("group", "project_id", "paths")
    template_fields_renderers = {"paths": "json"}
    ui_color = "#f0eee4"

    def __init__(
        self,
        group: str,
        paths: list,
        project_id: str | None = None,
        region: str | None = None,
        huaweicloud_conn_id: str = "huaweicloud_default",
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)

        self.region = region
        self.project_id = project_id
        self.group = group
        self.paths = paths
        self.huaweicloud_conn_id = huaweicloud_conn_id

    def execute(self, context):
        dli_hook = DLIHook(
            huaweicloud_conn_id=self.huaweicloud_conn_id, region=self.region, project_id=self.project_id
        )

        return dli_hook.upload_files(group=self.group, paths=self.paths).to_json_object()


class DLIRunSqlJobOperator(BaseOperator):
    """
    This operator is used to submit jobs to a queue using SQL statements.
    The job types support DDL, DCL, IMPORT, QUERY, and INSERT.

    :param project_id: Specifies the project ID.
    :param sql_query: SQL statement that you want to execute.
    :param database_name: Database where the SQL statement is executed. This parameter does not need to be
        configured during database creation.
    :param queue_name: Name of the queue to which a job to be submitted belongs.
        The name can contain only digits, letters, and underscores (_), but cannot contain only digits or
        start with an underscore (_).
    :param list_tags_body: Label of a job.
    :param list_conf_body: You can set the configuration parameters for the SQL job in the form of Key/Value.
    :param region: Regions where the API is available.
    :param huaweicloud_conn_id: The Airflow connection used for SMN credentials.
    """

    template_fields: Sequence[str] = (
        "project_id",
        "sql_query",
        "database_name",
        "queue_name",
        "list_tags_body",
        "list_conf_body",
    )
    template_fields_renderers = {"list_tags_body": "json", "list_conf_body": "json"}
    ui_color = "#f0eee4"

    def __init__(
        self,
        sql_query: str,
        project_id: str | None = None,
        database_name: str | None = None,
        queue_name: str | None = None,
        list_tags_body: list | None = None,
        list_conf_body: list | None = None,
        region: str | None = None,
        huaweicloud_conn_id: str = "huaweicloud_default",
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)

        self.region = region
        self.project_id = project_id
        self.sql_query = sql_query
        self.database_name = database_name
        self.queue_name = queue_name
        self.huaweicloud_conn_id = huaweicloud_conn_id
        self.list_tags_body = list_tags_body
        self.list_conf_body = list_conf_body

    def execute(self, context):
        dli_hook = DLIHook(
            huaweicloud_conn_id=self.huaweicloud_conn_id, region=self.region, project_id=self.project_id
        )

        return dli_hook.run_job(
            sql_query=self.sql_query,
            database_name=self.database_name,
            queue_name=self.queue_name,
            list_tags_body=self.list_tags_body,
            list_conf_body=self.list_conf_body,
        ).to_json_object()


class DLIGetSqlJobResultOperator(BaseOperator):
    """
    This operator is used to view the job execution result after a job is executed using SQL query
    statements. Currently, you can only query execution results of jobs of the QUERY type.

    This API can be used to view only the first 1000 result records and does not support pagination query.
    To view all query results, you need to export the query results first

    :param project_id: Specifies the project ID.
    :param job_id: Job ID
    :param queue_name: Name of the queue to which a job to be submitted belongs.
        The name can contain only digits, letters, and underscores (_), but cannot contain only digits or
        start with an underscore (_).
    :param region: Regions where the API is available.
    :param huaweicloud_conn_id: The Airflow connection used for SMN credentials.
    """

    template_fields: Sequence[str] = ("job_id", "project_id", "queue_name")
    ui_color = "#66c3ff"

    def __init__(
        self,
        job_id: str,
        project_id: str | None = None,
        queue_name: str | None = None,
        region: str | None = None,
        huaweicloud_conn_id: str = "huaweicloud_default",
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)

        self.region = region
        self.project_id = project_id
        self.job_id = job_id
        self.queue_name = queue_name
        self.huaweicloud_conn_id = huaweicloud_conn_id

    def execute(self, context):
        dli_hook = DLIHook(
            huaweicloud_conn_id=self.huaweicloud_conn_id, region=self.region, project_id=self.project_id
        )

        return dli_hook.get_job_result(job_id=self.job_id, queue_name=self.queue_name).to_json_object()
