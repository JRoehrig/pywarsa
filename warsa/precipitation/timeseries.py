# _*_ coding: utf-8
# __author__ = 'roehrig'

import os
import calendar
import numpy as np
import pandas as pd
from pandas import ExcelWriter
from os.path import splitext, dirname
from datetime import datetime
from dateutil.relativedelta import relativedelta


# ##############################################################################
# ################## Read time series ##########################################
# ##############################################################################


def read_time_series(filename, columns=None, beg_datetime=pd.Timestamp.min, end_datetime=pd.Timestamp.max, worksheet_name=None):
    if filename.endswith('.csv'):
        return read_csv(filename, columns, beg_datetime, end_datetime)
    elif filename.endswith('.xls'):
        return read_xls(filename, columns, beg_datetime, end_datetime, worksheet_name)
    elif filename.endswith('.xlsx'):
        return read_xlsx(filename, columns, beg_datetime, end_datetime, worksheet_name)
    raise Exception('File type unknown: {}'.format(filename))


def _read_time_series(df, columns=None, beg_datetime=pd.Timestamp.min, end_datetime=pd.Timestamp.max):
    """
    Import time series df from files containing a first column with dates and subsequent columns with values,
    each column representing one time series. The first valid row has columns names, the further rows contain values.
    There should be no empty column between the datetime column and the last station.

    The optional parameter columns is a list containing the stations codes to read df from.
    If not given, all columns will be read

    IMPORTANT: The first valid column and row must contain the text "Date". This method
    searches for Date starting from the first column.
    Example:
        Date          P66    P77   ...
        01.10.1998    0.0          ...
        02.10.1998    0.0          ...
        03.10.1998    0.0    0.0   ...
        ...           ...    ...

    Parameters
    ----------
    filename : str
        The csv file code.
    columns : list of str, optional
        The list of tss to import df from

    Returns
    -------
    None

    Raises
    ------
    None
    """
    if columns:
        df = df[columns]
    df = slice_by_datetime(df, beg_datetime, end_datetime)
    df = drop_date_duplicates(df)
    fvi = df.first_valid_index()
    lvi = df.last_valid_index()
    df = df[fvi:lvi]
    return df.sort_index().astype(float)


def read_csv(filename, columns=None, beg_datetime=pd.Timestamp.min, end_datetime=pd.Timestamp.max, separator=';', index_col=0):
    try:
        df = pd.read_csv(filename, sep=separator, index_col=index_col, parse_dates=True)
        if len(df) > 0:
            return _read_time_series(df, columns, beg_datetime, end_datetime)
        else:
            return None
    except ValueError:
        return None


def read_xlsx(excel_filename, columns=None, beg_datetime=None, end_datetime=None, worksheet_name=None):
    """
    Reads only one worksheet. If worksheet_name=None, reads the first worksheet

    return: list of DataFrame
    """
    xl_file = pd.ExcelFile(excel_filename)
    for sheet_name in xl_file.sheet_names:
        if worksheet_name is None or worksheet_name == sheet_name:
            df = pd.DataFrame({sheet_name: xl_file.parse(sheet_name)})
            return _read_time_series(df, columns, beg_datetime, end_datetime)
    raise Exception('read_time_series_from_xlsx: worksheet_name {} not found in {}'.format(worksheet_name, excel_filename))


def read_xls(excel_filename, columns=None, beg_datetime=pd.Timestamp.min, end_datetime=pd.Timestamp.max, worksheet_name=0):
    """ Reads only one worksheet. If worksheet_name=None, reads the first worksheet

    io_ex: string, file-like object, or xlrd workbook

    return: DataFrame
    """
    df = pd.io.excel.read_excel(excel_filename, sheetname=worksheet_name)
    if not isinstance(df, pd.DataFrame):
        raise Exception('read_time_series_from_xls: worksheet_name {} not found in {}'.format(worksheet_name, excel_filename))
    return _read_time_series(df, columns, beg_datetime, end_datetime)


# =============================================================================
# Write time series
# =============================================================================
def write_time_series(df, filename, start_row=0, separated=False, column=None):
    """
    Write the time series in df into the filename. Filename can be in
        the formats csv, xls, or xlsx.

    If separated is False, save the time series into one file in the case of
        csv-files or into one worksheet in the case of xls- or xlsx-format
        Otherwise, save each time series into a different file in the case of
        csv-files or in different worksheets in case of excel-files. In these
        cases, the code (identifier) of time series will be appended to the
        respective outputfilename before the suffix for csv-files or will be
        use to name the different worksheets for excel files.

    column applies only when separated is False and the filename has a suffix
        .xls or .xlsx
    """
    if filename.endswith('.csv'):
        if not os.path.isdir(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))
        to_csv(df, filename, start_row, separated)
    elif filename.endswith('.xls') or filename.endswith('.xlsx'):
        if not os.path.isdir(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))
        to_excel(df, filename, start_row, separated, column)
    else:
        raise Exception('write_time_series(): unknown file format {}'.format(filename))


