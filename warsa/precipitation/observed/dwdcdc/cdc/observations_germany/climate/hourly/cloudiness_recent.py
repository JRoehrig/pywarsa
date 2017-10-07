__author__ = 'roehrig'

from warsa.precipitation.observed import CDCRecent


class CDCObservationsGermanyClimateHourlyCloudinessRecent(CDCRecent):

    def __init__(self, local_root_dir):
        super(CDCObservationsGermanyClimateHourlyCloudinessRecent, self).__init__(
            local_root_dir,
            'observations_germany/climate/hourly/cloudiness/recent/',
            'N_Stundenwerte_Beschreibung_Stationen.txt')




