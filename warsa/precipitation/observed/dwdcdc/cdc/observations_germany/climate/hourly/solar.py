__author__ = 'roehrig'

from warsa.precipitation.observed import CDCRecent


class CDCObservationsGermanyClimateHourlySolar(CDCRecent):

    def __init__(self, local_root_dir):
        super(CDCObservationsGermanyClimateHourlySolar, self).__init__(
            local_root_dir,
            'observations_germany/climate/hourly/solar/',
            'ST_Beschreibung_Stationen.txt'
        )
