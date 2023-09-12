from typing import TypeVar, Optional, Callable, Union

T = TypeVar('T')


def default(arg: Optional[T], dflt: Union[T, Callable[[], T]]) -> T:
    if arg is not None:
        return arg

    if callable(dflt):
        return dflt()
    return dflt


# noinspection PyPep8Naming
def raise_if_None(arg: Optional[T], arg_name: str) -> T:
    if arg is None:
        raise ValueError(f'Argument "{arg_name}" cannot be None')
    return arg

