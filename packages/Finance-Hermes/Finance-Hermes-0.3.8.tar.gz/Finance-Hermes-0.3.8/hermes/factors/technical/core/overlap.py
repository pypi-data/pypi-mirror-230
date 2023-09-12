# -*- encoding:utf-8 -*-
import numpy as np
import pandas as pd
from hermes.factors.technical.core.utilities import *


def dema(close, length=None, offset=None, **kwargs):
    length = int(length) if length and length > 0 else 10
    offset = int(offset) if isinstance(offset, int) else 0
    ema1 = ema(close=close, length=length)
    ema2 = ema(close=ema1, length=length)
    dema = 2 * ema1 - ema2
    # Offset
    if offset != 0:
        dema = dema.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        dema.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        dema.fillna(method=kwargs["fill_method"], inplace=True)
    return dema


def ema(close, length=None, offset=None, **kwargs):
    """Indicator: Exponential Moving Average (EMA)"""
    # Validate Arguments
    length = int(length) if length and length > 0 else 10
    adjust = kwargs.pop("adjust", False)
    sma = kwargs.pop("sma", True)
    offset = int(offset) if isinstance(offset, int) else 0
    # Calculate Result
    if sma:
        close = close.copy()
        sma_nth = close[0:length].mean()
        close[:length - 1] = np.nan
        close.iloc[length - 1] = sma_nth
    ema = close.ewm(span=length, adjust=adjust).mean()

    # Offset
    if offset != 0:
        ema = ema.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        ema.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        ema.fillna(method=kwargs["fill_method"], inplace=True)
    return ema


def fwma(close, length=None, asc=None, offset=None, **kwargs):
    length = int(length) if length and length > 0 else 10
    asc = asc if asc else True
    offset = int(offset) if isinstance(offset, int) else 0
    # Calculate Result
    fibs = fibonacci(n=length, weighted=True)
    fwma = close.rolling(length, min_periods=length).apply(weights(fibs),
                                                           raw=True)
    # Offset
    if offset != 0:
        fwma = fwma.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        fwma.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        fwma.fillna(method=kwargs["fill_method"], inplace=True)
    return fwma


def hl2(high, low, offset=None, **kwargs):
    offset = int(offset) if isinstance(offset, int) else 0
    hl2 = 0.5 * (high + low)
    # Offset
    if offset != 0:
        hl2 = hl2.shift(offset)
    return hl2


def hlc3(high, low, close, offset=None, **kwargs):
    offset = int(offset) if isinstance(offset, int) else 0
    hlc3 = (high + low + close) / 3.0
    # Offset
    if offset != 0:
        hlc3 = hlc3.shift(offset)
    return hlc3


def hma(close, length=None, offset=None, **kwargs):
    length = int(length) if length and length > 0 else 10
    offset = int(offset) if isinstance(offset, int) else 0
    # Calculate Result
    half_length = int(length / 2)
    sqrt_length = int(np.sqrt(length))

    wmaf = wma(close=close, length=half_length)
    wmas = wma(close=close, length=length)
    hma = wma(close=2 * wmaf - wmas, length=sqrt_length)

    # Offset
    if offset != 0:
        hma = hma.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        hma.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        hma.fillna(method=kwargs["fill_method"], inplace=True)
    return hma


def ichimoku(high,
             low,
             close,
             tenkan=None,
             kijun=None,
             senkou=None,
             include_chikou=True,
             offset=None,
             **kwargs):
    offset = int(offset) if isinstance(offset, int) else 0
    tenkan = int(tenkan) if tenkan and tenkan > 0 else 9
    kijun = int(kijun) if kijun and kijun > 0 else 26
    senkou = int(senkou) if senkou and senkou > 0 else 52

    # Calculate Result
    tenkan_sen = midprice(high=high, low=low, length=tenkan)
    kijun_sen = midprice(high=high, low=low, length=kijun)
    span_a = 0.5 * (tenkan_sen + kijun_sen)
    span_b = midprice(high=high, low=low, length=senkou)

    # Copy Span A and B values before their shift
    _span_a = span_a[-kijun:].copy()
    _span_b = span_b[-kijun:].copy()

    span_a = span_a.shift(kijun)
    span_b = span_b.shift(kijun)
    chikou_span = close.shift(-kijun)

    # Offset
    if offset != 0:
        tenkan_sen = tenkan_sen.shift(offset)
        kijun_sen = kijun_sen.shift(offset)
        span_a = span_a.shift(offset)
        span_b = span_b.shift(offset)
        chikou_span = chikou_span.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        span_a.fillna(kwargs["fillna"], inplace=True)
        span_b.fillna(kwargs["fillna"], inplace=True)
        chikou_span.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        span_a.fillna(method=kwargs["fill_method"], inplace=True)
        span_b.fillna(method=kwargs["fill_method"], inplace=True)
        chikou_span.fillna(method=kwargs["fill_method"], inplace=True)

    return span_a, span_b


