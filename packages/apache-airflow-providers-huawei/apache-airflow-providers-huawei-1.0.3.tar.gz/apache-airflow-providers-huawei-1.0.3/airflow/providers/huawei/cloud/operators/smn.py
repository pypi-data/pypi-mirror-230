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
"""This module contains Huawei Cloud SMN operators."""
from __future__ import annotations

import json
from typing import TYPE_CHECKING, Sequence

from airflow.models import BaseOperator
from airflow.providers.huawei.cloud.hooks.smn import SMNHook

if TYPE_CHECKING:
    from airflow.utils.context import Context


class SMNPublishMessageTemplateOperator(BaseOperator):
    """
    This operator is used to publish template messages to a topic

    :param project_id: Specifies the project ID.For details about how to obtain the project ID
    :param topic_urn: Specifies the resource identifier of the topic, which is unique. To obtain the resource
        identifier.
    :param tags: Specifies the dictionary consisting of variable parameters and values.
    :param template_name: Specifies the message template name
    :param region: Regions where the API is available
    :param email_subject: Specifies the message subject, which is used as the email subject when you publish email
        messages
    :param huaweicloud_conn_id: The Airflow connection used for SMN credentials.
    """

    template_fields: Sequence[str] = ("template_name", "project_id", "topic_urn", "email_subject")
    ui_color = "#66c3ff"

    def __init__(
        self,
        topic_urn: str,
        tags: dict,
        template_name: str,
        project_id: str | None = None,
        region: str | None = None,
        email_subject: str | None = None,
        huaweicloud_conn_id: str = "huaweicloud_default",
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)

        self.region = region
        self.project_id = project_id
        self.topic_urn = topic_urn
        self.email_subject = email_subject
        self.tags = tags
        self.template_name = template_name
        self.huaweicloud_conn_id = huaweicloud_conn_id

    def execute(self, context: Context):

        smn_hook = SMNHook(
            huaweicloud_conn_id=self.huaweicloud_conn_id, region=self.region, project_id=self.project_id
        )

        smn_hook.send_message(
            topic_urn=self.topic_urn, tags=self.tags, template_name=self.template_name, subject=self.email_subject
        )


class SMNPublishTextMessageOperator(BaseOperator):
    """
    This operator is used to publish text messages to a topic

    :param project_id: Specifies the project ID.For details about how to obtain the project ID
    :param topic_urn: Specifies the resource identifier of the topic, which is unique. To obtain the resource
        identifier.
    :param message: Specifies the message content
    :param region: Regions where the API is available
    :param email_subject: Specifies the message subject, which is used as the email subject when you publish email
        messages
    :param huaweicloud_conn_id: The Airflow connection used for SMN credentials.
    """

    template_fields: Sequence[str] = ("message", "project_id", "topic_urn", "email_subject")
    ui_color = "#66c3ff"

    def __init__(
        self,
        topic_urn: str,
        message: str,
        project_id: str | None = None,
        region: str | None = None,
        email_subject: str | None = None,
        huaweicloud_conn_id: str = "huaweicloud_default",
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)

        self.region = region
        self.project_id = project_id
        self.topic_urn = topic_urn
        self.email_subject = email_subject
        self.message = message
        self.huaweicloud_conn_id = huaweicloud_conn_id

    def execute(self, context: Context):

        smn_hook = SMNHook(
            huaweicloud_conn_id=self.huaweicloud_conn_id, region=self.region, project_id=self.project_id
        )

        smn_hook.send_message(topic_urn=self.topic_urn, message=self.message, subject=self.email_subject)


class SMNPublishJsonMessageOperator(BaseOperator):
    """
    This operator is used to publish json messages to a topic

    :param project_id: Specifies the project ID.For details about how to obtain the project ID
    :param topic_urn: Specifies the resource identifier of the topic, which is unique.
    :param message_structure: Specifies the message structure, which contains JSON strings
    :param region: Regions where the API is available
    :param email_subject: Specifies the message subject, which is used as the email subject when you publish email
        messages.
    :param huaweicloud_conn_id: The Airflow connection used for SMN credentials.
    """

    template_fields: Sequence[str] = (
        "project_id",
        "topic_urn",
        "email_subject",
        "default",
        "sms",
        "email_body",
        "http",
        "https",
        "functionstage",
    )

    ui_color = "#66c3ff"

    def __init__(
        self,
        topic_urn: str,
        default: str,
        project_id: str | None = None,
        sms: str | None = None,
        email_subject: str | None = None,
        email_body: str | None = None,
        http: str | None = None,
        https: str | None = None,
        functionstage: str | None = None,
        region: str | None = None,
        huaweicloud_conn_id: str = "huaweicloud_default",
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)

        self.region = region
        self.project_id = project_id
        self.topic_urn = topic_urn
        self.email_subject = email_subject
        self.email_body = email_body
        self.default = default
        self.sms = sms
        self.http = http
        self.https = https
        self.functionstage = functionstage
        msg = {
            "default": default,
            "sms": sms,
            "email": email_body,
            "http": http,
            "https": https,
            "functionstage": functionstage,
        }
        self.message_structure = json.dumps({i: j for i, j in msg.items() if j is not None})
        self.huaweicloud_conn_id = huaweicloud_conn_id

    def execute(self, context: Context):

        smn_hook = SMNHook(
            huaweicloud_conn_id=self.huaweicloud_conn_id, region=self.region, project_id=self.project_id
        )

        smn_hook.send_message(
            topic_urn=self.topic_urn, message_structure=self.message_structure, subject=self.email_subject
        )
