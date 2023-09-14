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

from airflow.models import BaseOperator
from airflow.providers.huawei.cloud.hooks.dws import DWSHook

if TYPE_CHECKING:
    from airflow.utils.context import Context


class DWSCreateClusterOperator(BaseOperator):
    r"""
    Creates a new cluster with the specified parameters.
    The cluster must run in a VPC. Before creating a cluster, you need to create a VPC and obtain the VPC
    and subnet IDs.This API is an asynchronous API. It takes 10 to 15 minutes to create a cluster.

    :param huaweicloud_conn_id: The Airflow connection used for DWS credentials.
        If this is None or empty then the default obs behaviour is used. If
        running Airflow in a distributed manner and huaweicloud_conn_id is None or
        empty, then default obs configuration would be used (and must be
        maintained on each worker node).
    :param project_id: Project ID.
    :param region: The DWS region.
        By default, the value is obtained from connection corresponding to huaweicloud_conn_id.
        Be associated with project_id.
    :param name: Cluster name, which must be unique. The cluster name must contain 4 to 64 characters,
        which must start with a letter. Only letters, digits, hyphens (-), and underscores (_) are allowed.
    :param node_type: The node type to be provisioned for the cluster.
    :param number_of_node: Number of cluster nodes. For a cluster, the value ranges from 3 to 256.
        For a hybrid data warehouse (standalone), the value is 1.
    :param subnet_id: Subnet ID, which is used for configuring cluster network.
    :param security_group_id: ID of a security group, which is used for configuring cluster network.
    :param vpc_id: VPC ID, which is used for configuring cluster network.
    :param availability_zone: AZ of a cluster For details, see Regions and Endpoints.
    :param user_name: Administrator username for logging in to a GaussDB(DWS) cluster.
        The administrator username must:

            - Consist of lowercase letters, digits, or underscores.
            - Start with a lowercase letter or an underscore.
            - Contain 1 to 63 characters.
            - Cannot be a keyword of the GaussDB(DWS) database.
    :param user_pwd: Administrator password for logging in to a GaussDB(DWS) cluster.

        - Contains 8 to 32 characters.
        - Contains at least three types of the following characters: uppercase letters, lowercase letters,
            digits, and special characters (~!?, .:;-_(){}[]/<>@# %^&*+|\=).
        - Cannot be the same as the username or the username written in reverse order.
    :param port: Service port of a cluster. The value ranges from 8000 to 30000. The default value is 8000.
    :param public_bind_type: Binding type of EIP. The value can be one of the following:
        auto_assign, not_use, bind_existing
    :param eip_id: EIP ID
    :param number_of_cn: Number of deployed CNs. The value ranges from 2 to the number of cluster nodes.
        The maximum value is 20 and the default value is 3.
    :param enterprise_project_id: Enterprise project. The default enterprise project ID is 0.
    """

    template_fields: Sequence[str] = (
        "name",
        "node_type",
        "number_of_node",
        "subnet_id",
        "security_group_id",
        "vpc_id",
    )
    ui_color = "#eeaa11"
    ui_fgcolor = "#ffffff"

    def __init__(
        self,
        *,
        name: str,
        node_type: str,
        number_of_node: int,
        subnet_id: str,
        security_group_id: str,
        availability_zone: str | None = None,
        vpc_id: str,
        user_name: str,
        user_pwd: str,
        port: int = 8000,
        public_bind_type: str | None = None,
        eip_id: str | None = None,
        number_of_cn: int | None = None,
        enterprise_project_id: str | None = None,
        region: str | None = None,
        project_id: str | None = None,
        huaweicloud_conn_id: str = "huaweicloud_default",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.name = name
        self.node_type = node_type
        self.number_of_node = number_of_node
        self.subnet_id = subnet_id
        self.security_group_id = security_group_id
        self.availability_zone = availability_zone
        self.vpc_id = vpc_id
        self.user_name = user_name
        self.user_pwd = user_pwd
        self.port = port
        self.public_bind_type = public_bind_type
        self.eip_id = eip_id
        self.number_of_cn = number_of_cn
        self.enterprise_project_id = enterprise_project_id
        self.project_id = project_id
        self.region = region
        self.huaweicloud_conn_id = huaweicloud_conn_id

    def execute(self, context: Context):
        dws_hook = DWSHook(
            huaweicloud_conn_id=self.huaweicloud_conn_id, region=self.region, project_id=self.project_id
        )
        self.log.info("Creating DWS cluster %s", self.name)

        cluster = dws_hook.create_cluster(
            name=self.name,
            node_type=self.node_type,
            number_of_node=self.number_of_node,
            subnet_id=self.subnet_id,
            security_group_id=self.security_group_id,
            availability_zone=self.availability_zone,
            vpc_id=self.vpc_id,
            user_name=self.user_name,
            user_pwd=self.user_pwd,
            port=self.port,
            public_bind_type=self.public_bind_type,
            eip_id=self.eip_id,
            number_of_cn=self.number_of_cn,
            enterprise_project_id=self.enterprise_project_id,
        )
        self.log.info("Created DWS cluster %s", self.name)
        return cluster


class DWSCreateClusterSnapshotOperator(BaseOperator):
    """
    Creates a manual snapshot of the specified cluster. The cluster must be in the available state

    :param huaweicloud_conn_id: The Airflow connection used for DWS credentials.
        If this is None or empty then the default obs behaviour is used. If
        running Airflow in a distributed manner and huaweicloud_conn_id is None or
        empty, then default obs configuration would be used (and must be
        maintained on each worker node).
    :param project_id:     Project ID.
    :param region: The DWS region.
        By default, the value is obtained from connection corresponding to huaweicloud_conn_id.
        Be associated with project_id.
    :param name: Snapshot name, which must be unique and start with a letter.
        It consists of 4 to 64 characters, which are case-insensitive and contain letters, digits,
        hyphens (-), and underscores (_) only.
    :param cluster_name: Cluster name.
    :param description: Snapshot description. If no value is specified, the description is empty.
        Enter a maximum of 256 characters. The following special characters are not allowed: !<>'=&"
    """

    template_fields: Sequence[str] = (
        "name",
        "cluster_name",
    )

    def __init__(
        self,
        *,
        name: str,
        cluster_name: str,
        description: str | None = None,
        region: str | None = None,
        project_id: str | None = None,
        huaweicloud_conn_id: str = "huaweicloud_default",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.name = name
        self.cluster_name = cluster_name
        self.description = description
        self.region = region
        self.project_id = project_id
        self.huaweicloud_conn_id = huaweicloud_conn_id

    def execute(self, context: Context) -> Any:
        dws_hook = DWSHook(
            huaweicloud_conn_id=self.huaweicloud_conn_id, region=self.region, project_id=self.project_id
        )
        return dws_hook.create_snapshot(
            name=self.name,
            cluster_name=self.cluster_name,
            description=self.description,
        )


class DWSDeleteClusterSnapshotOperator(BaseOperator):
    """
    Deletes the specified manual snapshot

    :param huaweicloud_conn_id: The Airflow connection used for DWS credentials.
        If this is None or empty then the default obs behaviour is used. If
        running Airflow in a distributed manner and huaweicloud_conn_id is None or
        empty, then default obs configuration would be used (and must be
        maintained on each worker node).
    :param project_id:     Project ID.
    :param region: The DWS region you want to create cluster.
        By default, the value is obtained from connection corresponding to huaweicloud_conn_id.
        Be associated with project_id.
    :param snapshot_name: Snapshot name.
    """

    template_fields: Sequence[str] = ("snapshot_name",)

    def __init__(
        self,
        *,
        snapshot_name: str,
        region: str | None = None,
        project_id: str | None = None,
        huaweicloud_conn_id: str = "huaweicloud_default",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.snapshot_name = snapshot_name
        self.project_id = project_id
        self.region = region
        self.huaweicloud_conn_id = huaweicloud_conn_id

    def execute(self, context: Context) -> Any:
        dws_hook = DWSHook(
            huaweicloud_conn_id=self.huaweicloud_conn_id, region=self.region, project_id=self.project_id
        )
        dws_hook.delete_snapshot(snapshot_name=self.snapshot_name)


class DWSRestoreClusterOperator(BaseOperator):
    """
    Restore the cluster using a snapshot

    :param huaweicloud_conn_id: The Airflow connection used for DWS credentials.
        If this is None or empty then the default obs behaviour is used. If
        running Airflow in a distributed manner and huaweicloud_conn_id is None or
        empty, then default obs configuration would be used (and must be
        maintained on each worker node).
    :param project_id:     Project ID.
    :param region: The DWS region you want to create cluster.
        By default, the value is obtained from connection corresponding to huaweicloud_conn_id.
        Be associated with project_id.
    :param snapshot_name: Snapshot name.
    :param name: Cluster name, which must be unique. The cluster name must contain 4 to 64 characters,
        which must start with a letter. Only letters, digits, hyphens (-), and underscores (_) are
        allowed.
    :param subnet_id: Subnet ID, which is used for configuring cluster network.
        The default value is the same as that of the original cluster.
    :param security_group_id: Security group ID, which is used for configuring cluster network.
        The default value is the same as that of the original cluster.
    :param vpc_id: VPC ID, which is used for configuring cluster network.
        The default value is the same as that of the original cluster.
    :param availability_zone: AZ of a cluster.
        The default value is the same as that of the original cluster.
    :param port: Service port of a cluster. The value ranges from 8000 to 30000.
        The default value is 8000.
    :param public_bind_type: Binding type of EIP. The value can be one of the following:
        auto_assign, not_use, bind_existing
    :param eip_id: EIP ID.
    :param enterprise_project_id: Enterprise project. The default enterprise project ID is 0.
    """

    template_fields: Sequence[str] = ("snapshot_name", "name")
    ui_color = "#eeaa11"
    ui_fgcolor = "#ffffff"

    def __init__(
        self,
        *,
        snapshot_name: str,
        name: str,
        subnet_id: str | None = None,
        security_group_id: str | None = None,
        vpc_id: str | None = None,
        availability_zone: str | None = None,
        port: int = 8000,
        public_bind_type: str | None = None,
        eip_id: str | None = None,
        enterprise_project_id: str | None = None,
        region: str | None = None,
        project_id: str | None = None,
        huaweicloud_conn_id: str = "huaweicloud_default",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.snapshot_name = snapshot_name
        self.name = name
        self.subnet_id = subnet_id
        self.security_group_id = security_group_id
        self.vpc_id = vpc_id
        self.availability_zone = availability_zone
        self.port = port
        self.public_bind_type = public_bind_type
        self.eip_id = eip_id
        self.enterprise_project_id = enterprise_project_id
        self.project_id = project_id
        self.huaweicloud_conn_id = huaweicloud_conn_id
        self.region = region

    def execute(self, context: Context):
        dws_hook = DWSHook(
            huaweicloud_conn_id=self.huaweicloud_conn_id, region=self.region, project_id=self.project_id
        )
        return dws_hook.restore_cluster(
            snapshot_name=self.snapshot_name,
            name=self.name,
            subnet_id=self.subnet_id,
            security_group_id=self.security_group_id,
            vpc_id=self.vpc_id,
            availability_zone=self.availability_zone,
            port=self.port,
            public_bind_type=self.public_bind_type,
            eip_id=self.eip_id,
            enterprise_project_id=self.enterprise_project_id,
        )


class DWSDeleteClusterBasedOnSnapshotOperator(BaseOperator):
    """
    Delete clusters based on snapshot.Filter by cluster tags.

    :param huaweicloud_conn_id: The Airflow connection used for DWS credentials.
        If this is None or empty then the default obs behaviour is used. If
        running Airflow in a distributed manner and huaweicloud_conn_id is None or
        empty, then default obs configuration would be used (and must be
        maintained on each worker node).
    :param project_id:     Project ID.
    :param region: The DWS region you want to create cluster.
        By default, the value is obtained from connection corresponding to huaweicloud_conn_id.
        Be associated with project_id.
    :param snapshot_name: Snapshot name.
    """

    template_fields: Sequence[str] = ("snapshot_name",)
    ui_color = "#eeaa11"
    ui_fgcolor = "#ffffff"

    def __init__(
        self,
        *,
        snapshot_name: str,
        region: str | None = None,
        project_id: str | None = None,
        huaweicloud_conn_id: str = "huaweicloud_default",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.project_id = project_id
        self.snapshot_name = snapshot_name
        self.huaweicloud_conn_id = huaweicloud_conn_id
        self.region = region

    def execute(self, context: Context):
        dws_hook = DWSHook(
            huaweicloud_conn_id=self.huaweicloud_conn_id, region=self.region, project_id=self.project_id
        )
        return dws_hook.delete_cluster_based_on_snapshot(snapshot_name=self.snapshot_name)


class DWSDeleteClusterOperator(BaseOperator):
    """
    Delete a cluster.

    :param huaweicloud_conn_id: The Airflow connection used for DWS credentials.
        If this is None or empty then the default obs behaviour is used. If
        running Airflow in a distributed manner and huaweicloud_conn_id is None or
        empty, then default obs configuration would be used (and must be
        maintained on each worker node).
    :param project_id:     Project ID.
    :param region: The DWS region you want to create cluster.
        By default, the value is obtained from connection corresponding to huaweicloud_conn_id.
        Be associated with project_id.
    :param cluster_name: Cluster name.
    :param keep_last_manual_snapshot: The number of latest manual snapshots that need to be retained
        for a cluster.
    """

    template_fields: Sequence[str] = ("cluster_name", "keep_last_manual_snapshot")
    ui_color = "#eeaa11"
    ui_fgcolor = "#ffffff"

    def __init__(
        self,
        *,
        cluster_name: str,
        keep_last_manual_snapshot: int,
        region: str | None = None,
        project_id: str | None = None,
        huaweicloud_conn_id: str = "huaweicloud_default",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.project_id = project_id
        self.cluster_name = cluster_name
        self.keep_last_manual_snapshot = keep_last_manual_snapshot
        self.huaweicloud_conn_id = huaweicloud_conn_id
        self.region = region

    def execute(self, context: Context):
        dws_hook = DWSHook(
            huaweicloud_conn_id=self.huaweicloud_conn_id, region=self.region, project_id=self.project_id
        )
        dws_hook.delete_cluster(
            cluster_name=self.cluster_name,
            keep_last_manual_snapshot=self.keep_last_manual_snapshot,
        )
