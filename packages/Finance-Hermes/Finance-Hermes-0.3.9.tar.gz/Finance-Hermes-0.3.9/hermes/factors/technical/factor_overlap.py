# -*- encoding:utf-8 -*-
import copy
from hermes.factors.base import FactorBase, LongCallMixin, ShortMixin
from hermes.factors.technical.core.utilities import pascals_triangle, weights
from hermes.factors.technical.core.overlap import *


class FactorOverlap(FactorBase, LongCallMixin, ShortMixin):

    def __init__(self, **kwargs):
        __str__ = 'overlap'
        self.category = 'overlap'

    def _init_self(self, **kwargs):
        pass

    def DEMA(self,
             data,
             length=None,
             offset=None,
             dependencies=['close'],
             **kwargs):
        length = int(length) if length and length > 0 else 10
        result = dema(copy.deepcopy(data['close']),
                      length=length,
                      offset=offset,
                      **kwargs)
        return self._format(result, f"DEMA_{length}")

    def EMA(self,
            data,
            length=None,
            offset=None,
            dependencies=['close'],
            **kwargs):
        length = int(length) if length and length > 0 else 10
        close = copy.deepcopy(data['close'])
        result = ema(close, length=length, offset=offset, **kwargs)
        return self._format(result, f"EMA_{length}")

    def FWMA(self,
             data,
             length=None,
             asc=None,
             offset=None,
             dependencies=['close'],
             **kwargs):
        length = int(length) if length and length > 0 else 10
        result = fwma(copy.deepcopy(data['close']),
                      length=length,
                      asc=asc,
                      offset=offset,
                      **kwargs)
        return self._format(result, f"FWMA_{length}")

    def HL2(self, data, offset=None, dependencies=['high', 'low'], **kwargs):
        result = hl2(copy.deepcopy(data['high']), copy.deepcopy(data['low']),
                     **kwargs)
        return self._format(result, f"HL2")

    def HLC3(self,
             data,
             offset=None,
             dependencies=['high', 'low', 'close'],
             **kwargs):
        result = hlc3(copy.deepcopy(data['high']),
                      copy.deepcopy(data['low']),
                      copy.deepcopy(data['close']),
                      offset=offset,
                      **kwargs)
        return self._format(result, f"HLC3")

    def HMA(self,
            data,
            length=None,
            offset=None,
            dependencies=['close'],
            **kwargs):
        length = int(length) if length and length > 0 else 10
        result = hma(copy.deepcopy(data['close']),
                     length=length,
                     offset=offset,
                     **kwargs)
        return self._format(result, f"HMA_{length}")

    def ICHIMOKU(self,
                 data,
                 tenkan=None,
                 kijun=None,
                 senkou=None,
                 include_chikou=True,
                 offset=None,
                 dependencies=['close', 'low', 'high'],
                 **kwargs):
        tenkan = int(tenkan) if tenkan and tenkan > 0 else 9
        kijun = int(kijun) if kijun and kijun > 0 else 26

        span_a, span_b = ichimoku(copy.deepcopy(data['high']),
                                  copy.deepcopy(data['low']),
                                  copy.deepcopy(data['close']),
                                  tenkan=tenkan,
                                  kijun=kijun,
                                  senkou=senkou,
                                  include_chikou=include_chikou,
                                  offset=offset,
                                  **kwargs)
        return self._format(span_b - span_a, f"ISB_{kijun}_ISA_{tenkan}")

    def MIDPOINT(self,
                 data,
                 length=None,
                 offset=None,
                 dependencies=['close'],
                 **kwargs):
        length = int(length) if length and length > 0 else 2
        result = midpoint(copy.deepcopy(data['close']),
                          length=length,
                          offset=offset,
                          **kwargs)
        return self._format(result, f"MIDPOINT_{length}")

    def MIDPRICE(self,
                 data,
                 length=None,
                 offset=None,
                 dependencies=['high', 'low'],
                 **kwargs):
        length = int(length) if length and length > 0 else 2
        result = midprice(copy.deepcopy(data['high']),
                          copy.deepcopy(data['low']),
                          length=length,
                          offset=offset,
                          **kwargs)
        return self._format(result, f"MIDPRICE_{length}")

    def OHLC4(self,
              data,
              offset=None,
              dependencies=['open', 'close', 'high', 'low'],
              **kwargs):
        result = ohlc4(copy.deepcopy(data['open']),
                       copy.deepcopy(data['high']),
                       copy.deepcopy(data['low']),
                       copy.deepcopy(data['close']),
                       offset=offset)
        return self._format(result, f"OHLC4")

    def PWMA(self,
             data,
             length=None,
             asc=None,
             offset=None,
             dependencies=['close'],
             **kwargs):
        length = int(length) if length and length > 0 else 10
        result = pwma(copy.deepcopy(data['close']),
                      length=length,
                      asc=asc,
                      offset=offset,
                      **kwargs)
        return self._format(result, f"PWMA_{length}")

    def RMA(self,
            data,
            length=None,
            offset=None,
            dependencies=['close'],
            **kwargs):
        length = int(length) if length and length > 0 else 10
        result = rma(copy.deepcopy(data['close']),
                     length=length,
                     offset=offset,
                     **kwargs)
        return self._format(result, f"RMA_{length}")

    def SMA(self,
            data,
            length=None,
            offset=None,
            dependencies=['close'],
            **kwargs):
        length = int(length) if length and length > 0 else 10
        result = sma(copy.deepcopy(data['close']),
                     length=length,
                     offset=offset,
                     **kwargs)
        return self._format(result, f"SMA_{length}")

    def SSF(self,
            data,
            length=None,
            poles=None,
            offset=None,
            dependencies=['close'],
            **kwargs):
        length = int(length) if length and length > 0 else 10
        poles = int(poles) if poles in [2, 3] else 2
        result = ssf(copy.deepcopy(data['close']),
                     length=length,
                     poles=poles,
                     offset=offset,
                     **kwargs)
        return self._format(result, f"SSF_{length}_{poles}")

    def SWMA(self,
             data,
             length=None,
             asc=None,
             offset=None,
             dependencies=['close'],
             **kwargs):
        length = int(length) if length and length > 0 else 10
        result = swma(copy.deepcopy(data['close']),
                      length=length,
                      asc=asc,
                      offset=offset,
                      **kwargs)
        return self._format(result, f"SWMA_{length}")

    def T3(self,
           data,
           length=None,
           a=None,
           talib=None,
           offset=None,
           dependencies=['close'],
           **kwargs):
        length = int(length) if length and length > 0 else 10
        a = float(a) if a and a > 0 and a < 1 else 0.7
        result = t3(copy.deepcopy(data['close']),
                    length=length,
                    a=a,
                    offset=offset,
                    **kwargs)
        return self._format(result, f"T3_{length}_{int(a)}")

    def TEMA(self,
             data,
             length=None,
             offset=None,
             dependencies=['close'],
             **kwargs):
        length = int(length) if length and length > 0 else 10
        result = tema(copy.deepcopy(data['close']),
                      length=length,
                      offset=offset,
                      **kwargs)
        return self._format(result, f"TEMA_{length}")

    def TRIMA(self,
              data,
              length=None,
              offset=None,
              dependencies=['close'],
              **kwargs):
        length = int(length) if length and length > 0 else 10
        result = trima(copy.deepcopy(data['close']),
                       length=length,
                       offset=offset,
                       **kwargs)
        return self._format(result, f"TRIMA_{length}")

    def VWMA(self,
             data,
             length=None,
             offset=None,
             dependencies=['close', 'volume'],
             **kwargs):
        length = int(length) if length and length > 0 else 10
        result = vwma(copy.deepcopy(data['close']),
                      copy.deepcopy(data['volume']),
                      length=length,
                      offset=offset,
                      **kwargs)
        return self._format(result, f"VWMA_{length}")

    def WCP(self,
            data,
            offset=None,
            dependencies=['high', 'low', 'close'],
            **kwargs):
        result = wcp(copy.deepcopy(data['high']),
                     copy.deepcopy(data['low']),
                     copy.deepcopy(data['close']),
                     offset=offset,
                     **kwargs)
        return self._format(result, f"WCP")

    def WMA(self,
            data,
            length=None,
            asc=None,
            offset=None,
            dependencies=['close'],
            **kwargs):
        length = int(length) if length and length > 0 else 10
        result = wma(copy.deepcopy(data['close']),
                     length=length,
                     asc=asc,
                     offset=offset,
                     **kwargs)
        return self._format(result, f"WMA_{length}")
