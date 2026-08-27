"""Object Storage Package."""
from packages.storage.base import ObjectStorage
from packages.storage.minio import MinIOStorageAdapter
from packages.storage.mock import DevMockStorageAdapter

__all__ = [
    "ObjectStorage",
    "MinIOStorageAdapter",
    "DevMockStorageAdapter"
]
