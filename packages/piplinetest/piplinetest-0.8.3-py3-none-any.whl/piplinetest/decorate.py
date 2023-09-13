import threading
import multiprocessing


def lock_decorator(lock_type: str = "thread", decorate_method: str = "execute"):
    """class decorator for threading|multiprocessing.Lock method

    make `class` `decorate_method` `lock`

    Args:
        lock_type (str, optional): _description_. Defaults to "thread".
        decorate_method (str, optional): _description_. Defaults to "execute".
    """

    def lock_decorator(cls):
        original_method = getattr(cls, decorate_method)

        if lock_type == "thread":
            lock = threading.Lock()
        elif lock_type == "process":
            lock = multiprocessing.Lock()
        else:
            raise ValueError("lock_type must be threading|process!")

        def new_lock_method(self, *args, **kwargs):
            lock.acquire()
            try:
                result = original_method(self, *args, **kwargs)
                return result
            finally:
                lock.release()

        setattr(cls, decorate_method, new_lock_method)
        return cls

    return lock_decorator
