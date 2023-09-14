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

import warnings
from copy import deepcopy
from typing import Union

import psycopg2
import psycopg2.extensions
import psycopg2.extras
from psycopg2.extensions import connection
from psycopg2.extras import DictCursor, NamedTupleCursor, RealDictCursor

from airflow.models.connection import Connection
from airflow.providers.common.sql.hooks.sql import DbApiHook

CursorType = Union[DictCursor, RealDictCursor, NamedTupleCursor]


class DWSSqlHook(DbApiHook):
    """
    Execute statements against Huawei Cloud DWS, using dws_connector

    This hook requires the dws_conn_id connection.

    :param dws_conn_id: reference to
        :ref:`Huawei Cloud DWS connection id<howto/connection:dws>`
    """

    conn_name_attr = "dws_conn_id"
    default_conn_name = "dws_default"
    conn_type = "dws"
    hook_name = "Huawei Cloud DWS"
    supports_autocommit = True

    def __init__(self, *args, **kwargs) -> None:
        if "schema" in kwargs:
            warnings.warn(
                'The "schema" arg has been renamed to "database" as it contained the database name.'
                'Please use "database" to set the database name.',
                DeprecationWarning,
                stacklevel=2,
            )
            kwargs["database"] = kwargs["schema"]
        super().__init__(*args, **kwargs)
        self.connection: Connection | None = kwargs.pop("connection", None)
        self.conn: connection = None
        self.database: str | None = kwargs.pop("database", None)

    def _get_cursor(self, raw_cursor: str) -> CursorType:
        _cursor = raw_cursor.lower()
        if _cursor == "dictcursor":
            return psycopg2.extras.DictCursor
        if _cursor == "realdictcursor":
            return psycopg2.extras.RealDictCursor
        if _cursor == "namedtuplecursor":
            return psycopg2.extras.NamedTupleCursor
        raise ValueError(f"Invalid cursor passed {_cursor}")

    def get_conn(self) -> connection:
        """Establishes a connection to a GussDB(DWS) database."""
        conn_id = getattr(self, self.conn_name_attr)
        conn = deepcopy(self.connection or self.get_connection(conn_id))

        conn_args = dict(
            host=conn.host,
            user=conn.login,
            password=conn.password,
            dbname=self.database or conn.schema,
            port=conn.port,
        )

        raw_cursor = conn.extra_dejson.get("cursor", False)
        if raw_cursor:
            conn_args["cursor_factory"] = self._get_cursor(raw_cursor)

        client_encoding = conn.extra_dejson.get("client_encoding", False)
        if client_encoding:
            conn_args["client_encoding"] = client_encoding

        self.conn = psycopg2.connect(**conn_args)
        return self.conn
