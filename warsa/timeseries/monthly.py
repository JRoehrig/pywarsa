import datetime
import pandas as pd
from dateutil.relativedelta import relativedelta
from timeseries import slice_by_timestamp
from yearly import replace_year


def set_to_begin(values):
    """Set the dates and times in the list to the begin of the month
    :param values:
    :type values:
    :return:
    :rtype:
    """
    return [pd.Timestamp(v).replace(day=1, hour=0, minute=0, second=0, microsecond=0) for v in values]


def set_to_end(values):
    """Set the dates and times in the list to the end of the month
    :param values:
    :type values:
    :return:
    :rtype:
    """
    try:
        return [pd.Timestamp(v).replace(day=last_day(v), hour=23, minute=59, second=59, microsecond=999999) for v in values]
    except TypeError:
        return pd.Timestamp(values).replace(day=last_day(values), hour=23, minute=59, second=59, microsecond=999999)


def last_day(dt):
    return (pd.Timestamp(dt) + pd.tseries.offsets.MonthEnd(n=0)).day


def is_last_day(dt):
    """Check whether day in ``dt`` is the last day of the month
    :param dt: datetime
    :type dt: datetime, pd.Timestamp, np.datetime64
    :return: True/False
    :rtype: bool
    """
    return pd.Timestamp(dt).day == last_day(dt)


def increment(dt, months=1, microseconds=0):
    """Increment ``ts`` by ``months``. Default is to increment one month. Return a ``pd.Timestamp``

    :param dt: timestamp
    :type dt: datetime, pd.Timestamp, np.datetime64
    :param months: number of months to increment. Negative values are allowed. Default months = 1
    :type months: int
    :param microseconds: microseconds to add to the right interval: 0 for closed, -1 for right opened interval
    :type microseconds: int
    :return: ts incremented by ``months``
    :rtype: pd.Timestamp
    """
    # Don't use pd.Timedelta:
    # pd.Timestamp('2000-12-30 07:30') + pd.Timedelta(1, unit='M') == Timestamp('2001-01-29 17:59:06')
    dt = pd.Timestamp(dt)
    ts1 = pd.Timestamp(pd.Timestamp(dt).to_datetime() + relativedelta(months=months, microseconds=microseconds))
    if is_last_day(dt):
        return ts1.replace(day=1) + pd.tseries.offsets.MonthEnd(n=1)
    else:
        return ts1


def intervals(indices, months=None, accum=1, start_at=None, closed_left=True, closed_right=True):
    """

    :param indices: list of timestamps
    :type indices: pd.DatetimeIndex
    :param months: months to get intervals
    :type months: list
    :param accum: number of accumulated months
    :type accum: int
    :param start_at: date and time to start. Only the day of date will be used, year and month are discarded.
    :type start_at: datetime.datetime, str
    :param closed_left: left close interval
    :type closed_left: bool
    :param closed_right: right close interval
    :type closed_right: bool
    :return: list of intervals [[begin0, end0], [begin1, end1], ..., [beginN, endN]]
    :rtype: list of [pd.Timestamp, pd.Timestamp]
    """
    if not months:
        months = range(1, 13)

    if start_at == 'beg':
        start_at = datetime.datetime(2000, 1, 1, 0, 0, 0, 0)
    elif start_at == 'end':
        start_at = indices[0].replace(day=last_day(indices[0])).replace(hour=23, minute=59, second=59,
                                                                        microsecond=999999)
    elif start_at is None:
        start_at = indices[0]

    tuples = list()
    ts0 = replace_year(start_at, indices[0].year)
    while ts0 <= indices[-1]:
        if ts0.month in months:
            tuples.append([ts0, increment(ts0, accum)] if accum > 0 else [increment(ts0, accum), ts0])
        ts0 = increment(ts0, 1)
    if not closed_right:
        tuples = [[ts0, ts1 - pd.Timedelta(1, unit='us')] for ts0, ts1 in tuples]
    if not closed_left:
        tuples = [[ts0 + pd.Timedelta(1, unit='us'), ts1] for ts0, ts1 in tuples]

    return tuples


