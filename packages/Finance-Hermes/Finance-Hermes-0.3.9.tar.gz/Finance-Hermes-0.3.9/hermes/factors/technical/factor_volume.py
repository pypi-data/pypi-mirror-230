# -*- encoding:utf-8 -*-
import copy
from numpy import fabs as npFabs
from hermes.factors.base import FactorBase, LongCallMixin, ShortMixin
from hermes.factors.technical.core.volume import *


class FactorVolume(FactorBase, LongCallMixin, ShortMixin):

    def __init__(self, **kwargs):
        __str__ = 'volume'
        self.category = 'volume'

    def _init_self(self, **kwargs):
        pass

    def AD(self,
           data,
           offset=None,
           dependencies=['high', 'low', 'close', 'volume', 'open'],
           **kwargs):
        result = ad(copy.deepcopy(data['high']),
                    copy.deepcopy(data['low']),
                    copy.deepcopy(data['close']),
                    copy.deepcopy(data['volume']),
                    copy.deepcopy(data['open']),
                    offset=offset,
                    **kwargs)
        return self._format(result, f"AD")

    def ADOSC(self,
              data,
              fast=None,
              slow=None,
              offset=None,
              dependencies=['high', 'low', 'close', 'volume', 'open'],
              **kwargs):
        fast = int(fast) if fast and fast > 0 else 3
        slow = int(slow) if slow and slow > 0 else 10
        result = adosc(copy.deepcopy(data['high']),
                       copy.deepcopy(data['low']),
                       copy.deepcopy(data['close']),
                       copy.deepcopy(data['volume']),
                       copy.deepcopy(data['open']),
                       fast=fast,
                       slow=slow,
                       offset=offset,
                       **kwargs)
        return self._format(result, f"ADOSC_{fast}_{slow}")

    def AOBV(self,
             data,
             fast=None,
             slow=None,
             max_lookback=None,
             min_lookback=None,
             offset=None,
             dependencies=['close', 'volume'],
             **kwargs):
        fast = int(fast) if fast and fast > 0 else 4
        slow = int(slow) if slow and slow > 0 else 12
        max_lookback = int(
            max_lookback) if max_lookback and max_lookback > 0 else 2
        min_lookback = int(
            min_lookback) if min_lookback and min_lookback > 0 else 2
        if "length" in kwargs: kwargs.pop("length")
        run_length = kwargs.pop("run_length", 2)

        obv_, maf, mas, obv_long, obv_short = aobv(
            copy.deepcopy(data['close']),
            copy.deepcopy(data['volume']),
            fast=fast,
            slow=slow,
            max_lookback=max_lookback,
            min_lookback=min_lookback,
            offset=offset,
            **kwargs)
        obv_ = self._format(
            obv_,
            f"AOBV_{fast}_{slow}_{min_lookback}_{max_lookback}_{run_length}")
        maf = self._format(
            maf,
            f"AOBV_FAST_{fast}_{slow}_{min_lookback}_{max_lookback}_{run_length}"
        )
        mas = self._format(
            mas,
            f"AOBV_SLOW_{fast}_{slow}_{min_lookback}_{max_lookback}_{run_length}"
        )
        obv_long = self._format(
            obv_long,
            f"AOBV_LR_{fast}_{slow}_{min_lookback}_{max_lookback}_{run_length}"
        )
        obv_short = self._format(
            obv_short,
            f"AOBV_SR_{fast}_{slow}_{min_lookback}_{max_lookback}_{run_length}"
        )
        return obv_, maf, mas, obv_long, obv_short

    def CMF(self,
            data,
            length=None,
            offset=None,
            dependencies=['high', 'low', 'close', 'volume', 'open'],
            **kwargs):
        length = int(length) if length and length > 0 else 20
        result = cmf(copy.deepcopy(data['high']),
                     copy.deepcopy(data['low']),
                     copy.deepcopy(data['close']),
                     copy.deepcopy(data['volume']),
                     copy.deepcopy(data['open']),
                     length=length,
                     offset=offset)
        return self._format(result, f"CMF_{length}")

    def EFI(self,
            data,
            length=None,
            drift=None,
            offset=None,
            dependencies=['close', 'volume'],
            **kwargs):
        length = int(length) if length and length > 0 else 13
        result = efi(copy.deepcopy(data['close']),
                     copy.deepcopy(data['volume']),
                     length=length,
                     drift=drift,
                     offset=offset,
                     **kwargs)
        return self._format(result, f"EFI_{length}")

    def EOM(self,
            data,
            length=None,
            divisor=None,
            drift=None,
            offset=None,
            dependencies=['high', 'low', 'volume'],
            **kwargs):
        length = int(length) if length and length > 0 else 14
        divisor = divisor if divisor and divisor > 0 else 100000000
        result = eom(copy.deepcopy(data['high']),
                     copy.deepcopy(data['low']),
                     copy.deepcopy(data['volume']),
                     length=length,
                     divisor=divisor,
                     drift=drift,
                     offset=offset,
                     **kwargs)
        return self._format(result, f"EOM_{length}")

    def KVO(self,
            data,
            fast=None,
            slow=None,
            signal=None,
            drift=None,
            offset=None,
            dependencies=['high', 'low', 'close', 'volume'],
            **kwargs):
        fast = int(fast) if fast and fast > 0 else 34
        slow = int(slow) if slow and slow > 0 else 55
        signal = int(signal) if signal and signal > 0 else 13
        result, kvo_signal = kvo(copy.deepcopy(data['high']),
                                 copy.deepcopy(data['low']),
                                 copy.deepcopy(data['close']),
                                 copy.deepcopy(data['volume']),
                                 fast=fast,
                                 slow=slow,
                                 signal=signal,
                                 drift=drift,
                                 offset=offset,
                                 **kwargs)
        result = self._format(result, f"KVO_{fast}_{slow}_{signal}")
        kvo_signal = self._format(kvo_signal, f"KVOs_{fast}_{slow}_{signal}")
        return result, kvo_signal

    def LINRATIO(self,
                 data,
                 length=None,
                 offset=None,
                 category='equal',
                 dependencies=['long'],
                 **kwargs):

        length = int(length) if length and length > 0 else 5
        result = linratio(copy.deepcopy(data['long']),
                          length=length,
                          offset=offset,
                          **kwargs)
        return self._format(result, f"LINRATIO_{category}_{length}")

    def LRTCHG(self,
               data,
               length=None,
               offset=None,
               category='equal',
               dependencies=['long', 'openint'],
               **kwargs):
        length = int(length) if length and length > 0 else 5
        result = lrtichg(copy.deepcopy(data['long']),
                         copy.deepcopy(data['openint']),
                         length=length,
                         offset=offset,
                         **kwargs)
        return self._format(result, f"LRTCHG_{category}_{length}")

    def LSSENTI(self,
                data,
                length=None,
                offset=None,
                category='equal',
                dependencies=['long', 'short', 'openint'],
                **kwargs):
        length = int(length) if length and length > 0 else 5
        result = lssenti(copy.deepcopy(data['long']),
                         copy.deepcopy(data['short']),
                         copy.deepcopy(data['openint']),
                         length=length,
                         offset=offset,
                         **kwargs)
        return self._format(result, f"LSSENTI_{category}_{length}")

    def NIC(self,
            data,
            length=None,
            offset=None,
            category='equal',
            dependencies=['long', 'short'],
            **kwargs):
        length = int(length) if length and length > 0 else 5
        result = nic(copy.deepcopy(data['long']),
                     copy.deepcopy(data['short']),
                     length=length,
                     offset=offset,
                     **kwargs)
        return self._format(result, f"NIC_{category}_{length}")

    def NITC(self,
             data,
             length=None,
             offset=None,
             category='equal',
             dependencies=['long', 'short', 'openint'],
             **kwargs):
        length = int(length) if length and length > 0 else 5
        result = nitc(copy.deepcopy(data['long']),
                      copy.deepcopy(data['short']),
                      copy.deepcopy(data['openint']),
                      length=length,
                      offset=offset,
                      **kwargs)
        return self._format(result, f"NITC_{category}_{length}")

    def NIR(self,
            data,
            length=None,
            offset=None,
            category='equal',
            dependencies=['long', 'short'],
            **kwargs):
        length = int(length) if length and length > 0 else 5
        result = nir(copy.deepcopy(data['long']),
                     copy.deepcopy(data['short']),
                     length=length,
                     offset=offset,
                     **kwargs)
        return self._format(result, f"NIR_{category}_{length}")

    def NVI(self,
            data,
            length=None,
            initial=None,
            offset=None,
            dependencies=['close', 'volume'],
            **kwargs):
        length = int(length) if length and length > 0 else 1
        result = nvi(copy.deepcopy(data['close']),
                     copy.deepcopy(data['volume']),
                     length=length,
                     initial=initial,
                     offset=offset,
                     **kwargs)
        return self._format(result, f"NVI_{length}")

    def OBV(self,
            data,
            offset=None,
            dependencies=['close', 'volume'],
            **kwargs):
        result = obv(copy.deepcopy(data['close']),
                     copy.deepcopy(data['volume']),
                     offset=offset,
                     **kwargs)
        return self._format(result, f"OBV")

    def PVI(self,
            data,
            length=None,
            initial=None,
            offset=None,
            dependencies=['close', 'volume'],
            **kwargs):
        length = int(length) if length and length > 0 else 1
        result = pvi(copy.deepcopy(data['close']),
                     copy.deepcopy(data['volume']),
                     length=length,
                     initial=initial,
                     offset=offset,
                     **kwargs)
        return self._format(result, f"PVI_{length}")

    def PVOL(self,
             data,
             length=None,
             offset=None,
             dependencies=['close', 'volume'],
             **kwargs):
        result = pvol(copy.deepcopy(data['close']),
                      copy.deepcopy(data['volume']),
                      length=length,
                      offset=offset,
                      **kwargs)
        return self._format(result, f"PVOL")

    def PVT(self,
            data,
            drift=None,
            offset=None,
            dependencies=['close', 'volume'],
            **kwargs):
        result = pvt(copy.deepcopy(data['close']),
                     copy.deepcopy(data['volume']),
                     drift=drift,
                     offset=offset,
                     **kwargs)
        return self._format(result, f"PVT")

    def SINRATIO(self,
                 data,
                 length=None,
                 offset=None,
                 category='equal',
                 dependencies=['short'],
                 **kwargs):
        length = int(length) if length and length > 0 else 5
        result = sinratio(copy.deepcopy(data['short']),
                          length=length,
                          offset=offset,
                          **kwargs)
        return self._format(result, f"SINRATIO_{category}_{length}")

    def SRTCHG(self,
               data,
               length=None,
               offset=None,
               category='equal',
               dependencies=['short', 'openint'],
               **kwargs):
        length = int(length) if length and length > 0 else 5
        result = srtichg(copy.deepcopy(data['short']),
                         copy.deepcopy(data['openint']),
                         length=length,
                         offset=offset,
                         **kwargs)
        return self._format(result, f"SRTCHG_{category}_{length}")