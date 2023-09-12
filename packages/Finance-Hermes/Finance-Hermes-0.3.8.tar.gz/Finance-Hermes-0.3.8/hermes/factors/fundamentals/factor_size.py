# -*- encoding:utf-8 -*-
import numpy as np
import pandas as pd
from alphakit.const import *
from alphakit.factor import *
from alphakit.portfolio import *
from alphakit.data import *

from hermes.factors.base import FactorBase, LongCallMixin, ShortCallMixin
from jdwdata.RetrievalAPI import get_data_by_map


class FactorSize(FactorBase, LongCallMixin, ShortCallMixin):

    def __init__(self, data_format, **kwargs):
        __str__ = 'factor_size'
        self.category = 'Size'
        self.name = '规模因子'
        self._data_format = data_format
        self._data = self.init_data(**kwargs) if 'end_date' in kwargs else None
        data = get_data_by_map(columns=BARRA_ALL_K,
                               begin_date=self.begin_date,
                               end_date=self.end_date,
                               method='ddb')
        self._risksizeindu = getdataset(data, BARRA_SIZEIND_K)

    def _init_self(self, **kwargs):
        pass

    def factor_size1(self,
                     data=None,
                     dependencies=['dummy120_fst', 'fuqer_NegMktValue', 'sw1'],
                     window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        factor = -data['fuqer_NegMktValue']
        factor = indfill_median(factor * dummy, sw1)
        return self._format(factor, "factor_size1")

    def factor_size2(
            self,
            data=None,
            dependencies=['dummy120_fst', 'ffancy_aShareholderZ', 'sw1'],
            window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        factor = data['ffancy_aShareholderZ']
        factor = indfill_median(factor * dummy, sw1)
        return self._format(factor, "factor_size2")

    def factor_size3(self,
                     data=None,
                     dependencies=['dummy120_fst', 'f_SIZENL', 'sw1'],
                     window=1):
        data = self._data if data is None else data
        dummy = data['dummy120_fst']
        sw1 = data['sw1']
        factor = data['f_SIZENL']
        factor = indfill_median(factor * dummy, sw1)
        factor = alphaOpNeu(factor * dummy, self._risksizeindu)
        return self._format(factor, "factor_size3")