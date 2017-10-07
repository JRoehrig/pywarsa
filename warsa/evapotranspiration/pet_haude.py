# -*- coding: utf-8 -*-
import os
import numpy as np
import pandas as pd


def pet_haude(df, temp_col, hum_col, monthly_factor=None):
    """
    :param df: pandas DataFrame with with at least two columns:
               - temperature in °C
               - relative air humidity in percentage
               both at 2 pm
    :param temp_col: name of the column containing temperature values
    :param hum_col: name of the column containing relative air humidity values
    :param monthly_factor: correction factor for each month (default to Germany)
    :return:
    """
    if not monthly_factor:
        monthly_factor = [0, 0.22, 0.22, 0.22, 0.29, 0.29, 0.28, 0.26, 0.25, 0.23, 0.22, 0.22, 0.22]

    df_haude = pd.Series(6.112 * np.exp((17.62*df[temp_col])/(243.12+df[temp_col])), index=df.index).to_frame('es')
    df_haude['Month'] = df.index.month
    df_haude['Haude_f'] = df_haude['Month'].apply(lambda month: monthly_factor[month])
    df_haude['PET_Haude'] = pd.Series((df_haude['Haude_f'] * df_haude['es'] * (1 - (df[hum_col] / 100.0))),
                                      index=df_haude.index)
    df_haude['PET_Haude'] = df_haude['PET_Haude'].apply(lambda v: v if v < 7.0 else 7.0)
    df_haude = df_haude['PET_Haude']
    df_haude.index.name = 'Date'
    return df_haude


if __name__ == '__main__':
    parser = lambda date: pd.datetime.strptime(date, '%d.%m.%Y %H:%M')
    d_tas = 'D:/tmp/tas_at_13'
    d_hurs = 'D:/tmp/hurs_at_13'
    f_tas = os.path.join(d_tas, 'Wupper_NASIM_mpi-esm-lr-cclm4-8-19-v1_decadal-predictions_r1i1p1-ds2r1e1_20150101-20241231_6.965_51.000_tas_hourly_hourly.csv')
    f_hurs = os.path.join(d_hurs, 'Wupper_NASIM_mpi-esm-lr-cclm4-8-19-v1_decadal-predictions_r1i1p1-ds2r1e1_20150101-20241231_6.965_51.000_hurs_hourly_hourly.csv')
    df_tas = pd.read_csv(f_tas, sep=';', decimal='.', index_col=0, parse_dates=[0], date_parser=parser).apply(lambda t: t -273.15)
    df_hurs = pd.read_csv(f_hurs, sep=';', decimal='.', index_col=0, parse_dates=[0], date_parser=parser)
    df1 = pd.concat([df_tas, df_hurs], axis=1)
    print pet_haude(df1, 'tas', 'hurs')
