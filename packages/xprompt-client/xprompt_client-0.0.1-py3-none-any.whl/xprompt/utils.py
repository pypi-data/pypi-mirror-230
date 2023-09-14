from typing import Any


def exclude_json_none(json_dict: dict[str, Any]) -> dict[str, Any]:
    """
    Delete keys with the value ``None`` in a dictionary, recursively.

    This alters the input so you may wish to ``copy`` the dict first.
    """
    # For Python 3, write `list(d.items())`; `d.items()` won’t work
    # For Python 2, write `d.items()`; `d.iteritems()` won’t work
    for key, value in list(json_dict.items()):
        if value is None:
            del json_dict[key]
        elif isinstance(value, dict):
            exclude_json_none(value)
    return json_dict
