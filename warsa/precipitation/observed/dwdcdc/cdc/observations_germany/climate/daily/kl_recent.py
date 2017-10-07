__author__ = 'roehrig'

from warsa.precipitation.observed import CDCRecent


class CDCObservationsGermanyClimateDailyKLRecent(CDCRecent):
    def __init__(self, local_root_dir):
        super(CDCObservationsGermanyClimateDailyKLRecent, self).__init__(
            local_root_dir,
            'observations_germany/climate/daily/kl/recent/',
            'KL_Tageswerte_Beschreibung_Stationen.txt')

