"Inspects functions signatures"
from inspect import signature, _empty
from typing import Callable


def types_checker(func: Callable):
    """Checks the types of annotations of a func and raises error if not corresponding.
    Meant to be used as a decorator

    Args:
        func (Callable): a func
    """
    def wrapper(*args, **kwargs):
        """
        Corps de test
        """
        arguments = args + tuple(kwargs.keys())
        args_types = [type(arg) for arg in arguments]
        signature_func = signature(func).parameters
        ret_annotation = signature(func).return_annotation
        annotations = [
            signature_func[elt].annotation for elt in signature_func]
        comp = zip(args_types, annotations)
        for i, (input_type, annotation) in enumerate(comp):
            if annotation is not _empty and input_type != annotation:
                try:
                    annotation(arguments[i])
                except TypeError as exc:
                    raise TypeError(
                        f"Error in {func.__name__} : input type {input_type} incompatible with {annotation}") from exc
        retour = func(*args, **kwargs)
        if ret_annotation is not _empty and ret_annotation is not None and isinstance(retour, ret_annotation):
            raise TypeError(
                f"Error in {func.__name__} : return type {type(retour)} does not match {ret_annotation}")

        return retour
    return wrapper
