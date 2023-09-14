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

import huaweicloudsdkcdm.v1 as CdmSdk
from huaweicloudsdkcdm.v1.region.cdm_region import CdmRegion
from huaweicloudsdkcore.auth.credentials import BasicCredentials

from airflow.exceptions import AirflowException
from airflow.providers.huawei.cloud.hooks.base_huawei_cloud import HuaweiBaseHook


class CDMHook(HuaweiBaseHook):
    """Interact with Huawei Cloud CDM, using the huaweicloudsdkcdm library."""

    def create_job(self, cluster_id, jobs) -> CdmSdk.CreateJobResponse:
        """
        Create a job in CDM cluster

        :param cluster_id: The ID of the cluster.
        :param jobs: The job information.
        :return: The response of the create job request.
        :rtype: CdmSdk.CreateJobResponse
        """
        try:
            return self.get_cdm_client().create_job(self.create_job_request(cluster_id=cluster_id, jobs=jobs))
        except Exception as e:
            self.log.error(e)
            raise AirflowException(f"Errors when creating job: {e}")

    def create_and_execute_job(
        self, x_language, clusters, jobs
    ) -> CdmSdk.CreateAndStartRandomClusterJobResponse:
        """
        Create and start a job in CDM cluster

        :param x_language: The language of the request.
        :param clusters: The cluster information.
        :param jobs: The job information.
        :return: The response of the create and start job request.
        :rtype: CdmSdk.CreateAndStartRandomClusterJobResponse
        """
        try:
            return self.get_cdm_client().create_and_start_random_cluster_job(
                self.create_and_execute_job_request(x_language=x_language, clusters=clusters, jobs=jobs)
            )
        except Exception as e:
            self.log.error(e)
            raise AirflowException(f"Errors when creating job: {e}")

    def start_job(self, cluster_id, job_name) -> CdmSdk.StartJobResponse:
        """
        Start a job in CDM cluster

        :param cluster_id: The ID of the cluster.
        :param job_name: The name of the job.
        :return: The response of the start job request.
        :rtype: CdmSdk.StartJobResponse
        """
        try:
            return self.get_cdm_client().start_job(
                self.start_job_request(cluster_id=cluster_id, job_name=job_name)
            )
        except Exception as e:
            self.log.error(e)
            raise AirflowException(f"Errors when starting job: {e}")

    def delete_job(self, cluster_id, job_name) -> CdmSdk.DeleteJobResponse:
        """
        Delete a job in CDM cluster

        :param cluster_id: The ID of the cluster.
        :param job_name: The name of the job.
        :return: The response of the delete job request.
        :rtype: CdmSdk.DeleteJobResponse
        """
        try:
            return self.get_cdm_client().delete_job(
                self.delete_job_request(cluster_id=cluster_id, job_name=job_name)
            )
        except Exception as e:
            self.log.error(e)
            raise AirflowException(f"Errors when deleting job: {e}")

    def stop_job(self, cluster_id, job_name) -> CdmSdk.StopJobResponse:
        """
        Stop a job in CDM cluster

        :param cluster_id: The ID of the cluster.
        :param job_name: The name of the job.
        :return: The response of the stop job request.
        :rtype: CdmSdk.StopJobResponse
        """
        try:
            return self.get_cdm_client().stop_job(
                self.stop_job_request(cluster_id=cluster_id, job_name=job_name)
            )
        except Exception as e:
            self.log.error(e)
            raise AirflowException(f"Errors when stopping job: {e}")

    def show_job_status(self, cluster_id, job_name) -> CdmSdk.ShowJobStatusResponse:
        """
        Show the status of a job in CDM cluster

        :param cluster_id: The ID of the cluster.
        :param job_name: The name of the job.
        :return: The response of the show job status request.
        :rtype: CdmSdk.ShowJobStatusResponse
        """
        try:
            response = (
                self.get_cdm_client()
                .show_job_status(self.show_job_status_request(cluster_id=cluster_id, job_name=job_name))
                .to_json_object()
            )
            return response["submissions"]
        except Exception as e:
            self.log.error(e)
            raise AirflowException(f"Errors when get job status: {e}")

    def create_job_request(self, cluster_id: str, jobs: list[dict]):
        request = CdmSdk.CreateJobRequest(cluster_id=cluster_id, body=CdmSdk.CdmCreateJobJsonReq(jobs))
        return request

    def create_and_execute_job_request(self, x_language: str, clusters: list, jobs: list[dict]):
        request_body = {"jobs": jobs, "clusters": clusters}
        request = CdmSdk.CreateAndStartRandomClusterJobRequest(x_language=x_language, body=request_body)
        return request

    def start_job_request(self, cluster_id, job_name):
        request = CdmSdk.StartJobRequest()
        request.cluster_id = cluster_id
        request.job_name = job_name
        return request

    def delete_job_request(self, cluster_id, job_name):
        request = CdmSdk.DeleteJobRequest()
        request.cluster_id = cluster_id
        request.job_name = job_name
        return request

    def stop_job_request(self, cluster_id, job_name):
        request = CdmSdk.StopJobRequest()
        request.cluster_id = cluster_id
        request.job_name = job_name
        return request

    def show_job_status_request(self, cluster_id, job_name):
        request = CdmSdk.ShowJobStatusRequest()
        request.cluster_id = cluster_id
        request.job_name = job_name
        return request

    def get_cdm_client(self) -> CdmSdk.CdmClient:

        ak = self.conn.login
        sk = self.conn.password

        credentials = BasicCredentials(ak, sk, self.get_project_id())

        return (
            CdmSdk.CdmClient.new_builder()
            .with_credentials(credentials)
            .with_region(CdmRegion.value_of(self.get_region()))
            .build()
        )
