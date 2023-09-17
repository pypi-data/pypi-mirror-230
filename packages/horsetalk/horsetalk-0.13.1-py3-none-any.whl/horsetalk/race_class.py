from typing import Self


class RaceClass:
    def __init__(self, value: str | int):
        if not 1 <= int(value) <= 7:
            raise ValueError(f"Class must be between 1 and 7, not {value}")

        self.value = int(value)

    def __repr__(self) -> str:
        return f"<RaceClass: {self.value}>"

    def __str__(self) -> str:
        return f"Class {self.value}"

    def __eq__(self, other: Self) -> bool:
        return self.value == other.value

    def __gt__(self, other: Self) -> bool:
        return self.value < other.value

    def __lt__(self, other: Self) -> bool:
        return self.value > other.value
