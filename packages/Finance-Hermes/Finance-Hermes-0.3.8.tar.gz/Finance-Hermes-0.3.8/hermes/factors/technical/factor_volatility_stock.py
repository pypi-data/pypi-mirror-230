# -*- encoding:utf-8 -*-
import numpy as np
import pandas as pd
from alphakit.const import *
from alphakit.factor import *
from alphakit.portfolio import *
from alphakit.data import *

from hermes.factors.base import FactorBase, LongCallMixin, ShortCallMixin
from jdwdata.RetrievalAPI import get_data_by_map


class FactorVolatilityStock(FactorBase, LongCallMixin, ShortCallMixin):

    def __init__(self, data_format, **kwargs):
        __str__ = 'factor_volatility_stock'
        self.category = 'Volatility'
        self.name = '股票波动率'
        self._data_format = data_format
        self._data = self.init_data(**kwargs) if 'end_date' in kwargs else None
        data = get_data_by_map(columns=BARRA_ALL_K,
                               begin_date=self.begin_date,
                               end_date=self.end_date,
                               method='ddb')
        self._risksizeindu = getdataset(data, BARRA_SIZEIND_K)

    def _init_self(self, **kwargs):
        pass

    def bollbais(self, invar, n, m):
        ma = invar.rolling(n, min_periods=1).mean()
        ma[ma <= 0] = np.nan
        std = invar.rolling(n, min_periods=3).std()
        std[std == 0] = np.nan
        boll_cls2up = invar / (ma + 2 * std) - 1
        boll_cls2dow = invar / (ma - 2 * std) - 1
        boll_cls2up[np.isinf(boll_cls2up)] = np.nan
        boll_cls2dow[np.isinf(boll_cls2dow)] = np.nan
        boll_cls2up_pnd = boll_cls2up.rolling(m, min_periods=1).sum()
        boll_cls2dow_pnd = boll_cls2dow.rolling(m, min_periods=1).sum()
        return boll_cls2up_pnd, boll_cls2dow_pnd

    def dma(self, invar, n, m):
        ma = invar.rolling(n, min_periods=1).mean()
        ma[ma <= 0] = np.nan
        testvar_dma = (invar - ma) / ma
        testvar_dma_pnd = testvar_dma.rolling(m, min_periods=1).sum()
        return testvar_dma_pnd

    def factor_vol1(self,
                    data=None,
                    dependencies=['dummy120_fst', 'fuqer_ACD20', 'sw1'],
                    window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        factor = -data['fuqer_ACD20']
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_vol1")

    def factor_vol2(self,
                    data=None,
                    dependencies=[
                        'dummy120_fst', 'closePrice', 'sw1', 'adjFactorPrice'
                    ],
                    window=15):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        adjFactorPrice = data['adjFactorPrice']
        closePrice = data['closePrice'] * dummy * adjFactorPrice
        closePrice[closePrice <= 0] = np.nan
        _, factor = self.bollbais(closePrice, 10, 1)
        factor = -indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_vol2")

    def factor_vol3(self,
                    data=None,
                    dependencies=['dummy120_fst', 'ffancy_upp01M20D', 'sw1'],
                    window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        factor = data['ffancy_upp01M20D']
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_vol3")

    def factor_vol4(self,
                    data=None,
                    dependencies=[
                        'dummy120_fst', 'closePrice', 'adjFactorPrice', 'sw1'
                    ],
                    window=30):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        adjFactorPrice = data['adjFactorPrice']
        closePrice = data['closePrice'] * dummy * adjFactorPrice
        closePrice[closePrice <= 0] = np.nan
        _, factor = self.bollbais(closePrice, 20, 5)
        factor = -indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_vol4")

    def factor_vol5(self,
                    data=None,
                    dependencies=[
                        'dummy120_fst', 'turnoverVol', 'sw1', 'adjFactorVol'
                    ],
                    window=120):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        adjFactorVol = data['adjFactorVol']
        vol = data['turnoverVol'] * dummy * adjFactorVol
        sw1 = data['sw1']
        factor = -vol.rolling(20, min_periods=10).std() / vol.rolling(
            120, min_periods=30).std()
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_vol5")

    def factor_vol6(self,
                    data=None,
                    dependencies=[
                        'dummy120_fst', 'closePrice', 'adjFactorPrice', 'sw1'
                    ],
                    window=65):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        adjFactorPrice = data['adjFactorPrice']
        closePrice = data['closePrice'] * dummy * adjFactorPrice
        closePrice[closePrice <= 0] = np.nan
        _, factor = self.bollbais(closePrice, 60, 1)
        factor = -indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_vol6")

    def factor_vol7(self,
                    data=None,
                    dependencies=[
                        'dummy120_fst', 'turnoverRate', 'adjFactorPrice', 'sw1'
                    ],
                    window=10):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        turnoverRate = data['turnoverRate'] * dummy
        factor = -turnoverRate.rolling(10, min_periods=5).std()
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_vol7")

    def factor_vol8(self,
                    data=None,
                    dependencies=[
                        'dummy120_fst', 'closePrice', 'adjFactorPrice', 'sw1'
                    ],
                    window=45):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        adjFactorPrice = data['adjFactorPrice']
        closePrice = data['closePrice'] * dummy * adjFactorPrice
        closePrice[closePrice <= 0] = np.nan
        factor, _ = self.bollbais(closePrice, 20, 20)
        factor = -indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_vol8")

    def factor_vol9(self,
                    data=None,
                    dependencies=['dummy120_fst', 'turnoverRate', 'sw1'],
                    window=90):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        turnoverRate = data['turnoverRate'] * dummy
        pnd = turnoverRate.rolling(90, min_periods=1).sum() / 90
        my_std = turnoverRate.rolling(90, min_periods=30).std()
        factor = pnd / my_std
        factor[np.isinf(factor)] = np.nan
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_vol9")

    def factor_vol10(self,
                     data=None,
                     dependencies=[
                         'dummy120_fst', 'closePrice', 'adjFactorPrice', 'sw1'
                     ],
                     window=30):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        adjFactorPrice = data['adjFactorPrice']
        closePrice = data['closePrice'] * dummy * adjFactorPrice
        closePrice[closePrice <= 0] = np.nan
        factor, _ = self.bollbais(closePrice, 20, 5)
        factor = -indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_vol10")

    def factor_vol11(self,
                     data=None,
                     dependencies=[
                         'dummy120_fst', 'closePrice', 'adjFactorPrice', 'sw1'
                     ],
                     window=245):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        adjFactorPrice = data['adjFactorPrice']
        closePrice = data['closePrice'] * dummy * adjFactorPrice
        closePrice[closePrice <= 0] = np.nan
        factor, _ = self.bollbais(closePrice, 240, 1)
        factor = -indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_vol11")

    def factor_vol12(self,
                     data=None,
                     dependencies=[
                         'dummy120_fst', 'closePrice', 'adjFactorPrice', 'sw1'
                     ],
                     window=80):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        adjFactorPrice = data['adjFactorPrice']
        closePrice = data['closePrice'] * dummy * adjFactorPrice
        closePrice[closePrice <= 0] = np.nan
        factor, _ = self.bollbais(closePrice, 60, 10)
        factor = -indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_vol12")

    def factor_vol13(self,
                     data=None,
                     dependencies=[
                         'dummy120_fst', 'highestPrice', 'sw1', 'lowestPrice'
                     ],
                     window=10):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        lowp = data['lowestPrice']
        highp = data['highestPrice']
        lowp[lowp <= 0] = np.nan
        price_range = highp / lowp
        factor = -price_range.rolling(10, min_periods=5).std()
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_vol13")

    def factor_vol14(self,
                     data=None,
                     dependencies=['dummy120_fst', 'turnoverRate', 'sw1'],
                     window=90):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        turnoverRate = data['turnoverRate']
        factor = -turnoverRate.rolling(90, min_periods=30).std()
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_vol14")

    def factor_vol15(self,
                     data=None,
                     dependencies=['dummy120_fst', 'fuqer_DBCD', 'sw1'],
                     window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        factor = -data['fuqer_DBCD']
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_vol15")

    def factor_vol16(self,
                     data=None,
                     dependencies=['dummy120_fst', 'fuqer_MassIndex', 'sw1'],
                     window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        factor = -data['fuqer_MassIndex']
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_vol16")

    def factor_vol17(self,
                     data=None,
                     dependencies=['dummy120_fst', 'fuqer_UOS', 'sw1'],
                     window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        factor = -data['fuqer_UOS']
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_vol17")

    def factor_vol18(self,
                     data=None,
                     dependencies=['dummy120_fst', 'fuqer_VSTD20', 'sw1'],
                     window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        factor = -data['fuqer_VSTD20']
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_vol18")