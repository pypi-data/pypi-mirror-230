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

import json
from functools import wraps
from inspect import signature
from typing import Any, Callable, TypeVar, cast
from urllib.parse import urlsplit

from obs import (
    CopyObjectHeader,
    DeleteObjectsRequest,
    Object,
    ObsClient,
    PutObjectHeader,
    SseKmsHeader,
    Tag,
    TagInfo,
)
from obs.bucket import BucketClient

from airflow.exceptions import AirflowException
from airflow.providers.huawei.cloud.hooks.base_huawei_cloud import HuaweiBaseHook

T = TypeVar("T", bound=Callable)


def provide_bucket_name(func: T) -> T:
    """
    Function decorator that provides a bucket name taken from the connection
    in case no bucket name has been passed to the function.
    """
    function_signature = signature(func)

    @wraps(func)
    def wrapper(*args, **kwargs) -> T:
        bound_args = function_signature.bind(*args, **kwargs)
        self = args[0]
        if bound_args.arguments.get("bucket_name") is None and self.huaweicloud_conn_id:
            connection = self.get_connection(self.huaweicloud_conn_id)
            if connection.extra_dejson.get("obs_bucket", None):
                bound_args.arguments["bucket_name"] = extra_dejson.get("obs_bucket")

        return func(*bound_args.args, **bound_args.kwargs)

    return cast(T, wrapper)


def unify_bucket_name_and_key(func: T) -> T:
    """
    Function decorator that unifies bucket name and object_key taken from the object_key
    in case no bucket name and at least an object_key has been passed to the function.
    """
    function_signature = signature(func)

    @wraps(func)
    def wrapper(*args, **kwargs) -> T:
        bound_args = function_signature.bind(*args, **kwargs)

        def get_key() -> str:
            if "object_key" in bound_args.arguments:
                return "object_key"
            raise ValueError("Missing object_key parameter!")

        key_name = get_key()
        if "bucket_name" not in bound_args.arguments or bound_args.arguments["bucket_name"] is None:
            bound_args.arguments["bucket_name"], bound_args.arguments["object_key"] = OBSHook.parse_obs_url(
                bound_args.arguments[key_name]
            )

        return func(*bound_args.args, **bound_args.kwargs)

    return cast(T, wrapper)


def get_err_info(resp):
    return json.dumps(
        {
            "status": resp.status,
            "reason": resp.reason,
            "errorCode": resp.errorCode,
            "errorMessage": resp.errorMessage,
        }
    )


