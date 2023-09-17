# -*- encoding:utf-8 -*-
from hermes.factors.base import FactorBase, LongCallMixin, ShortMixin
from hermes.factors.fundamentals.core.basis import *


class FactorBasis(FactorBase, LongCallMixin, ShortMixin):

    def __init__(self, **kwargs):
        __str__ = 'basis'
        self.category = 'basis'

    def _init_self(self, **kwargs):
        pass

    def RSACHG(self,
               data,
               drift=None,
               offset=None,
               dependencies=['spot', 'recent', 'rinterval'],
               **kwargs):
        result = rsannchg(data['spot'],
                          data['recent'],
                          data['rinterval'],
                          drift=drift,
                          offset=offset,
                          **kwargs)
        return self._format(result, f"RSACHG")

    def MSACHG(self,
               data,
               drift=None,
               offset=None,
               dependencies=['spot', 'main', 'minterval'],
               **kwargs):
        result = msannchg(data['spot'],
                          data['main'],
                          data['minterval'],
                          drift=drift,
                          offset=offset,
                          **kwargs)
        return self._format(result, f"MSACHG")

    def SSACHG(self,
               data,
               drift=None,
               offset=None,
               dependencies=['spot', 'second', 'sinterval'],
               **kwargs):
        result = ssannchg(data['spot'],
                          data['second'],
                          data['sinterval'],
                          drift=drift,
                          offset=offset,
                          **kwargs)
        return self._format(result, f"SSACHG")

    def FSACHG(self,
               data,
               drift=None,
               offset=None,
               dependencies=['spot', 'far', 'finterval'],
               **kwargs):
        result = fsannchg(data['spot'],
                          data['far'],
                          data['finterval'],
                          drift=drift,
                          offset=offset,
                          **kwargs)
        return self._format(result, f"FSACHG")
