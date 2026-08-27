from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, BinaryIO


class ObjectStorage(ABC):
    """Abstract interface for object storage adapters (MinIO, AWS S3, DevMock)."""

    @abstractmethod
    def put_object(
        self,
        bucket: str,
        object_key: str,
        data: bytes,
        content_type: str = "application/octet-stream",
        metadata: Optional[Dict[str, str]] = None
    ) -> str:
        """Upload object bytes to specified storage bucket. Return storage URL or object key."""
        pass

    @abstractmethod
    def get_object(self, bucket: str, object_key: str) -> bytes:
        """Download object content bytes from storage bucket."""
        pass

    @abstractmethod
    def delete_object(self, bucket: str, object_key: str) -> bool:
        """Delete specified object key from storage bucket."""
        pass

    @abstractmethod
    def object_exists(self, bucket: str, object_key: str) -> bool:
        """Check whether object key exists in storage bucket."""
        pass

    @abstractmethod
    def get_metadata(self, bucket: str, object_key: str) -> Dict[str, Any]:
        """Fetch metadata headers for specified object key."""
        pass

    @abstractmethod
    def generate_presigned_url(
        self,
        bucket: str,
        object_key: str,
        expires_in_seconds: int = 3600
    ) -> str:
        """Generate presigned HTTP GET download URL for client media retrieval."""
        pass
