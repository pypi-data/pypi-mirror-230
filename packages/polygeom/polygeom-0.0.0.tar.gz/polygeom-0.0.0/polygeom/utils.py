# utils.py

from typing import Iterable, List, Tuple, Optional
import math

import numpy as np

from polygeom.point import Point

__all__ = [
    "points_course",
    "points_angles",
    "points_distance",
    "points_distances",
    "polygon_points_angles",
    "polygon_points_sides",
    "polygon_points_area",
    "polygon_sides_angles"
]

def points_course(points: Iterable[Point]) -> float:
    """
    Returns the total points course of the data of the object.

    :param points: The points to calculate their points_course.

    :return: The total points course of values.
    """

    points = tuple(points)

    return sum(
        float(np.linalg.norm(points[i].values - points[i - 1].values))
        for i in range(1, len(points))
    )
# end points_course

def points_distance(start: Point, end: Point) -> float:
    """
    Returns the distance between the points.

    :param start: The start point.
    :param end: The ebd point.

    :return: The distance between the points.
    """

    return points_course((start, end))
# end points_distance

def points_distances(points: Iterable[Point]) -> Tuple[float, ...]:
    """
    Returns the points_distance of the first and last points of the object.

    :param points: The points to calculate their points_course.

    :return: The points_course of values.
    """

    points = tuple(points)

    return tuple(
        points_distance(start=points[i], end=points[i - 1])
        for i in range(1, len(points))
    )
# end points_distances

def points_angles(points: Iterable[Point]) -> Tuple[float, ...]:
    """
    Calculates the angles of the lines.

    :return: A tuple of the angles of the lines
    """

    points = tuple(points)

    if len(points) < 3:
        return ()

    else:
        triangles: List[List[Point]] = [
            list(points[i:i + 3])
            for i in range(len(points) - 2)
        ]

        angles = []

        for triangle_points in triangles:
            a = points_distance(triangle_points[0], triangle_points[1])
            b = points_distance(triangle_points[1], triangle_points[2])
            c = points_distance(triangle_points[2], triangle_points[0])

            angles.append(
                round(
                    math.acos(
                        ((a ** 2) + (b ** 2) - (c ** 2)) / (2 * a * b)
                    ) * 180 / math.pi,
                    12
                )
            )
        # end for

        return tuple(angles)
    # end if
# end points_angles

def polygon_points_angles(points: Iterable[Point]) -> Tuple[float, ...]:
    """
    Calculates the angles of the lines.

    :return: A tuple of the angles of the lines
    """

    points = tuple(points)

    return points_angles((points[-1], *points, points[0]))
# end polygon_points_angles

def polygon_points_sides(points: Iterable[Point]) -> Tuple[float, ...]:
    """
    Returns the points_distance of the first and last points of the object.

    :param points: The points to calculate their points_course.

    :return: The points_course of values.
    """

    points = tuple(points)

    return points_distances((*points, points[0]))
# end polygon_points_sides

def polygon_points_area(
        points: Optional[Iterable[Point]] = None,
        values: Optional[np.ndarray] = None
) -> float:
    """
    Calculates the area of the polygon.

    :param points: The points to calculate their points_course.
    :param values: The values of the points.

    :return: The area value
    """

    if values is None:
        if points is None:
            raise ValueError(f"No data given to {polygon_points_area}")
        # end if

        values = np.array([point.values for point in points])
    # end if

    if len(values) == 0:
        return 0.0
    # end if

    if len(values[0]) < 2:
        return 0.0
    # end if

    x = values[:, 0]
    y = values[:, 1]

    return 0.5 * np.abs(
        np.dot(x, np.roll(y, 1)) -
        np.dot(y, np.roll(x, 1))
    )
# end polygon_points_area

def polygon_sides_angles(sides: Iterable[float]) -> Tuple[float, ...]:
    """
    Calculates a set of inner angles for a polygon with the given sides.

    :param sides: The sides of the polygon.

    :return: The angles of the polygon.
    """

    angles = []

    sides = tuple(sides)

    radius = sides[0] / (2 * math.sin(180 / len(sides)))

    if (
        all(side == sides[0] for side in sides[1:]) or
        ((len(sides) == 4) and (sides[0] == sides[2]) and (sides[1] == sides[3]))
    ):
        return tuple([360 / len(sides)] * len(sides))
    # end if

    for side in sides:
        angles.append(
            (
                180 - math.acos(
                    (2 * radius ** 2 - side ** 2) / (2 * radius ** 2)
                ) * 180 / math.pi
            ) / 2
        )
    # end for

    first = angles[0]

    for i in range(len(angles) - 1):
        angles[i] += angles[i - 1]
    # end for

    angles[-1] += first
    angles[-1] += 360 - sum(angles)

    return tuple(angles)
# end polygon_sides_angles

print(sum(polygon_sides_angles([1, 1, 1, 1])))