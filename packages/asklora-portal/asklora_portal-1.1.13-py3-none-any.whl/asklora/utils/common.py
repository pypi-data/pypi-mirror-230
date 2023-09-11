from typing import Any


def deep_get(_dict: dict, keys: list[str], default: Any = None):
    """Get a value from a nested dictionary quickly.
    One downside is that we cannot tell the type of the value.

    Sourced from https://stackoverflow.com/a/43621819

    Example usage:
        data = {
            'name': 'foo',
            'address': {
                'street': 'foo',
                'city': 'bar',
                'country': 'baz',
            }
        }

        country = data['address']['country']  # common method

        country = data.get('address', {}).get('country', '')  # better method

        country = deep_get(data, ['address', 'country'])  # this utility function

    Args:
        _dict (dict): Dictionary we want to get the value from
        keys (List[str]): List of keys to the value we want
        default (Any, optional): Default value if the value isn't found. Defaults to None.

    Returns:
        Any: Value to be returned
    """

    for key in keys:
        if isinstance(_dict, dict):
            _dict = _dict.get(key, default)
        elif isinstance(_dict, list) and isinstance(key, int):
            _dict = _dict[key]
        else:
            return default
    return _dict
