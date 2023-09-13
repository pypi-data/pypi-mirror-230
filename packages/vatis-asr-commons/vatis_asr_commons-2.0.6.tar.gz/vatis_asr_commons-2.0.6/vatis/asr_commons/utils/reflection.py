import typing

from typing import Union


def is_optional(field) -> bool:
    """
    Checks if a given field in class was declared as optional
    :param field: class field type
    :return: True if is optional, False otherwise
    """
    return typing.get_origin(field) is Union and \
           type(None) in typing.get_args(field)
