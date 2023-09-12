# -*- encoding:utf-8 -*-
import numpy as np
import pandas as pd
from hermes.factors.technical.core.utilities import *


def ad(high, low, close, volume, open=None, offset=None, **kwargs):
    offset = int(offset) if isinstance(offset, int) else 0
    if open is not None:
        ad = non_zero_range(close, open)  # AD with Open
    else:
        ad = 2 * close - (high + low)  # AD with High, Low, Close

    high_low_range = non_zero_range(high, low)
    ad *= volume / high_low_range
    ad = ad.cumsum()
    # Offset
    if offset != 0:
        ad = ad.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        ad.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        ad.fillna(method=kwargs["fill_method"], inplace=True)
    return ad


def adosc(high,
          low,
          close,
          volume,
          open=None,
          fast=None,
          slow=None,
          offset=None,
          **kwargs):
    from hermes.factors.technical.core.overlap import ema
    fast = int(fast) if fast and fast > 0 else 3
    slow = int(slow) if slow and slow > 0 else 10
    offset = int(offset) if isinstance(offset, int) else 0
    if "length" in kwargs: kwargs.pop("length")
    ad_ = ad(high=high, low=low, close=close, volume=volume, open=open)
    fast_ad = ema(close=ad_, length=fast, **kwargs)
    slow_ad = ema(close=ad_, length=slow, **kwargs)
    adosc = fast_ad - slow_ad
    # Offset
    if offset != 0:
        adosc = adosc.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        adosc.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        adosc.fillna(method=kwargs["fill_method"], inplace=True)
    return adosc


def aobv(close,
         volume,
         fast=None,
         slow=None,
         max_lookback=None,
         min_lookback=None,
         offset=None,
         **kwargs):
    from hermes.factors.technical.core.overlap import ema
    from hermes.factors.technical.core.trend import long_run, short_run
    # Validate arguments
    fast = int(fast) if fast and fast > 0 else 4
    slow = int(slow) if slow and slow > 0 else 12
    max_lookback = int(
        max_lookback) if max_lookback and max_lookback > 0 else 2
    min_lookback = int(
        min_lookback) if min_lookback and min_lookback > 0 else 2
    if slow < fast:
        fast, slow = slow, fast
    offset = int(offset) if isinstance(offset, int) else 0
    if "length" in kwargs: kwargs.pop("length")
    run_length = kwargs.pop("run_length", 2)

    obv_ = obv(close=close, volume=volume, **kwargs)
    maf = ema(obv_, length=fast, **kwargs)
    mas = ema(obv_, length=slow, **kwargs)

    # When MAs are long and short
    obv_long = long_run(maf, mas, length=run_length)
    obv_short = short_run(maf, mas, length=run_length)

    # Offset
    if offset != 0:
        obv_ = obv_.shift(offset)
        maf = maf.shift(offset)
        mas = mas.shift(offset)
        obv_long = obv_long.shift(offset)
        obv_short = obv_short.shift(offset)

    # # Handle fills
    if "fillna" in kwargs:
        obv_.fillna(kwargs["fillna"], inplace=True)
        maf.fillna(kwargs["fillna"], inplace=True)
        mas.fillna(kwargs["fillna"], inplace=True)
        obv_long.fillna(kwargs["fillna"], inplace=True)
        obv_short.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        obv_.fillna(method=kwargs["fill_method"], inplace=True)
        maf.fillna(method=kwargs["fill_method"], inplace=True)
        mas.fillna(method=kwargs["fill_method"], inplace=True)
        obv_long.fillna(method=kwargs["fill_method"], inplace=True)
        obv_short.fillna(method=kwargs["fill_method"], inplace=True)
    return obv_, maf, mas, obv_long, obv_short


def cmf(high,
        low,
        close,
        volume,
        open=None,
        length=None,
        offset=None,
        **kwargs):
    length = int(length) if length and length > 0 else 20
    min_periods = int(
        kwargs["min_periods"]) if "min_periods" in kwargs and kwargs[
            "min_periods"] is not None else length
    offset = int(offset) if isinstance(offset, int) else 0

    # Calculate Result
    if open is not None:
        ad = non_zero_range(close, open)  # AD with Open
    else:
        ad = 2 * close - (high + low)  # AD with High, Low, Close

    ad *= volume / non_zero_range(high, low)
    cmf = ad.rolling(length, min_periods=min_periods).sum()
    cmf /= volume.rolling(length, min_periods=min_periods).sum()

    # Offset
    if offset != 0:
        cmf = cmf.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        cmf.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        cmf.fillna(method=kwargs["fill_method"], inplace=True)
    return cmf


