import logging
import time

from functools import wraps


def measure_time_async(async_func):
    @wraps(async_func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await async_func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        logging.info(f'Функция "{async_func.__name__}" выполнена за {execution_time:.4f} секунд.')
        return result

    return wrapper


def measure_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logging.info(f"Время выполнения функции {func.__name__}: {end_time - start_time} секунд")
        return result

    return wrapper
