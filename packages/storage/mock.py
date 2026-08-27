from typing import Optional, Dict, Any
from packages.storage.base import ObjectStorage
from packages.shared.exceptions import StorageException


class DevMockStorageAdapter(ObjectStorage):
    """In-memory dev mock object storage adapter for local unit testing and offline development."""

    def __init__(self):
        self._store: Dict[str, Dict[str, bytes]] = {}
        self._metadata: Dict[str, Dict[str, Dict[str, Any]]] = {}

    def put_object(
        self,
        bucket: str,
        object_key: str,
        data: bytes,
        content_type: str = "application/octet-stream",
        metadata: Optional[Dict[str, str]] = None
    ) -> str:
        if bucket not in self._store:
            self._store[bucket] = {}
            self._metadata[bucket] = {}

        self._store[bucket][object_key] = data
        self._metadata[bucket][object_key] = {
            "content_type": content_type,
            "content_length": len(data),
            "metadata": metadata or {}
        }
        return object_key

    def get_object(self, bucket: str, object_key: str) -> bytes:
        if bucket not in self._store or object_key not in self._store[bucket]:
            raise StorageException(f"Object '{object_key}' not found in bucket '{bucket}'")
        return self._store[bucket][object_key]

    def delete_object(self, bucket: str, object_key: str) -> bool:
        if bucket in self._store and object_key in self._store[bucket]:
            del self._store[bucket][object_key]
            del self._metadata[bucket][object_key]
            return True
        return False

    def object_exists(self, bucket: str, object_key: str) -> bool:
        return bucket in self._store and object_key in self._store[bucket]

    def get_metadata(self, bucket: str, object_key: str) -> Dict[str, Any]:
        if bucket not in self._metadata or object_key not in self._metadata[bucket]:
            raise StorageException(f"Metadata for '{object_key}' not found in bucket '{bucket}'")
        return self._metadata[bucket][object_key]

    def generate_presigned_url(
        self,
        bucket: str,
        object_key: str,
        expires_in_seconds: int = 3600
    ) -> str:
        return f"http://localhost:9000/{bucket}/{object_key}?token=mock_presigned_url_token"
