# -*- encoding:utf-8 -*-
import numpy as np
import pandas as pd
import pdb
import scipy.stats as st
from alphakit.const import *
from alphakit.factor import *
from alphakit.portfolio import *
from alphakit.data import *

from hermes.factors.base import FactorBase, LongCallMixin, ShortCallMixin
from jdwdata.RetrievalAPI import get_data_by_map


class FactorCom(FactorBase, LongCallMixin, ShortCallMixin):

    def __init__(self, data_format, **kwargs):
        __str__ = 'factor_com'
        self.category = 'Other'
        self.name = '综合因子'
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

    def getdep(self, cfs_FAOGPBDepr, reportquart):
        tradingday = reportquart.index
        ticker = reportquart.columns
        depall = cfs_FAOGPBDepr
        depall["year"] = depall.endDate.astype('str').str.split("-",
                                                                expand=True)[0]
        depall.sort_values("publishDate", inplace=True)
        depallc = depall.copy()
        all = pd.merge_asof(
            depall,
            depallc,
            by=["code", "year"],
            on="publishDate",
            direction="backward",
            allow_exact_matches=False,
        )
        all.loc[all.FAOGPBDepr_y.isna(), "FAOGPBDepr_y"] = 0
        all.loc[~all.endDate_x.astype('str').str.contains("-03-31"),
                "FAOGPBDepr_x"] = all.loc[
                    ~all.endDate_x.astype('str').str.contains("-03-31"),
                    "FAOGPBDepr_x"] - all.loc[
                        ~all.endDate_x.astype('str').str.contains("-03-31"),
                        "FAOGPBDepr_y"]
        reportquart = reportquart.unstack().reset_index()
        reportquart.columns = ["code", "publishDate", "endDate"]
        reportquart.sort_values("publishDate", inplace=True)
        reportquart.dropna(inplace=True)
        reportquart["year"] = reportquart.endDate.astype('str').str.split(
            "-", expand=True)[0]
        df = pd.merge_asof(
            left=reportquart,
            right=all,
            by=["code", "year"],
            on="publishDate",
            direction="backward",
        )
        ddf = df.pivot(index="publishDate",
                       columns="code",
                       values="FAOGPBDepr_x")
        ddf = ddf.reindex(index=tradingday, columns=ticker)
        return ddf

    def factor_com1(
            self,
            data=None,
            dependencies=[
                'dummy120_fst', 'sw1', 'ret', 'negMarketValue', 'closePrice',
                'totalShares', 'bspub_tShEquity_pnq0', 'fuqer_TVSTD20',
                'fuqer_TEMA5', 'turnoverVol', 'turnoverValue',
                'cfs_FAOGPBDepr', 'reportquart', 'bspub_surplusReser_pnq4',
                'isqpub_dilutedEPS_pnq0', 'isqpub_dilutedEPS_pnq1',
                'isqpub_dilutedEPS_pnq2', 'isqpub_dilutedEPS_pnq3',
                'isqpub_dilutedEPS_pnq4', 'isqpub_dilutedEPS_pnq5',
                'isqpub_dilutedEPS_pnq6', 'isqpub_dilutedEPS_pnq7',
                'isqpub_dilutedEPS_pnq8', 'isqpub_dilutedEPS_pnq9',
                'isqpub_dilutedEPS_pnq10', 'isqpub_dilutedEPS_pnq11',
                'marketValue', 'isqpub_operateProfit_pnq0',
                'isqpub_operateProfit_pnq1', 'isqpub_operateProfit_pnq2',
                'isqpub_operateProfit_pnq3', 'isqpub_operateProfit_pnq4',
                'isqpub_operateProfit_pnq5', 'isqpub_operateProfit_pnq6',
                'isqpub_operateProfit_pnq7', 'isqpub_operateProfit_pnq8',
                'isqpub_operateProfit_pnq9', 'isqpub_operateProfit_pnq10',
                'isqpub_operateProfit_pnq11', 'fbqpub_mergeEbt_pnq0',
                'fbqpub_Ebt_pnq0', 'fbqpub_mergeOprofit_pnq0',
                'fbqpub_mergeOprofit_pnq4', 'isqpub_assetsImpairLoss_pnq0',
                'isqpub_assetsImpairLoss_pnq1', 'indpub_timesInteEBIT_pnq0',
                'fuqer_NonOperatingNPTTM', 'fuqer_SFY12P',
                'cfqpub_cFrCapContr_pnq0', 'cfqpub_cFrCapContr_pnq1',
                'cfqpub_cPaidInvest_pnq0', 'cfqpub_cPaidInvest_pnq1',
                'ispub_NIncomeAttrP_pnq0', 'ispub_NIncomeAttrP_pnq1',
                'bspub_surplusReser_pnq0', 'bspub_surplusReser_pnq1',
                'cfqpub_purFixAssetsOth_pnq0', 'cfqpub_purFixAssetsOth_pnq4',
                'mapping'
            ] + BARRA_ALL_K,
            window=120):
        data = self._data if data is None else data
        riskfactor = getdataset(data, BARRA_ALL_K)
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        ret = data['ret']
        fcap = data['negMarketValue']
        closePrice = data['closePrice']
        totalShares = data['totalShares']
        tShEquity0 = data['bspub_tShEquity_pnq0']
        vol = data['turnoverVol']
        val = data['turnoverValue']
        cfs_FAOGPBDepr = data['cfs_FAOGPBDepr']
        reportquart = data['reportquart']
        mktcap = data['marketValue']
        qmergeEbt0 = data['fbqpub_mergeEbt_pnq0']
        Ebt_pnq0 = data['fbqpub_Ebt_pnq0']
        qmergeEbt0[qmergeEbt0.isna()] = Ebt_pnq0[qmergeEbt0.isna()]
        qmergeOprofit0 = data['fbqpub_mergeOprofit_pnq0']
        qoperateProfit0 = data['isqpub_operateProfit_pnq0']
        qmergeOprofit0[qmergeOprofit0.isna()] = qoperateProfit0[
            qmergeOprofit0.isna()]
        qmergeOprofit4 = data['fbqpub_mergeOprofit_pnq4']
        qoperateProfit4 = data['isqpub_operateProfit_pnq4']
        qmergeOprofit4[qmergeOprofit4.isna()] = qoperateProfit4[
            qmergeOprofit4.isna()]
        qassetsImpairLoss0 = data['isqpub_assetsImpairLoss_pnq0']
        qassetsImpairLoss1 = data['isqpub_assetsImpairLoss_pnq1']
        mapping = data['mapping']
        sw1c = mapping.loc[(mapping.type == 'industry')
                           & (mapping.category == 'sw') & (mapping.level == 1),
                           'code']

        tradingday = dummy.index
        ticker = dummy.columns
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

        reg_result = self.rolling_regress(
            ret_filled,
            pd.DataFrame(np.transpose([mktret, smb, hml]), index=tradingday),
            20, 3)
        ff_r2_20 = reg_result.query('vars_name=="r2"').reset_index(level=1,
                                                                   drop=True)
        boll120_2_cls2up, _ = self.bollbais(closePrice, 120, 1)
        ret[vol <= 0 | vol.isna()] = np.nan
        val[vol <= 0 | vol.isna()] = np.nan
        vol[vol <= 0 | vol.isna()] = np.nan
        illiq = abs(ret) / val
        illiq_p4d = illiq.rolling(4, min_periods=1).mean()
        illiq_p20d = illiq.rolling(20, min_periods=1).mean()
        ret_simple = np.exp(ret) - 1
        sw1_ret = pd.DataFrame(index=tradingday, columns=sw1c)
        for c in sw1c:
            temp = ret_simple.copy()
            temp[sw1 != c] = np.nan
            sw1_ret.loc[:, c] = np.log(temp.mean(axis=1) + 1)
        scalar40_r2 = pd.DataFrame(index=tradingday,
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
            scalar40_r2 = scalar40_r2.add(
                reg_result.query('vars_name=="r2"').reset_index(level=1,
                                                                drop=True) *
                dummy.loc[:, flag] * indu_dummy.loc[:, flag],
                fill_value=0)

        v1 = -data['fuqer_TVSTD20']
        v2 = -data['fuqer_TEMA5'].rolling(4, min_periods=1).mean()
        v3 = ff_r2_20.rolling(3, min_periods=1).mean()
        v4 = alphaOpNeu(
            (data['bspub_surplusReser_pnq0'] - data['bspub_surplusReser_pnq4'])
            * dummy, riskfactor).rolling(4, min_periods=1).mean()
        v7 = -alphaOpNeu(boll120_2_cls2up * dummy, riskfactor).rolling(
            2, min_periods=1).mean()
        v9 = -alphaOpNeu(illiq_p4d * dummy, riskfactor).rolling(
            15, min_periods=1).mean()
        v11 = alphaOpNeu(
            self.getdep(cfs_FAOGPBDepr, reportquart) * dummy,
            riskfactor).rolling(10, min_periods=1).mean()
        dfallv12 = pd.concat(
            [
                data['isqpub_dilutedEPS_pnq0'].unstack() -
                data['isqpub_dilutedEPS_pnq4'].unstack(),
                data['isqpub_dilutedEPS_pnq1'].unstack() -
                data['isqpub_dilutedEPS_pnq5'].unstack(),
                data['isqpub_dilutedEPS_pnq2'].unstack() -
                data['isqpub_dilutedEPS_pnq6'].unstack(),
                data['isqpub_dilutedEPS_pnq3'].unstack() -
                data['isqpub_dilutedEPS_pnq7'].unstack(),
                data['isqpub_dilutedEPS_pnq4'].unstack() -
                data['isqpub_dilutedEPS_pnq8'].unstack(),
                data['isqpub_dilutedEPS_pnq5'].unstack() -
                data['isqpub_dilutedEPS_pnq9'].unstack(),
                data['isqpub_dilutedEPS_pnq6'].unstack() -
                data['isqpub_dilutedEPS_pnq10'].unstack(),
                data['isqpub_dilutedEPS_pnq7'].unstack() -
                data['isqpub_dilutedEPS_pnq11'].unstack(),
            ],
            axis=1,
        )
        v12 = (dfallv12.iloc[:, 0] / dfallv12.std(axis=1)).reset_index()
        v12 = v12.pivot(index="trade_date", columns="code", values=0)
        v12 = v12.reindex(index=tradingday, columns=ticker)
        v12[np.isinf(v12)] = np.nan
        v16 = alphaOpNeu(illiq_p20d * dummy,
                         riskfactor).rolling(60, min_periods=1).mean()
        v17 = alphaOpNeu(v12 * dummy,
                         riskfactor).rolling(2, min_periods=1).mean()
        v18 = -alphaOpNeu(np.log(mktcap) * dummy, riskfactor).rolling(
            2, min_periods=1).mean()

        dfallv20 = pd.concat(
            [
                data['isqpub_operateProfit_pnq0'].unstack() -
                data['isqpub_operateProfit_pnq4'].unstack(),
                data['isqpub_operateProfit_pnq1'].unstack() -
                data['isqpub_operateProfit_pnq5'].unstack(),
                data['isqpub_operateProfit_pnq2'].unstack() -
                data['isqpub_operateProfit_pnq6'].unstack(),
                data['isqpub_operateProfit_pnq3'].unstack() -
                data['isqpub_operateProfit_pnq7'].unstack(),
                data['isqpub_operateProfit_pnq4'].unstack() -
                data['isqpub_operateProfit_pnq8'].unstack(),
                data['isqpub_operateProfit_pnq5'].unstack() -
                data['isqpub_operateProfit_pnq9'].unstack(),
                data['isqpub_operateProfit_pnq6'].unstack() -
                data['isqpub_operateProfit_pnq10'].unstack(),
                data['isqpub_operateProfit_pnq7'].unstack() -
                data['isqpub_operateProfit_pnq11'].unstack(),
            ],
            axis=1,
        )
        v20 = (dfallv20.iloc[:, 0] / dfallv20.std(axis=1)).reset_index()
        v20 = v20.pivot(index="trade_date", columns="code", values=0)
        v20 = v20.reindex(index=tradingday, columns=ticker)
        v20[np.isinf(v20)] = np.nan
        v27 = alphaOpNeu((qmergeEbt0 / totalShares) * dummy,
                         riskfactor).rolling(3, min_periods=1).mean()
        v29 = alphaOpNeu(
            data['indpub_timesInteEBIT_pnq0'] * dummy,
            riskfactor,
        ).rolling(15, min_periods=1).mean()
        v31 = alphaOpNeu(
            (qmergeOprofit0 - qmergeOprofit4) / totalShares * dummy,
            riskfactor).rolling(2, min_periods=1).mean()
        v32 = alphaOpNeu(qassetsImpairLoss0 / qassetsImpairLoss1 * dummy,
                         riskfactor).rolling(60, min_periods=1).mean()
        v36 = alphaOpNeu(data['fuqer_NonOperatingNPTTM'] * dummy,
                         riskfactor).rolling(4, min_periods=1).mean()
        v38 = alphaOpNeu(data['fuqer_SFY12P'] * dummy,
                         riskfactor).rolling(4, min_periods=1).mean()

        v39 = alphaOpNeu(
            data['cfqpub_cFrCapContr_pnq0'] / data['cfqpub_cFrCapContr_pnq1'] *
            dummy, riskfactor).rolling(4, min_periods=1).mean()
        v39[np.isinf(v39)] = np.nan
        v40 = alphaOpNeu(
            data['cfqpub_cPaidInvest_pnq0'] / data['cfqpub_cPaidInvest_pnq1'] *
            dummy, riskfactor).rolling(120, min_periods=1).mean()
        v40[np.isinf(v40)] = np.nan
        v41 = scalar40_r2.rolling(4, min_periods=1).mean()
        v42 = data['ispub_NIncomeAttrP_pnq0'] / data['ispub_NIncomeAttrP_pnq1']
        v42[np.isinf(v42)] = np.nan
        v44 = alphaOpNeu(
            (data['bspub_surplusReser_pnq0'] - data['bspub_surplusReser_pnq1'])
            * dummy, riskfactor).rolling(30, min_periods=1).mean()
        v46 = alphaOpNeu(
            data['cfqpub_purFixAssetsOth_pnq0'] /
            data['cfqpub_purFixAssetsOth_pnq4'] * dummy,
            riskfactor).rolling(40, min_periods=1).mean()
        v46[np.isinf(v46)] = np.nan
        factor = factor_merge([
            v1 * 2, v2, v3 * 2, v4 * 2, v7 * 6, v9 * 3, v11, v12, v16 * 3, v17,
            v18, v20, v27, v29 * 2, v31, v32, v36, v38, v39, v40, v41, v42,
            v44, v46 * 2
        ])
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_com1")

    def factor_com2(
            self,
            data=None,
            dependencies=[
                'dummy120_fst', 'sw1', 'ret', 'mapping', 'totalShares',
                'fuqer_TEMA5', 'turnoverVol', 'turnoverValue',
                'cfs_FAOGPBDepr', 'reportquart', 'isqpub_dilutedEPS_pnq0',
                'isqpub_dilutedEPS_pnq1', 'isqpub_dilutedEPS_pnq2',
                'isqpub_dilutedEPS_pnq3', 'isqpub_dilutedEPS_pnq4',
                'isqpub_dilutedEPS_pnq5', 'isqpub_dilutedEPS_pnq6',
                'isqpub_dilutedEPS_pnq7', 'isqpub_dilutedEPS_pnq8',
                'isqpub_dilutedEPS_pnq9', 'isqpub_dilutedEPS_pnq10',
                'isqpub_dilutedEPS_pnq11', 'marketValue',
                'isqpub_operateProfit_pnq0', 'isqpub_operateProfit_pnq1',
                'isqpub_operateProfit_pnq2', 'isqpub_operateProfit_pnq3',
                'isqpub_operateProfit_pnq4', 'isqpub_operateProfit_pnq5',
                'isqpub_operateProfit_pnq6', 'isqpub_operateProfit_pnq7',
                'isqpub_operateProfit_pnq8', 'isqpub_operateProfit_pnq9',
                'isqpub_operateProfit_pnq10', 'isqpub_operateProfit_pnq11',
                'fbqpub_mergeEbt_pnq0', 'fbqpub_Ebt_pnq0',
                'fbqpub_mergeOprofit_pnq0', 'fbqpub_mergeOprofit_pnq4',
                'indpub_timesInteEBIT_pnq0', 'fuqer_NonOperatingNPTTM',
                'cfqpub_cFrCapContr_pnq0', 'cfqpub_cFrCapContr_pnq1',
                'cfqpub_cPaidInvest_pnq0', 'cfqpub_cPaidInvest_pnq1',
                'ispub_NIncomeAttrP_pnq0', 'ispub_NIncomeAttrP_pnq1',
                'cfqpub_purFixAssetsOth_pnq0', 'cfqpub_purFixAssetsOth_pnq4',
                'isqpub_basicEPS_pnq0', 'isqpub_basicEPS_pnq4', 'fuqer_ETOP',
                'bspub_tShEquity_pnq0', 'closePrice'
            ] + BARRA_ALL_K,
            window=120):
        data = self._data if data is None else data
        riskfactor = getdataset(data, BARRA_ALL_K)
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        ret = data['ret']
        vol = data['turnoverVol']
        val = data['turnoverValue']
        closePrice = data['closePrice']
        totalShares = data['totalShares']
        cfs_FAOGPBDepr = data['cfs_FAOGPBDepr']
        reportquart = data['reportquart']
        qmergeEbt0 = data['fbqpub_mergeEbt_pnq0']
        Ebt_pnq0 = data['fbqpub_Ebt_pnq0']
        tShEquity0 = data['bspub_tShEquity_pnq0']
        qmergeEbt0[qmergeEbt0.isna()] = Ebt_pnq0[qmergeEbt0.isna()]
        qmergeOprofit0 = data['fbqpub_mergeOprofit_pnq0']
        qoperateProfit0 = data['isqpub_operateProfit_pnq0']
        qmergeOprofit0[qmergeOprofit0.isna()] = qoperateProfit0[
            qmergeOprofit0.isna()]
        qmergeOprofit4 = data['fbqpub_mergeOprofit_pnq4']
        qoperateProfit4 = data['isqpub_operateProfit_pnq4']
        qmergeOprofit4[qmergeOprofit4.isna()] = qoperateProfit4[
            qmergeOprofit4.isna()]
        mapping = data['mapping']
        sw1c = mapping.loc[(mapping.type == 'industry')
                           & (mapping.category == 'sw') & (mapping.level == 1),
                           'code']
        tradingday = dummy.index
        ticker = dummy.columns
        dy_q_pb_caldr = closePrice / (4 * tShEquity0 / totalShares)
        dy_q_pb_caldr[np.isinf(dy_q_pb_caldr)] = np.nan
        mktret = (ret * dummy).mean(axis=1)
        ret_filled = indfill_median(ret * dummy, sw1)
        ret[vol <= 0 | vol.isna()] = np.nan
        val[vol <= 0 | vol.isna()] = np.nan
        vol[vol <= 0 | vol.isna()] = np.nan
        illiq = abs(ret) / val
        illiq_p60d = illiq.rolling(60, min_periods=1).mean()
        ret_simple = np.exp(ret) - 1
        sw1_ret = pd.DataFrame(index=tradingday, columns=sw1c)
        for c in sw1c:
            temp = ret_simple.copy()
            temp[sw1 != c] = np.nan
            sw1_ret.loc[:, c] = np.log(temp.mean(axis=1) + 1)
        scalar40_r2 = pd.DataFrame(index=tradingday,
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
            scalar40_r2 = scalar40_r2.add(
                reg_result.query('vars_name=="r2"').reset_index(level=1,
                                                                drop=True) *
                dummy.loc[:, flag] * indu_dummy.loc[:, flag],
                fill_value=0)

        v2 = -data['fuqer_TEMA5'].rolling(4, min_periods=1).mean()
        v4 = alphaOpNeu(
            (data['bspub_surplusReser_pnq0'] - data['bspub_surplusReser_pnq4'])
            * dummy, riskfactor).rolling(4, min_periods=1).mean()
        v11 = alphaOpNeu(
            self.getdep(cfs_FAOGPBDepr, reportquart) * dummy,
            riskfactor).rolling(10, min_periods=1).mean()
        dfallv12 = pd.concat(
            [
                data['isqpub_dilutedEPS_pnq0'].unstack() -
                data['isqpub_dilutedEPS_pnq4'].unstack(),
                data['isqpub_dilutedEPS_pnq1'].unstack() -
                data['isqpub_dilutedEPS_pnq5'].unstack(),
                data['isqpub_dilutedEPS_pnq2'].unstack() -
                data['isqpub_dilutedEPS_pnq6'].unstack(),
                data['isqpub_dilutedEPS_pnq3'].unstack() -
                data['isqpub_dilutedEPS_pnq7'].unstack(),
                data['isqpub_dilutedEPS_pnq4'].unstack() -
                data['isqpub_dilutedEPS_pnq8'].unstack(),
                data['isqpub_dilutedEPS_pnq5'].unstack() -
                data['isqpub_dilutedEPS_pnq9'].unstack(),
                data['isqpub_dilutedEPS_pnq6'].unstack() -
                data['isqpub_dilutedEPS_pnq10'].unstack(),
                data['isqpub_dilutedEPS_pnq7'].unstack() -
                data['isqpub_dilutedEPS_pnq11'].unstack(),
            ],
            axis=1,
        )
        v12 = (dfallv12.iloc[:, 0] / dfallv12.std(axis=1)).reset_index()
        v12 = v12.pivot(index="trade_date", columns="code", values=0)
        v12 = v12.reindex(index=tradingday, columns=ticker)
        v12[np.isinf(v12)] = np.nan
        dfallv20 = pd.concat(
            [
                data['isqpub_operateProfit_pnq0'].unstack() -
                data['isqpub_operateProfit_pnq4'].unstack(),
                data['isqpub_operateProfit_pnq1'].unstack() -
                data['isqpub_operateProfit_pnq5'].unstack(),
                data['isqpub_operateProfit_pnq2'].unstack() -
                data['isqpub_operateProfit_pnq6'].unstack(),
                data['isqpub_operateProfit_pnq3'].unstack() -
                data['isqpub_operateProfit_pnq7'].unstack(),
                data['isqpub_operateProfit_pnq4'].unstack() -
                data['isqpub_operateProfit_pnq8'].unstack(),
                data['isqpub_operateProfit_pnq5'].unstack() -
                data['isqpub_operateProfit_pnq9'].unstack(),
                data['isqpub_operateProfit_pnq6'].unstack() -
                data['isqpub_operateProfit_pnq10'].unstack(),
                data['isqpub_operateProfit_pnq7'].unstack() -
                data['isqpub_operateProfit_pnq11'].unstack(),
            ],
            axis=1,
        )
        v20 = (dfallv20.iloc[:, 0] / dfallv20.std(axis=1)).reset_index()
        v20 = v20.pivot(index="trade_date", columns="code", values=0)
        v20 = v20.reindex(index=tradingday, columns=ticker)
        v20[np.isinf(v20)] = np.nan
        v25 = alphaOpNeu(illiq_p60d * dummy,
                         riskfactor).rolling(60, min_periods=1).mean()
        v27 = alphaOpNeu((qmergeEbt0 / totalShares) * dummy,
                         riskfactor).rolling(3, min_periods=1).mean()
        v29 = alphaOpNeu(
            data['indpub_timesInteEBIT_pnq0'] * dummy,
            riskfactor,
        ).rolling(15, min_periods=1).mean()
        v36 = alphaOpNeu(data['fuqer_NonOperatingNPTTM'] * dummy,
                         riskfactor).rolling(4, min_periods=1).mean()
        v37 = alphaOpNeu(data['fuqer_ETOP'] * dummy,
                         riskfactor).rolling(4, min_periods=1).mean()
        v39 = alphaOpNeu(
            data['cfqpub_cFrCapContr_pnq0'] / data['cfqpub_cFrCapContr_pnq1'] *
            dummy, riskfactor).rolling(4, min_periods=1).mean()
        v39[np.isinf(v39)] = np.nan
        v40 = alphaOpNeu(
            data['cfqpub_cPaidInvest_pnq0'] / data['cfqpub_cPaidInvest_pnq1'] *
            dummy, riskfactor).rolling(120, min_periods=1).mean()
        v40[np.isinf(v40)] = np.nan
        v41 = scalar40_r2.rolling(4, min_periods=1).mean()
        v42 = data['ispub_NIncomeAttrP_pnq0'] / data['ispub_NIncomeAttrP_pnq1']
        v42[np.isinf(v42)] = np.nan
        v46 = alphaOpNeu(
            data['cfqpub_purFixAssetsOth_pnq0'] /
            data['cfqpub_purFixAssetsOth_pnq4'] * dummy,
            riskfactor).rolling(40, min_periods=1).mean()
        v46[np.isinf(v46)] = np.nan
        factor = factor_merge([
            v2, v4, v11 * 2, v12, v20, v25 * 2, v27, v29, v36, v37, v39, v41,
            v42, v46
        ])
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_com2")