import logging
import time


def measure_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logging.info(f"Время выполнения функции {func.__name__}: {end_time - start_time} секунд")
        return result

    return wrapper