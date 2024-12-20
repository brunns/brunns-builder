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
    return random.randint(a or 0, b or sys.maxsize)  # nosec


def a_boolean():
    return one_of(True, False)  # noqa: FBT003


def one_of(*args):
    return random.choice(args)  # nosec


class BuilderMeta(type):
    def __new__(cls, name, bases, namespace):  # noqa: C901
        target = namespace.pop("target", None)
        args = namespace.pop("args", [])

        def __init__(self, **kwargs):
            # Defaults from factories (plus method overrides.
            for key, value in namespace.items():
                if key in {"build"} or getattr(value, "is_method", False):  # It's an overridable base method.
                    m = MethodType(value, self)
                    setattr(self, key, m)
                elif isclass(value) and issubclass(value, Builder):  # It's a nested builder.
                    setattr(self, key, value().build())
                elif not key.startswith("__"):  # It's a field value or factory.
                    if callable(value):
                        setattr(self, key, value())
                    else:
                        setattr(self, key, value)

            # Values from keyword arguments.
            for key, value in kwargs.items():
                setattr(self, key, value)

            self.args = args() if callable(args) else [arg() if callable(arg) else arg for arg in args]

        def __getattr__(self, item):
            """Dynamic 'with_x' and 'and_x' methods."""
            attr_name = item.partition("with_")[2] or item.partition("and_")[2]
            if attr_name:

                def with_(value):
                    setattr(self, attr_name, value)
                    return self

                return with_
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
            msg = "Needs a target (i.e. a callable instance factory)."
            raise ValueError(msg)

        result = type.__new__(cls, name, bases, {})

        setattr(result, __init__.__name__, __init__)
        setattr(result, __getattr__.__name__, __getattr__)
        setattr(result, __getitem__.__name__, __getitem__)
        setattr(result, __repr__.__name__, __repr__)
        setattr(result, __str__.__name__, __str__)
        setattr(result, build.__name__, build)

        return result


class Builder(metaclass=BuilderMeta):
    """TODO"""


def method(func):
    """Decorate Builder method, so that the Builder doesn't think it's an attribute factory."""
    func.is_method = True
    return func