def series_starting_at(series, rule='sum', months=None, accum=1, start_at=None, closed_left=True, closed_right=False,
                       label='right', is_sorted=False):
    """Beginning at ``begin``, return the series resampled to the months listed in ``months``,
    taking ``accum`` adjacent months. The default resampling rule is ``sum``.

    :param series:
    :type series: DataFrame, Series
    :param rule:
    :type rule: DataFrame, Series
    :param months: If months is None, all 12 months will be used.
    :type months: list
    :param accum: number of months to accumulate (default 1). It may be also negative.
    :type accum: int
    :param start_at: datetime, 'beg', or 'end'
    :type start_at: datetime.datetime, str
    :param closed_left: left close interval
    :type closed_left: bool
    :param closed_right: right close interval
    :type closed_right: bool
    :param label:
    :type label:
    :param is_sorted:
    :type is_sorted:
    :return:
    :rtype: DataFrame, Series
    """
    if not is_sorted:
        series = series.sort_index()
    if accum > 0:
        if label == 'right':
            tdf = zip(*[[end, getattr(slice_by_timestamp(series, beg, end), rule)()]
                        for beg, end in intervals(series.index, months=months, accum=accum, start_at=start_at,
                                                  closed_left=closed_left, closed_right=closed_right)])
        elif label == 'left':
            tdf = zip(*[[beg, getattr(slice_by_timestamp(series, beg, end), rule)()]
                        for beg, end in intervals(series.index, months=months, accum=accum, start_at=start_at,
                                                  closed_left=closed_left, closed_right=closed_right)])
    else:
        if label == 'right':
            tdf = zip(*[[end, getattr(slice_by_timestamp(series, beg, end), rule)()]
                        for beg, end in intervals(series.index, months=months, accum=accum, start_at=start_at,
                                                  closed_left=closed_left, closed_right=closed_right)])
        elif label == 'left':
            tdf = zip(*[[beg, getattr(slice_by_timestamp(series, beg, end), rule)()]
                        for beg, end in intervals(series.index, months=months, accum=accum, start_at=start_at,
                                                  closed_left=closed_left, closed_right=closed_right)])
    if label == 'right':
        pass
    elif label == 'left':
        pass

    try:
        return pd.concat(tdf[1][:], axis=1).transpose().set_index(pd.DatetimeIndex(tdf[0]))
    except TypeError:
        return pd.Series(tdf[1], index=tdf[0])

    # indices = list()
    # values = list()
    # for interval in intervals(series.index, months=months, accum=accum, start_at=start_at, closed=closed):
    #     indices.append(interval[0])
    #     values.append(slice_by_datetime(series, interval[0], interval[1]).sum())
    # return pd.Series(values, index=indices)


# def monthly(series, rule='sum', months=None, accum=1, closed='left', label='right'):
#     """
#
#     :param series: Series
#     :type series: pandas.Series
#     :param months: months
#     :type months: list
#     :param accum: number of months to aggregate
#     :type accum: int
#     :param closed:
#     :type closed:
#     :param label:
#     :type label:
#     :return:
#     :rtype:
#     """
#     if not months:
#         result = series.resample(rule=str(accum) + 'M', closed=closed, label=label).sum()
#     else:
#         result = None
#         for m in months:
#             if accum > 0:
#                 srm = monthly(series.loc[(series.index.month >= m) & (series.index.month < m + accum)], accum=accum).dropna(how='all')
#             else:
#                 srm = monthly(series.loc[(series.index.month >= m + accum) & (series.index.month < m)], accum=accum).dropna(how='all')
#             result = pd.concat([result, srm])
#         if result is not None:
#             result = result.sort_index()
#     return result


def split_monthly_data_annually(sr, months=range(1, 13), n=1, closed='left', label='right', prefix='M'):
    """Aggregate data monthly according to the number of months, closed and label

    :param sr:
    :param months:
    :param n:
    :param closed:
    :param label:
    :param prefix:
    :return:
    """
    months = [m for m in months if m in set(sr.index.month)]
    df = pd.DataFrame(index=range(min(sr.index.year), max(sr.index.year)+1))
    for m in months:
        srm = sr.loc[(sr.index.month == m)]
        srm.index = srm.index.year
        df1 = pd.DataFrame(index=srm.index)
        suffix = str((m - n) % 12 + 1).zfill(2) + '-' + str(m).zfill(2) if n > 1 else str(m).zfill(2)
        df1[prefix + suffix] = srm
        df = pd.concat([df, df1], axis=1)
    return df


