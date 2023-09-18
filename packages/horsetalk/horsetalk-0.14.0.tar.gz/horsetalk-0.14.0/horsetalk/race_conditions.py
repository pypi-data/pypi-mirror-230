from pendulum import DateTime
from .going import Going
from .race_distance import RaceDistance
from .stalls_position import StallsPosition
from .racecourse import Racecourse


class RaceConditions:
    """
    A class for grouping together race conditions into a single object.

    """

    def __init__(
        self,
        *,
        datetime: DateTime,
        racecourse: Racecourse,
        distance: RaceDistance,
        going: Going,
        stalls_position: StallsPosition | None = None,
    ):
        """
        Initialize a RaceConditions instance.

        Args:
            datetime: The datetime of the race
            racecourse: The racecourse on which the race is run
            distance: The race distance
            going: The going of the race
            stalls_position: The position of the stalls on the track

        """
        self.datetime = datetime
        self.racecourse = racecourse
        self.distance = distance
        self.going = going
        self.stalls_position = stalls_position

    def __repr__(self):
        return (
            f"<RaceConditions: datetime={self.datetime}, "
            f"racecourse={self.racecourse!r}, "
            f"distance={self.distance}, "
            f"going={self.going}, "
            f"stalls_position={self.stalls_position}>"
        )

    def __str__(self):
        return (
            f"{self.datetime.format('D MMM YYYY, HH:mm')}, "
            f"{self.racecourse.name}, "
            f"{self.distance.furlong}f ({self.going})"
            f"{', Stalls: ' + str(self.stalls_position.name.title()) if self.stalls_position else ''}"
        )
