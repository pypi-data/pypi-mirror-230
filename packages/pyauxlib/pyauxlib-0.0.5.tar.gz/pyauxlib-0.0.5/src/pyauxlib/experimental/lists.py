from typing import Any

from pyauxlib.experimental.decorator import experimental


@experimental
def list_elements_to_numeric(lst: list) -> list:
    """Converts to numeric values all the possible elements of a list.
    First try to convert to int, and then to float. Elements that cannot be converted
    are left untouched.

    Parameters
    ----------
    lst : list
        original list

    Returns
    -------
    list
        list with all possible elements converted to numeric
    """
    new_list = []
    for ele in lst:
        new_list.append(is_number(ele))

    return new_list


@experimental
def is_number(ele: Any) -> int | float | Any:
    """Returns an object converted to int. If it cannot be converted to int, it will
    try to convert to float.

    Parameters
    ----------
    ele : _type_
        object

    Returns
    -------
    int(ele) | is_float(ele)
    """
    try:
        return int(ele)
    except ValueError:
        return is_float(ele)


@experimental
def is_float(ele: Any) -> float | Any:
    """Returns an object converted to float, or the original object if it cannot be
    converted

    Parameters
    ----------
    ele : _type_
        original object

    Returns
    -------
    float(ele) | ele
    """
    try:
        return float(ele)
    except ValueError:
        return ele
