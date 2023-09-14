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

from typing import TYPE_CHECKING, Sequence

from airflow.compat.functools import cached_property
from airflow.providers.huawei.cloud.hooks.dws import DWSHook
from airflow.sensors.base import BaseSensorOperator

if TYPE_CHECKING:
    from airflow.utils.context import Context


class DWSClusterSensor(BaseSensorOperator):
    """
    Waits for a DWS cluster to reach a specific status.

    :param cluster_name: The name for the cluster being pinged.
    :param target_status: The cluster status desired.
    :param region: The DWS region.
    :param project_id: Project ID.
    :param huaweicloud_conn_id: The Airflow connection used for DWS credentials.
        If this is None or empty then the default obs behaviour is used. If
        running Airflow in a distributed manner and huaweicloud_conn_id is None or
        empty, then default obs configuration would be used (and must be
        maintained on each worker node).
    """

    template_fields: Sequence[str] = ("cluster_name", "target_status")

    def __init__(
        self,
        *,
        cluster_name: str,
        target_status: str = "AVAILABLE",
        region: str | None = None,
        project_id: str | None = None,
        huaweicloud_conn_id: str = "huaweicloud_default",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.cluster_name = cluster_name
        self.target_status = target_status
        self.region = region
        self.project_id = project_id
        self.huaweicloud_conn_id = huaweicloud_conn_id

    def poke(self, context: Context):
        self.log.info("Poking for status : %s\nfor cluster %s", self.target_status, self.cluster_name)
        return self.get_hook.get_cluster_status(self.cluster_name) == self.target_status

    @cached_property
    def get_hook(self) -> DWSHook:
        """Create and return a DWSHook"""
        return DWSHook(
            huaweicloud_conn_id=self.huaweicloud_conn_id, project_id=self.project_id, region=self.region
        )


class DWSSnapshotSensor(BaseSensorOperator):
    """
    Waits for a DWS snapshot to reach a specific status.

    :param snapshot_name: The name for the snapshot being pinged.
    :param target_status: The snapshot status desired.
    :param region: The DWS region.
    :param project_id: Project ID.
    :param huaweicloud_conn_id: The Airflow connection used for DWS credentials.
        If this is None or empty then the default obs behaviour is used. If
        running Airflow in a distributed manner and huaweicloud_conn_id is None or
        empty, then default obs configuration would be used (and must be
        maintained on each worker node).
    """

    template_fields: Sequence[str] = ("snapshot_name", "target_status")

    def __init__(
        self,
        *,
        snapshot_name: str,
        target_status: str = "AVAILABLE",
        region: str | None = None,
        project_id: str | None = None,
        huaweicloud_conn_id: str = "huaweicloud_default",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.snapshot_name = snapshot_name
        self.target_status = target_status
        self.region = region
        self.project_id = project_id
        self.huaweicloud_conn_id = huaweicloud_conn_id

    def poke(self, context: Context):
        self.log.info("Poking for status : %s\nfor snapshot %s", self.target_status, self.snapshot_name)
        return self.get_hook.get_snapshot_status(self.snapshot_name) == self.target_status

    @cached_property
    def get_hook(self) -> DWSHook:
        """Create and return a DWSHook"""
        return DWSHook(
            huaweicloud_conn_id=self.huaweicloud_conn_id, project_id=self.project_id, region=self.region
        )
