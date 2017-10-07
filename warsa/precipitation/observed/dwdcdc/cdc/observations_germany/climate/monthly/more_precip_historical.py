__author__ = 'roehrig'

from warsa.precipitation.observed import CDCHistorical


class CDCObservationsGermanyClimateMonthlyMorePrecipHistorical(CDCHistorical):

    def __init__(self, local_root_dir):
        super(CDCObservationsGermanyClimateMonthlyMorePrecipHistorical, self).__init__(
            local_root_dir,
            'observations_germany/climate/monthly/more_precip/historical/',
            'RR_Monatswerte_Beschreibung_Stationen.txt')




