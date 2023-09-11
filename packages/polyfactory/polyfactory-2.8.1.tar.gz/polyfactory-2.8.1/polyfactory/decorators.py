from __future__ import annotations

import inspect
from typing import Any, Callable

from polyfactory import PostGenerated


class post_generated:  # noqa: N801
    """Descriptor class for wrapping a classmethod into a ``PostGenerated`` field."""

    __slots__ = ("method", "cache")

    def __init__(self, method: Callable | classmethod) -> None:
        if not isinstance(method, classmethod):
            raise TypeError("post_generated decorator can only be used on classmethods")
        self.method = method
        self.cache: dict[type, PostGenerated] = {}

    def __get__(self, obj: Any, objtype: type) -> PostGenerated:
        try:
            return self.cache[objtype]
        except KeyError:
            pass

        fn = self.method.__func__
        fn_args = inspect.getfullargspec(fn).args[1:]

        def new_fn(name: str, values: dict[str, Any]) -> Any:
            return fn(objtype, **{arg: values[arg] for arg in fn_args if arg in values})

        return self.cache.setdefault(objtype, PostGenerated(new_fn))
