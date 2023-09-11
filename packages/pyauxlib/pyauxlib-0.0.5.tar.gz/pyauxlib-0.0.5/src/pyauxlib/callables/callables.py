import inspect
import sys
from collections.abc import Callable


def call_with_arguments(*args: dict, callable_object: Callable) -> Callable:
    """Check if the required arguments of a callable object are included in the
    passed arguments, and returns the callable_object(arguments)

    Parameters
    ----------
    *args : dict
        variable number of dictionaries with arguments to be passed to the callable.
        In case of duplicate entries, the last values from last dictionaries overwrite
        those of the first ones.
    callable_object : Callable
        callable object (function, class)

    Returns
    -------
    Callable
        the callable object with the passed arguments

    Raises
    ------
    TypeError
        required argument for the callable object is absent in arguments
    """

    if callable(callable_object):
        # Check the parameters of callable_object
        params = inspect.signature(callable_object).parameters
    else:
        # TODO: handle the fact that the object passed is not callable...
        sys.exit(1)

    argskwargs = _get_argskwargs(callable_object)

    # Merge all the dictionaries in *args into a single one
    # Values from last dictionaries in *args will overwrite existing keys in the previous
    arguments = {key: val for d in args for key, val in d.items()}

    # TODO: do anything with the arguments passed but not in the function???
    # Just pass them as **kwargs or raise a warning??"""
    # If pass them as *args/**kwargs, then need to see if the callable accept them,
    # in the 'params_spec' of get _get_argskwargs (varargs, varkw, as seen in
    # https://docs.python.org/3/library/inspect.html#inspect.getfullargspec
    {k: v for (k, v) in arguments.items() if k not in params.keys()}

    kwargs = {}

    for arg_name, v in params.items():
        # Required argument (doesn't have a default value in callable_object)
        # *args and **kwargs are not required
        required_argument = (v.default == inspect.Parameter.empty) if arg_name not in argskwargs else False

        arg_value = arguments.get(arg_name)

        if required_argument:
            if arg_name in arguments.keys():
                kwargs[arg_name] = arguments[arg_name]
            else:
                raise TypeError(f"Argument '{arg_name}' is missing")
        elif arg_name in arguments.keys():
            # ??? Returns the default value if 'None' in arguments. Ok?
            kwargs[arg_name] = arg_value if arg_value is not None else v.default

    return callable_object(**kwargs)  # FIXME Some Callables don't accept kwargs (e.g. math.floor)


def _get_argskwargs(callable: Callable) -> list[str | None]:
    """Returns a list with the args and kwargs of a callable

    Parameters
    ----------
    callable : Callable
        object to check for args and kwargs

    Returns
    -------
    list[str]
        list of args and kwargs
    """

    params_spec = inspect.getfullargspec(callable)

    return [params_spec.varargs, params_spec.varkw]
