# -*- encoding:utf-8 -*-
import numpy as np
import pandas as pd
from hermes.factors.technical.core.utilities import *


def adx(high,
        low,
        close,
        length=None,
        lensig=None,
        scalar=None,
        drift=None,
        offset=None,
        **kwargs):
    from hermes.factors.technical.core.volatility import atr
    from hermes.factors.technical.core.overlap import rma
    length = length if length and length > 0 else 14
    lensig = lensig if lensig and lensig > 0 else length
    scalar = float(scalar) if scalar else 100
    drift = int(drift) if isinstance(drift, int) and drift != 0 else 1
    offset = int(offset) if isinstance(offset, int) else 0

    if high is None or low is None or close is None: return

    # Calculate Result
    atr_ = atr(high=high, low=low, close=close, length=length)

    up = high - high.shift(drift)  # high.diff(drift)
    dn = low.shift(drift) - low  # low.diff(-drift).shift(drift)

    pos = ((up > dn) & (up > 0)) * up
    neg = ((dn > up) & (dn > 0)) * dn

    k = scalar / atr_
    dmp = k * rma(pos, length=length)
    dmn = k * rma(neg, length=length)

    dx = scalar * (dmp - dmn).abs() / (dmp + dmn)
    adx = rma(dx, length=lensig)

    # Offset
    if offset != 0:
        dmp = dmp.shift(offset)
        dmn = dmn.shift(offset)
        adx = adx.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        adx.fillna(kwargs["fillna"], inplace=True)
        dmp.fillna(kwargs["fillna"], inplace=True)
        dmn.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        adx.fillna(method=kwargs["fill_method"], inplace=True)
        dmp.fillna(method=kwargs["fill_method"], inplace=True)
        dmn.fillna(method=kwargs["fill_method"], inplace=True)
    return adx, dmp, dmn


def amat(close=None,
         fast=None,
         slow=None,
         lookback=None,
         offset=None,
         **kwargs):
    from hermes.factors.technical.core.overlap import ema
    fast = int(fast) if fast and fast > 0 else 8
    slow = int(slow) if slow and slow > 0 else 21
    lookback = int(lookback) if lookback and lookback > 0 else 2
    offset = int(offset) if isinstance(offset, int) else 0

    # # Calculate Result
    fast_ma = ema(close, length=fast, **kwargs)
    slow_ma = ema(close, length=slow, **kwargs)

    mas_long = long_run(fast_ma, slow_ma, length=lookback)
    mas_short = short_run(fast_ma, slow_ma, length=lookback)

    # Offset
    if offset != 0:
        mas_long = mas_long.shift(offset)
        mas_short = mas_short.shift(offset)

    # # Handle fills
    if "fillna" in kwargs:
        mas_long.fillna(kwargs["fillna"], inplace=True)
        mas_short.fillna(kwargs["fillna"], inplace=True)

    if "fill_method" in kwargs:
        mas_long.fillna(method=kwargs["fill_method"], inplace=True)
        mas_short.fillna(method=kwargs["fill_method"], inplace=True)
    return mas_long, mas_short


def chop(high,
         low,
         close,
         length=None,
         atr_length=None,
         ln=None,
         scalar=None,
         drift=None,
         offset=None,
         **kwargs):
    from hermes.factors.technical.core.volatility import atr
    length = int(length) if length and length > 0 else 14
    atr_length = int(
        atr_length) if atr_length is not None and atr_length > 0 else 1
    ln = bool(ln) if isinstance(ln, bool) else False
    scalar = float(scalar) if scalar else 100

    offset = int(offset) if isinstance(offset, int) else 0

    drift = int(drift) if isinstance(drift, int) and drift != 0 else 1

    # Calculate Result
    diff = high.rolling(length).max() - low.rolling(length).min()

    atr_ = atr(high=high, low=low, close=close, length=atr_length)
    atr_sum = atr_.rolling(length).sum()

    chop = scalar
    if ln:
        chop *= (np.log(atr_sum) - np.log(diff)) / np.log(length)
    else:
        chop *= (np.log10(atr_sum) - np.log10(diff)) / np.log10(length)

    # Offset
    if offset != 0:
        chop = chop.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        chop.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        chop.fillna(method=kwargs["fill_method"], inplace=True)

    return chop


def cksp(high,
         low,
         close,
         p=None,
         x=None,
         q=None,
         tvmode=None,
         offset=None,
         **kwargs):
    from hermes.factors.technical.core.volatility import atr
    p = int(p) if p and p > 0 else 10
    x = float(x) if x and x > 0 else 1 if tvmode is True else 3
    q = int(q) if q and q > 0 else 9 if tvmode is True else 20

    offset = int(offset) if isinstance(offset, int) else 0

    tvmode = tvmode if isinstance(tvmode, bool) else True

    atr_ = atr(high=high, low=low, close=close, length=p)

    long_stop_ = high.rolling(p).max() - x * atr_
    long_stop = long_stop_.rolling(q).max()

    short_stop_ = low.rolling(p).min() + x * atr_
    short_stop = short_stop_.rolling(q).min()

    # Offset
    if offset != 0:
        long_stop = long_stop.shift(offset)
        short_stop = short_stop.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        long_stop.fillna(kwargs["fillna"], inplace=True)
        short_stop.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        long_stop.fillna(method=kwargs["fill_method"], inplace=True)
        short_stop.fillna(method=kwargs["fill_method"], inplace=True)

    return long_stop, short_stop


