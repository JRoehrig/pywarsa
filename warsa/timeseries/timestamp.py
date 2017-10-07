import pandas as pd


def set_time(values, time):
    """Set time to all elements in the list values

    :param values: list of datetime, pd.Timestamp, or np.datetime64
    :type values: list, pd.DatetimeIndex, or np.array
    :param time: time (hour, minute, second, microsecond), 0 < microsecond < 999999
    :type time: datetime.time
    :return: list of pd.Timestamp
    :rtype: list
    """
    hour, minute, second, microsecond = time.hour, time.minute, time.second, time.microsecond
    return [pd.Timestamp(v).replace(hour=hour, minute=minute, second=second, microsecond=microsecond) for v in values]


