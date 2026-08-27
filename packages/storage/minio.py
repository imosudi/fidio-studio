import io
from typing import Optional, Dict, Any
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

from packages.storage.base import ObjectStorage
from packages.shared.config import settings
from packages.shared.exceptions import StorageException
from packages.shared.logging import logger


class MinIOStorageAdapter(ObjectStorage):
    """Production MinIO S3 object storage adapter."""

    def __init__(
        self,
        endpoint_url: Optional[str] = None,
        external_endpoint_url: Optional[str] = None,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        use_ssl: Optional[bool] = None
    ):
        self.endpoint_url = endpoint_url or (
            f"https://{settings.MINIO_ENDPOINT}" if settings.MINIO_USE_SSL else f"http://{settings.MINIO_ENDPOINT}"
        )
        self.external_endpoint_url = external_endpoint_url or settings.MINIO_EXTERNAL_ENDPOINT
        self.access_key = access_key or settings.MINIO_ACCESS_KEY
        self.secret_key = secret_key or settings.MINIO_SECRET_KEY

        # Initialize boto3 S3 client for MinIO
        self.client = boto3.client(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            config=Config(signature_version="s3v4"),
            region_name="us-east-1"
        )
        self.presigned_client = boto3.client(
            "s3",
            endpoint_url=self.external_endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            config=Config(signature_version="s3v4"),
            region_name="us-east-1"
        )
        self._ensure_buckets_exist()

    def _ensure_buckets_exist(self):
        """Idempotently ensure required media and render buckets exist."""
        for bucket in [settings.MINIO_BUCKET_MEDIA, settings.MINIO_BUCKET_RENDERS]:
            try:
                self.client.head_bucket(Bucket=bucket)
            except ClientError:
                try:
                    self.client.create_bucket(Bucket=bucket)
                    logger.info(f"Initialized MinIO bucket '{bucket}'")
                except Exception as e:
                    logger.warning(f"Could not initialize MinIO bucket '{bucket}': {e}")

    def put_object(
        self,
        bucket: str,
        object_key: str,
        data: bytes,
        content_type: str = "application/octet-stream",
        metadata: Optional[Dict[str, str]] = None
    ) -> str:
        try:
            extra_args = {"ContentType": content_type}
            if metadata:
                extra_args["Metadata"] = metadata

            self.client.put_object(
                Bucket=bucket,
                Key=object_key,
                Body=data,
                **extra_args
            )
            logger.info(f"Uploaded object '{object_key}' to MinIO bucket '{bucket}' ({len(data)} bytes)")
            return object_key
        except Exception as e:
            logger.error(f"MinIO put_object failed for bucket='{bucket}' key='{object_key}': {e}")
            raise StorageException(f"Failed to upload object '{object_key}': {str(e)}")

    def get_object(self, bucket: str, object_key: str) -> bytes:
        try:
            response = self.client.get_object(Bucket=bucket, Key=object_key)
            return response["Body"].read()
        except Exception as e:
            logger.error(f"MinIO get_object failed for bucket='{bucket}' key='{object_key}': {e}")
            raise StorageException(f"Failed to fetch object '{object_key}': {str(e)}")

    def delete_object(self, bucket: str, object_key: str) -> bool:
        try:
            self.client.delete_object(Bucket=bucket, Key=object_key)
            return True
        except Exception as e:
            logger.error(f"MinIO delete_object failed for key='{object_key}': {e}")
            raise StorageException(f"Failed to delete object '{object_key}': {str(e)}")

    def object_exists(self, bucket: str, object_key: str) -> bool:
        try:
            self.client.head_object(Bucket=bucket, Key=object_key)
            return True
        except ClientError:
            return False

    def get_metadata(self, bucket: str, object_key: str) -> Dict[str, Any]:
        try:
            res = self.client.head_object(Bucket=bucket, Key=object_key)
            return {
                "content_type": res.get("ContentType"),
                "content_length": res.get("ContentLength"),
                "metadata": res.get("Metadata", {}),
                "last_modified": res.get("LastModified")
            }
        except Exception as e:
            raise StorageException(f"Failed to fetch metadata for object '{object_key}': {str(e)}")

    def generate_presigned_url(
        self,
        bucket: str,
        object_key: str,
        expires_in_seconds: int = 3600
    ) -> str:
        try:
            url = self.presigned_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": bucket, "Key": object_key},
                ExpiresIn=expires_in_seconds
            )
            return url
        except Exception as e:
            logger.error(f"Failed to generate presigned URL for object '{object_key}': {e}")
            return f"{self.external_endpoint_url}/{bucket}/{object_key}"
