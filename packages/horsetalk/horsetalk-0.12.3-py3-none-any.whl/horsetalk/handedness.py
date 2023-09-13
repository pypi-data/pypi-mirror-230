from .parsing_enum import ParsingEnum


class Handedness(ParsingEnum):
    """
    An enumeration representing the handedness of a racecourse.

    """

    UNKNOWN = 0
    LEFT = 1
    RIGHT = 2
    BOTH = 3

    # Alternatives
    NEITHER = UNKNOWN
    L = LEFT
    R = RIGHT
    LR = BOTH
    LH = LEFT
    RH = RIGHT
