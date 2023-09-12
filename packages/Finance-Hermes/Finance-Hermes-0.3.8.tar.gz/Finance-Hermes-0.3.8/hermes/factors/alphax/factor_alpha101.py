# -*- encoding:utf-8 -*-
from hermes.factors.base import FactorBase, LongCallMixin
from hermes.factors.alphax.core.alpha101 import *


class FactorAlpha101(FactorBase, LongCallMixin, ShortMixin):

    def __init__(self, **kwargs):
        __str__ = 'alpha101'
        self.category = 'alpha101'

    def _init_self(self, **kwargs):
        pass

    def Alpha101_4(self,
                   data,
                   length=None,
                   offset=None,
                   dependencies=['low'],
                   **kwargs):
        length = int(length) if length and length > 0 else 6
        result = alpha101_4(data['low'],
                            length=length,
                            offset=offset,
                            **kwargs)
        return self._format(result, f"Alpha101_4_{length}")

    def Alpha101_5(self,
                   data,
                   length=None,
                   offset=None,
                   dependencies=['open', 'vwap'],
                   **kwargs):
        length = length if length and length > 0 else 10
        offset = int(offset) if isinstance(offset, int) else 0

        result = alpha101_5(data['open'],
                            data['vwap'],
                            length=length,
                            offset=offset,
                            **kwargs)
        return self._format(result, f"Alpha101_5_{length}")

    def Alpha101_11(self,
                    data,
                    length=None,
                    periods=None,
                    offset=None,
                    dependencies=['open', 'vwap', 'volume'],
                    **kwargs):
        length = length if length and length > 0 else 3
        periods = periods if periods and periods > 0 else 3
        offset = int(offset) if isinstance(offset, int) else 0

        result = alpha101_11(data['open'],
                             data['vwap'],
                             data['volume'],
                             length=length,
                             offset=offset,
                             **kwargs)
        return self._format(result, f"Alpha101_11_{length}")

    def Alpha101_12(self,
                    data,
                    length=None,
                    periods=None,
                    offset=None,
                    dependencies=['close', 'volume'],
                    **kwargs):
        length = length if length and length > 0 else 2
        offset = int(offset) if isinstance(offset, int) else 0

        result = alpha101_12(data['close'],
                             data['volume'],
                             length=length,
                             offset=offset,
                             **kwargs)
        return self._format(result, f"Alpha101_12_{length}")

    def Alpha101_19(self,
                    data,
                    fast=None,
                    slow=None,
                    offset=None,
                    dependencies=['close', 'returns'],
                    **kwargs):
        fast = fast if fast and fast > 0 else 7
        slow = slow if slow and slow > 0 else 10
        offset = int(offset) if isinstance(offset, int) else 0

        result = alpha101_12(data['close'],
                             data['returns'],
                             fast=fast,
                             slow=slow,
                             offset=offset,
                             **kwargs)
        return self._format(result, f"Alpha101_12_{fast}_{slow}")

    def Alpha101_23(self,
                    data,
                    fast=None,
                    slow=None,
                    offset=None,
                    dependencies=['high'],
                    **kwargs):
        slow = slow if slow and slow > 0 else 20
        fast = fast if fast and fast > 0 else 2
        offset = int(offset) if isinstance(offset, int) else 0

        result = alpha101_23(data['high'],
                             fast=fast,
                             slow=slow,
                             offset=offset,
                             **kwargs)
        return self._format(result, f"Alpha101_12_{fast}_{slow}")

    def Alpha101_52(self,
                    data,
                    fast=None,
                    slow=None,
                    lw=None,
                    sw=None,
                    tsw=None,
                    offset=None,
                    dependencies=['low', 'returns', 'volume'],
                    **kwargs):
        fast = fast if fast and fast > 0 else 8
        slow = slow if slow and slow > 0 else 8
        lw = lw if lw and lw > 0 else 20
        sw = sw if sw and sw > 0 else 18
        tsw = tsw if tsw and tsw > 0 else 8
        offset = int(offset) if isinstance(offset, int) else 0

        result = alpha101_52(data['high'],
                             data['returns'],
                             data['volume'],
                             fast=fast,
                             slow=slow,
                             offset=offset,
                             **kwargs)
        return self._format(result,
                            f"Alpha101_12_{fast}_{slow}_{lw}_{sw}_{tsw}")

    def Alpha101_53(self,
                    data,
                    length=None,
                    offset=None,
                    dependencies=['close', 'low', 'high'],
                    **kwargs):
        length = length if length and length > 0 else 9
        offset = int(offset) if isinstance(offset, int) else 0

        result = alpha101_53(data['close'],
                             data['low'],
                             data['high'],
                             length=length,
                             offset=offset,
                             **kwargs)
        return self._format(result, f"Alpha101_53_{length}")

    def Alpha101_54(self,
                    data,
                    length=None,
                    offset=None,
                    dependencies=['close', 'low', 'high', 'open'],
                    **kwargs):
        length = length if length and length > 0 else 5
        offset = int(offset) if isinstance(offset, int) else 0

        result = alpha101_54(data['close'],
                             data['low'],
                             data['high'],
                             data['open'],
                             length=length,
                             offset=offset,
                             **kwargs)
        return self._format(result, f"Alpha101_54_{length}")

    def Alpha101_84(self,
                    data,
                    max_length=None,
                    rank_length=None,
                    diff_length=None,
                    offset=None,
                    dependencies=['vwap', 'close'],
                    **kwargs):
        max_length = max_length if max_length and max_length > 0 else 15
        rank_length = rank_length if rank_length and rank_length > 0 else 20
        diff_length = diff_length if diff_length and diff_length > 0 else 6
        offset = int(offset) if isinstance(offset, int) else 0

        result = alpha101_84(data['vwap'],
                             data['close'],
                             max_length=max_length,
                             rank_length=rank_length,
                             diff_length=diff_length,
                             offset=offset,
                             **kwargs)
        return self._format(
            result, f"Alpha101_53_{max_length}_{rank_length}_{diff_length}")