def efi(close, volume, length=None, drift=None, offset=None, **kwargs):
    from hermes.factors.technical.core.overlap import ema
    length = int(length) if length and length > 0 else 13
    drift = int(drift) if isinstance(drift, int) and drift != 0 else 1
    offset = int(offset) if isinstance(offset, int) else 0

    # Calculate Result
    pv_diff = close.diff(drift) * volume
    efi = ema(pv_diff, length=length)

    # Offset
    if offset != 0:
        efi = efi.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        efi.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        efi.fillna(method=kwargs["fill_method"], inplace=True)
    return efi


def eom(high,
        low,
        volume,
        length=None,
        divisor=None,
        drift=None,
        offset=None,
        **kwargs):
    from hermes.factors.technical.core.overlap import hl2, sma
    length = int(length) if length and length > 0 else 14
    divisor = divisor if divisor and divisor > 0 else 100000000
    drift = int(drift) if isinstance(drift, int) and drift != 0 else 1
    offset = int(offset) if isinstance(offset, int) else 0

    # Calculate Result
    high_low_range = non_zero_range(high, low)
    distance = hl2(high=high, low=low)
    distance -= hl2(high=high.shift(drift), low=low.shift(drift))
    box_ratio = volume / divisor
    box_ratio /= high_low_range
    eom = distance / box_ratio
    eom = sma(eom, length=length)

    # Offset
    if offset != 0:
        eom = eom.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        eom.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        eom.fillna(method=kwargs["fill_method"], inplace=True)
    return eom


def kvo(high,
        low,
        close,
        volume,
        fast=None,
        slow=None,
        signal=None,
        drift=None,
        offset=None,
        **kwargs):
    from hermes.factors.technical.core.overlap import hlc3, ema
    # Validate arguments
    fast = int(fast) if fast and fast > 0 else 34
    slow = int(slow) if slow and slow > 0 else 55
    signal = int(signal) if signal and signal > 0 else 13
    drift = int(drift) if isinstance(drift, int) and drift != 0 else 1
    offset = int(offset) if isinstance(offset, int) else 0

    # Calculate Result
    signed_volume = volume * signed_series(hlc3(high, low, close), 1)
    sv = signed_volume.loc[signed_volume.first_valid_index():, ]
    kvo = ema(sv, length=fast) - ema(sv, length=slow)
    kvo_signal = ema(kvo.loc[kvo.first_valid_index():, ], length=signal)

    # Offset
    if offset != 0:
        kvo = kvo.shift(offset)
        kvo_signal = kvo_signal.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        kvo.fillna(kwargs["fillna"], inplace=True)
        kvo_signal.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        kvo.fillna(method=kwargs["fill_method"], inplace=True)
        kvo_signal.fillna(method=kwargs["fill_method"], inplace=True)
    return kvo, kvo_signal


def linratio(long, length=None, offset=None, **kwargs):
    length = int(length) if length and length > 0 else 5
    offset = int(offset) if isinstance(offset, int) else 0

    longinratio = long / long.shift(length) - 1

    # Offset
    if offset != 0:
        longinratio = longinratio.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        longinratio.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        longinratio.fillna(method=kwargs["fill_method"], inplace=True)
    return longinratio


def lrtichg(long, openint, length=None, offset=None, **kwargs):
    length = int(length) if length and length > 0 else 5
    offset = int(offset) if isinstance(offset, int) else 0

    lrtichg = (long / openint - long.shift(length) / openint.shift(length)) / (
        long.shift(length) / openint.shift(length))

    # Offset
    if offset != 0:
        lrtichg = lrtichg.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        lrtichg.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        lrtichg.fillna(method=kwargs["fill_method"], inplace=True)
    return lrtichg


def lssenti(long, short, openint, length=None, offset=None, **kwargs):
    length = int(length) if length and length > 0 else 5
    offset = int(offset) if isinstance(offset, int) else 0

    lssenti = (long - short) / openint

    # Offset
    if offset != 0:
        lssenti = lssenti.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        lssenti.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        lssenti.fillna(method=kwargs["fill_method"], inplace=True)
    return lssenti


def nic(long, short, length=None, offset=None, **kwargs):
    length = int(length) if length and length > 0 else 5
    offset = int(offset) if isinstance(offset, int) else 0

    nic = (long - short) / (long.shift(length) - short.shift(length)) - 1

    # Offset
    if offset != 0:
        nic = nic.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        nic.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        nic.fillna(method=kwargs["fill_method"], inplace=True)
    return nic


def nitc(long, short, openint, length=None, offset=None, **kwargs):
    length = int(length) if length and length > 0 else 5
    offset = int(offset) if isinstance(offset, int) else 0

    nitc = (long - short) / openint - (long.shift(length) -
                                       short.shift(length)) / openint

    # Offset
    if offset != 0:
        nitc = nic.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        nitc.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        nitc.fillna(method=kwargs["fill_method"], inplace=True)
    return nitc


