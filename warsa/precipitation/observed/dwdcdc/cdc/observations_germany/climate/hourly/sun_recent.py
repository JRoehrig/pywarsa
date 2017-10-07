__author__ = 'roehrig'

from warsa.precipitation.observed import CDCRecent


class CDCObservationsGermanyClimateHourlySunRecent(CDCRecent):

    def __init__(self, local_root_dir):
        super(CDCObservationsGermanyClimateHourlySunRecent, self).__init__(
            local_root_dir,
            'observations_germany/climate/hourly/sun/recent/',
            'SD_Stundenwerte_Beschreibung_Stationen.txt')

