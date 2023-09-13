import os
from google.cloud import storage


def stage_files_locally(
    bucket_name: str,
    object_name: str,
    file_name: str = "*",
    ignore_files: list = [],
    model_extra_files: bool = False,
):
    """Stage prediction files locally"""

    if model_extra_files:
        extra_files = ""

    storage_client = storage.Client()
    blobs = storage_client.list_blobs(bucket_name, prefix=object_name)
    for blob in blobs:
        blob_name = blob.name.split(f"{object_name}/")[1]
        if blob_name in ignore_files or blob_name == "":
            continue
        if blob_name.endswith("/"):
            os.makedirs(blob_name[:-1], exist_ok=True)
        elif blob_name == file_name or file_name == "*":
            blob.download_to_filename(blob_name)
            print(f"Downloaded {blob_name}")
            if model_extra_files:
                extra_files += f"{blob_name}" + ","

    if model_extra_files:
        extra_files = extra_files.rstrip(",")
        return extra_files


def upload_to_gcs(bucket_name: str, object_name: str, model_name: str):
    """Upload packaged .mar file to GCS"""

    if object_name.endswith("/"):
        object_name = object_name[:-1]

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    destination_blob_name = f"{object_name}/{model_name}.mar"
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(f"{model_name}.mar")

    return destination_blob_name


def split_bucket_object_file(path: str, file_name: str = None) -> (str, str, str):
    """Splits a GCS path and file name into bucket, object and file"""
    bucket_name = path.split("gs://")[1].split("/")[0]
    full_object_name = path.split(f"gs://{bucket_name}/")[1]
    if file_name:
        object_name = full_object_name.split(file_name)[0]
    else:
        object_name = full_object_name
    if object_name.endswith("/"):
        object_name = object_name[:-1]
    return bucket_name, object_name, file_name