def midpoint(close, length=None, offset=None, **kwargs):
    length = int(length) if length and length > 0 else 2
    min_periods = int(
        kwargs["min_periods"]) if "min_periods" in kwargs and kwargs[
            "min_periods"] is not None else length
    offset = int(offset) if isinstance(offset, int) else 0
    lowest = close.rolling(length, min_periods=min_periods).min()
    highest = close.rolling(length, min_periods=min_periods).max()

    midpoint = 0.5 * (lowest + highest)

    # Offset
    if offset != 0:
        midpoint = midpoint.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        midpoint.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        midpoint.fillna(method=kwargs["fill_method"], inplace=True)
    return midpoint


def midprice(high, low, length=None, offset=None, **kwargs):
    length = int(length) if length and length > 0 else 2
    min_periods = int(
        kwargs["min_periods"]) if "min_periods" in kwargs and kwargs[
            "min_periods"] is not None else length
    offset = int(offset) if isinstance(offset, int) else 0
    lowest_low = low.rolling(length, min_periods=min_periods).min()
    highest_high = high.rolling(length, min_periods=min_periods).max()
    midprice = 0.5 * (lowest_low + highest_high)
    # Offset
    if offset != 0:
        midprice = midprice.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        midprice.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        midprice.fillna(method=kwargs["fill_method"], inplace=True)
    return midprice


def ohlc4(open, high, low, close, offset=None, **kwargs):
    offset = int(offset) if isinstance(offset, int) else 0
    # Calculate Result
    ohlc4 = 0.25 * (open + high + low + close)
    # Offset
    if offset != 0:
        ohlc4 = ohlc4.shift(offset)
    return ohlc4


def pwma(close, length=None, asc=None, offset=None, **kwargs):
    length = int(length) if length and length > 0 else 10
    asc = asc if asc else True
    offset = int(offset) if isinstance(offset, int) else 0
    # Calculate Result
    triangle = pascals_triangle(n=length - 1, weighted=True)
    pwma = close.rolling(length, min_periods=length).apply(weights(triangle),
                                                           raw=True)
    # Offset
    if offset != 0:
        pwma = pwma.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        pwma.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        pwma.fillna(method=kwargs["fill_method"], inplace=True)
    return pwma


def rma(close, length=None, offset=None, **kwargs):
    length = int(length) if length and length > 0 else 10
    offset = int(offset) if isinstance(offset, int) else 0
    alpha = (1.0 / length) if length > 0 else 0.5
    rma = close.ewm(alpha=alpha, min_periods=length).mean()
    # Offset
    if offset != 0:
        rma = rma.shift(offset)
    # Handle fills
    if "fillna" in kwargs:
        rma.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        rma.fillna(method=kwargs["fill_method"], inplace=True)
    return rma


def sma(close, length=None, offset=None, **kwargs):
    length = int(length) if length and length > 0 else 10
    min_periods = int(
        kwargs["min_periods"]) if "min_periods" in kwargs and kwargs[
            "min_periods"] is not None else length
    offset = int(offset) if isinstance(offset, int) else 0

    sma = close.rolling(length, min_periods=min_periods).mean()

    # Offset
    if offset != 0:
        sma = sma.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        sma.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        sma.fillna(method=kwargs["fill_method"], inplace=True)
    return sma


def ssf(close, length=None, poles=None, offset=None, **kwargs):
    length = int(length) if length and length > 0 else 10
    poles = int(poles) if poles in [2, 3] else 2
    offset = int(offset) if isinstance(offset, int) else 0

    m = close.shape[0]
    ssf = close.copy()

    if poles == 3:
        x = np.pi / length  # x = PI / n
        a0 = np.exp(-x)  # e^(-x)
        b0 = 2 * a0 * np.cos(np.sqrt(3) * x)  # 2e^(-x)*cos(3^(.5) * x)
        c0 = a0 * a0  # e^(-2x)

        c4 = c0 * c0  # e^(-4x)
        c3 = -c0 * (1 + b0)  # -e^(-2x) * (1 + 2e^(-x)*cos(3^(.5) * x))
        c2 = c0 + b0  # e^(-2x) + 2e^(-x)*cos(3^(.5) * x)
        c1 = 1 - c2 - c3 - c4

        for i in range(0, m):
            ssf.iloc[i] = c1 * close.iloc[i] + c2 * ssf.iloc[
                i - 1] + c3 * ssf.iloc[i - 2] + c4 * ssf.iloc[i - 3]

    else:  # poles == 2
        x = np.pi * np.sqrt(2) / length  # x = PI * 2^(.5) / n
        a0 = np.exp(-x)  # e^(-x)
        a1 = -a0 * a0  # -e^(-2x)
        b1 = 2 * a0 * np.cos(x)  # 2e^(-x)*cos(x)
        c1 = 1 - a1 - b1  # e^(-2x) - 2e^(-x)*cos(x) + 1

        for i in range(0, m):
            ssf.iloc[i] = c1 * close.iloc[i] + b1 * ssf.iloc[
                i - 1] + a1 * ssf.iloc[i - 2]
    # Offset
    if offset != 0:
        ssf = ssf.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        ssf.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        ssf.fillna(method=kwargs["fill_method"], inplace=True)
    return ssf


