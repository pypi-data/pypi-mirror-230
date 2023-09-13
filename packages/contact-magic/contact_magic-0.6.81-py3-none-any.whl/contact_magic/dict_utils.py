"""
Helpers for working with potentially heavily nested pieces of data
"""


def get_first_level_items(data: dict) -> dict:
    """
    Returns only the top level of data from a dict that is valid.
    :param data:
    :return:
    """
    return {
        key: value for key, value in data.items() if not isinstance(value, (dict, list))
    }


def delete_key_in_object(data, target_key):
    """
    Go through original object and delete
    all occurrences of a target key
    """
    if isinstance(data, list):
        for list_item in data:
            delete_key_in_object(list_item, target_key)
    elif isinstance(data, dict):
        if target_key in data:
            del data[target_key]
        for dict_key, dict_value in data.items():
            delete_key_in_object(dict_value, target_key)
    return data


def replace_values_in_object(data, key, value):
    """
    Go through original object and replace
    all occurrences of a key with new value.
    """
    if isinstance(data, list):
        for list_items in data:
            replace_values_in_object(list_items, key, value)
    elif isinstance(data, dict):
        for dict_key, dict_value in data.items():
            if dict_key == key:
                data[key] = value
            replace_values_in_object(dict_value, key, value)
    return data


def replace_keys_in_object(data, mapping: dict) -> dict:
    """
    Go through the original object and swap any keys to the target mapping.
    """

    result = {}

    for key, value in data.items():
        if isinstance(value, dict):
            result[mapping.get(key, key)] = replace_keys_in_object(value, mapping)
        elif isinstance(value, list):
            result[mapping.get(key, key)] = [
                replace_keys_in_object(item, mapping)
                for item in value
                if isinstance(item, dict)
            ]
        else:
            result[mapping.get(key, key)] = value

    return result


def get_values_in_object_by_key(data, key):
    return list(_get_values_in_object_by_key(data, key))


def _get_values_in_object_by_key(data, key):
    """
    Go through original object and get
    all values based on target key
    """
    if isinstance(data, list):
        for d in data:
            yield from _get_values_in_object_by_key(d, key)
    if isinstance(data, dict):
        for k, v in data.items():
            if key == k:
                yield v
            if isinstance(v, dict):
                yield from _get_values_in_object_by_key(v, key)
            elif isinstance(v, list):
                for d in v:
                    yield from _get_values_in_object_by_key(d, key)
