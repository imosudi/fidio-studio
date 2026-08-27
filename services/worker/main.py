import asyncio
import signal
import sys
from typing import Optional
from sqlalchemy import select

from packages.domain.database import AsyncSessionLocal
from packages.domain.entities import GenerationJob, JobStatus
from packages.domain.state import JobStateMachine
from packages.generation.orchestrator import PipelineOrchestrator, JobCancelledException
from packages.shared.config import settings
from packages.shared.logging import logger

running = True


def handle_shutdown(signum, frame):
    global running
    logger.info(f"Worker received shutdown signal ({signum}). Gracefully stopping...")
    running = False


class WorkerProcess:
    """Asynchronous background worker process processing QUEUED generation jobs."""

    def __init__(self, poll_interval_seconds: float = 2.0):
        self.poll_interval = poll_interval_seconds
        self.orchestrator = PipelineOrchestrator()

    async def run_forever(self):
        logger.info(f"Fídíò Generation Worker initialized. Polling interval: {self.poll_interval}s")

        while running:
            try:
                job_processed = await self.process_next_job()
                if not job_processed:
                    await asyncio.sleep(self.poll_interval)
            except Exception as e:
                logger.error(f"Worker iteration exception: {e}", exc_info=True)
                await asyncio.sleep(self.poll_interval)

        logger.info("Worker process terminated gracefully.")

    async def process_next_job(self) -> bool:
        """Poll PostgreSQL for single QUEUED job and process pipeline execution."""
        async with AsyncSessionLocal() as session:
            query = (
                select(GenerationJob)
                .where(GenerationJob.status == JobStatus.QUEUED)
                .order_by(GenerationJob.created_at.asc())
                .limit(1)
                .with_for_update(skip_locked=True)
            )
            result = await session.execute(query)
            job = result.scalar_one_or_none()

            if not job:
                return False

            logger.info(f"Worker acquired QUEUED GenerationJob ID={job.id}")

            try:
                await self.orchestrator.execute_job(job.id, session)
                return True

            except JobCancelledException:
                logger.info(f"Worker finished processing cancelled job ID={job.id}")
                return True

            except Exception as exc:
                logger.error(f"Execution error processing job ID={job.id}: {exc}")
                # Retry handling logic
                retry_success = JobStateMachine.increment_retry(job)
                if retry_success:
                    logger.warning(
                        f"Retrying job ID={job.id}. Attempt {job.retry_count}/{job.max_retries}"
                    )
                else:
                    logger.error(f"Max retries reached for job ID={job.id}. Job marked FAILED.")
                await session.commit()
                return True


if __name__ == "__main__":
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    worker = WorkerProcess()
    asyncio.run(worker.run_forever())