def to_csv(df, filename, start_row=None, separated=True):
    if start_row:
        df = df.iloc[start_row:]
    if separated:
        prefix = filename('.csv') + '_'
        for col in df.columns:
            df0 = df[col]
            df0 = pd.DataFrame(df0, columns=[col])
            df0.to_csv(path_or_buf=prefix + col + '.csv', sep=';', index_label='Date', date_format='%Y-%m-%d %H:%M', float_format='%0.2f')
    else:
        df.to_csv(path_or_buf=filename, sep=';', index_label='Date', date_format='%Y-%m-%d %H:%M', float_format='%0.2f')


def to_excel(df, filename, start_row, separated=True, column=None):
    if start_row:
        df = df.iloc[start_row:]
    writer = pd.ExcelWriter(filename)
    if column:
        assert column in df.columns
        df[column].to_excel(writer,column)
    if separated:
        for col in df.columns:
            df0 = df[col]
            df0 = pd.DataFrame(df0, columns=[col])
            df0.to_excel(writer,col)
    else:
        df.to_excel(writer, 'TS')
    writer.save()


# =============================================================================
# Slicing
# =============================================================================
def slice_by_datetime(df, beg_datetime=pd.Timestamp.min, end_datetime=pd.Timestamp.max):
    return df.ix[df.index.searchsorted(beg_datetime):df.index.searchsorted(end_datetime)]


def slice_to_full_years(df, beg_month=1, beg_day=1, beg_hour=0, beg_min=0, beg_sec=0, beg_ms=0):
    try:  # DataFrame
        ts0 = df.index[0].dt
        ts1 = df.index[-1].dt
    except AttributeError, e:  # Series
        ts0 = df.index[0]
        ts1 = df.index[-1]
    rd = relativedelta(microseconds=-1)
    beg_ts = pd.Timestamp(datetime(ts0.year, beg_month, beg_day, beg_hour, beg_min, beg_sec, beg_ms))
    end_ts = pd.Timestamp(datetime(ts1.year, beg_month, beg_day, beg_hour, beg_min, beg_sec, beg_ms) + rd)
    if beg_ts < ts0:
        beg_ts = pd.Timestamp(datetime(ts0.year+1, beg_month, beg_day, beg_hour, beg_min, beg_sec, beg_ms))
    if end_ts > ts1:
        end_ts = pd.Timestamp(datetime(ts1.year-1, beg_month, beg_day, beg_hour, beg_min, beg_sec, beg_ms) + rd)
    return df.ix[df.index.searchsorted(beg_ts):df.index.searchsorted(end_ts)]


def get_n_monthly_data(sr, months=range(1, 13), n=1, how='sum'):
    """
    :param sr: Series
    :param months: list of months, e.g. [11, 12, 1, 2, 3]
    :param n: number of months to aggregate: 1, 2, 3, 4, or 6. Default: n=1
    :return: pandas.DataFrame with n-monthly values 'M' for each year
    """
    assert n in [1, 2, 3, 4, 6]
    sr = slice_to_full_years(sr, beg_month=(months[0]-n) % 12 + 1)
    sr = sr.resample('M', how='sum')
    if n > 1:
        sr = sr.resample(str(n) + 'M', how=how, closed='left', loffset='-1M')
        sr.index = [t + relativedelta(months=+(n-1)) for t in sr.index]
    return sr


def split_monthly_data_annualy(sr, months=range(1, 13), n=1, prefix='M'):
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


