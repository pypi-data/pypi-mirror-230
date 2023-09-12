# -*- encoding:utf-8 -*-
import pdb
import numpy as np
from hermes.factors.technical.factor_overlap import *
from hermes.factors.technical.factor_statistics import *


def alpha101_4(low, length=None, offset=None, **kwargs):
    length = length if length and length > 0 else 9
    offset = int(offset) if isinstance(offset, int) else 0

    alpha4 = low.rank(axis=1, pct=True)

    # Offset
    if offset != 0:
        alpha4 = alpha4.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        alpha4.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        alpha4.fillna(method=kwargs["fill_method"], inplace=True)
    return alpha4


def alpha101_5(open, vwap, length=None, offset=None, **kwargs):
    length = length if length and length > 0 else 10
    offset = int(offset) if isinstance(offset, int) else 0

    ov = (open - vwap).rolling(length).mean()
    ro = ov.rank(axis=1, pct=True)
    ar = (open - vwap).rank(axis=1, pct=True).abs() * (-1.0)
    alpha5 = (ro * ar)

    # Offset
    if offset != 0:
        alpha5 = alpha5.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        alpha5.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        alpha5.fillna(method=kwargs["fill_method"], inplace=True)
    return alpha5


def alpha101_11(close,
                vwap,
                volume,
                length=None,
                periods=None,
                offset=None,
                **kwargs):
    length = length if length and length > 0 else 3
    periods = periods if periods and periods > 0 else 3
    offset = int(offset) if isinstance(offset, int) else 0

    tmax = (vwap - close).rolling(length).max()
    tmin = (vwap - close).rolling(length).min()
    dv = volume.diff(periods)

    rank_tmax = tmax.rank(axis=1, pct=True)
    rank_tmin = tmin.rank(axis=1, pct=True)
    rank_vol = dv.rank(axis=1, pct=True)

    alpha11 = (rank_tmax + rank_tmin) * rank_vol

    # Offset
    if offset != 0:
        alpha11 = alpha11.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        alpha11.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        alpha11.fillna(method=kwargs["fill_method"], inplace=True)
    return alpha11


def alpha101_12(close, volume, length=None, offset=None, **kwargs):
    length = length if length and length > 0 else 2
    offset = int(offset) if isinstance(offset, int) else 0

    alpha12 = np.sign(volume.diff(length)) * close.diff(length)
    alpha12 = alpha12 * -1

    # Offset
    if offset != 0:
        alpha12 = alpha12.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        alpha12.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        alpha12.fillna(method=kwargs["fill_method"], inplace=True)
    return alpha12


def alpha101_19(close, returns, fast=None, slow=None, offset=None, **kwargs):
    fast = fast if fast and fast > 0 else 7
    slow = slow if slow and slow > 0 else 10
    offset = int(offset) if isinstance(offset, int) else 0

    sign_se = np.sign(close.diff(fast))
    rank_se = 1 + returns.rolling(slow).sum().rank(axis=1, pct=True)
    alpha19 = -1 * sign_se * rank_se
    # Offset
    if offset != 0:
        alpha19 = alpha19.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        alpha19.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        alpha19.fillna(method=kwargs["fill_method"], inplace=True)
    return alpha19


def alpha101_23(high, fast=None, slow=None, offset=None, **kwargs):
    slow = slow if slow and slow > 0 else 20
    fast = fast if fast and fast > 0 else 2
    offset = int(offset) if isinstance(offset, int) else 0

    hm = high.rolling(slow).mean()
    mark = hm < high
    dh = -1.0 * high.diff(fast)
    dh[mark == False] = dh[mark == False] * 0.25
    alpha23 = dh
    # Offset
    if offset != 0:
        alpha23 = alpha23.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        alpha23.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        alpha23.fillna(method=kwargs["fill_method"], inplace=True)
    return alpha23


def alpha101_52(low,
                returns,
                volume,
                fast=None,
                slow=None,
                lw=None,
                sw=None,
                tsw=None,
                offset=None,
                **kwargs):

    fast = fast if fast and fast > 0 else 8
    slow = slow if slow and slow > 0 else 8
    lw = lw if lw and lw > 0 else 20
    sw = sw if sw and sw > 0 else 18
    tsw = tsw if tsw and tsw > 0 else 8
    offset = int(offset) if isinstance(offset, int) else 0

    part1 = low.shift(slow).rolling(fast).min() - low.rolling(fast).min()
    ret_se = returns.rolling(lw).sum() - returns.rolling(sw).sum()
    part2 = (ret_se / (1.0 * (lw - sw))).rank(pct=True)
    part3 = volume.rank(axis=1, pct=True)
    alpha52 = part1 * part2 * part3

    # Offset
    if offset != 0:
        alpha52 = alpha52.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        alpha52.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        alpha52.fillna(method=kwargs["fill_method"], inplace=True)

    return alpha52


def alpha101_53(close, low, high, length=None, offset=None, **kwargs):
    length = length if length and length > 0 else 9
    offset = int(offset) if isinstance(offset, int) else 0

    alpha53 = ((close * 2 - low - high) / (close - low + 0.001)).diff(length)

    # Offset
    if offset != 0:
        alpha53 = alpha53.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        alpha53.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        alpha53.fillna(method=kwargs["fill_method"], inplace=True)

    return alpha53


def alpha101_54(close, low, high, open, length=None, offset=None, **kwargs):
    length = length if length and length > 0 else 5
    offset = int(offset) if isinstance(offset, int) else 0

    numerator = (low - close + 0.001) * (open**5)
    denominator = (low - high + 0.001) * (close**5)
    alpha54 = (-1.0 * numerator / denominator).rolling(length).mean()
    alpha54[alpha54 == -1.0] = np.NaN

    # Offset
    if offset != 0:
        alpha54 = alpha54.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        alpha54.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        alpha54.fillna(method=kwargs["fill_method"], inplace=True)

    return alpha54


def alpha101_84(vwap,
                close,
                max_length=None,
                rank_length=None,
                diff_length=None,
                offset=None,
                **kwargs):

    max_length = max_length if max_length and max_length > 0 else 15
    rank_length = rank_length if rank_length and rank_length > 0 else 20
    diff_length = diff_length if diff_length and diff_length > 0 else 6
    offset = int(offset) if isinstance(offset, int) else 0

    price = vwap - vwap.rolling(max_length).max()
    part1 = price.rank(axis=1, pct=True)
    part2 = close.diff(periods=diff_length).rank(axis=1, pct=True)

    alpha84 = np.sign(part1) * (part1.abs()**part2)

    # Offset
    if offset != 0:
        alpha84 = alpha84.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        alpha84.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        alpha84.fillna(method=kwargs["fill_method"], inplace=True)

    return alpha84
