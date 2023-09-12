# -*- encoding:utf-8 -*-
import copy
from numpy import nan as npNaN
from numpy import sqrt as npSqrt
from hermes.factors.base import FactorBase, LongCallMixin, ShortMixin
from hermes.factors.technical.core.utilities import pascals_triangle, weights
from hermes.factors.technical.core.volatility import *


class FactorVolatility(FactorBase, LongCallMixin, ShortMixin):

    def __init__(self, **kwargs):
        __str__ = 'volatility'
        self.category = 'volatility'

    def _init_self(self, **kwargs):
        pass

    def ABERRATION(self,
                   data,
                   length=None,
                   atr_length=None,
                   offset=None,
                   dependencies=['high', 'low', 'close'],
                   **kwargs):
        length = int(length) if length and length > 0 else 5
        atr_length = int(atr_length) if atr_length and atr_length > 0 else 15

        zg, sg, xg, atr_ = aberration(copy.deepcopy(data['high']),
                                      copy.deepcopy(data['low']),
                                      copy.deepcopy(data['close']),
                                      length=length,
                                      atr_length=atr_length,
                                      offset=offset,
                                      **kwargs)

        zg = self._format(zg, f"ABER_ZG_{length}_{atr_length}")
        sg = self._format(sg, f"ABER_SG_{length}_{atr_length}")
        xg = self._format(xg, f"ABER_XG_{length}_{atr_length}")
        atr_ = self._format(atr_, f"ABER_ATR_{length}_{atr_length}")
        return zg, sg, xg, atr_

    def ACCBANDS(self,
                 data,
                 length=None,
                 c=None,
                 drift=None,
                 offset=None,
                 dependencies=['high', 'low', 'close'],
                 **kwargs):

        length = int(length) if length and length > 0 else 20
        lower, mid, upper = accbands(copy.deepcopy(data['high']),
                                     copy.deepcopy(data['low']),
                                     copy.deepcopy(data['close']),
                                     length=length,
                                     c=c,
                                     drift=drift,
                                     offset=offset)
        lower = self._format(lower, f"ACCBL_{length}")
        mid = self._format(mid, f"ACCBM_{length}")
        upper = self._format(upper, f"ACCBU_{length}")
        return lower, mid, upper

    def ATR(self,
            data,
            length=None,
            drift=None,
            offset=None,
            dependencies=['high', 'low', 'close'],
            **kwargs):
        length = int(length) if length and length > 0 else 14
        percentage = kwargs.pop("percent", False)
        result = atr(copy.deepcopy(data['high']),
                     copy.deepcopy(data['low']),
                     copy.deepcopy(data['close']),
                     length=length,
                     drift=drift,
                     offset=offset,
                     **kwargs)
        return self._format(result, f"ATR_{length}{'p' if percentage else ''}")

    def BBANDS(self,
               data,
               length=None,
               std=None,
               ddof=0,
               offset=None,
               dependencies=['close'],
               **kwargs):
        length = int(length) if length and length > 0 else 5
        std = float(std) if std and std > 0 else 2.0
        lower, mid, upper, bandwidth, percent = bbands(copy.deepcopy(
            data['close']),
                                                       length=length,
                                                       std=std,
                                                       ddof=ddof,
                                                       offset=offset,
                                                       **kwargs)
        lower = self._format(lower, f"BBL_{length}_{int(std)}")
        mid = self._format(mid, f"BBM_{length}_{int(std)}")
        upper = self._format(upper, f"BBU_{length}_{int(std)}")
        bandwidth = self._format(bandwidth, f"BBB_{length}_{int(std)}")
        percent = self._format(percent, f"BBP_{length}_{int(std)}")
        return lower, mid, upper, bandwidth, percent

    def DONCHINAN(self,
                  data,
                  lower_length=None,
                  upper_length=None,
                  offset=None,
                  dependencies=['high', 'low'],
                  **kwargs):
        lower_length = int(
            lower_length) if lower_length and lower_length > 0 else 20
        upper_length = int(
            upper_length) if upper_length and upper_length > 0 else 20

        lower, mid, upper = donchian(copy.deepcopy(data['high']),
                                     copy.deepcopy(data['low']),
                                     lower_length=lower_length,
                                     upper_length=upper_length,
                                     offset=offset,
                                     **kwargs)

        lower = self._format(lower, f"DCL_{lower_length}_{upper_length}")
        mid = self._format(mid, f"DCM_{lower_length}_{upper_length}")
        upper = self._format(upper, f"DCU_{lower_length}_{upper_length}")
        return lower, mid, upper

    def KC(self,
           data,
           length=None,
           scalar=None,
           offset=None,
           dependencies=['high', 'low', 'close'],
           **kwargs):
        length = int(length) if length and length > 0 else 20
        scalar = float(scalar) if scalar and scalar > 0 else 2

        lower, basis, upper = kc(copy.deepcopy(data['high']),
                                 copy.deepcopy(data['low']),
                                 copy.deepcopy(data['close']),
                                 length=length,
                                 scalar=scalar,
                                 offset=offset,
                                 **kwargs)

        lower = self._format(lower, f"KCL_{length}_{scalar}")
        basis = self._format(basis, f"KCB_{length}_{scalar}")
        upper = self._format(upper, f"KCU_{length}_{scalar}")
        return lower, basis, upper

    def MASSI(self,
              data,
              fast=None,
              slow=None,
              offset=None,
              dependencies=['high', 'low'],
              **kwargs):
        fast = int(fast) if fast and fast > 0 else 9
        slow = int(slow) if slow and slow > 0 else 25

        result = massi(copy.deepcopy(data['high']),
                       copy.deepcopy(data['low']),
                       fast=fast,
                       slow=slow,
                       offset=offset,
                       **kwargs)
        return self._format(result, f"MASSI_{fast}_{slow}")

    def NATR(self,
             data,
             length=None,
             scalar=None,
             drift=None,
             offset=None,
             dependencies=['high', 'low', 'close'],
             **kwargs):
        length = int(length) if length and length > 0 else 14
        result = natr(copy.deepcopy(data['high']),
                      copy.deepcopy(data['low']),
                      copy.deepcopy(data['close']),
                      length=length,
                      scalar=scalar,
                      drift=drift,
                      offset=offset,
                      **kwargs)
        return self._format(result, f"NATR_{length}")

    def PDIST(self,
              data,
              drift=None,
              offset=None,
              dependencies=['open', 'high', 'low', 'close'],
              **kwargs):
        result = pdist(copy.deepcopy(data['open']),
                       copy.deepcopy(data['high']),
                       copy.deepcopy(data['low']),
                       copy.deepcopy(data['close']),
                       drift=drift,
                       offset=offset,
                       **kwargs)
        return self._format(result, f"PDIST")

    def RVI(self,
            data,
            length=None,
            scalar=None,
            refined=None,
            thirds=None,
            drift=None,
            offset=None,
            dependencies=['high', 'low', 'close'],
            **kwargs):
        length = int(length) if length and length > 0 else 14
        scalar = float(scalar) if scalar and scalar > 0 else 100
        result = rvi(copy.deepcopy(data['close']),
                     copy.deepcopy(data['high']),
                     copy.deepcopy(data['low']),
                     length=length,
                     scalar=scalar,
                     refined=refined,
                     thirds=thirds,
                     drift=drift,
                     offset=offset)
        return self._format(result, f"RVI_{length}_{scalar}")

    def THERMO(self,
               data,
               length=None,
               long=None,
               short=None,
               drift=None,
               offset=None,
               dependencies=['high', 'low'],
               **kwargs):
        length = int(length) if length and length > 0 else 20
        long = float(long) if long and long > 0 else 2
        short = float(short) if short and short > 0 else 0.5
        result, thermo_ma, thermo_long, thermo_short = thermo(
            copy.deepcopy(data['high']),
            copy.deepcopy(data['low']),
            length=length,
            long=long,
            short=short,
            drift=drift,
            offset=offset,
            **kwargs)

        result = self._format(result,
                              f"THERMO_{length}_{int(long)}_{int(short)}")
        thermo_ma = self._format(
            thermo_ma, f"THERMOma_{length}_{int(long)}_{int(short)}")
        thermo_long = self._format(
            thermo_long, f"THERMOl_{length}_{int(long)}_{int(short)}")
        thermo_short = self._format(
            thermo_short, f"THERMOs_{length}_{int(long)}_{int(short)}")
        return result, thermo_ma, thermo_long, thermo_short

    def TRUE_RANGE(self,
                   data,
                   drift=None,
                   offset=None,
                   dependencies=['high', 'low', 'close'],
                   **kwargs):
        drift = int(drift) if isinstance(drift, int) and drift != 0 else 1
        result = true_range(copy.deepcopy(data['high']),
                            copy.deepcopy(data['low']),
                            copy.deepcopy(data['close']),
                            drift=drift,
                            offset=offset,
                            **kwargs)
        return self._format(result, f"TRUERANGE_{drift}")

    def UI(self,
           data,
           length=None,
           scalar=None,
           offset=None,
           dependencies=['close'],
           **kwargs):
        length = int(length) if length and length > 0 else 14
        result = ui(copy.deepcopy(data['close']),
                    length=length,
                    scalar=scalar,
                    offset=offset,
                    **kwargs)
        return self._format(result, f"UI_{length}")
