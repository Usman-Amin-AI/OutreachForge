import time
import functools
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from typing import Callable, Any
from .errors import ExternalAPIError, CircuitOpenError
from .logger import log, warn


class CircuitBreaker:
    def __init__(self, max_failures: int = 3, reset_timeout: int = 60):
        self.max_failures = max_failures
        self.reset_timeout = reset_timeout
        self.failure_count = 0
        self.last_failure_timestamp = 0.0
        self.state = "CLOSED"

    def _open(self) -> None:
        self.state = "OPEN"
        self.last_failure_timestamp = time.time()
        warn("circuit_breaker_opened", failure_count=self.failure_count)

    def _close(self) -> None:
        self.state = "CLOSED"
        self.failure_count = 0
        log("circuit_breaker_closed")

    def _half_open(self) -> None:
        self.state = "HALF_OPEN"
        log("circuit_breaker_half_open")

    def call(self, func: Callable[..., Any], *args, **kwargs) -> Any:
        if self.state == "OPEN":
            if time.time() - self.last_failure_timestamp > self.reset_timeout:
                self._half_open()
            else:
                raise CircuitOpenError("Circuit is open; skipping external call")

        try:
            result = func(*args, **kwargs)
            if self.state == "HALF_OPEN":
                self._close()
            return result
        except ExternalAPIError as exc:
            self.failure_count += 1
            warn("external_api_failure", error=str(exc), failure_count=self.failure_count)
            if self.failure_count >= self.max_failures:
                self._open()
            raise


def call_with_timeout(func: Callable[..., Any], timeout: float, *args, **kwargs) -> Any:
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(func, *args, **kwargs)
        try:
            return future.result(timeout=timeout)
        except FutureTimeoutError as exc:
            raise ExternalAPIError(f"Operation timed out after {timeout} seconds") from exc


def retry(max_attempts: int = 3, base_delay: float = 1.0, backoff_factor: float = 2.0):
    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            attempt = 0
            while True:
                try:
                    return fn(*args, **kwargs)
                except ExternalAPIError as exc:
                    attempt += 1
                    if attempt >= max_attempts:
                        warn("retry_exhausted", attempts=attempt)
                        raise
                    delay = base_delay * (backoff_factor ** (attempt - 1))
                    warn("retry_backoff", attempt=attempt, delay=delay, error=str(exc))
                    time.sleep(delay)
        return wrapper
    return decorator


class ResilientProxy:
    def __init__(self, target: Any, circuit_breaker: CircuitBreaker, timeout: float = 20.0):
        self._target = target
        self._circuit = circuit_breaker
        self._timeout = timeout

    def __getattr__(self, item: str) -> Any:
        attr = getattr(self._target, item)
        if callable(attr):
            def wrapper(*args, **kwargs):
                def call_target():
                    try:
                        return attr(*args, **kwargs)
                    except Exception as exc:
                        raise ExternalAPIError(f"External call failed on {item}: {exc}") from exc
                return self._circuit.call(lambda: call_with_timeout(call_target, self._timeout))
            return wrapper
        return attr

    def __call__(self, *args, **kwargs) -> Any:
        def call_target():
            try:
                return self._target(*args, **kwargs)
            except Exception as exc:
                raise ExternalAPIError(f"External call failed: {exc}") from exc
        return self._circuit.call(lambda: call_with_timeout(call_target, self._timeout))
