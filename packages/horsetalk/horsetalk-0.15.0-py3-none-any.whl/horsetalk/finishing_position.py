from peak_utility.number import Ordinal  # type: ignore


class FinishingPosition(Ordinal):
    """
    A class that represents the finishing position of a horse in a race.

    """

    def __new__(cls, value):
        if int(value) < 0:
            raise ValueError("Finishing position cannot be negative.")
        return super().__new__(cls, value)

    def __bool__(self):
        return int(self) >= 0

    def __repr__(self):
        if int(self) == 0:
            return "<FinishingPosition: Unplaced>"
        return f"<FinishingPosition: {super().__repr__()}>"

    def __str__(self):
        if int(self) == 0:
            return "Unplaced"
        return super().__repr__()

    def __add__(self, other: int) -> int:
        raise TypeError("FinishingPosition cannot be added to.")

    def __sub__(self, other: int) -> int:
        raise TypeError("FinishingPosition cannot be subtracted from.")

    def __mul__(self, other: int) -> int:
        raise TypeError("FinishingPosition cannot be multiplied.")

    def __truediv__(self, other: int) -> int:
        raise TypeError("FinishingPosition cannot be divided.")

    def __eq__(self, other: object) -> bool:
        if isinstance(other, FinishingPosition):
            return int(self) == int(other)
        return False

    def __lt__(self, other: int) -> bool:
        return int(self) > int(other)

    def __le__(self, other: int) -> bool:
        return int(self) >= int(other)

    def __gt__(self, other: int) -> bool:
        return int(self) < int(other)

    def __ge__(self, other: int) -> bool:
        return int(self) <= int(other)
