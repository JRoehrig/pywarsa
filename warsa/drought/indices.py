import math
import numpy as np
from scipy.stats import norm
from scipy.stats import gamma
from warsa.hydrostatistics import moments
import warsa.hydrostatistics.genloglogistic as glo
from warsa.timeseries.timeseries import get_n_monthly_data
from warsa.timeseries.monthly import split_monthly_data_annually


# =============================================================================
# SPEI
# =============================================================================
def spi(precipitation):
    """
    :param precipitation: precipitation values
    :type precipitation: list or np.array
    :return: list of spi
    :rtype: list
    """
    try:
        precipitation = np.array(precipitation)
    except AttributeError:
        pass
    if precipitation is None:
        return np.array([])
    result = np.full(len(precipitation), np.nan)
    if len(precipitation) < 2:
        return result
    precipitation_gtz = precipitation[precipitation > 0.0]
    lambda1, lambda2 = moments.lmoments(precipitation_gtz, 2)
    alpha, beta = moments.lmoments_parameter_estimation_gamma(lambda1, lambda2)
    f = float(len(precipitation_gtz)) / len([np.isnan(p) for p in precipitation])
    for i, p in enumerate(precipitation):
        if not np.isnan(p):
            result[i] = norm.ppf((1 - f) + f * gamma.cdf(p, alpha, scale=beta))
    return result


def spi_old(precipitation):
    """
    :param precipitation: precipitation values
    :type precipitation: list or np.array
    :return: list of spi
    :rtype: list
    """
    try:
        precipitation = precipitation.tolist()
    except AttributeError:
        pass

    if not precipitation:
        return []
    elif len(precipitation) < 2:
        return [None] * len(precipitation)
    c0 = 2.515517
    c1 = 0.802853
    c2 = 0.010328
    d1 = 1.432788
    d2 = 0.189269
    d3 = 0.001308
    # number of set precipitation (not None)
    num_val = 0
    # number of precipitation greater then zero
    num_gtz = 0
    # ln(p) for p!=None and p>0.0
    sum_lnp = 0.0
    # Sum of p
    sum_p = 0.0
    for p in precipitation:
        if p is not None:
            num_val += 1
            if p > 0:
                num_gtz += 1
                sum_lnp += math.log(p)
                sum_p += p

    A = math.log(sum_p / num_gtz) - sum_lnp / num_gtz
    alpha = (1 / (4.0 * A)) * (1.0 + math.sqrt(1.0 + 4.0 * A / 3.0))
    beta = (sum_p / num_gtz) / alpha
    result = []
    for p in precipitation:
        if p is not None:
            gammap = gamma.cdf(p, alpha, scale=beta)
            q = (1.0 - float(num_gtz) / num_val)
            h = q + (1.0 - q) * gammap
            if h <= 0.5:
                t = math.sqrt(math.log(1.0 / (h ** 2)))
                v = -(t - (c0 + c1 * t + c2 * t ** 2) / (1 + d1 * t + d2 * t ** 2 + d3 * t ** 3))
            else:
                t = math.sqrt(math.log(1.0 / ((1.0 - h) ** 2)))
                v = t - (c0 + c1 * t + c2 * t ** 2) / (1 + d1 * t + d2 * t ** 2 + d3 * t ** 3)
            result.append(v)
        else:
            result.append(None)
    return result


def spi_monthly(sr, months=range(1, 13), n=1, prefix='Prec', min_years=20):
    """
    :param sr: Series with precipitation depth
    :type sr:
    :param months: list of months, e.g. [11, 12, 1, 2, 3]
    :type months:
    :param n: number of months to aggregate: 1, 2, 3, 4, or 6. Default: n=1
    :type n:
    :param prefix:
    :type prefix:
    :param min_years:
    :type min_years:
    :return: pandas.DataFrame with precipitations 'Prec' and drought indices 'Spi' fro each year and month
    :rtype:
    """
    sr = get_n_monthly_data(sr, months, n)
    if len(sr.index) == 0:
        return None
    df = split_monthly_data_annually(sr, months, n, prefix=prefix)
    if len(df.index) < min_years:
        return None
    for c in df.columns:
        df['Spi' + c[len(prefix):]] = np.array(spi(df[c].tolist()))
    return df


# =============================================================================
# SPEI
# =============================================================================
def spei(values):
    """Calculate SPEI from given values.

    Values are the differences between precipitation and potential evapotranspiration.

    For example if you want to calculate spei from January in the


    :param values: list or numpy array of values
    :type values: list, numpy array
    :return:
    :rtype:
    """
    lambda1, lambda2, tau3 = moments.lmoments(values, 3)
    mu, sigma, kappa = moments.lmoments_parameter_estimation_generalized_logistic(lambda1, lambda2, tau3)
    return norm.ppf(glo.cdf(values, kappa, mu, sigma))


