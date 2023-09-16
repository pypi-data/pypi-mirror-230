from .aw_going_description import AWGoingDescription
from .dirt_going_description import DirtGoingDescription
from .going_description import GoingDescription
from .turf_going_description import TurfGoingDescription


class Going:
    """
    A class to represent a going.
    """

    Scales = (TurfGoingDescription, AWGoingDescription, DirtGoingDescription)

    def __init__(self, description: str, reading: float | None = None):
        """
        Initialize a Going instance.

        Args:
            description: The description of the going.
            reading: The reading of the going stick.
        """
        self.description = description
        self.reading = reading

        assert (self.primary and self.secondary) or self.primary

    @property
    def primary(self) -> GoingDescription:
        """
        The primary property of the going.

        Returns:
            A value selected from the appropriate going scale.
        """
        key = self._description_parts[0]
        return Going._lookup(key)

    @property
    def secondary(self) -> GoingDescription | None:
        """
        The secondary or 'in places' property of the going.

        Returns:
            A value selected from the appropriate going scale.
        """
        key = self._description_parts[1]
        return Going._lookup(key) if key else None

    @property
    def value(self) -> float:
        """
        A numerical value for the going.

        Returns:
            The value of the going.
        """
        return (
            self.primary.value
            if self.secondary is None
            else (self.primary.value + self.secondary.value) / 2
        )

    @property
    def _description_parts(self) -> list[str]:
        """
        The parts of the description.

        Returns:
            The parts of the description.
        """
        texts = self.description.upper().replace(" IN PLACES", "").split(", ")
        return texts if len(texts) == 2 else texts + [""]

    @classmethod
    def _lookup(cls, key: str) -> GoingDescription:
        """
        Lookup a value in the appropriate going scale.

        Args:
            key: The key to lookup.

        Returns:
            A value selected from the appropriate going scale.

        Raises:
            ValueError: If the key is not found in any of the going scales.
        """
        for scale in Going.Scales:
            try:
                return scale[key]
            except KeyError:
                pass

        raise ValueError(f"Unknown going description: {key}")
