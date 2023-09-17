class Draw:
    def __init__(self, value: int | str) -> None:
        """
        Initialize a Draw instance.

        Args:
            value: The stall number in which the horse is drawn.
        """
        if not str(int(value)) == str(value):
            raise ValueError("Draw must be an integer value")

        self.value = int(value)

    def __gt__(self, other: "Draw") -> bool:
        """
        Returns True if the draw is higher than the other draw.

        Args:
            other: The other draw to compare against.
        """
        return self.value > other.value

    def __lt__(self, other: "Draw") -> bool:
        """
        Returns True if the draw is lower than the other draw.

        Args:
            other: The other draw to compare against.
        """
        return self.value < other.value
