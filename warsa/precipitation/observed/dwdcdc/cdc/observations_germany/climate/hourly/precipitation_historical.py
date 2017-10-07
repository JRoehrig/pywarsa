__author__ = 'roehrig'

from warsa.precipitation.observed import CDCHistorical


class CDCObservationsGermanyClimateHourlyPrecipitationHistorical(CDCHistorical):

    def __init__(self, local_root_dir):
        super(CDCObservationsGermanyClimateHourlyPrecipitationHistorical, self).__init__(
            local_root_dir,
            'observations_germany/climate/hourly/precipitation/historical/',
            'RR_Stundenwerte_Beschreibung_Stationen.txt')




