# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
from hermes.factors.technical.core.utilities import *


def aberration(high,
               low,
               close,
               length=None,
               atr_length=None,
               offset=None,
               **kwargs):
    from hermes.factors.technical.core.overlap import hlc3, sma
    length = int(length) if length and length > 0 else 5
    atr_length = int(atr_length) if atr_length and atr_length > 0 else 15
    offset = int(offset) if isinstance(offset, int) else 0
    # Calculate Result
    atr_ = atr(high=high, low=low, close=close, length=atr_length)
    jg = hlc3(high=high, low=low, close=close)

    zg = sma(jg, length)
    sg = zg + atr_
    xg = zg - atr_

    # Offset
    if offset != 0:
        zg = zg.shift(offset)
        sg = sg.shift(offset)
        xg = xg.shift(offset)
        atr_ = atr_.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        zg.fillna(kwargs["fillna"], inplace=True)
        sg.fillna(kwargs["fillna"], inplace=True)
        xg.fillna(kwargs["fillna"], inplace=True)
        atr_.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        zg.fillna(method=kwargs["fill_method"], inplace=True)
        sg.fillna(method=kwargs["fill_method"], inplace=True)
        xg.fillna(method=kwargs["fill_method"], inplace=True)
        atr_.fillna(method=kwargs["fill_method"], inplace=True)

    return zg, sg, xg, atr_


def accbands(high,
             low,
             close,
             length=None,
             c=None,
             drift=None,
             offset=None,
             **kwargs):
    from hermes.factors.technical.core.overlap import sma
    length = int(length) if length and length > 0 else 20
    c = float(c) if c and c > 0 else 4
    drift = int(drift) if isinstance(drift, int) and drift != 0 else 1
    offset = int(offset) if isinstance(offset, int) else 0

    # Calculate Result
    high_low_range = non_zero_range(high, low)
    hl_ratio = high_low_range / (high + low)
    hl_ratio *= c
    _lower = low * (1 - hl_ratio)
    _upper = high * (1 + hl_ratio)

    lower = sma(_lower, length=length)
    mid = sma(close, length=length)
    upper = sma(_upper, length=length)

    # Offset
    if offset != 0:
        lower = lower.shift(offset)
        mid = mid.shift(offset)
        upper = upper.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        lower.fillna(kwargs["fillna"], inplace=True)
        mid.fillna(kwargs["fillna"], inplace=True)
        upper.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        lower.fillna(method=kwargs["fill_method"], inplace=True)
        mid.fillna(method=kwargs["fill_method"], inplace=True)
        upper.fillna(method=kwargs["fill_method"], inplace=True)
    return lower, mid, upper


def atr(high, low, close, length=None, drift=None, offset=None, **kwargs):
    from hermes.factors.technical.core.overlap import rma
    length = int(length) if length and length > 0 else 14
    drift = int(drift) if isinstance(drift, int) and drift != 0 else 1
    offset = int(offset) if isinstance(offset, int) else 0

    # Calculate Result
    tr = true_range(high=high, low=low, close=close, drift=drift)
    atr = rma(tr, length=length)
    percentage = kwargs.pop("percent", False)
    if percentage:
        atr *= 100 / close
    # Offset
    if offset != 0:
        atr = atr.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        atr.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        atr.fillna(method=kwargs["fill_method"], inplace=True)

    return atr


def bbands(close, length=None, std=None, ddof=0, offset=None, **kwargs):
    from hermes.factors.technical.core.statistics import stdev
    from hermes.factors.technical.core.overlap import sma
    length = int(length) if length and length > 0 else 5
    std = float(std) if std and std > 0 else 2.0
    ddof = int(ddof) if ddof >= 0 and ddof < length else 1
    offset = int(offset) if isinstance(offset, int) else 0

    standard_deviation = stdev(close=close, length=length, ddof=ddof)
    deviations = std * standard_deviation
    mid = sma(close, length=length, **kwargs)
    lower = mid - deviations
    upper = mid + deviations

    ulr = non_zero_range(upper, lower)
    bandwidth = 100 * ulr / mid
    percent = non_zero_range(close, lower) / ulr

    # Offset
    if offset != 0:
        lower = lower.shift(offset)
        mid = mid.shift(offset)
        upper = upper.shift(offset)
        bandwidth = bandwidth.shift(offset)
        percent = bandwidth.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        lower.fillna(kwargs["fillna"], inplace=True)
        mid.fillna(kwargs["fillna"], inplace=True)
        upper.fillna(kwargs["fillna"], inplace=True)
        bandwidth.fillna(kwargs["fillna"], inplace=True)
        percent.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        lower.fillna(method=kwargs["fill_method"], inplace=True)
        mid.fillna(method=kwargs["fill_method"], inplace=True)
        upper.fillna(method=kwargs["fill_method"], inplace=True)
        bandwidth.fillna(method=kwargs["fill_method"], inplace=True)
        percent.fillna(method=kwargs["fill_method"], inplace=True)
    return lower, mid, upper, bandwidth, percent