def decreasing(close,
               length=None,
               strict=None,
               asint=None,
               percent=None,
               drift=None,
               offset=None,
               **kwargs):
    length = int(length) if length and length > 0 else 1
    strict = strict if isinstance(strict, bool) else False
    asint = asint if isinstance(asint, bool) else True
    drift = int(drift) if isinstance(drift, int) and drift != 0 else 1
    offset = int(offset) if isinstance(offset, int) else 0
    percent = float(percent) if is_percent(percent) else False

    if close is None: return

    # Calculate Result
    close_ = (1 - 0.01 * percent) * close if percent else close
    if strict:
        # Returns value as float64? Have to cast to bool
        decreasing = close < close_.shift(drift)
        for x in range(3, length + 1):
            decreasing = decreasing & (close.shift(x - (drift + 1)) <
                                       close_.shift(x - drift))

        decreasing.fillna(0, inplace=True)
        decreasing = decreasing.astype(bool)
    else:
        decreasing = close_.diff(length) < 0

    if asint:
        decreasing = decreasing.astype(int)

    # Offset
    if offset != 0:
        decreasing = decreasing.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        decreasing.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        decreasing.fillna(method=kwargs["fill_method"], inplace=True)

    return decreasing


def dpo(close, length=None, centered=True, offset=None, **kwargs):
    from hermes.factors.technical.core.overlap import sma
    length = int(length) if length and length > 0 else 20
    offset = int(offset) if isinstance(offset, int) else 0

    if not kwargs.get("lookahead", True):
        centered = False

    # Calculate Result
    t = int(0.5 * length) + 1
    ma = sma(close, length)

    dpo = close - ma.shift(t)
    if centered:
        dpo = (close.shift(t) - ma).shift(t)

    # Offset
    if offset != 0:
        dpo = dpo.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        dpo.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        dpo.fillna(method=kwargs["fill_method"], inplace=True)

    return dpo


def increasing(close,
               length=None,
               strict=None,
               asint=None,
               percent=None,
               drift=None,
               offset=None,
               **kwargs):
    length = int(length) if length and length > 0 else 1
    strict = strict if isinstance(strict, bool) else False
    asint = asint if isinstance(asint, bool) else True
    drift = int(drift) if isinstance(drift, int) and drift != 0 else 1
    offset = int(offset) if isinstance(offset, int) else 0
    percent = float(percent) if is_percent(percent) else False

    if close is None: return

    # Calculate Result
    close_ = (1 + 0.01 * percent) * close if percent else close
    if strict:
        increasing = close > close_.shift(drift)
        for x in range(3, length + 1):
            increasing = increasing & (close.shift(x - (drift + 1)) >
                                       close_.shift(x - drift))

        increasing.fillna(0, inplace=True)
        increasing = increasing.astype(bool)
    else:
        increasing = close_.diff(length) > 0

    if asint:
        increasing = increasing.astype(int)

    # Offset
    if offset != 0:
        increasing = increasing.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        increasing.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        increasing.fillna(method=kwargs["fill_method"], inplace=True)

    return increasing


def long_run(fast, slow, length=None, offset=None, **kwargs):
    length = int(length) if length and length > 0 else 2
    offset = int(offset) if isinstance(offset, int) else 0

    if fast is None or slow is None: return

    # Calculate Result
    pb = increasing(fast, length) & decreasing(
        slow, length)  # potential bottom or bottom
    bi = increasing(fast, length) & increasing(
        slow, length)  # fast and slow are increasing
    long_run = pb | bi

    # Offset
    if offset != 0:
        long_run = long_run.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        long_run.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        long_run.fillna(method=kwargs["fill_method"], inplace=True)

    return long_run


def qstick(open, close, length=None, offset=None, **kwargs):
    from hermes.factors.technical.core.overlap import dema, ema, hma, rma, sma
    length = int(length) if length and length > 0 else 10
    ma = kwargs.pop("ma", "sma")
    offset = int(offset) if isinstance(offset, int) else 0

    # Calculate Result
    diff = non_zero_range(close, open)

    if ma == "dema":
        qstick = dema(diff, length=length, **kwargs)
    elif ma == "ema":
        qstick = ema(diff, length=length, **kwargs)
    elif ma == "hma":
        qstick = hma(diff, length=length)
    elif ma == "rma":
        qstick = rma(diff, length=length)
    else:  # "sma"
        qstick = sma(diff, length=length)

    # Offset
    if offset != 0:
        qstick = qstick.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        qstick.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        qstick.fillna(method=kwargs["fill_method"], inplace=True)
    return qstick


