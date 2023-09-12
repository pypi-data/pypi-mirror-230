# -*- encoding:utf-8 -*-
import numpy as np
import pandas as pd
from hermes.factors.technical.core.utilities import *


def annealn(high, low, close, length=None, offset=None, **kwargs):
    length = int(length) if length and length > 0 else 14
    offset = int(offset) if isinstance(offset, int) else 0
    high_low_range = high - low
    high_close_range = (high - close.shift()).abs()
    low_close_range = (low - close.shift()).abs()
    cond1 = high_low_range > high_close_range
    high_close_range[cond1] = high_low_range[cond1]
    cond2 = high_close_range > low_close_range
    low_close_range[cond2] = high_close_range[cond2]
    tr = low_close_range
    atr = tr.rolling(length).mean()
    ret = close - close.shift(length) + 0.00001
    atr_adj = 2 * ret / (atr + atr.shift(length))
    # Offset
    if offset != 0:
        atr_adj = atr_adj.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        atr_adj.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        atr_adj.fillna(method=kwargs["fill_method"], inplace=True)

    return atr_adj


def ao(high, low, fast=None, slow=None, offset=None, **kwargs):
    from hermes.factors.technical.core.overlap import sma
    fast = int(fast) if fast and fast > 0 else 5
    slow = int(slow) if slow and slow > 0 else 34
    if slow < fast:
        fast, slow = slow, fast

    offset = int(offset) if isinstance(offset, int) else 0
    # Calculate Result
    median_price = 0.5 * (high + low)
    fast_sma = sma(median_price, fast)
    slow_sma = sma(median_price, slow)
    ao = fast_sma - slow_sma

    # Offset
    if offset != 0:
        ao = ao.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        ao.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        ao.fillna(method=kwargs["fill_method"], inplace=True)

    return ao


def apo(close, fast=None, slow=None, offset=None, **kwargs):
    from hermes.factors.technical.core.overlap import sma
    fast = int(fast) if fast and fast > 0 else 12
    slow = int(slow) if slow and slow > 0 else 26
    if slow < fast:
        fast, slow = slow, fast

    offset = int(offset) if isinstance(offset, int) else 0
    fastma = sma(close, length=fast, **kwargs)
    slowma = sma(close, length=slow, **kwargs)
    apo = fastma - slowma
    # Offset
    if offset != 0:
        apo = apo.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        apo.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        apo.fillna(method=kwargs["fill_method"], inplace=True)

    return apo


def bias(close, length=None, offset=None, **kwargs):
    from hermes.factors.technical.core.overlap import sma
    length = int(length) if length and length > 0 else 26
    offset = int(offset) if isinstance(offset, int) else 0
    # Calculate Result
    bma = sma(close, length=length, **kwargs)
    bias = (close / bma) - 1

    # Offset
    if offset != 0:
        bias = bias.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        bias.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        bias.fillna(method=kwargs["fill_method"], inplace=True)
    return bias


def bop(open, high, low, close, scalar=None, offset=None, **kwargs):
    scalar = float(scalar) if scalar else 1
    offset = int(offset) if isinstance(offset, int) else 0
    high_low_range = non_zero_range(high, low)
    close_open_range = non_zero_range(close, open)
    bop = scalar * close_open_range / high_low_range
    # Offset
    if offset != 0:
        bop = bop.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        bop.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        bop.fillna(method=kwargs["fill_method"], inplace=True)
    return bop


def brar(open,
         high,
         low,
         close,
         length=None,
         scalar=None,
         drift=None,
         offset=None,
         **kwargs):
    length = int(length) if length and length > 0 else 26
    scalar = float(scalar) if scalar else 100
    high_open_range = non_zero_range(high, open)
    open_low_range = non_zero_range(open, low)
    drift = int(drift) if isinstance(drift, int) and drift != 0 else 1
    offset = int(offset) if isinstance(offset, int) else 0
    # Calculate Result
    hcy = non_zero_range(high, close.shift(drift))
    cyl = non_zero_range(close.shift(drift), low)
    hcy[hcy < 0] = 0  # Zero negative values
    cyl[cyl < 0] = 0  # ""

    ar = scalar * high_open_range.rolling(length).sum()
    ar /= open_low_range.rolling(length).sum()

    br = scalar * hcy.rolling(length).sum()
    br /= cyl.rolling(length).sum()
    # Offset
    if offset != 0:
        ar = ar.shift(offset)
        br = ar.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        ar.fillna(kwargs["fillna"], inplace=True)
        br.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        ar.fillna(method=kwargs["fill_method"], inplace=True)
        br.fillna(method=kwargs["fill_method"], inplace=True)
    return ar, br


