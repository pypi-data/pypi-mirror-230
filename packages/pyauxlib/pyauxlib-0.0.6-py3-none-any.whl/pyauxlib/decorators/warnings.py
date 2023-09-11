import inspect
import warnings
from collections.abc import Callable
from typing import Any

import wrapt

_routine_stacklevel = 2

__all__ = ["deprecated", "deprecated_argument", "experimental"]


def _get_msg(decorator_name: str, wrapped: Callable[..., Any], reason: str | None = None, version: str | None = None) -> str:
    """To add messages to the decorators"""
    if inspect.isclass(wrapped):
        fmt = f"Call to {decorator_name} class {{name}}."
    else:
        fmt = f"Call to {decorator_name} function {{name}}."
    if reason:
        fmt += " ({reason})"
    if version:
        fmt += f" -- {decorator_name.capitalize()} since version {{version}}."
    return fmt.format(name=wrapped.__name__, reason=reason or "", version=version or "")


def _warning_decorator(decorator_name: str) -> Callable[..., Any]:
    """
    This is a decorator factory that creates decorators to emit warnings.
    It is used to create actual decorators such as 'experimental' and 'deprecated'.
    The 'decorator_name' parameter specifies the name of the decorator being created.
    """

    # REFERENCE: adapted from 'deprecated' of deprecated library
    # REFERENCE: see also how they handle the deprecated decorator in sklearn

    def actual_decorator(*args, **kwargs):
        category = kwargs.get("category", Warning)
        if len(args) == 1 and callable(args[0]):

            @wrapt.decorator
            def wrapper_without_args(wrapped, instance, args_, kwargs_) -> Any:
                msg = _get_msg(decorator_name, wrapped, None, None)
                warnings.warn(msg, category=category, stacklevel=_routine_stacklevel)
                return wrapped(*args_, **kwargs_)

            return wrapper_without_args(args[0])

        else:

            @wrapt.decorator
            def wrapper_with_args(wrapped, instance, args_, kwargs_) -> Any:
                msg = _get_msg(decorator_name, wrapped, kwargs.get("reason"), kwargs.get("version"))
                if action := kwargs.get("action"):
                    with warnings.catch_warnings():
                        warnings.simplefilter(action)
                        warnings.warn(msg, category=category, stacklevel=_routine_stacklevel)
                else:
                    warnings.warn(msg, category=category, stacklevel=_routine_stacklevel)
                return wrapped(*args_, **kwargs_)

            return wrapper_with_args

    return actual_decorator


def experimental(*args, **kwargs) -> Callable[..., Any]:
    """
    Decorator to mark functions or classes as experimental.

    Parameters
    ----------
    reason : str, optional
        The reason why the function or class is marked as experimental.
    version : str, optional
        The version since when the function or class is marked as experimental.
    category : Type[Warning], optional
        The category of the warning to be issued. By default, `FutureWarning`.
    action : {None, "error", "ignore", "always", "default", "module", "once"}
        The action to be taken when the warning is issued. If `None`, uses the global
        warning filter.

    Returns
    -------
    Callable[..., Any]
        The decorated function or class.

    Examples
    --------
    ```python
    @experimental
    def function(a, b):
        return [a, b]

    @experimental(reason="use another function", version="1.2.0", category=FutureWarning, action="error")
    def function(a, b):
        return [a, b]
    ```
    """
    kwargs["category"] = kwargs.get("category", FutureWarning)
    return _warning_decorator("experimental")(*args, **kwargs)


def deprecated(*args, **kwargs):
    """
    Decorator to mark functions or classes as deprecated.

    Parameters
    ----------
    reason : str, optional
        The reason why the function or class is marked as deprecated.
    version : str, optional
        The version since when the function or class is marked as deprecated.
    category : Type[Warning], optional
        The category of the warning to be issued. By default, `DeprecationWarning`.
    action : {None, "error", "ignore", "always", "default", "module", "once"}
        The action to be taken when the warning is issued. If `None`, uses the global
        warning filter.

    Returns
    -------
    Callable[..., Any]
        The decorated function or class.

    Examples
    --------
    ```python
    @deprecated
    def function(a, b):
        return [a, b]

    @deprecated(reason="use another function", version="1.2.0", category=DeprecationWarning, action="error")
    def function(a, b):
        return [a, b]
    ```
    """
    kwargs["category"] = kwargs.get("category", DeprecationWarning)
    return _warning_decorator("deprecated")(*args, **kwargs)


def deprecated_argument(
    argument: str = "",
    version: str = "",
    additional_msg: str = "",
    category=DeprecationWarning,
) -> Callable[..., Any]:
    """
    Decorator that warns of a deprecated argument.
    It should be used on the function or method where the deprecated argument is being used.

    Parameters
    ----------
    argument : str, optional
        The name of the deprecated argument.
    version : str, optional
        The version in which the argument will be removed.
    additional_msg : str, optional
        Additional message to be included in the warning, e.g., "Use 'other_arg' instead".
    category : Warning, optional
        The category of the warning. Default is DeprecationWarning.

    Returns
    -------
    Callable[..., Any]
        The decorated function or class.

    Examples
    --------
    One deprecated argument:
    ```python
    @deprecated_argument(arguments=["my_arg1"], version="2.0", additional_msg="Use 'other_arg' instead")
    def my_func(my_arg1=None, my_arg2=None, other_arg=None):
        pass
    ```

    Multiple arguments can be deprecated:
    ```python
    @deprecated_argument(arguments=["my_arg1"], version="2.0", additional_msg="Use 'other_arg' instead")
    @deprecated_argument(arguments=["my_arg2"], version="3.0", additional_msg="Use 'yet_another_arg' instead")
    def my_func(my_arg1=None, my_arg2=None, other_arg=None):
        pass
    ```
    """

    @wrapt.decorator
    def wrapper(wrapped, instance, args, kwargs):
        if argument in kwargs:
            module_name = inspect.getmodule(wrapped).__name__
            if module_name == "__main__":
                module_name = ""
            else:
                module_name += "."
            method = module_name + wrapped.__name__
            if instance is not None:
                method = instance.__class__.__name__ + "." + method
            version_str = f" in version {version}" if version else ""
            additional_msg_str = f" {additional_msg}." if additional_msg else ""
            msg = f"Argument '{argument}' from '{method}' is being deprecated{version_str}.{additional_msg_str}"
            warnings.warn(msg, category=category, stacklevel=_routine_stacklevel)
        return wrapped(*args, **kwargs)

    return wrapper
