__author__ = 'roehrig'

from warsa.precipitation.observed import CDCHistorical


class CDCObservationsGermanyClimateHourlyPressureHistorical(CDCHistorical):

    def __init__(self, local_root_dir):
        super(CDCObservationsGermanyClimateHourlyPressureHistorical, self).__init__(
            local_root_dir,
            'observations_germany/climate/hourly/pressure/historical/',
            'P0_Stundenwerte_Beschreibung_Stationen.txt')




