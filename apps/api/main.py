import uuid
import time
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from packages.shared.config import settings
from packages.shared.logging import logger
from packages.shared.exceptions import FidioException

app = FastAPI(
    title=settings.APP_NAME,
    description="Fídíò Studio REST API — AI Video Generation Platform",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def correlation_id_middleware(request: Request, call_next):
    """Correlation ID and Structured Logging Middleware."""
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
    request.state.correlation_id = correlation_id
    start_time = time.time()

    response: Response = await call_next(request)
    duration_ms = round((time.time() - start_time) * 1000, 2)

    response.headers["X-Correlation-ID"] = correlation_id
    logger.info(
        f"{request.method} {request.url.path} -> {response.status_code} ({duration_ms}ms)",
        extra={"correlation_id": correlation_id}
    )
    return response


@app.exception_handler(FidioException)
async def fidio_exception_handler(request: Request, exc: FidioException):
    """Global handler for domain & platform exceptions."""
    correlation_id = getattr(request.state, "correlation_id", "unknown")
    logger.warning(
        f"Domain Error [{exc.code}]: {exc.message}",
        extra={"correlation_id": correlation_id}
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
                "request_id": correlation_id
            }
        }
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Global handler for unhandled internal exceptions."""
    correlation_id = getattr(request.state, "correlation_id", "unknown")
    logger.error(f"Unhandled Exception: {exc}", exc_info=True, extra={"correlation_id": correlation_id})
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred. Please contact system administrator.",
                "details": {},
                "request_id": correlation_id
            }
        }
    )


# Health & Readiness Endpoints
@app.get("/healthz", tags=["Health"])
@app.get("/readyz", tags=["Health"])
@app.get("/livez", tags=["Health"])
async def health_check():
    """Liveness & Readiness health probe."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "version": "0.1.0"
    }


@app.get("/", tags=["Root"])
async def root():
    return {
        "brand": "Fídíò",
        "product": "Fídíò Studio API",
        "tagline": "Imagine. Create. Fídíò.",
        "documentation": "/docs"
    }
