# -*- encoding:utf-8 -*-
import numpy as np
import pandas as pd
import scipy.stats as st
from alphakit.const import *
from alphakit.factor import *
from alphakit.portfolio import *
from alphakit.data import *

from hermes.factors.base import FactorBase, LongCallMixin, ShortCallMixin
from jdwdata.RetrievalAPI import get_data_by_map


class FactorRiskStock(FactorBase, LongCallMixin, ShortCallMixin):

    def __init__(self, data_format, **kwargs):
        __str__ = 'factor_risk_stock'
        self.category = 'Risk'
        self.name = '股票风险因子'
        self._data_format = data_format
        self._data = self.init_data(**kwargs) if 'end_date' in kwargs else None
        data = get_data_by_map(columns=BARRA_ALL_K,
                               begin_date=self.begin_date,
                               end_date=self.end_date,
                               method='ddb')
        self._risksizeindu = getdataset(data, BARRA_SIZEIND_K)

    def _init_self(self, **kwargs):
        pass

    def rolling_regress(self, my_y, my_x, p, x_count):
        if my_x.empty:
            df = my_y
            timex = True
        else:
            df = pd.merge(my_x, my_y, left_index=True, right_index=True)
            timex = False
        usedata = self.roll(df, p).apply(self.ols,
                                         x_count=x_count,
                                         timex=timex)
        usedata.index.names = ['date', 'vars_name']
        return usedata

    def rolling_window_sub(self, a, nn):
        shape = a.shape[:-1] + (a.shape[-1] - nn + 1, nn)
        strides = a.strides + (a.strides[-1], )
        return np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)

    def roll(self, df, w):
        roll_array = self.rolling_window_sub(
            np.insert(df.values,
                      0,
                      values=np.nan * np.ones(shape=(w - 1, df.shape[1])),
                      axis=0).transpose(), w)
        test = pd.DataFrame(roll_array.reshape((-1, w)),
                            index=pd.MultiIndex.from_product(
                                [df.columns.to_list(),
                                 df.index.to_list()]),
                            columns=pd.Series(range(w)))
        test = test.unstack(level=1).T.groupby(level=1)
        return test

    def ols(self, df, x_count, timex):
        p = len(df)
        cl = ['alpha', 'r2', 'res', 'res_mean', 'res_ku', 'res_sk', 'res_mon']
        for i in range(x_count):
            cl.append('beta' + str(i))

        if timex:
            X = pd.DataFrame(index=range(p),
                             columns=range(x_count),
                             dtype='float')
            for i in range(x_count):
                X.iloc[range(p), i] = (pd.Series(range(p)) + 1)**(i + 1)
            X = X.values
            Y = df.values
            c = df.columns
        else:
            X = df.values[:, 0:x_count]
            Y = df.values[:, x_count:]
            c = df.columns[x_count:]
        X = np.concatenate([np.ones((p, 1)), X], axis=1)
        try:
            b = np.linalg.pinv(np.array(X.T.dot(X),
                                        dtype='float')).dot(X.T).dot(Y)
        except:
            return pd.DataFrame(columns=c, index=cl)
        yhat = X.dot(b)
        resid = Y - yhat
        ybar = np.mean(Y, axis=0)
        r2 = np.sum((yhat - ybar)**2, axis=0) / np.sum((Y - ybar)**2, axis=0)
        r2[np.isinf(r2)] = np.nan
        res = np.std(resid, axis=0)
        res[res == 0] = np.nan
        res_mean = np.mean(resid, axis=0)
        res_ku = st.kurtosis(resid, axis=0, bias=False)
        res_sk = st.skew(resid, axis=0, bias=False)
        res_mom = (np.prod(resid + 1, axis=0) - 1) / res
        b = np.insert(b,
                      1,
                      values=[r2, res, res_mean, res_ku, res_sk, res_mom],
                      axis=0)
        return pd.DataFrame(b, columns=c, index=cl)

    def factor_risk1(self,
                     data=None,
                     dependencies=[
                         'dummy120_fst', 'fuqer_GainLossVarianceRatio20', 'sw1'
                     ],
                     window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        factor = -data['fuqer_GainLossVarianceRatio20']
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_risk1")

    def factor_risk2(self,
                     data=None,
                     dependencies=[
                         'dummy120_fst', 'fuqer_GainLossVarianceRatio60', 'sw1'
                     ],
                     window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        fuqer_GainLossVarianceRatio60 = data['fuqer_GainLossVarianceRatio60']
        factor = -fuqer_GainLossVarianceRatio60
        factor = indfill_median(factor * dummy, sw1)
        return self._format(factor, "factor_risk2")

    def factor_risk3(self,
                     data=None,
                     dependencies=[
                         'dummy120_fst', 'fuqer_GainLossVarianceRatio120',
                         'sw1'
                     ],
                     window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        fuqer_GainLossVarianceRatio120 = data['fuqer_GainLossVarianceRatio120']
        factor = -fuqer_GainLossVarianceRatio120
        factor = indfill_median(factor * dummy, sw1)
        return self._format(factor, "factor_risk3")

    def factor_risk4(
            self,
            data=None,
            dependencies=['dummy120_fst', 'fuqer_GainVariance20', 'sw1'],
            window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        factor = -data['fuqer_GainVariance20']
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_risk4")

    def factor_risk5(self,
                     data=None,
                     dependencies=['dummy120_fst', 'SRISK', 'sw1'],
                     window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        factor = -data['SRISK']
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_risk5")

    def factor_risk6(self,
                     data=None,
                     dependencies=['dummy120_fst', 'ret', 'sw1'],
                     window=20):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        ret = data['ret']
        mktret = (ret * dummy).mean(axis=1)
        ret_filled = indfill_median(ret * dummy, sw1)
        reg_result = self.rolling_regress(ret_filled, pd.DataFrame(mktret), 20,
                                          1)
        factor = reg_result.query('vars_name=="r2"').reset_index(level=1,
                                                                 drop=True)
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_risk6")

    def factor_risk7(self,
                     data=None,
                     dependencies=[
                         'dummy120_fst', 'ret', 'sw1', 'negMarketValue',
                         'closePrice', 'totalShares', 'bspub_tShEquity_pnq0'
                     ],
                     window=40):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        ret = data['ret']
        fcap = data['negMarketValue']
        closePrice = data['closePrice']
        totalShares = data['totalShares']
        tShEquity0 = data['bspub_tShEquity_pnq0']
        dy_q_pb_caldr = closePrice / (4 * tShEquity0 / totalShares)
        dy_q_pb_caldr[np.isinf(dy_q_pb_caldr)] = np.nan
        mktret = (ret * dummy).mean(axis=1)
        ret_filled = indfill_median(ret * dummy, sw1)
        temp = pd.DataFrame().reindex_like(ret)
        temp.mask(dy_q_pb_caldr.sub(dy_q_pb_caldr.quantile(0.1, axis=1),
                                    axis=0) <= 0,
                  -1,
                  inplace=True)
        temp.mask(dy_q_pb_caldr.sub(dy_q_pb_caldr.quantile(0.9, axis=1),
                                    axis=0) > 0,
                  1,
                  inplace=True)
        hml = temp.mul(ret, axis=0).sum(axis=1)
        hml[hml == 0] = np.nan
        temp = pd.DataFrame().reindex_like(ret)
        temp.mask(fcap.sub(fcap.quantile(0.1, axis=1), axis=0) <= 0,
                  -1,
                  inplace=True)
        temp.mask(fcap.sub(fcap.quantile(0.9, axis=1), axis=0) > 0,
                  1,
                  inplace=True)
        smb = temp.mul(ret, axis=0).sum(axis=1)
        smb[smb == 0] = np.nan

        tradingday = dummy.index
        reg_result = self.rolling_regress(
            ret_filled,
            pd.DataFrame(np.transpose([mktret, smb, hml]), index=tradingday),
            40, 3)
        factor = -reg_result.query('vars_name=="alpha"').reset_index(level=1,
                                                                     drop=True)
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_risk7")

    def factor_risk8(self,
                     data=None,
                     dependencies=[
                         'dummy120_fst', 'ret', 'sw1', 'negMarketValue',
                         'closePrice', 'totalShares', 'bspub_tShEquity_pnq0'
                     ],
                     window=20):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        ret = data['ret']
        fcap = data['negMarketValue']
        closePrice = data['closePrice']
        totalShares = data['totalShares']
        tShEquity0 = data['bspub_tShEquity_pnq0']
        dy_q_pb_caldr = closePrice / (4 * tShEquity0 / totalShares)
        dy_q_pb_caldr[np.isinf(dy_q_pb_caldr)] = np.nan
        mktret = (ret * dummy).mean(axis=1)
        ret_filled = indfill_median(ret * dummy, sw1)
        temp = pd.DataFrame().reindex_like(ret)
        temp.mask(dy_q_pb_caldr.sub(dy_q_pb_caldr.quantile(0.1, axis=1),
                                    axis=0) <= 0,
                  -1,
                  inplace=True)
        temp.mask(dy_q_pb_caldr.sub(dy_q_pb_caldr.quantile(0.9, axis=1),
                                    axis=0) > 0,
                  1,
                  inplace=True)
        hml = temp.mul(ret, axis=0).sum(axis=1)
        hml[hml == 0] = np.nan
        temp = pd.DataFrame().reindex_like(ret)
        temp.mask(fcap.sub(fcap.quantile(0.1, axis=1), axis=0) <= 0,
                  -1,
                  inplace=True)
        temp.mask(fcap.sub(fcap.quantile(0.9, axis=1), axis=0) > 0,
                  1,
                  inplace=True)
        smb = temp.mul(ret, axis=0).sum(axis=1)
        smb[smb == 0] = np.nan

        tradingday = dummy.index
        reg_result = self.rolling_regress(
            ret_filled,
            pd.DataFrame(np.transpose([mktret, smb, hml]), index=tradingday),
            20, 3)
        factor = -reg_result.query('vars_name=="res"').reset_index(level=1,
                                                                   drop=True)
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_risk8")

    def factor_risk9(self,
                     data=None,
                     dependencies=[
                         'dummy120_fst', 'ret', 'sw1', 'negMarketValue',
                         'closePrice', 'totalShares', 'bspub_tShEquity_pnq0'
                     ],
                     window=40):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        ret = data['ret']
        fcap = data['negMarketValue']
        closePrice = data['closePrice']
        totalShares = data['totalShares']
        tShEquity0 = data['bspub_tShEquity_pnq0']
        dy_q_pb_caldr = closePrice / (4 * tShEquity0 / totalShares)
        dy_q_pb_caldr[np.isinf(dy_q_pb_caldr)] = np.nan
        mktret = (ret * dummy).mean(axis=1)
        ret_filled = indfill_median(ret * dummy, sw1)
        temp = pd.DataFrame().reindex_like(ret)
        temp.mask(dy_q_pb_caldr.sub(dy_q_pb_caldr.quantile(0.1, axis=1),
                                    axis=0) <= 0,
                  -1,
                  inplace=True)
        temp.mask(dy_q_pb_caldr.sub(dy_q_pb_caldr.quantile(0.9, axis=1),
                                    axis=0) > 0,
                  1,
                  inplace=True)
        hml = temp.mul(ret, axis=0).sum(axis=1)
        hml[hml == 0] = np.nan
        temp = pd.DataFrame().reindex_like(ret)
        temp.mask(fcap.sub(fcap.quantile(0.1, axis=1), axis=0) <= 0,
                  -1,
                  inplace=True)
        temp.mask(fcap.sub(fcap.quantile(0.9, axis=1), axis=0) > 0,
                  1,
                  inplace=True)
        smb = temp.mul(ret, axis=0).sum(axis=1)
        smb[smb == 0] = np.nan

        tradingday = dummy.index
        reg_result = self.rolling_regress(
            ret_filled,
            pd.DataFrame(np.transpose([mktret, smb, hml]), index=tradingday),
            40, 3)
        factor = reg_result.query('vars_name=="r2"').reset_index(level=1,
                                                                 drop=True)
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_risk9")

    def factor_risk10(self,
                      data=None,
                      dependencies=[
                          'dummy120_fst', 'ret', 'sw1', 'negMarketValue',
                          'closePrice', 'totalShares', 'bspub_tShEquity_pnq0'
                      ],
                      window=90):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        ret = data['ret']
        fcap = data['negMarketValue']
        closePrice = data['closePrice']
        totalShares = data['totalShares']
        tShEquity0 = data['bspub_tShEquity_pnq0']
        dy_q_pb_caldr = closePrice / (4 * tShEquity0 / totalShares)
        dy_q_pb_caldr[np.isinf(dy_q_pb_caldr)] = np.nan
        mktret = (ret * dummy).mean(axis=1)
        ret_filled = indfill_median(ret * dummy, sw1)
        temp = pd.DataFrame().reindex_like(ret)
        temp.mask(dy_q_pb_caldr.sub(dy_q_pb_caldr.quantile(0.1, axis=1),
                                    axis=0) <= 0,
                  -1,
                  inplace=True)
        temp.mask(dy_q_pb_caldr.sub(dy_q_pb_caldr.quantile(0.9, axis=1),
                                    axis=0) > 0,
                  1,
                  inplace=True)
        hml = temp.mul(ret, axis=0).sum(axis=1)
        hml[hml == 0] = np.nan
        temp = pd.DataFrame().reindex_like(ret)
        temp.mask(fcap.sub(fcap.quantile(0.1, axis=1), axis=0) <= 0,
                  -1,
                  inplace=True)
        temp.mask(fcap.sub(fcap.quantile(0.9, axis=1), axis=0) > 0,
                  1,
                  inplace=True)
        smb = temp.mul(ret, axis=0).sum(axis=1)
        smb[smb == 0] = np.nan

        tradingday = dummy.index
        reg_result = self.rolling_regress(
            ret_filled,
            pd.DataFrame(np.transpose([mktret, smb, hml]), index=tradingday),
            90, 3)
        factor = reg_result.query('vars_name=="r2"').reset_index(level=1,
                                                                 drop=True)
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_risk10")

    def factor_risk11(
            self,
            data=None,
            dependencies=['dummy120_fst', 'fuqer_TreynorRatio60', 'sw1'],
            window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        factor = -data['fuqer_TreynorRatio60']
        factor = indfill_median(factor * dummy, sw1)
        return self._format(factor, "factor_risk11")

    def factor_risk12(self,
                      data=None,
                      dependencies=['dummy120_fst', 'fuqer_Skewness', 'sw1'],
                      window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        factor = -data['fuqer_Skewness']
        factor = indfill_median(factor * dummy, sw1)
        return self._format(factor, "factor_risk12")

    def factor_risk13(
            self,
            data=None,
            dependencies=['dummy120_fst', 'fuqer_REVS20Indu1', 'sw1'],
            window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        factor = -data['fuqer_REVS20Indu1']
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_risk13")

    def factor_risk14(self,
                      data=None,
                      dependencies=['dummy120_fst', 'fuqer_Alpha120', 'sw1'],
                      window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        factor = -data['fuqer_Alpha120']
        factor = indfill_median(factor * dummy, sw1)
        return self._format(factor, "factor_risk14")

    def factor_risk15(self,
                      data=None,
                      dependencies=['dummy120_fst', 'fuqer_Beta20', 'sw1'],
                      window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        factor = data['fuqer_Beta20']
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_risk15")

    def factor_risk16(self,
                      data=None,
                      dependencies=['dummy120_fst', 'fuqer_Beta60', 'sw1'],
                      window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        factor = data['fuqer_Beta60']
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_risk16")

    def factor_risk17(self,
                      data=None,
                      dependencies=[
                          'dummy120_fst', 'ret', 'sw1', 'negMarketValue',
                          'closePrice', 'totalShares', 'bspub_tShEquity_pnq0'
                      ],
                      window=20):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        ret = data['ret']
        fcap = data['negMarketValue']
        closePrice = data['closePrice']
        totalShares = data['totalShares']
        tShEquity0 = data['bspub_tShEquity_pnq0']
        dy_q_pb_caldr = closePrice / (4 * tShEquity0 / totalShares)
        dy_q_pb_caldr[np.isinf(dy_q_pb_caldr)] = np.nan
        mktret = (ret * dummy).mean(axis=1)
        ret_filled = indfill_median(ret * dummy, sw1)
        temp = pd.DataFrame().reindex_like(ret)
        temp.mask(dy_q_pb_caldr.sub(dy_q_pb_caldr.quantile(0.1, axis=1),
                                    axis=0) <= 0,
                  -1,
                  inplace=True)
        temp.mask(dy_q_pb_caldr.sub(dy_q_pb_caldr.quantile(0.9, axis=1),
                                    axis=0) > 0,
                  1,
                  inplace=True)
        hml = temp.mul(ret, axis=0).sum(axis=1)
        hml[hml == 0] = np.nan
        temp = pd.DataFrame().reindex_like(ret)
        temp.mask(fcap.sub(fcap.quantile(0.1, axis=1), axis=0) <= 0,
                  -1,
                  inplace=True)
        temp.mask(fcap.sub(fcap.quantile(0.9, axis=1), axis=0) > 0,
                  1,
                  inplace=True)
        smb = temp.mul(ret, axis=0).sum(axis=1)
        smb[smb == 0] = np.nan

        tradingday = dummy.index
        reg_result = self.rolling_regress(
            ret_filled,
            pd.DataFrame(np.transpose([mktret, smb, hml]), index=tradingday),
            20, 3)
        factor = -reg_result.query('vars_name=="alpha"').reset_index(level=1,
                                                                     drop=True)
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_risk17")

    def factor_risk18(self,
                      data=None,
                      dependencies=[
                          'dummy120_fst', 'ret', 'sw1', 'negMarketValue',
                          'closePrice', 'totalShares', 'bspub_tShEquity_pnq0'
                      ],
                      window=60):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        ret = data['ret']
        fcap = data['negMarketValue']
        closePrice = data['closePrice']
        totalShares = data['totalShares']
        tShEquity0 = data['bspub_tShEquity_pnq0']
        dy_q_pb_caldr = closePrice / (4 * tShEquity0 / totalShares)
        dy_q_pb_caldr[np.isinf(dy_q_pb_caldr)] = np.nan
        mktret = (ret * dummy).mean(axis=1)
        ret_filled = indfill_median(ret * dummy, sw1)
        temp = pd.DataFrame().reindex_like(ret)
        temp.mask(dy_q_pb_caldr.sub(dy_q_pb_caldr.quantile(0.1, axis=1),
                                    axis=0) <= 0,
                  -1,
                  inplace=True)
        temp.mask(dy_q_pb_caldr.sub(dy_q_pb_caldr.quantile(0.9, axis=1),
                                    axis=0) > 0,
                  1,
                  inplace=True)
        hml = temp.mul(ret, axis=0).sum(axis=1)
        hml[hml == 0] = np.nan
        temp = pd.DataFrame().reindex_like(ret)
        temp.mask(fcap.sub(fcap.quantile(0.1, axis=1), axis=0) <= 0,
                  -1,
                  inplace=True)
        temp.mask(fcap.sub(fcap.quantile(0.9, axis=1), axis=0) > 0,
                  1,
                  inplace=True)
        smb = temp.mul(ret, axis=0).sum(axis=1)
        smb[smb == 0] = np.nan

        tradingday = dummy.index
        reg_result = self.rolling_regress(
            ret_filled,
            pd.DataFrame(np.transpose([mktret, smb, hml]), index=tradingday),
            60, 3)
        factor = -reg_result.query('vars_name=="alpha"').reset_index(level=1,
                                                                     drop=True)
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_risk18")

    def factor_risk19(self,
                      data=None,
                      dependencies=[
                          'dummy120_fst', 'ret', 'sw1', 'negMarketValue',
                          'closePrice', 'totalShares', 'bspub_tShEquity_pnq0'
                      ],
                      window=90):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        ret = data['ret']
        fcap = data['negMarketValue']
        closePrice = data['closePrice']
        totalShares = data['totalShares']
        tShEquity0 = data['bspub_tShEquity_pnq0']
        dy_q_pb_caldr = closePrice / (4 * tShEquity0 / totalShares)
        dy_q_pb_caldr[np.isinf(dy_q_pb_caldr)] = np.nan
        mktret = (ret * dummy).mean(axis=1)
        ret_filled = indfill_median(ret * dummy, sw1)
        temp = pd.DataFrame().reindex_like(ret)
        temp.mask(dy_q_pb_caldr.sub(dy_q_pb_caldr.quantile(0.1, axis=1),
                                    axis=0) <= 0,
                  -1,
                  inplace=True)
        temp.mask(dy_q_pb_caldr.sub(dy_q_pb_caldr.quantile(0.9, axis=1),
                                    axis=0) > 0,
                  1,
                  inplace=True)
        hml = temp.mul(ret, axis=0).sum(axis=1)
        hml[hml == 0] = np.nan
        temp = pd.DataFrame().reindex_like(ret)
        temp.mask(fcap.sub(fcap.quantile(0.1, axis=1), axis=0) <= 0,
                  -1,
                  inplace=True)
        temp.mask(fcap.sub(fcap.quantile(0.9, axis=1), axis=0) > 0,
                  1,
                  inplace=True)
        smb = temp.mul(ret, axis=0).sum(axis=1)
        smb[smb == 0] = np.nan

        tradingday = dummy.index
        reg_result = self.rolling_regress(
            ret_filled,
            pd.DataFrame(np.transpose([mktret, smb, hml]), index=tradingday),
            90, 3)
        factor = -reg_result.query('vars_name=="alpha"').reset_index(level=1,
                                                                     drop=True)
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_risk19")

    def factor_risk20(self,
                      data=None,
                      dependencies=['dummy120_fst', 'ret', 'sw1', 'mapping'],
                      window=60):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        tradingday = dummy.index
        ticker = dummy.columns
        mapping = data['mapping']
        sw1c = mapping.loc[(mapping.type == 'industry')
                           & (mapping.category == 'sw') & (mapping.level == 1),
                           'code']
        sw1 = data['sw1']
        ret = data['ret']
        ret_simple = np.exp(ret) - 1
        mktret = (ret * dummy).mean(axis=1)
        ret_filled = indfill_median(ret * dummy, sw1)
        sw1_ret = pd.DataFrame(index=tradingday, columns=sw1c)
        for c in sw1c:
            temp = ret_simple.copy()
            temp[sw1 != c] = np.nan
            sw1_ret.loc[:, c] = np.log(temp.mean(axis=1) + 1)
        factor = pd.DataFrame(index=tradingday,
                              columns=ticker,
                              dtype='float64')
        for ss in sw1c.values:
            indu_dummy = sw1.copy()
            indu_dummy[sw1 != ss] = np.nan
            indu_dummy.replace(ss, 1, inplace=True)
            flag = indu_dummy.sum() > 0
            tret = pd.DataFrame(np.transpose([mktret, sw1_ret.loc[:, ss]]),
                                index=tradingday)
            tret = tret.astype('float')
            reg_result = self.rolling_regress(ret_filled.loc[:, flag], tret,
                                              60, 2)
            factor = factor.add(
                reg_result.query('vars_name=="r2"').reset_index(level=1,
                                                                drop=True) *
                dummy.loc[:, flag] * indu_dummy.loc[:, flag],
                fill_value=0)
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_risk20")

    def factor_risk21(self,
                      data=None,
                      dependencies=['dummy120_fst', 'ret', 'sw1', 'mapping'],
                      window=60):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        tradingday = dummy.index
        ticker = dummy.columns
        mapping = data['mapping']
        sw1c = mapping.loc[(mapping.type == 'industry')
                           & (mapping.category == 'sw') & (mapping.level == 1),
                           'code']
        sw1 = data['sw1']
        ret = data['ret']
        ret_simple = np.exp(ret) - 1
        mktret = (ret * dummy).mean(axis=1)
        ret_filled = indfill_median(ret * dummy, sw1)
        sw1_ret = pd.DataFrame(index=tradingday, columns=sw1c)
        for c in sw1c:
            temp = ret_simple.copy()
            temp[sw1 != c] = np.nan
            sw1_ret.loc[:, c] = np.log(temp.mean(axis=1) + 1)
        factor = pd.DataFrame(index=tradingday,
                              columns=ticker,
                              dtype='float64')
        for ss in sw1c.values:
            indu_dummy = sw1.copy()
            indu_dummy[sw1 != ss] = np.nan
            indu_dummy.replace(ss, 1, inplace=True)
            flag = indu_dummy.sum() > 0
            tret = pd.DataFrame(np.transpose([mktret, sw1_ret.loc[:, ss]]),
                                index=tradingday)
            tret = tret.astype('float')
            reg_result = self.rolling_regress(ret_filled.loc[:, flag], tret,
                                              40, 2)
            factor = factor.add(
                reg_result.query('vars_name=="alpha"').reset_index(level=1,
                                                                   drop=True) *
                dummy.loc[:, flag] * indu_dummy.loc[:, flag],
                fill_value=0)
        factor = -indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_risk21")

    def factor_risk22(self,
                      data=None,
                      dependencies=['dummy120_fst', 'ret', 'sw1', 'mapping'],
                      window=60):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        tradingday = dummy.index
        ticker = dummy.columns
        mapping = data['mapping']
        sw1c = mapping.loc[(mapping.type == 'industry')
                           & (mapping.category == 'sw') & (mapping.level == 1),
                           'code']
        sw1 = data['sw1']
        ret = data['ret']
        ret_simple = np.exp(ret) - 1
        mktret = (ret * dummy).mean(axis=1)
        ret_filled = indfill_median(ret * dummy, sw1)
        sw1_ret = pd.DataFrame(index=tradingday, columns=sw1c)
        for c in sw1c:
            temp = ret_simple.copy()
            temp[sw1 != c] = np.nan
            sw1_ret.loc[:, c] = np.log(temp.mean(axis=1) + 1)
        factor = pd.DataFrame(index=tradingday,
                              columns=ticker,
                              dtype='float64')
        for ss in sw1c.values:
            indu_dummy = sw1.copy()
            indu_dummy[sw1 != ss] = np.nan
            indu_dummy.replace(ss, 1, inplace=True)
            flag = indu_dummy.sum() > 0
            tret = pd.DataFrame(np.transpose([mktret, sw1_ret.loc[:, ss]]),
                                index=tradingday)
            tret = tret.astype('float')
            reg_result = self.rolling_regress(ret_filled.loc[:, flag], tret,
                                              60, 2)
            factor = factor.add(
                reg_result.query('vars_name=="alpha"').reset_index(level=1,
                                                                   drop=True) *
                dummy.loc[:, flag] * indu_dummy.loc[:, flag],
                fill_value=0)
        factor = -indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_risk22")

    def factor_risk23(self,
                      data=None,
                      dependencies=['dummy120_fst', 'ret', 'sw1'],
                      window=40):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        ret = data['ret']
        sw1 = data['sw1']
        mktret = (ret * dummy).mean(axis=1)
        ret_filled = indfill_median(ret * dummy, sw1)
        reg_result = self.rolling_regress(ret_filled, pd.DataFrame(mktret), 40,
                                          1)
        factor = reg_result.query('vars_name=="beta0"').reset_index(level=1,
                                                                    drop=True)
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_risk23")

    def factor_risk24(self,
                      data=None,
                      dependencies=[
                          'dummy120_fst', 'ret', 'sw1', 'negMarketValue',
                          'closePrice', 'totalShares', 'bspub_tShEquity_pnq0'
                      ],
                      window=20):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        ret = data['ret']
        fcap = data['negMarketValue']
        closePrice = data['closePrice']
        totalShares = data['totalShares']
        tShEquity0 = data['bspub_tShEquity_pnq0']
        dy_q_pb_caldr = closePrice / (4 * tShEquity0 / totalShares)
        dy_q_pb_caldr[np.isinf(dy_q_pb_caldr)] = np.nan
        mktret = (ret * dummy).mean(axis=1)
        ret_filled = indfill_median(ret * dummy, sw1)
        temp = pd.DataFrame().reindex_like(ret)
        temp.mask(dy_q_pb_caldr.sub(dy_q_pb_caldr.quantile(0.1, axis=1),
                                    axis=0) <= 0,
                  -1,
                  inplace=True)
        temp.mask(dy_q_pb_caldr.sub(dy_q_pb_caldr.quantile(0.9, axis=1),
                                    axis=0) > 0,
                  1,
                  inplace=True)
        hml = temp.mul(ret, axis=0).sum(axis=1)
        hml[hml == 0] = np.nan
        temp = pd.DataFrame().reindex_like(ret)
        temp.mask(fcap.sub(fcap.quantile(0.1, axis=1), axis=0) <= 0,
                  -1,
                  inplace=True)
        temp.mask(fcap.sub(fcap.quantile(0.9, axis=1), axis=0) > 0,
                  1,
                  inplace=True)
        smb = temp.mul(ret, axis=0).sum(axis=1)
        smb[smb == 0] = np.nan

        tradingday = dummy.index
        reg_result = self.rolling_regress(
            ret_filled,
            pd.DataFrame(np.transpose([mktret, smb, hml]), index=tradingday),
            20, 3)
        factor = reg_result.query('vars_name=="beta0"').reset_index(level=1,
                                                                    drop=True)
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_risk24")

    def factor_risk25(self,
                      data=None,
                      dependencies=['dummy120_fst', 'ret', 'sw1'],
                      window=40):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        ret = data['ret']
        sw1 = data['sw1']
        ret_filled = indfill_median(ret * dummy, sw1)
        reg_result = self.rolling_regress(
            ret_filled.rolling(40, min_periods=1).sum(), pd.DataFrame(), 40, 2)
        factor = reg_result.query('vars_name=="beta1"').reset_index(level=1,
                                                                    drop=True)
        factor = -indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_risk25")