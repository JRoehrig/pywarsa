import os
import datetime
from warsa.precipitation.satellite.download import FTPDownload


class RFE2AfricaBinFTP(FTPDownload):
    """Source:
        ftp://ftp.cpc.ncep.noaa.gov/fews/fewsdata/africa/rfe2/bin
    Format:
        all_products.bin.20010101.gz

    """
    def __init__(self, local_dir):
        super(RFE2AfricaBinFTP, self).__init__(local_dir, 'all_products.bin.', '.gz', None,
                                               'ftp.cpc.ncep.noaa.gov', '/fews/fewsdata/africa/rfe2/bin')

    @staticmethod
    def get_datetime_from_file_name(filename):
        return datetime.datetime.strptime(os.path.splitext(filename)[0].split('.')[-1], '%Y%m%d')


class RFE2AfricaTifFTP(FTPDownload):
    """Source:
        ftp://ftp.cpc.ncep.noaa.gov/fews/fewsdata/africa/rfe2/geotiff/
    Format:
        africa_rfe.20010101.tif.zip

    """
    def __init__(self, local_dir):
        super(RFE2AfricaTifFTP, self).__init__(local_dir, 'africa_rfe.', '.tif.zip', None,
                                               'ftp.cpc.ncep.noaa.gov', '/fews/fewsdata/africa/rfe2/geotiff')

    @staticmethod
    def get_datetime_from_file_name(filename):
        return datetime.datetime.strptime(os.path.splitext(os.path.basename(filename))[0].split('.')[1], '%Y%m%d')


class RFE2AsiaBinFTP(FTPDownload):

    def __init__(self, local_dir):
        super(RFE2AsiaBinFTP, self).__init__(local_dir, 'cpc_rfe_v2.0_sa_dly.bin.', '.gz', None,
                                             'ftp.cpc.ncep.noaa.gov', '/fews/S.Asia/data')

    @staticmethod
    def get_datetime_from_file_name(filename):
        return datetime.datetime.strptime(os.path.splitext(os.path.basename(filename))[0].split('.')[-1], '%Y%m%d')


