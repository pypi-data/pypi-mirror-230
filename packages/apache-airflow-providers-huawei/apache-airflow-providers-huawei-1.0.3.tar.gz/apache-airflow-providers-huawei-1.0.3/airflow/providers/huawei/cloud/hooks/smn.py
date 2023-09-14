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

from typing import Any

import huaweicloudsdksmn.v2 as SmnSdk
from huaweicloudsdkcore.auth.credentials import BasicCredentials
from huaweicloudsdksmn.v2.region.smn_region import SmnRegion

from airflow.exceptions import AirflowException
from airflow.providers.huawei.cloud.hooks.base_huawei_cloud import HuaweiBaseHook


class SMNHook(HuaweiBaseHook):
    """Interact with Huawei Cloud SMN, using the huaweicloudsdksmn library."""

    def send_message(
        self,
        topic_urn: str,
        tags: dict | None = None,
        template_name: str | None = None,
        subject: str | None = None,
        message_structure: str | None = None,
        message: str | None = None,
    ):
        """
        This function is used to publish messages to a topic

        :param project_id: Specifies the project ID.
        :param topic_urn: Specifies the resource identifier of the topic, which is unique.
        :param tags: Specifies the dictionary consisting of variable parameters and values.
        :param template_name: Specifies the message template name.
        :param subject: Specifies the message subject, which is used as the email subject
            when you publish email messages.
        :param message_structure: Specifies the message structure, which contains JSON strings.
        :param message: Specifies the message content.
        """
        kwargs: dict[str, Any] = {}

        if message_structure:
            kwargs["message_structure"] = message_structure
        if template_name:
            kwargs["message_template_name"] = template_name
        if subject:
            kwargs["subject"] = subject
        if tags:
            kwargs["tags"] = tags
        if message:
            kwargs["message"] = message

        self.send_request(self.make_publish_app_message_request(topic_urn=topic_urn, body=kwargs))

    def send_request(self, request: SmnSdk.PublishMessageRequest) -> None:
        try:
            self.get_smn_client().publish_message(request)
        except Exception as e:
            self.log.error(e)
            raise AirflowException(f"Errors when publishing: {e}")

    def make_publish_app_message_request(self, topic_urn, body: dict) -> SmnSdk.PublishMessageRequest:
        request = SmnSdk.PublishMessageRequest()
        request.topic_urn = topic_urn
        request.body = SmnSdk.PublishMessageRequestBody(**body)
        return request

    def get_smn_client(self) -> SmnSdk.SmnClient:
        ak = self.conn.login
        sk = self.conn.password

        credentials = BasicCredentials(ak, sk, self.get_project_id())

        return (
            SmnSdk.SmnClient.new_builder()
            .with_credentials(credentials)
            .with_region(SmnRegion.value_of(self.get_region()))
            .build()
        )
