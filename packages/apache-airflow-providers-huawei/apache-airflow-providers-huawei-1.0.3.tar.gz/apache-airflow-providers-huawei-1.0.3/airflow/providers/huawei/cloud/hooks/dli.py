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

from __future__ import annotations

import os.path

import huaweicloudsdkdli.v1 as DliSdk
from huaweicloudsdkcore.auth.credentials import BasicCredentials
from huaweicloudsdkdli.v1.region.dli_region import DliRegion

from airflow.exceptions import AirflowException
from airflow.providers.huawei.cloud.hooks.base_huawei_cloud import HuaweiBaseHook


class DLIHook(HuaweiBaseHook):
    """Interact with Huawei Cloud DLI, using the huaweicloudsdkdli library."""

    def create_queue(
        self,
        queue_name,
        platform,
        enterprise_project_id,
        elastic_resource_pool_name,
        feature,
        resource_mode,
        charging_mode,
        description,
        queue_type,
        list_tags_body,
        list_labels_body,
        cu_count,
    ) -> DliSdk.CreateQueueResponse:
        """
        Create a queue in DLI

        :param queue_name: The name of the queue.
        :param platform: The platform of the queue.
        :param enterprise_project_id: The enterprise project ID of the queue.
        :param elastic_resource_pool_name: The elastic resource pool name of the queue.
        :param feature: The feature of the queue.
        :param resource_mode: The resource mode of the queue.
        :param charging_mode: The charging mode of the queue.
        :param description: The description of the queue.
        :param queue_type: The type of the queue.
        :param list_tags_body: The tags of the queue.
        :param list_labels_body: The labels of the queue.
        :param cu_count: The CU count of the queue.
        :return: The response of the queue creation.
        :rtype: DliSdk.CreateQueueResponse
        """
        if list_tags_body is not None and len(list_tags_body) > 10:
            raise AirflowException("You can add up to 10 tags.")
        try:
            return self.get_dli_client().create_queue(
                self.create_queue_request(
                    elastic_resource_pool_name=elastic_resource_pool_name,
                    list_tags_body=list_tags_body,
                    feature=feature,
                    list_labels_body=list_labels_body,
                    resource_mode=resource_mode,
                    platform=platform,
                    enterprise_project_id=enterprise_project_id
                    if enterprise_project_id is not None
                    else self.get_enterprise_project_id_from_extra_data(),
                    charging_mode=charging_mode,
                    cu_count=cu_count,
                    description=description,
                    queue_type=queue_type,
                    queue_name=queue_name,
                )
            )
        except Exception as e:
            self.log.error(e)
            raise AirflowException(f"Errors when creating: {e}")

    def update_queue_cidr(self, queue_name, cidr_in_vpc) -> DliSdk.UpdateQueueCidrResponse:
        """
        Update the CIDR of a queue in DLI

        :param queue_name: The name of the queue.
        :param cidr_in_vpc: The CIDR of the queue.
        :return: The response of the queue update.
        :rtype: DliSdk.UpdateQueueCidrResponse
        """
        try:
            return self.get_dli_client().update_queue_cidr(
                self.update_queue_cidr_request(queue_name=queue_name, cidr_in_vpc=cidr_in_vpc)
            )
        except Exception as e:
            self.log.error(e)
            raise AirflowException(f"Errors when updating: {e}")

    def delete_queue(self, queue_name) -> DliSdk.DeleteQueueResponse:
        """
        Delete a queue in DLI

        :param queue_name: The name of the queue.
        :return: The response of the queue deletion.
        :rtype: DliSdk.DeleteQueueResponse
        """
        try:
            return self.get_dli_client().delete_queue(self.delete_queue_request(queue_name))
        except Exception as e:
            self.log.error(e)
            raise AirflowException(f"Errors when deleting: {e}")

    def list_queues(
        self, queue_type, tags, return_billing_info, return_permission_info
    ) -> DliSdk.ListQueuesResponse:
        """
        List queues in DLI

        :param queue_type: The type of the queue.
        :param tags: The tags of the queue.
        :param return_billing_info: Whether to return billing information.
        :param return_permission_info: Whether to return permission information.
        :return: The response of the queue listing.
        :rtype: DliSdk.ListQueuesResponse
        """
        try:
            return self.get_dli_client().list_queues(
                self.list_queues_request(
                    queue_type=queue_type,
                    tags=tags,
                    return_billing_info=return_billing_info,
                    return_permission_info=return_permission_info,
                )
            )
        except Exception as e:
            self.log.error(e)
            raise AirflowException(f"Errors when listing: {e}")

    def create_batch_job(
        self,
        queue_name,
        file,
        class_name,
        obs_bucket,
        catalog_name,
        image,
        max_retry_times,
        auto_recovery,
        spark_version,
        feature,
        num_executors,
        executor_cores,
        executor_memory,
        driver_cores,
        driver_memory,
        name,
        list_conf_body,
        list_groups_body,
        list_resources_body,
        list_modules_body,
        list_files_body,
        list_python_files_body,
        list_jars_body,
        sc_type,
        list_args_body,
        cluster_name,
    ) -> DliSdk.CreateBatchJobResponse:
        """
        Create a batch job in DLI

        :param queue_name: The name of the queue.
        :param file: The file of the batch job.
        :param class_name: The class name of the batch job.
        :param obs_bucket: The OBS bucket of the batch job.
        :param catalog_name: The catalog name of the batch job.
        :param image: The image of the batch job.
        :param max_retry_times: The maximum retry times of the batch job.
        :param auto_recovery: Whether to enable auto recovery.
        :param spark_version: The Spark version of the batch job.
        :param feature: The feature of the batch job.
        :param num_executors: The number of executors of the batch job.
        :param executor_cores: The number of cores of the executor.
        :param executor_memory: The memory of the executor.
        :param driver_cores: The number of cores of the driver.
        :param driver_memory: The memory of the driver.
        :param name: The name of the batch job.
        :param list_conf_body: The configuration of the batch job.
        :param list_groups_body: The groups of the batch job.
        :param list_resources_body: The resources of the batch job.
        :param list_modules_body: The modules of the batch job.
        :param list_files_body: The files of the batch job.
        :param list_python_files_body: The Python files of the batch job.
        :param list_jars_body: The JAR files of the batch job.
        :param sc_type: The type of the Spark context.
        :param list_args_body: The arguments of the batch job.
        :param cluster_name: The name of the cluster.
        :return: The response of the batch job creation.
        :rtype: DliSdk.CreateBatchJobResponse
        """
        try:
            return self.get_dli_client().create_batch_job(
                self.create_batch_job_request(
                    queue_name=queue_name,
                    file=file,
                    class_name=class_name,
                    obs_bucket=obs_bucket,
                    catalog_name=catalog_name,
                    image=image,
                    max_retry_times=max_retry_times,
                    auto_recovery=auto_recovery,
                    spark_version=spark_version,
                    feature=feature,
                    num_executors=num_executors,
                    executor_cores=executor_cores,
                    executor_memory=executor_memory,
                    driver_cores=driver_cores,
                    driver_memory=driver_memory,
                    name=name,
                    list_conf_body=list_conf_body,
                    list_groups_body=list_groups_body,
                    list_resources_body=list_resources_body,
                    list_modules_body=list_modules_body,
                    list_files_body=list_files_body,
                    list_python_files_body=list_python_files_body,
                    list_jars_body=list_jars_body,
                    sc_type=sc_type,
                    list_args_body=list_args_body,
                    cluster_name=cluster_name,
                )
            )
        except Exception as e:
            self.log.error(e)
            raise AirflowException(f"Errors when crating batch job: {e}")

    def upload_files(self, paths, group) -> DliSdk.UploadFilesResponse:
        """
        Upload files to DLI

        :param paths: The paths of the files to be uploaded.
        :param group: The group of the files to be uploaded.
        :return: The response of the file upload.
        :rtype: DliSdk.UploadFilesResponse
        """
        try:
            return self.get_dli_client().upload_files(self.upload_files_request(paths=paths, group=group))
        except Exception as e:
            self.log.error(e)
            raise AirflowException(f"Errors when uploading files: {e}")

    def run_job(
        self, sql_query, database_name, queue_name, list_conf_body, list_tags_body
    ) -> DliSdk.RunJobResponse:
        """
        Run a job in DLI

        :param sql_query: The SQL query of the job.
        :param database_name: The database name of the job.
        :param queue_name: The queue name of the job.
        :param list_conf_body: The configuration of the job.
        :param list_tags_body: The tags of the job.
        :return: The response of the job run.
        :rtype: DliSdk.RunJobResponse
        """
        try:
            if os.path.isfile(sql_query):
                sql_file = open(sql_query)
                sql_query = sql_file.read()
                sql_file.close()

            return self.get_dli_client().run_job(
                self.run_job_request(
                    sql_query=sql_query,
                    database_name=database_name,
                    list_conf_body=list_conf_body,
                    list_tags_body=list_tags_body,
                    queue_name=queue_name,
                )
            )
        except Exception as e:
            self.log.error(e)
            raise AirflowException(f"Errors when running: {e}")

    def show_batch_state(self, job_id) -> str:
        """
        Get the state of a batch job

        :param job_id: The ID of the batch job.
        :return: The state of the batch job.
        :rtype: str
        """
        try:
            response = self.get_dli_client().show_batch_state(self.show_batch_state_request(job_id))
            return response.state
        except Exception as e:
            self.log.error(e)
            raise AirflowException(f"Errors when get batch state: {e}")

    def show_job_status(self, job_id) -> str:
        """
        Get the status of a job

        :param job_id: The ID of the job.
        :return: The status of the job.
        :rtype: str
        """
        try:
            response = self.get_dli_client().show_job_status(self.show_job_status_request(job_id))
            return response.status
        except Exception as e:
            self.log.error(e)
            raise AirflowException(f"Errors when get job status: {e}")

    def get_dli_client(self) -> DliSdk.DliClient:
        ak = self.conn.login
        sk = self.conn.password

        credentials = BasicCredentials(ak, sk, self.get_project_id())

        return (
            DliSdk.DliClient.new_builder()
            .with_credentials(credentials)
            .with_region(DliRegion.value_of(self.get_region()))
            .build()
        )

    def show_job_status_request(self, job_id):
        return DliSdk.ShowJobStatusRequest(job_id)

    def show_batch_state_request(self, job_id):
        return DliSdk.ShowBatchStateRequest(job_id)

    def run_job_request(self, sql_query, database_name, queue_name, list_conf_body, list_tags_body):
        request = DliSdk.RunJobRequest()
        request.body = DliSdk.CommitJobReq(
            queue_name=queue_name,
            currentdb=database_name,
            sql=sql_query,
            tags=list_tags_body,
            conf=list_conf_body,
        )
        return request

    def upload_files_request(self, paths, group):
        request = DliSdk.UploadFilesRequest()
        request.body = DliSdk.UploadGroupPackageReq(group=group, paths=paths)
        return request

    def create_batch_job_request(
        self,
        queue_name,
        file,
        class_name,
        obs_bucket,
        catalog_name,
        image,
        max_retry_times,
        auto_recovery,
        spark_version,
        feature,
        num_executors,
        executor_cores,
        executor_memory,
        driver_cores,
        driver_memory,
        name,
        list_conf_body,
        list_groups_body,
        list_resources_body,
        list_modules_body,
        list_files_body,
        list_python_files_body,
        list_jars_body,
        sc_type,
        list_args_body,
        cluster_name,
    ):
        request = DliSdk.CreateBatchJobRequest()
        request.body = DliSdk.CreateBatchJobReq(
            queue=queue_name,
            file=file,
            class_name=class_name,
            obs_bucket=obs_bucket,
            catalog_name=catalog_name,
            image=image,
            max_retry_times=max_retry_times,
            auto_recovery=auto_recovery,
            spark_version=spark_version,
            feature=feature,
            num_executors=num_executors,
            executor_cores=executor_cores,
            executor_memory=executor_memory,
            driver_cores=driver_cores,
            driver_memory=driver_memory,
            name=name,
            conf=list_conf_body,
            groups=list_groups_body,
            resources=list_resources_body,
            modules=list_modules_body,
            files=list_files_body,
            python_files=list_python_files_body,
            jars=list_jars_body,
            sc_type=sc_type,
            args=list_args_body,
            cluster_name=cluster_name,
        )
        return request

    def list_queues_request(self, queue_type, tags, return_billing_info, return_permission_info):
        return DliSdk.ListQueuesRequest(
            queue_type=queue_type,
            tags=tags,
            with_charge_info=return_billing_info,
            with_priv=return_permission_info,
        )

    def delete_queue_request(self, queue_name):
        return DliSdk.DeleteQueueRequest(queue_name)

    def update_queue_cidr_request(self, queue_name, cidr_in_vpc):
        request = DliSdk.UpdateQueueCidrRequest()
        request.queue_name = queue_name
        request.body = DliSdk.UpdateQueueCidrReq(cidr_in_vpc=cidr_in_vpc)
        return request

    def create_queue_request(
        self,
        queue_name,
        platform,
        enterprise_project_id,
        elastic_resource_pool_name,
        feature,
        resource_mode,
        charging_mode,
        description,
        queue_type,
        list_tags_body,
        list_labels_body,
        cu_count,
    ):
        request = DliSdk.CreateQueueRequest()
        request.body = DliSdk.CreateQueueReq(
            elastic_resource_pool_name=elastic_resource_pool_name,
            tags=list_tags_body,
            feature=feature,
            labels=list_labels_body,
            resource_mode=resource_mode,
            platform=platform,
            enterprise_project_id=enterprise_project_id,
            charging_mode=charging_mode,
            cu_count=cu_count,
            description=description,
            queue_type=queue_type,
            queue_name=queue_name,
        )
        return request

    def get_job_result(self, job_id, queue_name) -> DliSdk.ShowJobResultResponse:
        try:
            response = self.get_dli_client().show_job_result(self.get_job_result_request(job_id, queue_name))
            return response
        except Exception as e:
            self.log.error(e)
            raise AirflowException(f"Errors when get job result: {e}")

    def get_job_result_request(self, job_id, queue_name):
        request = DliSdk.ShowJobResultRequest(job_id=job_id, queue_name=queue_name)
        return request
