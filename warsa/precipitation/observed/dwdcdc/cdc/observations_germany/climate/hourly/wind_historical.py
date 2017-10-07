__author__ = 'roehrig'

from warsa.precipitation import CDCHistorical


class CDCObservationsGermanyClimateHourlyWindHistorical(CDCHistorical):

    def __init__(self, local_root_dir):
        super(CDCObservationsGermanyClimateHourlyWindHistorical, self).__init__(
            local_root_dir,
            'observations_germany/climate/hourly/wind/historical/',
            'FF_Stundenwerte_Beschreibung_Stationen.txt')

