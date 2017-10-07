__author__ = 'roehrig'

from warsa.precipitation.observed import CDCRecent


class CDCObservationsGermanyClimateHourlyWindRecent(CDCRecent):

    def __init__(self, local_root_dir):
        super(CDCObservationsGermanyClimateHourlyWindRecent, self).__init__(
            local_root_dir,
            'observations_germany/climate/hourly/wind/recent/',
            'FF_Stundenwerte_Beschreibung_Stationen.txt')

