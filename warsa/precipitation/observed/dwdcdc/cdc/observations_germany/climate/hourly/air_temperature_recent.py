__author__ = 'roehrig'

from warsa.precipitation.observed import CDCRecent


class CDCObservationsGermanyClimateHourlyAirTemperatureRecent(CDCRecent):

    def __init__(self, local_root_dir):
        super(CDCObservationsGermanyClimateHourlyAirTemperatureRecent, self).__init__(
            local_root_dir,
            'observations_germany/climate/hourly/air_temperature/recent/',
            'TU_Stundenwerte_Beschreibung_Stationen.txt')


