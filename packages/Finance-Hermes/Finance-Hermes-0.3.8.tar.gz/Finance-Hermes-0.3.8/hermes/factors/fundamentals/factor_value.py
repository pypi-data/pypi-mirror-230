# -*- encoding:utf-8 -*-
import numpy as np
import pandas as pd
from alphakit.const import *
from alphakit.factor import *
from alphakit.portfolio import *
from alphakit.data import *
from ultron.factor.data.neutralize import neutralize

from hermes.factors.base import FactorBase, LongCallMixin, ShortCallMixin
from jdwdata.RetrievalAPI import get_data_by_map


class FactorValue(FactorBase, LongCallMixin, ShortCallMixin):

    def __init__(self, data_format, **kwargs):
        __str__ = 'factor_value'
        self.category = 'Value'
        self.name = '估值因子'
        self._data_format = data_format
        self._data = self.init_data(**kwargs) if 'end_date' in kwargs else None
        data = get_data_by_map(columns=BARRA_ALL_K,
                               begin_date=self.begin_date,
                               end_date=self.end_date,
                               method='ddb')
        self._risksizeindu = getdataset(data, BARRA_SIZEIND_K)

    def _init_self(self, **kwargs):
        pass

    def factor_value1(
            self,
            data=None,
            dependencies=[
                'dummy120_fst', 'sw1', 'isqpub_tRevenue_pnq0',
                'isqpub_tRevenue_pnq1', 'isqpub_tRevenue_pnq2',
                'isqpub_tRevenue_pnq3', 'isqpub_COGS_pnq0', 'isqpub_COGS_pnq1',
                'isqpub_COGS_pnq2', 'isqpub_COGS_pnq3', 'isqpub_sellExp_pnq0',
                'isqpub_sellExp_pnq1', 'isqpub_sellExp_pnq2',
                'isqpub_sellExp_pnq3', 'isqpub_bizTaxSurchg_pnq0',
                'isqpub_bizTaxSurchg_pnq1', 'isqpub_bizTaxSurchg_pnq2',
                'isqpub_bizTaxSurchg_pnq3'
            ],
            window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        qtRevenue0 = data['isqpub_tRevenue_pnq0']
        qtRevenue1 = data['isqpub_tRevenue_pnq1']
        qtRevenue2 = data['isqpub_tRevenue_pnq2']
        qtRevenue3 = data['isqpub_tRevenue_pnq3']
        qcogs0 = data['isqpub_COGS_pnq0']
        qcogs1 = data['isqpub_COGS_pnq1']
        qcogs2 = data['isqpub_COGS_pnq2']
        qcogs3 = data['isqpub_COGS_pnq3']
        qsellExp0 = data['isqpub_sellExp_pnq0']
        qsellExp1 = data['isqpub_sellExp_pnq1']
        qsellExp2 = data['isqpub_sellExp_pnq2']
        qsellExp3 = data['isqpub_sellExp_pnq3']
        qbizTaxSurchg0 = data['isqpub_bizTaxSurchg_pnq0']
        qbizTaxSurchg1 = data['isqpub_bizTaxSurchg_pnq1']
        qbizTaxSurchg2 = data['isqpub_bizTaxSurchg_pnq2']
        qbizTaxSurchg3 = data['isqpub_bizTaxSurchg_pnq3']
        sw1 = data['sw1']
        tradingday = sw1.index
        ticker = sw1.columns
        dfall = pd.concat([(qtRevenue0.sub(qcogs0, fill_value=0).sub(
            qsellExp0, fill_value=0).sub(qbizTaxSurchg0,
                                         fill_value=0)).unstack(),
                           (qtRevenue1.sub(qcogs1, fill_value=0).sub(
                               qsellExp1, fill_value=0).sub(
                                   qbizTaxSurchg1, fill_value=0)).unstack(),
                           (qtRevenue2.sub(qcogs2, fill_value=0).sub(
                               qsellExp2, fill_value=0).sub(
                                   qbizTaxSurchg2, fill_value=0)).unstack(),
                           (qtRevenue3.sub(qcogs3, fill_value=0).sub(
                               qsellExp3, fill_value=0).sub(
                                   qbizTaxSurchg3, fill_value=0)).unstack()],
                          axis=1)
        vstd = dfall.std(axis=1)
        vstd[vstd == 0] = 0
        f = (dfall.iloc[:, 0] - dfall.mean(axis=1)) / vstd
        f = pd.DataFrame(f).reset_index()
        factor = f.pivot_table(index='trade_date', columns='code', values=0)
        factor = factor.reindex(index=tradingday, columns=ticker)
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_value1")

    def factor_value2(self,
                      data=None,
                      dependencies=[
                          'dummy120_fst', 'totalShares', 'closePrice', 'sw1',
                          'fbqpub_mergeOprofit_pnq0', 'bspub_tLiab_pnq0',
                          'isqpub_operateProfit_pnq0'
                      ],
                      window=1):
        data = self._data if data is None else data
        totalShares = data['totalShares']
        dummy = data['dummy120_fst']
        closePrice = data['closePrice']
        closePrice[closePrice <= 0] = np.nan
        totalShares[totalShares <= 0] = np.nan
        sw1 = data['sw1']
        qmergeOprofit0 = data['fbqpub_mergeOprofit_pnq0']
        qoperateProfit0 = data['isqpub_operateProfit_pnq0']
        qmergeOprofit0[qmergeOprofit0.isna()] = qoperateProfit0[
            qmergeOprofit0.isna()]
        tLiab0 = data['bspub_tLiab_pnq0']
        factor = qmergeOprofit0 / (totalShares * closePrice).add(tLiab0,
                                                                 fill_value=0)
        factor[np.isinf(factor)] = np.nan
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_value2")

    def factor_value3(self,
                      data=None,
                      dependencies=[
                          'dummy120_fst', 'sw1', 'fbqpub_mergeProfit_pnq0',
                          'isqpub_nIncomeAttrP_pnq0', 'totalShares',
                          'closePrice'
                      ],
                      window=245):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        totalShares = data['totalShares']
        closePrice = data['closePrice']
        closePrice[closePrice <= 0] = np.nan
        totalShares[totalShares <= 0] = np.nan
        qmergeprofit0 = data['fbqpub_mergeProfit_pnq0']
        qnIncomeAttrP0 = data['isqpub_nIncomeAttrP_pnq0']
        qmergeprofit0[qmergeprofit0.isna()] = qnIncomeAttrP0[
            qmergeprofit0.isna()]
        v = qmergeprofit0 / totalShares / closePrice
        factor = v / v.shift(245) - 1
        factor[np.isinf(factor)] = np.nan
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_value3")

    def factor_value4(self,
                      data=None,
                      dependencies=[
                          'dummy120_fst', 'sw1', 'bspub_tLiab_pnq0',
                          'bspub_cashCEquiv_pnq0', 'marketValue',
                          'bspub_minorityInt_pnq0', 'fbqpub_mergeIncome_pnq0',
                          'isqpub_COGS_pnq0', 'isqpub_revenue_pnq0'
                      ],
                      window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        tLiab0 = data['bspub_tLiab_pnq0']
        minorityInt0 = data['bspub_minorityInt_pnq0']
        cashCEquiv0 = data['bspub_cashCEquiv_pnq0']
        qcogs0 = data['isqpub_COGS_pnq0']
        qmergeIncome0 = data['fbqpub_mergeIncome_pnq0']
        qrevenue0 = data['isqpub_revenue_pnq0']
        qmergeIncome0[qmergeIncome0.isna()] = qrevenue0[qmergeIncome0.isna()]
        mktcap = data['marketValue']
        ev = mktcap.add(tLiab0,
                        fill_value=0).add(minorityInt0,
                                          fill_value=0).sub(cashCEquiv0,
                                                            fill_value=0)
        ev[ev == 0] = np.nan
        factor = abs(qmergeIncome0.sub(qcogs0, fill_value=0) / ev)
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_value4")

    def factor_value5(self,
                      data=None,
                      dependencies=[
                          'dummy120_fst', 'sw1', 'f_SIZE', 'totalShares',
                          'marketValue', 'fbqpub_mergeProfit_pnq0',
                          'isqpub_tRevenue_pnq0', 'bspub_tAssets_pnq0',
                          'contar_conTarPrice', 'isqpub_nIncomeAttrP_pnq0'
                      ],
                      window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        qmergeprofit0 = data['fbqpub_mergeProfit_pnq0']
        qnIncomeAttrP0 = data['isqpub_nIncomeAttrP_pnq0']
        qmergeprofit0[qmergeprofit0.isna()] = qnIncomeAttrP0[
            qmergeprofit0.isna()]
        totalShares = data['totalShares']
        totalShares[totalShares <= 0] = np.nan
        conTarPrice = data['contar_conTarPrice']
        qtRevenue0 = data['isqpub_tRevenue_pnq0']
        mktcap = data['marketValue']
        tAssets0 = data['bspub_tAssets_pnq0']
        size = data['f_SIZE']
        sw1 = data['sw1']
        tradingday = sw1.index
        ticker = sw1.columns

        eps = qmergeprofit0 / totalShares * dummy
        f1 = eps / conTarPrice
        f1[np.isinf(f1)] = np.nan

        dfall = pd.concat(
            [eps.unstack(),
             qtRevenue0.unstack(),
             mktcap.unstack()], axis=1)
        dfall.columns = ['eps', 'revenue', 'size']
        dfall['inter'] = 1.0
        dfall.reset_index(inplace=True)
        dfall.dropna(inplace=True)
        dfall.reset_index(inplace=True, drop=True)
        retdbeta = neutralize(dfall[['eps', 'revenue', 'inter']].values,
                              dfall['size'].values,
                              groups=dfall['trade_date'].values)
        ret_dbeta = dfall[['trade_date', 'code']].copy()
        ret_dbeta['adjfactor'] = retdbeta
        adjdata = ret_dbeta.pivot_table(index='trade_date',
                                        columns='code',
                                        values='adjfactor')
        redata = adjdata.reindex(index=tradingday, columns=ticker)
        f2 = (mktcap - redata) / mktcap
        f2[np.isinf(f2)] = np.nan

        d1 = qmergeprofit0 / mktcap * dummy
        dfall = pd.concat([
            d1.unstack(),
            qmergeprofit0.unstack() / tAssets0.unstack(),
            size.unstack()
        ],
                          axis=1)
        dfall[np.isinf(dfall)] = np.nan
        dfall.columns = ['nf01', 'nf02', 'size']
        dfall['inter'] = 1.0
        dfall.reset_index(inplace=True)
        dfall.dropna(inplace=True)
        dfall.reset_index(inplace=True, drop=True)
        retdbeta = neutralize(dfall[['nf01', 'nf02', 'inter']].values,
                              dfall['size'].values,
                              groups=dfall['trade_date'].values)
        ret_dbeta = dfall[['trade_date', 'code']].copy()
        ret_dbeta['adjfactor'] = retdbeta
        adjdata = ret_dbeta.pivot_table(index='trade_date',
                                        columns='code',
                                        values='adjfactor')
        redata = adjdata.reindex(index=tradingday, columns=ticker)
        f3 = -redata

        d2 = qtRevenue0 / mktcap * dummy
        dfall = pd.concat([d1.unstack(), d2.unstack(), size.unstack()], axis=1)
        dfall[np.isinf(dfall)] = np.nan
        dfall.columns = ['nf01', 'nf02', 'size']
        dfall['inter'] = 1.0
        dfall.reset_index(inplace=True)
        dfall.dropna(inplace=True)
        dfall.reset_index(inplace=True, drop=True)
        retdbeta = neutralize(dfall[['nf01', 'nf02', 'inter']].values,
                              dfall['size'].values,
                              groups=dfall['trade_date'].values)
        ret_dbeta = dfall[['trade_date', 'code']].copy()
        ret_dbeta['adjfactor'] = retdbeta
        adjdata = ret_dbeta.pivot_table(index='trade_date',
                                        columns='code',
                                        values='adjfactor')
        redata = adjdata.reindex(index=tradingday, columns=ticker)
        f4 = (size - redata) / size
        f4[np.isinf(f4)] = np.nan
        factor = factor_merge([f1, f2, f3, f4])
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_value5")

    def factor_value6(self,
                      data=None,
                      dependencies=[
                          'dummy120_fst', 'closePrice', 'sw1', 'totalShares',
                          'fbqpub_mergeEbt_pnq0', 'fbqpub_Ebt_pnq0'
                      ],
                      window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        closePrice = data['closePrice']
        qmergeEbt0 = data['fbqpub_mergeEbt_pnq0']
        qEbt0 = data['fbqpub_Ebt_pnq0']
        qmergeEbt0[qmergeEbt0.isna()] = qEbt0[qmergeEbt0.isna()]
        totalShares = data['totalShares']
        closePrice[closePrice <= 0] = np.nan
        totalShares[totalShares <= 0] = np.nan
        sw1 = data['sw1']
        dy_q_evebitda_caldr = closePrice / (4 * qmergeEbt0 / totalShares)
        dy_q_evebitda_caldr[np.isinf(dy_q_evebitda_caldr)] = np.nan
        factor = dy_q_evebitda_caldr
        factor = -abs(factor)
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_value6")

    def factor_value7(
            self,
            data=None,
            dependencies=[
                'dummy120_fst', 'sw1', 'fbttmpub_mergeProfit_pnq0',
                'fbttmpub_mergeProfit_pnq1', 'fbttmpub_mergeProfit_pnq2',
                'fbttmpub_mergeProfit_pnq3', 'fbttmpub_mergeProfit_pnq4',
                'fbttmpub_mergeProfit_pnq5', 'fbttmpub_mergeProfit_pnq6',
                'fbttmpub_mergeProfit_pnq7', 'bspub_tEquityAttrP_pnq0',
                'bspub_tEquityAttrP_pnq1', 'bspub_tEquityAttrP_pnq2',
                'bspub_tEquityAttrP_pnq3', 'bspub_tEquityAttrP_pnq4',
                'bspub_tEquityAttrP_pnq5', 'bspub_tEquityAttrP_pnq6',
                'bspub_tEquityAttrP_pnq7', 'isttmpub_nIncomeAttrP_pnq0',
                'isttmpub_nIncomeAttrP_pnq1', 'isttmpub_nIncomeAttrP_pnq2',
                'isttmpub_nIncomeAttrP_pnq3', 'isttmpub_nIncomeAttrP_pnq4',
                'isttmpub_nIncomeAttrP_pnq5', 'isttmpub_nIncomeAttrP_pnq6',
                'isttmpub_nIncomeAttrP_pnq7'
            ],
            window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        tradingday = sw1.index
        ticker = sw1.columns
        ttmmergeprofit0 = data['fbttmpub_mergeProfit_pnq0']
        ttmnIncomeAttrP0 = data['isttmpub_nIncomeAttrP_pnq0']
        ttmmergeprofit0[ttmmergeprofit0.isna()] = ttmnIncomeAttrP0[
            ttmmergeprofit0.isna()]
        ttmmergeprofit1 = data['fbttmpub_mergeProfit_pnq1']
        ttmnIncomeAttrP1 = data['isttmpub_nIncomeAttrP_pnq1']
        ttmmergeprofit1[ttmmergeprofit1.isna()] = ttmnIncomeAttrP1[
            ttmmergeprofit1.isna()]
        ttmmergeprofit2 = data['fbttmpub_mergeProfit_pnq2']
        ttmnIncomeAttrP2 = data['isttmpub_nIncomeAttrP_pnq2']
        ttmmergeprofit2[ttmmergeprofit2.isna()] = ttmnIncomeAttrP2[
            ttmmergeprofit2.isna()]
        ttmmergeprofit3 = data['fbttmpub_mergeProfit_pnq3']
        ttmnIncomeAttrP3 = data['isttmpub_nIncomeAttrP_pnq3']
        ttmmergeprofit3[ttmmergeprofit3.isna()] = ttmnIncomeAttrP3[
            ttmmergeprofit3.isna()]
        ttmmergeprofit4 = data['fbttmpub_mergeProfit_pnq4']
        ttmnIncomeAttrP4 = data['isttmpub_nIncomeAttrP_pnq4']
        ttmmergeprofit4[ttmmergeprofit4.isna()] = ttmnIncomeAttrP4[
            ttmmergeprofit4.isna()]
        ttmmergeprofit5 = data['fbttmpub_mergeProfit_pnq5']
        ttmnIncomeAttrP5 = data['isttmpub_nIncomeAttrP_pnq5']
        ttmmergeprofit5[ttmmergeprofit5.isna()] = ttmnIncomeAttrP5[
            ttmmergeprofit5.isna()]
        ttmmergeprofit6 = data['fbttmpub_mergeProfit_pnq6']
        ttmnIncomeAttrP6 = data['isttmpub_nIncomeAttrP_pnq6']
        ttmmergeprofit6[ttmmergeprofit6.isna()] = ttmnIncomeAttrP6[
            ttmmergeprofit6.isna()]
        ttmmergeprofit7 = data['fbttmpub_mergeProfit_pnq7']
        ttmnIncomeAttrP7 = data['isttmpub_nIncomeAttrP_pnq7']
        ttmmergeprofit7[ttmmergeprofit7.isna()] = ttmnIncomeAttrP7[
            ttmmergeprofit7.isna()]
        tEquityAttrP0 = data['bspub_tEquityAttrP_pnq0']
        tEquityAttrP1 = data['bspub_tEquityAttrP_pnq1']
        tEquityAttrP2 = data['bspub_tEquityAttrP_pnq2']
        tEquityAttrP3 = data['bspub_tEquityAttrP_pnq3']
        tEquityAttrP4 = data['bspub_tEquityAttrP_pnq4']
        tEquityAttrP5 = data['bspub_tEquityAttrP_pnq5']
        tEquityAttrP6 = data['bspub_tEquityAttrP_pnq6']
        tEquityAttrP7 = data['bspub_tEquityAttrP_pnq7']
        dfall = pd.concat([(ttmmergeprofit7 / tEquityAttrP7).unstack(),
                           (ttmmergeprofit6 / tEquityAttrP6).unstack(),
                           (ttmmergeprofit5 / tEquityAttrP5).unstack(),
                           (ttmmergeprofit4 / tEquityAttrP4).unstack(),
                           (ttmmergeprofit3 / tEquityAttrP3).unstack(),
                           (ttmmergeprofit2 / tEquityAttrP2).unstack(),
                           (ttmmergeprofit1 / tEquityAttrP1).unstack(),
                           (ttmmergeprofit0 / tEquityAttrP0).unstack()],
                          axis=1)
        dfall[np.isinf(dfall)] = np.nan
        vstd = dfall.std(axis=1)
        vstd[vstd == 0] = np.nan
        f = (dfall.iloc[:, -1] -
             dfall.ewm(halflife=8, axis=1).mean().iloc[:, -1]) / vstd
        ff = pd.DataFrame(f).reset_index()
        factor = ff.pivot_table(index='trade_date', columns='code', values=0)
        factor = factor.reindex(index=tradingday, columns=ticker)
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_value7")

    def factor_value8(
            self,
            data=None,
            dependencies=['dummy120_fst', 'ffancy_aiEtopZ180', 'sw1'],
            window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        factor = data['ffancy_aiEtopZ180']
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_value8")

    def factor_value9(self,
                      data=None,
                      dependencies=['dummy120_fst', 'fuqer_PEHist20', 'sw1'],
                      window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        fuqer_PEHist20 = data['fuqer_PEHist20']
        sw1 = data['sw1']
        factor = -fuqer_PEHist20
        factor = indfill_median(factor * dummy, sw1)
        return self._format(factor, "factor_value9")

    def factor_value10(self,
                       data=None,
                       dependencies=['dummy120_fst', 'fuqer_PEHist120', 'sw1'],
                       window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        factor = -data['fuqer_PEHist120']
        factor = indfill_median(factor * dummy, sw1)
        return self._format(factor, "factor_value10")

    def factor_value11(self,
                       data=None,
                       dependencies=['dummy120_fst', 'fuqer_PEHist60', 'sw1'],
                       window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        factor = -data['fuqer_PEHist60']
        factor = indfill_median(factor * dummy, sw1)
        return self._format(factor, "factor_value11")