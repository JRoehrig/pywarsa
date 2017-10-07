__author__ = 'roehrig'

from warsa.precipitation.observed import CDCRecent


class CDCObservationsGermanyClimateMonthlyMorePrecipRecent(CDCRecent):

    def __init__(self, local_root_dir):
        super(CDCObservationsGermanyClimateMonthlyMorePrecipRecent, self).__init__(
            local_root_dir,
            'observations_germany/climate/monthly/more_precip/recent/',
            'RR_Monatswerte_Beschreibung_Stationen.txt')




