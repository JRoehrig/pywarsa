__author__ = 'roehrig'

from warsa.precipitation.observed import CDCHistorical


class CDCObservationsGermanyClimateHourlyAirTemperatureHistorical(CDCHistorical):

    def __init__(self, local_root_dir):
        super(CDCObservationsGermanyClimateHourlyAirTemperatureHistorical, self).__init__(
            local_root_dir,
            'observations_germany/climate/hourly/air_temperature/historical/',
            'TU_Stundenwerte_Beschreibung_Stationen.txt')

