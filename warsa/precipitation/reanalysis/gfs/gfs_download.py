import os
from warsa.precipitation.satellite.download import SatelliteBasedPrecipitationDownload


class GFSDownload(SatelliteBasedPrecipitationDownload):
    # ftp://ftp.cpc.ncep.noaa.gov/precip/CMORPH_V0.ir/RAW/8km-30min/2011/201108/CMORPH_V0.x_RAW_8km-30min_2011080100.gz
    def __init__(self):
        SatelliteBasedPrecipitationDownload.__init__(self)
        self.ftp_host = 'nomads.ncdc.noaa.gov'
        self.dir_lens = [4,6]

    def get_ftp_file_names(self, lines):
        file_names = []
        for line in lines:
            if not line.startswith('d'):
                filename = line.split()[-1]
                if filename.startswith(self.prefix) and (filename.endswith('.grb2')):
                    file_names.append(filename)
        return file_names

    def get_datetime_string_from_file_name(self, filename):
        return os.path.splitext(filename)[0].split('_')[-1]

    def get_full_dir_name(self, dt):
        return self.local_dir + '/' + str(dt.year) + '/' + str(dt.year) + str(dt.month).zfill(2) + '/'

class GFSGRID4Download(GFSDownload):
    # ftp://ftp.cpc.ncep.noaa.gov/precip/CMORPH_V0.ir/RAW/8km-30min/2011/201108/CMORPH_V0.x_RAW_8km-30min_2011080100.gz
    def __init__(self):
        GFSDownload.__init__(self)
        self.ftp_dir = '/GFS/Grid4'
        self.prefix = 'gfs_4_'
        self.datetime_format = '%Y%m%d_%H%M'


def download(target_dir):
    # make_dir(target_dir)
    trmm = GFSGRID4Download()
    trmm.verbose = True
    trmm.local_dir = target_dir
    trmm.download_ftp(True)