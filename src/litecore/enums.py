import enum


class NoValueEnum(enum.Enum):
    def __repr__(self):
        return f'<{type(self).__name__}.{self.name}>'


class AutoNumberedEnum(enum.Enum):
    def __new__(cls):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj


class OrderedEnum(enum.Enum):
    def __ge__(self, other):
        if type(self) is not type(other):
            return NotImplemented
        return self.value >= other.value

    def __gt__(self, other):
        if type(self) is not type(other):
            return NotImplemented
        return self.value > other.value

    def __le__(self, other):
        if type(self) is not type(other):
            return NotImplemented
        return self.value <= other.value

    def __lt__(self, other):
        if type(self) is not type(other):
            return NotImplemented
        return self.value < other.value


class DuplicateFreeEnum(enum.Enum):
    def __init__(self, *args):
        cls = type(self)
        if any(self.value == element.value for element in cls):
            msg = (
                f'{self.name} is a disallowed alias '
                f'for {cls(self.value).name}'
            )
            raise ValueError(msg)