def chkbar(close, high, length=None, offset=None, **kwargs):
    length = int(length) if length and length > 0 else 5
    offset = int(offset) if isinstance(offset, int) else 0

    chkbar = ((close - high) / high).rolling(length).mean()

    # Offset
    if offset != 0:
        chkbar = chkbar.shift(offset)\

    # Handle fills
    if "fillna" in kwargs:
        chkbar.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        chkbar.fillna(method=kwargs["fill_method"], inplace=True)
    return chkbar


def clkbar(close, low, length=None, offset=None, **kwargs):
    length = int(length) if length and length > 0 else 5
    offset = int(offset) if isinstance(offset, int) else 0

    clkbar = ((close - low) / low).rolling(length).mean()

    # Offset
    if offset != 0:
        clkbar = clkbar.shift(offset)\

    # Handle fills
    if "fillna" in kwargs:
        clkbar.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        clkbar.fillna(method=kwargs["fill_method"], inplace=True)
    return clkbar


def cci(high, low, close, length=None, c=None, offset=None, **kwargs):
    from hermes.factors.technical.core.overlap import sma, hlc3
    from hermes.factors.technical.core.statistics import mad
    length = int(length) if length and length > 0 else 14
    c = float(c) if c and c > 0 else 0.015
    offset = int(offset) if isinstance(offset, int) else 0
    typical_price = hlc3(high=high, low=low, close=close)
    mean_typical_price = sma(typical_price, length=length)
    mad_typical_price = mad(typical_price, length=length)

    cci = typical_price - mean_typical_price
    cci /= c * mad_typical_price
    # Offset
    if offset != 0:
        cci = cci.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        cci.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        cci.fillna(method=kwargs["fill_method"], inplace=True)
    return cci


def cg(close, length=None, offset=None, **kwargs):
    length = int(length) if length and length > 0 else 10
    offset = int(offset) if isinstance(offset, int) else 0

    # Calculate Result
    coefficients = [length - i for i in range(0, length)]
    numerator = -close.rolling(length).apply(weights(coefficients), raw=True)
    cg = numerator / close.rolling(length).sum()

    # Offset
    if offset != 0:
        cg = cg.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        cg.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        cg.fillna(method=kwargs["fill_method"], inplace=True)
    return cg


def cmo(close, length=None, scalar=None, drift=None, offset=None, **kwargs):
    length = int(length) if length and length > 0 else 14
    scalar = float(scalar) if scalar else 100
    drift = int(drift) if isinstance(drift, int) and drift != 0 else 1
    offset = int(offset) if isinstance(offset, int) else 0

    mom = close.diff(drift)
    positive = mom.copy().clip(lower=0)
    negative = mom.copy().clip(upper=0).abs()
    pos_ = positive.rolling(length).sum()
    neg_ = negative.rolling(length).sum()
    cmo = scalar * (pos_ - neg_) / (pos_ + neg_)
    # Offset
    if offset != 0:
        cmo = cmo.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        cmo.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        cmo.fillna(method=kwargs["fill_method"], inplace=True)
    return cmo


def coppock(close, length=None, fast=None, slow=None, offset=None, **kwargs):
    from hermes.factors.technical.core.overlap import wma
    length = int(length) if length and length > 0 else 10
    fast = int(fast) if fast and fast > 0 else 11
    slow = int(slow) if slow and slow > 0 else 14
    offset = int(offset) if isinstance(offset, int) else 0

    # Calculate Result
    total_roc = roc(close, fast) + roc(close, slow)
    coppock = wma(total_roc, length)

    # Offset
    if offset != 0:
        coppock = coppock.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        coppock.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        coppock.fillna(method=kwargs["fill_method"], inplace=True)
    return coppock


