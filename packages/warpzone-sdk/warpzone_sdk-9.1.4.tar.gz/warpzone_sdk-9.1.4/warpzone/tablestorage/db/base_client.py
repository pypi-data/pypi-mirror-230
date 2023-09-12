import pandas as pd

from warpzone.blobstorage.client import WarpzoneBlobClient

TABLE_STORAGE_TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
DATA_CONTAINER_NAME = "tables"
BLOB_NAME_COLUMN = "blob_path"


def generate_query_string(time_interval: pd.Interval) -> str:
    if time_interval:
        start_time_str = time_interval.left.strftime(TABLE_STORAGE_TIME_FORMAT)
        end_time_str = time_interval.right.strftime(TABLE_STORAGE_TIME_FORMAT)
        return (
            f"(PartitionKey ge '{start_time_str}')"
            f" and (PartitionKey le '{end_time_str}')"
        )
    else:
        return ""


def generate_dataframe_from_records(
    records: list[dict],
    blob_client: WarpzoneBlobClient,
) -> pd.DataFrame:
    # Return empty dataframe if the query result is empty
    if not records:
        return pd.DataFrame()

    # Download blobs and return the data stored if table entries contain blob_path
    if BLOB_NAME_COLUMN in records[0]:
        df = pd.DataFrame()
        for entity in records:
            blob_data = blob_client.download(
                DATA_CONTAINER_NAME, entity[BLOB_NAME_COLUMN]
            )
            df = pd.concat([df, blob_data.to_pandas()], ignore_index=True)
    else:
        df = pd.DataFrame.from_records(records)

    return df.drop(columns=["PartitionKey", "RowKey"])


def filter_dataframe(df: pd.DataFrame, filters: dict[str, object]) -> pd.DataFrame:
    df = df[(df[filters.keys()] == filters.values()).all(axis=1)]
    df = df.reset_index(drop=True)

    return df
