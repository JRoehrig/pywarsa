import datetime
import calendar
import pandas as pd
from timeseries import is_leap_day, split_annually
from dateutil.relativedelta import relativedelta


def replace_year(dt, year):
    """Replace the year in ``dt`` by ``year``. If dt has the last day in the month, keep also the last day of the
    month for leap years

    :param dt:
    :type dt:
    :param year:
    :type year:
    :return:
    :rtype:
    """
    dt = pd.Timestamp(dt)
    if is_leap_day(dt):
        if calendar.isleap(year):
            dt0 = dt.replace(year=year)
        else:
            dt0 = dt.replace(year=year, day=28)
    else:
        if calendar.isleap(year) and dt.day == 28 and dt.month == 2:
            dt0 = dt.replace(year=year, day=29)
        else:
            dt0 = dt.replace(year=year)
    return dt0


def increment(dt, years=1, microseconds=0):
    """Increment ``ts`` by ``years``. Default is to increment one year. Return a ``pd.Timestamp``

    :param dt: timestamp
    :type dt: datetime, pd.Timestamp, np.datetime64
    :param years: number of years to increment. Negative values are allowed. Default years = 1
    :type years: int
    :param microseconds: microseconds to add to the right interval: 0 for closed, -1 for right opened interval
    :type microseconds: int
    :return: ts incremented by ``years``
    :rtype: pd.Timestamp
    """
    # Don't use pd.Timedelta:
    # pd.Timestamp('2000-12-30 07:30') + pd.Timedelta(1, unit='M') == Timestamp('2001-01-29 17:59:06')
    dt = pd.Timestamp(dt)
    return pd.Timestamp(pd.Timestamp(dt).to_pydatetime() + relativedelta(years=years, microseconds=microseconds))


def get_max_min_mean(df, beg_datetime, end_datetime):
    df_dict = split_annually(df, beg_datetime, end_datetime)
    result_list = list()
    for k in sorted(df_dict.keys()):
        df_annual = df_dict[k]
        result_list.append([k[1].year, float(df_annual.min()), float(df_annual.max()), float(df_annual.mean())])
    result_list = map(list, zip(*result_list))
    return pd.DataFrame({'min': result_list[1], 'max': result_list[2], 'mean': result_list[3]},
                        index=result_list[0], columns=['min', 'max', 'mean'])
