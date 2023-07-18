from functools import wraps
import threading
import timeit

def threaded(func):
    @wraps(func)
    def async_func(*args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.start()

    return async_func

def measure_execution_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = timeit.default_timer()
        result = func(*args, **kwargs)
        end_time = timeit.default_timer()

        execution_time = end_time - start_time
        print(f"Execution Time of {func.__name__}: {execution_time} seconds")
        return result

    return wrapper