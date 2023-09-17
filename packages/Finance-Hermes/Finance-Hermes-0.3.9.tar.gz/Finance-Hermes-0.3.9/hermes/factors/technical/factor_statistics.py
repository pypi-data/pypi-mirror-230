# -*- encoding:utf-8 -*-
import copy
from hermes.factors.base import FactorBase, LongCallMixin, ShortMixin
from hermes.factors.technical.core.statistics import *


class FactorStatistics(FactorBase, LongCallMixin, ShortMixin):

    def __init__(self, **kwargs):
        __str__ = 'statistics'
        self.category = 'statistics'

    def _init_self(self, **kwargs):
        pass

    def KURTOSIS(self,
                 data,
                 length=None,
                 offset=None,
                 dependencies=['close'],
                 **kwargs):
        length = int(length) if length and length > 0 else 30
        result = kurtosis(copy.deepcopy(data['close']),
                          length=length,
                          offset=offset,
                          **kwargs)
        return self._format(result, f"KURT_{length}")

    def MAD(self,
            data,
            length=None,
            offset=None,
            dependencies=['close'],
            **kwargs):
        length = int(length) if length and length > 0 else 30
        result = mad(copy.deepcopy(data['close']),
                     length=length,
                     offset=offset,
                     **kwargs)
        return self._format(result, f"MAD_{length}")

    def MEDIAN(self,
               data,
               length=None,
               offset=None,
               dependencies=['close'],
               **kwargs):
        length = int(length) if length and length > 0 else 30
        result = median(copy.deepcopy(data['close']),
                        length=length,
                        offset=offset,
                        **kwargs)
        return self._format(result, f"MEDIAN_{length}")

    def QUANTILE(self,
                 data,
                 length=None,
                 offset=None,
                 q=None,
                 dependencies=['close'],
                 **kwargs):
        length = int(length) if length and length > 0 else 20
        q = float(q) if q and q > 0 and q < 1 else 0.5
        result = median(copy.deepcopy(data['close']),
                        length=length,
                        offset=offset,
                        q=q,
                        **kwargs)
        return self._format(result, f"QTL_{length}_{int(q)}")

    def SKEW(self,
             data,
             length=None,
             offset=None,
             dependencies=['close'],
             **kwargs):

        length = int(length) if length and length > 0 else 30
        result = skew(copy.deepcopy(data['close']),
                      length=length,
                      offset=offset,
                      **kwargs)
        return self._format(result, f"SKEW_{length}")

    def STDEV(self,
              data,
              length=None,
              ddof=None,
              offset=None,
              dependencies=['close'],
              **kwargs):
        length = int(length) if length and length > 0 else 30
        result = stdev(copy.deepcopy(data['close']),
                       length=length,
                       ddof=ddof,
                       offset=offset,
                       **kwargs)
        return self._format(result, f"STDEV_{length}")

    def VARIANCE(self,
                 data,
                 length=None,
                 ddof=None,
                 offset=None,
                 dependencies=['close'],
                 **kwargs):

        length = int(length) if length and length > 0 else 30
        result = variance(copy.deepcopy(data['close']),
                          length=length,
                          ddof=ddof,
                          offset=offset,
                          **kwargs)
        return self._format(result, f"VAR_{length}")

    def ZSCORE(self,
               data,
               length=None,
               std=None,
               offset=None,
               dependencies=['close'],
               **kwargs):
        length = int(length) if length and length > 0 else 30
        result = zscore(copy.deepcopy(data['close']),
                        length=length,
                        std=std,
                        offset=offset,
                        **kwargs)
        return self._format(result, f"ZS_{length}")
