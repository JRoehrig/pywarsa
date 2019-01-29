import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import scipy
from scipy import stats
from warsa.timeseries.timeseries import split_annually
matplotlib.style.use('ggplot')


def get_annual_maxima(sr, beg_datetime=None, end_datetime=None):
    df_dict = split_annually(sr, beg_datetime=beg_datetime, end_datetime=end_datetime)
    years, discharges = zip(*[(k[1].year, df_dict[k].max().Value) for k in sorted(df_dict.keys())])
    return pd.Series(discharges, years)


def plot(sr, kind='line'):
    """Plot series
    """
    sr.plot(kind=kind)
    plt.show()


def plot_histogram(sr):
    # sr.plot.hist
    pd.Series().plot()


def probability_plot_pearson3(sr):
    s, loc, scale = scipy.stats.pearson3.fit(sr)
    scipy.stats.probplot(sr, sparams=s, dist='pearson3', fit=True, plot=plt)
    plt.show()


def probability_plot_gumbel_r(sr):
    scipy.stats.probplot(sr, sparams=(), dist='gumbel_r', fit=True, plot=plt)
    plt.show()


def probability_plot_lognorm(sr):
    s, loc, scale = scipy.stats.lognorm.fit(sr, floc=0)
    scipy.stats.probplot(sr, sparams=s, dist='lognorm', fit=True, plot=plt)
    plt.show()


def probability_plot_norm(sr):
    scipy.stats.probplot(sr, sparams=(), dist='norm', fit=True, plot=plt)
    plt.show()


