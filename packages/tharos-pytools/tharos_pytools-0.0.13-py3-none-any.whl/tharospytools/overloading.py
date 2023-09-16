'Module for overloading functions'
from typing import Callable


def overload(*dtypes: list):
    """Allows C-like overloading of functions
    Designed to be used as a decorator, like :

    @overload(int)
    def foo(number:int) -> None:
        pass

    @overload(str,list)
    def foo(string:str,some_list:list) -> None:
        pass
    """
    if not hasattr(overload, 'mapper'):
        overload.mapper = {}

    def funchandler(func: Callable):
        overload.mapper[(func.__qualname__, dtypes)] = func

        def funcwrapper(*args: list, **kwargs: dict):
            return overload.mapper[(func.__qualname__, tuple(map(type, (*args, *kwargs.values()))))](*args, **kwargs)
        return funcwrapper
    return funchandler
