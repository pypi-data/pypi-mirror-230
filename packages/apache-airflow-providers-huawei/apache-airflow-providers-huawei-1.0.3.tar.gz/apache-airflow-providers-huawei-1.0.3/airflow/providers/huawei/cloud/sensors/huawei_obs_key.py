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

from typing import TYPE_CHECKING, Sequence

from airflow.exceptions import AirflowException
from airflow.providers.huawei.cloud.hooks.huawei_obs import OBSHook
from airflow.sensors.base import BaseSensorOperator

if TYPE_CHECKING:
    from airflow.utils.context import Context


class OBSObjectKeySensor(BaseSensorOperator):
    """
    Waits for an object key (a file-like instance on OBS) to be present in an OBS bucket.

    :param huaweicloud_conn_id: The Airflow connection used for OBS credentials.
        If this is None or empty then the default obs behaviour is used. If
        running Airflow in a distributed manner and huaweicloud_conn_id is None or
        empty, then default obs configuration would be used (and must be
        maintained on each worker node).
    :param region: OBS region you want to create bucket.
        By default, the value is obtained from connection corresponding to huaweicloud_conn_id.
        If region is cn-north-1, you can determine whether objects in a bucket in any region exist.
    :param bucket_name: OBS bucket name.
    :param object_key: The key being waited on. Supports full obs:// style url
        or relative path from root level. When it's specified as a full obs://
        url, please leave bucket_name as `None`.
    """

    template_fields: Sequence[str] = ("bucket_name", "object_key")

    def __init__(
        self,
        object_key: str | list[str],
        region: str | None = None,
        bucket_name: str | None = None,
        huaweicloud_conn_id: str = "huaweicloud_default",
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.huaweicloud_conn_id = huaweicloud_conn_id
        self.region = region
        self.bucket_name = bucket_name
        self.object_key = [object_key] if isinstance(object_key, str) else object_key
        self.hook: OBSHook | None = None
        self.object_list = None

    def _check_object_key(self, object_key):
        bucket_name, object_key = OBSHook.get_obs_bucket_object_key(
            self.bucket_name, object_key, "bucket_name", "object_key"
        )
        obs_hook = self.hook if self.hook else self.get_hook()

        if not obs_hook.exist_bucket(bucket_name):
            raise AirflowException(
                f"OBS Bucket with name: {bucket_name} doesn't exist on region: {obs_hook.get_region()}."
            )

        return obs_hook.exist_object(object_key=object_key, bucket_name=bucket_name)

    def poke(self, context: Context):
        """Check if the object exists in the bucket to pull key."""
        return all(self._check_object_key(object_key) for object_key in self.object_key)

    def get_hook(self) -> OBSHook:
        """Create and return an OBSHook."""
        if not self.hook:
            self.hook = OBSHook(huaweicloud_conn_id=self.huaweicloud_conn_id, region=self.region)
        return self.hook