def split_annualy(df, beg_datetime=None, end_datetime=None):
    """
    Returns a dictionary with (initial_datetime, final_datetime) as key and the data frame with from the corresponding
        year as value.

    beg_datetime: datetime to start the first split.

    end_datetime: datetime to finish the last split (the last row may include end_datetime).

    The slices start at beg_datetime and repeat each year at the same month, day, hour, minute, and microsecond as
    defined in beg_datetime.

    The slices upper limits correspond to the month, day, hour, minute, and microsecond as defined in end_datetime

    If month, day, hour, minute, and microsecond in end_datetime are less then those defined in beg_datetime, then the
    slices upper limits will fall in the next year. Example:
    beg_datetime=datetime(2000,10,1), end_datetime=datetime(2003,3,31)
    1. slice key: datetime(2000,10,1) to datetime(2001,3,31)
    2. slice key: datetime(2001,10,1) to datetime(2002,3,31)
    3. slice key: datetime(2002,10,1) to datetime(2003,3,31)
    """
    df_dict = {}
    if df is None:
        return df_dict

    df.sort_index(inplace=True)

    first_datetime = df.first_valid_index()
    last_datetime = df.last_valid_index()

    if first_datetime is None:
        return df_dict

    first_year = first_datetime.year

    if beg_datetime is None:
        beg_datetime = datetime(first_year, 1, 1)

    if end_datetime is None:
        end_datetime = beg_datetime + relativedelta(years=1, microseconds=-1)

    beg_dt, end_dt = get_annually_begin_and_end_datetime(beg_datetime, end_datetime, first_year)

    while end_dt <= last_datetime:
        df_dict[(beg_dt, end_dt)] = df.ix[df.index.searchsorted(beg_dt):df.index.searchsorted(end_dt)]
        beg_dt += relativedelta(years=1)
        end_dt += relativedelta(years=1)

    return df_dict


def get_annually_begin_and_end_datetime(beg_datetime, end_datetime, year=None):
    if not year:
        year = beg_datetime.year
    try:
        same_year = beg_datetime < end_datetime.replace(year=beg_datetime.year)
    except ValueError:  # day is out of range for month = 29.02
        same_year = beg_datetime < end_datetime.replace(year=beg_datetime.year, day=28)
    try:
        beg_dt = beg_datetime.replace(year=year)
    except ValueError:  # day is out of range for month = 29.02
        beg_dt = beg_datetime.replace(year=year, day=28)
    try:
        end_dt = end_datetime.replace(year=year if same_year else year + 1)
    except ValueError:  # day is out of range for month = 29.02
        end_dt = end_datetime.replace(year=year if same_year else year + 1, day=28)
    return beg_dt, end_dt


# =============================================================================
# Statistics
# =============================================================================
def create_gap_statistics(df, beg_datetime, end_datetime, frequency='D'):
    """Return a data frame with the number of i-days gaps: number of 1-day gaps, number of 2-days gaps, etc. Starts from
    """
    df = df.reindex(index=pd.date_range(beg_datetime, end_datetime, freq=frequency), method='pad')
    sl = []
    for c in df.columns:
        s = df[c].isnull().astype(int).groupby(df[c].notnull().astype(int).cumsum()).sum().value_counts()
        s.name = str(c)
        sl.append(s)
    df = pd.concat(sl, axis=1)
    df.index.name = 'Consecutive gaps'
    return pd.concat(sl, axis=1)


def create_annual_statistics(df, beg_datetime, end_datetime, frequency='D', stat=np.sum,
                             gaps=True, isnull=True, zeros=True, greaterthenzero=True):
    def func_isnull(row):
        return sum(row.index * row.values)

    dfa_dict = split_annualy(df, beg_datetime, end_datetime)
    dfg_list = []
    dfs_list = []
    dfn_list = []
    dfz_list = []
    dfp_list = []
    for k in sorted(dfa_dict.keys()):
        dfa = dfa_dict[k]
        year_str = str(k[0].year)
        if stat:
            dfs = dfa.apply(stat, axis=0)
            dfs.name = year_str
            dfs_list.append(dfs)
        if gaps or isnull:
            dfg = create_gap_statistics(dfa, k[0], k[1], frequency)
            if isnull:
                dfn = dfg.apply(func_isnull).apply(stat, axis=0)
                dfn.name = year_str
                dfn_list.append(dfn)
            dfg.columns = [cn + ' (' + year_str + ')' for cn in dfg.columns]
            dfg_list.append(dfg)
        if zeros:
            dfz = (dfa == 0.0).apply(stat, axis=0)
            dfz.name = year_str
            dfz_list.append(dfz)
        if greaterthenzero:
            dfp = (dfa > 0.0).apply(stat, axis=0)
            dfp.name = year_str
            dfp_list.append(dfp)
    dfn = None
    if dfn_list:
        dfn = pd.DataFrame(dfn_list[0]).transpose()
        for i in range(1, len(dfn_list)):
            dfn = dfn.append(pd.DataFrame(dfn_list[i]).transpose())
        dfn = pd.DataFrame(dfn)

    dfg = pd.concat(dfg_list, axis=1).transpose() if dfg_list else None
    dfs = pd.concat(dfs_list, axis=1).transpose() if dfs_list else None
    dfz = pd.concat(dfz_list, axis=1).transpose() if dfz_list else None
    dfp = pd.concat(dfp_list, axis=1).transpose() if dfp_list else None
    return dfg, dfs, dfn, dfz, dfp


