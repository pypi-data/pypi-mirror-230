# polygon.py

from typing import Tuple, Optional, Iterable, Any, Union

import numpy as np

from polygeom.point import Point
from polygeom.vector import Vector, Line
from polygeom.utils import (
    polygon_points_angles, polygon_points_sides,
    polygon_points_area, polygon_points_triangles
)

class Polygon(Vector):
    """A class to represent a polygon."""

    __slots__ = ('_area', '_sides')

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

        super().__init__(points=points, values=values)

        self._area: Optional[float] = None
        self._sides: Optional[Tuple[float, ...]] = None
    # end __init__

    @classmethod
    def from_vector(cls, vector: Vector) -> Self:
        """
        Creates a polygon from a vector.

        :param vector: The vector object.

        :return: The new polygon object.
        """

        return Polygon(points=vector.points, values=vector.values)
    # end from_vector

    def sides(self) -> Tuple[float, ...]:
        """
        Returns the points_distance of the first and last points of the object.

        :return: The points_course of values.
        """

        if self._sides is None:
            self._sides = polygon_points_sides(self.points)
        # end if

        return self._sides
    # end points_distance

    def perimeter(self) -> float:
        """
        Calculates the perimeter of the polygon.

        :return: The perimeter value
        """

        return sum(self.sides())
    # end perimeter

    def area(self) -> float:
        """
        Calculates the area of the polygon.

        :return: The area value
        """

        if self._area is None:
            self._area = polygon_points_area(values=self.values)
        # end if

        return self._area
    # end area

    def angles(self) -> Tuple[float, ...]:
        """
        Calculates the angles of the lines.

        :return: A tuple of the angles of the lines
        """

        if self._angles is None:
            self._angles = polygon_points_angles(self.points)
        # end if

        return self._angles
    # end angles

    def lines(self) -> Tuple["Line", ...]:
        """
        Returns a line from the first to last point.

        :return: The new line object.
        """

        return *super().lines(), Line(points=(self.points[-1], self.points[0]))
    # end line

    def diagonals(
            self,
            start: Optional[Union[int, Iterable[int]]] = None,
            end: Optional[Union[int, Iterable[int]]] = None
    ) -> Tuple[Tuple["Line", ...]]:
        """
        Returns lines from the first to any point or from any point to the last.

        :param start: The start index for the lines.
        :param end: The end index for the lines.

        :return: The new line object.
        """

        return self.cross_lines(start=start, end=end, neighbours=False)
    # end diagonals

    def triangles(
            self, anchor: Optional[Union[int, Iterable[int]]] = 0,
    ) -> Tuple[Tuple["Polygon", ...], ...]:
        """
        Calculates the area of the polygon.

        :param anchor: The anchor for all triangles.

        :return: The area value
        """

        return tuple(
            tuple(Polygon(triangle) for triangle in triangles)
            for triangles in polygon_points_triangles(
                points=self.points, anchor=anchor
            )
        )
    # end triangles

    def sides_count(self) -> int:
        """
        Returns the amount of sides in the polygon.

        :return: The sides of values.
        """

        return len(self)
    # end sides_count

    def points_count(self) -> int:
        """
        Returns the amount of points in the polygon.

        :return: The points of values.
        """

        return len(self)
    # end points_count

    def diagonals_count(self) -> int:
        """
        Returns the amount of diagonals in the polygon.

        :return: The diagonals of values.
        """

        return (len(self) * (len(self) - 3)) // 2
    # end diagonals_count
# end Polygon