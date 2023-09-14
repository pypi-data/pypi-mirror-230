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

from typing import TYPE_CHECKING, Any, Sequence

if TYPE_CHECKING:
    from airflow.utils.context import Context

from airflow.compat.functools import cached_property
from airflow.exceptions import AirflowException
from airflow.providers.huawei.cloud.hooks.cdm import CDMHook
from airflow.sensors.base import BaseSensorOperator


class CDMShowJobStatusSensor(BaseSensorOperator):
    """
    Waits for the process to complete

    :param project_id: Specifies the project ID.
    :param cluster_id: Cluster ID.
    :param job_name: Job name.
    :param region: Regions where the API is available.
    :param huaweicloud_conn_id: The Airflow connection used for CDM credentials.
    """

    INTERMEDIATE_STATES = ("BOOTING", "RUNNING", "UNKNOWN", "NEVER_EXECUTED")
    FAILURE_STATES = ("FAILED", "FAILURE_ON_SUBMIT")
    SUCCESS_STATES = ("SUCCEEDED", "STOPPED")

    template_fields: Sequence[str] = ("cluster_id",)
    template_ext: Sequence[str] = ()
    ui_color = "#66c3ff"

    def __init__(
        self,
        *,
        cluster_id: str,
        job_name: str,
        project_id: str | None = None,
        region: str | None = None,
        huaweicloud_conn_id: str = "huaweicloud_default",
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.huaweicloud_conn_id = huaweicloud_conn_id
        self.cluster_id = cluster_id
        self.job_name = job_name
        self.project_id = project_id
        self.region = region

    def poke(self, context: Context) -> bool:
        """
        Query the job status.
        @param self - the object itself
        @param context - the context of the object
        @returns True if the job status succeeded, False otherwise
        """
        submissions = self.get_hook.show_job_status(cluster_id=self.cluster_id, job_name=self.job_name)

        for submission in submissions:
            if submission["status"] in self.FAILURE_STATES:
                raise AirflowException("CDM sensor failed")

            if submission["status"] in self.INTERMEDIATE_STATES:
                return False
        return True

    @cached_property
    def get_hook(self) -> CDMHook:
        """Create and return a CDMHook"""
        return CDMHook(
            huaweicloud_conn_id=self.huaweicloud_conn_id, project_id=self.project_id, region=self.region
        )
