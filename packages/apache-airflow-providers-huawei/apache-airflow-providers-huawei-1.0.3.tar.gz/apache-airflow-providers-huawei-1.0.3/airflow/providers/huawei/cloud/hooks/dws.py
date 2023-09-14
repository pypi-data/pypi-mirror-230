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

from huaweicloudsdkcore.auth.credentials import BasicCredentials
from huaweicloudsdkcore.exceptions.exceptions import ClientRequestException
from huaweicloudsdkdws.v2 import (
    BatchCreateResourceTag,
    BatchCreateResourceTagRequest,
    BatchCreateResourceTags,
    ClusterInfo,
    CreateClusterInfo,
    CreateClusterRequest,
    CreateClusterRequestBody,
    CreateSnapshotRequest,
    CreateSnapshotRequestBody,
    DeleteClusterRequest,
    DeleteClusterRequestBody,
    DeleteSnapshotRequest,
    ListClusterDetailsRequest,
    ListClustersRequest,
    ListClusterTagsRequest,
    ListSnapshotDetailsRequest,
    ListSnapshotsRequest,
    Restore,
    RestoreClusterRequest,
    RestoreClusterRequestBody,
    Snapshot,
    Snapshots,
)
from huaweicloudsdkdws.v2.dws_client import DwsClient
from huaweicloudsdkdws.v2.model.public_ip import PublicIp
from huaweicloudsdkdws.v2.region.dws_region import DwsRegion

from airflow.exceptions import AirflowException
from airflow.providers.huawei.cloud.hooks.base_huawei_cloud import HuaweiBaseHook


