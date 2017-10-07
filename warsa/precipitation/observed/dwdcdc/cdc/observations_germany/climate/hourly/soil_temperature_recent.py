__author__ = 'roehrig'

from warsa.precipitation.observed import CDCRecent


class CDCObservationsGermanyClimateHourlySoilTemperatureRecent(CDCRecent):

    def __init__(self, local_root_dir):
        super(CDCObservationsGermanyClimateHourlySoilTemperatureRecent, self).__init__(
            local_root_dir,
            'observations_germany/climate/hourly/soil_temperature/recent/',
            'EB_Stundenwerte_Beschreibung_Stationen.txt')




