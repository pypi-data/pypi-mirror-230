from __future__ import annotations

from typing import Generic, cast

from vecked.numbers import distance_between
from vecked.types import AnyNumber, TNumeric, TVector


class Vector2(Generic[TNumeric]):
    """
    A two-dimensional vector.

    .. testcode::

        from vecked import Vector2

        v = Vector2(3, 9)

        print(f"x = {v.x}")
        print(f"y = {v.y}")

    .. testoutput::
       :options: +NORMALIZE_WHITESPACE

       x = 3
       y = 9
    """

    def __init__(
        self,
        x: TNumeric,
        y: TNumeric,
    ) -> None:
        self._x: TNumeric = x
        self._y: TNumeric = y

    def __eq__(self, other: object) -> bool:
        if other is None:
            return False

        if isinstance(other, Vector2):
            other = cast(Vector2[AnyNumber], other)
            return self.vector == other.vector

        return self.vector == other

    def __str__(self) -> str:
        return str(self.vector)

    @staticmethod
    def distance_between(
        a: TVector[AnyNumber],
        b: TVector[AnyNumber],
    ) -> TVector[AnyNumber]:
        """
        Gets the distance between two vectors.

        .. testcode::

            from vecked import Vector2

            a = (3, 4)
            b = (-2, 2)
            d = Vector2.distance_between(a, b)

            print(f"distance = {d}")

        .. testoutput::
            :options: +NORMALIZE_WHITESPACE

            distance = (5, 2)
        """

        return (
            distance_between(a[0], b[0]),
            distance_between(a[1], b[1]),
        )

    def distance_to(
        self,
        other: AnyVector2,
    ) -> Vector2[AnyNumber]:
        """
        Gets the distance from this vector to another.

        .. testcode::

            from vecked import Vector2

            v = Vector2(3, 4)
            d = v.distance_to((-2, 2))

            print(f"distance = {d}")

        .. testoutput::
            :options: +NORMALIZE_WHITESPACE

            distance = (5, 2)
        """

        v = self.distance_between(
            self.vector,
            other.vector if isinstance(other, Vector2) else other,
        )

        return Vector2(v[0], v[1])

    @property
    def vector(self) -> TVector[TNumeric]:
        """
        Tuple of lengths.

        .. testcode::

            from vecked import Vector2

            v = Vector2(3, 9)

            print(f"vector = {v.vector}")

        .. testoutput::
            :options: +NORMALIZE_WHITESPACE

            vector = (3, 9)
        """

        return (self._x, self._y)

    @property
    def x(self) -> TNumeric:
        """
        X length.

        .. testcode::

            from vecked import Vector2

            v = Vector2(3, 9)

            print(f"x = {v.x}")

        .. testoutput::
            :options: +NORMALIZE_WHITESPACE

            x = 3
        """

        return self._x

    @property
    def y(self) -> TNumeric:
        """
        Y length.

        .. testcode::

            from vecked import Vector2

            v = Vector2(3, 9)

            print(f"y = {v.y}")

        .. testoutput::
            :options: +NORMALIZE_WHITESPACE

            y = 9
        """

        return self._y


AnyVector2 = Vector2[AnyNumber] | TVector[AnyNumber]
"""
Any vector type.
"""