def donchian(high,
             low,
             lower_length=None,
             upper_length=None,
             offset=None,
             **kwargs):
    lower_length = int(
        lower_length) if lower_length and lower_length > 0 else 20
    upper_length = int(
        upper_length) if upper_length and upper_length > 0 else 20
    lower_min_periods = int(
        kwargs["lower_min_periods"]
    ) if "lower_min_periods" in kwargs and kwargs[
        "lower_min_periods"] is not None else lower_length
    upper_min_periods = int(
        kwargs["upper_min_periods"]
    ) if "upper_min_periods" in kwargs and kwargs[
        "upper_min_periods"] is not None else upper_length
    offset = int(offset) if isinstance(offset, int) else 0

    # Calculate Result
    lower = low.rolling(lower_length, min_periods=lower_min_periods).min()
    upper = high.rolling(upper_length, min_periods=upper_min_periods).max()
    mid = 0.5 * (lower + upper)

    # Handle fills
    if "fillna" in kwargs:
        lower.fillna(kwargs["fillna"], inplace=True)
        mid.fillna(kwargs["fillna"], inplace=True)
        upper.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        lower.fillna(method=kwargs["fill_method"], inplace=True)
        mid.fillna(method=kwargs["fill_method"], inplace=True)
        upper.fillna(method=kwargs["fill_method"], inplace=True)

    # Offset
    if offset != 0:
        lower = lower.shift(offset)
        mid = mid.shift(offset)
        upper = upper.shift(offset)
    return lower, mid, upper


def kc(high, low, close, length=None, scalar=None, offset=None, **kwargs):
    from hermes.factors.technical.core.overlap import ema
    length = int(length) if length and length > 0 else 20
    scalar = float(scalar) if scalar and scalar > 0 else 2

    offset = int(offset) if isinstance(offset, int) else 0

    use_tr = kwargs.pop("tr", False)
    if use_tr:
        range_ = true_range(high, low, close)
    else:
        range_ = non_zero_range(high, low)

    basis = ema(close, length=length)
    band = ema(range_, length=length)

    lower = basis - scalar * band
    upper = basis + scalar * band

    # Offset
    if offset != 0:
        lower = lower.shift(offset)
        basis = basis.shift(offset)
        upper = upper.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        lower.fillna(kwargs["fillna"], inplace=True)
        basis.fillna(kwargs["fillna"], inplace=True)
        upper.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        lower.fillna(method=kwargs["fill_method"], inplace=True)
        basis.fillna(method=kwargs["fill_method"], inplace=True)
        upper.fillna(method=kwargs["fill_method"], inplace=True)
    return lower, basis, upper


def massi(high, low, fast=None, slow=None, offset=None, **kwargs):
    from hermes.factors.technical.core.overlap import ema
    # Validate arguments
    fast = int(fast) if fast and fast > 0 else 9
    slow = int(slow) if slow and slow > 0 else 25
    if slow < fast:
        fast, slow = slow, fast

    offset = int(offset) if isinstance(offset, int) else 0

    # Calculate Result
    high_low_range = non_zero_range(high, low)
    hl_ema1 = ema(close=high_low_range, length=fast, **kwargs)
    hl_ema2 = ema(close=hl_ema1, length=fast, **kwargs)

    hl_ratio = hl_ema1 / hl_ema2
    massi = hl_ratio.rolling(slow, min_periods=slow).sum()

    # Offset
    if offset != 0:
        massi = massi.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        massi.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        massi.fillna(method=kwargs["fill_method"], inplace=True)
    return massi


def natr(high,
         low,
         close,
         length=None,
         scalar=None,
         drift=None,
         offset=None,
         **kwargs):
    length = int(length) if length and length > 0 else 14
    scalar = float(scalar) if scalar else 100
    drift = int(drift) if isinstance(drift, int) and drift != 0 else 1
    offset = int(offset) if isinstance(offset, int) else 0

    natr = scalar / close
    natr *= atr(high=high,
                low=low,
                close=close,
                length=length,
                drift=drift,
                offset=offset,
                **kwargs)
    # Offset
    if offset != 0:
        natr = natr.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        natr.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        natr.fillna(method=kwargs["fill_method"], inplace=True)
    return natr


def pdist(open, high, low, close, drift=None, offset=None, **kwargs):
    drift = int(drift) if isinstance(drift, int) and drift != 0 else 1
    offset = int(offset) if isinstance(offset, int) else 0

    # Calculate Result
    pdist = 2 * non_zero_range(high, low)
    pdist += non_zero_range(open, close.shift(drift)).abs()
    pdist -= non_zero_range(close, open).abs()

    # Offset
    if offset != 0:
        pdist = pdist.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        pdist.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        pdist.fillna(method=kwargs["fill_method"], inplace=True)
    return pdist


