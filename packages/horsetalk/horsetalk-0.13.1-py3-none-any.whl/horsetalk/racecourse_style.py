from .parsing_enum import ParsingEnum


class RacecourseStyle(ParsingEnum):
    """
    An enumeration representing the style of a racecourse.

    """

    UNKNOWN = 0
    GALLOPING = 1
    STIFF = 2
    TIGHT = 3
