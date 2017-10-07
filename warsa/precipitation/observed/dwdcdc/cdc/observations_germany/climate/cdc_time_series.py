__author__ = 'roehrig'

import os

import numpy as np
import pandas as pd
from precipytation.observed.dwdcdc import \
    CDCObservationsGermanyClimateHourlyCloudinessHistorical
from precipytation.observed.dwdcdc.cdc.observations_germany.climate.cdc_climate import create_dir
from precipytation.observed.dwdcdc.cdc.observations_germany.climate.daily.kl_historical import \
    CDCObservationsGermanyClimateDailyKLHistorical
from precipytation.observed.dwdcdc.cdc.observations_germany.climate.daily.kl_recent import \
    CDCObservationsGermanyClimateDailyKLRecent
from precipytation.observed.dwdcdc.cdc.observations_germany.climate.daily.more_precip_historical import \
    CDCObservationsGermanyClimateDailyMorePrecipHistorical
from precipytation.observed.dwdcdc.cdc.observations_germany.climate.daily.more_precip_recent import \
    CDCObservationsGermanyClimateDailyMorePrecipRecent
from precipytation.observed.dwdcdc.cdc.observations_germany.climate.daily.soil_temperature_recent import \
    CDCObservationsGermanyClimateDailySoilTemperatureRecent
from precipytation.observed.dwdcdc.cdc.observations_germany.climate.daily.solar import \
    CDCObservationsGermanyClimateDailySolar
from precipytation.observed.dwdcdc.cdc.observations_germany.climate.hourly.air_temperature_historical import \
    CDCObservationsGermanyClimateHourlyAirTemperatureHistorical
from precipytation.observed.dwdcdc.cdc.observations_germany.climate.hourly.air_temperature_recent import \
    CDCObservationsGermanyClimateHourlyAirTemperatureRecent
from precipytation.observed.dwdcdc.cdc.observations_germany.climate.hourly.cloudiness_recent import \
    CDCObservationsGermanyClimateHourlyCloudinessRecent
from precipytation.observed.dwdcdc.cdc.observations_germany.climate.hourly.pressure_historical import \
    CDCObservationsGermanyClimateHourlyPressureHistorical
from precipytation.observed.dwdcdc.cdc.observations_germany.climate.hourly.pressure_recent import \
    CDCObservationsGermanyClimateHourlyPressureRecent
from precipytation.observed.dwdcdc.cdc.observations_germany.climate.hourly.soil_temperature_historical import \
    CDCObservationsGermanyClimateHourlySoilTemperatureHistorical
from precipytation.observed.dwdcdc.cdc.observations_germany.climate.hourly.soil_temperature_recent import \
    CDCObservationsGermanyClimateHourlySoilTemperatureRecent
from precipytation.observed.dwdcdc.cdc.observations_germany.climate.hourly.solar import \
    CDCObservationsGermanyClimateHourlySolar
from precipytation.observed.dwdcdc.cdc.observations_germany.climate.hourly.sun_historical import \
    CDCObservationsGermanyClimateHourlySunHistorical
from precipytation.observed.dwdcdc.cdc.observations_germany.climate.hourly.sun_recent import \
    CDCObservationsGermanyClimateHourlySunRecent
from precipytation.observed.dwdcdc.cdc.observations_germany.climate.hourly.wind_historical import \
    CDCObservationsGermanyClimateHourlyWindHistorical
from precipytation.observed.dwdcdc.cdc.observations_germany.climate.hourly.wind_recent import \
    CDCObservationsGermanyClimateHourlyWindRecent
from precipytation.observed.dwdcdc.cdc.observations_germany.climate.monthly.kl_historical import \
    CDCObservationsGermanyClimateMonthlyKLHistorical
from precipytation.observed.dwdcdc.cdc.observations_germany.climate.monthly.kl_recent import \
    CDCObservationsGermanyClimateMonthlyKLRecent
from precipytation.observed.dwdcdc.cdc.observations_germany.climate.monthly.more_precip_historical import \
    CDCObservationsGermanyClimateMonthlyMorePrecipHistorical
from precipytation.observed.dwdcdc.cdc.observations_germany.climate.monthly.more_precip_recent import \
    CDCObservationsGermanyClimateMonthlyMorePrecipRecent

from warsa.precipitation.observed.dwdcdc.cdc.observations_germany.climate.daily.soil_temperature_historical import \
    CDCObservationsGermanyClimateDailySoilTemperatureHistorical


def read_all(local_dir, output_dir, station_ids=None):
    read_all_daily(local_dir, output_dir, station_ids)
    read_all_hourly(local_dir, output_dir, station_ids)


