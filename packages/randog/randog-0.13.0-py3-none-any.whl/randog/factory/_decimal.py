import typing as t
from decimal import Decimal
from random import Random

from ._base import Factory, decide_rnd
from ._float import randfloat
from .._utils.nullsafe import dforc


def randdecimal(
    minimum: t.Optional[t.SupportsFloat] = None,
    maximum: t.Optional[t.SupportsFloat] = None,
    *,
    decimal_len: t.Optional[int] = None,
    p_inf: t.SupportsFloat = 0.0,
    n_inf: t.SupportsFloat = 0.0,
    nan: t.SupportsFloat = 0.0,
    rnd: t.Optional[Random] = None,
) -> Factory[Decimal]:
    """Return a factory generating random Decimal values.

    Parameters
    ----------
    minimum : float, optional
        the minimum
    maximum : float, optional
        the maximum
    decimal_len : int, optional
        the length of decimal part
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
    return DecimalRandomFactory(
        minimum,
        maximum,
        decimal_len=decimal_len,
        p_inf=p_inf,
        n_inf=n_inf,
        nan=nan,
        rnd=rnd,
    )


class DecimalRandomFactory(Factory[Decimal]):
    """factory generating random Decimal values"""

    _random: Random
    _factory: Factory[float]
    _decimal_len: t.Optional[Decimal]

    def __init__(
        self,
        minimum: t.Optional[t.SupportsFloat] = None,
        maximum: t.Optional[t.SupportsFloat] = None,
        *,
        decimal_len: t.Optional[int] = None,
        p_inf: t.SupportsFloat = 0.0,
        n_inf: t.SupportsFloat = 0.0,
        nan: t.SupportsFloat = 0.0,
        rnd: t.Optional[Random] = None,
    ):
        """Return a factory generating random Decimal values.

        Parameters
        ----------
        minimum : float, optional
            the minimum
        maximum : float, optional
            the maximum
        decimal_len : int, optional
            the length of decimal part
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
        self._factory = randfloat(
            minimum, maximum, p_inf=p_inf, n_inf=n_inf, nan=nan, rnd=self._random
        )
        self._decimal_len = dforc(lambda x: Decimal(1).scaleb(-x), decimal_len)

    def _next(self) -> Decimal:
        pre_value = self._factory.next()
        value = Decimal(pre_value)

        if self._decimal_len is not None and value.is_finite():
            value = value.quantize(self._decimal_len)

        return value
