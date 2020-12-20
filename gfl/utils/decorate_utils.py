from functools import wraps
from typing import Sequence


def NotNull(all=None, any=None, ret=None):

    if any is None:
        any = []
    if all is None:
        all = []

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):

            for arg in all:
                try:
                    idx = int(arg)
                    if len(args) <= idx or args[idx] is None:
                        return ret
                except:
                    if kwargs.get(arg) is None:
                        return ret

            if len(any) == 0:
                return func(*args, **kwargs)

            for arg in any:
                try:
                    idx = int(arg)
                    if len(args) > idx and args[idx] is not None:
                        return func(*args, **kwargs)
                except:
                    if kwargs.get(arg) is not None:
                        return func(*args, **kwargs)

            return ret

        return wrapper

    return decorator


def AllArgsNotNone(ret=None):

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            for arg in args:
                if arg is None:
                    return ret
            for k, v in kwargs.items():
                if v is None:
                    return ret
            return func(*args, **kwargs)

        return wrapper

    return decorator


def AnyArgsNotNone(ret=None):

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            for arg in args:
                if arg is not None:
                    return func(*args, **kwargs)
            for k, v in kwargs.items():
                if v is not None:
                    return func(*args, **kwargs)

            return ret

        return wrapper

    return decorator
