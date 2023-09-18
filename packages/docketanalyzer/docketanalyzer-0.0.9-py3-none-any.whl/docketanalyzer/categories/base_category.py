from enum import Enum


class Category(Enum):
    def __new__(cls, value, description=None):
        obj = object.__new__(cls)
        obj._value_ = value
        obj._description_ = description
        return obj

    @property
    def description(self):
        return self._description_
