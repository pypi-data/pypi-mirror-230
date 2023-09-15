# -*- coding: utf-8 -*-
"""
    202205-? Dr. Jie Zheng & Dr./Prof. Linqiao Jiang
    Light_Curve_Pipeline
    Match 2d objects, simplified
    v4 (202309) clean up, publish to pypi
"""


import numpy as np


def match2d(x1, y1, x2, y2, dislimit=5.0):
    """
    match 2d objects, with distance lower than distance limit
    Use O(n^2), not O(nlogn), but simpler, good enough for small lists
    :param x1:
    :param y1:
    :param x2:
    :param y2:
    :param dislimit:
    :return: ix1 and ix2
    """

    # numbers of objects list 1 and 2
    n1 = len(x1)
    n2 = len(x2)

    # distance matrix of each x1-x2 and y1-y2
    x12 = np.array([x1] * n2).T - np.array([x2] * n1)
    y12 = np.array([y1] * n2).T - np.array([y2] * n1)
    # 2d distance (squared)
    xy12 = x12 * x12 + y12 * y12
    # find pairs close enough
    ix1, ix2 = np.where(xy12 < dislimit * dislimit)

    return ix1, ix2


def offset1d(v1, v2, maxd=100, bins=200):
    """
    Find offset between v1 and v2, use peaks of v1-v2
    For 2d offset, use this method twice for x and y
    :param v1:
    :param v2:
    :param maxd: max distance
    :param bins: number of bins
    :return: offset and std
    """

    # numbers of v1 and v2
    n1 = len(v1)
    n2 = len(v2)

    # distance matrix fo each v1 - v2
    d12 = np.array([v1] * n2).T - np.array([v2] * n1)
    d12f = d12.flatten()
    # histrogram
    hi = np.histogram(d12f, bins=bins, range=(-maxd, maxd))
    # peak as the most common distance
    peak_ix = np.argmax(hi[0])
    d = (hi[1][peak_ix] + hi[1][peak_ix + 1]) / 2
    # keep pairs in +-5 bins
    d12p1 = d12f[np.abs(d12f - d) < (maxd / bins * 10)]
    # mean and std of offset
    d = np.mean(d12p1)
    s = np.std(d12p1)
    # use med+-3std pairs
    d12p2 = d12f[np.abs(d12f - d) < 3 * s]
    d = np.mean(d12p2)
    s = np.std(d12p2)

    return d, s
