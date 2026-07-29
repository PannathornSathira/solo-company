from concurrent.futures import Future, ThreadPoolExecutor
import logging
from threading import RLock
from uuid import UUID

from app.runtime.service import RuntimeService

logger = logging.getLogger(__name__)


class RuntimeCoordinator:
    def __init__(self, runtime: RuntimeService) -> None:
        self.runtime = runtime
        self._executor = ThreadPoolExecutor(
            max_workers=1,
            thread_name_prefix="phase1-runtime",
        )
        self._lock = RLock()
        self._futures: dict[UUID, Future[None]] = {}
        self._closed = False

    def submit(self, run_id: UUID) -> bool:
        with self._lock:
            if self._closed:
                return False
            existing = self._futures.get(run_id)
            if existing is not None and not existing.done():
                return False
            future = self._executor.submit(self.runtime.resume_run, run_id)
            self._futures[run_id] = future
            future.add_done_callback(
                lambda completed, target=run_id: self._finished(
                    target, completed
                )
            )
            return True

    def recover_incomplete_runs(self) -> None:
        for run_id in self.runtime.list_recoverable_run_ids():
            self.submit(run_id)

    def shutdown(self) -> None:
        with self._lock:
            self._closed = True
        self._executor.shutdown(wait=True, cancel_futures=False)

    def _finished(
        self, run_id: UUID, future: Future[None]
    ) -> None:
        try:
            future.result()
        except Exception:
            logger.exception(
                "Unhandled runtime worker failure for run_id=%s", run_id
            )
        finally:
            with self._lock:
                current = self._futures.get(run_id)
                if current is future:
                    self._futures.pop(run_id, None)