def dnclvolatility(close, low, length=None, offset=None, **kwargs):
    length = int(length) if length and length > 0 else 5
    offset = int(offset) if isinstance(offset, int) else 0

    pre_close = close.shift(1)

    dnclvolatility = ((low - pre_close) / pre_close).rolling(length).mean()

    # Offset
    if offset != 0:
        dnclvolatility = dnclvolatility.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        dnclvolatility.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        dnclvolatility.fillna(method=kwargs["fill_method"], inplace=True)
    return dnclvolatility


def dnllvolatility(low, length=None, offset=None, **kwargs):
    length = int(length) if length and length > 0 else 5
    offset = int(offset) if isinstance(offset, int) else 0

    pre_low = low.shift(1)

    dnllvolatility = ((low - pre_low) / pre_low).rolling(length).mean()

    # Offset
    if offset != 0:
        dnllvolatility = dnllvolatility.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        dnllvolatility.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        dnllvolatility.fillna(method=kwargs["fill_method"], inplace=True)
    return dnllvolatility


def dm(high, low, length=None, drift=None, offset=None, **kwargs):
    from hermes.factors.technical.core.overlap import rma
    length = int(length) if length and length > 0 else 14
    drift = int(drift) if isinstance(drift, int) and drift != 0 else 1
    offset = int(offset) if isinstance(offset, int) else 0
    up = high - high.shift(drift)
    dn = low.shift(drift) - low

    pos_ = ((up > dn) & (up > 0)) * up
    neg_ = ((dn > up) & (dn > 0)) * dn
    pos_[pos_.abs() < sflt.epsilon] = 0
    neg_[neg_.abs() < sflt.epsilon] = 0

    # Not the same values as TA Lib's -+DM (Good First Issue)
    pos = rma(pos_, length=length)
    neg = rma(neg_, length=length)
    # Offset
    if offset != 0:
        pos = pos.shift(offset)
        neg = neg.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        pos.fillna(kwargs["fillna"], inplace=True)
        neg.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        pos.fillna(method=kwargs["fill_method"], inplace=True)
        neg.fillna(method=kwargs["fill_method"], inplace=True)
    return pos, neg


def dnintraday(open, low, length=None, **kwargs):
    length = int(length) if length and length > 0 else 10
    offset = int(offset) if isinstance(offset, int) else 0

    dnintraday = ((low - open) / open).rolling(length).mean()

    # Offset
    if offset != 0:
        er = er.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        dnintraday.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        dnintraday.fillna(method=kwargs["fill_method"], inplace=True)
    return dnintraday


def er(close, length=None, drift=None, offset=None, **kwargs):
    length = int(length) if length and length > 0 else 10
    drift = int(drift) if isinstance(drift, int) and drift != 0 else 1
    offset = int(offset) if isinstance(offset, int) else 0
    # Calculate Result
    abs_diff = close.diff(length).abs()
    abs_volatility = close.diff(drift).abs()

    er = abs_diff
    er /= abs_volatility.rolling(window=length).sum()

    # Offset
    if offset != 0:
        er = er.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        er.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        er.fillna(method=kwargs["fill_method"], inplace=True)
    return er


def eri(high, low, close, length=None, offset=None, **kwargs):
    from hermes.factors.technical.core.overlap import ema
    length = int(length) if length and length > 0 else 13
    offset = int(offset) if isinstance(offset, int) else 0
    # Calculate Result
    ema_ = ema(close, length)
    bull = high - ema_
    bear = low - ema_

    # Offset
    if offset != 0:
        bull = bull.shift(offset)
        bear = bear.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        bull.fillna(kwargs["fillna"], inplace=True)
        bear.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        bull.fillna(method=kwargs["fill_method"], inplace=True)
        bear.fillna(method=kwargs["fill_method"], inplace=True)
    return bull, bear


