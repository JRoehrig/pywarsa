__author__ = 'roehrig'

from warsa.precipitation.observed import CDCRecent


class CDCObservationsGermanyClimateDailySoilTemperatureRecent(CDCRecent):

    def __init__(self, local_root_dir):
        super(CDCObservationsGermanyClimateDailySoilTemperatureRecent, self).__init__(
            local_root_dir,
            'observations_germany/climate/daily/soil_temperature/recent/',
            'EB_Tageswerte_Beschreibung_Stationen.txt'
        )