def rvi(close,
        high=None,
        low=None,
        length=None,
        scalar=None,
        refined=None,
        thirds=None,
        drift=None,
        offset=None,
        **kwargs):
    from hermes.factors.technical.core.statistics import stdev
    from hermes.factors.technical.core.overlap import ema
    length = int(length) if length and length > 0 else 14
    scalar = float(scalar) if scalar and scalar > 0 else 100
    refined = False if refined is None else refined
    thirds = False if thirds is None else thirds
    drift = int(drift) if isinstance(drift, int) and drift != 0 else 1
    offset = int(offset) if isinstance(offset, int) else 0

    # Calculate Result
    def _rvi(source, length, scalar, drift):
        """RVI"""
        std = stdev(source, length)
        pos, neg = unsigned_differences(source, amount=drift)

        pos_std = pos * std
        neg_std = neg * std

        pos_avg = ema(pos_std, length=length)
        neg_avg = ema(neg_std, length=length)

        result = scalar * pos_avg
        result /= pos_avg + neg_avg
        return result

    _mode = ""
    if refined:
        high_rvi = _rvi(high, length, scalar, drift)
        low_rvi = _rvi(low, length, scalar, drift)
        rvi = 0.5 * (high_rvi + low_rvi)
        _mode = "r"
    elif thirds:
        high_rvi = _rvi(high, length, scalar, drift)
        low_rvi = _rvi(low, length, scalar, drift)
        close_rvi = _rvi(close, length, scalar, drift)
        rvi = (high_rvi + low_rvi + close_rvi) / 3.0
        _mode = "t"
    else:
        rvi = _rvi(close, length, scalar, drift)

    # Offset
    if offset != 0:
        rvi = rvi.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        rvi.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        rvi.fillna(method=kwargs["fill_method"], inplace=True)
    return rvi


def thermo(high,
           low,
           length=None,
           long=None,
           short=None,
           drift=None,
           offset=None,
           **kwargs):
    from hermes.factors.technical.core.overlap import ema
    # Validate arguments
    length = int(length) if length and length > 0 else 20
    long = float(long) if long and long > 0 else 2
    short = float(short) if short and short > 0 else 0.5

    drift = int(drift) if isinstance(drift, int) and drift != 0 else 1
    offset = int(offset) if isinstance(offset, int) else 0

    asint = kwargs.pop("asint", True)

    # Calculate Result
    thermoL = (low.shift(drift) - low).abs()
    thermoH = (high - high.shift(drift)).abs()

    thermo = thermoL
    thermo = thermo.where(thermoH < thermoL, thermoH)
    thermo.index = high.index

    thermo_ma = ema(thermo, length=length)
    # Create signals
    thermo_long = thermo < (thermo_ma * long)
    thermo_short = thermo > (thermo_ma * short)

    # Binary output, useful for signals
    if asint:
        thermo_long = thermo_long.astype(int)
        thermo_short = thermo_short.astype(int)

    # Offset
    if offset != 0:
        thermo = thermo.shift(offset)
        thermo_ma = thermo_ma.shift(offset)
        thermo_long = thermo_long.shift(offset)
        thermo_short = thermo_short.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        thermo.fillna(kwargs["fillna"], inplace=True)
        thermo_ma.fillna(kwargs["fillna"], inplace=True)
        thermo_long.fillna(kwargs["fillna"], inplace=True)
        thermo_short.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        thermo.fillna(method=kwargs["fill_method"], inplace=True)
        thermo_ma.fillna(method=kwargs["fill_method"], inplace=True)
        thermo_long.fillna(method=kwargs["fill_method"], inplace=True)
        thermo_short.fillna(method=kwargs["fill_method"], inplace=True)
    return thermo, thermo_ma, thermo_long, thermo_short


def true_range(high, low, close, drift=None, offset=None, **kwargs):
    drift = int(drift) if isinstance(drift, int) and drift != 0 else 1
    offset = int(offset) if isinstance(offset, int) else 0
    high_low_range = non_zero_range(high, low)
    prev_close = close.shift(drift)
    true_range = high_low_range.copy()
    true_range[true_range < high - prev_close] = high - prev_close
    true_range[true_range < prev_close - low] = prev_close - low
    true_range.iloc[:drift] = np.nan
    # Offset
    if offset != 0:
        true_range = true_range.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        true_range.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        true_range.fillna(method=kwargs["fill_method"], inplace=True)
    return true_range


def ui(close, length=None, scalar=None, offset=None, **kwargs):
    from hermes.factors.technical.core.overlap import sma
    length = int(length) if length and length > 0 else 14
    scalar = float(scalar) if scalar and scalar > 0 else 100
    offset = int(offset) if isinstance(offset, int) else 0

    # Calculate Result
    highest_close = close.rolling(length).max()
    downside = scalar * (close - highest_close)
    downside /= highest_close
    d2 = downside * downside

    everget = kwargs.pop("everget", False)
    if everget:
        # Everget uses SMA instead of SUM for calculation
        ui = (sma(d2, length) / length).apply(np.sqrt)
    else:
        ui = (d2.rolling(length).sum() / length).apply(np.sqrt)

    # Offset
    if offset != 0:
        ui = ui.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        ui.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        ui.fillna(method=kwargs["fill_method"], inplace=True)
    return ui