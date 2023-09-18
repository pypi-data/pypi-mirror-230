from typing import Generic, TypeVar

TNumeric = TypeVar("TNumeric", int, float)


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

    @property
    def x(self) -> TNumeric:
        """
        X length.
        """

        return self._x

    @property
    def y(self) -> TNumeric:
        """
        Y length.
        """

        return self._y