def nir(long, short, length=None, offset=None, **kwargs):
    length = int(length) if length and length > 0 else 5
    offset = int(offset) if isinstance(offset, int) else 0

    nir = (long - short) / (long + short)

    # Offset
    if offset != 0:
        nir = nic.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        nir.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        nir.fillna(method=kwargs["fill_method"], inplace=True)
    return nir


def nvi(close, volume, length=None, initial=None, offset=None, **kwargs):
    from hermes.factors.technical.core.momentum import roc
    length = int(length) if length and length > 0 else 1
    # min_periods = int(kwargs["min_periods"]) if "min_periods" in kwargs and kwargs["min_periods"] is not None else length
    initial = int(initial) if initial and initial > 0 else 1000
    offset = int(offset) if isinstance(offset, int) else 0

    if close is None or volume is None: return

    # Calculate Result
    roc_ = roc(close=close, length=length)
    signed_volume = signed_series(volume, 1)
    nvi = signed_volume[signed_volume < 0].abs() * roc_
    nvi.fillna(0, inplace=True)
    nvi.iloc[0] = initial
    nvi = nvi.cumsum()

    # Offset
    if offset != 0:
        nvi = nvi.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        nvi.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        nvi.fillna(method=kwargs["fill_method"], inplace=True)
    return nvi


def obv(close, volume, offset=None, **kwargs):
    offset = int(offset) if isinstance(offset, int) else 0

    # Calculate Result
    sign = close.diff(1)
    sign[sign > 0] = 1
    sign[sign < 0] = -1
    sign.iloc[0] = 1

    signed_volume = sign * volume
    obv = signed_volume.cumsum()

    # Offset
    if offset != 0:
        obv = obv.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        obv.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        obv.fillna(method=kwargs["fill_method"], inplace=True)
    return obv


def pvi(close, volume, length=None, initial=None, offset=None, **kwargs):
    from hermes.factors.technical.core.momentum import roc
    length = int(length) if length and length > 0 else 1
    # min_periods = int(kwargs["min_periods"]) if "min_periods" in kwargs and kwargs["min_periods"] is not None else length
    initial = int(initial) if initial and initial > 0 else 1000

    offset = int(offset) if isinstance(offset, int) else 0

    # Calculate Result
    signed_volume = signed_series(volume, 1)
    pvi = roc(close=close,
              length=length) * signed_volume[signed_volume > 0].abs()
    pvi.fillna(0, inplace=True)
    pvi.iloc[0] = initial
    pvi = pvi.cumsum()

    # Offset
    if offset != 0:
        pvi = pvi.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        pvi.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        pvi.fillna(method=kwargs["fill_method"], inplace=True)
    return pvi


def pvol(close, volume, offset=None, **kwargs):
    # Validate arguments
    offset = int(offset) if isinstance(offset, int) else 0
    signed = kwargs.pop("signed", False)

    # Calculate Result
    pvol = close * volume
    if signed:
        pvol *= signed_series(close, 1)

    # Offset
    if offset != 0:
        pvol = pvol.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        pvol.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        pvol.fillna(method=kwargs["fill_method"], inplace=True)
    return pvol


def pvt(close, volume, drift=None, offset=None, **kwargs):
    from hermes.factors.technical.core.momentum import roc
    drift = int(drift) if isinstance(drift, int) and drift != 0 else 1
    offset = int(offset) if isinstance(offset, int) else 0

    # Calculate Result
    pv = roc(close=close, length=drift) * volume
    pvt = pv.cumsum()

    # Offset
    if offset != 0:
        pvt = pvt.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        pvt.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        pvt.fillna(method=kwargs["fill_method"], inplace=True)
    return pvt


def sinratio(short, length=None, offset=None, **kwargs):
    length = int(length) if length and length > 0 else 5
    offset = int(offset) if isinstance(offset, int) else 0

    sinratio = short / short.shift(length) - 1

    # Offset
    if offset != 0:
        sinratio = sinratio.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        sinratio.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        sinratio.fillna(method=kwargs["fill_method"], inplace=True)
    return sinratio


def srtichg(short, openint, length=None, offset=None, **kwargs):
    length = int(length) if length and length > 0 else 5
    offset = int(offset) if isinstance(offset, int) else 0

    srtichg = (short.shift(length) / openint.shift(length) -
               short / openint) / (short.shift(length) / openint.shift(length))

    # Offset
    if offset != 0:
        srtichg = srtichg.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        srtichg.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        srtichg.fillna(method=kwargs["fill_method"], inplace=True)
    return srtichg