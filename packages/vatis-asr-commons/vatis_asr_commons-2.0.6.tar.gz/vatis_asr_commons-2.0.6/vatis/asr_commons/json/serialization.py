import abc

from typing import get_type_hints
from vatis.asr_commons.utils import reflection


class JSONSerializable(abc.ABC):
    @abc.abstractmethod
    def to_json(self) -> dict:
        pass


class ExcludeNullsJSONSerializer(JSONSerializable):
    def to_json(self) -> dict:
        obj_dict = {}
        type_hints = get_type_hints(self.__class__)

        for field, value in self.__dict__.items():
            if value is None:
                field_type = type_hints[field]

                if not reflection.is_optional(field_type):
                    obj_dict[field] = None
            elif isinstance(value, JSONSerializable):
                obj_dict[field] = value.to_json()
            elif isinstance(value, list):
                new_value = []

                for elem in value:
                    if isinstance(elem, JSONSerializable):
                        new_value.append(elem.to_json())
                    else:
                        new_value.append(elem)

                obj_dict[field] = new_value
            else:
                obj_dict[field] = value

        return obj_dict
