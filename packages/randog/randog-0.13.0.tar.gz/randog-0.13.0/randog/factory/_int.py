import typing as t
from random import Random

from ._base import Factory, decide_rnd
from ..exceptions import FactoryConstructionError


def randint(
    minimum: int,
    maximum: int,
    *,
    rnd: t.Optional[Random] = None,
) -> Factory[int]:
    """Return a factory generating random int values.

    Parameters
    ----------
    minimum : int
        the minimum
    maximum : int
        the maximum
    rnd : Random, optional
        random number generator to be used

    Raises
    ------
    FactoryConstructionError
        When the specified generating conditions are inconsistent.
    """
    return IntRandomFactory(minimum, maximum, rnd=rnd)


class IntRandomFactory(Factory[int]):
    """factory generating random int values"""

    _random: Random
    _min: int
    _max: int

    def __init__(
        self,
        minimum: int,
        maximum: int,
        *,
        rnd: t.Optional[Random] = None,
    ):
        """Return a factory generating random int values.

        Parameters
        ----------
        minimum : int
            the minimum
        maximum : int
            the maximum
        rnd : Random, optional
            random number generator to be used

        Raises
        ------
        FactoryConstructionError
            When the specified generating conditions are inconsistent.
        """
        self._random = decide_rnd(rnd)
        self._min = minimum
        self._max = maximum

        if minimum > maximum:
            raise FactoryConstructionError("empty range for randint")

    def _next(self) -> int:
        return self._random.randint(self._min, self._max)
