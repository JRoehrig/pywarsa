__author__ = 'roehrig'

from warsa.precipitation.observed import CDCHistorical


class CDCObservationsGermanyClimateHourlySoilTemperatureHistorical(CDCHistorical):

    def __init__(self, local_root_dir):
        super(CDCObservationsGermanyClimateHourlySoilTemperatureHistorical, self).__init__(
            local_root_dir,
            'observations_germany/climate/hourly/soil_temperature/historical/',
            'EB_Stundenwerte_Beschreibung_Stationen.txt')




