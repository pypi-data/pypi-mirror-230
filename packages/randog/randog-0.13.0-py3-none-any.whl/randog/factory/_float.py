import typing as t
from random import Random

from ._base import Factory, decide_rnd
from ..exceptions import FactoryConstructionError


def randfloat(
    minimum: t.Optional[t.SupportsFloat] = None,
    maximum: t.Optional[t.SupportsFloat] = None,
    *,
    p_inf: t.SupportsFloat = 0.0,
    n_inf: t.SupportsFloat = 0.0,
    nan: t.SupportsFloat = 0.0,
    rnd: t.Optional[Random] = None,
) -> Factory[float]:
    """Return a factory generating random float values.

    Parameters
    ----------
    minimum : float, optional
        the minimum
    maximum : float, optional
        the maximum
    p_inf : float, default=0
        the probability of positive infinity
    n_inf : float, default=0
        the probability of negative infinity
    nan : float, default=0
        the probability of NaN
    rnd : Random, optional
        random number generator to be used

    Raises
    ------
    FactoryConstructionError
        When the specified generating conditions are inconsistent.
    """
    return FloatRandomFactory(
        minimum,
        maximum,
        p_inf=p_inf,
        n_inf=n_inf,
        nan=nan,
        rnd=rnd,
    )


class FloatRandomFactory(Factory[float]):
    """factory generating random float values"""

    _random: Random
    _min: float
    _max: float
    _p_inf: float
    _n_inf: float
    _nan: float

    def __init__(
        self,
        minimum: t.Optional[t.SupportsFloat] = None,
        maximum: t.Optional[t.SupportsFloat] = None,
        *,
        p_inf: t.SupportsFloat = 0.0,
        n_inf: t.SupportsFloat = 0.0,
        nan: t.SupportsFloat = 0.0,
        rnd: t.Optional[Random] = None,
    ):
        """Return a factory generating random float values.

        Parameters
        ----------
        minimum : float, optional
            the minimum
        maximum : float, optional
            the maximum
        p_inf : float, default=0
            the probability of positive infinity
        n_inf : float, default=0
            the probability of negative infinity
        nan : float, default=0
            the probability of NaN
        rnd : Random, optional
            random number generator to be used

        Raises
        ------
        FactoryConstructionError
            When the specified generating conditions are inconsistent.
        """
        self._random = decide_rnd(rnd)
        self._min, self._max = self._normalize(minimum, maximum)
        self._p_inf = float(p_inf)
        self._n_inf = float(n_inf)
        self._nan = float(nan)

        if self._min > self._max:
            raise FactoryConstructionError("empty range for randfloat")
        if self._p_inf < 0.0 or self._n_inf < 0.0 or self._nan < 0.0:
            raise FactoryConstructionError(
                "the probabilities `p_inf`, `n_inf`, and `nan` must range from 0 to 1"
            )
        if self._p_inf + self._n_inf + self._nan > 1.0:
            raise FactoryConstructionError(
                "the sum of probabilities `p_inf`, `n_inf`, and `nan` "
                "must range from 0 to 1"
            )

    def _next(self) -> float:
        pre_weight = self._random.random()
        pre_weight -= self._p_inf
        if pre_weight < 0:
            return float("inf")
        pre_weight -= self._n_inf
        if pre_weight < 0:
            return float("-inf")
        pre_weight -= self._nan
        if pre_weight < 0:
            return float("NaN")

        weight = self._random.random()
        return self._max * weight + self._min * (1 - weight)

    @classmethod
    def _normalize(
        cls,
        minimum: t.Optional[t.SupportsFloat],
        maximum: t.Optional[t.SupportsFloat],
    ) -> t.Tuple[float, float]:
        default_range = 1.0

        if minimum is None and maximum is None:
            return 0.0, 1.0
        elif minimum is None:
            maximum = float(maximum)
            return maximum - default_range, maximum
        elif maximum is None:
            minimum = float(minimum)
            return minimum, minimum + default_range
        else:
            return float(minimum), float(maximum)
