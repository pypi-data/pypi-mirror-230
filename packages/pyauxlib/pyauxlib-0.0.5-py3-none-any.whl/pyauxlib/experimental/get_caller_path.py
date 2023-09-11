from inspect import currentframe, getframeinfo
from pathlib import Path
from types import FrameType


def get_caller_path() -> Path | None:
    # FIXME: Does this work as intended? Is it useful?
    """Gets the path of the caller script.
    The 'caller' here is the caller of the script that called this one.

    Returns
    -------
    Path | None
        Path of the caller script (None if there is no caller)
    """
    # Gets the path of the calling script (must be the "main")

    # NOTE: 'f:back' twice
    # The 1st is for the script calling this one, the 2nd is for the script calling the
    # script that called this... which might be a NoneType

    caller_1 = currentframe().f_back
    caller_2 = caller_1.f_back

    if not isinstance(caller_1, FrameType):
        # No caller
        # TODO: raise some exception, warning???
        return None

    caller = caller_2 if isinstance(caller_2, FrameType) else caller_1

    return Path(getframeinfo(caller).filename)
