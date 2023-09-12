# -*- encoding:utf-8 -*-
from hermes.factors.base import FactorBase, LongCallMixin, ShortMixin
from hermes.factors.alphax.core.alpha191 import *


class FactorAlpha191(FactorBase, LongCallMixin, ShortMixin):

    def __init__(self, **kwargs):
        __str__ = 'alpha191'
        self.category = 'alpha191'

    def _init_self(self, **kwargs):
        pass

    def Alpha191_2(self,
                   data,
                   offset=None,
                   dependencies=['close', 'high', 'low'],
                   **kwargs):
        result = alpha191_2(data['close'],
                            data['low'],
                            data['high'],
                            offset=offset,
                            **kwargs)
        return self._format(result, f"Alpha191_2")

    def Alpha191_6(self,
                   data,
                   length=None,
                   offset=None,
                   dependencies=['open', 'high'],
                   **kwargs):
        length = int(length) if length and length > 0 else 4
        result = alpha191_6(data['open'],
                            data['high'],
                            length=length,
                            offset=offset,
                            **kwargs)
        return self._format(result, f"Alpha191_6_{length}")

    def Alpha191_12(self,
                    data,
                    length=None,
                    offset=None,
                    dependencies=['close', 'open', 'vwap'],
                    **kwargs):
        length = int(length) if length and length > 0 else 10
        result = alpha191_12(data['close'],
                             data['open'],
                             data['vwap'],
                             length=length,
                             offset=offset,
                             **kwargs)
        return self._format(result, f"Alpha191_12_{length}")

    def Alpha191_13(self,
                    data,
                    length=None,
                    offset=None,
                    dependencies=['high', 'low', 'vwap'],
                    **kwargs):
        length = int(length) if length and length > 0 else 10
        result = alpha191_13(data['high'],
                             data['low'],
                             data['vwap'],
                             length=length,
                             offset=offset,
                             **kwargs)
        return self._format(result, f"Alpha191_13_{length}")

    def Alpha191_14(self,
                    data,
                    length=None,
                    offset=None,
                    dependencies=['close'],
                    **kwargs):
        length = int(length) if length and length > 0 else 5
        result = alpha191_14(data['close'],
                             length=length,
                             offset=offset,
                             **kwargs)
        return self._format(result, f"Alpha191_14_{length}")

    def Alpha191_15(self,
                    data,
                    length=None,
                    offset=None,
                    dependencies=['close', 'open'],
                    **kwargs):
        length = int(length) if length and length > 0 else 5
        result = alpha191_15(data['close'],
                             data['open'],
                             length=length,
                             offset=offset,
                             **kwargs)
        return self._format(result, f"Alpha191_15_{length}")

    def Alpha191_18(self,
                    data,
                    length=None,
                    offset=None,
                    dependencies=['close'],
                    **kwargs):
        length = int(length) if length and length > 0 else 5
        result = alpha191_18(data['close'],
                             length=length,
                             offset=offset,
                             **kwargs)
        return self._format(result, f"Alpha191_18_{length}")

    def Alpha191_20(self,
                    data,
                    length=None,
                    offset=None,
                    dependencies=['close'],
                    **kwargs):
        length = int(length) if length and length > 0 else 5
        result = alpha191_20(data['close'],
                             length=length,
                             offset=offset,
                             **kwargs)
        return self._format(result, f"Alpha191_20_{length}")

    def Alpha191_24(self,
                    data,
                    length=None,
                    offset=None,
                    dependencies=['close'],
                    **kwargs):
        length = int(length) if length and length > 0 else 5
        result = alpha191_24(data['close'],
                             length=length,
                             offset=offset,
                             **kwargs)
        return self._format(result, f"Alpha191_24_{length}")

    def Alpha191_27(self,
                    data,
                    length=None,
                    offset=None,
                    dependencies=['close'],
                    **kwargs):
        length = int(length) if length and length > 0 else 5
        result = alpha191_27(data['close'],
                             length=length,
                             offset=offset,
                             **kwargs)
        return self._format(result, f"Alpha191_27_{length}")

    def Alpha191_29(self,
                    data,
                    length=None,
                    offset=None,
                    dependencies=['close', 'volume'],
                    **kwargs):
        length = int(length) if length and length > 0 else 5
        result = alpha191_29(data['close'],
                             data['volume'],
                             length=length,
                             offset=offset,
                             **kwargs)
        return self._format(result, f"Alpha191_29_{length}")

    def Alpha191_32(self,
                    data,
                    length=None,
                    offset=None,
                    dependencies=['close', 'high', 'volume'],
                    **kwargs):
        length = int(length) if length and length > 0 else 5
        result = alpha191_32(data['close'],
                             data['high'],
                             data['volume'],
                             length=length,
                             offset=offset,
                             **kwargs)
        return self._format(result, f"Alpha191_32_{length}")

    def Alpha191_34(self,
                    data,
                    length=None,
                    offset=None,
                    dependencies=['close'],
                    **kwargs):
        length = int(length) if length and length > 0 else 5
        result = alpha191_34(data['close'],
                             length=length,
                             offset=offset,
                             **kwargs)
        return self._format(result, f"Alpha191_34_{length}")

    def Alpha191_41(self,
                    data,
                    length=None,
                    diff=None,
                    offset=None,
                    dependencies=['vwap'],
                    **kwargs):
        length = int(length) if length and length > 0 else 5
        diff = diff if diff and diff > 0 else 5
        result = alpha191_41(data['vwap'],
                             length=length,
                             diff=diff,
                             offset=offset,
                             **kwargs)
        return self._format(result, f"Alpha191_41_{length}_{diff}")

    def Alpha191_42(self,
                    data,
                    length=None,
                    offset=None,
                    dependencies=['close', 'high', 'volume'],
                    **kwargs):
        length = int(length) if length and length > 0 else 3
        result = alpha191_42(data['close'],
                             data['high'],
                             data['volume'],
                             length=length,
                             offset=offset,
                             **kwargs)
        return self._format(result, f"Alpha191_42_{length}")

    def Alpha191_46(self,
                    data,
                    length=None,
                    offset=None,
                    dependencies=['close'],
                    **kwargs):
        length = int(length) if length and length > 0 else 5
        result = alpha191_46(data['close'],
                             length=length,
                             offset=offset,
                             **kwargs)
        return self._format(result, f"Alpha191_46_{length}")

    def Alpha191_47(self,
                    data,
                    length=None,
                    offset=None,
                    dependencies=['close', 'high', 'low'],
                    **kwargs):
        length = int(length) if length and length > 0 else 5
        result = alpha191_47(data['close'],
                             data['high'],
                             data['low'],
                             length=length,
                             offset=offset,
                             **kwargs)
        return self._format(result, f"Alpha191_47_{length}")

    def Alpha191_52(self,
                    data,
                    length=None,
                    offset=None,
                    dependencies=['close', 'high', 'low'],
                    **kwargs):
        length = int(length) if length and length > 0 else 5
        result = alpha191_52(data['close'],
                             data['high'],
                             data['low'],
                             length=length,
                             offset=offset,
                             **kwargs)
        return self._format(result, f"Alpha191_52_{length}")

    def Alpha191_57(self,
                    data,
                    length=None,
                    offset=None,
                    dependencies=['close', 'high', 'low'],
                    **kwargs):
        length = int(length) if length and length > 0 else 5
        result = alpha191_57(data['close'],
                             data['high'],
                             data['low'],
                             length=length,
                             offset=offset,
                             **kwargs)
        return self._format(result, f"Alpha191_57_{length}")

    def Alpha191_60(self,
                    data,
                    length=None,
                    offset=None,
                    dependencies=['close', 'high', 'low', 'volume'],
                    **kwargs):
        length = int(length) if length and length > 0 else 5
        result = alpha191_60(data['close'],
                             data['high'],
                             data['low'],
                             data['volume'],
                             length=length,
                             offset=offset,
                             **kwargs)
        return self._format(result, f"Alpha191_60_{length}")

    def Alpha191_65(self,
                    data,
                    length=None,
                    offset=None,
                    dependencies=['close'],
                    **kwargs):
        length = int(length) if length and length > 0 else 6
        result = alpha191_65(data['close'],
                             length=length,
                             offset=offset,
                             **kwargs)
        return self._format(result, f"Alpha191_65_{length}")

    def Alpha191_66(self,
                    data,
                    length=None,
                    offset=None,
                    dependencies=['close'],
                    **kwargs):
        length = int(length) if length and length > 0 else 6
        result = alpha191_66(data['close'],
                             length=length,
                             offset=offset,
                             **kwargs)
        return self._format(result, f"Alpha191_66_{length}")

    def Alpha191_68(self,
                    data,
                    length=None,
                    offset=None,
                    dependencies=['high', 'low', 'volume'],
                    **kwargs):
        length = int(length) if length and length > 0 else 6
        result = alpha191_68(data['high'],
                             data['low'],
                             data['volume'],
                             length=length,
                             offset=offset,
                             **kwargs)
        return self._format(result, f"Alpha191_68_{length}")

    def Alpha191_70(self,
                    data,
                    length=None,
                    offset=None,
                    dependencies=['values'],
                    **kwargs):
        length = int(length) if length and length > 0 else 6
        result = alpha191_70(data['values'],
                             length=length,
                             offset=offset,
                             **kwargs)
        return self._format(result, f"Alpha191_70_{length}")