def short_run(fast, slow, length=None, offset=None, **kwargs):
    length = int(length) if length and length > 0 else 2
    offset = int(offset) if isinstance(offset, int) else 0

    if fast is None or slow is None: return

    # Calculate Result
    pt = decreasing(fast, length) & increasing(slow,
                                               length)  # potential top or top
    bd = decreasing(fast, length) & decreasing(
        slow, length)  # fast and slow are decreasing
    short_run = pt | bd

    # Offset
    if offset != 0:
        short_run = short_run.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        short_run.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        short_run.fillna(method=kwargs["fill_method"], inplace=True)

    return short_run


def tsignals(trend,
             asbool=None,
             trend_reset=0,
             trade_offset=None,
             drift=None,
             offset=None,
             **kwargs):
    asbool = bool(asbool) if isinstance(asbool, bool) else False
    trend_reset = int(trend_reset) if trend_reset and isinstance(
        trend_reset, int) else 0
    if trade_offset != 0:
        trade_offset = int(trade_offset) if trade_offset and isinstance(
            trade_offset, int) else 0
    drift = int(drift) if isinstance(drift, int) and drift != 0 else 1
    offset = int(offset) if isinstance(offset, int) else 0

    # Calculate Result
    trends = trend.astype(int)
    trades = trends.diff(drift).shift(trade_offset).fillna(0).astype(int)
    entries = (trades > 0).astype(int)
    exits = (trades < 0).abs().astype(int)

    if asbool:
        trends = trends.astype(bool)
        entries = entries.astype(bool)
        exits = exits.astype(bool)

    # Offset
    if offset != 0:
        df = df.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        trends.fillna(kwargs["fillna"], inplace=True)
        trades.fillna(kwargs["fillna"], inplace=True)
        entries.fillna(kwargs["fillna"], inplace=True)
        exits.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        trends.fillna(method=kwargs["fill_method"], inplace=True)
        trades.fillna(method=kwargs["fill_method"], inplace=True)
        entries.fillna(method=kwargs["fill_method"], inplace=True)
        exits.fillna(method=kwargs["fill_method"], inplace=True)
    return trends, trades, entries, exits


def ttm_trend(high, low, close, length=None, offset=None, **kwargs):
    from hermes.factors.technical.core.overlap import hl2
    length = int(length) if length and length > 0 else 6
    offset = int(offset) if isinstance(offset, int) else 0

    # Calculate Result
    trend_avg = hl2(high, low)
    for i in range(1, length):
        trend_avg = trend_avg + hl2(high.shift(i), low.shift(i))

    trend_avg = trend_avg / length

    tm_trend = (close > trend_avg).astype(int)
    tm_trend.replace(0, -1, inplace=True)

    # Offset
    if offset != 0:
        tm_trend = tm_trend.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        tm_trend.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        tm_trend.fillna(method=kwargs["fill_method"], inplace=True)

    return tm_trend


def vhf(close, length=None, drift=None, offset=None, **kwargs):
    length = int(length) if length and length > 0 else 28
    drift = int(drift) if isinstance(drift, int) and drift != 0 else 1
    offset = int(offset) if isinstance(offset, int) else 0

    # Calculate Result
    hcp = close.rolling(length).max()
    lcp = close.rolling(length).min()
    diff = np.fabs(close.diff(drift))
    vhf = np.fabs(non_zero_range(hcp, lcp)) / diff.rolling(length).sum()

    # Offset
    if offset != 0:
        vhf = vhf.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        vhf.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        vhf.fillna(method=kwargs["fill_method"], inplace=True)
    return vhf


def vortex(high, low, close, length=None, drift=None, offset=None, **kwargs):
    from hermes.factors.technical.core.volatility import true_range
    length = length if length and length > 0 else 14
    min_periods = int(
        kwargs["min_periods"]) if "min_periods" in kwargs and kwargs[
            "min_periods"] is not None else length
    drift = int(drift) if isinstance(drift, int) and drift != 0 else 1
    offset = int(offset) if isinstance(offset, int) else 0

    # Calculate Result
    tr = true_range(high=high, low=low, close=close)
    tr_sum = tr.rolling(length, min_periods=min_periods).sum()

    vmp = (high - low.shift(drift)).abs()
    vmm = (low - high.shift(drift)).abs()

    vip = vmp.rolling(length, min_periods=min_periods).sum() / tr_sum
    vim = vmm.rolling(length, min_periods=min_periods).sum() / tr_sum

    # Offset
    if offset != 0:
        vip = vip.shift(offset)
        vim = vim.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        vip.fillna(kwargs["fillna"], inplace=True)
        vim.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        vip.fillna(method=kwargs["fill_method"], inplace=True)
        vim.fillna(method=kwargs["fill_method"], inplace=True)
    return vip, vim
