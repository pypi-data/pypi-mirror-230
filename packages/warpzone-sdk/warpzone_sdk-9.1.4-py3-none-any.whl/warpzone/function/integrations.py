import os
from typing import Optional

import azure.functions as func
import pandas as pd
from azure.servicebus import ServiceBusClient, ServiceBusMessage

from warpzone.blobstorage.client import BlobData, WarpzoneBlobClient
from warpzone.enums.topicenum import Topic
from warpzone.servicebus.data.client import DataMessage, WarpzoneDataClient
from warpzone.servicebus.events.client import EventMessage, WarpzoneEventClient
from warpzone.tablestorage.db.client import WarpzoneDatabaseClient
from warpzone.tablestorage.db.client_async import WarpzoneDatabaseClientAsync
from warpzone.tablestorage.tables.client import WarpzoneTableClient
from warpzone.tablestorage.tables.client_async import WarpzoneTableClientAsync


def get_sb_client() -> ServiceBusClient:
    return ServiceBusClient.from_connection_string(
        os.environ["SERVICE_BUS_CONNECTION_STRING"]
    )


def get_data_client() -> WarpzoneDataClient:
    return WarpzoneDataClient.from_connection_strings(
        service_bus_conn_str=os.environ["SERVICE_BUS_CONNECTION_STRING"],
        storage_account_conn_str=os.environ["DATA_STORAGE_ACCOUNT_CONNECTION_STRING"],
    )


def get_event_client() -> WarpzoneEventClient:
    return WarpzoneEventClient.from_connection_string(
        conn_str=os.environ["SERVICE_BUS_CONNECTION_STRING"],
    )


def get_table_client() -> WarpzoneTableClient:
    return WarpzoneTableClient.from_connection_string(
        conn_str=os.environ["DATA_STORAGE_ACCOUNT_CONNECTION_STRING"],
    )


def get_table_client_async() -> WarpzoneTableClientAsync:
    return WarpzoneTableClientAsync.from_connection_string(
        conn_str=os.environ["DATA_STORAGE_ACCOUNT_CONNECTION_STRING"],
    )


def get_db_client() -> WarpzoneDatabaseClient:
    return WarpzoneDatabaseClient.from_connection_string(
        conn_str=os.environ["DATA_STORAGE_ACCOUNT_CONNECTION_STRING"],
    )


def get_db_client_async() -> WarpzoneDatabaseClientAsync:
    return WarpzoneDatabaseClientAsync.from_connection_string(
        conn_str=os.environ["DATA_STORAGE_ACCOUNT_CONNECTION_STRING"],
    )


def get_blob_client() -> WarpzoneBlobClient:
    return WarpzoneBlobClient.from_connection_string(
        conn_str=os.environ["ARCHIVE_STORAGE_ACCOUNT_CONNECTION_STRING"]
    )


def func_msg_to_event(msg: func.ServiceBusMessage) -> EventMessage:
    event_msg = EventMessage.from_func_msg(msg)
    return event_msg


def func_msg_to_data(msg: func.ServiceBusMessage) -> DataMessage:
    data_client = get_data_client()
    event_msg = func_msg_to_event(msg)
    data_msg = data_client.event_to_data(event_msg)
    return data_msg


def func_msg_to_pandas(msg: func.ServiceBusMessage) -> pd.DataFrame:
    data_msg = func_msg_to_data(msg)
    return data_msg.to_pandas()


def send_func_msg(data_msg: ServiceBusMessage, topic: Topic):
    sb_client = get_sb_client()
    with sb_client.get_topic_sender(topic.value) as sender:
        sender.send_messages(message=data_msg)


def send_event(event_msg: EventMessage, topic: Topic) -> None:
    event_client = get_event_client()
    event_client.send(
        topic=topic,
        event_msg=event_msg,
    )


def send_data(data_msg: DataMessage, topic: Topic) -> None:
    data_client = get_data_client()
    data_client.send(
        topic=topic,
        data_msg=data_msg,
    )


def send_pandas(
    df: pd.DataFrame, topic: Topic, subject: str, schema: Optional[dict] = None
) -> None:
    data_msg = DataMessage.from_pandas(df, subject, schema=schema)
    send_data(data_msg, topic)


def read_pandas(
    table_name: str,
    time_interval: pd.Interval = None,
) -> pd.DataFrame:
    db_client = get_db_client()

    return db_client.query(table_name, time_interval)


def upload_blob(blob_data: BlobData, container_name: str) -> None:
    blob_client = get_blob_client()
    blob_client.upload(container_name=container_name, blob_data=blob_data)