def read_all_monthly(local_dir, output_dir, station_ids=None):
    output_dir = create_dir(output_dir)
    CDCObservationsGermanyClimateMonthlyKLHistorical(local_dir).read(os.path.join(output_dir, 'monthly_kl_historical/'), station_ids=station_ids)
    CDCObservationsGermanyClimateMonthlyKLRecent(local_dir).read(os.path.join(output_dir, 'monthly_kl_recent/'), station_ids=station_ids)
    CDCObservationsGermanyClimateMonthlyMorePrecipHistorical(local_dir).read(os.path.join(output_dir, 'monthly_more_precipitation_historical/'), station_ids=station_ids)
    CDCObservationsGermanyClimateMonthlyMorePrecipRecent(local_dir).read(os.path.join(output_dir, 'monthly_more_precipitation_recent/'), station_ids=station_ids)


def read_all_daily(local_dir, output_dir, station_ids=None):
    output_dir = create_dir(output_dir)
    CDCObservationsGermanyClimateDailyKLHistorical(local_dir).read(os.path.join(output_dir, 'daily_kl_historical/'), station_ids=station_ids)
    CDCObservationsGermanyClimateDailyKLRecent(local_dir).read(os.path.join(output_dir, 'daily_kl_recent/'), station_ids=station_ids)
    CDCObservationsGermanyClimateDailyMorePrecipHistorical(local_dir).read(os.path.join(output_dir, 'daily_more_precipitation_historical/'), station_ids=station_ids)
    CDCObservationsGermanyClimateDailyMorePrecipRecent(local_dir).read(os.path.join(output_dir, 'daily_more_precipitation_recent/'), station_ids=station_ids)
    CDCObservationsGermanyClimateDailySoilTemperatureHistorical(local_dir).read(os.path.join(output_dir, 'daily_soil_temperature_historical/'), station_ids=station_ids)
    CDCObservationsGermanyClimateDailySoilTemperatureRecent(local_dir).read(os.path.join(output_dir, 'daily_soil_temperature_recent/'), station_ids=station_ids)
    CDCObservationsGermanyClimateDailySolar(local_dir).read(os.path.join(output_dir, 'daily_solar/'), station_ids=station_ids)


def read_all_hourly(local_dir, output_dir, station_ids=None):
    output_dir = create_dir(output_dir)
    CDCObservationsGermanyClimateHourlyAirTemperatureHistorical(local_dir).read(os.path.join(output_dir, 'hourly_air_temperature_historical/'), station_ids=station_ids)
    CDCObservationsGermanyClimateHourlyAirTemperatureRecent(local_dir).read(os.path.join(output_dir, 'hourly_air_temperature_recent/'), station_ids=station_ids)
    CDCObservationsGermanyClimateHourlyCloudinessHistorical(local_dir).read(os.path.join(output_dir, 'hourly_cloudiness_historical/'), station_ids=station_ids)
    CDCObservationsGermanyClimateHourlyCloudinessRecent(local_dir).read(os.path.join(output_dir, 'hourly_cloudiness_recent/'), station_ids=station_ids)
    CDCObservationsGermanyClimateHourlyPressureHistorical(local_dir).read(os.path.join(output_dir, 'hourly_pressure_historical/'), station_ids=station_ids)
    CDCObservationsGermanyClimateHourlyPressureRecent(local_dir).read(os.path.join(output_dir, 'hourly_pressure_recent/'), station_ids=station_ids)
    CDCObservationsGermanyClimateHourlySoilTemperatureHistorical(local_dir).read(os.path.join(output_dir, 'hourly_soil_temperature_historical/'), station_ids=station_ids)
    CDCObservationsGermanyClimateHourlySoilTemperatureRecent(local_dir).read(os.path.join(output_dir, 'hourly_soil_temperature_recent/'), station_ids=station_ids)
    CDCObservationsGermanyClimateHourlySolar(local_dir).read(os.path.join(output_dir, 'hourly_solar/'), station_ids=station_ids)
    CDCObservationsGermanyClimateHourlySunHistorical(local_dir).read(os.path.join(output_dir, 'hourly_sun_historical/'), station_ids=station_ids)
    CDCObservationsGermanyClimateHourlySunRecent(local_dir).read(os.path.join(output_dir, 'hourly_sun_recent/'), station_ids=station_ids)
    CDCObservationsGermanyClimateHourlyWindHistorical(local_dir).read(os.path.join(output_dir, 'hourly_wind_historical/'), station_ids=station_ids)
    CDCObservationsGermanyClimateHourlyWindRecent(local_dir).read(os.path.join(output_dir, 'hourly_wind_recent/'), station_ids=station_ids)


