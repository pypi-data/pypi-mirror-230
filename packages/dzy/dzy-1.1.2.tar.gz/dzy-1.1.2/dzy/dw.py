import json

from google.cloud import bigquery, secretmanager, storage
from google.cloud.exceptions import Conflict, NotFound


class CloudStorageExecutor:
    """
    Google Cloud Storage handler.

    Operations for buckets and blobs.
    """
    def __init__(self):
        """
        Initiate object.
        """
        self.storage_client = storage.Client()

    def list_buckets(self):
        """
        Lists all buckets.
        """
        buckets = self.storage_client.list_buckets()
        for bucket in buckets:
            print(bucket.name)

    def create_bucket(
            self,
            bucket_name: str
    ):
        """
        Creates new bucket.
        """
        self.bucket = self.storage_client.create_bucket(bucket_name)
        print(f"Bucket {bucket_name} created")

    def list_blobs(
            self,
            bucket_name: str,
            returns: bool = False
    ):
        """
        Lists all the blobs in the bucket.
        """
        blobs = self.storage_client.list_blobs(bucket_name)
        if returns:
            return list(blobs)
        else:
            for blob in blobs:
                print(blob.name)

    def copy_blob(
            self,
            bucket_name: str,
            blob_name: str,
            destination_bucket_name: str,
            destination_blob_name: str
    ):
        """
        Copies a blob from one bucket to another with a new name.
        """
        source_bucket = self.storage_client.bucket(bucket_name)
        source_blob = source_bucket.blob(blob_name)
        destination_bucket = self.storage_client.bucket(
            destination_bucket_name
        )

        blob_copy = source_bucket.copy_blob(
            source_blob,
            destination_bucket,
            destination_blob_name
        )

        print(
            f"Blob {source_blob.name} in bucket {source_bucket.name} copied "
            f"to blob {blob_copy.name} in bucket {destination_bucket.name}."
        )

    def rename_blob(
            self,
            bucket_name: str,
            blob_name: str,
            new_name: str
    ):
        """
        Renames a blob.
        """
        bucket = self.storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        new_blob = bucket.rename_blob(blob, new_name)

        print(f"Blob {blob.name} has been renamed to {new_blob.name}")

    def move_blob(
            self,
            bucket_name: str,
            blob_name: str,
            destination_bucket_name: str,
            destination_blob_name: str
    ):
        """
        Moves a blob from one bucket to another with a new name.
        """
        source_bucket = self.storage_client.bucket(bucket_name)
        source_blob = source_bucket.blob(blob_name)
        destination_bucket = self.storage_client.bucket(
            destination_bucket_name
        )

        blob_copy = source_bucket.copy_blob(
            source_blob,
            destination_bucket,
            destination_blob_name
        )
        source_bucket.delete_blob(blob_name)

        print(
            f"Blob {source_blob.name} in bucket {source_bucket.name,} moved "
            f"to blob {blob_copy.name} in bucket {destination_bucket.name}."
        )

    def delete_blob(
            self,
            bucket_name: str,
            blob_name: str
    ):
        """
        Deletes a blob from the bucket.
        """
        bucket = self.storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.delete()

        print(f"Blob {blob_name} deleted.")

    def upload_blob_from_filename(
            self,
            bucket_name: str,
            source_file_name: str,
            destination_blob_name: str
    ):
        """
        Uploads blob from the provided file.
        """
        bucket = self.storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(source_file_name)
        print(f"File {source_file_name} uploaded to {destination_blob_name}.")

    def upload_blob_from_string(
            self,
            bucket_name: str,
            source_string: str,
            destination_blob_name: str,
            content_type: str = 'text/plain'
    ):
        """
        Uploads blob from the provided string.
        """
        bucket = self.storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_string(source_string, content_type=content_type)
        print(f"File {destination_blob_name} uploaded from string")

    def download_blob_as_string(
            self,
            bucket_name: str,
            file_path: str
    ):
        """
        Download blob as string.
        """
        bucket = self.storage_client.get_bucket(bucket_name)
        blob = bucket.blob(file_path)

        return blob.download_as_string()


