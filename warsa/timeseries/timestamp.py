import pandas as pd


def set_time(datetime, time):
    """Set time to all elements in the list values

    :param datetime: list of datetime, pd.Timestamp, or np.datetime64
    :type datetime: list, pd.DatetimeIndex, or np.array
    :param time: time (hour, minute, second, microsecond), 0 < microsecond < 999999
    :type time: datetime.time
    :return: list of pd.Timestamp
    :rtype: list
    """
    hour, minute, second, microsecond = time.hour, time.minute, time.second, time.microsecond
    return [pd.Timestamp(v).replace(hour=hour, minute=minute, second=second, microsecond=microsecond) for v in datetime]


