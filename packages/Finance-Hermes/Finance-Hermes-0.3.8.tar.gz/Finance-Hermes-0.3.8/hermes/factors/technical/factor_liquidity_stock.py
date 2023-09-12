# -*- encoding:utf-8 -*-
import numpy as np
import pandas as pd
from alphakit.const import *
from alphakit.factor import *
from alphakit.portfolio import *
from alphakit.data import *

from hermes.factors.base import FactorBase, LongCallMixin, ShortCallMixin
from jdwdata.RetrievalAPI import get_data_by_map


class FactorLiquidityStock(FactorBase, LongCallMixin, ShortCallMixin):

    def __init__(self, data_format, **kwargs):
        __str__ = 'factor_liquidity_stock'
        self.category = 'Liquidity'
        self.name = '股票流动性'
        self._data_format = data_format
        self._data = self.init_data(**kwargs) if 'end_date' in kwargs else None
        data = get_data_by_map(columns=BARRA_ALL_K,
                               begin_date=self.begin_date,
                               end_date=self.end_date,
                               method='ddb')
        self._risksizeindu = getdataset(data, BARRA_SIZEIND_K)

    def _init_self(self, **kwargs):
        pass

    def factor_liquid1(
            self,
            data=None,
            dependencies=['dummy120_fst', 'ffancy_bcvp05M20D', 'sw1'],
            window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        factor = data['ffancy_bcvp05M20D']
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_liquid1")

    def factor_liquid2(
            self,
            data=None,
            dependencies=['dummy120_fst', 'ffancy_taEntropy', 'sw1'],
            window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        factor = data['ffancy_taEntropy']
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_liquid2")

    def factor_liquid3(self,
                       data=None,
                       dependencies=[
                           'dummy120_fst', 'turnoverVol', 'sw1', 'adjFactorVol'
                       ],
                       window=3):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        adjFactorVol = data['adjFactorVol']
        vol = data['turnoverVol'] * adjFactorVol * dummy
        vol[vol <= 0] = np.nan
        log_val = np.log(vol)
        factor = -log_val.rolling(3, min_periods=1).sum() / 3
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_liquid3")

    def factor_liquid4(self,
                       data=None,
                       dependencies=['dummy120_fst', 'turnoverValue', 'sw1'],
                       window=60):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        vol = data['turnoverVol'] * dummy
        vol[vol <= 0] = np.nan
        log_val = np.log(vol)
        factor = -log_val.rolling(60, min_periods=20).std()
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_liquid4")

    def factor_liquid5(self,
                       data=None,
                       dependencies=['dummy120_fst', 'turnoverValue', 'sw1'],
                       window=120):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        vol = data['turnoverVol'] * dummy
        vol[vol <= 0] = np.nan
        log_val = np.log(vol)
        factor = -log_val.rolling(120, min_periods=30).std()
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_liquid5")

    def factor_liquid6(self,
                       data=None,
                       dependencies=['dummy120_fst', 'fuqer_Volumn3M', 'sw1'],
                       window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        factor = -data['fuqer_Volumn3M']
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_liquid6")

    def factor_liquid7(self,
                       data=None,
                       dependencies=['dummy120_fst', 'fuqer_DAVOL5', 'sw1'],
                       window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        factor = -data['fuqer_DAVOL5']
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_liquid7")

    def factor_liquid8(self,
                       data=None,
                       dependencies=[
                           'dummy120_fst', 'turnoverValue', 'turnoverVol',
                           'ret', 'sw1'
                       ],
                       window=240):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        ret = data['ret']
        val = data['turnoverValue']
        vol = data['turnoverVol']
        ret[vol <= 0 | vol.isna()] = np.nan
        val[vol <= 0 | vol.isna()] = np.nan
        vol[vol <= 0 | vol.isna()] = np.nan
        illiq = abs(ret) / val
        factor = -illiq.rolling(240, min_periods=5).std()
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_liquid8")