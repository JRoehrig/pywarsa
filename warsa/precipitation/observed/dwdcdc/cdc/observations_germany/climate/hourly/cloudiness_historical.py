__author__ = 'roehrig'

from warsa.precipitation.observed import CDCHistorical


class CDCObservationsGermanyClimateHourlyCloudinessHistorical(CDCHistorical):

    def __init__(self, local_root_dir):
        super(CDCObservationsGermanyClimateHourlyCloudinessHistorical, self).__init__(
            local_root_dir,
            'observations_germany/climate/hourly/cloudiness/historical/',
            'N_Stundenwerte_Beschreibung_Stationen.txt')




