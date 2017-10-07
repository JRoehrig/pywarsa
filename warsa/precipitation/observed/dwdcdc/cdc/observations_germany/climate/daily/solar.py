__author__ = 'roehrig'

from warsa.precipitation.observed import CDCRecent


class CDCObservationsGermanyClimateDailySolar(CDCRecent):

    def __init__(self, local_root_dir):
        super(CDCObservationsGermanyClimateDailySolar, self).__init__(
            local_root_dir,
            'observations_germany/climate/daily/solar/',
            'ST_Beschreibung_Stationen.txt'
        )


