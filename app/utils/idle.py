"""Inactivity tracking for automatic log-out."""
import time


class IdleTracker:
    def __init__(self, timeout_seconds: float, clock=time.monotonic):
        self.timeout = timeout_seconds
        self._clock = clock
        self._last = clock()

    def touch(self) -> None:
        self._last = self._clock()

    def expired(self) -> bool:
        return self._clock() - self._last >= self.timeout
