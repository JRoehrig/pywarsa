__author__ = 'roehrig'

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
from precipytation.observed.dwdcdc.cdc.observations_germany.climate.hourly.precipitation_historical import \
    CDCObservationsGermanyClimateHourlyPrecipitationHistorical
from precipytation.observed.dwdcdc.cdc.observations_germany.climate.hourly.precipitation_recent import \
    CDCObservationsGermanyClimateHourlyPrecipitationRecent
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
from precipytation.observed.dwdcdc.cdc.observations_germany.climate.multi_annual.cdc_multi_annual import \
    CDCObservationsGermanyClimateMultiAnnual19611990, CDCObservationsGermanyClimateMultiAnnual19712000, \
    CDCObservationsGermanyClimateMultiAnnual19812010

from warsa.precipitation.observed.dwdcdc.cdc.observations_germany.climate.daily.soil_temperature_historical import \
    CDCObservationsGermanyClimateDailySoilTemperatureHistorical


def download_historical(local_dir):
    local_dir = create_dir(local_dir)
    CDCObservationsGermanyClimateDailyKLHistorical(local_dir).download()
    CDCObservationsGermanyClimateDailyMorePrecipHistorical(local_dir).download()
    CDCObservationsGermanyClimateDailySoilTemperatureHistorical(local_dir).download()
    CDCObservationsGermanyClimateHourlyAirTemperatureHistorical(local_dir).download()
    CDCObservationsGermanyClimateHourlyCloudinessHistorical(local_dir).download()
    CDCObservationsGermanyClimateHourlyPrecipitationHistorical(local_dir).download()
    CDCObservationsGermanyClimateHourlyPressureHistorical(local_dir).download()
    CDCObservationsGermanyClimateHourlySoilTemperatureHistorical(local_dir).download()
    CDCObservationsGermanyClimateHourlySunHistorical(local_dir).download()
    CDCObservationsGermanyClimateHourlyWindHistorical(local_dir).download()
    CDCObservationsGermanyClimateMonthlyKLHistorical(local_dir).download()
    CDCObservationsGermanyClimateMonthlyMorePrecipHistorical(local_dir).download()


def download_recent(local_dir):
    local_dir = create_dir(local_dir)
    CDCObservationsGermanyClimateDailyKLRecent(local_dir).download()
    CDCObservationsGermanyClimateDailyMorePrecipRecent(local_dir).download()
    CDCObservationsGermanyClimateDailySoilTemperatureRecent(local_dir).download()
    CDCObservationsGermanyClimateDailySolar(local_dir).download()
    CDCObservationsGermanyClimateHourlyAirTemperatureRecent(local_dir).download()
    CDCObservationsGermanyClimateHourlyCloudinessRecent(local_dir).download()
    CDCObservationsGermanyClimateHourlyPrecipitationRecent(local_dir).download()
    CDCObservationsGermanyClimateHourlyPressureRecent(local_dir).download()
    CDCObservationsGermanyClimateHourlySoilTemperatureRecent(local_dir).download()
    CDCObservationsGermanyClimateHourlySolar(local_dir).download()
    CDCObservationsGermanyClimateHourlySunRecent(local_dir).download()
    CDCObservationsGermanyClimateHourlyWindRecent(local_dir).download()
    CDCObservationsGermanyClimateMonthlyKLRecent(local_dir).download()
    CDCObservationsGermanyClimateMonthlyMorePrecipRecent(local_dir).download()


def download_multi_annual(local_dir):
    local_dir = create_dir(local_dir)
    CDCObservationsGermanyClimateMultiAnnual19611990(local_dir).download()
    CDCObservationsGermanyClimateMultiAnnual19712000(local_dir).download()
    CDCObservationsGermanyClimateMultiAnnual19812010(local_dir).download()


def download_all(local_dir):
    local_dir = create_dir(local_dir)
    download_multi_annual(local_dir)
    download_historical(local_dir)
    download_recent(local_dir)


def download_historical_and_recent(local_dir):
    local_dir = create_dir(local_dir)
    download_historical(local_dir)
    download_recent(local_dir)


