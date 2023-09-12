"""Cursor for ClickZetta DB-API."""

import collections
import logging
import contextlib

from clickzetta.enums import JobID

from clickzetta.query_result import QueryResult

_LOGGER = logging.getLogger(__name__)

Column = collections.namedtuple(
    "Column",
    [
        "name",
        "type_code",
        "display_size",
        "internal_size",
        "precision",
        "scale",
        "null_ok",
    ],
)


class Cursor(object):
    def __init__(self, connection):
        self.connection = connection
        self.description = None
        self.arraysize = 100
        self.rowcount = -1
        self._query_result = None
        self._query_data = None
        self._closed = False
        self.job_id = None
        self._rows = None
        self.row_number = 0

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        self._closed = True

    def check_rows(self):
        if self._rows is None or self.row_number >= len(self._rows):
            self._rows = self._query_data.read()
            self.row_number = 0

    def _set_rowcount(self, query_result):

        self.rowcount = query_result.total_row_count

    def _set_description(self, query_result: QueryResult):
        if query_result.schema is None:
            self.description = None
            return

        self.description = tuple(
            Column(
                name=field.name,
                type_code=field.field_type,
                display_size=None,
                internal_size=field.length,
                precision=field.precision,
                scale=field.scale,
                null_ok=field.nullable,
            )
            for field in query_result.schema
        )

    def execute(self, operation: str, parameters=None):

        self._execute(operation, parameters)

    def _execute(
            self, operation: str, parameters
    ):
        if operation is None:
            raise ValueError("sql is empty")
        else:
            operation = operation.strip()
            if operation == "":
                raise ValueError("sql is empty")
        self._query_data = None
        self._query_job = None
        client = self.connection._client
        operation = operation + ";" if not operation.endswith(";") else operation

        self.job_id = client._format_job_id()

        job_id = JobID(self.job_id, client.workspace, 100)
        self._query_result = client.submit_sql_job(token=client.token, sql=operation, job_id=job_id,
                                                   parameters=parameters)
        self._set_rowcount(self._query_result)
        self._query_data = self._query_result.data
        self._set_description(self._query_result)

    def executemany(self, operations, methods):
        print("not supported yet")

    def fetchone(self):
        self.check_rows()
        if self._rows is None or self.row_number >= len(self._rows):
            return []
        else:
            row = self._rows[self.row_number]
            self.row_number += 1
            return row

    def fetchmany(self, size=None):
        self.check_rows()
        if self._rows is None or self.row_number >= len(self._rows):
            return []
        else:
            end = self.row_number + (size or self.arraysize)
            rows = self._rows[self.row_number:end]
            self.row_number = min(end, len(self._rows))
            return rows

    def fetchall(self):
        self.check_rows()
        if self._rows is None or self.row_number >= len(self._rows):
            return []
        else:
            rows = self._rows[self.row_number:]
            self.row_number = len(self._rows)
            return rows

    def get_job_id(self):
        return self.job_id

    def setinputsizes(self, sizes):
        """No-op, but for consistency raise an error if cursor is closed."""

    def setoutputsize(self, size, column=None):
        """No-op, but for consistency raise an error if cursor is closed."""

    def __iter__(self):
        return iter(self._query_data)
