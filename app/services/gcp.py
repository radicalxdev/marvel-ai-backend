from google.cloud import storage
from fastapi import UploadFile

def upload_to_gcs(file: UploadFile, bucket_name: str, blob_name: str):
    """
    Uploads a file to GCS and returns the public URL
    
    Args:
        file (UploadFile): The file to upload
        bucket_name (str): The bucket to upload to
        blob_name (str): The name of the blob to upload to
    
    Returns:
        str: The public URL of the uploaded file
    """
    client = storage.Client()
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)
    
    blob.upload_from_file(file.file.read(), content_type=file.content_type)
    file.file.close()
    
    return blob.public_url

def delete_from_gcs(bucket_name: str, blob_name: str):
    """
    Deletes a file from GCS
    
    Args:
        bucket_name (str): The bucket to delete from
        blob_name (str): The name of the blob to delete
    """
    client = storage.Client()
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)
    
    blob.delete()