class DWSHook(HuaweiBaseHook):
    """Interact with Huawei Cloud DWS, using the huaweicloudsdkdws library"""

    def get_credential(self) -> tuple:
        """Gets user authentication information from connection."""
        access_key_id = self.conn.login
        access_key_secret = self.conn.password
        if not access_key_id:
            raise Exception(f"No access_key_id is specified for connection: {self.huaweicloud_conn_id}.")

        if not access_key_secret:
            raise Exception(f"No access_key_secret is specified for connection: {self.huaweicloud_conn_id}.")

        return access_key_id, access_key_secret

    def get_dws_client(self) -> DwsClient:
        ak, sk = self.get_credential()
        credentials = BasicCredentials(ak=ak, sk=sk, project_id=self.get_project_id())
        client = (
            DwsClient.new_builder()
            .with_credentials(credentials=credentials)
            .with_region(region=DwsRegion.value_of(region_id=self.get_region()))
            .build()
        )
        return client

    def _list_clusters(self) -> list[ClusterInfo]:
        request = ListClustersRequest()
        return self.get_dws_client().list_clusters(request).clusters

    def _list_snapshots(self) -> list[Snapshots]:
        request = ListSnapshotsRequest()
        return self.get_dws_client().list_snapshots(request).snapshots

    def get_snapshot_tag_clusters(self, snapshot_id: str) -> list[str]:
        clusters = self._list_clusters()
        if not clusters:
            return []
        cluster_ids = []
        for cluster in clusters:
            if not cluster.tags:
                continue
            for tag in cluster.tags:
                if tag.key == "snapshot_id" and snapshot_id in tag.value:
                    cluster_ids.append(cluster.id)
                    break
        return cluster_ids

    def _get_cluster_id(self, cluster_name: str) -> str:
        clusters = self._list_clusters()
        if not clusters:
            raise AirflowException(f"The cluster_name {cluster_name} does not exist.")

        for cluster in clusters:
            if cluster.name == cluster_name:
                return cluster.id
        else:
            raise AirflowException(f"The cluster_name {cluster_name} does not exist.")

    def _get_snapshot_id(self, snapshot_name: str) -> str:
        snapshots = self._list_snapshots()
        if not snapshots:
            raise AirflowException(f"The snapshot_name {snapshot_name} does not exist.")
        for snapshot in snapshots:
            if snapshot.name == snapshot_name:
                return snapshot.id
        else:
            raise AirflowException(f"The snapshot_name {snapshot_name} does not exist.")

    def get_cluster_status(self, cluster_name: str) -> str:
        cluster_id = self._get_cluster_id(cluster_name)
        request = ListClusterDetailsRequest(cluster_id)
        return self.get_dws_client().list_cluster_details(request).cluster.status

    def get_snapshot_status(self, snapshot_name: str) -> str:
        snapshot_id = self._get_snapshot_id(snapshot_name)
        request = ListSnapshotDetailsRequest(snapshot_id)
        return self.get_dws_client().list_snapshot_details(request).snapshot.status

    def create_cluster(
        self,
        name: str,
        node_type: str,
        number_of_node: int,
        subnet_id: str,
        security_group_id: str,
        vpc_id: str,
        user_name: str,
        user_pwd: str,
        port: int = 8000,
        number_of_cn: int | None = None,
        availability_zone: str | None = None,
        enterprise_project_id: str | None = None,
        eip_id: str | None = None,
        public_bind_type: str | None = None,
    ) -> str:
        r"""
        Creates a new cluster with the specified parameters.
        The cluster must run in a VPC. Before creating a cluster, you need to create a VPC and obtain the VPC
        and subnet IDs.This API is an asynchronous API. It takes 10 to 15 minutes to create a cluster.

        :param name: Cluster name, which must be unique. The cluster name must contain 4 to 64 characters,
            which must start with a letter. Only letters, digits, hyphens (-), and underscores (_) are
            allowed.
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
            - Contains at least three types of the following characters: uppercase letters, lowercase
              letters, digits, and special characters (~!?, .:;-_(){}[]/<>@# %^&*+|\=).
            - Cannot be the same as the username or the username written in reverse order.
        :param port: Service port of a cluster. The value ranges from 8000 to 30000.
            The default value is 8000.
        :param public_bind_type: Binding type of EIP. The value can be one of the following: auto_assign,
            not_use, bind_existing
        :param eip_id: EIP ID
        :param number_of_cn: Number of deployed CNs. The value ranges from 2 to the number of cluster nodes.
            The maximum value is 20 and the default value is 3.
        :param enterprise_project_id: Enterprise project. The default enterprise project ID is 0.
        :param project_id:     Project ID
        """
        public_ip = PublicIp(public_bind_type=public_bind_type, eip_id=eip_id) if public_bind_type else None
        cluster_info = CreateClusterInfo(
            name=name,
            node_type=node_type,
            number_of_node=number_of_node,
            number_of_cn=number_of_cn,
            subnet_id=subnet_id,
            security_group_id=security_group_id,
            vpc_id=vpc_id,
            availability_zone=availability_zone,
            port=port,
            user_name=user_name,
            user_pwd=user_pwd,
            public_ip=public_ip,
            enterprise_project_id=enterprise_project_id,
        )

        request = CreateClusterRequest(body=CreateClusterRequestBody(cluster=cluster_info))

        try:
            resp = self.get_dws_client().create_cluster(request)
            self.log.info(resp)
            print(resp.cluster.id)
            return resp.cluster.id
        except ClientRequestException as e:
            self.log.error(e)
            raise e

    def create_snapshot(
        self,
        name: str,
        cluster_name: str,
        description: str | None = None,
    ) -> str:
        """
        Creates a manual snapshot of the specified cluster. The cluster must be in the available state.
        When a snapshot is created, the cluster is labeled.

        :param name: Snapshot name, which must be unique and start with a letter.
            It consists of 4 to 64 characters, which are case-insensitive and contain letters, digits,
            hyphens (-), and underscores (_) only.
        :param cluster_name: Cluster name.
        :param description: Snapshot description. If no value is specified, the description is empty.
            Enter a maximum of 256 characters. The following special characters are not allowed: !<>'=&"
        """
        cluster_state = self.get_cluster_status(cluster_name)
        if cluster_state != "AVAILABLE":
            raise AirflowException(
                "DWS cluster must be in AVAILABLE state. " f"DWS cluster current state is {cluster_state}"
            )

        cluster_id = self._get_cluster_id(cluster_name)
        snapshot_info = Snapshot(name=name, cluster_id=cluster_id, description=description)
        request = CreateSnapshotRequest(body=CreateSnapshotRequestBody(snapshot=snapshot_info))
        try:
            resp = self.get_dws_client().create_snapshot(request)
            self.log.info(resp)

            self.set_cluster_snapshot_tag(cluster_id=cluster_id, snapshot_id=resp.snapshot.id)
            return resp.snapshot.id
        except ClientRequestException as e:
            self.log.error(e)
            raise e

    def delete_snapshot(self, snapshot_name: str) -> None:
        """
        Deletes the specified manual snapshot.

        :param snapshot_name: Snapshot name.
        """
        snapshot_id = self._get_snapshot_id(snapshot_name)
        request = DeleteSnapshotRequest(snapshot_id=snapshot_id)
        resp = self.get_dws_client().delete_snapshot(request)
        self.log.info(resp)

    def delete_cluster(self, cluster_name: str, keep_last_manual_snapshot: int) -> None:
        """
        Delete a cluster.All resources of the deleted cluster, including customer data, will be released.
        For data security, create a snapshot for the cluster that you want to delete before deleting
        the cluster.

        :param cluster_name: Cluster name.
        :param keep_last_manual_snapshot: The number of latest manual snapshots that need to be retained
            for a cluster.
        """
        cluster_id = self._get_cluster_id(cluster_name)
        request = DeleteClusterRequest(
            cluster_id=cluster_id,
            body=DeleteClusterRequestBody(keep_last_manual_snapshot=keep_last_manual_snapshot),
        )
        resp = self.get_dws_client().delete_cluster(request)
        self.log.info(resp)

    def delete_cluster_based_on_snapshot(self, snapshot_name: str) -> None:
        """
        Delete clusters based on snapshot. Filter by cluster tags.

        :param snapshot_name: Snapshot name.
        """
        snapshot_id = self._get_snapshot_id(snapshot_name)
        cluster_ids = self.get_snapshot_tag_clusters(snapshot_id)
        dws_client = self.get_dws_client()
        for cluster_id in cluster_ids:
            request = DeleteClusterRequest(cluster_id=cluster_id, body=DeleteClusterRequestBody(0))
            resp = dws_client.delete_cluster(request)
            self.log.info(resp)

    def restore_cluster(
        self,
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
    ) -> str | None:
        """
        Restore the cluster using a snapshot

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
        snapshot_id = self._get_snapshot_id(snapshot_name)
        snapshot_status = self.get_snapshot_status(snapshot_name)
        if snapshot_status != "AVAILABLE":
            self.log.warning(f"The status of the snapshot is {snapshot_status}, not AVAILABLE.")
            return None
        restore = Restore(
            name=name,
            subnet_id=subnet_id,
            security_group_id=security_group_id,
            vpc_id=vpc_id,
            availability_zone=availability_zone,
            port=port,
            public_ip=PublicIp(public_bind_type=public_bind_type, eip_id=eip_id),
            enterprise_project_id=enterprise_project_id,
        )
        request = RestoreClusterRequest(snapshot_id=snapshot_id, body=RestoreClusterRequestBody(restore))
        try:
            resp = self.get_dws_client().restore_cluster(request)
            self.log.info(resp)
            self.set_cluster_snapshot_tag(cluster_id=resp.cluster.id, snapshot_id=snapshot_id)
            return resp.cluster.id
        except ClientRequestException as e:
            self.log.error(e)
            raise e

    def set_cluster_snapshot_tag(self, cluster_id: str, snapshot_id: str) -> None:
        """Sets a tag for the snapshot ID of the cluster."""
        value = self.get_cluster_snapshot_tag(cluster_id)
        if value and (snapshot_id not in value):
            snapshot_id = "+".join((value, snapshot_id))
        tag = BatchCreateResourceTag(key="snapshot_id", value=snapshot_id)
        tags = BatchCreateResourceTags([tag])
        request = BatchCreateResourceTagRequest(cluster_id=cluster_id, body=tags)
        self.get_dws_client().batch_create_resource_tag(request)

    def get_cluster_snapshot_tag(self, cluster_id) -> str | None:
        """Returns the value of snapshot_id in the cluster tags."""
        request = ListClusterTagsRequest(cluster_id)
        resp = self.get_dws_client().list_cluster_tags(request)
        if not resp.tags:
            return None
        for tag in resp.tags:
            if tag.key == "snapshot_id":
                return tag.value
        return None
