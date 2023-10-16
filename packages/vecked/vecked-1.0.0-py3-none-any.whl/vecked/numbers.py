from vecked.types import AnyNumber


def distance_between(a: AnyNumber, b: AnyNumber) -> AnyNumber:
    """
    Calculates the distance between two points on a number line.

    Distances are always positive and do not suggest direction.

    .. testcode::

        from vecked import distance_between

        distance = distance_between(-5, 3)

        print(f"distance = {distance}")

    .. testoutput::
       :options: +NORMALIZE_WHITESPACE

       distance = 8
    """

    multiplier = -1 if (a < 0) == (b < 0) else 1
    return abs(abs(a) + (abs(b) * multiplier))
