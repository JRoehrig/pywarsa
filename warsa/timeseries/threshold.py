import os
import datetime
import pandas as pd
import matplotlib.pyplot as plt
plt.style.use('ggplot')
pd.options.display.max_columns = 200
pd.options.display.width = 500


def threshold_ranges(sr, threshold):
    """Returns a pandas data frame with the columns Beg, End, and Type. Beg is a date/time with the beginning of the a
    time interval over/under threshold, End is a date/time with the end of this time interval. Type is 1 for intervals
    over threshold and -1 for intervals under or equal threshold. Beg of an interval is equal End of the previous
    interval. End of the last interval is NaT (not a time), i.e., it is an open interval. Consecutive intervals have
    alternating 1 and -1 values.
    Example:

    Beg                 End                 Type
    01.11.1937 07:30    12.10.1947 07:30     1        -> over threshold
    12.10.1947 07:30    14.11.1947 07:30    -1        -> under or equal threshold
    14.11.1947 07:30    01.09.1959 07:30     1
    01.09.1959 07:30    30.01.1960 07:30    -1
    ...
    12.09.2015 07:30    25.10.2015 07:30     1
    25.10.2015 07:30    20.11.2015 07:30    -1
    20.11.2015 07:30    NaT                  1


    :param sr: pandas series with date as index
    :param threshold:
    :return:
    """
    try:
        sr = sr[sr.columns[0]]
    except AttributeError:
        pass

    df_result = pd.DataFrame(columns=['Beg', 'End', 'Type'])

    row = 0

    over_threshold = 1 if sr[0] > threshold else -1
    df_result.loc[row] = [sr.index[row], None, over_threshold]

    for date, value in sr.iteritems():
        if value > threshold and over_threshold == -1:
            df_result.set_value(row, 'End', date)  # Close dry spell
            row += 1
            over_threshold = 1
            df_result.loc[row] = [date, None, over_threshold]  # Open wet spell
        if value <= threshold and over_threshold == 1:
            df_result.set_value(row, 'End', date)  # Close wet spell
            row += 1
            over_threshold = -1
            df_result.loc[row] = [date, None, over_threshold]  # Open dry spell
    return df_result


def threshold_ranges_annual(df, beg_month=1, beg_day=1, beg_hour=0, beg_minute=0):
    df_result = pd.DataFrame(columns=df.columns)
    row1 = 0
    beg0 = pd.Timestamp('{}-{:02d}-{:02d} {:02d}:{:02d}'.format(
        df.iloc[0]['Beg'].year, beg_month, beg_day, beg_hour, beg_minute), tz=None)
    for row in df.itertuples():
        end = row[2]
        typ = row[3]
        while beg0 < end:
            end0 = pd.Timestamp('{}-{:02d}-{:02d} {:02d}:{:02d}'.format(
                beg0.year, beg_month, beg_day, beg_hour, beg_minute), tz=None)  # same year
            if beg0 >= end0:  # next year
                end0 = pd.Timestamp('{}-{:02d}-{:02d} {:02d}:{:02d}'.format(
                    beg0.year + 1, beg_month, beg_day, beg_hour, beg_minute), tz=None)
            if end < end0:
                end0 = end
            df_result.loc[row1] = [beg0, end0, typ]
            row1 += 1
            beg0 = end0
    return df_result


def threshold_ranges_annual_plot(df, ax=None, plot_name=None, colors=None):
    from matplotlib.dates import DateFormatter
    formatter = DateFormatter('%b')

    def ff(row):
        beg = row['Beg']
        end = row['End']
        y_beg = beg.year
        y_end = end.year
        if y_beg == y_end:
            return datetime.date(2000, beg.month, beg.day), datetime.date(2000, end.month, end.day), beg.year
        else:
            return datetime.date(2000, beg.month, beg.day), datetime.date(2001, end.month, end.day), beg.year

    df[['x0', 'x1', 'y']] = df.apply(ff, axis=1)
    x0 = df['x0'].values
    x1 = df['x1'].values
    y = df['y'].values
    if not ax:
        _, ax = plt.subplots(1, 1)
    yc = 0
    color = color1
    for i in range(len(x0)):
        if y[i] == yc:
            color = color2 if color == color1 else color2
        else:
            color = color1
            yc = y[i]
        ax.plot([x0[i], x1[i]], [y[i], y[i]], linewidth=5.0, color=color)
    ax.xaxis.set_major_formatter(formatter)

    plt.show()
    # plt.savefig(plot_name, figsize=(400, 1000))


def threshold_ranges_annual_plot1(df, ax=None, plot_name=None, color1='C1', color2='C2'):
    from matplotlib.dates import DateFormatter
    formatter = DateFormatter('%b')

    def ff(row):
        beg = row['Beg']
        end = row['End']
        y_beg = beg.year
        y_end = end.year
        if y_beg == y_end:
            return datetime.date(2000, beg.month, beg.day), datetime.date(2000, end.month, end.day), beg.year
        else:
            print datetime.date(2000, beg.month, beg.day), datetime.date(2001, end.month, end.day), beg.year
            return datetime.date(2000, beg.month, beg.day), datetime.date(2001, end.month, end.day), beg.year

    df[['x0', 'x1', 'y']] = df.apply(ff, axis=1)
    x0 = df['x0'].values
    x1 = df['x1'].values
    y = df['y'].values
    if not ax:
        _, ax = plt.subplots(1, 1)
    yc = 0
    color = color1
    for i in range(len(x0)):
        if y[i] == yc:
            color = color2 if color == color1 else color2
        else:
            color = color1
            yc = y[i]
        ax.plot([x0[i], x1[i]], [y[i], y[i]], linewidth=5.0, color=color)
    ax.xaxis.set_major_formatter(formatter)

    plt.show()
    # plt.savefig(plot_name, figsize=(400, 1000))


