__author__ = 'roehrig'

from warsa.precipitation.observed import CDCRecent


class CDCObservationsGermanyClimateDailyMorePrecipRecent(CDCRecent):

    def __init__(self, local_root_dir):
        super(CDCObservationsGermanyClimateDailyMorePrecipRecent, self).__init__(
            local_root_dir,
            'observations_germany/climate/daily/more_precip/recent/',
            'RR_Tageswerte_Beschreibung_Stationen.txt'
        )

