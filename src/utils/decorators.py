from functools import wraps
from typing import Any, Callable, Tuple

from tenacity import RetryError, Retrying, retry_if_exception_type, stop_after_delay


def retry(
    stop_after: float = 2.0, value_if_error: Any = None, exceptions: Tuple[Exception] = (Exception), *args, **kwargs
):
    def callable_decorator(fn: Callable):
        @wraps(fn)
        def decorated_function(*fn_args):
            try:
                for retry in Retrying(stop=stop_after_delay(stop_after), retry=retry_if_exception_type(exceptions)):
                    with retry:
                        return fn(*fn_args, *args, **kwargs)

            except RetryError:
                return value_if_error

        return decorated_function

    return callable_decorator
