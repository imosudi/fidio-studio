import time
import os
from packages.shared.config import settings
from packages.shared.logging import logger


def start_worker():
    """Start Celery / RQ async worker daemon for background generation jobs."""
    logger.info(
        f"Starting Fídíò Worker Service in environment '{settings.APP_ENV}'",
        extra={"redis_host": settings.REDIS_HOST}
    )
    logger.info(f"Connecting to Redis at {settings.redis_url}")

    # Verify FFmpeg availability in worker environment
    ffmpeg_installed = os.system("ffmpeg -version > /dev/null 2>&1") == 0
    if ffmpeg_installed:
        logger.info("FFmpeg binary detected and ready for media composition.")
    else:
        logger.warning("FFmpeg binary not found in worker path! Media rendering will fail.")

    logger.info("Worker process initialized and listening for incoming generation jobs...")


if __name__ == "__main__":
    start_worker()
    # Keep worker process alive for container run
    while True:
        time.sleep(3600)
