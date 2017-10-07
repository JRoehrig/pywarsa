__author__ = 'roehrig'

from warsa.precipitation.observed import CDCHistorical


class CDCObservationsGermanyClimateDailySoilTemperatureHistorical(CDCHistorical):

    def __init__(self, local_root_dir):
        super(CDCObservationsGermanyClimateDailySoilTemperatureHistorical, self).__init__(
            local_root_dir,
            'observations_germany/climate/daily/soil_temperature/historical/',
            'EB_Tageswerte_Beschreibung_Stationen.txt'
        )

