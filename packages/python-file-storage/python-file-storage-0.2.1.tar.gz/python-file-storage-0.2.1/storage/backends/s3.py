import tempfile
import mimetypes

import boto3
from botocore.exceptions import ClientError

from storage.base import Storage
from storage.exceptions import StorageError
from storage.files import File, ContentFile
from storage.conf import settings




class S3Storage(Storage):

    def __init__(
        self,
        bucket_name,
        endpoint_url=None,
        upload_options={},
        access_key_id=None,
        secret_access_key=None,
    ):
        if not endpoint_url:
            endpoint_url = settings.S3_ENDPOINT_URL
        if not access_key_id:
            access_key_id = settings.S3_ACCESS_KEY_ID
        if not secret_access_key:
            secret_access_key = settings.S3_SECRET_ACCESS_KEY

        self.bucket_name = bucket_name
        self.client = boto3.client(
            service_name='s3',
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            endpoint_url=endpoint_url,
        )
        self.upload_options = upload_options


    def _save(self, name, content, content_type=None, encoding='utf-8'):
        options = self.upload_options.copy()

        if content_type is None:
            content_type, _ = mimetypes.guess_type(name)

        if content_type:
            options['ContentType'] = content_type

        try:
            self.client.put_object(
                Bucket=self.bucket_name,
                Key=name,
                Body=content,
                **options,
            )
        except ClientError as e:
            raise StorageError('Error uploading file to S3') from e


    def _open(self, name, mode='rb'):
        """
        Open a file from the S3 bucket.

        :param name: The name of the file in the bucket.
        :param mode: The mode to open the file in (default: "rb").
        :return: A file-like object.
        """
        if mode not in ('r', 'rb'):
            raise ValueError("S3Storage only supports read modes: 'r' and 'rb'")
        try:
            obj = self.client.get_object(
                Bucket=self.bucket_name,
                Key=name,
            )
        except ClientError as err:
            raise FileNotFoundError(f'File does not exist: {name}')

        content = obj["Body"].read()

        if "b" not in mode:
            content = content.decode()

        return ContentFile(content, name=name)


    def delete(self, name):
        try:
            self.client.delete_object(Bucket=self.bucket_name, Key=name)
        except ClientError as err:
            if err.response['ResponseMetadata']['HTTPStatusCode'] == 404:
                # Not an error to delete something that does not exist
                return
            raise StorageError('Error deleting file from S3') from err


    def exists(self, name):
        try:
            self.client.head_object(Bucket=self.bucket_name, Key=name)
            return True
        except ClientError as e:
            return False


    def size(self, name):
        try:
            obj = self.client.head_object(Bucket=self.bucket_name, Key=name)
            return obj['ContentLength']
        except ClientError as e:
            raise StorageError('Error getting file size from S3') from e


    def url(self, name):
        return f'{settings.S3_ENDPOINT_URL}/{name}'