def effratio(close, length=None, offset=None, **kwargs):
    length = int(length) if length and length > 0 else 14
    offset = int(offset) if isinstance(offset, int) else 0

    net_chg = close - close.shift(length)

    for i in range(length):
        net_chg.iloc[i] = close.iloc[i] - close.iloc[0]

    temp_chg = abs(close - close.shift(1))
    temp_chg.iloc[0] = temp_chg.iloc[1]

    tot_chg = temp_chg.rolling(length).sum()
    for i in range(length):
        if i == 0:
            tot_chg.iloc[i] = 0
        else:
            tot_chg.iloc[i] = temp_chg.iloc[:i + 1].sum() + (
                length - i - 1) * temp_chg.iloc[0]

    effratio = net_chg / tot_chg

    # Offset
    if offset != 0:
        effratio = effratio.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        effratio.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        effratio.fillna(method=kwargs["fill_method"], inplace=True)
    return effratio


def intraday(open, close, length=None, offset=None, **kwargs):
    length = int(length) if length and length > 0 else 5
    offset = int(offset) if isinstance(offset, int) else 0
    intraday = ((close - open) / open).rolling(length).mean()

    # Offset
    if offset != 0:
        intraday = intraday.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        intraday.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        intraday.fillna(method=kwargs["fill_method"], inplace=True)
    return intraday


def kdj(high=None,
        low=None,
        close=None,
        length=None,
        signal=None,
        offset=None,
        **kwargs):
    from hermes.factors.technical.core.overlap import rma
    length = int(length) if length and length > 0 else 9
    signal = int(signal) if signal and signal > 0 else 3
    offset = int(offset) if isinstance(offset, int) else 0
    highest_high = high.rolling(length).max()
    lowest_low = low.rolling(length).min()

    fastk = 100 * (close - lowest_low) / non_zero_range(
        highest_high, lowest_low)

    k = rma(fastk, length=signal)
    d = rma(k, length=signal)
    j = 3 * k - 2 * d

    # Offset
    if offset != 0:
        k = k.shift(offset)
        d = d.shift(offset)
        j = j.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        k.fillna(kwargs["fillna"], inplace=True)
        d.fillna(kwargs["fillna"], inplace=True)
        j.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        k.fillna(method=kwargs["fill_method"], inplace=True)
        d.fillna(method=kwargs["fill_method"], inplace=True)
        j.fillna(method=kwargs["fill_method"], inplace=True)
    return k, d, j


def kst(close,
        roc1=None,
        roc2=None,
        roc3=None,
        roc4=None,
        sma1=None,
        sma2=None,
        sma3=None,
        sma4=None,
        signal=None,
        drift=None,
        offset=None,
        **kwargs):
    roc1 = int(roc1) if roc1 and roc1 > 0 else 10
    roc2 = int(roc2) if roc2 and roc2 > 0 else 15
    roc3 = int(roc3) if roc3 and roc3 > 0 else 20
    roc4 = int(roc4) if roc4 and roc4 > 0 else 30

    sma1 = int(sma1) if sma1 and sma1 > 0 else 10
    sma2 = int(sma2) if sma2 and sma2 > 0 else 10
    sma3 = int(sma3) if sma3 and sma3 > 0 else 10
    sma4 = int(sma4) if sma4 and sma4 > 0 else 15

    signal = int(signal) if signal and signal > 0 else 9

    drift = int(drift) if isinstance(drift, int) and drift != 0 else 1
    offset = int(offset) if isinstance(offset, int) else 0
    # Calculate Result
    rocma1 = roc(close, roc1).rolling(sma1).mean()
    rocma2 = roc(close, roc2).rolling(sma2).mean()
    rocma3 = roc(close, roc3).rolling(sma3).mean()
    rocma4 = roc(close, roc4).rolling(sma4).mean()

    kst = 100 * (rocma1 + 2 * rocma2 + 3 * rocma3 + 4 * rocma4)
    kst_signal = kst.rolling(signal).mean()
    # Offset
    if offset != 0:
        kst = kst.shift(offset)
        kst_signal = kst_signal.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        kst.fillna(kwargs["fillna"], inplace=True)
        kst_signal.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        kst.fillna(method=kwargs["fill_method"], inplace=True)
        kst_signal.fillna(method=kwargs["fill_method"], inplace=True)
    return kst, kst_signal


