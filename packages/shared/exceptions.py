from typing import Any, Dict, Optional


class FidioException(Exception):
    """Base exception class for all Fídíò platform errors."""
    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}


class EntityNotFoundException(FidioException):
    def __init__(self, entity_name: str, entity_id: str):
        super().__init__(
            message=f"{entity_name} with ID '{entity_id}' not found.",
            code="ENTITY_NOT_FOUND",
            status_code=404,
            details={"entity": entity_name, "id": entity_id}
        )


class ValidationException(FidioException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=400,
            details=details
        )


class ProviderException(FidioException):
    def __init__(self, provider: str, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Provider '{provider}' failed: {message}",
            code="PROVIDER_ERROR",
            status_code=502,
            details={"provider": provider, **(details or {})}
        )


class StorageException(FidioException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Storage operation failed: {message}",
            code="STORAGE_ERROR",
            status_code=500,
            details=details
        )
