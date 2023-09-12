from functools import cache
from typing import Optional

import pandas as pd

from warpzone.blobstorage.client import WarpzoneBlobClient
from warpzone.tablestorage.db import base_client
from warpzone.tablestorage.tables.client_async import WarpzoneTableClientAsync


class WarpzoneDatabaseClientAsync:
    """Class to interact with Azure Table Storage for database queries
    asyncronously (using Azure Blob Service underneath)
    """

    def __init__(
        self, table_client: WarpzoneTableClientAsync, blob_client: WarpzoneBlobClient
    ):
        self._table_client = table_client
        self._blob_client = blob_client

    @classmethod
    def from_connection_string(cls, conn_str: str):
        table_client = WarpzoneTableClientAsync.from_connection_string(conn_str)
        blob_client = WarpzoneBlobClient.from_connection_string(conn_str)
        return cls(table_client, blob_client)

    @cache
    async def _query_to_pandas(self, table_name: str, query: str):
        records = await self._table_client.query(table_name, query)
        df = base_client.generate_dataframe_from_records(records, self._blob_client)

        return df

    async def query(
        self,
        table_name: str,
        time_interval: Optional[pd.Interval] = None,
        filters: Optional[dict[str, object]] = None,
        use_cache: Optional[bool] = True,
    ):
        query = base_client.generate_query_string(time_interval)

        if use_cache:
            df = await self._query_to_pandas(table_name, query)
        else:
            # Use __wrapped__ to bypass cache
            df = await self._query_to_pandas.__wrapped__(self, table_name, query)

        if not df.empty and filters:
            df = base_client.filter_dataframe(df, filters)

        return df
