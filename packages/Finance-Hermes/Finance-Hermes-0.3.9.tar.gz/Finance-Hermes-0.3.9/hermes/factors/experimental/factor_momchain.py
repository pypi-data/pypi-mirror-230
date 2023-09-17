# -*- encoding:utf-8 -*-
import copy
from hermes.factors.base import FactorBase, LongCallMixin, ShortMixin
from hermes.factors.experimental.core.momchain import *
from hermes.factors.experimental.core.dissection import factor_run as disscetion_run


class FactorMomchain(FactorBase, LongCallMixin, ShortMixin):

    def __init__(self, **kwargs):
        __str__ = 'momchain'
        self.category = 'momchain'

    def _init_self(self, **kwargs):
        pass

    def DOWNVOLATILITY(self,
                       data,
                       length=None,
                       offset=None,
                       dependencies=['close'],
                       **kwargs):
        length = int(length) if length and length > 0 else 4

        result = down_volatility(copy.deepcopy(data['close']),
                                 length=length,
                                 offset=offset,
                                 **kwargs)
        return self._format(result, f"DOWNVOLATILITY_{length}")

    def FLOWINRATIO(self,
                    data,
                    length=None,
                    offset=None,
                    dependencies=['close', 'values'],
                    **kwargs):
        length = int(length) if length and length > 0 else 4

        result = flowin_ratio(copy.deepcopy(data['close']),
                              copy.deepcopy(data['values']),
                              length=length,
                              offset=offset,
                              **kwargs)
        return self._format(result, f"FLOWINRATIO_{length}")

    def RHHI(self,
             data,
             length=None,
             offset=None,
             dependencies=['values'],
             **kwargs):
        length = int(length) if length and length > 0 else 2

        result = rhhi(copy.deepcopy(data['values']),
                      length=length,
                      offset=offset,
                      **kwargs)

        return self._format(result, f"RHHI_{length}")

    def RETD(self,
             data,
             length=None,
             offset=None,
             dependencies=['close'],
             **kwargs):
        length = int(length) if length and length > 0 else 2

        result = retd(copy.deepcopy(data['close']),
                      length=length,
                      offset=offset,
                      **kwargs)

        return self._format(result, f"RETD_{length}")

    def VRETD(self,
              data,
              length=None,
              offset=None,
              dependencies=['close', 'values'],
              **kwargs):
        length = int(length) if length and length > 0 else 2

        result = vretd(copy.deepcopy(data['close']),
                       copy.deepcopy(data['values']),
                       length=length,
                       offset=offset,
                       **kwargs)

        return self._format(result, f"VRETD_{length}")

    def VVOL(self,
             data,
             length=None,
             offset=None,
             dependencies=['values'],
             **kwargs):
        length = int(length) if length and length > 0 else 2

        result = vvol(copy.deepcopy(data['values']),
                      length=length,
                      offset=offset,
                      **kwargs)

        return self._format(result, f"VVOL_{length}")

    def VSKEW(self,
              data,
              length=None,
              offset=None,
              dependencies=['values'],
              **kwargs):
        length = int(length) if length and length > 0 else 2

        result = vskew(copy.deepcopy(data['values']),
                       length=length,
                       offset=offset,
                       **kwargs)

        return self._format(result, f"VSKEW_{length}")

    def VKURT(self,
              data,
              length=None,
              offset=None,
              dependencies=['values'],
              **kwargs):
        length = int(length) if length and length > 0 else 2

        result = vkurt(copy.deepcopy(data['values']),
                       length=length,
                       offset=offset,
                       **kwargs)

        return self._format(result, f"VKURT_{length}")

    def OPTIMALMOM(self,
                   data,
                   length=None,
                   offset=None,
                   dependencies=['close'],
                   **kwargs):
        length = int(length) if length and length > 0 else 5

        result = optimal_mom(copy.deepcopy(data['close']),
                             length=length,
                             offset=offset,
                             **kwargs)

        return self._format(result, f"OPTIMALMOM_{length}")

    def CROSSSTART(self,
                   data,
                   length=None,
                   offset=None,
                   dependencies=['close', 'index_close'],
                   **kwargs):
        length = int(length) if length and length > 0 else 5

        result = cross_start(copy.deepcopy(data['close']),
                             copy.deepcopy(data['index_close']),
                             length=length,
                             offset=offset,
                             **kwargs)
        return self._format(result, f"CROSSSTART_{length}")

    def YELLORPS(self,
                 data,
                 long_length=None,
                 middle_length=None,
                 short_length=None,
                 long_ratio=None,
                 middle_ratio=None,
                 short_ratio=None,
                 offset=None,
                 dependencies=['close'],
                 **kwargs):
        short_length = int(
            short_length) if short_length and short_length > 0 else 10
        middle_length = int(
            middle_length) if middle_length and middle_length > 0 else 20
        long_length = int(
            long_length) if long_length and long_length > 0 else 30

        long_ratio = float(
            long_ratio) if long_ratio and long_ratio > 0 else 0.5
        middle_ratio = float(
            middle_ratio) if middle_ratio and middle_ratio > 0 else 0.3
        short_ratio = float(
            short_ratio) if short_ratio and short_ratio > 0 else 0.2

        result = yello_rps(copy.deepcopy(data['close']),
                           long_length=long_length,
                           middle_length=middle_length,
                           short_length=short_length,
                           long_ratio=long_ratio,
                           middle_ratio=middle_ratio,
                           short_ratio=short_ratio,
                           offset=offset,
                           **kwargs)
        str_long_ratio = str(long_ratio).replace('.', '')
        str_middle_ratio = str(middle_ratio).replace('.', '')
        str_short_ratio = str(short_ratio).replace('.', '')
        return self._format(
            result,
            f"YELLORPS_{long_length}_{middle_length}_{short_length}_{str_long_ratio}_{str_middle_ratio}_{str_short_ratio}"
        )

    def DISSECTION(self,
                   data,
                   length=None,
                   threshold=None,
                   offset=None,
                   dependencies=['close', 'deal', 'volume'],
                   **kwargs):

        ##因子参数默认值设置，主要用于下面因子命名
        length = int(length) if length and length > 0 else 10
        threshold = int(threshold) if threshold and threshold > 0 else 10000
        result = disscetion_run(data['close'],
                                data['deal'],
                                data['volume'],
                                length=length,
                                threshold=threshold,
                                offset=offset,
                                **kwargs)

        return self._format(result, f"DISSECTION_{length}_{threshold}")
