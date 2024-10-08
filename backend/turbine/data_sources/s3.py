from .interface import DataSource, Document
from .splitter import RecursiveSplitter
from typing import Literal, Any
import boto3
from urllib.parse import urlparse
from turbine.config import config
import hashlib
from botocore.exceptions import ParamValidationError


class S3(DataSource):
    type: Literal["s3"]
    url: str
    splitter: RecursiveSplitter
    _client: Any
    _bucket: str
    _prefix: str

    def __init__(self, **data):
        super().__init__(**data)
        self._client = boto3.client(
            "s3",
            aws_access_key_id=config.aws_access_key_id,
            aws_secret_access_key=config.aws_secret_access_key,
        )
        parsed = urlparse(self.url)
        self._bucket = parsed.netloc
        self._prefix = parsed.path.lstrip("/")

    def validate_config(self) -> None:
        if self._bucket is None:
            raise ValueError("Missing bucket in S3 URL")
        if self._prefix is None:
            raise ValueError("Missing prefix in S3 URL")
        try:
            self._client.head_bucket(Bucket=self._bucket)
        except (self._client.exceptions.ClientError, ParamValidationError):
            raise ValueError("Invalid or inaccessible S3 URL")

    def get_keys(self) -> list[str]:
        keys = []
        continuation_token = None

        while True:
            if continuation_token is None:
                response = self._client.list_objects_v2(
                    Bucket=self._bucket, Prefix=self._prefix
                )
            else:
                response = self._client.list_objects_v2(
                    Bucket=self._bucket,
                    Prefix=self._prefix,
                    ContinuationToken=continuation_token,
                )

            if "Contents" in response:
                for obj in response["Contents"]:
                    keys.append(obj["Key"])

            if not response["IsTruncated"]:
                break
            continuation_token = response["NextContinuationToken"]

        return keys

    def get_documents(self, key: str) -> list[Document]:
        response = self._client.get_object(Bucket=self._bucket, Key=key)
        text = response["Body"].read().decode("utf-8")
        return [
            Document(
                id=hashlib.sha256(document.text.encode("utf-8")).hexdigest(),
                content=document.text,
                metadata=dict(**document.metadata, s3_object_name=key),
            )
            for document in self.splitter.split(text)
        ]
