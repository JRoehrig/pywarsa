__author__ = 'roehrig'

from warsa.precipitation.observed import CDCHistorical


class CDCObservationsGermanyClimateDailyKLHistorical(CDCHistorical):

    def __init__(self, local_root_dir):
        super(CDCObservationsGermanyClimateDailyKLHistorical, self).__init__(
            local_root_dir,
            'observations_germany/climate/daily/kl/historical/',
            'KL_Tageswerte_Beschreibung_Stationen.txt', sid_idx=1, beg_idx=2, end_idx=3)

