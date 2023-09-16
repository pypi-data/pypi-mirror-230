# vector.py

from typing import Optional, Any, Iterable, Tuple, Union

import numpy as np

from polygeom.point import Point
from polygeom.entity import Entity
from polygeom.utils import (
    points_course, points_distances,
    points_angles, points_distance
)

__all__ = [
    "Vector",
    "Line"
]

class Vector(Entity):
    """A class to represent a line between two points."""

    __slots__ = ('_points', '_angles', '_distance', '_length', '_distances')

    try:
        from typing import Self

    except ImportError:
        Self = Any
    # end try

    def __init__(
            self,
            points: Optional[Iterable[Point]] = None,
            values: Optional[np.ndarray] = None
    ) -> None:
        """
        Defines the attributes of the line.

        :param points: The points in space to form a line.
        :param values: The array of values of the object.
        """

        if (values is None) and (points is None):
            raise ValueError(f"No data given to {self.__init__}")
        # end if

        if values is None:
            values = np.array([point.values for point in points])
        # end if

        if points is None:
            points = (Point(data) for data in values)
        # end if

        if (len(tuple(points)) < 2) or (len(values) < 2):
            raise ValueError("Vector must contain at least 2 points.")
        # end if

        super().__init__(values)

        self._points = tuple(points)

        self._distance: Optional[float] = None
        self._length: Optional[float] = None
        self._angles: Optional[Tuple[float, ...]] = None
        self._distances: Optional[Tuple[float, ...]] = None
    # end __init__

    def __repr__(self) -> str:
        """
        Represents the object as a string.

        :return: The string data.
        """

        return f"{type(self).__name__}{tuple(self.points)}"
    # end __repr__

    def __hash__(self) -> int:
        """
        Returns the hash of the object.

        :return: The hash number.
        """

        return hash(tuple(self.points))
    # end __hash__

    def __iter__(self) -> Iterable:
        """
        Returns an iterable for the object.

        :return: The iterable object.
        """

        return iter(self.points)
    # end __iter__

    @property
    def points(self) -> Tuple[Point, ...]:
        """
        Returns the tuple of points of the vector.

        :return: The points of the vector.
        """

        return self._points
    # end points

    def length(self) -> float:
        """
        Returns the points_course of the data of the object.

        :return: The points_course of values.
        """

        return points_course(self.points)
    # end points_course

    def distance(self) -> float:
        """
        Returns the points_distance of the first and last points of the object.

        :return: The points_course of values.
        """

        if self._distance is None:
            self._distance = points_distance(
                start=self.points[0], end=self.points[-1]
            )
        # end if

        return self._distance
    # end points_distance

    def distances(self) -> Tuple[float, ...]:
        """
        Returns the points_distance of the first and last points of the object.

        :return: The points_course of values.
        """

        if self._distances is None:
            self._distances = points_distances(self.points)
        # end if

        return self._distances
    # end points_distance

    def angles(self) -> Tuple[float, ...]:
        """
        Calculates the angles of the lines.

        :return: A tuple of the angles of the lines
        """

        if self._angles is None:
            self._angles = points_angles(self.points)
        # end if

        return self._angles
    # end angles

    def line(self) -> "Line":
        """
        Returns a line from the first to last point.

        :return: The new line object.
        """

        return Line(points=(self.points[0], self.points[-1]))
    # end line

    def lines(self) -> Tuple["Line", ...]:
        """
        Returns a line from the first to last point.

        :return: The new line object.
        """

        return tuple(
            Line(points=self.points[i:i + 2])
            for i in range(len(self.points) - 1)
        )
    # end line
# end Vector

class Line(Vector):
    """A class to represent a line between two points."""

    __slots__ = ()

    def __init__(
            self,
            points: Optional[Union[Iterable[Point], Tuple[Point, Point]]] = None,
            values: Optional[np.ndarray] = None
    ) -> None:
        """
        Defines the attributes of the line.

        :param points: The points in space to form a line.
        :param values: The array of values of the object.
        """

        if (len(tuple(points)) != 2) or (len(values) != 2):
            raise ValueError("Line must contain exactly 2 points.")
        # end if

        super().__init__(points=points, values=values)
    # end __init__

    def vector(self) -> Vector:
        """
        Converts the line object into a vector.

        :return: The vector object.
        """

        return Vector(points=self.points, values=self.values)
    # end vector
# end Line