class BigQueryExecutor:
    """
    Google BigQuery handler.

    Operations for datasets and tables.
    """
    def __init__(
            self,
            project: str,
            location: str = "europe-west2"
    ):
        """
        Construct a BigQuery client object.
        """
        self.client = bigquery.Client(project=project)
        self.location = location
        self.project = project

    # dataset operations
    def list_datasets(
            self,
            returns: bool = False
    ):
        """
        List datasets in a project.
        """
        datasets = list(self.client.list_datasets())
        if returns:
            return datasets
        else:
            if datasets:
                print(f"Datasets in project '{self.project}':")
                for dataset in datasets:
                    print(f"\t{dataset.dataset_id}")
            else:
                print(f"Project '{self.project}' doesn't contain any datasets")

    def check_dataset_exists(
            self,
            dataset_name: str,
            returns: bool = False
    ):
        """
        Check whether a dataset exists.
        """
        dataset_id = f"{self.project}.{dataset_name}"
        try:
            self.client.get_dataset(dataset_id)
            if returns:
                return True
            else:
                print(f"Dataset '{dataset_id}' already exists")
        except NotFound:
            if returns:
                return False
            else:
                print(f"Dataset '{dataset_id}' is not found")

    def create_dataset(
            self,
            dataset_name: str
    ):
        """
        Create a dataset.
        """
        dataset_id = f"{self.project}.{dataset_name}"
        if self.check_dataset_exists(dataset_name, returns=True):
            print(f"Dataset '{dataset_id}' already exists")
        else:
            dataset = bigquery.Dataset(dataset_id)
            dataset.location = self.location
            try:
                dataset = self.client.create_dataset(dataset, timeout=30)
                print(f"Created dataset '{dataset_id}'")
            except Conflict:
                # in case it is created at the same time via another process
                pass

    def delete_dataset(
            self,
            dataset_name: str
    ):
        """
        Delete a dataset and its contents.
        """
        dataset_id = f"{self.project}.{dataset_name}"
        if self.check_dataset_exists(dataset_name, returns=True):
            self.client.delete_dataset(
                dataset_id,
                delete_contents=True
            )
            print(f"Deleted dataset '{dataset_id}'")
        else:
            print(f"Dataset '{dataset_id}' doesn't exist")

    # table operations
    def list_tables(
            self,
            dataset_name: str,
            returns: bool = False
    ):
        """
        List tables in a given dataset.
        """
        dataset_id = f"{self.project}.{dataset_name}"
        if self.check_dataset_exists(dataset_name, returns=True):
            tables = list(self.client.list_tables(dataset_id))
            if returns:
                return tables
            else:
                if tables:
                    print(f"Tables contained in '{dataset_id}':")
                    for table in tables:
                        print(f"\t{table.table_id}")
                else:
                    print(f"Dataset '{dataset_id}' doesn't contain any tables")
        else:
            if returns:
                return []
            else:
                print(f"Dataset '{dataset_id}' doesn't exist")

    def check_table_exists(
            self,
            dataset_name: str,
            table_name: str,
            returns: bool = False
    ):
        """
        Check whether a table exists.
        """
        table_id = f"{self.project}.{dataset_name}.{table_name}"
        try:
            self.client.get_table(table_id)
            if returns:
                return True
            else:
                print(f"Table '{table_id}' already exists")
        except NotFound:
            if returns:
                return False
            else:
                print(f"Table '{table_id}' is not found")

    def parse_table_schema_json(
            self,
            schema_path: str,
            schema_bucket: str = None
    ):
        """
        Parse table schema json file.
        - reads from cloud storage if 'schema_bucket' is given
        """
        if schema_bucket:
            storage_client = storage.Client()
            bucket = storage_client.get_bucket(schema_bucket)
            blob = bucket.blob(schema_path)
            json_schema = json.loads(blob.download_as_string())
        else:
            with open(schema_path, "r") as f_path:
                json_schema = json.load(f_path)

        return bigquery.schema._parse_schema_resource({"fields": json_schema})

    def create_table(
            self,
            dataset_name: str,
            table_name: str,
            schema: list
    ):
        """
        Create empty table with a schema definition.
        """
        if self.check_dataset_exists(dataset_name, returns=True):
            table_id = f"{self.project}.{dataset_name}.{table_name}"
            if self.check_table_exists(dataset_name, table_name, returns=True):
                print(f"Table '{table_id}' already exists")
            else:
                table = bigquery.Table(table_id, schema=schema)
                self.client.create_table(table)
                print(f"Created table '{table_id}'")
        else:
            print(f"Dataset '{dataset_name}' is not found")

    def create_tucp_table(
            self,
            dataset_name: str,
            table_name: str,
            schema: list,
            partition_field: str,
            partition_type: str = "DAY",
            partition_expiration: int = None
    ):
        """
        Create empty time-unit column-partitioned table.
        """
        if self.check_dataset_exists(dataset_name, returns=True):
            table_id = f"{self.project}.{dataset_name}.{table_name}"
            if self.check_table_exists(dataset_name, table_name, returns=True):
                print(f"Table '{table_id}' already exists")
            else:
                table = bigquery.Table(table_id, schema=schema)
                table.time_partitioning = bigquery.TimePartitioning(
                    type_=partition_type,
                    field=partition_field
                )
                if partition_expiration:
                    table.partition_expiration = partition_expiration
                self.client.create_table(table)
                print(f"Created partitioned table '{table_id}'")
        else:
            print(f"Dataset '{dataset_name}' is not found")

    def delete_table(
            self,
            dataset_name: str,
            table_name: str,
    ):
        """
        Delete a table from a dataset.
        """
        table_id = f"{self.project}.{dataset_name}.{table_name}"
        if self.check_table_exists(dataset_name, table_name, returns=True):
            self.client.delete_table(table_id)
            print(f"Deleted table '{table_id}'")
        else:
            print(f"Table '{table_id}' doesn't exist")

    def empty_table(
        self,
        dataset_name: str,
        table_name: str
    ):
        """
        Empty the table but preserve structure.
        """
        table_id = f"{self.project}.{dataset_name}.{table_name}"
        if self.client.get_table(table_id):
            sql = f"""
                DELETE FROM `{dataset_name}.{table_name}` WHERE TRUE
            """
            job_config = bigquery.QueryJobConfig()
            load_job = self.client.query(sql, job_config=job_config)
            load_job.result()
            print(f"Emptied table '{dataset_name}.{table_name}'")
        else:
            print(f"Table '{dataset_name}.{table_name}' is empty")

    # gcs to bq ingestion
    def load_gcs_json_to_bq(
            self,
            uri: str,
            dataset_name: str,
            table_name: str,
            append: bool,
            schema: str = [],
            partition_name: str = None
    ):
        """
        Load a CSV file from Cloud Storage.
        """
        table_id = f"{self.project}.{dataset_name}.{table_name}"
        if self.check_table_exists(dataset_name, table_name, returns=True):
            uri = f"gs://{uri}"
            job_config = bigquery.LoadJobConfig(
                source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
                write_disposition="WRITE_TRUNCATE"
            )
            if schema:
                job_config.schema = schema
            else:
                job_config.autodetect = True

            if append:
                job_config.write_disposition = "WRITE_APPEND"
                job_config.schema_update_options = [
                    "ALLOW_FIELD_ADDITION",
                    "ALLOW_FIELD_RELAXATION"
                ]
            if partition_name:
                job_config.write_disposition = "WRITE_TRUNCATE"
                table_id = f"{table_id}${partition_name}"

            load_job = self.client.load_table_from_uri(
                uri,
                table_id,
                location=self.location,
                job_config=job_config
            )
            load_job.result()
            destination_table = self.client.get_table(table_id)
            print(f"Loaded {destination_table.num_rows} rows to '{table_id}'")

        else:
            print(f"Table '{table_id}' doesn't exist")


def get_secret(
        project_id: str,
        secret_name: str
):
    """
    Returns a secret stored in Secret Manager.
    """
    client = secretmanager.SecretManagerServiceClient()
    request = {
        "name": f"projects/{project_id}/secrets/{secret_name}/versions/latest"
    }
    response = client.access_secret_version(request)
    secret_string = response.payload.data.decode("UTF-8")

    return secret_string
