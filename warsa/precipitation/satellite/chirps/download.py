import os
import datetime
from warsa.precipitation.satellite.download import FTPDownload


class Chirps20GlobalDaily05TifFTP(FTPDownload):
    """Download data from:
        ftp://ftp.chg.ucsb.edu/pub/org/chg/products/CHIRPS-2.0/global_daily/tifs/p05/1981/
    File format:
        chirps-v2.0.1981.01.01.tif.gz
    """
    def __init__(self, local_dir):
        super(Chirps20GlobalDaily05TifFTP, self).__init__(local_dir, 'chirps-v2.0.', '.tif.gz', [4], 'ftp.chg.ucsb.edu',
                                                          '/pub/org/chg/products/CHIRPS-2.0/global_daily/tifs/p05/')

    @staticmethod
    def get_datetime_from_file_name(filename):
        return datetime.datetime.strptime(''.join(os.path.basename(filename).split('.')[2:5]), '%Y%m%d')


class Chirps20GlobalDaily25TifFTP(FTPDownload):
    """Download data from:
        ftp://ftp.chg.ucsb.edu/pub/org/chg/products/CHIRPS-2.0/global_daily/tifs/p25
    File format:
        chirps-v2.0.1981.01.01.tif.gz
    """
    def __init__(self, local_dir):
        super(Chirps20GlobalDaily25TifFTP, self).__init__(local_dir, 'chirps-v2.0.', '.tif.gz', [4],
                                                          'ftp.chg.ucsb.edu',
                                                          '/pub/org/chg/products/CHIRPS-2.0/global_daily/tifs/p25/')

    @staticmethod
    def get_datetime_from_file_name(filename):
        return datetime.datetime.strptime(''.join(os.path.basename(filename).split('.')[2:5]), '%Y%m%d')


