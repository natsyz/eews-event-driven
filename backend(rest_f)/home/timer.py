import time

def getime(func):
    def func_wrapper(*args, **kwargs):
        start_time = time.time()
        func(*args, **kwargs)
        print("function {} completed in - {} seconds".format(
            func.__name__,
            time.time()-start_time))
    return func_wrapper