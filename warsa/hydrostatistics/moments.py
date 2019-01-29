"""

"""
import math
import numpy as np
from scipy import misc


def pwm(sample, n=4, sorted_sample=False):
    """
    See for example: Diana Bilkova (2014): L-Moments and TL-Moments as an Alternative Tool of Statistical Data
    Analysis. Journal of Applied Mathematics and Physics, Vol.02 No.10(2014), Article ID:49981, 10 pages
    10.4236/jamp.2014.210104 (http://file.scirp.org/Html/1-1720182_49981.htm)

    :param sample: list or numpy array of values
    :param n: number of returned pwms
    :param sorted_sample: default False
    :return:
    """
    if not sorted_sample:
        sample = np.sort(sample)
    ns = len(sample)
    return [sum([misc.comb(j, r) * sample[j] for j in range(ns)])/(ns*misc.comb(ns-1, r)) for r in range(n)]


def lmoments(sample, n=4, ratio=True, lcv=False, sorted_sample=False):
    """Return the n first L-moments of the sample.
    If ratio is True, return Lr/L2 for r >= 3, where L3/L2 is the L-skewness and L4/L2 is the L-kurtosis
    If lcv is True, return the L-coefficient of variation L2/L1. For a non-negative random variable, this lies in the
    interval (0,1) and is identical to the Gini coefficient (see https://en.wikipedia.org/wiki/L-moment)
    :param sample:
    :param n:
    :param ratio:
    :param lcv:
    :param sorted_sample:
    :return:
    """
    b = pwm(sample, n, sorted_sample)
    result = [sum([(-1)**(r-k) * misc.comb(r, k) * misc.comb(r + k, k) * b[k] for k in range(r+1)]) for r in range(n)]
    if ratio:
        result[2:] = [r / result[1] for r in result[2:]]
    if lcv:
        result[1] /= result[0]
    return result


def lmoments_parameter_estimation_generalized_logistic(lambda1, lambda2, tau):
    """Return the location, scale and shape or the generalized logistic distribution

    :param lambda1: L-moment-1
    :param lambda2: L-moment-2
    :param tau:  L-moment-3 /  L-moment-2
    :return:
    """
    assert lambda2 > 0 and -1 < -tau < 1
    try:
        k = -tau
        a = math.sin(k * math.pi) / (k * math.pi)
        s = lambda2 * a
        m = lambda1 - (s / k) * (1.0 - 1.0 / a)
        return m, s, k
    except ZeroDivisionError:
        return lambda1, lambda2, 0.0


def lmoments_parameter_estimation_gamma(lambda1, lambda2):
    """Return the location and scale of the gamma distribution.

    Based on SUBROUTINE PELGAM of the LMOMENTS Fortran package version 3.04, July 2005

    :param lambda1: L-moment-1
    :param lambda2: L-moment-2
    :return:
    """
    if lambda1 <= lambda2 or lambda2 <= 0.0:
        return None
    cv = lambda2 / lambda1
    if cv >= 0.5:
        t = 1.0 - cv
        alpha = t * (0.7213 - t * 0.5947) / (1.0 + t * (-2.1817 + t * 1.2113))
    else:
        t = math.pi * cv * cv
        alpha = (1.0 - 0.3080 * t) / (t * (1.0 + t * (-0.05812 + t * 0.01765)))
    return alpha, lambda1/alpha