def macd(close, fast=None, slow=None, signal=None, offset=None, **kwargs):
    from hermes.factors.technical.core.overlap import ema
    fast = int(fast) if fast and fast > 0 else 12
    slow = int(slow) if slow and slow > 0 else 26
    signal = int(signal) if signal and signal > 0 else 9
    if slow < fast:
        fast, slow = slow, fast
    offset = int(offset) if isinstance(offset, int) else 0

    as_mode = kwargs.setdefault("asmode", False)
    fastma = ema(close, length=fast)
    slowma = ema(close, length=slow)

    macd = fastma - slowma
    signalma = ema(close=macd.loc[macd.first_valid_index():, ], length=signal)
    histogram = macd - signalma
    if as_mode:
        macd = macd - signalma
        signalma = ema(close=macd.loc[macd.first_valid_index():, ],
                       length=signal)
        histogram = macd - signalma
    # Offset
    if offset != 0:
        macd = macd.shift(offset)
        histogram = histogram.shift(offset)
        signalma = signalma.shift(offset)
    return macd, histogram, signalma


def mom(close, length=None, offset=None, **kwargs):
    length = int(length) if length and length > 0 else 10
    offset = int(offset) if isinstance(offset, int) else 0
    mom = close.diff(length)
    # Offset
    if offset != 0:
        mom = mom.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        mom.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        mom.fillna(method=kwargs["fill_method"], inplace=True)
    return mom


def overnight(open, close, length=None, offset=None, **kwargs):
    length = int(length) if length and length > 0 else 10
    offset = int(offset) if isinstance(offset, int) else 0

    pre_close = close.shift(1)
    overnight = ((open - pre_close) / pre_close).rolling(length).mean()

    # Offset
    if offset != 0:
        overnight = overnight.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        overnight.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        overnight.fillna(method=kwargs["fill_method"], inplace=True)
    return overnight


def pgo(high, low, close, length=None, offset=None, **kwargs):
    from hermes.factors.technical.core.volatility import atr
    from hermes.factors.technical.core.overlap import sma, ema
    length = int(length) if length and length > 0 else 10
    offset = int(offset) if isinstance(offset, int) else 0

    # Calculate Result
    pgo = close - sma(close, length)
    pgo /= ema(atr(high, low, close, length), length)

    # Offset
    if offset != 0:
        pgo = pgo.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        pgo.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        pgo.fillna(method=kwargs["fill_method"], inplace=True)
    return pgo


def ppo(close,
        fast=None,
        slow=None,
        signal=None,
        scalar=None,
        offset=None,
        **kwargs):
    from hermes.factors.technical.core.overlap import sma, ema
    fast = int(fast) if fast and fast > 0 else 12
    slow = int(slow) if slow and slow > 0 else 26
    signal = int(signal) if signal and signal > 0 else 9
    scalar = float(scalar) if scalar else 100
    if slow < fast:
        fast, slow = slow, fast
    offset = int(offset) if isinstance(offset, int) else 0

    fastma = sma(close, length=fast)
    slowma = sma(close, length=slow)
    ppo = scalar * (fastma - slowma)
    ppo /= slowma

    signalma = ema(ppo, length=signal)
    histogram = ppo - signalma

    # Offset
    if offset != 0:
        ppo = ppo.shift(offset)
        histogram = histogram.shift(offset)
        signalma = signalma.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        ppo.fillna(kwargs["fillna"], inplace=True)
        histogram.fillna(kwargs["fillna"], inplace=True)
        signalma.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        ppo.fillna(method=kwargs["fill_method"], inplace=True)
        histogram.fillna(method=kwargs["fill_method"], inplace=True)
        signalma.fillna(method=kwargs["fill_method"], inplace=True)
    return ppo, histogram, signalma


def psl(close,
        open,
        length=None,
        scalar=None,
        drift=None,
        offset=None,
        **kwargs):
    length = int(length) if length and length > 0 else 12
    scalar = float(scalar) if scalar and scalar > 0 else 100
    offset = int(offset) if isinstance(offset, int) else 0
    drift = int(drift) if isinstance(drift, int) and drift != 0 else 1

    diff = np.sign(close - open)
    diff.fillna(0, inplace=True)
    diff[diff <= 0] = 0  # Zero negative values
    psl = scalar * diff.rolling(length).sum()
    psl /= length

    # Offset
    if offset != 0:
        psl = psl.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        psl.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        psl.fillna(method=kwargs["fill_method"], inplace=True)

    return psl


