from .handedness import Handedness
from .racecourse_contour import RacecourseContour
from .racecourse_shape import RacecourseShape
from .racecourse_style import RacecourseStyle
from .surface import Surface


class Racecourse:
    """
    A class for grouping together racecourse characteristics into a single object.

    """

    def __init__(self, name: str, surface: Surface, **kwargs):
        """
        Initialize a Racecourse instance.

        Args:
            name: The name of the racecourse
            surface: The surface on which the racecourse is run
            handedness: The handedness of the racecourse
            contour: The contour of the racecourse
            shape: The shape of the racecourse
            style: The style of the racecourse

        """
        self.name = name
        self.surface = surface
        self.handedness = Handedness[kwargs.get("handedness", "unknown")]
        self.contour = RacecourseContour[kwargs.get("contour", "unknown")]
        self.shape = RacecourseShape[kwargs.get("shape", "unknown")]
        self.style = RacecourseStyle[kwargs.get("style", "unknown")]