class OBSHook(HuaweiBaseHook):
    """Interact with Huawei Cloud OBS, using the obs library."""

    @staticmethod
    def parse_obs_url(obsurl: str) -> tuple:
        """
        Parses the OBS Url into a bucket name and object key.

        :param obsurl: The OBS Url to parse.
        :return: the parsed bucket name and object key.
        """
        parsed_url = urlsplit(obsurl)
        if not parsed_url.netloc:
            raise AirflowException(f"Please provide a bucket_name instead of '{obsurl}'.")

        bucket_name = parsed_url.netloc.split(".", 1)[0]
        object_key = parsed_url.path.lstrip("/")

        return bucket_name, object_key

    @staticmethod
    def get_obs_bucket_object_key(
        bucket_name: str | None, object_key: str, bucket_param_name: str, object_key_param_name: str
    ) -> tuple:
        """
        Get the OBS bucket name and object key from either:
            - bucket name and object key. Return the info as it is after checking `object_key` is a relative
              path.
            - object key. Must be a full obs:// url

        :param bucket_name: The OBS bucket name.
        :param object_key: The OBS object key.
        :param bucket_param_name: The parameter name containing the bucket name.
        :param object_key_param_name: The parameter name containing the object key name.
        :return: the parsed bucket name and object key.
        """
        if bucket_name is None:
            return OBSHook.parse_obs_url(object_key)

        parsed_url = urlsplit(object_key)
        if parsed_url.scheme != "" or parsed_url.netloc != "":
            raise TypeError(
                f"If `{bucket_param_name}` is provided, {object_key_param_name} should be a relative path "
                "from root level, rather than a full obs:// url."
            )

        return bucket_name, object_key

    def get_obs_client(self) -> ObsClient:
        """
        Gets an OBS client to manage resources on OBS services such as buckets and objects.
        Returns an OBS Client.

        """
        auth = self.get_credential()
        access_key_id, secret_access_key = auth
        region = self.get_region()
        server = f"https://obs.{region}.myhuaweicloud.com"
        return ObsClient(access_key_id=access_key_id, secret_access_key=secret_access_key, server=server)

    @provide_bucket_name
    def get_bucket_client(self, bucket_name: str | None = None) -> BucketClient:
        """
        Returns an OBS bucket client object.

        :param bucket_name: the name of the bucket.
        :return: the bucket object to the bucket name.
        """
        return self.get_obs_client().bucketClient(bucket_name)

    @provide_bucket_name
    def create_bucket(self, bucket_name: str | None = None) -> None:
        """
        Create a bucket.

        :param bucket_name: The name of the bucket.
        """
        bucket_client = self.get_bucket_client(bucket_name)
        if bucket_client.headBucket().status < 300:
            raise AirflowException(f"The OBS bucket named {bucket_name} already exists.")

        try:
            resp = bucket_client.createBucket(location=self.get_region())
            if resp.status < 300:
                self.log.info("Created OBS bucket with name: %s.", bucket_name)
            else:
                e = get_err_info(resp)
                self.log.error("Error message when creating a bucket: %s.", e)
                raise AirflowException(e)
        except Exception as e:
            raise AirflowException(f"Errors when create bucket {bucket_name}({e}).")

    def list_bucket(self) -> list[dict[str, Any]] | None:
        """Gets a list of bucket information."""
        try:
            resp = self.get_obs_client().listBuckets()
            if resp.status < 300:
                buckets = []
                for bucket in resp.body.buckets:
                    buckets.append(
                        {
                            "name": bucket.name,
                            "region": bucket.location,
                            "create_date": bucket.create_date,
                            "bucket_type": bucket.bucket_type,
                        }
                    )
                return buckets
            else:
                e = get_err_info(resp)
                self.log.error("Error message when getting a list of bucket information: %s.", e)
                raise AirflowException(e)
        except Exception as e:
            raise AirflowException(f"Errors when list bucket({e}).")

    @provide_bucket_name
    def exist_bucket(self, bucket_name) -> bool:
        """
        Check whether the bucket exists.

        :param bucket_name: The name of the bucket.
        """
        resp = self.get_bucket_client(bucket_name).headBucket()

        if resp.status < 300:
            return True
        elif resp.status == 404:
            self.log.info("Bucket %s does not exist.", bucket_name)
        elif resp.status == 403:
            self.log.error(get_err_info(resp))
        return False

    @provide_bucket_name
    def delete_bucket(
        self,
        bucket_name: str | None = None,
    ) -> None:
        """
        Delete bucket from OBS.
        Non-empty buckets cannot be deleted directly.

        :param bucket_name: the name of the bucket.
        """
        try:
            resp = self.get_bucket_client(bucket_name).deleteBucket()
            if resp.status < 300:
                self.log.info("Deleted OBS bucket: %s.", bucket_name)
            else:
                e = get_err_info(resp)
                self.log.error("Error message when deleting a bucket: %s.", e)
                raise AirflowException(e)
        except Exception as e:
            raise AirflowException(f"Errors when deleting {bucket_name}({e})")

    @provide_bucket_name
    def get_bucket_tagging(
        self,
        bucket_name: str | None = None,
    ) -> list[dict[str, str]]:
        """
        Get bucket tagging from OBS.

        :param bucket_name: the name of the bucket.
        """
        try:
            resp = self.get_bucket_client(bucket_name).getBucketTagging()
            if resp.status < 300:
                tag_info = [{"tag": tag.key, "value": tag.value} for tag in resp.body.tagSet]
                self.log.info("Getting the bucket tagging succeeded. %s", tag_info)
                return tag_info
            else:
                e = get_err_info(resp)
                self.log.error("Error message when obtaining the bucket label: %s.", e)
                raise AirflowException(e)
        except Exception as e:
            raise AirflowException(f"Errors when getting the bucket tagging of {bucket_name}({e}).")

    @provide_bucket_name
    def set_bucket_tagging(
        self,
        tag_info: dict[str, str] | None = None,
        bucket_name: str | None = None,
    ) -> None:
        """
        Set bucket tagging from OBS.

        :param bucket_name: the name of the bucket.
        :param tag_info: bucket tagging information.
        """
        if not tag_info:
            self.log.warning("No 'tag_info' information was passed.")
            return
        tags = [Tag(key=tag, value=str(tag_info[tag])) for tag in tag_info]
        tag_info = TagInfo(tags)

        try:
            resp = self.get_bucket_client(bucket_name).setBucketTagging(tagInfo=tag_info)
            if resp.status < 300:
                self.log.info("Setting the bucket tagging succeeded.")
            else:
                e = get_err_info(resp)
                self.log.error("Error message when setting the bucket tagging: %s.", e)
                raise AirflowException(e)
        except Exception as e:
            raise AirflowException(f"Errors when setting the bucket tagging of {bucket_name}({e}).")

    @provide_bucket_name
    def delete_bucket_tagging(
        self,
        bucket_name: str | None = None,
    ) -> None:
        """
        Delete bucket tagging from OBS.

        :param bucket_name: the name of the bucket.
        """
        try:
            resp = self.get_bucket_client(bucket_name).deleteBucketTagging()
            if resp.status < 300:
                self.log.info("Deleting the bucket label succeeded.")
            else:
                e = get_err_info(resp)
                self.log.error("Error message when Deleting the bucket tagging: %s.", e)
                raise AirflowException(e)
        except Exception as e:
            raise AirflowException(f"Errors when deleting the bucket tagging of {bucket_name}({e}).")

    def exist_object(
        self,
        object_key: str,
        bucket_name: str | None = None,
    ) -> bool:
        """
        Check whether the object in the bucket exists

        :param bucket_name: bucket name.
        :param object_key: object key.
        """
        bucket_name, object_key = OBSHook.get_obs_bucket_object_key(
            bucket_name, object_key, "bucket_name", "object_key"
        )
        resp = self.get_bucket_client(bucket_name).headObject(object_key)
        if resp.status < 300:
            return True
        self.log.error("Error message when checking the object: %s", get_err_info(resp))
        return False

    @provide_bucket_name
    def list_object(
        self,
        bucket_name: str | None = None,
        prefix: str | None = None,
        marker: str | None = None,
        max_keys: int | None = None,
        is_truncated: bool | None = False,
    ) -> list | None:
        """
        Lists the objects of a bucket in the specified region.
        If the region is cn-north-1, you can list the objects of a bucket in any region

        :param bucket_name: This is bucket name you want to list all objects.
        :param prefix: Name prefix that the objects to be listed must contain.
        :param marker: Object name to start with when listing objects in a bucket.
            All objects are listed in the lexicographical order.
        :param max_keys: Maximum number of objects returned in the response. The value ranges from 1 to 1000.
            If the value is not in this range, 1000 is returned by default.
        :param is_truncated: Whether to enable paging query and list all objects that meet the conditions.
        """
        bucket_client = self.get_bucket_client(bucket_name)
        resp = self._list_object(
            bucket_client,
            prefix=prefix,
            marker=marker,
            max_keys=max_keys,
        )
        if resp.status < 300:
            object_list = [content.key for content in resp.body.contents]
            if not is_truncated:
                return object_list
        else:
            self.log.error("Error message when listing the objects: %s.", get_err_info(resp))
            return None
        object_lists = [object_list]

        while resp.body.is_truncated:
            resp = self._list_object(
                bucket_client,
                prefix=prefix,
                marker=resp.body.next_marker,
                max_keys=max_keys,
            )
            if resp.status < 300:
                object_lists.append([content.key for content in resp.body.contents])
            else:
                self.log.error("Error message when listing the objects: %s.", get_err_info(resp))
                return None
        return object_lists

    @staticmethod
    def _list_object(bucket_client, **kwargs):
        return bucket_client.listObjects(**kwargs)

    @provide_bucket_name
    def create_object(
        self,
        object_key: str,
        data: str | object,
        object_type: str | None = "content",
        bucket_name: str | None = None,
        metadata: dict | None = None,
        headers: dict | None = None,
    ) -> None | list:
        """
        Uploads an object to the specified bucket.

        :param bucket_name: The name of the bucket.
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
        :param headers: The additional header field of the uploaded object.
        """
        if object_type not in ["content", "file"]:
            raise AirflowException("invalid object_type(choices 'content', 'file')")
        try:
            headers = headers if headers else {}
            sse_header = (
                self._get_encryption_header(
                    encryption=headers.pop("encryption", None), key=headers.pop("key", None)
                )
                if headers
                else None
            )
            headers = PutObjectHeader(sseHeader=sse_header, **headers)
            if object_type == "content":
                resp = self.get_bucket_client(bucket_name).putContent(
                    objectKey=object_key,
                    content=data,
                    metadata=metadata,
                    headers=headers,
                )
                if getattr(data, "read", None) and hasattr(data, "close") and callable(data.close):
                    data.close()
            else:
                resp = self.get_bucket_client(bucket_name).putFile(
                    objectKey=object_key,
                    file_path=data,
                    metadata=metadata,
                    headers=headers,
                )

            if isinstance(resp, list):
                err_object = [i[0] for i in self.flatten(resp) if i[1]["status"] >= 300]
                if err_object:
                    self.log.error("List of objects that failed to upload: %s.", err_object)
                    return err_object
                return None

            if resp.status < 300:
                self.log.info(f"Object uploaded successfully, the url of object is {resp.body.objectUrl}.")
                return None
            else:
                e = get_err_info(resp)
                self.log.error("Error message when uploading the object: %s.", e)
                raise AirflowException(e)

        except Exception as e:
            if (
                object_type == "content"
                and getattr(data, "read", None)
                and hasattr(data, "close")
                and callable(data.close)
            ):
                data.close()
            raise AirflowException(f"Errors when create object({e}).")

    @staticmethod
    def _get_encryption_header(encryption, key):
        if encryption == "kms":
            return SseKmsHeader(encryption=encryption, key=key)

    def flatten(self, sequence):
        for item in sequence:
            if isinstance(item[1], list):
                for subitem in self.flatten(item[1]):
                    yield subitem
            else:
                yield item

    @unify_bucket_name_and_key
    @provide_bucket_name
    def get_object(
        self,
        object_key: str,
        download_path: str,
        bucket_name: str | None = None,
    ) -> str:
        """
        Downloads an object in a specified bucket.

        :param bucket_name: The name of the bucket.
        :param object_key: Object name or the name of the file to be downloaded.
        :param download_path: The target path to which the object is downloaded, including the file name,
            for example, aa/bb.txt.When selecting the current directory,
            the path format must specify the current directory, for example, ./xxx.
        """
        try:
            resp = self.get_bucket_client(bucket_name).getObject(
                objectKey=object_key,
                downloadPath=download_path,
            )
            if resp.status < 300:
                self.log.info(f"The {object_key} is successfully downloaded and saved to the {download_path}")
                return download_path
            else:
                e = get_err_info(resp)
                self.log.error("Error message when getting the object: %s.", e)
                raise AirflowException(e)
        except Exception as e:
            raise AirflowException(f"Errors when get: {object_key}({e})")

    def copy_object(
        self,
        source_object_key: str,
        dest_object_key: str,
        source_bucket_name: str | None = None,
        dest_bucket_name: str | None = None,
        version_id: str | None = None,
        headers: dict | None = None,
        metadata: dict | None = None,
    ) -> None:
        """
         Creates a copy for an object in a specified bucket.

        :param source_object_key: Source object name.
        :param dest_object_key: Target object name.
        :param source_bucket_name: Source bucket name.
        :param dest_bucket_name: Target bucket name.
        :param version_id: Source object version ID.
        :param metadata: Customized metadata of the target object,
            directive in headers needs to be specified as 'REPLACE'.
        :param headers: Additional header of the request for copying an object.
        """
        try:
            headers = CopyObjectHeader(**headers) if headers else None

            dest_bucket_name, dest_object_key = self.get_obs_bucket_object_key(
                dest_bucket_name, dest_object_key, "dest_bucket_name", "dest_object_key"
            )

            source_bucket_name, source_object_key = self.get_obs_bucket_object_key(
                source_bucket_name, source_object_key, "source_bucket_name", "source_object_key"
            )

            resp = self.get_obs_client().copyObject(
                sourceObjectKey=source_object_key,
                destObjectKey=dest_object_key,
                sourceBucketName=source_bucket_name,
                destBucketName=dest_bucket_name,
                versionId=version_id,
                headers=headers,
                metadata=metadata,
            )
            if resp.status < 300:
                self.log.info("Object replication succeeded")
            else:
                e = get_err_info(resp)
                self.log.error("Error message when copying object: %s.", e)
                raise AirflowException(e)
        except Exception as e:
            raise AirflowException(f"Errors when copying: {source_object_key}({e}).")

    @unify_bucket_name_and_key
    @provide_bucket_name
    def delete_object(
        self,
        object_key: str,
        version_id: str | None = None,
        bucket_name: str | None = None,
    ) -> None:
        """
        Deletes an object from bucket.

        :param bucket_name: OBS bucket name.
        :param object_key: object name.
        :param version_id: object version id.
        """
        try:
            bucket_name, object_key = self.get_obs_bucket_object_key(
                bucket_name, object_key, "bucket_name", "object_key"
            )
            resp = self.get_bucket_client(bucket_name).deleteObject(
                objectKey=object_key,
                versionId=version_id,
            )
            if resp.status < 300:
                self.log.info("Object deleted successfully")
            else:
                e = get_err_info(resp)
                self.log.error("Error message when deleting object: %s.", e)
                raise AirflowException(e)
        except Exception as e:
            raise AirflowException(f"Errors when deleting: {object_key}({e})")

    def delete_objects(
        self,
        bucket_name: str,
        object_list: list,
        quiet: bool | None = True,
    ) -> None:
        """
        Deletes objects from a specified bucket in a batch.

        :param bucket_name: OBS bucket name.
        :param object_list: List of objects to be deleted.
        :param quiet: Response mode of a batch deletion request.
            If this field is set to False, objects involved in the deletion will be returned.
            If this field is set to True, only objects failed to be deleted will be returned.
        """
        try:
            if not object_list:
                self.log.warning("The object list is empty.")
                return
            if len(object_list) > 1000:
                self.log.warning(
                    f"A maximum of 1000 objects can be deleted in a batch, "
                    f"{len(object_list)} is out of limit"
                )
                return
            if isinstance(object_list[0], dict):
                objects = [
                    Object(key=obj.get("object_key", None), versionId=obj.get("version_id", None))
                    for obj in object_list
                ]
            else:
                objects = [Object(key=obj) for obj in object_list]
            delete_objects_request = DeleteObjectsRequest(objects=objects, quiet=quiet)
            resp = self.get_bucket_client(bucket_name).deleteObjects(delete_objects_request)
            if resp.status < 300:
                self.log.info("Succeeded in deleting objects in batches.")
            else:
                e = get_err_info(resp)
                self.log.error("Error message when deleting batch objects: %s.", e)
                raise AirflowException(e)
        except Exception as e:
            raise AirflowException(f"Errors when deleting: {object_list}({e}).")

    def move_object(
        self,
        source_object_key: str,
        dest_object_key: str,
        dest_bucket_name: str,
        source_bucket_name: str | None = None,
    ) -> None:
        """
        Creates a move for an object in a specified bucket.

        :param source_object_key: Source object name.
        :param dest_object_key: Target object name.
        :param source_bucket_name: Source bucket name.
        :param dest_bucket_name: Target bucket name.
        """
        try:
            obs_client = self.get_obs_client()
            copy_resp = obs_client.copyObject(
                sourceObjectKey=source_object_key,
                sourceBucketName=source_bucket_name,
                destBucketName=dest_bucket_name,
                destObjectKey=dest_object_key,
            )
            if copy_resp.status < 300:
                delete_resp = obs_client.deleteObject(
                    objectKey=source_object_key, bucketName=source_bucket_name
                )
                if delete_resp.status < 300:
                    self.log.info("Object moved successfully")
                else:
                    obs_client.deleteObject(objectKey=dest_object_key, bucketName=dest_bucket_name)
                    e = get_err_info(delete_resp)
                    self.log.error("Error message when moving objects: %s.", e)
                    raise AirflowException(e)
            else:
                e = get_err_info(copy_resp)
                self.log.error("Error message when getting the object: %s.", e)
                raise AirflowException(e)
        except Exception as e:
            raise AirflowException(f"Errors when Moving: {source_object_key}({e}).")

    def get_credential(self) -> tuple:
        """Gets user authentication information from connection."""
        access_key_id = self.conn.login
        access_key_secret = self.conn.password
        if not access_key_id:
            raise Exception(f"No access_key_id is specified for connection: {self.huaweicloud_conn_id}.")

        if not access_key_secret:
            raise Exception(f"No access_key_secret is specified for connection: {self.huaweicloud_conn_id}.")

        return access_key_id, access_key_secret
