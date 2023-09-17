# -*- encoding:utf-8 -*-
import numpy as np
import pandas as pd


def marsts(recent,
           far,
           rinterval,
           finterval,
           drift=None,
           offset=None,
           **kwargs):
    offset = int(offset) if isinstance(offset, int) else 0
    drift = int(drift) if isinstance(drift, int) else 365.0

    marsts = ((recent - far) / far) * drift / (finterval - rinterval)

    # Offset
    if offset != 0:
        marsts = marsts.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        marsts.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        marsts.fillna(method=kwargs["fill_method"], inplace=True)
    return marsts


def plutots(main,
            second,
            minterval,
            sinterval,
            drift=None,
            offset=None,
            **kwargs):
    offset = int(offset) if isinstance(offset, int) else 0
    drift = int(drift) if isinstance(drift, int) else 365.0

    plutots = ((main - second) / second) * drift / (sinterval - minterval)

    # Offset
    if offset != 0:
        plutots = plutots.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        plutots.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        plutots.fillna(method=kwargs["fill_method"], inplace=True)
    return plutots


def comentts(main,
             far,
             minterval,
             finterval,
             drift=None,
             offset=None,
             **kwargs):
    offset = int(offset) if isinstance(offset, int) else 0
    drift = int(drift) if isinstance(drift, int) else 365.0

    comentts = ((main - far) / far) * drift / (finterval - minterval)

    # Offset
    if offset != 0:
        comentts = comentts.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        comentts.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        comentts.fillna(method=kwargs["fill_method"], inplace=True)
    return comentts


def ariests(recent,
            second,
            rinterval,
            sinterval,
            drift=None,
            offset=None,
            **kwargs):
    offset = int(offset) if isinstance(offset, int) else 0
    drift = int(drift) if isinstance(drift, int) else 365.0

    ariests = ((recent - second) / second) * drift / (sinterval - rinterval)

    # Offset
    if offset != 0:
        ariests = ariests.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        ariests.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        ariests.fillna(method=kwargs["fill_method"], inplace=True)
    return ariests


def marstsmom(recent, far, length=None, offset=None, **kwargs):
    offset = int(offset) if isinstance(offset, int) else 0
    length = int(length) if isinstance(length, int) else 20

    marstsmom = recent.rolling(length).sum() - far.rolling(length).sum()

    # Offset
    if offset != 0:
        marstsmom = marstsmom.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        marstsmom.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        marstsmom.fillna(method=kwargs["fill_method"], inplace=True)
    return marstsmom


def plutotsmom(main, second, length=None, offset=None, **kwargs):
    offset = int(offset) if isinstance(offset, int) else 0
    length = int(length) if isinstance(length, int) else 20

    plutotsmom = main.rolling(length).sum() - second.rolling(length).sum()

    # Offset
    if offset != 0:
        plutotsmom = plutotsmom.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        plutotsmom.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        plutotsmom.fillna(method=kwargs["fill_method"], inplace=True)
    return plutotsmom


def comenttsmom(main, far, length=None, offset=None, **kwargs):
    offset = int(offset) if isinstance(offset, int) else 0
    length = int(length) if isinstance(length, int) else 20

    comenttsmom = main.rolling(length).sum() - far.rolling(length).sum()

    # Offset
    if offset != 0:
        comenttsmom = comenttsmom.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        comenttsmom.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        comenttsmom.fillna(method=kwargs["fill_method"], inplace=True)
    return comenttsmom


def ariestsmom(recent, second, length=None, offset=None, **kwargs):
    offset = int(offset) if isinstance(offset, int) else 0
    length = int(length) if isinstance(length, int) else 20

    ariestsmom = recent.rolling(length).sum() - second.rolling(length).sum()

    # Offset
    if offset != 0:
        ariestsmom = ariestsmom.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        ariestsmom.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        ariestsmom.fillna(method=kwargs["fill_method"], inplace=True)
    return ariestsmom