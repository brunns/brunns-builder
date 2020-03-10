# encoding=utf-8
import logging
import random
import string
import sys
from inspect import isclass
from types import MethodType

logger = logging.getLogger(__name__)


def a_string(length=10, characters=string.ascii_letters + string.digits):
    return "".join(random.choice(characters) for _ in range(length))  # nosec


def an_integer(a=None, b=None):
    return random.randint(a if a else 0, b if b else sys.maxsize)  # nosec


def a_boolean():
    return one_of(True, False)


def one_of(*args):
    return random.choice(args)  # nosec


class BuilderMeta(type):
    def __new__(metacls, name, bases, namespace, **kwds):  # noqa: C901
        target = namespace.pop("target", None)
        args = namespace.pop("args", [])

        def __init__(self, **kwargs):
            # Defaults from factories (plus method overrides.
            for name, value in namespace.items():
                if name in {"build"} or getattr(
                    value, "is_method", False
                ):  # It's an overridable base method.
                    m = MethodType(value, self)
                    setattr(self, name, m)
                elif isclass(value) and issubclass(value, Builder):  # It's a nested builder.
                    setattr(self, name, value().build())
                elif not name.startswith("__"):  # It's a field value or factory.
                    if callable(value):
                        setattr(self, name, value())
                    else:
                        setattr(self, name, value)

            # Values from keyword arguments.
            for name, value in kwargs.items():
                setattr(self, name, value)

            self.args = (
                args() if callable(args) else [arg() if callable(arg) else arg for arg in args]
            )

        def __getattr__(self, item):
            """Dynamic 'with_x' and 'and_x' methods."""
            attr_name = item.partition("with_")[2] or item.partition("and_")[2]
            if attr_name:

                def with_(value):
                    setattr(self, attr_name, value)
                    return self

                return with_
            else:
                return getattr(self.build(), item)

        def __getitem__(self, item):
            return self.build()[item]

        def __repr__(self):
            return repr(self.build())

        def __str__(self):
            return str(self.build())

        def build(self):
            state = vars(self)
            args = state.pop("args", [])
            if callable(target):
                return target(*args, **state)
            else:
                raise ValueError("Needs a target (i.e. a callable instance factory).")

        result = type.__new__(metacls, name, bases, {})

        setattr(result, __init__.__name__, __init__)
        setattr(result, __getattr__.__name__, __getattr__)
        setattr(result, __getitem__.__name__, __getitem__)
        setattr(result, __repr__.__name__, __repr__)
        setattr(result, __str__.__name__, __str__)
        setattr(result, build.__name__, build)

        return result


class Builder(metaclass=BuilderMeta):
    """TODO"""

    pass


def method(func):
    """Decorate Builder method, so that the Builder doesn't think it's an attribute factory."""
    func.is_method = True
    return func
