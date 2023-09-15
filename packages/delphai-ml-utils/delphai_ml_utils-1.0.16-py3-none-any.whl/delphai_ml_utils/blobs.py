# Requires !pip install azure-storage-blob==12.9.0

from azure.storage.blob import BlobServiceClient, BlobClient
from azure.core.exceptions import ServiceRequestError, ResourceNotFoundError, AzureError
from delphai_ml_utils.config import get_config

azure_blobs_connection_string = get_config("azure.blobs.connection_string")
azure_blobs_container = get_config("azure.blobs.folder_name")


def read_blob(blob_name: str) -> str:
    blob = BlobClient.from_connection_string(
        azure_blobs_connection_string, azure_blobs_container, blob_name
    )
    stream = blob.download_blob()
    data = stream.readall()
    content = data.decode("utf-8")
    return content


def blob_exist(key: str) -> bool:
    blob = BlobClient.from_connection_string(
        conn_str=azure_blobs_connection_string,
        container_name=azure_blobs_container,
        blob_name=key,
    )
    return blob.exists()
