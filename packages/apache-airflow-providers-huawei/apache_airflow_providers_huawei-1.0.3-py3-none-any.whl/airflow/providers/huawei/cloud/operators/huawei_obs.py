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
"""This module contains Huawei Cloud OBS operators."""
from __future__ import annotations

from typing import TYPE_CHECKING, Sequence

from airflow.models import BaseOperator
from airflow.providers.huawei.cloud.hooks.huawei_obs import OBSHook

if TYPE_CHECKING:
    from airflow.utils.context import Context


class OBSCreateBucketOperator(BaseOperator):
    """
    This operator creates an OBS bucket on the region which in the huaweicloud_conn_id

    :param huaweicloud_conn_id: The Airflow connection used for OBS credentials.
        If this is None or empty then the default obs behaviour is used. If
        running Airflow in a distributed manner and huaweicloud_conn_id is None or
        empty, then default obs configuration would be used (and must be
        maintained on each worker node).
    :param region: OBS region you want to create bucket.
        By default, the value is obtained from connection corresponding to huaweicloud_conn_id.
        If cn-north-1 is used, a bucket in any region can be created.
    :param bucket_name: This is bucket name you want to create.
    """

    template_fields: Sequence[str] = ("bucket_name",)

    def __init__(
        self,
        region: str | None = None,
        bucket_name: str | None = None,
        huaweicloud_conn_id: str = "huaweicloud_default",
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.huaweicloud_conn_id = huaweicloud_conn_id
        self.bucket_name = bucket_name
        self.region = region

    def execute(self, context: Context):
        obs_hook = OBSHook(huaweicloud_conn_id=self.huaweicloud_conn_id, region=self.region)
        obs_hook.create_bucket(bucket_name=self.bucket_name)


class OBSListBucketOperator(BaseOperator):
    """
    This operator gets a list of bucket information.
    This operator returns a python list with the information of buckets which can be
    used by `xcom` in the downstream task.

    :param huaweicloud_conn_id: The Airflow connection used for OBS credentials.
        If this is None or empty then the default obs behaviour is used. If
        running Airflow in a distributed manner and huaweicloud_conn_id is None or
        empty, then default obs configuration would be used (and must be
        maintained on each worker node).
    """

    def __init__(
        self,
        region: str | None = None,
        huaweicloud_conn_id: str = "huaweicloud_default",
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.huaweicloud_conn_id = huaweicloud_conn_id

    def execute(self, context: Context):
        obs_hook = OBSHook(huaweicloud_conn_id=self.huaweicloud_conn_id)
        return obs_hook.list_bucket()


class OBSDeleteBucketOperator(BaseOperator):
    """
    This operator to delete an OBS bucket.

    :param huaweicloud_conn_id: The Airflow connection used for OBS credentials.
        If this is None or empty then the default obs behaviour is used. If
        running Airflow in a distributed manner and huaweicloud_conn_id is None or
        empty, then default obs configuration would be used (and must be
        maintained on each worker node).
    :param region: OBS region you want to create bucket.
        By default, the value is obtained from connection corresponding to huaweicloud_conn_id.
        If cn-north-1 is used, a bucket in any region can be deleted.
    :param bucket_name: This is bucket name you want to delete.
    """

    template_fields: Sequence[str] = ("bucket_name",)

    def __init__(
        self,
        region: str | None = None,
        bucket_name: str | None = None,
        huaweicloud_conn_id: str = "huaweicloud_default",
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.huaweicloud_conn_id = huaweicloud_conn_id
        self.region = region
        self.bucket_name = bucket_name

    def execute(self, context: Context):
        obs_hook = OBSHook(huaweicloud_conn_id=self.huaweicloud_conn_id, region=self.region)
        if obs_hook.exist_bucket(self.bucket_name):
            obs_hook.delete_bucket(bucket_name=self.bucket_name)
        else:
            self.log.warning(
                f"OBS Bucket with name: {self.bucket_name} doesn't exist on region: {obs_hook.get_region()}."
            )


class OBSListObjectsOperator(BaseOperator):
    """
    List all objects from the bucket with the given string prefix in name.
    This operator returns a python list with the name of objects which can be
    used by `xcom` in the downstream task.

    :param huaweicloud_conn_id: The Airflow connection used for OBS credentials.
        If this is None or empty then the default obs behaviour is used. If
        running Airflow in a distributed manner and huaweicloud_conn_id is None or
        empty, then default obs configuration would be used (and must be
        maintained on each worker node).
    :param region: OBS region you want to create bucket.
        By default, the value is obtained from connection corresponding to huaweicloud_conn_id.
        If region is cn-north-1, you can list the names of objects in a bucket in any region.
    :param bucket_name: This is bucket name you want to list all objects.
    :param prefix: Name prefix that the objects to be listed must contain.
    :param marker: Object name to start with when listing objects in a bucket.
        All objects are listed in the lexicographical order.
    :param max_keys: Maximum number of objects returned in the response. The value ranges from 1 to 1000.
        If the value is not in this range, 1000 is returned by default.
    :param is_truncated: Whether to enable paging query and list all objects that meet the conditions.
    """

    template_fields: Sequence[str] = (
        "bucket_name",
        "prefix",
        "marker",
        "max_keys",
    )
    ui_color = "#ffd700"

    def __init__(
        self,
        bucket_name: str | None = None,
        region: str | None = None,
        prefix: str | None = None,
        marker: str | None = None,
        max_keys: int | None = None,
        is_truncated: bool | None = False,
        huaweicloud_conn_id: str = "huaweicloud_default",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.huaweicloud_conn_id = huaweicloud_conn_id
        self.region = region
        self.bucket_name = bucket_name
        self.prefix = prefix
        self.marker = marker
        self.max_keys = max_keys
        self.is_truncated = is_truncated

    def execute(self, context: Context):
        obs_hook = OBSHook(huaweicloud_conn_id=self.huaweicloud_conn_id, region=self.region)

        if obs_hook.exist_bucket(self.bucket_name):
            return obs_hook.list_object(
                bucket_name=self.bucket_name,
                prefix=self.prefix,
                marker=self.marker,
                max_keys=self.max_keys,
                is_truncated=self.is_truncated,
            )
        else:
            self.log.warning(
                f"OBS Bucket with name: {self.bucket_name} doesn't exist on region: {obs_hook.get_region()}."
            )
            return None


class OBSGetBucketTaggingOperator(BaseOperator):
    """
    This operator get OBS bucket tagging.

    :param huaweicloud_conn_id: The Airflow connection used for OBS credentials.
        If this is None or empty then the default obs behaviour is used. If
        running Airflow in a distributed manner and huaweicloud_conn_id is None or
        empty, then default obs configuration would be used (and must be
        maintained on each worker node).
    :param region: OBS region you want to create bucket.
        By default, the value is obtained from connection corresponding to huaweicloud_conn_id.
        If region is cn-north-1, you can obtain bucket tagging for any region.
    :param bucket_name: This is bucket name you want to get bucket tagging.
    """

    template_fields: Sequence[str] = ("bucket_name",)

    def __init__(
        self,
        huaweicloud_conn_id: str = "huaweicloud_default",
        region: str | None = None,
        bucket_name: str | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.huaweicloud_conn_id = huaweicloud_conn_id
        self.region = region
        self.bucket_name = bucket_name

    def execute(self, context: Context):
        obs_hook = OBSHook(huaweicloud_conn_id=self.huaweicloud_conn_id, region=self.region)

        if obs_hook.exist_bucket(self.bucket_name):
            return obs_hook.get_bucket_tagging(self.bucket_name)
        else:
            self.log.warning(
                f"OBS Bucket with name: {self.bucket_name} doesn't exist on region: {obs_hook.get_region()}."
            )
            return None


class OBSSetBucketTaggingOperator(BaseOperator):
    """
    This operator set OBS bucket tagging.
    This operator will reset the original bucket tagging.

    :param huaweicloud_conn_id: The Airflow connection used for OBS credentials.
        If this is None or empty then the default obs behaviour is used. If
        running Airflow in a distributed manner and huaweicloud_conn_id is None or
        empty, then default obs configuration would be used (and must be
        maintained on each worker node).
    :param region: OBS region you want to create bucket.
        By default, the value is obtained from connection corresponding to huaweicloud_conn_id.
        If region is cn-north-1, you can set bucket tagging for any region.
    :param bucket_name: This is bucket name you want to set bucket tagging.
    :param tag_info: bucket tagging information.
    """

    template_fields: Sequence[str] = ("bucket_name",)
    template_fields_renderers = {"tag_info": "json"}

    def __init__(
        self,
        tag_info: dict[str, str] | None = None,
        bucket_name: str | None = None,
        huaweicloud_conn_id: str = "huaweicloud_default",
        region: str | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.huaweicloud_conn_id = huaweicloud_conn_id
        self.bucket_name = bucket_name
        self.tag_info = tag_info
        self.region = region

    def execute(self, context: Context):
        obs_hook = OBSHook(huaweicloud_conn_id=self.huaweicloud_conn_id, region=self.region)
        if obs_hook.exist_bucket(self.bucket_name):
            obs_hook.set_bucket_tagging(bucket_name=self.bucket_name, tag_info=self.tag_info)
        else:
            self.log.warning(
                f"OBS Bucket with name: {self.bucket_name} doesn't exist on region: {obs_hook.get_region()}."
            )


class OBSDeleteBucketTaggingOperator(BaseOperator):
    """
    This operator delete OBS bucket tagging

    :param huaweicloud_conn_id: The Airflow connection used for OBS credentials.
        If this is None or empty then the default obs behaviour is used. If
        running Airflow in a distributed manner and huaweicloud_conn_id is None or
        empty, then default obs configuration would be used (and must be
        maintained on each worker node).
    :param region: OBS region you want to create bucket.
        By default, the value is obtained from connection corresponding to huaweicloud_conn_id.
        If region is cn-north-1, you can delete bucket tagging for any region.
    :param bucket_name: This is bucket name you want to delete bucket tagging.
    """

    template_fields: Sequence[str] = ("bucket_name",)

    def __init__(
        self,
        huaweicloud_conn_id: str = "huaweicloud_default",
        region: str | None = None,
        bucket_name: str | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.huaweicloud_conn_id = huaweicloud_conn_id
        self.bucket_name = bucket_name
        self.region = region

    def execute(self, context: Context):
        obs_hook = OBSHook(huaweicloud_conn_id=self.huaweicloud_conn_id, region=self.region)
        if obs_hook.exist_bucket(self.bucket_name):
            obs_hook.delete_bucket_tagging(bucket_name=self.bucket_name)
        else:
            self.log.warning(
                f"OBS Bucket with name: {self.bucket_name} doesn't exist on region: {obs_hook.get_region()}."
            )


class OBSCreateObjectOperator(BaseOperator):
    """
    This operator to create object.

    This operator returns a python list containing the names of failed upload objects,
    which can be used by 'xcom' in downstream tasks.

    :param huaweicloud_conn_id: The Airflow connection used for OBS credentials.
        If this is None or empty then the default obs behaviour is used. If
        running Airflow in a distributed manner and huaweicloud_conn_id is None or
        empty, then default obs configuration would be used (and must be
        maintained on each worker node).
    :param region: OBS region you want to create bucket.
        By default, the value is obtained from connection corresponding to huaweicloud_conn_id.
        If region is cn-north-1, you can create objects in a bucket in any region.
    :param bucket_name: This is bucket name you want to create.
    :param object_key: Object name or the name of the uploaded file.
    :param object_type: The type of the object, default is content.

        - file:
            Full path of the file/folder to be uploaded, for example, /aa/bb.txt, or /aa/.
        - content:
            Upload text to the specified bucket using a string as the data source of the object,
            or upload data to the specified bucket as a network stream or file stream using a
            readable object with a "read" attribute as the data source of the object.
    :param data: Object to be uploaded.
        If data is a folder type, the md5 parameter is ignored.
    :param metadata: Upload custom metadata for the object.
    :param md5: Base64-encoded MD5 value of the object data to be uploaded.
        It is provided for the OBS server to verify data integrity.
    :param acl: Pre-defined Access Control Policies specified during the object upload.
        The access policy is as follows:

            - PRIVATE: Private read/write.
            - PUBLIC_READ: Public read.
            - PUBLIC_READ_WRITE: Public read/write.
            - BUCKET_OWNER_FULL_CONTROL: The owner of a bucket or object has the full control permission on
                the bucket or object.
    :param storage_class: Storage Classes, which can be specified during the object creation.
        The access policy is as follows:

            - STANDARD:
                Standard storage class.
                Features low access latency and high throughput and is applicable
                to storing frequently-accessed (multiple times per month) hotspot
                or small objects (< 1 MB) requiring quick response.
            - WARM:
                Infrequent Access storage class.
                Applicable to storing semi-frequently accessed (less than 12 times a year) data
                requiring quick response.
            - COLD:
                Archive storage class.
                Applicable to archiving rarely-accessed (once a year) data.
    :param expires: Expiration time of an object to be uploaded, in days.
    :param encryption: Algorithm used in SSE-KMS encryption. The value can be:kms
    :param key: The key used in SSE-KMS encryption. The value can be None.
    """

    template_fields: Sequence[str] = ("bucket_name", "object_key", "object_type", "data", "metadata")

    def __init__(
        self,
        object_key: str,
        data: str | object,
        object_type: str | None = "content",
        region: str | None = None,
        bucket_name: str | None = None,
        huaweicloud_conn_id: str = "huaweicloud_default",
        metadata: dict | None = None,
        md5: str | None = None,
        acl: str | None = None,
        encryption: str | None = None,
        key: str | None = None,
        storage_class: str | None = None,
        expires: int | None = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.region = region
        self.object_key = object_key
        self.object_type = object_type
        self.data = data
        self.bucket_name = bucket_name
        self.huaweicloud_conn_id = huaweicloud_conn_id
        self.metadata = metadata
        self.headers = {
            "md5": md5,
            "acl": acl,
            "encryption": encryption,
            "key": key,
            "storageClass": storage_class,
            "expires": expires,
        }
        self.headers = self.headers if any(self.headers.values()) else None

    def execute(self, context: Context):
        obs_hook = OBSHook(huaweicloud_conn_id=self.huaweicloud_conn_id, region=self.region)
        return obs_hook.create_object(
            bucket_name=self.bucket_name,
            object_key=self.object_key,
            object_type=self.object_type,
            data=self.data,
            metadata=self.metadata,
            headers=self.headers,
        )


class OBSGetObjectOperator(BaseOperator):
    """
    This operator to Download an OBS object.

    :param huaweicloud_conn_id: The Airflow connection used for OBS credentials.
        If this is None or empty then the default obs behaviour is used. If
        running Airflow in a distributed manner and huaweicloud_conn_id is None or
        empty, then default obs configuration would be used (and must be
        maintained on each worker node).
    :param region: OBS region you want to create bucket.
        By default, the value is obtained from connection corresponding to huaweicloud_conn_id.
        If region is cn-north-1, you can download an object in a bucket in any region.
    :param bucket_name: The name of the bucket.
    :param object_key: Object name or the name of the file to be downloaded.
    :param download_path: The target path to which the object is downloaded, including the file name,
        for example, aa/bb.txt.When selecting the current directory,
        the path format must specify the current directory, for example, ./xxx.
    """

    ui_color = "#3298ff"
    template_fields: Sequence[str] = ("bucket_name", "object_key", "download_path")

    def __init__(
        self,
        object_key: str,
        download_path: str,
        bucket_name: str | None = None,
        region: str | None = None,
        huaweicloud_conn_id: str = "huaweicloud_default",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.huaweicloud_conn_id = huaweicloud_conn_id
        self.region = region
        self.bucket_name = bucket_name
        self.object_key = object_key
        self.download_path = download_path

    def execute(self, context: Context):
        obs_hook = OBSHook(huaweicloud_conn_id=self.huaweicloud_conn_id, region=self.region)
        return obs_hook.get_object(
            bucket_name=self.bucket_name,
            object_key=self.object_key,
            download_path=self.download_path,
        )


class OBSCopyObjectOperator(BaseOperator):
    """
    This operator to create a copy for an object in a specified bucket.

    :param huaweicloud_conn_id: The Airflow connection used for OBS credentials.
        If this is None or empty then the default obs behaviour is used. If
        running Airflow in a distributed manner and huaweicloud_conn_id is None or
        empty, then default obs configuration would be used (and must be
        maintained on each worker node).
    :param region: OBS region you want to create bucket.
        By default, the value is obtained from connection corresponding to huaweicloud_conn_id.
        Inter-region copy is not supported.
    :param source_object_key: Source object name.
    :param dest_object_key: Target object name.
    :param source_bucket_name: Source bucket name.
    :param dest_bucket_name: Target bucket name.
    :param version_id: Source object version ID.
    :param metadata: Customized metadata of the target object,
        directive in headers needs to be specified as 'REPLACE'.
    :param directive: Whether to copy source object attributes to the target object.
        Possible values are:

            - COPY: Default value; Attributes of the target object are copied from the source object.
            - REPLACE: Attributes of the target object are replaced with values specified in the request
                parameter.
    :param acl: Pre-set access policies, which can be specified during object copy.
        The access policy is as follows:

            - PRIVATE: Private read/write.
            - PUBLIC_READ: Public read.
            - PUBLIC_READ_WRITE: Public read/write.
            - BUCKET_OWNER_FULL_CONTROL: The owner of a bucket or object has the full control permission on
                the bucket or object.
    """

    template_fields: Sequence[str] = (
        "source_object_key",
        "dest_object_key",
        "source_bucket_name",
        "dest_bucket_name",
    )

    def __init__(
        self,
        source_object_key: str,
        dest_object_key: str,
        source_bucket_name: str | None = None,
        dest_bucket_name: str | None = None,
        version_id: str | None = None,
        metadata: dict | None = None,
        directive: str | None = None,
        acl: str | None = None,
        region: str | None = None,
        huaweicloud_conn_id: str = "huaweicloud_default",
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.huaweicloud_conn_id = huaweicloud_conn_id
        self.region = region
        self.source_object_key = source_object_key
        self.dest_object_key = dest_object_key
        self.source_bucket_name = source_bucket_name
        self.dest_bucket_name = dest_bucket_name
        self.version_id = version_id
        self.headers = {
            "directive": directive,
            "acl": acl,
        }
        self.metadata = metadata

    def execute(self, context: Context):
        obs_hook = OBSHook(huaweicloud_conn_id=self.huaweicloud_conn_id, region=self.region)
        obs_hook.copy_object(
            source_object_key=self.source_object_key,
            dest_object_key=self.dest_object_key,
            source_bucket_name=self.source_bucket_name,
            dest_bucket_name=self.dest_bucket_name,
            version_id=self.version_id,
            headers=self.headers,
            metadata=self.metadata,
        )


class OBSDeleteObjectOperator(BaseOperator):
    """
    This operator to delete an object from bucket.

    :param huaweicloud_conn_id: The Airflow connection used for OBS credentials.
        If this is None or empty then the default obs behaviour is used. If
        running Airflow in a distributed manner and huaweicloud_conn_id is None or
        empty, then default obs configuration would be used (and must be
        maintained on each worker node).
    :param region: OBS region you want to create bucket.
        By default, the value is obtained from connection corresponding to huaweicloud_conn_id.
        If region is cn-north-1, an object in a bucket in any region can be deleted.
    :param bucket_name: OBS bucket name
    :param object_key: Object name
    :param version_id:  Version ID
    """

    template_fields: Sequence[str] = (
        "bucket_name",
        "object_key",
        "version_id",
    )

    def __init__(
        self,
        object_key: str,
        bucket_name: str | None = None,
        version_id: str | None = None,
        region: str | None = None,
        huaweicloud_conn_id: str = "huaweicloud_default",
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.huaweicloud_conn_id = huaweicloud_conn_id
        self.region = region
        self.object_key = object_key
        self.bucket_name = bucket_name
        self.version_id = version_id

    def execute(self, context: Context):
        obs_hook = OBSHook(huaweicloud_conn_id=self.huaweicloud_conn_id, region=self.region)
        obs_hook.delete_object(
            object_key=self.object_key,
            bucket_name=self.bucket_name,
            version_id=self.version_id,
        )


class OBSDeleteBatchObjectOperator(BaseOperator):
    """
    This operator to delete objects from a specified bucket in a batch.

    :param huaweicloud_conn_id: The Airflow connection used for OBS credentials.
        If this is None or empty then the default obs behaviour is used. If
        running Airflow in a distributed manner and huaweicloud_conn_id is None or
        empty, then default obs configuration would be used (and must be
        maintained on each worker node).
    :param region: OBS region you want to create bucket.
        By default, the value is obtained from connection corresponding to huaweicloud_conn_id.
        If region is cn-north-1, objects in a bucket in any region can be deleted.
    :param bucket_name: OBS bucket name.
    :param object_list: List of objects to be deleted.
    :param quiet: Response mode of a batch deletion request.
        If this field is set to False, objects involved in the deletion will be returned.
        If this field is set to True, only objects failed to be deleted will be returned.
    """

    template_fields: Sequence[str] = ("bucket_name", "object_list")

    def __init__(
        self,
        object_list: list[str | dict[str, str]],
        bucket_name: str,
        quiet: bool | None = True,
        region: str | None = None,
        huaweicloud_conn_id: str = "huaweicloud_default",
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.huaweicloud_conn_id = huaweicloud_conn_id
        self.region = region
        self.bucket_name = bucket_name
        self.object_list = object_list
        self.quiet = quiet

    def execute(self, context: Context):
        obs_hook = OBSHook(huaweicloud_conn_id=self.huaweicloud_conn_id, region=self.region)
        if obs_hook.exist_bucket(self.bucket_name):
            obs_hook.delete_objects(
                bucket_name=self.bucket_name,
                object_list=self.object_list,
                quiet=self.quiet,
            )
        else:
            self.log.warning(
                f"OBS Bucket with name: {self.bucket_name} doesn't exist on region: {obs_hook.get_region()}."
            )


class OBSMoveObjectOperator(BaseOperator):
    """
    This operator to create a move for an object in a specified bucket.

    :param huaweicloud_conn_id: The Airflow connection used for OBS credentials.
        If this is None or empty then the default obs behaviour is used. If
        running Airflow in a distributed manner and huaweicloud_conn_id is None or
        empty, then default obs configuration would be used (and must be
        maintained on each worker node).
    :param region: OBS region you want to create bucket.
        By default, the value is obtained from connection corresponding to huaweicloud_conn_id.
        Inter-region move is not supported.
    :param source_object_key: Source object name.
    :param dest_object_key: Target object name.
    :param source_bucket_name: Source bucket name.
    :param dest_bucket_name: Target bucket name.
    """

    template_fields: Sequence[str] = (
        "source_bucket_name",
        "dest_bucket_name",
        "source_object_key",
        "dest_object_key",
    )

    def __init__(
        self,
        source_object_key: str,
        dest_object_key: str,
        dest_bucket_name: str,
        source_bucket_name: str | None = None,
        region: str | None = None,
        huaweicloud_conn_id: str = "huaweicloud_default",
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        source_bucket_name = source_bucket_name if source_bucket_name else dest_bucket_name
        self.source_object_key = source_object_key
        self.dest_object_key = dest_object_key
        self.source_bucket_name = source_bucket_name
        self.dest_bucket_name = dest_bucket_name
        self.huaweicloud_conn_id = huaweicloud_conn_id
        self.region = region

    def execute(self, context: Context):
        obs_hook = OBSHook(huaweicloud_conn_id=self.huaweicloud_conn_id, region=self.region)
        if not obs_hook.exist_bucket(self.dest_bucket_name):
            self.log.warning(
                "OBS Bucket with name: %s doesn't exist on region: %s.",
                self.dest_bucket_name,
                obs_hook.get_region(),
            )
            return
        if not obs_hook.exist_bucket(self.source_bucket_name):
            self.log.warning(
                "OBS Bucket with name: %s doesn't exist on region: %s.",
                self.source_bucket_name,
                obs_hook.get_region(),
            )
            return

        obs_hook.move_object(
            source_bucket_name=self.source_bucket_name,
            dest_bucket_name=self.dest_bucket_name,
            source_object_key=self.source_object_key,
            dest_object_key=self.dest_object_key,
        )
