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

import huaweicloudsdkdlf.v1 as DlfSdk
from huaweicloudsdkcore.auth.credentials import BasicCredentials
from huaweicloudsdkdlf.v1.region.dlf_region import DlfRegion

from airflow.exceptions import AirflowException
from airflow.providers.huawei.cloud.hooks.base_huawei_cloud import HuaweiBaseHook


class DataArtsHook(HuaweiBaseHook):
    """Interact with Huawei Cloud DataArts DLF, using the huaweicloudsdkdlf library."""

    def dlf_start_job(self, workspace, job_name, body) -> DlfSdk.StartJobResponse:
        """
        Start a job in DataArts DLF

        :param workspace: The workspace name.
        :param job_name: The job name.
        :param body: The request body.
        """
        try:
            return self.get_dlf_client().start_job(self.dlf_start_job_request(workspace, job_name, body))
        except Exception as e:
            raise AirflowException(f"Errors when starting: {e}")

    def dlf_show_job_status(self, workspace, job_name) -> str:
        """
        Show the status of a job in DataArts DLF

        :param workspace: The workspace name.
        :param job_name: The job name.
        """
        try:
            return (
                self.get_dlf_client()
                .show_job_status(self.dlf_show_job_status_request(workspace, job_name))
                .to_json_object()["status"]
            )
        except Exception as e:
            raise AirflowException(f"Errors when showing job status: {e}")

    def dlf_list_job_instances(self, workspace) -> list:
        try:
            return (
                self.get_dlf_client()
                .list_job_instances(self.dlf_list_job_instances_request(workspace))
                .instances
            )
        except Exception as e:
            raise AirflowException(f"Errors when listing job instances: {e}")

    def get_dlf_client(self) -> DlfSdk.DlfClient:

        ak = self.conn.login
        sk = self.conn.password

        credentials = BasicCredentials(ak, sk, self.get_project_id())

        return (
            DlfSdk.DlfClient.new_builder()
            .with_credentials(credentials)
            .with_region(DlfRegion.value_of(self.get_region()))
            .build()
        )

    def dlf_start_job_request(self, workspace, job_name, body):
        request = DlfSdk.StartJobRequest(workspace=workspace, job_name=job_name, body=body)
        return request

    def dlf_show_job_status_request(self, workspace, job_name):
        request = DlfSdk.ShowJobStatusRequest(workspace=workspace, job_name=job_name)
        return request

    def dlf_list_job_instances_request(self, workspace):
        request = DlfSdk.ListJobInstancesRequest(workspace=workspace)
        return request
