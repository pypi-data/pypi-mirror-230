## 入口函数
def factor_run(close,
               deal,
               volume,
               length=None,
               threshold=None,
               offset=None,
               **kwargs):

    length = int(length) if length and length > 0 else 10
    offset = int(offset) if isinstance(offset, int) else 0

    avg_values = volume / deal
    v = close.pct_change(periods=length)
    cond = avg_values < threshold
    v[cond] = 0

    dissection = v.rollong(length).sum()
    # Offset
    if offset != 0:
        dissection = dissection.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        dissection.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        dissection.fillna(method=kwargs["fill_method"], inplace=True)

    return dissection