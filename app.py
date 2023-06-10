
import os
import json
import datetime
import time
from azure.identity import ClientSecretCredential
from azure.storage.blob import BlobServiceClient, BlobClient
from azure.mgmt.monitor import MonitorManagementClient

azure_tenant_id = os.environ["tenant_id"]
azure_client_id = os.environ["client_id"]
azure_client_secret = os.environ["client_secret"]
subscription_id = os.environ["subscription_id"]
RESOURCE_GROUP_NAME = os.environ["RESOURCE_GROUP_NAME"]
COSMOS_ACCOUNT_NAME = os.environ["COSMOS_ACCOUNT_NAME"]
STORAGE_CONTAINER_NAME = os.environ["STORAGE_CONTAINER_NAME"]
conn_string = os.environ["conn_string"]

credentials = ClientSecretCredential(
    azure_tenant_id, azure_client_id, azure_client_secret
)


resource_id = (
    "subscriptions/{}/"
    "resourceGroups/{}/"
    "providers/Microsoft.DocumentDB/databaseAccounts/{}"
).format(subscription_id, RESOURCE_GROUP_NAME, COSMOS_ACCOUNT_NAME)


while True:
    # create client
    monitor_client = MonitorManagementClient(
        credentials,
        subscription_id
    )
    today = datetime.datetime.now()
    yesterday = today - datetime.timedelta(days=1)    
    total_requests = monitor_client.metrics.list(
        resource_id,
        timespan="{}/{}".format(yesterday, today),
        interval='PT1H',
        metricnames='TotalRequests',
        aggregation='Total'
    )
    document_count = monitor_client.metrics.list(
        resource_id,
        timespan="{}/{}".format(yesterday, today),
        interval='PT1H',
        metricnames='DocumentCount',
        aggregation='Total'
    )
    data_usage = monitor_client.metrics.list(
        resource_id,
        timespan="{}/{}".format(yesterday, today),
        interval='PT5M',
        metricnames='DataUsage',
        aggregation='Total'
    )

    blob_service_client = BlobServiceClient.from_connection_string(conn_string)
    logs_request = total_requests.as_dict()['value'][0]['timeseries'][0]['data']
    logs_document = document_count.as_dict()['value'][0]['timeseries'][0]['data']
    logs_usage = document_count.as_dict()['value'][0]['timeseries'][0]['data']
    date_today = datetime.datetime.today().strftime('%Y-%m-%d')

    blob_client = blob_service_client.get_blob_client(STORAGE_CONTAINER_NAME, f'request_data/{date_today}.json')
    blob_client.upload_blob(json.dumps(logs_request), overwrite=True)
    blob_client = blob_service_client.get_blob_client(STORAGE_CONTAINER_NAME, f'document_count/{date_today}.json')
    blob_client.upload_blob(json.dumps(logs_document), overwrite=True)
    blob_client = blob_service_client.get_blob_client(STORAGE_CONTAINER_NAME, f'data_usage/{date_today}.json')
    blob_client.upload_blob(json.dumps(logs_usage), overwrite=True)
    
    time.sleep(3600*24)
