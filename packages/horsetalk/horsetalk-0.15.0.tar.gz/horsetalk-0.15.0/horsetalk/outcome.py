from typing import Self
from .disaster import Disaster
from .finishing_position import FinishingPosition


class Outcome:
    def __init__(self, value: int | str | Disaster | FinishingPosition):
        if not isinstance(value, (Disaster, FinishingPosition)):
            if str(value).isdigit():
                value = FinishingPosition(value)
            else:
                try:
                    value = Disaster[str(value)]
                except KeyError:
                    raise ValueError(f"Invalid outcome: {value}")

        self._value = value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Outcome):
            return False

        if isinstance(self._value, Disaster):
            return isinstance(other._value, Disaster)

        if isinstance(self._value, FinishingPosition):
            return not isinstance(other._value, Disaster) and self._value == other

    def __lt__(self, other: Self) -> bool:
        if isinstance(self._value, Disaster):
            return not isinstance(other._value, Disaster)

        return not isinstance(other._value, Disaster) and self._value < other

    def __le__(self, other: Self) -> bool:
        return self == other or self < other

    def __gt__(self, other: Self) -> bool:
        if isinstance(self._value, Disaster):
            return False

        return isinstance(other._value, Disaster) or self._value > other

    def __ge__(self, other: Self) -> bool:
        return self == other or self > other
