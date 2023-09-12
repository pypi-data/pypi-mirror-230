# -*- encoding:utf-8 -*-
import numpy as np
import pandas as pd
from alphakit.const import *
from alphakit.factor import *
from alphakit.portfolio import *
from alphakit.data import *

from hermes.factors.base import FactorBase, LongCallMixin, ShortCallMixin
from jdwdata.RetrievalAPI import get_data_by_map


class FactorMoneyflow(FactorBase, LongCallMixin, ShortCallMixin):

    def __init__(self, data_format, **kwargs):
        __str__ = 'factor_moneyflow'
        self.category = 'MoneyFlow'
        self.name = '资金流因子'
        self._data_format = data_format
        self._data = self.init_data(**kwargs) if 'end_date' in kwargs else None
        data = get_data_by_map(columns=BARRA_ALL_K,
                               begin_date=self.begin_date,
                               end_date=self.end_date,
                               method='ddb')
        self._risksizeindu = getdataset(data, BARRA_SIZEIND_K)

    def _init_self(self, **kwargs):
        pass

    def mf_sub1(self, data):
        return np.nanmean(np.abs(data - np.nanmean(data, axis=0)), axis=0)

    def mf_sub2(self, x1, x2):
        xx1 = x1 - np.nanmean(x1, axis=0)
        xx2 = x2 - np.nanmean(x2, axis=0)
        d1 = np.exp(-np.power(xx1 - np.nanmean(xx1, axis=0), 2) /
                    (2 * np.power(np.nanstd(xx1, axis=0), 2)))
        d2 = np.exp(-np.power(xx2 - np.nanmean(xx1, axis=0), 2) /
                    (2 * np.power(np.nanstd(xx2, axis=0), 2)))
        result = np.nanmean(np.log(np.cosh(d1 - d2)), axis=0)
        return result

    def mf_sub3(self, x1, x2):
        xx1 = x1 - np.nanmean(x1, axis=0)
        xx2 = x2 - np.nanmean(x2, axis=0)
        t = xx1 * xx2
        nancount = np.isnan(t).sum(axis=0)
        dot = np.nansum(t, axis=0)
        dot[nancount == t.shape[0]] = np.nan
        t = np.vstack((np.nanstd(xx1, axis=0), np.nanstd(xx2, axis=0)))
        nancount = np.isnan(t).sum(axis=0)
        sigma = np.nansum(t, axis=0)
        sigma[nancount == t.shape[0]] = np.nan
        result = np.tanh(dot / (2 * np.power(sigma, 2)))
        return result

    def factor_mf1(self,
                   data=None,
                   dependencies=[
                       'dummy120_fst', 'stkfwd_VALUE_DIFF_MED_TRADER',
                       'stkfwd_VALUE_DIFF_SMALL_TRADER', 'sw1'
                   ],
                   window=10):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        value_diff_med_trader = data['stkfwd_VALUE_DIFF_MED_TRADER']
        value_diff_small_trader = data['stkfwd_VALUE_DIFF_SMALL_TRADER']
        factor = (value_diff_med_trader.rolling(10, min_periods=5).mean().sub(
            value_diff_small_trader.rolling(10, min_periods=5).mean(),
            fill_value=0))
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_mf1")

    def factor_mf2(self,
                   data=None,
                   dependencies=[
                       'dummy120_fst', 'stkfwd_BUY_TRADES_SMALL_ORDER',
                       'stkfwd_BUY_VALUE_SMALL_ORDER', 'sw1'
                   ],
                   window=30):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        buy_trades_small_order = data['stkfwd_BUY_TRADES_SMALL_ORDER']
        buy_value_small_order = data['stkfwd_BUY_VALUE_SMALL_ORDER']
        x1_rolling = rolling_window(buy_trades_small_order.values, 30)
        x2_rolling = rolling_window(buy_value_small_order.values, 30)
        factor = pd.DataFrame(map(lambda x1, x2: self.mf_sub2(x1, x2),
                                  x1_rolling, x2_rolling),
                              index=buy_trades_small_order.index,
                              columns=buy_trades_small_order.columns)
        c = factor.rolling(30, min_periods=0).count()
        factor[c < 10] = np.nan
        factor[np.isinf(factor)] = np.nan
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_mf2")

    def factor_mf3(self,
                   data=None,
                   dependencies=[
                       'dummy120_fst', 'stkfwd_VALUE_DIFF_INSTITUTE',
                       'stkfwd_VALUE_DIFF_SMALL_TRADER', 'sw1'
                   ],
                   window=60):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        value_diff_institute = data['stkfwd_VALUE_DIFF_INSTITUTE']
        value_diff_small_trader = data['stkfwd_VALUE_DIFF_SMALL_TRADER']
        factor = -(value_diff_institute.rolling(60, min_periods=30).skew().add(
            value_diff_small_trader.rolling(60, min_periods=30).skew(),
            fill_value=0))
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_mf3")

    def factor_mf4(self,
                   data=None,
                   dependencies=[
                       'dummy120_fst', 'stkfwd_NET_INFLOW_RATE_VALUE',
                       'stkfwd_MONEYFLOW_PCT_VOLUME', 'sw1'
                   ],
                   window=40):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        net_inflow_rate_value = data['stkfwd_NET_INFLOW_RATE_VALUE']
        moneyflow_pct_volume = data['stkfwd_MONEYFLOW_PCT_VOLUME']
        x1_rolling = rolling_window(net_inflow_rate_value.values, 40)
        x2_rolling = rolling_window(moneyflow_pct_volume, 40)
        f1 = pd.DataFrame(map(lambda x1, x2: self.mf_sub3(x1, x2), x1_rolling,
                              x2_rolling),
                          index=net_inflow_rate_value.index,
                          columns=net_inflow_rate_value.columns)
        c1 = f1.rolling(40, min_periods=0).count()
        f1[c1 < 20] = np.nan
        f1[np.isinf(f1)] = np.nan
        factor = f1
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_mf4")

    def factor_mf5(self,
                   data=None,
                   dependencies=[
                       'dummy120_fst', 'stkfwd_SELL_VALUE_LARGE_ORDER_ACT',
                       'ret', 'sw1'
                   ],
                   window=50):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        sell_value_large_order_act = data['stkfwd_SELL_VALUE_LARGE_ORDER_ACT']
        ret = data['ret']
        x1_rolling = rolling_window(sell_value_large_order_act.values, 50)
        x2_rolling = rolling_window(ret.values, 50)
        factor = -pd.DataFrame(map(lambda x1, x2: self.mf_sub3(x1, x2),
                                   x1_rolling, x2_rolling),
                               index=ret.index,
                               columns=ret.columns)
        c = factor.rolling(50, min_periods=0).count()
        factor[c < 10] = np.nan
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_mf5")

    def factor_mf6(self,
                   data=None,
                   dependencies=[
                       'dummy120_fst', 'stkfwd_OPEN_NET_INFLOW_RATE_VALUE',
                       'sw1'
                   ],
                   window=30):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        open_net_inflow_rate_value = data['stkfwd_OPEN_NET_INFLOW_RATE_VALUE']
        factor = open_net_inflow_rate_value.rolling(30, min_periods=10).sum()
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_mf6")

    def factor_mf7(self,
                   data=None,
                   dependencies=[
                       'dummy120_fst', 'stkfwd_OPEN_MONEYFLOW_PCT_VALUE',
                       'turnoverValue', 'sw1'
                   ],
                   window=20):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        amount = data['turnoverValue']
        open_moneyflow_pct_value = data['stkfwd_OPEN_MONEYFLOW_PCT_VALUE']
        f = open_moneyflow_pct_value / amount
        f[np.isinf(f)] = np.nan
        factor = f.rolling(20, min_periods=5).mean()
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_mf7")

    def factor_mf8(self,
                   data=None,
                   dependencies=[
                       'dummy120_fst', 'stkfwd_BUY_VALUE_EXLARGE_ORDER',
                       'stkfwd_SELL_VALUE_EXLARGE_ORDER',
                       'stkfwd_BUY_VALUE_EXLARGE_ORDER_ACT',
                       'stkfwd_SELL_VALUE_EXLARGE_ORDER_ACT', 'sw1'
                   ],
                   window=30):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        buy_value_exlarge_order = data['stkfwd_BUY_VALUE_EXLARGE_ORDER']
        sell_value_exlarge_order = data['stkfwd_SELL_VALUE_EXLARGE_ORDER']
        buy_value_exlarge_order_act = data[
            'stkfwd_BUY_VALUE_EXLARGE_ORDER_ACT']
        sell_value_exlarge_order_act = data[
            'stkfwd_SELL_VALUE_EXLARGE_ORDER_ACT']
        f1 = buy_value_exlarge_order.sub(sell_value_exlarge_order,
                                         fill_value=0)
        f2 = abs(
            buy_value_exlarge_order_act.sub(sell_value_exlarge_order_act,
                                            fill_value=0))
        factor = (-f1.rolling(30, min_periods=10).sum() /
                  f2.rolling(30, min_periods=10).sum())
        factor[np.isinf(factor)] = np.nan
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_mf8")

    def factor_mf9(self,
                   data=None,
                   dependencies=[
                       'dummy120_fst', 'stkfwd_BUY_VALUE_LARGE_ORDER',
                       'stkfwd_SELL_VALUE_LARGE_ORDER',
                       'stkfwd_BUY_VALUE_LARGE_ORDER_ACT',
                       'stkfwd_SELL_VALUE_LARGE_ORDER_ACT', 'sw1'
                   ],
                   window=120):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        buy_value_large_order = data['stkfwd_BUY_VALUE_LARGE_ORDER']
        sell_value_large_order = data['stkfwd_SELL_VALUE_LARGE_ORDER']
        buy_value_large_order_act = data['stkfwd_BUY_VALUE_LARGE_ORDER_ACT']
        sell_value_large_order_act = data['stkfwd_SELL_VALUE_LARGE_ORDER_ACT']
        f1 = buy_value_large_order.sub(sell_value_large_order, fill_value=0)
        f2 = abs(
            buy_value_large_order_act.sub(sell_value_large_order_act,
                                          fill_value=0))
        factor = -abs(
            f1.rolling(120, min_periods=60).sum() /
            f2.rolling(120, min_periods=60).sum())
        factor[np.isinf(factor)] = np.nan
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_mf9")

    def factor_mf10(self,
                    data=None,
                    dependencies=[
                        'dummy120_fst', 'stkfwd_BUY_VALUE_SMALL_ORDER_ACT',
                        'stkfwd_SELL_TRADES_SMALL_ORDER', 'sw1'
                    ],
                    window=30):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        buy_value_small_order_act = data['stkfwd_BUY_VALUE_SMALL_ORDER_ACT']
        sell_trades_small_order = data['stkfwd_SELL_TRADES_SMALL_ORDER']
        a1 = buy_value_small_order_act.rolling(30, min_periods=10).mean()
        a2 = sell_trades_small_order.rolling(30, min_periods=10).mean()
        b1_rolling = rolling_window(buy_value_small_order_act.values, 30)
        b1 = pd.DataFrame(map(lambda x: self.mf_sub1(x), b1_rolling),
                          index=a1.index,
                          columns=a1.columns)
        c1 = b1.rolling(30, min_periods=0).count()
        b1[c1 < 10] = np.nan
        b2_rolling = rolling_window(sell_trades_small_order.values, 30)
        b2 = pd.DataFrame(map(lambda x: self.mf_sub1(x), b2_rolling),
                          index=a1.index,
                          columns=a1.columns)
        c2 = b2.rolling(30, min_periods=0).count()
        b2[c2 < 10] = np.nan
        b1[b1 == 0] = np.nan
        b2[b2 == 0] = np.nan
        factor = (b1 * np.exp(-abs(a1 - a2) / b1) +
                  abs(a1 - a2)) / b2 + np.log(b2 / b1) - 1
        factor[np.isinf(factor)] = np.nan
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_mf10")

    def factor_mf11(self,
                    data=None,
                    dependencies=[
                        'dummy120_fst', 'stkfwd_S_MFD_INFLOW_OPEN',
                        'stkfwd_S_MFD_INFLOW_CLOSE', 'sw1'
                    ],
                    window=80):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        s_mfd_inflow_open = data['stkfwd_S_MFD_INFLOW_OPEN']
        s_mfd_inflow_close = data['stkfwd_S_MFD_INFLOW_CLOSE']
        factor = (s_mfd_inflow_open.rolling(80, min_periods=40).mean().sub(
            s_mfd_inflow_close.rolling(80, min_periods=40).mean(),
            fill_value=0))
        factor = indfill_median(factor * dummy, sw1)
        return self._format(factor, "factor_mf11")

    def factor_mf12(self,
                    data=None,
                    dependencies=[
                        'dummy120_fst', 'stkfwd_OPEN_MONEYFLOW_PCT_VALUE_L',
                        'sw1'
                    ],
                    window=60):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        open_moneyflow_pct_value_l = data['stkfwd_OPEN_MONEYFLOW_PCT_VALUE_L']
        factor = -abs(
            open_moneyflow_pct_value_l.rolling(60, min_periods=30).sum())
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_mf12")