def pvo(volume,
        fast=None,
        slow=None,
        signal=None,
        scalar=None,
        offset=None,
        **kwargs):
    from hermes.factors.technical.core.overlap import ema
    fast = int(fast) if fast and fast > 0 else 12
    slow = int(slow) if slow and slow > 0 else 26
    signal = int(signal) if signal and signal > 0 else 9
    scalar = float(scalar) if scalar else 100
    if slow < fast:
        fast, slow = slow, fast
    offset = int(offset) if isinstance(offset, int) else 0
    # Calculate Result
    fastma = ema(volume, length=fast)
    slowma = ema(volume, length=slow)
    pvo = scalar * (fastma - slowma)
    pvo /= slowma

    signalma = ema(pvo, length=signal)
    histogram = pvo - signalma

    # Offset
    if offset != 0:
        pvo = pvo.shift(offset)
        histogram = histogram.shift(offset)
        signalma = signalma.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        pvo.fillna(kwargs["fillna"], inplace=True)
        histogram.fillna(kwargs["fillna"], inplace=True)
        signalma.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        pvo.fillna(method=kwargs["fill_method"], inplace=True)
        histogram.fillna(method=kwargs["fill_method"], inplace=True)
        signalma.fillna(method=kwargs["fill_method"], inplace=True)
    return pvo, histogram, signalma


def roc(close, length=None, scalar=None, offset=None, **kwargs):
    length = int(length) if length and length > 0 else 10
    scalar = float(scalar) if scalar and scalar > 0 else 100
    offset = int(offset) if isinstance(offset, int) else 0

    roc = scalar * mom(close=close, length=length) / close.shift(length)

    # Offset
    if offset != 0:
        roc = roc.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        roc.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        roc.fillna(method=kwargs["fill_method"], inplace=True)
    return roc


def rsi(close, length=None, scalar=None, drift=None, offset=None, **kwargs):
    from hermes.factors.technical.core.overlap import rma
    length = int(length) if length and length > 0 else 14
    scalar = float(scalar) if scalar else 100
    drift = int(drift) if isinstance(drift, int) and drift != 0 else 1
    offset = int(offset) if isinstance(offset, int) else 0

    negative = close.diff(drift)
    positive = negative.copy()

    positive[positive < 0] = 0  # Make negatives 0 for the postive series
    negative[negative > 0] = 0  # Make postives 0 for the negative series

    positive_avg = rma(positive, length=length)
    negative_avg = rma(negative, length=length)

    rsi = scalar * positive_avg / (positive_avg + negative_avg.abs())

    # Offset
    if offset != 0:
        rsi = rsi.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        rsi.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        rsi.fillna(method=kwargs["fill_method"], inplace=True)
    return rsi


def rvgi(open_,
         high,
         low,
         close,
         length=None,
         swma_length=None,
         offset=None,
         **kwargs):
    from hermes.factors.technical.core.overlap import swma
    high_low_range = non_zero_range(high, low)
    close_open_range = non_zero_range(close, open_)
    length = int(length) if length and length > 0 else 14
    swma_length = int(swma_length) if swma_length and swma_length > 0 else 4
    offset = int(offset) if isinstance(offset, int) else 0
    # Calculate Result
    numerator = swma(close_open_range,
                     length=swma_length).rolling(length).sum()
    denominator = swma(high_low_range,
                       length=swma_length).rolling(length).sum()

    rvgi = numerator / denominator
    signal = swma(rvgi, length=swma_length)

    # Offset
    if offset != 0:
        rvgi = rvgi.shift(offset)
        signal = signal.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        rvgi.fillna(kwargs["fillna"], inplace=True)
        signal.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        rvgi.fillna(method=kwargs["fill_method"], inplace=True)
        signal.fillna(method=kwargs["fill_method"], inplace=True)
    return rvgi, signal


