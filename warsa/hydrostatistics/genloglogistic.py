import numpy as np


def cdf(x, c, loc=0, scale=1):
    """Return the cdf
    :param x:
    :type x:
    :param c:
    :type c:
    :param loc:
    :type loc:
    :param scale:
    :type scale:
    :return:
    :rtype:
    """
    x = (x - loc) / scale
    try:
        c = round(c, 15)
        x = np.log(1 - c * x) / c
        return 1.0 / (1 + np.exp(x))
    except ZeroDivisionError:
        return 1.0 / (1 + np.exp(-x))
