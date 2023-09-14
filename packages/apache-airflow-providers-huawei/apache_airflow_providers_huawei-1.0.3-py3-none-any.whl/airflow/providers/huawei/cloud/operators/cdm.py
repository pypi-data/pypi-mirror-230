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
"""This module contains Huawei Cloud CDM operators."""
from __future__ import annotations

from typing import TYPE_CHECKING, Sequence

from airflow.models import BaseOperator
from airflow.providers.huawei.cloud.hooks.cdm import CDMHook

if TYPE_CHECKING:
    pass


class CDMCreateJobOperator(BaseOperator):
    """
    This operator is used to create a job in a specified cluster.

    :param project_id: Specifies the project ID.
    :param cluster_id: Cluster ID.
    :param jobs: Job list.
    :param region: Regions where the API is available.
    :param huaweicloud_conn_id: The Airflow connection used for CDM credentials.
    """

    template_fields: Sequence[str] = ("cluster_id", "project_id")
    ui_color = "#f0eee4"

    def __init__(
        self,
        cluster_id: str,
        jobs: list,
        project_id: str | None = None,
        region: str | None = None,
        huaweicloud_conn_id: str = "huaweicloud_default",
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)

        self.region = region
        self.project_id = project_id
        self.cluster_id = cluster_id
        self.jobs = jobs
        self.huaweicloud_conn_id = huaweicloud_conn_id

    def execute(self, context):

        cdm_hook = CDMHook(
            huaweicloud_conn_id=self.huaweicloud_conn_id, region=self.region, project_id=self.project_id
        )

        return cdm_hook.create_job(cluster_id=self.cluster_id, jobs=self.jobs).to_json_object()


class CDMCreateAndExecuteJobOperator(BaseOperator):
    """
    This operator is used to create and execute a job in a random cluster.

    :param project_id: Specifies the project ID.
    :param clusters: IDs of CDM clusters. The system selects a random cluster in running
        state from the specified clusters and creates and executes a migration job in the cluster.
    :param x_language: Request language
    :param jobs: Job list.
    :param region: Regions where the API is available.
    :param huaweicloud_conn_id: The Airflow connection used for CDM credentials.
    """

    template_fields: Sequence[str] = ("x_language", "clusters", "project_id")
    ui_color = "#f0eee4"

    def __init__(
        self,
        x_language: str,
        clusters: list,
        jobs: list[dict],
        project_id: str | None = None,
        region: str | None = None,
        huaweicloud_conn_id: str = "huaweicloud_default",
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)

        self.region = region
        self.project_id = project_id
        self.x_language = x_language
        self.clusters = clusters
        self.jobs = jobs
        self.huaweicloud_conn_id = huaweicloud_conn_id

    def execute(self, context):

        cdm_hook = CDMHook(
            huaweicloud_conn_id=self.huaweicloud_conn_id, region=self.region, project_id=self.project_id
        )

        return cdm_hook.create_and_execute_job(
            x_language=self.x_language, clusters=self.clusters, jobs=self.jobs
        ).to_json_object()


class CDMStartJobOperator(BaseOperator):
    """
    This operator is used to start a job.

    :param project_id: Specifies the project ID.
    :param cluster_id: Cluster ID.
    :param job_name: Job name.
    :param region: Regions where the API is available.
    :param huaweicloud_conn_id: The Airflow connection used for CDM credentials.
    """

    template_fields: Sequence[str] = ("cluster_id", "job_name", "project_id")
    ui_color = "#f0eee4"

    def __init__(
        self,
        cluster_id: str,
        job_name: str,
        project_id: str | None = None,
        region: str | None = None,
        huaweicloud_conn_id: str = "huaweicloud_default",
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)

        self.region = region
        self.project_id = project_id
        self.cluster_id = cluster_id
        self.job_name = job_name
        self.huaweicloud_conn_id = huaweicloud_conn_id

    def execute(self, context):

        cdm_hook = CDMHook(
            huaweicloud_conn_id=self.huaweicloud_conn_id, region=self.region, project_id=self.project_id
        )

        return cdm_hook.start_job(cluster_id=self.cluster_id, job_name=self.job_name).to_json_object()


class CDMDeleteJobOperator(BaseOperator):
    """
    This operator is used to delete a job.

    :param project_id: Specifies the project ID.
    :param cluster_id: Cluster ID.
    :param job_name: Job name.
    :param region: Regions where the API is available.
    :param huaweicloud_conn_id: The Airflow connection used for CDM credentials.
    """

    template_fields: Sequence[str] = ("cluster_id", "job_name", "project_id")
    ui_color = "#f0eee4"

    def __init__(
        self,
        cluster_id: str,
        job_name: str,
        project_id: str | None = None,
        region: str | None = None,
        huaweicloud_conn_id: str = "huaweicloud_default",
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)

        self.region = region
        self.project_id = project_id
        self.cluster_id = cluster_id
        self.job_name = job_name
        self.huaweicloud_conn_id = huaweicloud_conn_id

    def execute(self, context):

        cdm_hook = CDMHook(
            huaweicloud_conn_id=self.huaweicloud_conn_id, region=self.region, project_id=self.project_id
        )

        return cdm_hook.delete_job(cluster_id=self.cluster_id, job_name=self.job_name).to_json_object()


class CDMStopJobOperator(BaseOperator):
    """
    This operator is used to stop a job.

    :param project_id: Specifies the project ID.
    :param cluster_id: Cluster ID.
    :param job_name: Job name.
    :param region: Regions where the API is available.
    :param huaweicloud_conn_id: The Airflow connection used for CDM credentials.
    """

    template_fields: Sequence[str] = ("cluster_id", "job_name", "project_id")
    ui_color = "#f0eee4"

    def __init__(
        self,
        cluster_id: str,
        job_name: str,
        region: str | None = None,
        project_id: str | None = None,
        huaweicloud_conn_id: str = "huaweicloud_default",
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)

        self.region = region
        self.project_id = project_id
        self.cluster_id = cluster_id
        self.job_name = job_name
        self.huaweicloud_conn_id = huaweicloud_conn_id

    def execute(self, context):

        cdm_hook = CDMHook(
            huaweicloud_conn_id=self.huaweicloud_conn_id, region=self.region, project_id=self.project_id
        )

        return cdm_hook.stop_job(cluster_id=self.cluster_id, job_name=self.job_name).to_json_object()