def slope(close,
          length=None,
          as_angle=None,
          to_degrees=None,
          vertical=None,
          offset=None,
          **kwargs):
    length = int(length) if length and length > 0 else 1
    as_angle = True if isinstance(as_angle, bool) else False
    to_degrees = True if isinstance(to_degrees, bool) else False
    offset = int(offset) if isinstance(offset, int) else 0

    slope = close.diff(length) / length
    if as_angle:
        slope = slope.apply(np.arctan)
        if to_degrees:
            slope *= 180 / np.pi

    # Offset
    if offset != 0:
        slope = slope.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        slope.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        slope.fillna(method=kwargs["fill_method"], inplace=True)
    return slope


def stoch(high,
          low,
          close,
          k=None,
          d=None,
          smooth_k=None,
          offset=None,
          **kwargs):
    from hermes.factors.technical.core.overlap import sma
    k = k if k and k > 0 else 14
    d = d if d and d > 0 else 3
    smooth_k = smooth_k if smooth_k and smooth_k > 0 else 3
    offset = int(offset) if isinstance(offset, int) else 0

    # Calculate Result
    lowest_low = low.rolling(k).min()
    highest_high = high.rolling(k).max()

    stoch = 100 * (close - lowest_low)
    stoch /= non_zero_range(highest_high, lowest_low)

    stoch_k = sma(stoch.loc[stoch.first_valid_index():, ], length=smooth_k)
    stoch_d = sma(stoch_k.loc[stoch_k.first_valid_index():, ], length=d)

    # Offset
    if offset != 0:
        stoch_k = stoch_k.shift(offset)
        stoch_d = stoch_d.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        stoch_k.fillna(kwargs["fillna"], inplace=True)
        stoch_d.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        stoch_k.fillna(method=kwargs["fill_method"], inplace=True)
        stoch_d.fillna(method=kwargs["fill_method"], inplace=True)
    return stoch_k, stoch_d


def stochrsi(close,
             length=None,
             rsi_length=None,
             k=None,
             d=None,
             offset=None,
             **kwargs):
    from hermes.factors.technical.core.overlap import sma
    length = length if length and length > 0 else 14
    rsi_length = rsi_length if rsi_length and rsi_length > 0 else 14
    k = k if k and k > 0 else 3
    d = d if d and d > 0 else 3

    offset = int(offset) if isinstance(offset, int) else 0

    # Calculate Result
    rsi_ = rsi(close, length=rsi_length)
    lowest_rsi = rsi_.rolling(length).min()
    highest_rsi = rsi_.rolling(length).max()

    stoch = 100 * (rsi_ - lowest_rsi)
    stoch /= non_zero_range(highest_rsi, lowest_rsi)

    stochrsi_k = sma(stoch, length=k)
    stochrsi_d = sma(stochrsi_k, length=d)

    # Offset
    if offset != 0:
        stochrsi_k = stochrsi_k.shift(offset)
        stochrsi_d = stochrsi_d.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        stochrsi_k.fillna(kwargs["fillna"], inplace=True)
        stochrsi_d.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        stochrsi_k.fillna(method=kwargs["fill_method"], inplace=True)
        stochrsi_d.fillna(method=kwargs["fill_method"], inplace=True)
    return stochrsi_k, stochrsi_d


def trix(close,
         length=None,
         signal=None,
         scalar=None,
         drift=None,
         offset=None,
         **kwargs):
    from hermes.factors.technical.core.overlap import ema
    length = int(length) if length and length > 0 else 30
    signal = int(signal) if signal and signal > 0 else 9
    scalar = float(scalar) if scalar else 100

    drift = int(drift) if isinstance(drift, int) and drift != 0 else 1
    offset = int(offset) if isinstance(offset, int) else 0

    # Calculate Result
    ema1 = ema(close=close, length=length, **kwargs)
    ema2 = ema(close=ema1, length=length, **kwargs)
    ema3 = ema(close=ema2, length=length, **kwargs)
    trix = scalar * ema3.pct_change(drift)

    trix_signal = trix.rolling(signal).mean()
    # Offset
    if offset != 0:
        trix = trix.shift(offset)
        trix_signal = trix_signal.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        trix.fillna(kwargs["fillna"], inplace=True)
        trix_signal.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        trix.fillna(method=kwargs["fill_method"], inplace=True)
        trix_signal.fillna(method=kwargs["fill_method"], inplace=True)
    return trix, trix_signal


