__author__ = 'roehrig'

from warsa.precipitation.observed import CDCHistorical


class CDCObservationsGermanyClimateMonthlyKLHistorical(CDCHistorical):

    def __init__(self, local_root_dir):
        super(CDCObservationsGermanyClimateMonthlyKLHistorical, self).__init__(
            local_root_dir,
            'observations_germany/climate/monthly/kl/historical/',
            'KL_Monatswerte_Beschreibung_Stationen.txt', sid_idx=1, beg_idx=2, end_idx=3)


