import math
from decimal import Decimal
from abc import ABC, abstractmethod


class BaseFigure(ABC):
    """Abc class for figures
    """
    @abstractmethod
    def __init__(self, shape: dict[str, float]) -> None:
        pass

    @abstractmethod
    def area(self) -> float:
        pass


class Circle(BaseFigure):
    """Circle figure

    In the shape arg, which should be a dictionary, add the
    key "radius" and a positive float value.
    """

    def __init__(self, shape: dict[str, float]) -> None:
        """
        Args:
            shape dict[str, float]: shapes of circle.
                                    Must include 'radius' key

        Raises:
            ValueError: nonpositive radius
            KeyValueError: radius not define
        """
        if shape['radius'] <= 0:
            raise ValueError('Radius must be a positive float.')
        self.shape = shape

    def area(self) -> float:
        """Area o circle

        Returns:
            float: area
        """
        return math.pi * (self.shape['radius']**2)


class Triangle(BaseFigure):
    """Triangle figure

    In the shape arg, which should be a dictionary, add the
    keys with names of sides of triangle and a positive float values.
    """

    def __init__(self, shape: dict[str, float]) -> None:
        """
        Args:
            shape dict[str, float]: shapes of circle.
                                    Must have 3 side key, like `a`, `b`, `c`

        Raises:
            ValueError: nonpositive side value
        """
        if len(shape) != 3:
            raise ValueError('Triangle must have 3 sides.')
        if not all([True if i > 0 else False for i in shape.values()]):
            raise ValueError(
                'All sides of triangle must have a positive float value.'
                    )
        self.shape = shape

    def area(self) -> float:
        """Area of triangle

        Returns:
            float: area
        """
        v = self.shape.values()
        s = sum(v) / 2
        result = s
        for i in v:
            result *= s - i
        return float(result ** 0.5)

    def is_right(self) -> bool:
        """Is triangle right side

        Returns:
            bool
        """
        v = list(self.shape.values())
        m = max(v)
        v.remove(m)
        m = m ** 2
        o = v[0] ** 2 + v[1] ** 2
        return True if Decimal(m) == Decimal(o) else False
