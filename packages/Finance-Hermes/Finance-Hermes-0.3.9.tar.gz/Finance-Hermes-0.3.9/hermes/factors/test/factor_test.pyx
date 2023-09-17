# -*- encoding:utf-8 -*-
import pdb
import numpy as np
from hermes.factors.base import FactorBase, LongCallMixin, ShortCallMixin


class FactorTest(FactorBase, LongCallMixin, ShortCallMixin):

    def __init__(self, data_format, **kwargs):
        __str__ = 'factor_test'
        self.category = 'test'
        self.name = 'Test Factor'
        self._data_format = data_format
        self._max_window = 10
        self._data = self.init_data(**kwargs) if 'end_date' in kwargs else None

    def _init_self(self, **kwargs):
        pass
    
    def test1(self, data=None, dependencies=['openPrice', 'closePrice', 'vwap'], window=0):
        data = self._data if data is None else data
        close_se = data['openPrice']
        dy_q_ti_se = data['closePrice']
        totalshares_se = data['vwap']
        dy_q_evebitda_caldr_se = close_se / (4 * dy_q_ti_se / totalshares_se)
        dy_q_evebitda_caldr_se[(dy_q_evebitda_caldr_se < 0) |
                               (np.isinf(dy_q_evebitda_caldr_se))] = np.nan
        return self._format(dy_q_evebitda_caldr_se, "test1")
    
    def test2(self, data=None, dependencies=['marketValue', 'turnoverVol', 'negMarketValue'], window=10):
        data = self._data if data is None else data
        close_se = data['marketValue']
        dy_q_ti_se = data['turnoverVol']
        totalshares_se = data['negMarketValue']
        dy_q_evebitda_caldr_se = close_se / (4 * dy_q_ti_se / totalshares_se)
        dy_q_evebitda_caldr_se[(dy_q_evebitda_caldr_se < 0) |
                               (np.isinf(dy_q_evebitda_caldr_se))] = np.nan
        return self._format(dy_q_evebitda_caldr_se, "test2")
    
    def test3(self, data=None, dependencies=['turnoverVol', 'closePrice'], window=14):
        data = self._data if data is None else data
        turnoverVol = data['turnoverVol']
        closePrice = data['closePrice']
        factor1 = turnoverVol * closePrice
        factor2 = turnoverVol + closePrice
        factors = {
            'factor3': self._format(factor1, "factor3"),
            'factor4': self._format(factor2, "factor4")
        }
        return factors