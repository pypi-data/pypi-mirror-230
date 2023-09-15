import warnings

from typing import Callable, Optional


class WarningError(Exception):
    """The code did not issue the expected warning."""

class DupaWarning(Warning): ...


def foo():
    warnings.warn("dupa", DupaWarning)
    return 10
    

def check_warning(
    function_call: Callable,
    warning_type: Optional[Warning] = None,
    handle_with: Exception = WarningError,
    message=Optional[None]):
    with warnings.catch_warnings(record=True) as w:
        warning = w[0]
        if not warning_type:
            if not issubclass(warning, Warning):
                raise handle_with
        

with warnings.catch_warnings(record=True) as w:
    x = foo()
    ww = w[0]
    print(f"""
        {ww.__class__ = }
        {ww.category = }
        {type(ww.message).__name__ = }
        {issubclass(ww.category, Warning)}
    """)
    assert x == 10
    