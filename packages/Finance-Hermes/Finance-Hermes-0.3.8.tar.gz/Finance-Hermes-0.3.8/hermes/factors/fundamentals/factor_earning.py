# -*- encoding:utf-8 -*-
import numpy as np
import pandas as pd
from alphakit.const import *
from alphakit.factor import *
from alphakit.portfolio import *
from alphakit.data import *

from hermes.factors.base import FactorBase, LongCallMixin, ShortCallMixin
from jdwdata.RetrievalAPI import get_data_by_map


class FactorEarning(FactorBase, LongCallMixin, ShortCallMixin):

    def __init__(self, data_format, **kwargs):
        __str__ = 'factor_earning'
        self.category = 'Earning'
        self.name = '盈利因子'
        self._data_format = data_format
        self._data = self.init_data(**kwargs) if 'end_date' in kwargs else None
        data = get_data_by_map(columns=BARRA_ALL_K,
                               begin_date=self.begin_date,
                               end_date=self.end_date,
                               method='ddb')
        self._risksizeindu = getdataset(data, BARRA_SIZEIND_K)

    def _init_self(self, **kwargs):
        pass

    def factor_earning1(
            self,
            data=None,
            dependencies=[
                'dummy120_fst', 'sw1', 'fbqpub_mergeIncome_pnq0',
                'fbqpub_mergeIncome_pnq1', 'fbqpub_mergeIncome_pnq2',
                'fbqpub_mergeIncome_pnq3', 'fbqpub_mergeIncome_pnq4',
                'fbqpub_mergeIncome_pnq5', 'fbqpub_mergeIncome_pnq6',
                'fbqpub_mergeIncome_pnq7', 'isqpub_COGS_pnq0',
                'isqpub_COGS_pnq1', 'isqpub_COGS_pnq2', 'isqpub_COGS_pnq3',
                'isqpub_COGS_pnq4', 'isqpub_COGS_pnq5', 'isqpub_COGS_pnq6',
                'isqpub_COGS_pnq7', 'isqpub_revenue_pnq0',
                'isqpub_revenue_pnq1', 'isqpub_revenue_pnq2',
                'isqpub_revenue_pnq3', 'isqpub_revenue_pnq4',
                'isqpub_revenue_pnq5', 'isqpub_revenue_pnq6',
                'isqpub_revenue_pnq7'
            ],
            window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        qmergeIncome0 = data['fbqpub_mergeIncome_pnq0']
        qrevenue0 = data['isqpub_revenue_pnq0']
        qmergeIncome0[qmergeIncome0.isna()] = qrevenue0[qmergeIncome0.isna()]
        qmergeIncome1 = data['fbqpub_mergeIncome_pnq1']
        qrevenue1 = data['isqpub_revenue_pnq1']
        qmergeIncome1[qmergeIncome1.isna()] = qrevenue1[qmergeIncome1.isna()]
        qmergeIncome2 = data['fbqpub_mergeIncome_pnq2']
        qrevenue2 = data['isqpub_revenue_pnq2']
        qmergeIncome2[qmergeIncome2.isna()] = qrevenue2[qmergeIncome2.isna()]
        qmergeIncome3 = data['fbqpub_mergeIncome_pnq3']
        qrevenue3 = data['isqpub_revenue_pnq3']
        qmergeIncome3[qmergeIncome3.isna()] = qrevenue3[qmergeIncome3.isna()]
        qmergeIncome4 = data['fbqpub_mergeIncome_pnq4']
        qrevenue4 = data['isqpub_revenue_pnq4']
        qmergeIncome4[qmergeIncome4.isna()] = qrevenue4[qmergeIncome4.isna()]
        qmergeIncome5 = data['fbqpub_mergeIncome_pnq5']
        qrevenue5 = data['isqpub_revenue_pnq5']
        qmergeIncome5[qmergeIncome5.isna()] = qrevenue5[qmergeIncome5.isna()]
        qmergeIncome6 = data['fbqpub_mergeIncome_pnq6']
        qrevenue6 = data['isqpub_revenue_pnq6']
        qmergeIncome6[qmergeIncome6.isna()] = qrevenue6[qmergeIncome6.isna()]
        qmergeIncome7 = data['fbqpub_mergeIncome_pnq7']
        qrevenue7 = data['isqpub_revenue_pnq7']
        qmergeIncome7[qmergeIncome7.isna()] = qrevenue7[qmergeIncome7.isna()]
        qcogs0 = data['isqpub_COGS_pnq0']
        qcogs1 = data['isqpub_COGS_pnq1']
        qcogs2 = data['isqpub_COGS_pnq2']
        qcogs3 = data['isqpub_COGS_pnq3']
        qcogs4 = data['isqpub_COGS_pnq4']
        qcogs5 = data['isqpub_COGS_pnq5']
        qcogs6 = data['isqpub_COGS_pnq6']
        qcogs7 = data['isqpub_COGS_pnq7']
        sw1 = data['sw1']
        tradingday = sw1.index
        ticker = sw1.columns
        dfall1 = pd.concat([
            qmergeIncome0.unstack(),
            qmergeIncome1.unstack(),
            qmergeIncome2.unstack(),
            qmergeIncome3.unstack(),
            qmergeIncome4.unstack(),
            qmergeIncome5.unstack(),
            qmergeIncome6.unstack(),
            qmergeIncome7.unstack()
        ],
                           axis=1)
        dfall2 = pd.concat([
            qcogs0.unstack(),
            qcogs1.unstack(),
            qcogs2.unstack(),
            qcogs3.unstack(),
            qcogs4.unstack(),
            qcogs5.unstack(),
            qcogs6.unstack(),
            qcogs7.unstack()
        ],
                           axis=1)

        v = dfall1.std(axis=1)
        v[v == 0] = np.nan
        df1 = dfall1.sub(dfall1.mean(axis=1), axis='rows').div(v, axis='rows')
        v = dfall2.std(axis=1)
        v[v == 0] = np.nan
        df2 = dfall2.sub(dfall2.mean(axis=1), axis='rows').div(v, axis='rows')
        df1.columns = ['q1', 'q2', 'q3', 'q4', 'q5', 'q6', 'q7', 'q8']  # x
        df2.columns = ['q1', 'q2', 'q3', 'q4', 'q5', 'q6', 'q7', 'q8']  # y
        b = (df1 * df2).sum(axis=1) / (df2 * df2).sum(axis=1)
        f = df1['q1'] - df2['q1'] * b
        f.name = 'factor'
        factor = pd.DataFrame(f).reset_index().pivot_table(index='trade_date',
                                                           columns='code',
                                                           values='factor')
        factor = factor.reindex(index=tradingday, columns=ticker)
        factor[np.isinf(factor)] = np.nan
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_earning1")

    def factor_earning2(self,
                        data=None,
                        dependencies=[
                            'dummy120_fst', 'isqpub_tRevenue_pnq0',
                            'isqpub_tCogs_pnq0', 'sw1'
                        ],
                        window=1):
        data = self._data if data is None else data
        qtRevenue0 = data['isqpub_tRevenue_pnq0']
        qtCogs0 = data['isqpub_tCogs_pnq0']
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        factor = 1 - (qtCogs0 / abs(qtRevenue0))
        factor[np.isinf(factor)] = np.nan
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_earning2")

    def factor_earning3(
            self,
            data=None,
            dependencies=[
                'dummy120_fst', 'sw1', 'fbqpub_mergeProfit_pnq0',
                'fbqpub_mergeProfit_pnq1', 'fbqpub_mergeProfit_pnq2',
                'fbqpub_mergeProfit_pnq3', 'fbqpub_mergeProfit_pnq4',
                'fbqpub_mergeProfit_pnq5', 'fbqpub_mergeProfit_pnq6',
                'fbqpub_mergeProfit_pnq7', 'fbqpub_mergeEbt_pnq0',
                'fbqpub_mergeEbt_pnq4', 'isqpub_tRevenue_pnq0',
                'isqpub_tRevenue_pnq4', 'cfqpub_cFRSaleGS_pnq0',
                'cfqpub_cFRSaleGS_pnq4', 'isqpub_finanExp_pnq0',
                'isqpub_finanExp_pnq4', 'isqpub_nIncomeAttrP_pnq0',
                'isqpub_nIncomeAttrP_pnq1', 'isqpub_nIncomeAttrP_pnq2',
                'isqpub_nIncomeAttrP_pnq3', 'isqpub_nIncomeAttrP_pnq4',
                'isqpub_nIncomeAttrP_pnq5', 'isqpub_nIncomeAttrP_pnq6',
                'isqpub_nIncomeAttrP_pnq7', 'fbqpub_Ebt_pnq0',
                'fbqpub_Ebt_pnq4'
            ],
            window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        qcFRSaleGS0 = data['cfqpub_cFRSaleGS_pnq0']
        qcFRSaleGS4 = data['cfqpub_cFRSaleGS_pnq4']
        qmergeEbt0 = data['fbqpub_mergeEbt_pnq0']
        qEbt0 = data['fbqpub_Ebt_pnq0']
        qmergeEbt0[qmergeEbt0.isna()] = qEbt0[qmergeEbt0.isna()]
        qmergeEbt4 = data['fbqpub_mergeEbt_pnq4']
        qEbt4 = data['fbqpub_Ebt_pnq4']
        qmergeEbt4[qmergeEbt4.isna()] = qEbt4[qmergeEbt4.isna()]
        qfinanExp0 = data['isqpub_finanExp_pnq0']
        qfinanExp4 = data['isqpub_finanExp_pnq4']
        qtRevenue0 = data['isqpub_tRevenue_pnq0']
        qtRevenue4 = data['isqpub_tRevenue_pnq4']
        qmergeprofit0 = data['fbqpub_mergeProfit_pnq0']
        qnIncomeAttrP0 = data['isqpub_nIncomeAttrP_pnq0']
        qmergeprofit0[qmergeprofit0.isna()] = qnIncomeAttrP0[
            qmergeprofit0.isna()]
        qmergeprofit1 = data['fbqpub_mergeProfit_pnq1']
        qnIncomeAttrP1 = data['isqpub_nIncomeAttrP_pnq1']
        qmergeprofit1[qmergeprofit1.isna()] = qnIncomeAttrP1[
            qmergeprofit1.isna()]
        qmergeprofit2 = data['fbqpub_mergeProfit_pnq2']
        qnIncomeAttrP2 = data['isqpub_nIncomeAttrP_pnq2']
        qmergeprofit2[qmergeprofit2.isna()] = qnIncomeAttrP2[
            qmergeprofit2.isna()]
        qmergeprofit3 = data['fbqpub_mergeProfit_pnq3']
        qnIncomeAttrP3 = data['isqpub_nIncomeAttrP_pnq3']
        qmergeprofit3[qmergeprofit3.isna()] = qnIncomeAttrP3[
            qmergeprofit3.isna()]
        qmergeprofit4 = data['fbqpub_mergeProfit_pnq4']
        qnIncomeAttrP4 = data['isqpub_nIncomeAttrP_pnq4']
        qmergeprofit4[qmergeprofit4.isna()] = qnIncomeAttrP4[
            qmergeprofit4.isna()]
        qmergeprofit5 = data['fbqpub_mergeProfit_pnq5']
        qnIncomeAttrP5 = data['isqpub_nIncomeAttrP_pnq5']
        qmergeprofit5[qmergeprofit5.isna()] = qnIncomeAttrP5[
            qmergeprofit5.isna()]
        qmergeprofit6 = data['fbqpub_mergeProfit_pnq6']
        qnIncomeAttrP6 = data['isqpub_nIncomeAttrP_pnq6']
        qmergeprofit6[qmergeprofit6.isna()] = qnIncomeAttrP6[
            qmergeprofit6.isna()]
        qmergeprofit7 = data['fbqpub_mergeProfit_pnq7']
        qnIncomeAttrP7 = data['isqpub_nIncomeAttrP_pnq7']
        qmergeprofit7[qmergeprofit7.isna()] = qnIncomeAttrP7[
            qmergeprofit7.isna()]

        sw1 = data['sw1']
        tradingday = sw1.index
        ticker = sw1.columns

        alpha_np = qmergeprofit0 / abs(qmergeprofit4)
        alpha_np[np.isinf(alpha_np)] = np.nan
        alpha_np = alpha_np.rank(pct=True, axis=1)
        alpha_cash = qcFRSaleGS0 / abs(qcFRSaleGS4)
        alpha_cash[np.isinf(alpha_cash)] = np.nan
        alpha_cash = alpha_cash.rank(pct=True, axis=1)
        alpha_ebit = qmergeEbt0.add(qfinanExp0, fill_value=0) / qmergeEbt4.add(
            qfinanExp4, fill_value=0)
        alpha_ebit[np.isinf(alpha_ebit)] = np.nan
        alpha_ebit = alpha_ebit.rank(pct=True, axis=1)
        alpha_sales = qtRevenue0 / abs(qtRevenue4)
        alpha_sales[np.isinf(alpha_sales)] = np.nan
        alpha_sales = alpha_sales.rank(pct=True, axis=1)

        f1 = alpha_np.copy()
        f1[:] = np.nan
        f1[(alpha_np > 0.7) & (alpha_sales > 0.7) & (alpha_cash > 0.5)] = 4
        f1[(alpha_np > 0.7) & (alpha_sales > 0.7) & (~(alpha_cash > 0.5))] = 3
        f1[(alpha_np > 0.7) & (~(alpha_sales > 0.7))] = 2
        f1[(alpha_np <= 0.7) & (alpha_np > 0.5) & (alpha_sales > 0.7)] = 1
        f1[(alpha_np <= 0.5) & (alpha_np > 0.3) & (alpha_sales < 0.3)] = -1
        f1[(alpha_np <= 0.3) & (alpha_cash < 0.5) & (alpha_sales < 0.3)] = -4
        f1[(alpha_np <= 0.3) & (~(alpha_cash < 0.5)) &
           (alpha_sales < 0.3)] = -3
        f1[(alpha_np <= 0.3) & (alpha_ebit < 0.3) &
           (~(alpha_sales < 0.3))] = -2
        f1 = f1.rank(pct=True, axis=1) - 0.5

        dfall = pd.concat([
            qmergeprofit0.unstack(),
            qmergeprofit1.unstack(),
            qmergeprofit2.unstack(),
            qmergeprofit3.unstack(),
            qmergeprofit4.unstack(),
            qmergeprofit5.unstack(),
            qmergeprofit6.unstack(),
            qmergeprofit7.unstack(),
        ],
                          axis=1)
        std_value = dfall.std(axis=1).reset_index()
        std_value = std_value.pivot_table(index='trade_date',
                                          columns='code',
                                          values=0)
        std_value = std_value.reindex(index=tradingday, columns=ticker)
        std_value[std_value == 0] = np.nan
        f2 = (qmergeprofit0 - qmergeprofit4) / std_value
        f2 = f2.rank(pct=True, axis=1) - 0.5
        factor = f1.add(f2, fill_value=0)
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_earning3")

    def factor_earning4(self,
                        data=None,
                        dependencies=[
                            'totalShares', 'closePrice', 'sw1', 'dummy120_fst',
                            'd', 'isqpub_nIncomeAttrP_pnq0'
                        ],
                        window=3 * 252):
        data = self._data if data is None else data
        d = data['d']
        dummy = data['dummy120_fst']
        qmergeprofit0 = data['fbqpub_mergeProfit_pnq0']
        qnIncomeAttrP0 = data['isqpub_nIncomeAttrP_pnq0']
        qmergeprofit0[qmergeprofit0.isna()] = qnIncomeAttrP0[
            qmergeprofit0.isna()]
        totalShares = data['totalShares']
        closePrice = data['closePrice']
        sw1 = data['sw1']
        dy_q_divout = d.rolling(3 * 252, min_periods=1).sum() / (
            qmergeprofit0.rolling(252 * 3, min_periods=1).sum() /
            totalShares.rolling(3 * 252, min_periods=1).mean())
        dy_q_divout[np.isinf(dy_q_divout)] = np.nan
        dy_q_pe_caldr = closePrice / (4 * qmergeprofit0 / totalShares)
        dy_q_pe_caldr[np.isinf(dy_q_pe_caldr)] = np.nan
        factor = dy_q_divout / dy_q_pe_caldr
        factor[np.isinf(factor)] = np.nan
        factor = indfill_median(factor * dummy, sw1)
        return self._format(factor, "factor_earning4")

    def factor_earning5(self,
                        data=None,
                        dependencies=[
                            'dummy120_fst', 'marketValue',
                            'fbqpub_mergeProfit_pnq0', 'sw1',
                            'bspub_tEquityAttrP_pnq0',
                            'isqpub_nIncomeAttrP_pnq0'
                        ],
                        window=1):
        data = self._data if data is None else data
        qmergeprofit0 = data['fbqpub_mergeProfit_pnq0']
        qnIncomeAttrP0 = data['isqpub_nIncomeAttrP_pnq0']
        qmergeprofit0[qmergeprofit0.isna()] = qnIncomeAttrP0[
            qmergeprofit0.isna()]
        dummy = data['dummy120_fst']
        mktcap = data['marketValue']
        tEquityAttrP0 = data['bspub_tEquityAttrP_pnq0']
        sw1 = data['sw1']
        roe = qmergeprofit0 / abs(tEquityAttrP0) * dummy
        roe[np.isinf(roe)] = np.nan
        bp = tEquityAttrP0 / mktcap * dummy
        bp[np.isinf(bp)] = np.nan
        factor = roe.rank(pct=True, axis=1) * bp.rank(pct=True, axis=1)
        factor = factor.sub(factor.mean(axis=1), axis='rows')
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_earning5")

    def factor_earning6(
            self,
            data=None,
            dependencies=[
                'dummy120_fst', 'sw1', 'fbqpub_mergeProfit_pnq0',
                'fbqpub_mergeProfit_pnq1', 'fbqpub_mergeProfit_pnq2',
                'fbqpub_mergeProfit_pnq3', 'fbqpub_mergeProfit_pnq4',
                'fbqpub_mergeProfit_pnq5', 'fbqpub_mergeProfit_pnq6',
                'fbqpub_mergeProfit_pnq7', 'totalShares',
                'isqpub_nIncomeAttrP_pnq1', 'isqpub_nIncomeAttrP_pnq2',
                'isqpub_nIncomeAttrP_pnq3', 'isqpub_nIncomeAttrP_pnq4',
                'isqpub_nIncomeAttrP_pnq5', 'isqpub_nIncomeAttrP_pnq6',
                'isqpub_nIncomeAttrP_pnq7'
            ],
            window=240):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        totalShares = data['totalShares']
        tradingday = sw1.index
        ticker = sw1.columns
        f0 = data['fbqpub_mergeProfit_pnq0']
        f0m = data['isqpub_nIncomeAttrP_pnq0']
        f0[f0.isna()] = f0m[f0.isna()]
        f1 = data['fbqpub_mergeProfit_pnq1']
        f1m = data['isqpub_nIncomeAttrP_pnq1']
        f1[f1.isna()] = f1m[f1.isna()]
        f2 = data['fbqpub_mergeProfit_pnq2']
        f2m = data['isqpub_nIncomeAttrP_pnq2']
        f2[f2.isna()] = f2m[f2.isna()]
        f3 = data['fbqpub_mergeProfit_pnq3']
        f3m = data['isqpub_nIncomeAttrP_pnq3']
        f3[f3.isna()] = f3m[f3.isna()]
        f4 = data['fbqpub_mergeProfit_pnq4']
        f4m = data['isqpub_nIncomeAttrP_pnq4']
        f4[f4.isna()] = f4m[f4.isna()]
        f5 = data['fbqpub_mergeProfit_pnq5']
        f5m = data['isqpub_nIncomeAttrP_pnq5']
        f5[f5.isna()] = f5m[f5.isna()]
        f6 = data['fbqpub_mergeProfit_pnq6']
        f6m = data['isqpub_nIncomeAttrP_pnq6']
        f6[f6.isna()] = f6m[f6.isna()]
        f7 = data['fbqpub_mergeProfit_pnq7']
        f7m = data['isqpub_nIncomeAttrP_pnq7']
        f7[f7.isna()] = f7m[f7.isna()]
        dfall = pd.concat([
            f0.unstack(),
            f1.unstack(),
            f2.unstack(),
            f3.unstack(),
            f4.unstack(),
            f5.unstack(),
            f6.unstack(),
            f7.unstack()
        ],
                          axis=1)
        epsall = dfall.div(totalShares.unstack(), axis="rows")
        epsstd = epsall.std(axis=1).reset_index()
        epsstd = epsstd.pivot_table(index="trade_date",
                                    columns="code",
                                    values=0)
        epsstd = epsstd.reindex(index=tradingday, columns=ticker)
        epsstd[epsstd == 0] = np.nan
        epsmean = epsall.mean(axis=1).reset_index()
        epsmean = epsmean.pivot_table(index="trade_date",
                                      columns="code",
                                      values=0)
        epsmean = epsmean.reindex(index=tradingday, columns=ticker)
        eps0 = f0 / totalShares
        f1 = (eps0 - epsmean) / abs(epsstd)
        f1[np.isinf(f1)] = np.nan
        nistd = dfall.std(axis=1).reset_index()
        nistd = nistd.pivot_table(index="trade_date", columns="code", values=0)
        nistd = nistd.reindex(index=tradingday, columns=ticker)
        nistd[nistd == 0] = np.nan
        nimean = dfall.mean(axis=1).reset_index()
        nimean = nimean.pivot_table(index="trade_date",
                                    columns="code",
                                    values=0)
        nimean = nimean.reindex(index=tradingday, columns=ticker)
        f2 = (f0 - nimean) / abs(nistd)
        f3 = f0.rolling(240, min_periods=120).rank(pct=True)
        factor = factor_merge([f1, f2, f3])
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_earning6")

    def factor_earning7(self,
                        data=None,
                        dependencies=[
                            'dummy120_fst', 'fbqpub_Ebit_pnq0',
                            'bspub_tAssets_pnq0', 'sw1'
                        ],
                        window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        f0 = data['fbqpub_Ebit_pnq0']
        tAssets0 = data['bspub_tAssets_pnq0']
        factor = f0 / tAssets0
        factor[np.isinf(factor)] = np.nan
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_earning7")

    def factor_earning8(self,
                        data=None,
                        dependencies=[
                            'dummy120_fst',
                            'marketValue',
                            'cfqpub_cPaidToForEmpl_pnq0',
                            'sw1',
                        ],
                        window=1):
        data = self._data if data is None else data
        qcPaidToForEmpl0 = data['cfqpub_cPaidToForEmpl_pnq0']
        dummy = data['dummy120_fst']
        mktcap = data['marketValue']
        sw1 = data['sw1']
        f = factor_score(qcPaidToForEmpl0 * dummy, 1).rank(pct=True,
                                                           axis=1) - 0.5
        dfall = pd.DataFrame(mktcap.unstack(), columns=['mktcap'])
        dfall.index.names = ['code', 'trade_date']
        out1 = alphaOpNeu(f, dfall)
        factor = standardize(factor_score(indLineNeu(out1, sw1), 3))
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_earning8")

    def factor_earning9(
            self,
            data=None,
            dependencies=[
                'dummy120_fst', 'sw1', 'bspub_capitalReser_pnq0',
                'bspub_capitalReser_pnq1', 'bspub_capitalReser_pnq2',
                'bspub_capitalReser_pnq3', 'bspub_capitalReser_pnq4',
                'bspub_capitalReser_pnq5', 'bspub_capitalReser_pnq6',
                'bspub_capitalReser_pnq7', 'bspub_capitalReser_pnq8',
                'bspub_capitalReser_pnq9', 'bspub_capitalReser_pnq10',
                'bspub_capitalReser_pnq11'
            ],
            window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        tradingday = dummy.index
        ticker = dummy.columns
        f0 = data['bspub_capitalReser_pnq0']
        f1 = data['bspub_capitalReser_pnq1']
        f2 = data['bspub_capitalReser_pnq2']
        f3 = data['bspub_capitalReser_pnq3']
        f4 = data['bspub_capitalReser_pnq4']
        f5 = data['bspub_capitalReser_pnq5']
        f6 = data['bspub_capitalReser_pnq6']
        f7 = data['bspub_capitalReser_pnq7']
        f8 = data['bspub_capitalReser_pnq8']
        f9 = data['bspub_capitalReser_pnq9']
        f10 = data['bspub_capitalReser_pnq10']
        f11 = data['bspub_capitalReser_pnq11']
        dfall = pd.concat([
            f0.unstack(),
            f1.unstack(),
            f2.unstack(),
            f3.unstack(),
            f4.unstack(),
            f5.unstack(),
            f6.unstack(),
            f7.unstack(),
            f8.unstack(),
            f9.unstack(),
            f10.unstack(),
            f11.unstack()
        ],
                          axis=1)
        dfstd = dfall.std(axis=1).reset_index()
        dfstd = dfstd.pivot_table(index='trade_date', columns='code', values=0)
        dfstd = dfstd.reindex(index=tradingday, columns=ticker)
        dfstd[dfstd == 0] = np.nan
        factor = -f0 / dfstd
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_earning9")

    def factor_earning10(
            self,
            data=None,
            dependencies=[
                'dummy120_fst', 'isqpub_finanExp_pnq0', 'marketValue',
                'fbqpub_mergeProfit_pnq0', 'fbqpub_mergeEbt_pnq0',
                'bspub_tAssets_pnq0', 'bspub_tAssets_pnq1', 'bspub_tLiab_pnq0',
                'bspub_tLiab_pnq1', 'isqpub_tRevenue_pnq0',
                'isqpub_tRevenue_pnq4', 'isqpub_finanExp_pnq4',
                'fbqpub_mergeEbt_pnq4', 'bspub_tAssets_pnq4',
                'bspub_tAssets_pnq5', 'sw1', 'isqpub_nIncomeAttrP_pnq0',
                'fbqpub_Ebt_pnq0', 'fbqpub_Ebt_pnq4'
            ],
            window=1):
        data = self._data if data is None else data
        qmergeprofit0 = data['fbqpub_mergeProfit_pnq0']
        qnIncomeAttrP0 = data['isqpub_nIncomeAttrP_pnq0']
        qmergeprofit0[qmergeprofit0.isna()] = qnIncomeAttrP0[
            qmergeprofit0.isna()]
        qmergeEbt0 = data['fbqpub_mergeEbt_pnq0']
        qEbt0 = data['fbqpub_Ebt_pnq0']
        qmergeEbt0[qmergeEbt0.isna()] = qEbt0[qmergeEbt0.isna()]
        dummy = data['dummy120_fst']
        mktcap = data['marketValue']
        tAssets0 = data['bspub_tAssets_pnq0']
        tAssets1 = data['bspub_tAssets_pnq1']
        tAssets4 = data['bspub_tAssets_pnq4']
        tAssets5 = data['bspub_tAssets_pnq5']
        tLiab0 = data['bspub_tLiab_pnq0']
        tLiab1 = data['bspub_tLiab_pnq1']
        qfinanExp0 = data['isqpub_finanExp_pnq0']
        qfinanExp4 = data['isqpub_finanExp_pnq4']
        qtRevenue0 = data['isqpub_tRevenue_pnq0']
        qtRevenue4 = data['isqpub_tRevenue_pnq4']
        qmergeEbt4 = data['fbqpub_mergeEbt_pnq4']
        qEbt4 = data['fbqpub_Ebt_pnq4']
        qmergeEbt4[qmergeEbt4.isna()] = qEbt4[qmergeEbt4.isna()]
        sw1 = data['sw1']
        tradingday = sw1.index
        ticker = sw1.columns
        tax_ratio_vector = qmergeprofit0 / qmergeEbt0
        tax_ratio_vector[np.isinf(tax_ratio_vector)] = np.nan
        eq = (tAssets0.sub(tLiab0,
                           fill_value=0)).add(tAssets1.sub(tLiab1,
                                                           fill_value=0),
                                              fill_value=0)
        roe_ratio_vector = qmergeprofit0 / eq
        roe_ratio_vector[np.isinf(roe_ratio_vector)] = np.nan
        interest_ratio_vector = qmergeEbt0 / (qmergeEbt0.add(qfinanExp0,
                                                             fill_value=0))
        interest_ratio_vector[np.isinf(interest_ratio_vector)] = np.nan
        alpha = tax_ratio_vector.copy()
        alpha[:] = np.nan
        alpha[tax_ratio_vector > 0.9] = roe_ratio_vector[
            tax_ratio_vector > 0.9] / tax_ratio_vector[tax_ratio_vector >
                                                       0.9] * 0.9
        alpha[tax_ratio_vector <= 0.9] = roe_ratio_vector[tax_ratio_vector <=
                                                          0.9]
        alpha[interest_ratio_vector > 0.8] = roe_ratio_vector[
            interest_ratio_vector > 0.8] / interest_ratio_vector[
                interest_ratio_vector > 0.8] * 0.8
        alpha[interest_ratio_vector <= 0.8] = roe_ratio_vector[
            interest_ratio_vector <= 0.8]
        alpha[np.isinf(alpha)] = np.nan
        alpha = alpha.rank(pct=True, axis=1)
        turnover_alpha = qtRevenue0 / tAssets0.add(
            tAssets1, fill_value=0) - qtRevenue4 / tAssets4.add(tAssets5,
                                                                fill_value=0)
        turnover_alpha[np.isinf(turnover_alpha)] = np.nan
        turnover_alpha = turnover_alpha.rank(pct=True, axis=1)
        profit_alpha = qmergeEbt0.add(
            qfinanExp0, fill_value=0) / qtRevenue0 - qmergeEbt4.add(
                qfinanExp4, fill_value=0) / qtRevenue4
        profit_alpha[np.isinf(profit_alpha)] = np.nan
        profit_alpha = profit_alpha.rank(pct=True, axis=1)
        leverage_alpha = tAssets0.add(tAssets1, fill_value=0) / eq
        leverage_alpha[np.isinf(leverage_alpha)] = np.nan

        dfall = pd.concat([leverage_alpha.unstack(), sw1.unstack()], axis=1)
        dfall.columns = ['leverage', 'sw1']
        dfall.reset_index(inplace=True)
        dfall['le'] = dfall.groupby(['trade_date',
                                     'sw1'])['leverage'].rank(pct=True)
        leverage_alpha = dfall.pivot_table(index='trade_date',
                                           columns='code',
                                           values='le')
        leverage_alpha = leverage_alpha.reindex(index=tradingday,
                                                columns=ticker)

        roe_vector = alpha.copy()
        roe_vector[(alpha > 0.5)
                   & ((turnover_alpha > 0.7)
                      | (profit_alpha > 0.7))] = roe_vector[(alpha > 0.5) & (
                          (turnover_alpha > 0.7) | (profit_alpha > 0.7))] + 0.5
        roe_vector[(alpha > 0.5)
                   & (~((turnover_alpha > 0.7) | (profit_alpha > 0.7))) &
                   (leverage_alpha > 0.35)] = np.nan
        roe_vector[(alpha <= 0.5)
                   & ((turnover_alpha < 0.3)
                      | (profit_alpha < 0.3))] = roe_vector[(alpha <= 0.5) & (
                          (turnover_alpha < 0.3) | (profit_alpha < 0.3))] - 0.5
        roe_vector[(alpha <= 0.5)
                   & (~((turnover_alpha < 0.3) | (profit_alpha < 0.3))) &
                   (leverage_alpha < -0.35)] = np.nan

        roe_vector = roe_vector.rank(pct=True, axis=1).unstack()
        asset_vector = mktcap.rank(pct=True, axis=1).unstack()

        dfall = pd.concat([roe_vector, asset_vector, sw1.unstack()], axis=1)
        dfall.columns = ['roe', 'asset', 'sw1']
        dfall.reset_index(inplace=True)
        group_corr1 = dfall.groupby(
            ['trade_date', 'sw1'])[['roe', 'asset']].apply(lambda x: x[
                'roe'].corr(x['asset']) * x['roe'].std() / x['asset'].std())
        group_corr1[np.isinf(group_corr1)] = np.nan
        group_corr1.name = 'group_corr1'
        dfall = dfall.merge(group_corr1.reset_index(),
                            on=['trade_date', 'sw1'],
                            how='left')

        dfall['inter'] = dfall['roe'] - dfall['group_corr1'] * dfall['asset']
        group_intercept1 = dfall.groupby(['trade_date', 'sw1'])['inter'].mean()
        group_intercept1.name = 'group_intercept1'
        dfall = dfall.merge(group_intercept1.reset_index(),
                            on=['trade_date', 'sw1'],
                            how='left')
        dfall['factor'] = dfall['roe'] - dfall['group_corr1'] * dfall[
            'asset'] - dfall['group_intercept1']
        factor = dfall.pivot_table(index='trade_date',
                                   columns='code',
                                   values='factor')
        factor = factor.reindex(index=tradingday, columns=ticker)
        factor[np.isinf(factor)] = np.nan
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_earning10")

    def factor_earning11(self,
                         data=None,
                         dependencies=['dummy120_fst', 'ffancy_aiSude', 'sw1'],
                         window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        factor = data['ffancy_aiSude']
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_earning11")

    def factor_earning12(self,
                         data=None,
                         dependencies=['dummy120_fst', 'ffancy_lpnpQ', 'sw1'],
                         window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        factor = data['ffancy_lpnpQ']
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_earning12")

    def factor_earning13(self,
                         data=None,
                         dependencies=['dummy120_fst', 'ffancy_rrocQ', 'sw1'],
                         window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        factor = data['ffancy_rrocQ']
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_earning13")

    def factor_earning14(self,
                         data=None,
                         dependencies=[
                             'dummy120_fst', 'bspub_tAssets_pnq0',
                             'ispub_rDExp_pnq0', 'sw1'
                         ],
                         window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        f0 = data['ispub_rDExp_pnq0']
        tAssets0 = data['bspub_tAssets_pnq0']
        factor = f0 / tAssets0
        factor[np.isinf(factor)] = np.nan
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_earning14")

    def factor_earning15(
            self,
            data=None,
            dependencies=[
                'dummy120_fst', 'bspub_surplusReser_pnq0',
                'bspub_surplusReser_pnq1', 'bspub_surplusReser_pnq2',
                'bspub_surplusReser_pnq3', 'bspub_surplusReser_pnq4',
                'bspub_surplusReser_pnq5', 'bspub_surplusReser_pnq6',
                'bspub_surplusReser_pnq7', 'bspub_surplusReser_pnq8',
                'bspub_surplusReser_pnq9', 'bspub_surplusReser_pnq10',
                'bspub_surplusReser_pnq11', 'sw1'
            ],
            window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        tradingday = dummy.index
        ticker = dummy.columns
        f0 = data['bspub_surplusReser_pnq0']
        f1 = data['bspub_surplusReser_pnq1']
        f2 = data['bspub_surplusReser_pnq2']
        f3 = data['bspub_surplusReser_pnq3']
        f4 = data['bspub_surplusReser_pnq4']
        f5 = data['bspub_surplusReser_pnq5']
        f6 = data['bspub_surplusReser_pnq6']
        f7 = data['bspub_surplusReser_pnq7']
        f8 = data['bspub_surplusReser_pnq8']
        f9 = data['bspub_surplusReser_pnq9']
        f10 = data['bspub_surplusReser_pnq10']
        f11 = data['bspub_surplusReser_pnq11']
        dfall = pd.concat([
            f0.unstack(),
            f1.unstack(),
            f2.unstack(),
            f3.unstack(),
            f4.unstack(),
            f5.unstack(),
            f6.unstack(),
            f7.unstack(),
            f8.unstack(),
            f9.unstack(),
            f10.unstack(),
            f11.unstack()
        ],
                          axis=1)
        dfstd = dfall.std(axis=1).reset_index()
        dfstd = dfstd.pivot_table(index='trade_date', columns='code', values=0)
        dfstd = dfstd.reindex(index=tradingday, columns=ticker)
        dfstd[dfstd == 0] = np.nan
        factor = -f0 / dfstd
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_earning15")

    def factor_earning16(self,
                         data=None,
                         dependencies=[
                             'dummy120_fst', 'bspub_tAssets_pnq0',
                             'fbqpub_mergeProfit_pnq0', 'sw1',
                             'isqpub_nIncomeAttrP_pnq0'
                         ],
                         window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        f0 = data['fbqpub_mergeProfit_pnq0']
        f0m = data['isqpub_nIncomeAttrP_pnq0']
        f0[f0.isna()] = f0m[f0.isna()]
        tAssets0 = data['bspub_tAssets_pnq0']
        factor = f0 / tAssets0
        factor[np.isinf(factor)] = np.nan
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_earning16")

    def factor_earning17(
            self,
            data=None,
            dependencies=[
                'dummy120_fst', 'bspub_tNcl_pnq0', 'bspub_tNcl_pnq1',
                'bspub_tNcl_pnq2', 'bspub_tNcl_pnq3', 'bspub_tNcl_pnq4',
                'bspub_tNcl_pnq5', 'bspub_tNcl_pnq6', 'bspub_tNcl_pnq7',
                'bspub_tNcl_pnq8', 'bspub_tNcl_pnq9', 'bspub_tNcl_pnq10',
                'bspub_tNcl_pnq11', 'sw1'
            ],
            window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        tradingday = dummy.index
        ticker = dummy.columns
        f0 = data['bspub_tNcl_pnq0']
        f1 = data['bspub_tNcl_pnq1']
        f2 = data['bspub_tNcl_pnq2']
        f3 = data['bspub_tNcl_pnq3']
        f4 = data['bspub_tNcl_pnq4']
        f5 = data['bspub_tNcl_pnq5']
        f6 = data['bspub_tNcl_pnq6']
        f7 = data['bspub_tNcl_pnq7']
        f8 = data['bspub_tNcl_pnq8']
        f9 = data['bspub_tNcl_pnq9']
        f10 = data['bspub_tNcl_pnq10']
        f11 = data['bspub_tNcl_pnq11']
        dfall = pd.concat([
            f0.unstack(),
            f1.unstack(),
            f2.unstack(),
            f3.unstack(),
            f4.unstack(),
            f5.unstack(),
            f6.unstack(),
            f7.unstack(),
            f8.unstack(),
            f9.unstack(),
            f10.unstack(),
            f11.unstack()
        ],
                          axis=1)
        dfstd = dfall.std(axis=1).reset_index()
        dfstd = dfstd.pivot_table(index='trade_date', columns='code', values=0)
        dfstd = dfstd.reindex(index=tradingday, columns=ticker)
        dfstd[dfstd == 0] = np.nan
        factor = -f0 / dfstd
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_earning17")

    def factor_earning18(self,
                         data=None,
                         dependencies=[
                             'dummy120_fst', 'totalShares',
                             'fbqpub_mergeEbt_pnq0', 'sw1', 'fbqpub_Ebt_pnq0'
                         ],
                         window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        f0 = data['fbqpub_mergeEbt_pnq0']
        qEbt0 = data['fbqpub_Ebt_pnq0']
        f0[f0.isna()] = qEbt0[f0.isna()]
        totalShares = data['totalShares']
        factor = f0 / totalShares
        factor[np.isinf(factor)] = np.nan
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_earning18")

    def factor_earning19(
            self,
            data=None,
            dependencies=[
                'dummy120_fst', 'isqpub_aJInvestIncome_pnq0',
                'isqpub_aJInvestIncome_pnq1', 'isqpub_aJInvestIncome_pnq2',
                'isqpub_aJInvestIncome_pnq3', 'isqpub_aJInvestIncome_pnq4',
                'isqpub_aJInvestIncome_pnq5', 'isqpub_aJInvestIncome_pnq6',
                'isqpub_aJInvestIncome_pnq7', 'isqpub_aJInvestIncome_pnq8',
                'isqpub_aJInvestIncome_pnq9', 'isqpub_aJInvestIncome_pnq10',
                'isqpub_aJInvestIncome_pnq11', 'sw1'
            ],
            window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        tradingday = dummy.index
        ticker = dummy.columns
        f0 = data['isqpub_aJInvestIncome_pnq0']
        f1 = data['isqpub_aJInvestIncome_pnq1']
        f2 = data['isqpub_aJInvestIncome_pnq2']
        f3 = data['isqpub_aJInvestIncome_pnq3']
        f4 = data['isqpub_aJInvestIncome_pnq4']
        f5 = data['isqpub_aJInvestIncome_pnq5']
        f6 = data['isqpub_aJInvestIncome_pnq6']
        f7 = data['isqpub_aJInvestIncome_pnq7']
        f8 = data['isqpub_aJInvestIncome_pnq8']
        f9 = data['isqpub_aJInvestIncome_pnq9']
        f10 = data['isqpub_aJInvestIncome_pnq10']
        f11 = data['isqpub_aJInvestIncome_pnq11']
        dfall = pd.concat([
            f0.unstack(),
            f1.unstack(),
            f2.unstack(),
            f3.unstack(),
            f4.unstack(),
            f5.unstack(),
            f6.unstack(),
            f7.unstack(),
            f8.unstack(),
            f9.unstack(),
            f10.unstack(),
            f11.unstack()
        ],
                          axis=1)
        dfstd = dfall.std(axis=1).reset_index()
        dfstd = dfstd.pivot_table(index='trade_date', columns='code', values=0)
        dfstd = dfstd.reindex(index=tradingday, columns=ticker)
        dfstd[dfstd == 0] = np.nan
        factor = f0 / dfstd
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_earning19")

    def factor_earning20(
            self,
            data=None,
            dependencies=[
                'dummy120_fst', 'sw1', 'fbpub_mergeProfit_pnq0',
                'fbpub_mergeProfit_pnq1', 'fbpub_mergeProfit_pnq2',
                'fbpub_mergeProfit_pnq3', 'fbpub_mergeProfit_pnq4',
                'fbpub_mergeProfit_pnq5', 'fbpub_mergeProfit_pnq6',
                'fbpub_mergeProfit_pnq7', 'fbpub_mergeProfit_pnq8',
                'fbpub_mergeProfit_pnq9', 'fbpub_mergeProfit_pnq10',
                'fbpub_mergeProfit_pnq11', 'ispub_nIncomeAttrP_pnq0',
                'ispub_nIncomeAttrP_pnq1', 'ispub_nIncomeAttrP_pnq2',
                'ispub_nIncomeAttrP_pnq3', 'ispub_nIncomeAttrP_pnq4',
                'ispub_nIncomeAttrP_pnq5', 'ispub_nIncomeAttrP_pnq6',
                'ispub_nIncomeAttrP_pnq7', 'ispub_nIncomeAttrP_pnq8',
                'ispub_nIncomeAttrP_pnq9', 'ispub_nIncomeAttrP_pnq10',
                'ispub_nIncomeAttrP_pnq11'
            ],
            window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        tradingday = sw1.index
        ticker = sw1.columns
        f0 = data['fbpub_mergeProfit_pnq0']
        f0m = data['ispub_nIncomeAttrP_pnq0']
        f0[f0.isna()] = f0m[f0.isna()]
        f1 = data['fbpub_mergeProfit_pnq1']
        f1m = data['ispub_nIncomeAttrP_pnq1']
        f1[f1.isna()] = f1m[f1.isna()]
        f2 = data['fbpub_mergeProfit_pnq2']
        f2m = data['ispub_nIncomeAttrP_pnq2']
        f2[f2.isna()] = f2m[f2.isna()]
        f3 = data['fbpub_mergeProfit_pnq3']
        f3m = data['ispub_nIncomeAttrP_pnq3']
        f3[f3.isna()] = f3m[f3.isna()]
        f4 = data['fbpub_mergeProfit_pnq4']
        f4m = data['ispub_nIncomeAttrP_pnq4']
        f4[f4.isna()] = f4m[f4.isna()]
        f5 = data['fbpub_mergeProfit_pnq5']
        f5m = data['ispub_nIncomeAttrP_pnq5']
        f5[f5.isna()] = f5m[f5.isna()]
        f6 = data['fbpub_mergeProfit_pnq6']
        f6m = data['ispub_nIncomeAttrP_pnq6']
        f6[f6.isna()] = f6m[f6.isna()]
        f7 = data['fbpub_mergeProfit_pnq7']
        f7m = data['ispub_nIncomeAttrP_pnq7']
        f7[f7.isna()] = f7m[f7.isna()]
        f8 = data['fbpub_mergeProfit_pnq8']
        f8m = data['ispub_nIncomeAttrP_pnq8']
        f8[f8.isna()] = f8m[f8.isna()]
        f9 = data['fbpub_mergeProfit_pnq9']
        f9m = data['ispub_nIncomeAttrP_pnq9']
        f9[f9.isna()] = f9m[f9.isna()]
        f10 = data['fbpub_mergeProfit_pnq10']
        f10m = data['ispub_nIncomeAttrP_pnq10']
        f10[f10.isna()] = f10m[f10.isna()]
        f11 = data['fbpub_mergeProfit_pnq11']
        f11m = data['ispub_nIncomeAttrP_pnq11']
        f11[f11.isna()] = f11m[f11.isna()]
        dfall = pd.concat([
            f0.unstack(),
            f1.unstack(),
            f2.unstack(),
            f3.unstack(),
            f4.unstack(),
            f5.unstack(),
            f6.unstack(),
            f7.unstack(),
            f8.unstack(),
            f9.unstack(),
            f10.unstack(),
            f11.unstack()
        ],
                          axis=1)
        dfstd = dfall.std(axis=1).reset_index()
        dfstd = dfstd.pivot_table(index='trade_date', columns='code', values=0)
        dfstd = dfstd.reindex(index=tradingday, columns=ticker)
        dfstd[dfstd == 0] = np.nan
        factor = f0 / dfstd
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_earning20")