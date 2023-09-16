# point.py

import math
from typing import Any, Union, Tuple, Iterable

import numpy as np

from polygeom.entity import Entity

__all__ = [
    "Point"
]

class Point(Entity):
    """A class to represent a point in space"""

    __slots__ = ()

    try:
        from typing import Self

    except ImportError:
        Self = Any
    # end try

    def __init__(self, values: Union[np.ndarray, Tuple[float, ...]]) -> None:
        """
        Defines the attributes of the point.

        :param values: The array of values of the object.
        """

        if len(values) == 0:
            raise ValueError("Point must get at least 1 value.")
        # end if

        super().__init__(values)
    # end __init__

    def __repr__(self) -> str:
        """
        Represents the object as a string.

        :return: The string data.
        """

        return f"{type(self).__name__}{tuple(self.values)}"
    # end __repr__

    def __hash__(self) -> int:
        """
        Returns the hash of the object.

        :return: The hash number.
        """

        return hash(tuple(self.values))
    # end __hash__

    def __iter__(self) -> Iterable:
        """
        Returns an iterable for the object.

        :return: The iterable object.
        """

        return iter(self.values)
    # end __iter__

    def move(self, distance: float, angle: float) -> Self:
        """
        Moves the point in space.

        :param distance: The distance to move.
        :param angle: The angle of the movement.

        :return: The new point object.
        """

        if len(self.values) < 2:
            return self + distance

        else:
            return Point(
                (
                    float(self.values[0] + distance * math.cos(angle)),
                    float(self.values[0] + distance * math.cos(angle)),
                    *self.values[2:]
                )
            )
        # end if
    # end move
# end Point