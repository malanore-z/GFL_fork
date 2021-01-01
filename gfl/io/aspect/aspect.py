from functools import wraps


def args2kwargs(func, args, kwargs):
    for i in range(len(args)):
        kwargs[func.__code__.co_varnames[i]] = args[i]
    return kwargs


def Aspect(advice, position="after"):

    if position not in ["before", "after"]:
        raise ValueError("positon only support before and after.")

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            if position == "before":
                new_kwargs = args2kwargs(advice, args, kwargs)
                aspect_ret = advice(*args, **new_kwargs)
                if aspect_ret is None:
                    aspect_ret = {}
                return func(**aspect_ret)
            elif position == "after":
                new_kwargs = args2kwargs(func, args, kwargs)
                func_ret = func(*args, **new_kwargs)
                if func_ret is None:
                    func_ret = {}
                advice(**func_ret)
        return wrapper
    return decorator
