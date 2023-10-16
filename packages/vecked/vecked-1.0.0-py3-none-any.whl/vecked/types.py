from typing import TypeVar

AnyNumber = int | float

TNumeric = TypeVar("TNumeric", bound=AnyNumber)
"""
Any numeric type.
"""

TVector = tuple[TNumeric, TNumeric]
"""
Any numeric vector type.
"""
