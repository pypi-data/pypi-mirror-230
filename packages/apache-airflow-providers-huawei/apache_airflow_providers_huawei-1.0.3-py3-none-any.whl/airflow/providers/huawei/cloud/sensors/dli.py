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
from airflow.providers.huawei.cloud.hooks.dli import DLIHook
from airflow.sensors.base import BaseSensorOperator


class DLISparkShowBatchStateSensor(BaseSensorOperator):
    """Sensor for checking the state of a DLI Spark job."""

    INTERMEDIATE_STATES = ("starting", "running", "recovering")
    FAILURE_STATES = ("dead",)
    SUCCESS_STATES = ("success",)

    template_fields: Sequence[str] = ("job_id",)
    template_ext: Sequence[str] = ()
    ui_color = "#66c3ff"

    def __init__(
        self,
        *,
        job_id: str,
        project_id: str | None = None,
        region: str | None = None,
        huaweicloud_conn_id: str = "huaweicloud_default",
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.huaweicloud_conn_id = huaweicloud_conn_id
        self.job_id = job_id
        self.project_id = project_id
        self.region = region

    def poke(self, context: Context) -> bool:
        state = self.get_hook.show_batch_state(job_id=self.job_id)
        if state in self.FAILURE_STATES:
            raise AirflowException("DLI sensor failed")

        if state in self.INTERMEDIATE_STATES:
            return False
        return True

    @cached_property
    def get_hook(self) -> DLIHook:
        """Create and return a DLIHook"""
        return DLIHook(
            huaweicloud_conn_id=self.huaweicloud_conn_id, project_id=self.project_id, region=self.region
        )


class DLISqlShowJobStatusSensor(BaseSensorOperator):
    """Sensor for checking the state of a DLI SQL job."""

    INTERMEDIATE_STATES = ("RUNNING", "SCALING", "LAUNCHING")
    FAILURE_STATES = ("FAILED", "CANCELLED")
    SUCCESS_STATES = ("FINISHED",)

    template_fields: Sequence[str] = ("job_id",)
    template_ext: Sequence[str] = ()
    ui_color = "#66c3ff"

    def __init__(
        self,
        *,
        job_id: str,
        project_id: str | None = None,
        region: str | None = None,
        huaweicloud_conn_id: str = "huaweicloud_default",
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.huaweicloud_conn_id = huaweicloud_conn_id
        self.job_id = job_id
        self.project_id = project_id
        self.region = region

    def poke(self, context: Context) -> bool:
        state = self.get_hook.show_job_status(job_id=self.job_id)
        if state in self.FAILURE_STATES:
            raise AirflowException("DLI sensor failed")

        if state in self.INTERMEDIATE_STATES:
            return False
        return True

    @cached_property
    def get_hook(self) -> DLIHook:
        """Create and return a DLIHook"""
        return DLIHook(
            huaweicloud_conn_id=self.huaweicloud_conn_id, project_id=self.project_id, region=self.region
        )