def swma(close, length=None, asc=None, offset=None, **kwargs):
    length = int(length) if length and length > 0 else 10
    asc = asc if asc else True
    offset = int(offset) if isinstance(offset, int) else 0

    # Calculate Result
    triangle = symmetric_triangle(length, weighted=True)
    swma = close.rolling(length, min_periods=length).apply(weights(triangle),
                                                           raw=True)
    # Offset
    if offset != 0:
        swma = swma.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        swma.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        swma.fillna(method=kwargs["fill_method"], inplace=True)
    return swma


def t3(close, length=None, a=None, offset=None, **kwargs):
    length = int(length) if length and length > 0 else 10
    a = float(a) if a and a > 0 and a < 1 else 0.7
    offset = int(offset) if isinstance(offset, int) else 0
    c1 = -a * a**2
    c2 = 3 * a**2 + 3 * a**3
    c3 = -6 * a**2 - 3 * a - 3 * a**3
    c4 = a**3 + 3 * a**2 + 3 * a + 1
    e1 = ema(close=close, length=length, **kwargs)
    e2 = ema(close=e1, length=length, **kwargs)
    e3 = ema(close=e2, length=length, **kwargs)
    e4 = ema(close=e3, length=length, **kwargs)
    e5 = ema(close=e4, length=length, **kwargs)
    e6 = ema(close=e5, length=length, **kwargs)
    t3 = c1 * e6 + c2 * e5 + c3 * e4 + c4 * e3
    # Offset
    if offset != 0:
        t3 = t3.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        t3.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        t3.fillna(method=kwargs["fill_method"], inplace=True)
    return t3


def tema(close, length=None, offset=None, **kwargs):
    length = int(length) if length and length > 0 else 10
    offset = int(offset) if isinstance(offset, int) else 0

    ema1 = ema(close=close, length=length, **kwargs)
    ema2 = ema(close=ema1, length=length, **kwargs)
    ema3 = ema(close=ema2, length=length, **kwargs)
    tema = 3 * (ema1 - ema2) + ema3

    # Offset
    if offset != 0:
        tema = tema.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        tema.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        tema.fillna(method=kwargs["fill_method"], inplace=True)
    return tema


def trima(close, length=None, offset=None, **kwargs):
    length = int(length) if length and length > 0 else 10
    offset = int(offset) if isinstance(offset, int) else 0
    half_length = round(0.5 * (length + 1))
    sma1 = sma(close, length=half_length)
    trima = sma(sma1, length=half_length)
    # Offset
    if offset != 0:
        trima = trima.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        trima.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        trima.fillna(method=kwargs["fill_method"], inplace=True)
    return trima


def vwma(close, volume, length=None, offset=None, **kwargs):
    length = int(length) if length and length > 0 else 10
    offset = int(offset) if isinstance(offset, int) else 0
    pv = close * volume
    vwma = sma(close=pv, length=length) / sma(close=volume, length=length)

    # Handle fills
    if "fillna" in kwargs:
        vwma.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        vwma.fillna(method=kwargs["fill_method"], inplace=True)
    return vwma


def wcp(high, low, close, offset=None, **kwargs):
    offset = int(offset) if isinstance(offset, int) else 0
    wcp = (high + low + 2 * close) / 4
    # Offset
    if offset != 0:
        wcp = wcp.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        wcp.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        wcp.fillna(method=kwargs["fill_method"], inplace=True)
    return wcp


def wma(close, length=None, asc=None, offset=None, **kwargs):
    length = int(length) if length and length > 0 else 10
    asc = asc if asc else True
    offset = int(offset) if isinstance(offset, int) else 0
    total_weight = 0.5 * length * (length + 1)
    weights_ = pd.Series(np.arange(1, length + 1))
    weights = weights_ if asc else weights_[::-1]

    def linear(w):

        def _compute(x):
            return np.dot(x, w) / total_weight

        return _compute

    close_ = close.rolling(length, min_periods=length)
    wma = close_.apply(linear(weights), raw=True)

    # Offset
    if offset != 0:
        wma = wma.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        wma.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        wma.fillna(method=kwargs["fill_method"], inplace=True)

    return wma
