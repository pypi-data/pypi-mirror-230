# -*- coding: utf-8 -*-
"""
    201901, Dr. Jie Zheng, Beijing & Xinglong, NAOC
    202101-? Dr. Jie Zheng & Dr./Prof. Linqiao Jiang
    Light_Curve_Pipeline
    v3 (2021A) Upgrade from former version, remove unused code
    v4 (202309) clean up, publish to pypi
"""


import numpy as np
from ._match_fast_ import match


def make_tri(x, y, goodix=None):
    """
    Generate C_n_3 triangles with given stars, return the triangle array
    :param x: x coordinates
    :param y: y coordinates
    :param goodix: indices of good stars
    :return: a rec-array of triangles
    """
    if goodix is None:
        goodix = np.arange(len(x))

    # number of good stars
    ngood = len(goodix)
    # number of triangles: C_n^3
    ntri = ngood * (ngood - 1) * (ngood - 2) // 6
    # print("{} Stars ==> {} Triangles".format(ngood, ntri))

    # 三角形数组
    tr = np.empty(ntri, [
        ("len0", float),  # Length of the largest edge
        ("fac1", float),  # fraction of the median edge to the largest
        ("fac2", float),  # fraction of the shortest edge to the largest
        ("p0", int),  # the point to the largest edge, or the largest angle
        ("p1", int),  # the point to the median edge
        ("p2", int),  # the point to the shortest edge
    ])

    # a function computing the length of an eage (two points)
    edgelen = lambda i1, i2: np.sqrt((x[pp[i1]] - x[pp[i2]]) ** 2 + (y[pp[i1]] - y[pp[i2]]) ** 2)

    k = 0
    for k1 in range(0, ngood - 2):
        for k2 in range(k1 + 1, ngood - 1):
            for k3 in range(k2 + 1, ngood):
                # generate a triangle, normalize it and add to list

                # the real ids of points
                pp = goodix[[k1, k2, k3]]
                # edge length
                ee = edgelen(1, 2), edgelen(2, 0), edgelen(0, 1)

                # sort and get indices
                ei = np.argsort(ee)
                # save to the triangle array
                tr[k]["len0"] = ee[ei[2]]
                tr[k]["fac1"] = ee[ei[1]] / ee[ei[2]]
                tr[k]["fac2"] = ee[ei[0]] / ee[ei[2]]
                tr[k]["p0"] = pp[ei[0]]
                tr[k]["p1"] = pp[ei[1]]
                tr[k]["p2"] = pp[ei[2]]

                k += 1

    return tr


def argunique_old(a):
    """
    find the first index of each element in a list
    """
    au = np.unique(a)
    nau = len(au)
    ix = np.empty(nau, int)
    for i in range(nau):
        ix[i] = np.where(a == au[i])[0][0]
    return ix


def argunique(a, b):
    """
    find the unique pair of matched points
    :param a:
    :param b:
    :return: (aaa, bbb), ensure each point appears only once
    """
    # check each item in a, add item to aa at the first time, check if the same at next time
    # -1 means conflict matching, discarded
    seta = {}
    for i, j in zip(a, b):
        if i not in seta:
            seta[i] = j
        elif seta[i] != j:
            seta[i] = -1
    aa = [i for i in seta if seta[i] != -1]
    bb = [seta[i] for i in seta if seta[i] != -1]
    # do this step again along b
    setb = {}
    for i, j in zip(aa, bb):
        if j not in setb:
            setb[j] = i
        elif setb[j] != i:
            setb[j] = -1
    aaa = [setb[j] for j in setb if setb[j] != -1]
    bbb = [j for j in setb if setb[j] != -1]

    return aaa, bbb


def match_triangle(tr1, tr2, maxerr=2.5e-3):
    """
    Match two arrays of triangles
    :param tr1: triangle list 1
    :param tr2: triangle list 2
    :param maxerr: max error in matching
    :return: matched stars
    """
    # match triangles with 2-d match process
    mix1, mix2, dis = match(
        tr1["fac1"], tr1["fac2"], None,
        tr2["fac1"], tr2["fac2"], None,
        dis_limit=maxerr)
    # print("{} Triangles matched".format(len(mix1)))

    # from triangles to points
    pp1 = np.concatenate((tr1[mix1]["p0"], tr1[mix1]["p1"], tr1[mix1]["p2"]))
    pp2 = np.concatenate((tr2[mix2]["p0"], tr2[mix2]["p1"], tr2[mix2]["p2"]))

    # remove duplicated and conflict pairs
    ppix = argunique_old(pp1)
    ppix = ppix[argunique_old(pp2[ppix])]
    pp1u = pp1[ppix]
    pp2u = pp2[ppix]
    # pp1u, pp2u = argunique(pp1, pp2)

    # return the points
    return pp1u, pp2u
