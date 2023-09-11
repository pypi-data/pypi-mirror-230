import functools
import inspect
import warnings
from collections.abc import Callable
from typing import Any

import wrapt
from deprecated.classic import ClassicAdapter

_routine_stacklevel = 2
string_types = (bytes, str)


# TODO: see also how they handle the deprecated decorator in sklearn:
# sklearn.utils.deprecation
def experimental(*args: Any, **kwargs: Any) -> functools.partial[Callable[..., Any]]:
    # REFERENCE: "adapted" from deprecated method of deprecated library
    # TODO: probably a simpler decorator can be used, w/o ClassicAdapted, ...
    """
    This is a decorator which can be used to mark functions
    as experimental. It will result in a warning being emitted
    when the function is used.

    **Classic usage:**

    To use this, decorate your experimental function with **@experimental** decorator:

    .. code-block:: python

       @experimental
       def some_old_function(x, y):
           return x + y

    You can also decorate a class or a method:

    .. code-block:: python

       class SomeClass(object):
           @experimental
           def some_old_method(self, x, y):
               return x + y


       @experimental
       class SomeOldClass(object):
           pass

    You can give a *reason* message to help the developer understand,
    and a *version* number.

    .. code-block:: python

       @experimental(reason="use another function", version='1.2.0')
       def some_old_function(x, y):
           return x + y

    The *category* keyword argument allow you to specify the experimental warning class of your choice.
    By default, :exc:`FutureWarning` is used but you can choose :exc:`PendingDeprecationWarning`
    or a custom subclass.

    .. code-block:: python

       @experimental(category=PendingDeprecationWarning)
       def some_old_function(x, y):
           return x + y

    The *action* keyword argument allow you to locally change the warning filtering.
    *action* can be one of "error", "ignore", "always", "default", "module", or "once".
    If ``None``, empty or missing, the the global filtering mechanism is used.
    See: `The Warnings Filter`_ in the Python documentation.

    .. code-block:: python

       @experimental(action="error")
       def some_old_function(x, y):
           return x + y

    """
    if args and isinstance(args[0], string_types):
        kwargs["reason"] = args[0]
        args = args[1:]

    if args and not callable(args[0]):
        raise TypeError(repr(type(args[0])))

    if args:
        action = kwargs.get("action")
        category = kwargs.get("category", FutureWarning)
        adapter_cls = kwargs.pop("adapter_cls", ClassicAdapter)
        adapter = adapter_cls(**kwargs)

        wrapped = args[0]
        if inspect.isclass(wrapped):
            wrapped = adapter(wrapped)
            return wrapped

        elif inspect.isroutine(wrapped):

            @wrapt.decorator(adapter=adapter)
            def wrapper_function(wrapped_, instance_, args_, kwargs_):
                msg = get_experimental_msg(wrapped_, instance_, adapter.reason, adapter.version)
                if action:
                    with warnings.catch_warnings():
                        warnings.simplefilter(action, category)
                        warnings.warn(msg, category=category, stacklevel=_routine_stacklevel)
                else:
                    warnings.warn(msg, category=category, stacklevel=_routine_stacklevel)
                return wrapped_(*args_, **kwargs_)

            return wrapper_function(wrapped)

        else:
            raise TypeError(repr(type(wrapped)))

    return functools.partial(experimental, **kwargs)


def get_experimental_msg(wrapped, instance, reason, version):
    """
    Get the experimental warning message for the user.

    :param wrapped: Wrapped class or function.

    :param instance: The object to which the wrapped function was bound when it was called.

    :return: The warning message.
    """
    if instance is None:
        if inspect.isclass(wrapped):
            fmt = "Call to experimental class {name}."
        else:
            fmt = "Call to experimental function (or staticmethod) {name}."
    else:
        if inspect.isclass(instance):
            fmt = "Call to experimental class method {name}."
        else:
            fmt = "Call to experimental method {name}."
    if reason:
        fmt += " ({reason})"
    if version:
        fmt += " -- Experimental since version {version}."
    return fmt.format(name=wrapped.__name__, reason=reason or "", version=version or "")
