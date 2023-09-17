from collections.abc import Iterable


def is_iterable(obj):
    return isinstance(obj, Iterable)

def is_list(obj):
    return isinstance(obj, list)

def is_dict(obj):
    return isinstance(obj, dict)
