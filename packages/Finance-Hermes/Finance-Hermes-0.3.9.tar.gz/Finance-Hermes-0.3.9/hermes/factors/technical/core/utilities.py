# -*- coding: utf-8 -*-
import numpy as np
from sys import float_info as sflt
from functools import reduce
from math import floor as mfloor
from operator import mul


def combination(**kwargs: dict) -> int:
    """https://stackoverflow.com/questions/4941753/is-there-a-math-ncr-function-in-python"""
    n = int(np.fabs(kwargs.pop("n", 1)))
    r = int(np.fabs(kwargs.pop("r", 0)))

    if kwargs.pop("repetition", False) or kwargs.pop("multichoose", False):
        n = n + r - 1

    # if r < 0: return None
    r = min(n, n - r)
    if r == 0:
        return 1

    numerator = reduce(mul, range(n, n - r, -1), 1)
    denominator = reduce(mul, range(1, r + 1), 1)
    return numerator // denominator


def non_zero_range(high, low):
    """Returns the difference of two series and adds epsilon to any zero values.  This occurs commonly in crypto data when 'high' = 'low'."""
    diff = high - low
    if diff.eq(0).any().any():
        diff += sflt.epsilon
    return diff


def fibonacci(n: int = 2, **kwargs: dict):
    """Fibonacci Sequence as a numpy array"""
    n = int(np.fabs(n)) if n >= 0 else 2

    zero = kwargs.pop("zero", False)
    if zero:
        a, b = 0, 1
    else:
        n -= 1
        a, b = 1, 1

    result = np.array([a])
    for _ in range(0, n):
        a, b = b, a + b
        result = np.append(result, a)

    weighted = kwargs.pop("weighted", False)
    if weighted:
        fib_sum = np.sum(result)
        if fib_sum > 0:
            return result / fib_sum
        else:
            return result
    else:
        return result


def pascals_triangle(n: int = None, **kwargs: dict):
    """Pascal's Triangle

    Returns a numpy array of the nth row of Pascal's Triangle.
    n=4  => triangle: [1, 4, 6, 4, 1]
         => weighted: [0.0625, 0.25, 0.375, 0.25, 0.0625]
         => inverse weighted: [0.9375, 0.75, 0.625, 0.75, 0.9375]
    """
    n = int(np.fabs(n)) if n is not None else 0

    # Calculation
    triangle = np.array([combination(n=n, r=i) for i in range(0, n + 1)])
    triangle_sum = np.sum(triangle)
    triangle_weights = triangle / triangle_sum
    inverse_weights = 1 - triangle_weights

    weighted = kwargs.pop("weighted", False)
    inverse = kwargs.pop("inverse", False)
    if weighted and inverse:
        return inverse_weights
    if weighted:
        return triangle_weights
    if inverse:
        return None

    return triangle


def symmetric_triangle(n: int = None, **kwargs: dict):
    """Symmetric Triangle with n >= 2

    Returns a numpy array of the nth row of Symmetric Triangle.
    n=4  => triangle: [1, 2, 2, 1]
         => weighted: [0.16666667 0.33333333 0.33333333 0.16666667]
    """
    n = int(np.fabs(n)) if n is not None else 2

    triangle = None
    if n == 2:
        triangle = [1, 1]

    if n > 2:
        if n % 2 == 0:
            front = [i + 1 for i in range(0, mfloor(n / 2))]
            triangle = front + front[::-1]
        else:
            front = [i + 1 for i in range(0, mfloor(0.5 * (n + 1)))]
            triangle = front.copy()
            front.pop()
            triangle += front[::-1]

    if kwargs.pop("weighted", False) and isinstance(triangle, list):
        triangle_sum = np.sum(triangle)
        triangle_weights = triangle / triangle_sum
        return triangle_weights

    return triangle


def unsigned_differences(series, amount: int = None, **kwargs):
    """Unsigned Differences
    Returns two Series, an unsigned positive and unsigned negative series based
    on the differences of the original series. The positive series are only the
    increases and the negative series are only the decreases.

    Default Example:
    series   = Series([3, 2, 2, 1, 1, 5, 6, 6, 7, 5, 3]) and returns
    postive  = Series([0, 0, 0, 0, 0, 1, 1, 0, 1, 0, 0])
    negative = Series([0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 1])
    """
    amount = int(amount) if amount is not None else 1
    negative = series.diff(amount)
    negative.fillna(0, inplace=True)
    positive = negative.copy()

    positive[positive <= 0] = 0
    positive[positive > 0] = 1

    negative[negative >= 0] = 0
    negative[negative < 0] = 1

    if kwargs.pop("asint", False):
        positive = positive.astype(int)
        negative = negative.astype(int)

    return positive, negative


def weights(w):
    """Calculates the dot product of weights with values x"""

    def _dot(x):
        return np.dot(w, x)

    return _dot


def signed_series(series, initial):
    """Returns a Signed Series with or without an initial value

    Default Example:
    series = Series([3, 2, 2, 1, 1, 5, 6, 6, 7, 5])
    and returns:
    sign = Series([NaN, -1.0, 0.0, -1.0, 0.0, 1.0, 1.0, 0.0, 1.0, -1.0])
    """
    sign = series.diff(1)
    sign[sign > 0] = 1
    sign[sign < 0] = -1
    sign.iloc[0] = initial
    return sign


def zero(x):
    """If the value is close to zero, then return zero. Otherwise return itself."""
    return 0 if abs(x) < sflt.epsilon else x


def is_percent(x: int or float) -> bool:
    if isinstance(x, (int, float)):
        return x is not None and x >= 0 and x <= 100
    return False