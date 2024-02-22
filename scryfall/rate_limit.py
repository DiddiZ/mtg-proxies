from __future__ import annotations

import threading
import time
from types import TracebackType


class RateLimiter:
    """Context manager for enforcing a rate limit to API calls."""

    def __init__(self, delay: float) -> None:
        """Initialie this RateLimit.

        Args:
            delay: Delay between calls in seconds
        """
        self.delay = delay
        self.lock = threading.Lock()
        self.last_call = 0

    def __enter__(self) -> None:
        with self.lock:  # Prevent asynchronous access
            # Check time since last call
            if time.time() < self.last_call + self.delay:  # Wait if neccessary
                time.sleep(self.last_call + self.delay - time.time())
            self.last_call = time.time()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        pass  # Nothing to do here
