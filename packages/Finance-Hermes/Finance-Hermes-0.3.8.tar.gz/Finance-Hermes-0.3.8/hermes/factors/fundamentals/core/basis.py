# -*- encoding:utf-8 -*-
import numpy as np
import pandas as pd


def annchg(spot, futures, interval, drift=None, offset=None, **kwargs):
    offset = int(offset) if isinstance(offset, int) else 0
    drift = int(drift) if isinstance(drift, int) else 365.0

    annchg = ((spot - futures) / futures) * drift / interval

    # Offset
    if offset != 0:
        annchg = annchg.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        annchg.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        annchg.fillna(method=kwargs["fill_method"], inplace=True)
    return annchg


def rsannchg(spot, recent, rinterval, drift=None, offset=None, **kwargs):
    return annchg(spot=spot,
                  futures=recent,
                  interval=rinterval,
                  drift=drift,
                  offset=offset,
                  **kwargs)


def msannchg(spot, main, minterval, drift=None, offset=None, **kwargs):
    return annchg(spot=spot,
                  futures=main,
                  interval=minterval,
                  drift=drift,
                  offset=offset,
                  **kwargs)


def fsannchg(spot, far, finterval, drift=None, offset=None, **kwargs):
    return annchg(spot=spot,
                  futures=far,
                  interval=finterval,
                  drift=drift,
                  offset=offset,
                  **kwargs)


def ssannchg(spot, second, sinterval, drift=None, offset=None, **kwargs):
    return annchg(spot=spot,
                  futures=second,
                  interval=sinterval,
                  drift=drift,
                  offset=offset,
                  **kwargs)