def read_monthly_precipitation(local_dir, output_dir, fd='NIEDERSCHLAGSHOEHE', station_ids=None):
    read_monthly_precipitation_recent(local_dir, output_dir, fd, station_ids)
    read_monthly_precipitation_historical(local_dir, output_dir, fd, station_ids)


def read_monthly_precipitation_historical(local_dir, output_dir, fd='NIEDERSCHLAGSHOEHE', station_ids=None):
    output_dir = create_dir(output_dir)
    CDCObservationsGermanyClimateMonthlyKLHistorical(local_dir).read(os.path.join(output_dir, 'monthly_kl_historical/'), fd, station_ids=station_ids)
    CDCObservationsGermanyClimateMonthlyMorePrecipHistorical(local_dir).read(os.path.join(output_dir, 'monthly_more_precipitation_historical/'), fd, station_ids=station_ids)


def read_monthly_precipitation_recent(local_dir, output_dir, fd='NIEDERSCHLAGSHOEHE', station_ids=None):
    output_dir = create_dir(output_dir)
    CDCObservationsGermanyClimateMonthlyKLRecent(local_dir).read(os.path.join(output_dir, 'monthly_kl_recent/'), fd, station_ids=station_ids)
    CDCObservationsGermanyClimateMonthlyMorePrecipRecent(local_dir).read(os.path.join(output_dir, 'monthly_more_precipitation_recent/'), fd, station_ids=station_ids)

def read_daily_precipitation(local_dir, output_dir, fd='NIEDERSCHLAGSHOEHE', station_ids=None):
    read_daily_precipitation_recent(local_dir, output_dir, fd, station_ids)
    read_daily_precipitation_historical(local_dir, output_dir, fd, station_ids)


def read_daily_precipitation_historical(local_dir, output_dir, fd='NIEDERSCHLAGSHOEHE', station_ids=None):
    output_dir = create_dir(output_dir)
    CDCObservationsGermanyClimateDailyKLHistorical(local_dir).read(os.path.join(output_dir, 'daily_kl_historical/'), fd, station_ids=station_ids)
    CDCObservationsGermanyClimateDailyMorePrecipHistorical(local_dir).read(os.path.join(output_dir, 'daily_more_precipitation_historical/'), fd, station_ids=station_ids)


def read_daily_precipitation_recent(local_dir, output_dir, fd='NIEDERSCHLAGSHOEHE', station_ids=None):
    output_dir = create_dir(output_dir)
    CDCObservationsGermanyClimateDailyKLRecent(local_dir).read(os.path.join(output_dir, 'daily_kl_recent/'), fd, station_ids=station_ids)
    CDCObservationsGermanyClimateDailyMorePrecipRecent(local_dir).read(os.path.join(output_dir, 'daily_more_precipitation_recent/'), fd, station_ids=station_ids)


def merge_precipitation(input_dirs, output_dir):
    stations = dict()
    output_dir = create_dir(output_dir)
    for in_dir in input_dirs:
        for f_in in [f for f in os.listdir(in_dir) if f.endswith('.csv')]:
            st_id = int(f_in.split('_')[0])
            f_in = os.path.join(in_dir, f_in)
            if st_id not in stations:
                stations[st_id] = [f_in]
            else:
                stations[st_id].append(f_in)
    for filenames in stations.values():
        df = None
        for f in filenames:
            if df is None:
                df = pd.read_csv(f, index_col=0, sep=';', parse_dates=True)
            else:
                df = df.combine_first(pd.read_csv(f, index_col=0, sep=';', parse_dates=True))
        df[df<0] = np.NaN
        df.to_csv(os.path.join(output_dir, os.path.basename(filenames[0])), sep=';')


def merge_hourly_precipitation(input_dirs, output_dir):
    stations = dict()
    output_dir = create_dir(output_dir)
    for in_dir in [os.path.join(input_dirs, f) for f in os.listdir(input_dirs)]:
        for f_in in [ f for f in os.listdir(in_dir) if f.endswith('.csv')]:
            st_id = int(f_in.split('_')[0])
            f_in = os.path.join(in_dir, f_in)
            if st_id not in stations:
                stations[st_id] = [f_in]
            else:
                stations[st_id].append(f_in)
    for filenames in stations.values():
        df = None
        for f in filenames:
            if df is None:
                df = pd.read_csv(f, index_col=0, sep=';', parse_dates=True)
            else:
                df = df.combine_first(pd.read_csv(f, index_col=0, sep=';', parse_dates=True))
        df.to_csv(os.path.join(output_dir, os.path.basename(filenames[0])), sep=';')




