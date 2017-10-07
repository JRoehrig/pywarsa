__author__ = 'roehrig'

from warsa.precipitation.observed import CDCRecent


class CDCObservationsGermanyClimateHourlyPrecipitationRecent(CDCRecent):

    def __init__(self, local_root_dir):
        super(CDCObservationsGermanyClimateHourlyPrecipitationRecent, self).__init__(
            local_root_dir,
            'observations_germany/climate/hourly/precipitation/recent/',
            'RR_Stundenwerte_Beschreibung_Stationen.txt')




