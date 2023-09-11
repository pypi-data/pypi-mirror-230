import warnings


def warn_deprecated_argument(
    method: str = "",
    argument: str = "",
    version: str = "",
    additional_msg: str = "",
    category=DeprecationWarning,
    stacklevel=2,
):
    # Warns of a deprecated argument.
    # To be called from within the method, when the deprecated argument is being used
    # method : method name
    # argument: argument to be deprecated
    # version: in which will be removed
    # additional_msg: e.g. "Use 'other_arg' instead"
    # TODO: PROBABLY it can be improved quite a lot...
    # TODO: Is it possible to convert it to a decorator?

    if not any([method, argument, version]):
        msg = "Used argument from method"
    if method:
        method = f"from method '{method}' "
    if argument:
        argument = f"'{argument}' "
    if version:
        version = f" in version {version}"
    if additional_msg:
        additional_msg = f". {additional_msg}."
    msg = f"Argument {argument}{method}is being deprecated{version}{additional_msg}"
    warnings.warn(msg, category=category, stacklevel=stacklevel)
