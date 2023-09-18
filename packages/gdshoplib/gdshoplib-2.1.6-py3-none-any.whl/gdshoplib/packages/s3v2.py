from typing import Optional

import boto3
from botocore.exceptions import ClientError
from pydantic import BaseModel

from gdshoplib.core.settings import S3Settings


class File(BaseModel):
    key: str
    content: Optional[bytes]
    mime: Optional[str]


class S3v2:
    _client = None

    def __init__(self, bucket="gdshop"):
        self.bucket = bucket
        self.content = None

    @classmethod
    @property
    def client(cls):
        if not cls._client:
            settings = S3Settings()
            cls._client = boto3.session.Session().client(
                service_name="s3",
                endpoint_url=settings.ENDPOINT_URL,
                aws_access_key_id=settings.ACCESS_KEY,
                aws_secret_access_key=settings.SECRET_KEY,
            )
        return cls._client

    def exception_handle(func):
        def wrap(*args, **kwargs):
            try:
                r = func(*args, **kwargs)
                return r["ResponseMetadata"]["HTTPStatusCode"] == 200
            except (ClientError, KeyError):
                return None

        return wrap

    @exception_handle
    def put(self, object: File):
        return self.client.put_object(
            Bucket=self.bucket,
            Key=object.key,
            Body=object.content,
            ACL="public-read",
            StorageClass="ICE",
            ContentType=object.mime,
        )

    @exception_handle
    def exists(self, object: File):
        return self.__class__.client.head_object(Bucket=self.bucket, Key=object.key)

    @exception_handle
    def get(self, object: File):
        return self.__class__.client.get_object(Bucket=self.bucket, Key=object.key)

    @exception_handle
    def delete(self, object: File):
        return self.__class__.client.delete_object(Bucket=self.bucket, Key=object.key)

    def __str__(self) -> str:
        return f"{self.__class__}: {self.bucket}"

    def __repr__(self) -> str:
        return f"{self.__class__}: {self.bucket}"
