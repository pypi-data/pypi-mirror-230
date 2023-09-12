# -*- encoding:utf-8 -*-
import numpy as np
import pandas as pd
from alphakit.const import *
from alphakit.factor import *
from alphakit.portfolio import *
from alphakit.data import *

from hermes.factors.base import FactorBase, LongCallMixin, ShortCallMixin
from jdwdata.RetrievalAPI import get_data_by_map


class FactorGrowth(FactorBase, LongCallMixin, ShortCallMixin):

    def __init__(self, data_format, **kwargs):
        __str__ = 'factor_growth'
        self.category = 'Growth'
        self.name = '成长因子'
        self._data_format = data_format
        self._data = self.init_data(**kwargs) if 'end_date' in kwargs else None
        data = get_data_by_map(columns=BARRA_ALL_K,
                               begin_date=self.begin_date,
                               end_date=self.end_date,
                               method='ddb')
        self._risksizeindu = getdataset(data, BARRA_SIZEIND_K)

    def _init_self(self, **kwargs):
        pass

    def factor_growth1(self,
                       data=None,
                       dependencies=[
                           'dummy120_fst', 'sw1', 'isqpub_tCogs_pnq4',
                           'isqpub_tRevenue_pnq4', 'isqpub_tCogs_pnq0',
                           'isqpub_tRevenue_pnq0'
                       ],
                       window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        qtCogs4 = data['isqpub_tCogs_pnq4']
        qtRevenue4 = data['isqpub_tRevenue_pnq4']
        qtCogs0 = data['isqpub_tCogs_pnq0']
        qtRevenue0 = data['isqpub_tRevenue_pnq0']
        factor = qtCogs4 / abs(qtRevenue4) - qtCogs0 / abs(qtRevenue0)
        factor[np.isinf(factor)] = np.nan
        factor = indfill_median(factor * dummy, sw1)
        return self._format(factor, "factor_growth1")

    def factor_growth2(self,
                       data=None,
                       dependencies=[
                           'marketValue', 'bspub_tLiab_pnq0',
                           'bspub_tLiab_pnq4', 'bspub_minorityInt_pnq0',
                           'bspub_minorityInt_pnq4', 'fbqpub_mergeIncome_pnq0',
                           'fbqpub_mergeIncome_pnq4', 'isqpub_COGS_pnq0',
                           'isqpub_COGS_pnq4', 'bspub_cashCEquiv_pnq0',
                           'bspub_cashCEquiv_pnq4', 'sw1', 'dummy120_fst',
                           'isqpub_revenue_pnq0', 'isqpub_revenue_pnq4'
                       ],
                       window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        mktcap = data['marketValue']
        tLiab4 = data['bspub_tLiab_pnq4']
        tLiab0 = data['bspub_tLiab_pnq0']
        minorityInt0 = data['bspub_minorityInt_pnq0']
        minorityInt4 = data['bspub_minorityInt_pnq4']
        cashCEquiv0 = data['bspub_cashCEquiv_pnq0']
        cashCEquiv4 = data['bspub_cashCEquiv_pnq4']
        qmergeIncome0 = data['fbqpub_mergeIncome_pnq0']
        qrevenue0 = data['isqpub_revenue_pnq0']
        qmergeIncome0[qmergeIncome0.isna()] = qrevenue0[qmergeIncome0.isna()]
        qmergeIncome4 = data['fbqpub_mergeIncome_pnq4']
        qrevenue4 = data['isqpub_revenue_pnq4']
        qmergeIncome4[qmergeIncome4.isna()] = qrevenue4[qmergeIncome4.isna()]
        qcogs0 = data['isqpub_COGS_pnq0']
        qcogs4 = data['isqpub_COGS_pnq4']
        sw1 = data['sw1']
        ev0 = mktcap.add(tLiab0,
                         fill_value=0).add(minorityInt0,
                                           fill_value=0).add(cashCEquiv0,
                                                             fill_value=0)
        ev4 = mktcap.add(tLiab4,
                         fill_value=0).add(minorityInt4,
                                           fill_value=0).add(cashCEquiv4,
                                                             fill_value=0)
        ev0[ev0 == 0] = np.nan
        ev4[ev4 == 0] = np.nan
        value0 = (qmergeIncome0 - qcogs0) / ev0
        value4 = (qmergeIncome4 - qcogs4) / ev4
        factor = value0 - value4
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_growth2")

    def factor_growth3(self,
                       data=None,
                       dependencies=[
                           'dummy120_fst', 'fbpub_mergeOprofit_pnq0',
                           'fbpub_mergeOprofit_pnq4', 'sw1',
                           'ispub_operateProfit_pnq0',
                           'ispub_operateProfit_pnq4'
                       ],
                       window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        mergeOprofit0 = data['fbpub_mergeOprofit_pnq0']
        operateProfit0 = data['ispub_operateProfit_pnq0']
        mergeOprofit0[mergeOprofit0.isna()] = operateProfit0[
            mergeOprofit0.isna()]
        mergeOprofit4 = data['fbpub_mergeOprofit_pnq4']
        operateProfit4 = data['ispub_operateProfit_pnq4']
        mergeOprofit4[mergeOprofit4.isna()] = operateProfit4[
            mergeOprofit4.isna()]
        factor = (mergeOprofit0 - mergeOprofit4) / abs(mergeOprofit4)
        factor[np.isinf(factor)] = np.nan
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_growth3")

    def factor_growth4(self,
                       data=None,
                       dependencies=[
                           'dummy120_fst', 'fbqpub_mergeProfit_pnq0',
                           'fbqpub_mergeProfit_pnq4', 'sw1', 'marketValue',
                           'isqpub_nIncomeAttrP_pnq0',
                           'isqpub_nIncomeAttrP_pnq4'
                       ],
                       window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        qmergeprofit0 = data['fbqpub_mergeProfit_pnq0']
        qnIncomeAttrP0 = data['isqpub_nIncomeAttrP_pnq0']
        qmergeprofit0[qmergeprofit0.isna()] = qnIncomeAttrP0[
            qmergeprofit0.isna()]
        qmergeprofit4 = data['fbqpub_mergeProfit_pnq4']
        qnIncomeAttrP4 = data['isqpub_nIncomeAttrP_pnq4']
        qmergeprofit4[qmergeprofit4.isna()] = qnIncomeAttrP4[
            qmergeprofit4.isna()]
        mktcap = data['marketValue']
        factor = qmergeprofit0 * (qmergeprofit0 - qmergeprofit4) / abs(
            qmergeprofit4 * mktcap)
        factor[np.isinf(factor)] = np.nan
        factor = indfill_median(factor * dummy, sw1)
        return self._format(factor, "factor_growth4")

    def factor_growth5(
            self,
            data=None,
            dependencies=[
                'dummy120_fst', 'fbqpub_mergeProfit_pnq0',
                'fbqpub_mergeProfit_pnq1', 'fbqpub_mergeProfit_pnq2',
                'fbqpub_mergeProfit_pnq3', 'fbqpub_mergeProfit_pnq4',
                'fbqpub_mergeProfit_pnq5', 'fbqpub_mergeProfit_pnq6',
                'fbqpub_mergeProfit_pnq7', 'fbqpub_mergeProfit_pnq8',
                'fbqpub_mergeProfit_pnq9', 'fbqpub_mergeProfit_pnq10',
                'fbqpub_mergeProfit_pnq11', 'sw1', 'isqpub_nIncomeAttrP_pnq0',
                'isqpub_nIncomeAttrP_pnq1', 'isqpub_nIncomeAttrP_pnq2',
                'isqpub_nIncomeAttrP_pnq3', 'isqpub_nIncomeAttrP_pnq4',
                'isqpub_nIncomeAttrP_pnq5', 'isqpub_nIncomeAttrP_pnq6',
                'isqpub_nIncomeAttrP_pnq7', 'isqpub_nIncomeAttrP_pnq8',
                'isqpub_nIncomeAttrP_pnq9', 'isqpub_nIncomeAttrP_pnq10',
                'isqpub_nIncomeAttrP_pnq11'
            ],
            window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        tradingday = sw1.index
        ticker = sw1.columns
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
        qmergeprofit8 = data['fbqpub_mergeProfit_pnq8']
        qnIncomeAttrP8 = data['isqpub_nIncomeAttrP_pnq8']
        qmergeprofit8[qmergeprofit8.isna()] = qnIncomeAttrP8[
            qmergeprofit8.isna()]
        qmergeprofit9 = data['fbqpub_mergeProfit_pnq9']
        qnIncomeAttrP9 = data['isqpub_nIncomeAttrP_pnq9']
        qmergeprofit9[qmergeprofit9.isna()] = qnIncomeAttrP9[
            qmergeprofit9.isna()]
        qmergeprofit10 = data['fbqpub_mergeProfit_pnq10']
        qnIncomeAttrP10 = data['isqpub_nIncomeAttrP_pnq10']
        qmergeprofit10[qmergeprofit10.isna()] = qnIncomeAttrP10[
            qmergeprofit10.isna()]
        qmergeprofit11 = data['fbqpub_mergeProfit_pnq11']
        qnIncomeAttrP11 = data['isqpub_nIncomeAttrP_pnq11']
        qmergeprofit11[qmergeprofit11.isna()] = qnIncomeAttrP11[
            qmergeprofit11.isna()]
        dfall = pd.concat([(qmergeprofit0 - qmergeprofit4).unstack(),
                           (qmergeprofit1 - qmergeprofit5).unstack(),
                           (qmergeprofit2 - qmergeprofit6).unstack(),
                           (qmergeprofit3 - qmergeprofit7).unstack(),
                           (qmergeprofit4 - qmergeprofit8).unstack(),
                           (qmergeprofit5 - qmergeprofit9).unstack(),
                           (qmergeprofit6 - qmergeprofit10).unstack(),
                           (qmergeprofit7 - qmergeprofit11).unstack()],
                          axis=1)
        qstd = dfall.std(axis=1)
        qstd[qstd == 0] = np.nan
        ff3 = ((dfall.iloc[:, 0] - dfall.mean(axis=1)) / qstd).reset_index()
        factor = ff3.pivot_table(index='trade_date', columns='code', values=0)
        factor = factor.reindex(index=tradingday, columns=ticker)
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_growth5")

    def factor_growth6(self,
                       data=None,
                       dependencies=['dummy120_fst', 'fuqer_EgibsLong', 'sw1'],
                       window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        factor = data['fuqer_EgibsLong']
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_growth6")

    def factor_growth7(self,
                       data=None,
                       dependencies=[
                           'dummy120_fst', 'ispub_basicEps_pnq0',
                           'ispub_basicEps_pnq1', 'sw1'
                       ],
                       window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        f0 = data['ispub_basicEps_pnq0']
        f1 = data['ispub_basicEps_pnq1']
        factor = (f0 - f1) / abs(f1)
        factor[np.isinf(factor)] = np.nan
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_growth7")

    def factor_growth8(self,
                       data=None,
                       dependencies=[
                           'dummy120_fst', 'isttmpub_tProfit_pnq0',
                           'isttmpub_tProfit_pnq1', 'sw1'
                       ],
                       window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        f0 = data['isttmpub_tProfit_pnq0']
        f1 = data['isttmpub_tProfit_pnq1']
        factor = (f0 - f1) / abs(f1)
        factor[np.isinf(factor)] = np.nan
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_growth8")

    def factor_growth9(self,
                       data=None,
                       dependencies=[
                           'dummy120_fst', 'cfqpub_procSellInvest_pnq0',
                           'cfqpub_procSellInvest_pnq1', 'sw1'
                       ],
                       window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        f0 = data['cfqpub_procSellInvest_pnq0']
        f1 = data['cfqpub_procSellInvest_pnq1']
        factor = (f0 - f1) / abs(f1)
        factor[np.isinf(factor)] = np.nan
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_growth9")

    def factor_growth10(self,
                        data=None,
                        dependencies=[
                            'dummy120_fst', 'fbqpub_Ebit_pnq0',
                            'fbqpub_Ebit_pnq1', 'sw1'
                        ],
                        window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        f0 = data['fbqpub_Ebit_pnq0']
        f1 = data['fbqpub_Ebit_pnq1']
        factor = (f0 - f1) / abs(f1)
        factor[np.isinf(factor)] = np.nan
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_growth10")

    def factor_growth11(self,
                        data=None,
                        dependencies=[
                            'dummy120_fst', 'fbpub_mergeProfit_pnq0',
                            'fbpub_mergeProfit_pnq1', 'sw1',
                            'ispub_nIncomeAttrP_pnq0',
                            'ispub_nIncomeAttrP_pnq1'
                        ],
                        window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        f0 = data['fbpub_mergeProfit_pnq0']
        f0m = data['ispub_nIncomeAttrP_pnq0']
        f0[f0.isna()] = f0m[f0.isna()]
        f1 = data['fbpub_mergeProfit_pnq1']
        f1m = data['ispub_nIncomeAttrP_pnq1']
        f1[f1.isna()] = f1m[f1.isna()]
        factor = (f0 - f1) / abs(f1)
        factor[np.isinf(factor)] = np.nan
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_growth11")

    def factor_growth12(self,
                        data=None,
                        dependencies=[
                            'dummy120_fst', 'isqpub_nIncomeAttrP_pnq0',
                            'isqpub_nIncomeAttrP_pnq1', 'sw1'
                        ],
                        window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        f0 = data['isqpub_nIncomeAttrP_pnq0']
        f1 = data['isqpub_nIncomeAttrP_pnq1']
        factor = (f0 - f1) / abs(f1)
        factor[np.isinf(factor)] = np.nan
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_growth12")

    def factor_growth13(self,
                        data=None,
                        dependencies=[
                            'dummy120_fst', 'cfqpub_cPaidDivProfInt_pnq0',
                            'cfqpub_cPaidDivProfInt_pnq1', 'sw1'
                        ],
                        window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        f0 = data['cfqpub_cPaidDivProfInt_pnq0']
        f1 = data['cfqpub_cPaidDivProfInt_pnq1']
        factor = (f0 - f1) / abs(f1)
        factor[np.isinf(factor)] = np.nan
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_growth13")

    def factor_growth14(self,
                        data=None,
                        dependencies=[
                            'dummy120_fst', 'cfqpub_cFRCapContr_pnq0',
                            'cfqpub_cFRCapContr_pnq4', 'sw1'
                        ],
                        window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        f0 = data['cfqpub_cFRCapContr_pnq0']
        f4 = data['cfqpub_cFRCapContr_pnq4']
        factor = (f0 - f4) / abs(f4)
        factor[np.isinf(factor)] = np.nan
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_growth14")

    def factor_growth15(self,
                        data=None,
                        dependencies=[
                            'dummy120_fst', 'cfqpub_cFROthInvestA_pnq0',
                            'cfqpub_cFROthInvestA_pnq1', 'sw1'
                        ],
                        window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        f0 = data['cfqpub_cFROthInvestA_pnq0']
        f1 = data['cfqpub_cFROthInvestA_pnq1']
        factor = (f0 - f1) / abs(f1)
        factor[np.isinf(factor)] = np.nan
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_growth15")

    def factor_growth16(self,
                        data=None,
                        dependencies=[
                            'dummy120_fst', 'ispub_incomeTax_pnq0',
                            'ispub_incomeTax_pnq1', 'sw1'
                        ],
                        window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        f0 = data['ispub_incomeTax_pnq0']
        f1 = data['ispub_incomeTax_pnq1']
        factor = (f0 - f1) / abs(f1)
        factor[np.isinf(factor)] = np.nan
        factor = indfill_median(factor * dummy, sw1)
        return self._format(factor, "factor_growth16")

    def factor_growth17(self,
                        data=None,
                        dependencies=[
                            'dummy120_fst', 'cfpub_cPaidOthFinanA_pnq0',
                            'cfpub_cPaidOthFinanA_pnq1', 'sw1'
                        ],
                        window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        f0 = data['cfpub_cPaidOthFinanA_pnq0']
        f1 = data['cfpub_cPaidOthFinanA_pnq1']
        factor = (f0 - f1) / abs(f1)
        factor[np.isinf(factor)] = np.nan
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_growth17")

    def factor_growth18(self,
                        data=None,
                        dependencies=[
                            'dummy120_fst', 'bspub_ltEquityInvest_pnq0',
                            'bspub_ltEquityInvest_pnq1', 'sw1'
                        ],
                        window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        f0 = data['bspub_ltEquityInvest_pnq0']
        f1 = data['bspub_ltEquityInvest_pnq1']
        factor = (f0 - f1) / abs(f1)
        factor[np.isinf(factor)] = np.nan
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_growth18")

    def factor_growth19(self,
                        data=None,
                        dependencies=[
                            'dummy120_fst', 'cfpub_dispFixAssetsOth_pnq0',
                            'cfpub_dispFixAssetsOth_pnq1', 'sw1'
                        ],
                        window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        f0 = data['cfpub_dispFixAssetsOth_pnq0']
        f1 = data['cfpub_dispFixAssetsOth_pnq1']
        factor = (f0 - f1) / abs(f1)
        factor[np.isinf(factor)] = np.nan
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_growth19")

    def factor_growth20(self,
                        data=None,
                        dependencies=[
                            'dummy120_fst', 'bspub_deferTaxLiab_pnq0',
                            'bspub_deferTaxLiab_pnq1', 'sw1'
                        ],
                        window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        f0 = data['bspub_deferTaxLiab_pnq0']
        f1 = data['bspub_deferTaxLiab_pnq1']
        factor = (f0 - f1) / abs(f1)
        factor[np.isinf(factor)] = np.nan
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_growth20")

    def factor_growth21(
            self,
            data=None,
            dependencies=[
                'dummy120_fst', 'sw1', 'fbttmpub_NIncomeCut_pnq0',
                'fbttmpub_NIncomeCut_pnq1', 'fbttmpub_NIncomeCut_pnq2',
                'fbttmpub_NIncomeCut_pnq3', 'fbttmpub_NIncomeCut_pnq4',
                'fbttmpub_NIncomeCut_pnq5', 'fbttmpub_NIncomeCut_pnq6',
                'fbttmpub_NIncomeCut_pnq7', 'fbttmpub_NIncomeCut_pnq8',
                'fbttmpub_NIncomeCut_pnq9', 'fbttmpub_NIncomeCut_pnq10',
                'fbttmpub_NIncomeCut_pnq11'
            ],
            window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        tradingday = sw1.index
        ticker = sw1.columns
        f0 = data['fbttmpub_NIncomeCut_pnq0']
        f1 = data['fbttmpub_NIncomeCut_pnq1']
        f2 = data['fbttmpub_NIncomeCut_pnq2']
        f3 = data['fbttmpub_NIncomeCut_pnq3']
        f4 = data['fbttmpub_NIncomeCut_pnq4']
        f5 = data['fbttmpub_NIncomeCut_pnq5']
        f6 = data['fbttmpub_NIncomeCut_pnq6']
        f7 = data['fbttmpub_NIncomeCut_pnq7']
        f8 = data['fbttmpub_NIncomeCut_pnq8']
        f9 = data['fbttmpub_NIncomeCut_pnq9']
        f10 = data['fbttmpub_NIncomeCut_pnq10']
        f11 = data['fbttmpub_NIncomeCut_pnq11']
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
        factor = (f0 - f1) / dfstd
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_growth21")

    def factor_growth22(
            self,
            data=None,
            dependencies=[
                'dummy120_fst', 'sw1', 'isttmpub_incomeTax_pnq0',
                'isttmpub_incomeTax_pnq1', 'isttmpub_incomeTax_pnq2',
                'isttmpub_incomeTax_pnq3', 'isttmpub_incomeTax_pnq4',
                'isttmpub_incomeTax_pnq5', 'isttmpub_incomeTax_pnq6',
                'isttmpub_incomeTax_pnq7', 'isttmpub_incomeTax_pnq8',
                'isttmpub_incomeTax_pnq9', 'isttmpub_incomeTax_pnq10',
                'isttmpub_incomeTax_pnq11'
            ],
            window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        tradingday = sw1.index
        ticker = sw1.columns
        f0 = data['isttmpub_incomeTax_pnq0']
        f1 = data['isttmpub_incomeTax_pnq1']
        f2 = data['isttmpub_incomeTax_pnq2']
        f3 = data['isttmpub_incomeTax_pnq3']
        f4 = data['isttmpub_incomeTax_pnq4']
        f5 = data['isttmpub_incomeTax_pnq5']
        f6 = data['isttmpub_incomeTax_pnq6']
        f7 = data['isttmpub_incomeTax_pnq7']
        f8 = data['isttmpub_incomeTax_pnq8']
        f9 = data['isttmpub_incomeTax_pnq9']
        f10 = data['isttmpub_incomeTax_pnq10']
        f11 = data['isttmpub_incomeTax_pnq11']
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
        factor = (f0 - f1) / dfstd
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_growth22")

    def factor_growth23(self,
                        data=None,
                        dependencies=[
                            'dummy120_fst', 'cfttmpub_cPaidInvest_pnq0',
                            'cfttmpub_cPaidInvest_pnq4', 'sw1'
                        ],
                        window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        f0 = data['cfttmpub_cPaidInvest_pnq0']
        f4 = data['cfttmpub_cPaidInvest_pnq4']
        factor = (f0 - f4) / abs(f4)
        factor[np.isinf(factor)] = np.nan
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_growth23")

    def factor_growth24(self,
                        data=None,
                        dependencies=[
                            'dummy120_fst', 'cfpub_procSellInvest_pnq0',
                            'cfpub_procSellInvest_pnq4', 'sw1'
                        ],
                        window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        f0 = data['cfpub_procSellInvest_pnq0']
        f4 = data['cfpub_procSellInvest_pnq4']
        factor = (f0 - f4) / abs(f4)
        factor[np.isinf(factor)] = np.nan
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_growth24")

    def factor_growth25(self,
                        data=None,
                        dependencies=[
                            'dummy120_fst', 'cfpub_cFROthInvestA_pnq0',
                            'cfpub_cFROthInvestA_pnq4', 'sw1'
                        ],
                        window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        f0 = data['cfpub_cFROthInvestA_pnq0']
        f4 = data['cfpub_cFROthInvestA_pnq4']
        factor = (f0 - f4) / abs(f4)
        factor[np.isinf(factor)] = np.nan
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_growth25")

    def factor_growth26(self,
                        data=None,
                        dependencies=[
                            'dummy120_fst', 'isqpub_aJInvestIncome_pnq0',
                            'isqpub_aJInvestIncome_pnq4', 'sw1'
                        ],
                        window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        f0 = data['isqpub_aJInvestIncome_pnq0']
        f4 = data['isqpub_aJInvestIncome_pnq4']
        factor = (f0 - f4) / abs(f4)
        factor[np.isinf(factor)] = np.nan
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_growth26")

    def factor_growth27(self,
                        data=None,
                        dependencies=[
                            'dummy120_fst', 'fbpub_NIncomeCut_pnq0',
                            'fbpub_NIncomeCut_pnq4', 'sw1',
                            'bspub_tAssets_pnq4'
                        ],
                        window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        tAssets4 = data['bspub_tAssets_pnq4']
        f0 = data['fbpub_NIncomeCut_pnq0']
        f4 = data['fbpub_NIncomeCut_pnq4']
        factor = (f0 - f4) / abs(tAssets4)
        factor[np.isinf(factor)] = np.nan
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_growth27")

    def factor_growth28(self,
                        data=None,
                        dependencies=[
                            'dummy120_fst', 'bspub_retainedEarnings_pnq0',
                            'bspub_retainedEarnings_pnq1', 'sw1',
                            'bspub_tAssets_pnq1'
                        ],
                        window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        tAssets1 = data['bspub_tAssets_pnq1']
        f0 = data['bspub_retainedEarnings_pnq0']
        f1 = data['bspub_retainedEarnings_pnq1']
        factor = (f0 - f1) / abs(tAssets1)
        factor[np.isinf(factor)] = np.nan
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_growth28")

    def factor_growth29(self,
                        data=None,
                        dependencies=[
                            'dummy120_fst', 'isttmpub_sellExp_pnq0',
                            'isttmpub_sellExp_pnq1', 'sw1',
                            'bspub_tAssets_pnq1'
                        ],
                        window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        tAssets1 = data['bspub_tAssets_pnq1']
        f0 = data['isttmpub_sellExp_pnq0']
        f1 = data['isttmpub_sellExp_pnq1']
        factor = (f0 - f1) / abs(tAssets1)
        factor[np.isinf(factor)] = np.nan
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_growth29")

    def factor_growth30(self,
                        data=None,
                        dependencies=[
                            'dummy120_fst', 'fbpub_mergeEbt_pnq0',
                            'fbpub_Ebt_pnq0', 'sw1', 'fbpub_mergeEbt_pnq1',
                            'fbpub_Ebt_pnq1'
                        ],
                        window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        f0 = data['fbpub_mergeEbt_pnq0']
        f0m = data['fbpub_Ebt_pnq0']
        f0[f0.isna()] = f0m[f0.isna()]
        f1 = data['fbpub_mergeEbt_pnq1']
        f1m = data['fbpub_Ebt_pnq1']
        f1[f1.isna()] = f1m[f1.isna()]
        factor = (f0 - f1) / abs(f1)
        factor[np.isinf(factor)] = np.nan
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_growth30")

    def factor_growth31(self,
                        data=None,
                        dependencies=[
                            'dummy120_fst', 'bspub_capitalReser_pnq0',
                            'bspub_capitalReser_pnq4', 'sw1'
                        ],
                        window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        f0 = data['bspub_capitalReser_pnq0']
        f4 = data['bspub_capitalReser_pnq4']
        factor = (f0 - f4) / abs(f4)
        factor[np.isinf(factor)] = np.nan
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_growth31")

    def factor_growth32(self,
                        data=None,
                        dependencies=[
                            'dummy120_fst', 'bspub_ltEquityInvest_pnq0',
                            'bspub_ltEquityInvest_pnq4', 'sw1'
                        ],
                        window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        f0 = data['bspub_ltEquityInvest_pnq0']
        f4 = data['bspub_ltEquityInvest_pnq4']
        factor = (f0 - f4) / abs(f4)
        factor[np.isinf(factor)] = np.nan
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_growth32")

    def factor_growth33(self,
                        data=None,
                        dependencies=[
                            'dummy120_fst', 'ispub_noperateIncome_pnq0',
                            'ispub_noperateIncome_pnq4', 'sw1'
                        ],
                        window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        f0 = data['ispub_noperateIncome_pnq0']
        f4 = data['ispub_noperateIncome_pnq4']
        factor = -(f0 - f4) / abs(f4)
        factor[np.isinf(factor)] = np.nan
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_growth33")

    def factor_growth34(self,
                        data=None,
                        dependencies=[
                            'dummy120_fst', 'fbttmpub_mergeIncome_pnq0',
                            'fbttmpub_mergeIncome_pnq1', 'sw1',
                            'bspub_tAssets_pnq1', 'isttmpub_revenue_pnq0',
                            'isttmpub_revenue_pnq1'
                        ],
                        window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        tAssets1 = data['bspub_tAssets_pnq1']
        f0 = data['fbttmpub_mergeIncome_pnq0']
        f0m = data['isttmpub_revenue_pnq0']
        f0[f0.isna()] = f0m[f0.isna()]
        f1 = data['fbttmpub_mergeIncome_pnq1']
        f1m = data['isttmpub_revenue_pnq1']
        f1[f1.isna()] = f1m[f1.isna()]
        factor = (f0 - f1) / abs(tAssets1)
        factor[np.isinf(factor)] = np.nan
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_growth34")

    def factor_growth35(self,
                        data=None,
                        dependencies=[
                            'dummy120_fst', 'isqpub_noperateIncome_pnq0',
                            'isqpub_noperateIncome_pnq4', 'sw1'
                        ],
                        window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        f0 = data['isqpub_noperateIncome_pnq0']
        f4 = data['isqpub_noperateIncome_pnq4']
        factor = -(f0 - f4) / abs(f4)
        factor[np.isinf(factor)] = np.nan
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_growth35")

    def factor_growth36(self,
                        data=None,
                        dependencies=[
                            'dummy120_fst', 'fbqpub_NIncomeCut_pnq0',
                            'fbqpub_NIncomeCut_pnq1', 'sw1', 'totalShares'
                        ],
                        window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        totalShares = data['totalShares']
        f0 = data['fbqpub_NIncomeCut_pnq0']
        f1 = data['fbqpub_NIncomeCut_pnq1']
        factor = (f0 - f1) / totalShares
        factor[np.isinf(factor)] = np.nan
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_growth36")

    def factor_growth37(self,
                        data=None,
                        dependencies=[
                            'dummy120_fst', 'fbqpub_mergeEbt_pnq0',
                            'fbqpub_mergeEbt_pnq1', 'sw1', 'totalShares',
                            'fbqpub_Ebt_pnq0', 'fbqpub_Ebt_pnq1'
                        ],
                        window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        totalShares = data['totalShares']
        f0 = data['fbqpub_mergeEbt_pnq0']
        f0m = data['fbqpub_Ebt_pnq0']
        f0[f0.isna()] = f0m[f0.isna()]
        f1 = data['fbqpub_mergeEbt_pnq1']
        f1m = data['fbqpub_Ebt_pnq1']
        f1[f1.isna()] = f1m[f1.isna()]
        factor = (f0 - f1) / totalShares
        factor[np.isinf(factor)] = np.nan
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_growth37")

    def factor_growth38(self,
                        data=None,
                        dependencies=[
                            'dummy120_fst', 'bspub_tradingFa_pnq0',
                            'bspub_tradingFa_pnq4', 'sw1'
                        ],
                        window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        f0 = data['bspub_tradingFa_pnq0']
        f4 = data['bspub_tradingFa_pnq4']
        factor = (f0 - f4) / abs(f4)
        factor[np.isinf(factor)] = np.nan
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_growth38")

    def factor_growth39(self,
                        data=None,
                        dependencies=[
                            'dummy120_fst', 'isttmpub_rDExp_pnq0',
                            'isttmpub_rDExp_pnq1', 'sw1', 'totalShares'
                        ],
                        window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        totalShares = data['totalShares']
        f0 = data['isttmpub_rDExp_pnq0']
        f1 = data['isttmpub_rDExp_pnq1']
        factor = (f0 - f1) / totalShares
        factor[np.isinf(factor)] = np.nan
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_growth39")

    def factor_growth40(
            self,
            data=None,
            dependencies=[
                'dummy120_fst', 'sw1', 'fbpub_Ebit_pnq0', 'fbpub_Ebit_pnq1',
                'fbpub_Ebit_pnq2', 'fbpub_Ebit_pnq3', 'fbpub_Ebit_pnq4',
                'fbpub_Ebit_pnq5', 'fbpub_Ebit_pnq6', 'fbpub_Ebit_pnq7',
                'fbpub_Ebit_pnq8', 'fbpub_Ebit_pnq9', 'fbpub_Ebit_pnq10',
                'fbpub_Ebit_pnq11'
            ],
            window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        tradingday = sw1.index
        ticker = sw1.columns
        f0 = data['fbpub_Ebit_pnq0']
        f1 = data['fbpub_Ebit_pnq1']
        f2 = data['fbpub_Ebit_pnq2']
        f3 = data['fbpub_Ebit_pnq3']
        f4 = data['fbpub_Ebit_pnq4']
        f5 = data['fbpub_Ebit_pnq5']
        f6 = data['fbpub_Ebit_pnq6']
        f7 = data['fbpub_Ebit_pnq7']
        f8 = data['fbpub_Ebit_pnq8']
        f9 = data['fbpub_Ebit_pnq9']
        f10 = data['fbpub_Ebit_pnq10']
        f11 = data['fbpub_Ebit_pnq11']
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
        factor = (f0 - f1) / dfstd
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_growth40")

    def factor_growth41(
            self,
            data=None,
            dependencies=[
                'dummy120_fst', 'sw1', 'fbqpub_mergeEbt_pnq0',
                'fbqpub_mergeEbt_pnq1', 'fbqpub_mergeEbt_pnq2',
                'fbqpub_mergeEbt_pnq3', 'fbqpub_mergeEbt_pnq4',
                'fbqpub_mergeEbt_pnq5', 'fbqpub_mergeEbt_pnq6',
                'fbqpub_mergeEbt_pnq7', 'fbqpub_mergeEbt_pnq8',
                'fbqpub_mergeEbt_pnq9', 'fbqpub_mergeEbt_pnq10',
                'fbqpub_mergeEbt_pnq11', 'fbqpub_Ebt_pnq0', 'fbqpub_Ebt_pnq1',
                'fbqpub_Ebt_pnq2', 'fbqpub_Ebt_pnq3', 'fbqpub_Ebt_pnq4',
                'fbqpub_Ebt_pnq5', 'fbqpub_Ebt_pnq6', 'fbqpub_Ebt_pnq7',
                'fbqpub_Ebt_pnq8', 'fbqpub_Ebt_pnq9', 'fbqpub_Ebt_pnq10',
                'fbqpub_Ebt_pnq11'
            ],
            window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        tradingday = sw1.index
        ticker = sw1.columns
        f0 = data['fbqpub_mergeEbt_pnq0']
        f0m = data['fbqpub_Ebt_pnq0']
        f0[f0.isna()] = f0m[f0.isna()]
        f1 = data['fbqpub_mergeEbt_pnq1']
        f1m = data['fbqpub_Ebt_pnq1']
        f1[f1.isna()] = f1m[f1.isna()]
        f2 = data['fbqpub_mergeEbt_pnq2']
        f2m = data['fbqpub_Ebt_pnq2']
        f2[f2.isna()] = f2m[f2.isna()]
        f3 = data['fbqpub_mergeEbt_pnq3']
        f3m = data['fbqpub_Ebt_pnq3']
        f3[f3.isna()] = f3m[f3.isna()]
        f4 = data['fbqpub_mergeEbt_pnq4']
        f4m = data['fbqpub_Ebt_pnq4']
        f4[f4.isna()] = f4m[f4.isna()]
        f5 = data['fbqpub_mergeEbt_pnq5']
        f5m = data['fbqpub_Ebt_pnq5']
        f5[f5.isna()] = f5m[f5.isna()]
        f6 = data['fbqpub_mergeEbt_pnq6']
        f6m = data['fbqpub_Ebt_pnq6']
        f6[f6.isna()] = f6m[f6.isna()]
        f7 = data['fbqpub_mergeEbt_pnq7']
        f7m = data['fbqpub_Ebt_pnq7']
        f7[f7.isna()] = f7m[f7.isna()]
        f8 = data['fbqpub_mergeEbt_pnq8']
        f8m = data['fbqpub_Ebt_pnq8']
        f8[f8.isna()] = f8m[f8.isna()]
        f9 = data['fbqpub_mergeEbt_pnq9']
        f9m = data['fbqpub_Ebt_pnq9']
        f9[f9.isna()] = f9m[f9.isna()]
        f10 = data['fbqpub_mergeEbt_pnq10']
        f10m = data['fbqpub_Ebt_pnq10']
        f10[f10.isna()] = f10m[f10.isna()]
        f11 = data['fbqpub_mergeEbt_pnq11']
        f11m = data['fbqpub_Ebt_pnq11']
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
        factor = (f0 - f4) / dfstd
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_growth41")

    def factor_growth42(
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
        factor = (f0 - f1) / dfstd
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_growth42")

    def factor_growth43(
            self,
            data=None,
            dependencies=[
                'dummy120_fst', 'sw1', 'ispub_operateProfit_pnq0',
                'ispub_operateProfit_pnq1', 'ispub_operateProfit_pnq2',
                'ispub_operateProfit_pnq3', 'ispub_operateProfit_pnq4',
                'ispub_operateProfit_pnq5', 'ispub_operateProfit_pnq6',
                'ispub_operateProfit_pnq7', 'ispub_operateProfit_pnq8',
                'ispub_operateProfit_pnq9', 'ispub_operateProfit_pnq10',
                'ispub_operateProfit_pnq11'
            ],
            window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        tradingday = sw1.index
        ticker = sw1.columns
        f0 = data['ispub_operateProfit_pnq0']
        f1 = data['ispub_operateProfit_pnq1']
        f2 = data['ispub_operateProfit_pnq2']
        f3 = data['ispub_operateProfit_pnq3']
        f4 = data['ispub_operateProfit_pnq4']
        f5 = data['ispub_operateProfit_pnq5']
        f6 = data['ispub_operateProfit_pnq6']
        f7 = data['ispub_operateProfit_pnq7']
        f8 = data['ispub_operateProfit_pnq8']
        f9 = data['ispub_operateProfit_pnq9']
        f10 = data['ispub_operateProfit_pnq10']
        f11 = data['ispub_operateProfit_pnq11']
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
        factor = (f0 - f1) / dfstd
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_growth43")

    def factor_growth44(
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
        factor = (f0 - f4) / dfstd
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_growth44")

    def factor_growth45(
            self,
            data=None,
            dependencies=[
                'dummy120_fst', 'sw1', 'fbqpub_mergeProfit_pnq0',
                'fbqpub_mergeProfit_pnq1', 'fbqpub_mergeProfit_pnq2',
                'fbqpub_mergeProfit_pnq3', 'fbqpub_mergeProfit_pnq4',
                'fbqpub_mergeProfit_pnq5', 'fbqpub_mergeProfit_pnq6',
                'fbqpub_mergeProfit_pnq7', 'fbqpub_mergeProfit_pnq8',
                'fbqpub_mergeProfit_pnq9', 'fbqpub_mergeProfit_pnq10',
                'fbqpub_mergeProfit_pnq11', 'isqpub_nIncomeAttrP_pnq0',
                'isqpub_nIncomeAttrP_pnq1', 'isqpub_nIncomeAttrP_pnq2',
                'isqpub_nIncomeAttrP_pnq3', 'isqpub_nIncomeAttrP_pnq4',
                'isqpub_nIncomeAttrP_pnq5', 'isqpub_nIncomeAttrP_pnq6',
                'isqpub_nIncomeAttrP_pnq7', 'isqpub_nIncomeAttrP_pnq8',
                'isqpub_nIncomeAttrP_pnq9', 'isqpub_nIncomeAttrP_pnq10',
                'isqpub_nIncomeAttrP_pnq11'
            ],
            window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
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
        f8 = data['fbqpub_mergeProfit_pnq8']
        f8m = data['isqpub_nIncomeAttrP_pnq8']
        f8[f8.isna()] = f8m[f8.isna()]
        f9 = data['fbqpub_mergeProfit_pnq9']
        f9m = data['isqpub_nIncomeAttrP_pnq9']
        f9[f9.isna()] = f9m[f9.isna()]
        f10 = data['fbqpub_mergeProfit_pnq10']
        f10m = data['isqpub_nIncomeAttrP_pnq10']
        f10[f10.isna()] = f10m[f10.isna()]
        f11 = data['fbqpub_mergeProfit_pnq11']
        f11m = data['isqpub_nIncomeAttrP_pnq11']
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
        factor = (f0 - f1) / dfstd
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_growth45")

    def factor_growth46(self,
                        data=None,
                        dependencies=[
                            'dummy120_fst', 'sw1', 'bspub_nclWithin1y_pnq0',
                            'bspub_nclWithin1y_pnq4'
                        ],
                        window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        f0 = data['bspub_nclWithin1y_pnq0']
        f4 = data['bspub_nclWithin1y_pnq4']
        factor = (f0 - f4) / abs(f4)
        factor[np.isinf(factor)] = np.nan
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_growth46")

    def factor_growth47(self,
                        data=None,
                        dependencies=[
                            'dummy120_fst', 'sw1', 'cfqpub_cFROthInvestA_pnq0',
                            'cfqpub_cFROthInvestA_pnq4'
                        ],
                        window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        f0 = data['cfqpub_cFROthInvestA_pnq0']
        f4 = data['cfqpub_cFROthInvestA_pnq4']
        factor = (f0 - f4) / abs(f4)
        factor[np.isinf(factor)] = np.nan
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_growth47")

    def factor_growth48(self,
                        data=None,
                        dependencies=[
                            'dummy120_fst', 'sw1', 'isttmpub_tRevenue_pnq0',
                            'isttmpub_tRevenue_pnq1', 'isttmpub_tRevenue_pnq2',
                            'isttmpub_tRevenue_pnq3', 'isttmpub_tRevenue_pnq4',
                            'isttmpub_tRevenue_pnq5', 'isttmpub_tRevenue_pnq6',
                            'isttmpub_tRevenue_pnq7', 'isttmpub_tRevenue_pnq8',
                            'isttmpub_tRevenue_pnq9',
                            'isttmpub_tRevenue_pnq10',
                            'isttmpub_tRevenue_pnq11'
                        ],
                        window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        tradingday = sw1.index
        ticker = sw1.columns
        f0 = data['isttmpub_tRevenue_pnq0']
        f1 = data['isttmpub_tRevenue_pnq1']
        f2 = data['isttmpub_tRevenue_pnq2']
        f3 = data['isttmpub_tRevenue_pnq3']
        f4 = data['isttmpub_tRevenue_pnq4']
        f5 = data['isttmpub_tRevenue_pnq5']
        f6 = data['isttmpub_tRevenue_pnq6']
        f7 = data['isttmpub_tRevenue_pnq7']
        f8 = data['isttmpub_tRevenue_pnq8']
        f9 = data['isttmpub_tRevenue_pnq9']
        f10 = data['isttmpub_tRevenue_pnq10']
        f11 = data['isttmpub_tRevenue_pnq11']
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
        factor = (f0 - f1) / dfstd
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_growth48")

    def factor_growth49(self,
                        data=None,
                        dependencies=[
                            'dummy120_fst', 'ispub_rDExp_pnq0',
                            'ispub_rDExp_pnq4', 'sw1'
                        ],
                        window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        f0 = data['ispub_rDExp_pnq0']
        f4 = data['ispub_rDExp_pnq4']
        factor = (f0 - f4) / abs(f4)
        factor[np.isinf(factor)] = np.nan
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_growth49")

    def factor_growth50(self,
                        data=None,
                        dependencies=[
                            'dummy120_fst', 'cfqpub_cInfFRFinanA_pnq0',
                            'cfqpub_cInfFRFinanA_pnq4', 'sw1'
                        ],
                        window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        f0 = data['cfqpub_cInfFRFinanA_pnq0']
        f4 = data['cfqpub_cInfFRFinanA_pnq4']
        factor = (f0 - f4) / abs(f4)
        factor[np.isinf(factor)] = np.nan
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_growth50")

    def factor_growth51(
            self,
            data=None,
            dependencies=[
                'dummy120_fst', 'sw1', 'fbqpub_Ebit_pnq0', 'fbqpub_Ebit_pnq1',
                'fbqpub_Ebit_pnq2', 'fbqpub_Ebit_pnq3', 'fbqpub_Ebit_pnq4',
                'fbqpub_Ebit_pnq5', 'fbqpub_Ebit_pnq6', 'fbqpub_Ebit_pnq7',
                'fbqpub_Ebit_pnq8', 'fbqpub_Ebit_pnq9', 'fbqpub_Ebit_pnq10',
                'fbqpub_Ebit_pnq11'
            ],
            window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        tradingday = sw1.index
        ticker = sw1.columns
        f0 = data['fbqpub_Ebit_pnq0']
        f1 = data['fbqpub_Ebit_pnq1']
        f2 = data['fbqpub_Ebit_pnq2']
        f3 = data['fbqpub_Ebit_pnq3']
        f4 = data['fbqpub_Ebit_pnq4']
        f5 = data['fbqpub_Ebit_pnq5']
        f6 = data['fbqpub_Ebit_pnq6']
        f7 = data['fbqpub_Ebit_pnq7']
        f8 = data['fbqpub_Ebit_pnq8']
        f9 = data['fbqpub_Ebit_pnq9']
        f10 = data['fbqpub_Ebit_pnq10']
        f11 = data['fbqpub_Ebit_pnq11']
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
        factor = (f0 - f4) / dfstd
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_growth51")

    def factor_growth52(self,
                        data=None,
                        dependencies=[
                            'dummy120_fst', 'cfttmpub_procSellInvest_pnq0',
                            'cfttmpub_procSellInvest_pnq4', 'sw1'
                        ],
                        window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        f0 = data['cfttmpub_procSellInvest_pnq0']
        f4 = data['cfttmpub_procSellInvest_pnq4']
        factor = (f0 - f4) / abs(f4)
        factor[np.isinf(factor)] = np.nan
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_growth52")

    def factor_growth53(self,
                        data=None,
                        dependencies=['dummy120_fst', 'fuqer_FSALESG', 'sw1'],
                        window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        factor = data['fuqer_FSALESG']
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_growth53")
