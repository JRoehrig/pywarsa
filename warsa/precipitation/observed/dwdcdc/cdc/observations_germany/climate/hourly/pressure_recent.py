__author__ = 'roehrig'

from warsa.precipitation.observed import CDCRecent


class CDCObservationsGermanyClimateHourlyPressureRecent(CDCRecent):

    def __init__(self, local_root_dir):
        super(CDCObservationsGermanyClimateHourlyPressureRecent, self).__init__(
            local_root_dir,
            'observations_germany/climate/hourly/pressure/recent/',
            'P0_Stundenwerte_Beschreibung_Stationen.txt')




