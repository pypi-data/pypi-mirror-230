# -*- encoding:utf-8 -*-
import copy, hashlib, json, inspect, pdb
import six as six
from abc import ABCMeta, abstractmethod
from jdwdata.RetrievalAPI import get_data_by_map
from jdwdate.api import *
from hermes.kdutils.create_id import create_id
from hermes.kdutils.lazy import LazyFunc
from hermes.kdutils.base import ParamBase, FreezeAttrMixin


class LongCallMixin(FreezeAttrMixin):
    """
        混入类，混入代表多头，不完全是期权中buy call的概念，
    """

    @LazyFunc
    def long_type_str(self):
        """用来区别多头类型unique 值为call"""
        return "long"

    @LazyFunc
    def expect_direction(self):
        """期望收益方向，1.0即正向期望"""
        return 1.0


class ShortMixin(FreezeAttrMixin):
    """
        混入类，混入代表空头，应用场景在于期权，期货策略中，
        不完全是期权中buy put的概念，只代看跌反向操作，
        即期望买入后交易目标价格下跌，下跌带来收益
    """

    @LazyFunc
    def short_type_str(self):
        """用来区别买入类型unique 值为put"""
        return "short"

    @LazyFunc
    def expect_direction(self):
        """期望收益方向，1.0即反向期望"""
        return -1.0


class ShortMixin(FreezeAttrMixin):
    """
        混入类，混入代表空头，应用场景在于期权，期货策略中，
        不完全是期权中buy put的概念，只代看跌反向操作，
        即期望买入后交易目标价格下跌，下跌带来收益
    """

    @LazyFunc
    def short_type_str(self):
        """用来区别买入类型unique 值为put"""
        return "short"

    @LazyFunc
    def expect_direction(self):
        """期望收益方向，1.0即反向期望"""
        return -1.0


class ShortCallMixin(FreezeAttrMixin):
    """
        混入类，混入代表空头，应用场景在于期权，期货策略中，
        不完全是期权中buy put的概念，只代看跌反向操作，
        即期望买入后交易目标价格下跌，下跌带来收益
    """

    @LazyFunc
    def short_type_str(self):
        """用来区别买入类型unique 值为put"""
        return "short"

    @LazyFunc
    def expect_direction(self):
        """期望收益方向，1.0即反向期望"""
        return -1.0


class FactorBase(six.with_metaclass(ABCMeta, ParamBase)):

    def __init__(self, **kwargs):
        # 子类继续完成自有的构造
        self._init_self(**kwargs)

    @abstractmethod
    def _init_self(self, **kwargs):
        """子类因子针对可扩展参数的初始化"""
        pass

    def init_data(self, **kwargs):
        dependencies_list = self.get_dependencies()
        func_window = self.get_window()
        window = func_window if func_window > 0 else int(
            kwargs['window']) if 'window' in kwargs else 0
        method = 'ddb' if 'method' not in kwargs else kwargs['method']
        self.begin_date = kwargs['begin_date']
        self.end_date = kwargs['end_date']
        start_date = advanceDateByCalendar(
            'china.sse', self.begin_date,
            '-{0}b'.format(window)).strftime('%Y-%m-%d')
        data = get_data_by_map(columns=dependencies_list,
                               begin_date=start_date,
                               end_date=self.end_date,
                               method=method)
        return data

    def get_dependencies(self):
        dependencies_list = []
        member_func = self.factors_list()
        for func in member_func:
            func_module = getattr(self, func)
            fun_param = inspect.signature(func_module).parameters
            if 'dependencies' in fun_param:
                dependencies = fun_param['dependencies'].default
                dependencies_list += dependencies
        return list(set(dependencies_list))

    def get_window(self):
        window_list = []
        member_func = self.factors_list()
        for func in member_func:
            func_module = getattr(self, func)
            fun_param = inspect.signature(func_module).parameters
            if 'window' in fun_param:
                window = fun_param['window'].default
                window_list.append(window)
        return max(window_list, default=0)

    def _create_id(self, **kwargs):
        feature = copy.deepcopy(kwargs)
        feature['category'] = self.category
        s = hashlib.md5(
            json.dumps(feature).encode(encoding="utf-8")).hexdigest()
        return "{0}".format(create_id(original=s, digit=15))

    def _format2(self, data, name):
        data = data.stack()
        data.name = name
        data.category = self.category
        return data

    def _format(self, data, name, **kwargs):
        # 0 matrix  1 serise  2 DatFrame
        if not hasattr(self, 'begin_date') or not hasattr(self, 'begin_date'):
            data = data.stack()
            data.name = name
            data.category = self.category
            return data

        data = data.sort_values(by=['trade_date'])
        data = data.loc[self.begin_date:self.end_date]
        data_format = 1 if not hasattr(self,
                                       '_data_format') else self._data_format

        if data_format == 1 or data_format == 2:
            data = data.stack()
            if data_format == 2:
                data.name = 'value'
                data = data.reset_index()
                data['name'] = name
        data.name = name
        data.category = self.category
        data.id = self._create_id(name=name, **kwargs)
        return data

    def factors_list(self):
        return list(
            filter(
                lambda x: not x.startswith('_') and callable(getattr(self, x)),
                dir(self)))
