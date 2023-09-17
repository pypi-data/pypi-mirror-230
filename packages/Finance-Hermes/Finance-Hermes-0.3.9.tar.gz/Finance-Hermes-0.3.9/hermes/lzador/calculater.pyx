# -*- encoding:utf-8 -*-
import importlib, inspect, copy, pdb
import pandas as pd


def batch_factors(data, packet_name, class_name):
    class_module = importlib.import_module(packet_name).__getattribute__(
        class_name)
    res = []
    factors_func = class_module().factors_list()
    for func in factors_func:
        func_module = getattr(class_module, func)
        fun_param = inspect.signature(func_module).parameters
        dependencies = fun_param['dependencies'].default
        result = getattr(class_module(),
                         func)(copy.deepcopy(data[dependencies]))
        res.append(result)
    return pd.concat(res, axis=1)
