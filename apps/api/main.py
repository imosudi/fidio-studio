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
async def security_and_correlation_middleware(request: Request, call_next):
    """Security Headers, Path Traversal Check, and Correlation ID Middleware."""
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
    request.state.correlation_id = correlation_id
    start_time = time.time()

    # Path Traversal & Injection Prevention
    raw_path = str(request.url.path)
    if ".." in raw_path or "%2e%2e" in raw_path.lower():
        logger.warning(f"Rejected path traversal attempt: {raw_path}", extra={"correlation_id": correlation_id})
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "error": {
                    "code": "PATH_TRAVERSAL_DETECTED",
                    "message": "Invalid request path containing unsafe traversal sequences.",
                    "details": {},
                    "request_id": correlation_id
                }
            }
        )

    response: Response = await call_next(request)
    duration_ms = round((time.time() - start_time) * 1000, 2)

    # Inject Security Headers & Record Telemetry Metrics
    response.headers["X-Correlation-ID"] = correlation_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    from packages.shared.telemetry import metrics
    metrics.inc_counter("http_requests_total", labels={"method": request.method, "status": str(response.status_code)})
    metrics.observe_histogram("http_request_duration_seconds", value=duration_ms / 1000.0, labels={"method": request.method})

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


@app.get("/metrics", tags=["Observability"])
async def get_prometheus_metrics():
    """Prometheus metrics scraper endpoint."""
    from packages.shared.telemetry import metrics
    return Response(content=metrics.generate_prometheus_text(), media_type="text/plain; version=0.0.4")


@app.get("/", tags=["Root"])
async def root():
    return {
        "brand": "Fídíò",
        "product": "Fídíò Studio API",
        "tagline": "Imagine. Create. Fídíò.",
        "documentation": "/docs"
    }


# Include API Routers
from apps.api.routes import projects_router, generation_router, jobs_router, assets_router

app.include_router(projects_router, prefix=settings.API_V1_PREFIX)
app.include_router(generation_router, prefix=settings.API_V1_PREFIX)
app.include_router(jobs_router, prefix=settings.API_V1_PREFIX)
app.include_router(assets_router, prefix=settings.API_V1_PREFIX)