def create_annual_precipitation_statistics(filenames_in, filename_out, beg_datetime, end_datetime, frequency='D', precipitation_column_name=None):
    def _precipitation_column_name(filename):
        fn = os.path.splitext(os.path.basename(filename))[0]
        return 'P' + fn.split('_')[0]
    if precipitation_column_name is None:
        precipitation_column_name = _precipitation_column_name

    beg_dt, end_dt = get_annually_begin_and_end_datetime(beg_datetime, end_datetime)
    dt = end_dt-beg_dt
    if frequency == 'D':
        max_value = dt.days + 1
    elif frequency == 'H':
        max_value = int(dt.days * 24 + dt.seconds / 3600.0) + 1
    elif frequency == 'T':  # minutely
        max_value = int(dt.days * 1440 + dt.seconds / 60.0) + 1
    dfg_list = []
    dfs_list = []
    dfn_list = []
    dfz_list = []
    dfp_list = []
    for filename in filenames_in:
        print filename
        df = read_time_series(filename)
        dfg, dfs, dfn, dfz, dfp = create_annual_statistics(df, beg_datetime, end_datetime, frequency, stat=np.sum,
                                                           gaps=True, isnull=True, zeros=True, greaterthenzero=True)
        if dfg is not None:
            dfg_list.append(dfg)
        if dfs is not None:
            dfs.columns = [precipitation_column_name(filename).decode('latin-1').encode('utf-8')]
            dfs_list.append(dfs)
        if dfn is not None:
            dfn_list.append(dfn)
        if dfz is not None:
            dfz_list.append(dfz)
        if dfp is not None:
            dfp_list.append(dfp)

    writer = None
    for dfg in dfg_list:
        if dfg is not None:
            if writer is None:
                f_out = splitext(filename_out)[0] + '_gaps.xlsx'
                d_out = dirname(f_out)
                if not os.path.isdir(d_out):
                    os.makedirs(d_out)
                writer = ExcelWriter(f_out, engine='xlsxwriter')
            dfg.to_excel(writer, dfg.index[0].split()[0])
    if writer is not None:
        writer.save()

    dfs = pd.concat(dfs_list, axis=1) if dfs_list else None
    dfn = pd.concat(dfn_list, axis=1) if dfn_list else None
    dfz = pd.concat(dfz_list, axis=1) if dfz_list else None
    dfp = pd.concat(dfp_list, axis=1) if dfp_list else None

    print dfs
    writer = ExcelWriter(filename_out, engine='xlsxwriter')

    def write_excel(wrt, dfw, name, min_value, max_value, invert=False):
        if dfw is None:
            return
        dfw.to_excel(wrt, name)
        minc, midc, maxc = ('#66CC66', '#FFFF99', '#C03010') if invert else ('#C03010', '#FFFF99', '#66CC66')
        param = {'type': '3_color_scale', 'min_value': min_value, 'max_value': max_value,
                 'min_color': minc, 'mid_color': midc, 'max_color': maxc}
        wrt.sheets[name].conditional_format(1, 1, len(dfw) + 1, len(dfw.columns) + 1, param)

    write_excel(writer, dfs, 'Sum', 0, max_value, invert=False)
    write_excel(writer, dfn, 'Gaps', 0, max_value, invert=True)
    write_excel(writer, dfz, 'Zeros', 0, max_value, invert=False)
    write_excel(writer, dfp, 'Greater than zero', 0, max_value, invert=False)
    writer.save()


# =============================================================================
# Others
# =============================================================================
def drop_date_duplicates(df):
    index = df.index.name
    return df.reset_index().drop_duplicates(subset=index, inplace=False).set_index(index)


# def round(df, decimals):
#     return np.around(df, decimals)
#

# def create_rainfall_statistics(time_series_filename, output_filename, from_to):
#     """
#     Calculate the rainfall statistics on a yearly basis for the given intervals
#         in the list from_to and save it in the file in output filename
#     """
#     ts_list = read_time_series(time_series_filename)
#     create_annual_rainfall_statistics(ts_list, output_filename, from_to)


# def create_annual_rainfall_statistics(ts_list, xls_filename, from_to):
#     book = get_xlwt_workbook()
#     insert_into_worksheet_xls(book, 'annual rainfall', ts_list)
#     station_statistics = get_operation_statistics(ts_list)
#     write_operation_statistics_xls(book, station_statistics)
#     for beg_datetime, end_datetime in from_to:
#         write_annual_statistics_xls(book, ts_list, 'sum', beg_datetime, end_datetime)
#     for beg_datetime, end_datetime in from_to:
#         insert_station_aggregated_values_for_arcgis_xls(book, ts_list, 'sum', beg_datetime, end_datetime)
#     book.save(xls_filename)



