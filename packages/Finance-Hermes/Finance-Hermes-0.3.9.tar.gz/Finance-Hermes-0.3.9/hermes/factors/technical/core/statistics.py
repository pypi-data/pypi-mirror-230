# -*- coding: utf-8 -*-
import numpy as np


def kurtosis(close, length=None, offset=None, **kwargs):
    # Validate Arguments
    length = int(length) if length and length > 0 else 30
    min_periods = int(
        kwargs["min_periods"]) if "min_periods" in kwargs and kwargs[
            "min_periods"] is not None else length
    offset = int(offset) if isinstance(offset, int) else 0

    # Calculate Result
    kurtosis = close.rolling(length, min_periods=min_periods).kurt()

    # Offset
    if offset != 0:
        kurtosis = kurtosis.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        kurtosis.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        kurtosis.fillna(method=kwargs["fill_method"], inplace=True)

    return kurtosis


def mad(close, length=None, offset=None, **kwargs):
    length = int(length) if length and length > 0 else 30
    min_periods = int(
        kwargs["min_periods"]) if "min_periods" in kwargs and kwargs[
            "min_periods"] is not None else length
    offset = int(offset) if isinstance(offset, int) else 0

    # Calculate Result
    def mad_(series):
        """Mean Absolute Deviation"""
        return np.fabs(series - series.mean()).mean()

    mad = close.rolling(length, min_periods=min_periods).apply(mad_, raw=True)
    # Offset
    if offset != 0:
        mad = mad.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        mad.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        mad.fillna(method=kwargs["fill_method"], inplace=True)
    return mad


def median(close, length=None, offset=None, **kwargs):
    length = int(length) if length and length > 0 else 30
    min_periods = int(
        kwargs["min_periods"]) if "min_periods" in kwargs and kwargs[
            "min_periods"] is not None else length
    offset = int(offset) if isinstance(offset, int) else 0
    # Calculate Result
    median = close.rolling(length, min_periods=min_periods).median()

    # Offset
    if offset != 0:
        median = median.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        median.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        median.fillna(method=kwargs["fill_method"], inplace=True)
    return median


def quantile(close, length=None, q=None, offset=None, **kwargs):
    length = int(length) if length and length > 0 else 30
    min_periods = int(
        kwargs["min_periods"]) if "min_periods" in kwargs and kwargs[
            "min_periods"] is not None else length
    q = float(q) if q and q > 0 and q < 1 else 0.5
    offset = int(offset) if isinstance(offset, int) else 0

    # Calculate Result
    quantile = close.rolling(length, min_periods=min_periods).quantile(q)

    # Offset
    if offset != 0:
        quantile = quantile.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        quantile.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        quantile.fillna(method=kwargs["fill_method"], inplace=True)
    return quantile


def skew(close, length=None, offset=None, **kwargs):
    length = int(length) if length and length > 0 else 30
    min_periods = int(
        kwargs["min_periods"]) if "min_periods" in kwargs and kwargs[
            "min_periods"] is not None else length
    offset = int(offset) if isinstance(offset, int) else 0

    # Calculate Result
    skew = close.rolling(length, min_periods=min_periods).skew()

    # Offset
    if offset != 0:
        skew = skew.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        skew.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        skew.fillna(method=kwargs["fill_method"], inplace=True)

    return skew


def stdev(close, length=None, ddof=None, offset=None, **kwargs):
    length = int(length) if length and length > 0 else 30
    ddof = int(ddof) if isinstance(ddof,
                                   int) and ddof >= 0 and ddof < length else 1
    offset = int(offset) if isinstance(offset, int) else 0
    stdev = variance(close=close, length=length, ddof=ddof).apply(np.sqrt)
    # Offset
    if offset != 0:
        stdev = stdev.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        stdev.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        stdev.fillna(method=kwargs["fill_method"], inplace=True)
    return stdev


def variance(close, length=None, ddof=None, offset=None, **kwargs):
    length = int(length) if length and length > 1 else 30
    ddof = int(ddof) if isinstance(ddof,
                                   int) and ddof >= 0 and ddof < length else 1
    min_periods = int(
        kwargs["min_periods"]) if "min_periods" in kwargs and kwargs[
            "min_periods"] is not None else length
    offset = int(offset) if isinstance(offset, int) else 0

    variance = close.rolling(length, min_periods=min_periods).var(ddof)
    # Offset
    if offset != 0:
        variance = variance.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        variance.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        variance.fillna(method=kwargs["fill_method"], inplace=True)
    return variance


def zscore(close, length=None, std=None, offset=None, **kwargs):
    from hermes.factors.technical.factor_overlap import sma
    length = int(length) if length and length > 1 else 30
    std = float(std) if std and std > 1 else 1

    offset = int(offset) if isinstance(offset, int) else 0

    std *= stdev(close=close, length=length, **kwargs)
    mean = sma(close=close, length=length, **kwargs)
    zscore = (close - mean) / std

    # Offset
    if offset != 0:
        zscore = zscore.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        zscore.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        zscore.fillna(method=kwargs["fill_method"], inplace=True)
    return zscore