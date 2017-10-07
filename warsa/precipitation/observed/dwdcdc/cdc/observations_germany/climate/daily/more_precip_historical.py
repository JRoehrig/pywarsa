__author__ = 'roehrig'

from warsa.precipitation.observed import CDCHistorical


class CDCObservationsGermanyClimateDailyMorePrecipHistorical(CDCHistorical):

    def __init__(self, local_root_dir):
        super(CDCObservationsGermanyClimateDailyMorePrecipHistorical, self).__init__(
            local_root_dir,
            'observations_germany/climate/daily/more_precip/historical/',
            'RR_Tageswerte_Beschreibung_Stationen.txt')



