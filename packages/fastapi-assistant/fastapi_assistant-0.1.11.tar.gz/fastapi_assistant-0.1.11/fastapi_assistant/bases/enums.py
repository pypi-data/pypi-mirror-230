from enum import Enum
from typing import Optional, Any


class BasicEnum(Enum):
    def __new__(cls, key, desc):
        obj = object.__new__(cls)
        obj.key = obj._value_ = key
        obj.desc = desc
        return obj

    @classmethod
    def get_enum(cls, value) -> Optional[Any]:
        try:
            return cls(value)
        except ValueError:
            return None

    @classmethod
    def get_enum_by_desc(cls, desc) -> Optional[Any]:
        for item in cls:
            if item.desc == desc:
                return item
        return None

    @classmethod
    def choices(cls):
        return [(item.key, item.desc) for item in cls]

    @classmethod
    def items(cls) -> list:
        return [item.key for item in cls]
