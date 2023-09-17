# -*- encoding:utf-8 -*-
import copy
from numpy import fabs as npFabs
from hermes.factors.base import FactorBase, LongCallMixin, ShortMixin
from hermes.factors.technical.core.trend import *


class FactorTrend(FactorBase, LongCallMixin, ShortMixin):

    def __init__(self, **kwargs):
        __str__ = 'trend'
        self.category = 'trend'

    def _init_self(self, **kwargs):
        pass

    def ADX(self,
            data,
            length=None,
            lensig=None,
            scalar=None,
            drift=None,
            offset=None,
            dependencies=['high', 'low', 'close'],
            **kwargs):
        length = length if length and length > 0 else 14
        lensig = lensig if lensig and lensig > 0 else length
        result, dmp, dmn = adx(copy.deepcopy(data['high']),
                               copy.deepcopy(data['low']),
                               copy.deepcopy(data['close']),
                               length=length,
                               lensig=lensig,
                               scalar=scalar,
                               drift=drift,
                               offset=offset,
                               **kwargs)
        result = self._format(result, f"ADX_{lensig}")
        dmp = self._format(dmp, f"ADXp_{length}")
        dmn = self._format(dmn, f"ADXn_{length}")
        return result, dmp, dmn

    def AMAT(self,
             data,
             fast=None,
             slow=None,
             lookback=None,
             offset=None,
             dependencies=['close'],
             **kwargs):
        fast = int(fast) if fast and fast > 0 else 8
        slow = int(slow) if slow and slow > 0 else 21
        lookback = int(lookback) if lookback and lookback > 0 else 2
        mas_long, mas_short = amat(copy.deepcopy(data['close']),
                                   fast=fast,
                                   slow=slow,
                                   lookback=lookback,
                                   offset=offset,
                                   **kwargs)
        mas_long = self._format(mas_long, f"AMAT_LR_{fast}_{slow}_{lookback}")
        mas_short = self._format(mas_short,
                                 f"AMAT_SR_{fast}_{slow}_{lookback}")
        return mas_long, mas_short

    def CHOP(self,
             data,
             length=None,
             atr_length=None,
             ln=None,
             scalar=None,
             drift=None,
             offset=None,
             dependencies=['high', 'low', 'close'],
             **kwargs):
        length = int(length) if length and length > 0 else 14
        atr_length = int(
            atr_length) if atr_length is not None and atr_length > 0 else 1
        ln = bool(ln) if isinstance(ln, bool) else False
        scalar = float(scalar) if scalar else 100

        result = chop(copy.deepcopy(data['high']),
                      copy.deepcopy(data['low']),
                      copy.deepcopy(data['close']),
                      length=length,
                      atr_length=atr_length,
                      ln=ln,
                      scalar=scalar,
                      drift=drift,
                      offset=offset,
                      **kwargs)
        return self._format(
            result, f"CHOP{'ln' if ln else ''}_{length}_{atr_length}_{scalar}")

    def CKSP(self,
             data,
             p=None,
             x=None,
             q=None,
             tvmode=None,
             offset=None,
             dependencies=['high', 'low', 'close'],
             **kwargs):

        p = int(p) if p and p > 0 else 10
        x = float(x) if x and x > 0 else 1 if tvmode is True else 3
        q = int(q) if q and q > 0 else 9 if tvmode is True else 20

        long_stop, short_stop = cksp(copy.deepcopy(data['high']),
                                     copy.deepcopy(data['low']),
                                     copy.deepcopy(data['close']),
                                     p=p,
                                     x=x,
                                     q=q,
                                     tvmode=tvmode,
                                     offset=offset,
                                     **kwargs)
        long_stop = self._format(long_stop, f"CKSPl_{p}_{x}_{q}")
        short_stop = self._format(short_stop, f"CKSPs_{p}_{x}_{q}")
        return long_stop, short_stop

    def DPO(self,
            data,
            length=None,
            centered=True,
            offset=None,
            dependencies=['close'],
            **kwargs):
        length = int(length) if length and length > 0 else 20
        result = dpo(copy.deepcopy(data['close']),
                     length=length,
                     centered=centered,
                     offset=offset,
                     **kwargs)
        return self._format(result, f"DPO_{length}")

    def QSTICK(self,
               data,
               length=None,
               offset=None,
               dependencies=['open', 'close'],
               **kwargs):
        length = int(length) if length and length > 0 else 10
        result = qstick(copy.deepcopy(data['open']),
                        copy.deepcopy(data['close']),
                        length=length,
                        offset=offset,
                        **kwargs)
        return self._format(result, f"QS_{length}")

    def TTM_TREND(self,
                  data,
                  length=None,
                  offset=None,
                  dependencies=['high', 'low', 'close'],
                  **kwargs):
        length = int(length) if length and length > 0 else 6
        result = ttm_trend(copy.deepcopy(data['high']),
                           copy.deepcopy(data['low']),
                           copy.deepcopy(data['close']),
                           length=length,
                           offset=offset,
                           **kwargs)
        return self._format(result, f"TTM_TRND_{length}")

    def VHF(self,
            data,
            length=None,
            drift=None,
            offset=None,
            dependencies=['close'],
            **kwargs):
        length = int(length) if length and length > 0 else 28
        result = vhf(copy.deepcopy(data['close']),
                     length=length,
                     drift=drift,
                     offset=offset,
                     **kwargs)
        return self._format(result, f"VHF_{length}")

    def VORTEX(self,
               data,
               length=None,
               drift=None,
               offset=None,
               dependencies=['high', 'low', 'close'],
               **kwargs):
        length = length if length and length > 0 else 14
        vip, vim = vortex(copy.deepcopy(data['high']),
                          copy.deepcopy(data['low']),
                          copy.deepcopy(data['close']),
                          length=length,
                          drift=drift,
                          offset=offset,
                          **kwargs)
        vip = self._format(vip, f"VTXP_{length}")
        vim = self._format(vim, f"VTXM_{length}")
        return vip, vim
