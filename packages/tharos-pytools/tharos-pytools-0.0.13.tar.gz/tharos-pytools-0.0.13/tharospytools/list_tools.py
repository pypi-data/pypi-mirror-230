"Utilities for lists"
from typing import Generator, Callable


def cast(dtype: type):
    """Allows dynamic cast for generators

    Args:
        dtype (type): a data type
    """
    def funchandler(func: Callable):
        def funcwrapper(*args: list, **kwargs: dict):
            return dtype(func(*args, **kwargs))
        return funcwrapper
    return funchandler


@cast(list)
def flatten(list_to_flatten: list) -> Generator:
    """Flattens a potentially multi-level list

    Args:
        list_to_flatten (list): a list eventually containing other lists and elts

    Yields:
        Generator: series of elements, converted by decorator to a list
    """
    for elt in list_to_flatten:
        if isinstance(elt, list):
            yield from flatten(elt)
        else:
            yield elt
