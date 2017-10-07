from cdc_climate import create_dir, CDCObservationsGermanyClimateDailyKLHistorical, CDCObservationsGermanyClimateDailyKLRecent, \
    CDCObservationsGermanyClimateDailyMorePrecipHistorical, CDCObservationsGermanyClimateDailyMorePrecipRecent, \
    CDCObservationsGermanyClimateDailySoilTemperatureHistorical, CDCObservationsGermanyClimateDailySoilTemperatureRecent, \
    CDCObservationsGermanyClimateDailySolar, CDCObservationsGermanyClimateHourlyAirTemperatureHistorical, \
    CDCObservationsGermanyClimateHourlyAirTemperatureRecent, CDCObservationsGermanyClimateHourlyCloudinessHistorical, \
    CDCObservationsGermanyClimateHourlyCloudinessRecent, CDCObservationsGermanyClimateHourlyPrecipitationHistorical, \
    CDCObservationsGermanyClimateHourlyPrecipitationRecent, CDCObservationsGermanyClimateHourlyPressureHistorical, \
    CDCObservationsGermanyClimateHourlyPressureRecent, CDCObservationsGermanyClimateHourlySoilTemperatureHistorical, \
    CDCObservationsGermanyClimateHourlySoilTemperatureRecent, CDCObservationsGermanyClimateHourlySolar, \
    CDCObservationsGermanyClimateHourlySunHistorical, CDCObservationsGermanyClimateHourlySunRecent, \
    CDCObservationsGermanyClimateHourlyWindHistorical, CDCObservationsGermanyClimateHourlyWindRecent, \
    CDCObservationsGermanyClimateMonthlyKLHistorical, CDCObservationsGermanyClimateMonthlyKLRecent, \
    CDCObservationsGermanyClimateMonthlyMorePrecipHistorical, CDCObservationsGermanyClimateMonthlyMorePrecipRecent, \
    CDCObservationsGermanyClimateMultiAnnual19611990, CDCObservationsGermanyClimateMultiAnnual19712000, \
    CDCObservationsGermanyClimateMultiAnnual19812010


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


