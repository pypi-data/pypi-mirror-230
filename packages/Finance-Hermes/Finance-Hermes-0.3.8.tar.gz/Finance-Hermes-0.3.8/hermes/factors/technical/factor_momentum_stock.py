# -*- encoding:utf-8 -*-
import numpy as np
import pandas as pd
from alphakit.const import *
from alphakit.factor import *
from alphakit.portfolio import *
from alphakit.data import *

from hermes.factors.base import FactorBase, LongCallMixin, ShortCallMixin
from jdwdata.RetrievalAPI import get_data_by_map


class FactorMomentumStock(FactorBase, LongCallMixin, ShortCallMixin):

    def __init__(self, data_format, **kwargs):
        __str__ = 'factor_momentum_stock'
        self.category = 'Momentum'
        self.name = '股票动量因子'
        self._data_format = data_format
        self._data = self.init_data(**kwargs) if 'end_date' in kwargs else None
        data = get_data_by_map(columns=BARRA_ALL_K,
                               begin_date=self.begin_date,
                               end_date=self.end_date,
                               method='ddb')
        self._risksizeindu = getdataset(data, BARRA_SIZEIND_K)

    def _init_self(self, **kwargs):
        pass

    def pv_sub3(self, data, halflife):
        t = pd.DataFrame(data)
        return t.ewm(halflife=halflife, axis=0).mean().iloc[-1, :].values

    def factor_mom1(self,
                    data=None,
                    dependencies=[
                        'dummy120_fst', 'preClosePrice', 'highestPrice',
                        'lowestPrice', 'sw1', 'ret'
                    ],
                    window=60):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        ret = data['ret']
        preClosePrice = data['preClosePrice']
        highestPrice = data['highestPrice']
        lowestPrice = data['lowestPrice']
        preClosePrice[preClosePrice == 0] = np.nan
        ret1 = (highestPrice - lowestPrice) / preClosePrice
        rank = ret1.rolling(60, min_periods=10).rank(pct=True)
        ret2 = ret.copy()
        ret2[:] = np.nan
        ret2[rank >= 0.8] = ret[rank >= 0.8]
        ret2[rank <= 0.2] = -ret[rank <= 0.2]
        factor = -ret2.rolling(60, min_periods=5).sum()
        factor = indfill_median(factor * dummy, sw1)
        return self._format(factor, "factor_mom1")

    def factor_mom2(self,
                    data=None,
                    dependencies=['dummy120_fst', 'fuqer_MTMMA', 'sw1'],
                    window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        factor = -data['fuqer_MTMMA']
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_mom2")

    def factor_mom3(self,
                    data=None,
                    dependencies=['dummy120_fst', 'fuqer_Price3M', 'sw1'],
                    window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        factor = -data['fuqer_Price3M']
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_mom3")

    def factor_mom4(self,
                    data=None,
                    dependencies=['dummy120_fst', 'ret', 'sw1'],
                    window=60):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        ret = data['ret'] * dummy
        rk = ret.rank(axis=1, ascending=False)
        rk[rk <= 50] = 1
        rk[rk > 50] = 0
        mid = ret
        mid[rk == 1] = np.nan
        b_rolling = rolling_window(rk.values, 60)
        f1 = pd.DataFrame(map(lambda x: self.pv_sub3(x, 60), b_rolling),
                          index=ret.index,
                          columns=ret.columns)
        c = rk.rolling(60, min_periods=0).count()
        f1[c < 10] = np.nan
        f2 = mid.rolling(20, min_periods=5).std()
        factor = -f1 * f2
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_mom4")

    def factor_mom5(self,
                    data=None,
                    dependencies=[
                        'dummy120_fst', 'preClosePrice', 'closePrice',
                        'openPrice', 'sw1'
                    ],
                    window=21):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        preClosePrice = data['preClosePrice']
        closePrice = data['closePrice']
        openPrice = data['openPrice']
        preClosePrice[preClosePrice <= 0] = np.nan
        openPrice[openPrice <= 0] = np.nan
        closePrice[closePrice <= 0] = np.nan
        f = (closePrice - openPrice) / preClosePrice * dummy
        factor = -f.rolling(21, min_periods=5).mean()
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_mom5")

    def factor_mom6(self,
                    data=None,
                    dependencies=[
                        'dummy120_fst', 'preClosePrice', 'reportquart',
                        'openPrice', 'sw1'
                    ],
                    window=300):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        preClosePrice = data['preClosePrice']
        reportquart = data['reportquart']
        openPrice = data['openPrice']
        preClosePrice[preClosePrice <= 0] = np.nan
        openPrice[openPrice <= 0] = np.nan
        sft1 = reportquart.shift(1)
        sft2 = reportquart.shift(2)
        f = np.log(openPrice / preClosePrice)
        f[sft1 == sft2] = np.nan
        tf = f.ffill(limit=300)
        factor = tf.sub(tf.mean(axis=1), axis='rows')
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_mom6")

    def factor_mom7(self,
                    data=None,
                    dependencies=['dummy120_fst', 'fuqer_REVS750', 'sw1'],
                    window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        factor = -data['fuqer_REVS750']
        factor = indfill_median(factor * dummy, sw1)
        return self._format(factor, "factor_mom7")

    def factor_mom8(self,
                    data=None,
                    dependencies=['dummy120_fst', 'ret', 'sw1'],
                    window=90):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        ret = data['ret'] * dummy
        factor = -ret.rolling(90, min_periods=1).sum()
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_mom8")

    def getswret(self, ret, sw1, sw1c):
        ret_simple = np.exp(ret) - 1
        tradingday = ret.index
        sw1_ret = pd.DataFrame(index=tradingday, columns=sw1c)
        for c in sw1c:
            temp = ret_simple.copy()
            temp[sw1 != c] = np.nan
            sw1_ret.loc[:, c] = np.log(temp.mean(axis=1) + 1)
        tempa = sw1.unstack().reset_index()
        tempa.columns = ['ticker', 'datetime', 'indu']
        tempb = sw1_ret.unstack().reset_index()
        tempb.columns = ['indu', 'datetime', 'ret']
        tempc = tempa.merge(tempb, how='left', on=['datetime', 'indu'])
        sw1_ret_matrix = tempc.pivot(index='datetime',
                                     columns='ticker',
                                     values='ret')
        return sw1_ret_matrix

    def factor_mom9(self,
                    data=None,
                    dependencies=['dummy120_fst', 'ret', 'sw1', 'mapping'],
                    window=20):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        ret = data['ret'] * dummy
        mapping = data['mapping']
        sw1c = mapping.loc[(mapping.type == 'industry')
                           & (mapping.category == 'sw') & (mapping.level == 1),
                           'code']
        sw1_ret_matrix = self.getswret(ret, sw1, sw1c)
        factor = (ret * dummy).rolling(window=20, min_periods=10).corr(
            sw1_ret_matrix * dummy)
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_mom9")

    def factor_mom10(self,
                     data=None,
                     dependencies=['dummy120_fst', 'ret', 'sw1', 'mapping'],
                     window=40):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        ret = data['ret'] * dummy
        mapping = data['mapping']
        sw1c = mapping.loc[(mapping.type == 'industry')
                           & (mapping.category == 'sw') & (mapping.level == 1),
                           'code']
        sw1_ret_matrix = self.getswret(ret, sw1, sw1c)
        factor = (ret * dummy).rolling(window=40, min_periods=20).corr(
            sw1_ret_matrix * dummy)
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_mom10")

    def factor_mom11(self,
                     data=None,
                     dependencies=['dummy120_fst', 'fuqer_ADTM', 'sw1'],
                     window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        factor = -data['fuqer_ADTM']
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_mom11")

    def factor_mom12(self,
                     data=None,
                     dependencies=['dummy120_fst', 'fuqer_AR', 'sw1'],
                     window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        factor = -data['fuqer_AR']
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_mom12")

    def factor_mom13(self,
                     data=None,
                     dependencies=['dummy120_fst', 'fuqer_ASI', 'sw1'],
                     window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        factor = -data['fuqer_ASI']
        factor = indfill_median(factor * dummy, sw1)
        return self._format(factor, "factor_mom13")

    def factor_mom14(self,
                     data=None,
                     dependencies=['dummy120_fst', 'fuqer_BBIC', 'sw1'],
                     window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        factor = data['fuqer_BBIC']
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_mom14")

    def factor_mom15(
            self,
            data=None,
            dependencies=['dummy120_fst', 'fuqer_ChaikinOscillator', 'sw1'],
            window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        factor = -data['fuqer_ChaikinOscillator']
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_mom15")

    def factor_mom16(self,
                     data=None,
                     dependencies=['dummy120_fst', 'fuqer_PLRC12', 'sw1'],
                     window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        factor = -data['fuqer_PLRC12']
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_mom16")

    def factor_mom17(self,
                     data=None,
                     dependencies=['dummy120_fst', 'fuqer_RSTR24', 'sw1'],
                     window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        factor = -data['fuqer_RSTR24']
        factor = indfill_median(factor * dummy, sw1)
        return self._format(factor, "factor_mom17")

    def factor_mom18(self,
                     data=None,
                     dependencies=['dummy120_fst', 'fuqer_WVAD', 'sw1'],
                     window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        factor = -data['fuqer_WVAD']
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_mom18")