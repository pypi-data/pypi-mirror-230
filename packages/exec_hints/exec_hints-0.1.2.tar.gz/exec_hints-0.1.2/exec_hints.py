from contextlib import suppress
from functools import wraps
from inspect import getfullargspec, isclass
from sys import modules
from types import GenericAlias, ModuleType, UnionType
from typing import Callable, ParamSpec, TypeVar, get_type_hints

P = ParamSpec("P")
T = TypeVar("T")


def apply_hint(hint, arg):
    if isinstance(hint, GenericAlias):
        args = hint.__args__
        t = hint.__mro__[0]
        if not args:
            return t(arg)
        if isinstance(arg, dict):
            if len(args) == 1:
                return {k: apply_hint(args[0], v) for k, v in arg.items()}
            elif len(args) == 2:
                return {
                    apply_hint(args[0], k): apply_hint(args[1], v)
                    for k, v in arg.items()
                }
            raise ValueError(
                f"Invalid number of subhints specified for arg of type dict: {len(args)} "
                f"not in (1, 2), no hint application method found"
            )
        elif hasattr(t, "__iter__"):
            if len(args) == 1:
                return t(apply_hint(args[0], v) for v in arg)
            elif len(args) == len(arg):
                return t(map(apply_hint, args, arg))
        raise ValueError(
            f"Invalid number of subhints specified for iterable type {t}: {len(args)} "
            f"not in (1, {len(arg)}), no hint application method found"
        )
    elif isinstance(hint, (UnionType, _UnionType)):
        args = hint.__args__
        for opt in args:
            with suppress(TypeError, ValueError):
                return apply_hint(opt, arg)
        raise ValueError(f"Things didn't work out, all of {args} errored on {arg}")
    else:
        return hint(arg) if callable(hint) else hint


def exec_hints(func: Callable[P, T]) -> Callable[P, T]:
    @wraps(func)
    def inner(*args, **kwargs):
        ann = get_type_hints(func)
        spec = getfullargspec(func)

        if isclass(func):
            if spec.args[0] == "self":
                spec.args.pop(0)
            else:
                raise TypeError(
                    f"First argument to a class signature must be self, failed on {spec.args}"
                )

        args, vargs = args[: len(spec.args)], args[len(spec.args) :]

        def maybe_apply(name, val):
            return apply_hint(ann[name], val) if name in ann else val

        args = [*map(maybe_apply, spec.args, args)]

        if spec.varargs:
            args.extend(maybe_apply(spec.varargs, vargs))

        kwargs = {n: maybe_apply(n, v) for n, v in list(kwargs.items())}

        if spec.kwonlyargs:
            kwonlyvals = [kwargs.pop(k, spec.kwonlydefaults[k]) for k in spec.kwonlyargs]  # type: ignore

        if spec.varkw:
            kwargs = maybe_apply(spec.varkw, kwargs)

        if spec.kwonlyargs:
            for k, v in zip(spec.kwonlyargs, kwonlyvals):  # type: ignore
                kwargs[k] = maybe_apply(k, v)

        return maybe_apply("return", func(*args, **kwargs))  # type: ignore

    return inner  # type: ignore


class _UnionType:
    def __init__(self, *args):
        self.__args__ = list(args)

    def __or__(self, other):
        if isinstance(other, (UnionType, _UnionType)):
            return _UnionType(*self.__args__, *other.__args__)
        return _UnionType(*self.__args__, other)

    def __ror__(self, other):
        if isinstance(other, (UnionType, _UnionType)):
            return _UnionType(*other.__args__, *self.__args__)
        return _UnionType(other, *self.__args__)


class Literal:
    def __init__(self, v):
        self.v = v

    @classmethod
    def __class_getitem__(cls, x):
        return cls(x)

    def __or__(self, other):
        if isinstance(other, (UnionType, _UnionType)):
            return _UnionType(self.v, *other.__args__)
        return _UnionType(self.v, other)

    def __ror__(self, other):
        if isinstance(other, (UnionType, _UnionType)):
            return _UnionType(*other.__args__, self.v)
        return _UnionType(other, self.v)

    def __call__(self, arg):
        return self.v(arg) if callable(arg) else self.v


modules[__name__].__class__ = type(
    "M", (ModuleType,), {"__call__": lambda self, func: exec_hints(func)}
)
