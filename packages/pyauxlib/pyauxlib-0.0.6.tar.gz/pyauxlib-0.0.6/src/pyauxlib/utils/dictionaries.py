def remove_keys(dictionary: dict, remove: list) -> dict:
    """Removes the keys from a dictionary specified in the list `remove`.

    If an element from `remove` is not a key in `dict`, then it will ignore (won't raise
    any error)

    Parameters
    ----------
    dictionary : dict
        Original dictionary
    remove : list
        List with the keys to be removed from `dictionary`

    Returns
    -------
    dict
        Dictionary with the specified keys removed.
    """

    new_dict = dictionary.copy()
    for k in remove:
        new_dict.pop(k, None)

    return new_dict


def is_empty_or_none(dictionary: dict) -> bool:
    """Returns if a dictionary is empty, or if all the values are `None`.

    .. note::
        A value of '0' is not considered empty.

    Examples
    --------
    >>>nested_dict = {'a': {'b': None, 'c': {}}}
    >>>print(is_empty_or_none(nested_dict))  # Output: True

    >>>nested_dict = {'a': {'b': None, 'c': {'d': None}}}
    >>>print(is_empty_or_none(nested_dict))  # Output: True

    >>>nested_dict = {'a': {'b': 0, 'c': {'d': None}}}
    >>>print(is_empty_or_none(nested_dict))  # Output: False
    """
    if not dictionary:
        return True

    for v in dictionary.values():
        if isinstance(v, dict):
            if not is_empty_or_none(v):
                return False
        elif v is not None:
            return False

    return True
