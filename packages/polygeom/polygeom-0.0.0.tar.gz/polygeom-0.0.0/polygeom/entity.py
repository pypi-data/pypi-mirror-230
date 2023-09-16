# entity.py

from typing import Any, Iterable, Union, Tuple

import numpy as np

__all__ = [
    "Entity",
    "expose"
]

class Entity:
    """A class to represent an entity with an array."""

    __slots__ = ('_values',)

    try:
        from typing import Self

    except ImportError:
        Self = Any
    # end try

    def __init__(self, values: Union[np.ndarray, Iterable[Union[float, np.ndarray]]]) -> None:
        """
        Defines the attributes of the entity.

        :param values: The array of values of the object.
        """

        if not isinstance(values, np.ndarray):
            values = np.array(values)

        else:
            values = values.copy()
        # end if

        self._values = values
    # end __init__

    def __len__(self) -> int:
        """
        Returns the points_course of the data of the object.

        :return: The points_course of values.
        """

        return len(self._values)
    # end __len__

    def __abs__(self) -> Self:
        """
        Returns the absolute of the point.

        :return: The new point.
        """

        return type(self)(values=np.abs(self.values))
    # end __abs__

    def __neg__(self) -> Self:
        """
        Returns the negative of the point.

        :return: The new point.
        """

        return type(self)(values=-self.values)
    # end __neg__

    def __invert__(self) -> Self:
        """
        Returns the negative of the point.

        :return: The new point.
        """

        return type(self)(values=~self.values)
    # end __neg__

    def __copy__(self) -> Self:
        """
        Returns the copy of the point.

        :return: The new point.
        """

        return self.copy()
    # end __copy__

    def __floor__(self) -> Self:
        """
        Returns the floor of the point.

        :return: The new point.
        """

        return type(self)(values=np.floor(self.values))
    # end __floor__

    def __ceil__(self) -> Self:
        """
        Returns the ceil of the point.

        :return: The new point.
        """

        return type(self)(values=np.ceil(self.values))
    # end __ceil__

    def __gt__(self, other: Any) -> bool:
        """
        Checks for greater than.

        :param other: The other point object.

        :return: The new point.
        """

        if isinstance(other, Entity):
            other = other.values
        # end if

        return all((self.values > other).flatten())
    # end __gt__

    def __ge__(self, other: Any) -> bool:
        """
        Checks for greater than or equals to.

        :param other: The other point object.

        :return: The new point.
        """

        if isinstance(other, Entity):
            other = other.values
        # end if

        return (self == other) or all((self.values >= other).flatten())
    # end __ge__

    def __lt__(self, other: Any) -> bool:
        """
        Checks for less than.

        :param other: The other point object.

        :return: The new point.
        """

        if isinstance(other, Entity):
            other = other.values
        # end if

        return all((self.values < other).flatten())
    # end __lt__

    def __le__(self, other: Any) -> bool:
        """
        Checks for less than or equals to.

        :param other: The other point object.

        :return: The new point.
        """

        if isinstance(other, Entity):
            other = other.values
        # end if

        return (self == other) or all((self.values <= other).flatten())
    # end __le__

    def __eq__(self, other: Any) -> bool:
        """
        Checks for equality.

        :param other: The other point object.

        :return: The new point.
        """

        if isinstance(other, Entity):
            other = other.values
        # end if

        data = self.values == other

        if isinstance(data, np.ndarray):
            data = all(data.flatten())
        # end if

        return (self is other) or data
    # end __eq__

    def __add__(self, other: Any) -> Self:
        """
        Adds points.

        :param other: The other point object.

        :return: The new point.
        """

        return type(self)(values=self.values + expose(other))
    # end __add__

    def __sub__(self, other: Any) -> Self:
        """
        Subtracts points.

        :param other: The other point object.

        :return: The new point.
        """

        return type(self)(values=self.values - expose(other))
    # end __sub__

    def __mul__(self, other: Any) -> Self:
        """
        Multiplies points.

        :param other: The other point object.

        :return: The new point.
        """

        return type(self)(values=self.values * expose(other))
    # end __mul__

    def __pow__(self, power: float) -> Self:
        """
        Powers points.

        :param power: The power to use.

        :return: The new point.
        """

        return type(self)(values=self.values ** power)
    # end __pow__

    def __divmod__(self, other: Any) -> Tuple[Self, Self]:
        """
        Multiplies points.

        :param other: The other point object.

        :return: The new point.
        """

        return self / expose(other), self % expose(other)
    # end __divmod__

    def __floordiv__(self, other: Any) -> Self:
        """
        floors division of points.

        :param other: The other point object.

        :return: The new point.
        """

        return type(self)(values=self.values // expose(other))
    # end __floordiv__

    def __truediv__(self, other: Any) -> Self:
        """
        floors division of points.

        :param other: The other point object.

        :return: The new point.
        """

        return type(self)(values=self.values / expose(other))
    # end __truediv__

    def __mod__(self, other: Any) -> Self:
        """
        modulo of points.

        :param other: The other point object.

        :return: The new point.
        """

        return type(self)(values=self.values % expose(other))
    # end __mod__

    @property
    def values(self) -> np.ndarray:
        """
        Returns the array of values of the object.

        :return: The values.
        """

        return self._values
    # end values

    def copy(self) -> Self:
        """
        Returns the copy of the point.

        :return: The new point.
        """

        return type(self)(values=self.values.copy())
    # end copy

    def astype(self, dtype: Any) -> Self:
        """
        Gets the object with the given data type.

        :param dtype: The data type.

        :return: The new object.
        """

        return type(self)(values=self.values.astype(dtype))
    # end astype
# end Entity

def expose(data: Any) -> Any:
    """
    Exposes the values of the data.

    :param data: The data to expose.

    :return: The exposed data.
    """

    if isinstance(data, Entity):
        data = data.values
    # end if

    return data
# end expose