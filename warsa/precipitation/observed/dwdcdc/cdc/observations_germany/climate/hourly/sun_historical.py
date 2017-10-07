__author__ = 'roehrig'

from warsa.precipitation.observed import CDCHistorical


class CDCObservationsGermanyClimateHourlySunHistorical(CDCHistorical):

    def __init__(self, local_root_dir):
        super(CDCObservationsGermanyClimateHourlySunHistorical, self).__init__(
            local_root_dir,
            'observations_germany/climate/hourly/sun/historical/',
            'SD_Stundenwerte_Beschreibung_Stationen.txt')

