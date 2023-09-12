# -*- encoding:utf-8 -*-
import numpy as np
import pandas as pd
from alphakit.const import *
from alphakit.factor import *
from alphakit.portfolio import *
from alphakit.data import *

from hermes.factors.base import FactorBase, LongCallMixin, ShortCallMixin
from jdwdata.RetrievalAPI import get_data_by_map


class FactorFormulaStock(FactorBase, LongCallMixin, ShortCallMixin):

    def __init__(self, data_format, **kwargs):
        __str__ = 'factor_formula_stock'
        self.category = 'Formula'
        self.name = '股票公式因子'
        self._data_format = data_format
        self._data = self.init_data(**kwargs) if 'end_date' in kwargs else None
        data = get_data_by_map(columns=BARRA_ALL_K,
                               begin_date=self.begin_date,
                               end_date=self.end_date,
                               method='ddb')
        self._risksizeindu = getdataset(data, BARRA_SIZEIND_K)

    def _init_self(self, **kwargs):
        pass

    def factor_formula1(self,
                        data=None,
                        dependencies=[
                            'dummy120_fst', 'vwap', 'sw1', 'ret',
                            'adjFactorVol', 'turnoverVol'
                        ],
                        window=30):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        vol = data['turnoverVol'] * data['adjFactorVol'] * dummy
        sw1 = data['sw1']
        ret = data['ret']
        vwap = data['vwap']
        factor = clear_by_cond(dfabs(ts_rank(dfabs(ts_rank(ret, 7)), 6)),
                               ts_max(vol, 4),
                               vdelta(rank(decay_linear(vwap, 3)), 4))
        factor = factor.where(factor != 0, factor + 0.1)
        factor = -factor.rolling(20, min_periods=10).mean()
        factor[np.isinf(factor)] = np.nan
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_formula1")

    def factor_formula2(self,
                        data=None,
                        dependencies=[
                            'dummy120_fst', 'highestPrice', 'sw1',
                            'turnoverVol', 'adjFactorVol', 'adjFactorPrice'
                        ],
                        window=30):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        vol = data['turnoverVol'] * data['adjFactorVol'] * dummy
        highestPrice = data['highestPrice'] * data['adjFactorPrice']
        factor = ts_max(corr(highestPrice, vol, 6), 5)
        factor = -factor.rolling(20, min_periods=10).mean()
        factor[np.isinf(factor)] = np.nan
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_formula2")

    def factor_formula3(self,
                        data=None,
                        dependencies=[
                            'dummy120_fst', 'sw1', 'closePrice', 'vwap',
                            'adjFactorPrice'
                        ],
                        window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        closePrice = data['closePrice']
        vwap = data['vwap']
        factor = -ts_max(vsub(closePrice, vwap), 1)
        factor = indfill_median(factor * dummy, sw1)
        return self._format(factor, "factor_formula3")

    def factor_formula4(self,
                        data=None,
                        dependencies=[
                            'dummy120_fst', 'sw1', 'closePrice', 'vwap',
                            'turnoverVol', 'adjFactorVol', 'adjFactorPrice'
                        ],
                        window=10):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        closePrice = data['closePrice'] * data['adjFactorPrice']
        volume = data['turnoverVol'] * data['adjFactorVol']
        vwap = data['vwap']
        factor = vsub(ts_argmin(vdiv(closePrice, vwap), 10),
                      ts_stdev(volume, 10))
        factor[np.isinf(factor)] = np.nan
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_formula4")

    def factor_formula5(self,
                        data=None,
                        dependencies=[
                            'dummy120_fst', 'sw1', 'closePrice', 'turnoverVol',
                            'adjFactorVol', 'adjFactorPrice'
                        ],
                        window=40):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        closePrice = data['closePrice'] * data['adjFactorPrice']
        vol = data['turnoverVol'] * data['adjFactorVol']
        factor = (vmul(
            ts_rank(vdiv(vol, sma(vol, 20)), 20),
            ts_rank(vneg(vdelta(closePrice, 7)), 8),
        ) + 1)
        factor = factor.rolling(20, min_periods=10).mean()
        factor[np.isinf(factor)] = np.nan
        factor = indfill_median(factor * dummy, sw1)
        return self._format(factor, "factor_formula5")

    def factor_formula6(self,
                        data=None,
                        dependencies=[
                            'dummy120_fst', 'sw1', 'closePrice', 'turnoverVol',
                            'adjFactorVol', 'adjFactorPrice', 'ret',
                            'lowestPrice', 'openPrice'
                        ],
                        window=10):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        ret = data['ret']
        lowestPrice = data['lowestPrice']
        openPrice = data['openPrice']
        vol = data['turnoverVol']
        factor = clear_by_cond(vsub(ret, lowestPrice), mean2(vol, openPrice),
                               sma(vol, 3))
        factor = -factor.where(factor != 0, factor + 0.1)
        factor[np.isinf(factor)] = np.nan
        factor = -np.square(factor_score(factor * dummy, 1))
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_formula6")