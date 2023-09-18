# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3
"""
Module building on behaviour from the builtin functools  module
"""

from functools import lru_cache, wraps
from typing import Any, Callable, Optional, TypeVar, cast

from .globals import prefix_name

F = TypeVar("F", bound=Callable[..., Any])
_T = TypeVar("_T", bound=Callable[..., Any])


def prefix_aware_cache(func: F) -> F:
    """
    A variant of functools.lru_cache which treats the prefix as if it were an argument
    """

    @wraps(func)
    @lru_cache(maxsize=None)
    def inner(prefix: Optional[str], *args, **kwargs):
        return func(*args, **kwargs)

    @wraps(func)
    def prefix_wrapper(*args, **kwargs):
        return inner(prefix_name(), *args, **kwargs)

    prefix_wrapper.cache_clear = inner.cache_clear  # type: ignore
    return cast(F, prefix_wrapper)


def deprecated(*args, **kwargs):
    """Custom version of deprecated.sphinx which does nothing if deprecated isn't installed"""
    try:
        from deprecated.sphinx import deprecated
    except ModuleNotFoundError:

        def deprecated(*args, **kwargs):  # type: ignore
            def inner(func):
                return func

            return inner

    @wraps(deprecated)
    def decorator(func: Callable[..., _T]) -> Callable[..., _T]:
        @deprecated(*args, **kwargs)
        @wraps(func)
        def inner(*args, **kwargs):
            return func(*args, **kwargs)

        return cast(Callable[..., _T], inner)

    return decorator
