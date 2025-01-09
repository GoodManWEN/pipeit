import time
from functools import wraps 
from typing import Callable, Awaitable, Any, Union
from functools import cache
from inspect import iscoroutinefunction
import asyncio


def retry(times: int = 1, delay: float = 1) -> Union[Callable, Awaitable]:
    """
    Attempt to call a function, if it fails, try again with a specified delay.

    Usage:
    >>> @retry(times=3, delay=1)
    >>> def connect() -> None:
    >>>     time.sleep(1)
    >>>     raise Exception("Could not connect to internet...")
    >>> connect()
    """
    times, delay = int(times), float(delay)
    if times < 1 or delay < 0:
        raise ValueError("Parameter times must >= 1 and delay must >= 0")
    
    def decorator(func: Union[Callable, Awaitable]) -> Union[Callable, Awaitable]:
        if iscoroutinefunction(func):
            @wraps(func)
            async def awrapper(*args, **kwargs) -> Any:
                for i in range(1, times+1):
                    try:
                        return await func(*args, **kwargs)
                    except Exception as e:
                        if i >= times:
                            # Break out of the loop if the max amount of times is exceeded
                            print(f'ARetry Error: {type(e)}, {repr(e)}.')
                            print(f'"{func.__name__}()" failed after {times} retries.')
                        else:
                            print(f'ARetry Error: {type(e)}, {repr(e)} -> Retrying...')
                            if delay > 0:
                                await asyncio.sleep(delay)
            return awrapper
        else:
            @wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                for i in range(1, times+1):
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        if i >= times:
                            # Break out of the loop if the max amount of times is exceeded
                            print(f'Retry Error: {type(e)}, {repr(e)}.')
                            print(f'"{func.__name__}()" failed after {times} retries.')
                        else:
                            print(f'Retry Error: {type(e)}, {repr(e)} -> Retrying...')
                            if delay > 0:
                                time.sleep(delay)
            return wrapper
    return decorator

