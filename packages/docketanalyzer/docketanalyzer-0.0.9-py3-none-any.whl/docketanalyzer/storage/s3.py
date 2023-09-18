import boto3
from docketanalyzer.utils import (
    AWS_S3_BUCKET_NAME,
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    AWS_S3_ENDPOINT_URL,
    AWS_S3_REGION_NAME,
)


def load_s3():
    return boto3.client('s3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        endpoint_url=AWS_S3_ENDPOINT_URL,
        region_name=AWS_S3_REGION_NAME,
    )


def s3_download(key, path=None, bucket_name=None, s3=None):
    if path is None:
        path = key
    if bucket_name is None:
        bucket_name = AWS_S3_BUCKET_NAME
    if s3 is None:
        s3 = load_s3()
    s3.download_file(bucket_name, str(key), str(path))


def s3_upload(path, key=None, bucket_name=None, s3=None):
    if key is None:
        key = path
    if bucket_name is None:
        bucket_name = AWS_S3_BUCKET_NAME
    if s3 is None:
        s3 = load_s3()
    s3.upload_file(path, str(bucket_name), str(key))

