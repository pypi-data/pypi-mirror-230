# -*- encoding:utf-8 -*-
import numpy as np
import pandas as pd
from alphakit.const import *
from alphakit.factor import *
from alphakit.portfolio import *
from alphakit.data import *

from hermes.factors.base import FactorBase, LongCallMixin, ShortCallMixin
from jdwdata.RetrievalAPI import get_data_by_map


class FactorNorth(FactorBase, LongCallMixin, ShortCallMixin):

    def __init__(self, data_format, **kwargs):
        __str__ = 'factor_north'
        self.category = 'North'
        self.name = '北向资金'
        self._data_format = data_format
        self._data = self.init_data(**kwargs) if 'end_date' in kwargs else None
        data = get_data_by_map(columns=BARRA_ALL_K,
                               begin_date=self.begin_date,
                               end_date=self.end_date,
                               method='ddb')
        self._risksizeindu = getdataset(data, BARRA_SIZEIND_K)

    def _init_self(self, **kwargs):
        pass

    def north_sub1(self, data, halflife):
        t = pd.DataFrame(data)
        return t.ewm(halflife=halflife, axis=0).mean().iloc[-1, :].values

    def factor_north1(
            self,
            data=None,
            dependencies=['dummy120_fst', 'ffancy_hkHoldVolChgB120', 'sw1'],
            window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        factor = data['ffancy_hkHoldVolChgB120']
        factor = indfill_median(factor * dummy, sw1)
        factor.fillna(method="pad", inplace=True)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_north1")

    def factor_north2(
            self,
            data=None,
            dependencies=['dummy120_fst', 'sw1', 'ffancy_hkHoldRatioB'],
            window=1):
        data = self._data if data is None else data
        factor = data['ffancy_hkHoldRatioB']
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        factor = indfill_median(factor * dummy, sw1)
        factor.fillna(method='pad', inplace=True)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_north2")

    def factor_north3(self,
                      data=None,
                      dependencies=['dummy120_fst', 'sw1', 'partyPct'],
                      window=120):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        holdpct = data['partyPct']
        sw1 = data['sw1']
        factor = holdpct.rolling(120, min_periods=40).rank(pct=True)
        factor = indfill_median(factor * dummy, sw1)
        factor.fillna(method='pad', inplace=True)
        return self._format(factor, "factor_north3")