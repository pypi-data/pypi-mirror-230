# -*- encoding:utf-8 -*-
import numpy as np
import pandas as pd


def down_volatility(close, length=None, offset=None, **kwargs):
    length = int(length) if length and length > 0 else 4
    offset = int(offset) if isinstance(offset, int) else 0

    v = np.log(close / close.shift(1))
    down_g = v[v < 0].fillna(0)
    v1 = np.power(v, 2).rolling(length).sum()
    v2 = np.power(down_g, 2).rolling(length).sum()

    dv = v2 / v1

    # Offset
    if offset != 0:
        dv = dv.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        dv.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        dv.fillna(method=kwargs["fill_method"], inplace=True)

    return dv


def flowin_ratio(close, values, length=None, offset=None, **kwargs):
    length = int(length) if length and length > 0 else 4
    offset = int(offset) if isinstance(offset, int) else 0

    v = close * values * np.sign(close - close.shift(1))
    fr = v.rolling(length).sum() / values.rolling(length).sum()

    # Offset
    if offset != 0:
        fr = fr.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        fr.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        fr.fillna(method=kwargs["fill_method"], inplace=True)

    return fr


def rhhi(values, length=None, offset=None, **kwargs):
    length = int(length) if length and length > 0 else 1
    offset = int(offset) if isinstance(offset, int) else 0

    rhhi = (values.pct_change() /
            values.pct_change().abs().rolling(length).sum())**2

    # Offset
    if offset != 0:
        rhhi = rhhi.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        rhhi.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        rhhi.fillna(method=kwargs["fill_method"], inplace=True)

    return rhhi


def retd(close, length=None, offset=None, **kwargs):
    length = int(length) if length and length > 0 else 1

    offset = int(offset) if isinstance(offset, int) else 0

    retd = close.pct_change().rolling(
        1).sum() / close.pct_change().abs().rolling(length).sum()

    # Offset
    if offset != 0:
        retd = retd.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        retd.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        retd.fillna(method=kwargs["fill_method"], inplace=True)

    return retd


def vretd(close, values, length=None, offset=None, **kwargs):
    length = int(length) if length and length > 0 else 1
    offset = int(offset) if isinstance(offset, int) else 0

    vretd = (values * close.pct_change()).rolling(length).sum() / (
        values * close.pct_change().abs()).rolling(length).sum()

    # Offset
    if offset != 0:
        vretd = vretd.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        vretd.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        vretd.fillna(method=kwargs["fill_method"], inplace=True)

    return vretd


def vvol(values, length=None, offset=None, **kwargs):
    length = int(length) if length and length > 0 else 1
    offset = int(offset) if isinstance(offset, int) else 0

    vvol = values.pct_change().rolling(length).std()

    # Offset
    if offset != 0:
        vvol = vvol.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        vvol.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        vvol.fillna(method=kwargs["fill_method"], inplace=True)

    return vvol


def vskew(values, length=None, offset=None, **kwargs):
    length = int(length) if length and length > 0 else 1
    offset = int(offset) if isinstance(offset, int) else 0

    vskew = values.pct_change().rolling(length).skew()

    # Offset
    if offset != 0:
        vskew = vskew.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        vskew.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        vskew.fillna(method=kwargs["fill_method"], inplace=True)

    return vskew


def vkurt(values, length=None, offset=None, **kwargs):
    length = int(length) if length and length > 0 else 1
    offset = int(offset) if isinstance(offset, int) else 0

    vkurt = values.pct_change().rolling(length).kurt()

    # Offset
    if offset != 0:
        vkurt = vkurt.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        vkurt.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        vkurt.fillna(method=kwargs["fill_method"], inplace=True)

    return vkurt


def optimal_mom(close, length=None, offset=None, **kwargs):
    length = int(length) if length and length > 0 else 5
    offset = int(offset) if isinstance(offset, int) else 0

    v = close.pct_change().rolling(length).mean()
    mom = (
        v *
        (np.abs(v) / np.abs(v).rolling(length).sum())).rolling(length).sum()

    # Offset
    if offset != 0:
        mom = mom.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        mom.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        mom.fillna(method=kwargs["fill_method"], inplace=True)

    return mom


def cross_start(close, index_close, length=None, offset=None, **kwargs):
    length = int(length) if length and length > 0 else 5
    offset = int(offset) if isinstance(offset, int) else 0

    change = close.pct_change() - index_close.pct_change()

    high_change = change.rolling(length).max()
    low_change = change.rolling(length).min()
    open_change = change.shift(length)
    close_change = change

    oc = close_change - open_change
    lh = high_change - low_change
    lc = close_change - low_change

    cond1 = open_change > close_change

    oc[cond1] = (open_change - close_change)
    lh[cond1] = (low_change - high_change)
    lc[cond1] = (low_change - close_change)

    H = (oc > 0.005)
    T = (lh.abs() > oc.abs() * 3)
    D = (lc.abs() > oc.abs() * 3)

    cond2 = H & T & D
    oc[cond2] = 0.1

    cross_start = oc

    # Offset
    if offset != 0:
        cross_start = cross_start.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        cross_start.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        cross_start.fillna(method=kwargs["fill_method"], inplace=True)

    return cross_start


def yello_rps(close,
              long_length=None,
              middle_length=None,
              short_length=None,
              long_ratio=None,
              middle_ratio=None,
              short_ratio=None,
              offset=None,
              **kwargs):

    short_length = int(
        short_length) if short_length and short_length > 0 else 10
    middle_length = int(
        middle_length) if middle_length and middle_length > 0 else 20
    long_length = int(long_length) if long_length and long_length > 0 else 30

    long_ratio = float(long_ratio) if long_ratio and long_ratio > 0 else 0.5
    middle_ratio = float(
        middle_ratio) if middle_ratio and middle_ratio > 0 else 0.3
    short_ratio = float(
        short_ratio) if short_ratio and short_ratio > 0 else 0.2

    offset = int(offset) if isinstance(offset, int) else 0

    short_rps = close.pct_change(periods=short_length)
    middle_rps = close.pct_change(periods=middle_length)
    long_rps = close.pct_change(periods=long_length)

    cond1 = short_rps > 0.8
    cond2 = middle_rps > 0.8
    cond3 = long_rps > 0.8

    cond = cond1 & cond2 & cond3

    yello_rps = short_rps * short_ratio + middle_rps * middle_ratio + long_rps * long_ratio

    yello_rps[cond] = yello_rps[cond] * 1.5

    # Offset
    if offset != 0:
        yello_rps = yello_rps.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        yello_rps.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        yello_rps.fillna(method=kwargs["fill_method"], inplace=True)

    return yello_rps