def tsi(close,
        fast=None,
        slow=None,
        signal=None,
        scalar=None,
        drift=None,
        offset=None,
        **kwargs):
    from hermes.factors.technical.core.overlap import ema
    fast = int(fast) if fast and fast > 0 else 13
    slow = int(slow) if slow and slow > 0 else 25
    signal = int(signal) if signal and signal > 0 else 13
    scalar = float(scalar) if scalar else 100

    drift = int(drift) if isinstance(drift, int) and drift != 0 else 1
    offset = int(offset) if isinstance(offset, int) else 0

    # Calculate Result
    diff = close.diff(drift)
    slow_ema = ema(close=diff, length=slow, **kwargs)
    fast_slow_ema = ema(close=slow_ema, length=fast, **kwargs)

    abs_diff = diff.abs()
    abs_slow_ema = ema(close=abs_diff, length=slow, **kwargs)
    abs_fast_slow_ema = ema(close=abs_slow_ema, length=fast, **kwargs)

    tsi = scalar * fast_slow_ema / abs_fast_slow_ema
    tsi_signal = ema(tsi, length=signal)

    # Offset
    if offset != 0:
        tsi = tsi.shift(offset)
        tsi_signal = tsi_signal.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        tsi.fillna(kwargs["fillna"], inplace=True)
        tsi_signal.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        tsi.fillna(method=kwargs["fill_method"], inplace=True)
        tsi_signal.fillna(method=kwargs["fill_method"], inplace=True)
    return tsi, tsi_signal


def upintraday(open, high, length=None, offset=None, **kwargs):
    length = int(length) if length and length > 0 else 5
    offset = int(offset) if isinstance(offset, int) else 0

    upintraday = ((high - open) / open).rolling(length).mean()

    # Offset
    if offset != 0:
        upintraday = upintraday.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        upintraday.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        upintraday.fillna(method=kwargs["fill_method"], inplace=True)
    return upintraday


def dnintraday(open, low, length=None, offset=None, **kwargs):
    length = int(length) if length and length > 0 else 5
    offset = int(offset) if isinstance(offset, int) else 0

    dnintraday = ((low - open) / open).rolling(length).mean()

    # Offset
    if offset != 0:
        dnintraday = dnintraday.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        dnintraday.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        dnintraday.fillna(method=kwargs["fill_method"], inplace=True)
    return dnintraday


def upchvolatility(close, high, length=None, offset=None, **kwargs):
    length = int(length) if length and length > 0 else 5
    offset = int(offset) if isinstance(offset, int) else 0

    pre_close = close.shift(1)

    upchvolatility = ((high - pre_close) / pre_close).rolling(length).mean()

    # Offset
    if offset != 0:
        upchvolatility = upchvolatility.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        upchvolatility.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        upchvolatility.fillna(method=kwargs["fill_method"], inplace=True)
    return upchvolatility


def uphhvolatility(high, length=None, offset=None, **kwargs):
    length = int(length) if length and length > 0 else 5
    offset = int(offset) if isinstance(offset, int) else 0

    pre_high = high.shift(1)

    uphhvolatility = ((high - pre_high) / pre_high).rolling(length).mean()

    # Offset
    if offset != 0:
        uphhvolatility = uphhvolatility.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        uphhvolatility.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        uphhvolatility.fillna(method=kwargs["fill_method"], inplace=True)
    return uphhvolatility


def willr(high, low, close, length=None, talib=None, offset=None, **kwargs):
    length = int(length) if length and length > 0 else 14
    min_periods = int(
        kwargs["min_periods"]) if "min_periods" in kwargs and kwargs[
            "min_periods"] is not None else length
    offset = int(offset) if isinstance(offset, int) else 0

    lowest_low = low.rolling(length, min_periods=min_periods).min()
    highest_high = high.rolling(length, min_periods=min_periods).max()

    willr = 100 * ((close - lowest_low) / (highest_high - lowest_low) - 1)

    # Offset
    if offset != 0:
        willr = willr.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        willr.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        willr.fillna(method=kwargs["fill_method"], inplace=True)
    return willr