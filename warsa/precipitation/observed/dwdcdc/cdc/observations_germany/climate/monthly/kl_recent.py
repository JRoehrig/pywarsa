__author__ = 'roehrig'

from warsa.precipitation.observed import CDCRecent


class CDCObservationsGermanyClimateMonthlyKLRecent(CDCRecent):

    def __init__(self, local_root_dir):
        super(CDCObservationsGermanyClimateMonthlyKLRecent, self).__init__(
            local_root_dir,
            'observations_germany/climate/monthly/kl/recent/',
            'KL_Monatswerte_Beschreibung_Stationen.txt', sid_idx=1)

