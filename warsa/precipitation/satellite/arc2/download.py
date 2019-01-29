import os
import datetime
from warsa.precipitation.satellite.download import SatelliteBasedPrecipitationDownloadFTP


class ARC2AfricaBinFTP(SatelliteBasedPrecipitationDownloadFTP):
    """Source:
        ftp://ftp.cpc.ncep.noaa.gov/fews/fewsdata/africa/arc2/bin/
    Format:
        daily_clim.bin.19830101.gz
    """
    def __init__(self, local_dir):
        super(ARC2AfricaBinFTP, self).__init__(local_dir, 'daily_clim.bin.', '.gz', None,
                                               'ftp.cpc.ncep.noaa.gov', '/fews/fewsdata/africa/arc2/bin/')

    @staticmethod
    def get_datetime_from_file_name(filename):
        return datetime.datetime.strptime(filename.split('.')[-2], '%Y%m%d')


class ARC2AfricaTifFTP(SatelliteBasedPrecipitationDownloadFTP):
    """Source:
        ftp://ftp.cpc.ncep.noaa.gov//fews/fewsdata/africa/arc2/geotiff/
    Format:
        africa_arc.19830101.tif.zip
    """
    def __init__(self, local_dir):
        super(ARC2AfricaTifFTP, self).__init__(local_dir, 'africa_arc.', '.tif.zip', None,
                                               'ftp.cpc.ncep.noaa.gov', '/fews/fewsdata/africa/arc2/geotiff/')

    @staticmethod
    def get_datetime_from_file_name(filename):
        return datetime.datetime.strptime(filename.split('.')[-3], '%Y%m%d')


